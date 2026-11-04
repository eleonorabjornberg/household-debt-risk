"""Parse outstanding single-family credit-enhancement coverage from Freddie Mac 10-K text (pdftotext -layout).

Eleonora's decision on A2 Q1 (2026-11-04): net exposure uses OUTSTANDING CRT and mortgage-insurance cover from the
Enterprises' 10-K/10-Q filings, with the FHFA issuance bounds (net_exposure.py) as the check.

Freddie Mac publishes one table per 10-K with the protected UPB and the maximum coverage of every credit-enhancement type
at two year ends. Its layout changed four times between FY2013 and FY2025, so each filing is assigned a layout in
FILINGS and the column order is taken from that layout, never guessed:

  upb2_max2  FY2013-FY2016  one row per type: UPB(t), UPB(t-1), MaxCov(t), MaxCov(t-1)
  pairs      FY2017         one row per type: UPB(t), MaxCov(t), UPB(t-1), MaxCov(t-1)
  blocks5    FY2018-FY2019  one block per year end: UPB, % of portfolio, first-loss, mezzanine, total MaxCov
  blocks3    FY2020-        one block per year end: UPB, % of portfolio, MaxCov

Every parsed block is checked: the components' maximum coverage must add up to the table's own Total (to $1M per
row, for rounding). A block that does not reconcile raises; nothing is filled in.

Categories (label regexes, applied the same way in every year):
  crt    STACR, ACIS, "credit risk transfer"/"risk transfer" transactions, insurance/reinsurance: the CRT programme
  pmi    primary mortgage insurance (loan-level; Freddie keeps the insurer counterparty risk)
  other  everything else (lender recourse and risk sharing, pool insurance, HFA indemnification, subordination incl.
         senior/subordinate structures, seller indemnification, deep MI, "Other"). From FY2021 Freddie reports only
         STACR, ACIS and "Other", so finer splits are not comparable over time and are not used.

Fannie Mae: not parsed here. Fannie prints outstanding CRT risk in force as a sentence, not a table; see
fannie_extract.py (10-Ks fetched from SEC EDGAR by fannie_10k.py under Eleonora's Q6 decision).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

NUM = re.compile(r"^\(?-?[\d,]+(?:\.\d+)?\)?%?$")
DASH = {"—", "–", "-", "$—", "$-"}
YEAR_ONLY = re.compile(r"^(19|20)\d\d$")
SKIP_LABEL = re.compile(r"in millions|december 31|form 10-k|^freddie mac|^table|outstanding as of", re.I)
NOT_COMPONENT = re.compile(r"^(total|less\b|single-family credit guarantee portfolio|single-family mortgage portfolio|"
                           r"single-family:|other credit protection|credit enhancements at the time|crt activities|"
                           r"other credit enhancements:|other:|(credit )?enhancements?\b)", re.I)
CRT = re.compile(r"stacr|acis|risk transfer|insurance/reinsurance", re.I)
PMI = re.compile(r"primary mortgage insurance", re.I)

# fiscal year -> (pdf name on freddiemac.com/investors/financials/pdf/, layout)
FILINGS = {
    2013: ("10k_022714.pdf", "upb2_max2"), 2014: ("10k_021915.pdf", "upb2_max2"),
    2015: ("10k_021816.pdf", "upb2_max2"), 2016: ("10k_021617.pdf", "upb2_max2"),
    2017: ("10k_021518.pdf", "pairs"), 2018: ("10k_021419.pdf", "blocks5"), 2019: ("10k_021320.pdf", "blocks5"),
    2020: ("10k_021121.pdf", "blocks3"), 2021: ("10k_021022.pdf", "blocks3"), 2022: ("10k_022223.pdf", "blocks3"),
    2023: ("10k_021424.pdf", "blocks3"), 2024: ("10k_021325.pdf", "blocks3"), 2025: ("10k_021226.pdf", "blocks3"),
}
# Where the table starts in each layout (first match after the table of contents).
ANCHOR = {
    "upb2_max2": re.compile(r"^\s*(Table 4\.5\s+.\s+Recourse and Other Forms of Credit Protection(\(\d\))?|"
                            r"CREDIT PROTECTION AND OTHER FORMS OF CREDIT ENHANCEMENT)\s*$", re.M),
    "pairs": re.compile(r"total current and protected UPB and maximum coverage", re.I),
    "blocks5": re.compile(r"^\s*Table \d+ - Details of Credit Enhanced Loans", re.M),
    "blocks3": re.compile(r"^\s*Table \d+ - Single-Family (Credit Guarantee|Mortgage) Portfolio Credit Enhancement "
                          r"Coverage Outstanding\s*$", re.M),
}


def tokens(line: str) -> tuple[str, list[float | None]]:
    """Split a layout line into (label, numbers). '—' is zero; '(123)' is negative; a bare footnote '(3)' is dropped."""
    parts = [p.strip() for p in re.split(r"\s{2,}|(?<=\S)\s(?=\$)", line.replace("$ ", "$").strip()) if p.strip()]
    label, nums = [], []
    for p in parts:
        if p == "$":
            continue
        q = p.replace("$", "")
        if q in DASH or p in DASH:
            nums.append(0.0)
        elif NUM.match(q) and not re.fullmatch(r"\(\d\)", q):
            neg = q.startswith("(") and q.endswith(")")
            v = float(q.strip("()%").replace(",", ""))
            nums.append(-v if neg else v)
        elif not nums:
            label.append(p)
    return re.sub(r"\(\d\)|\$", "", " ".join(label)).strip(), nums


@dataclass
class Row:
    label: str
    nums: list


def rows_until_total(lines: list[str]) -> tuple[list[Row], Row]:
    out, pending = [], ""
    for ln in lines:
        label, nums = tokens(ln)
        if not nums:
            # A wrapped label ("STACR debt note and ACIS" / "transactions(3)  241,450 ...") carries over to the next
            # row, but a section header ending in ":" does not.
            pending = "" if (label.endswith(":") or SKIP_LABEL.search(label)) else label
            continue
        if len(nums) < 2 or SKIP_LABEL.search(label) or all(YEAR_ONLY.match(f"{int(abs(n))}") for n in nums if n):
            pending = ""
            continue
        if pending and label and label[0].islower():
            label = f"{pending} {label}"
        pending = ""
        r = Row(label, nums)
        if re.fullmatch(r"total", label, re.I):
            return out, r
        out.append(r)
    raise ValueError("no Total row found")


def category(label: str) -> str:
    return "crt" if CRT.search(label) else "pmi" if PMI.search(label) else "other"


def _reconcile(comp: dict, total: float, n_rows: int, where: str) -> None:
    s = sum(comp.values())
    assert abs(s - total) <= max(1.0, n_rows), f"{where}: components {s:,.0f} != Total {total:,.0f} ($M)"


def parse(text: str, fy: int, layout: str) -> dict[int, dict[str, float]]:
    """Return {year_end: {'crt': maxcov, 'pmi': maxcov, 'other': maxcov, 'total': maxcov, 'portfolio_upb': upb|None}}."""
    m = ANCHOR[layout].search(text)
    if not m:
        raise ValueError(f"FY{fy}: table anchor for layout {layout} not found")
    lines = text[m.end():].splitlines()
    out: dict[int, dict[str, float]] = {}
    if layout in ("upb2_max2", "pairs"):
        rows, tot = rows_until_total(lines)
        mi = (2, 3) if layout == "upb2_max2" else (1, 3)
        for k, y in enumerate((fy, fy - 1)):
            comp = {"crt": 0.0, "pmi": 0.0, "other": 0.0}
            n = 0
            for r in rows:
                if NOT_COMPONENT.match(r.label) or len(r.nums) != 4:
                    continue
                comp[category(r.label)] += r.nums[mi[k]]
                n += 1
            _reconcile(comp, tot.nums[mi[k]], n, f"FY{fy} {y}")
            ui = (0, 1)[k] if layout == "upb2_max2" else (0, 2)[k]
            out[y] = {**comp, "total": tot.nums[mi[k]],
                      "portfolio_upb": tot.nums[ui] if layout == "pairs" else None}
        return out
    width = 5 if layout == "blocks5" else 3
    hdr = re.compile(r"^\s*(?:Outstanding as of )?December 31, (\d{4})\s*$")
    i = 0
    while len(out) < 2 and i < len(lines):
        h = hdr.match(lines[i])
        i += 1
        if not h:
            continue
        y = int(h.group(1))
        rows, tot = rows_until_total(lines[i:])
        comp = {"crt": 0.0, "pmi": 0.0, "other": 0.0}
        n = 0
        for r in rows:
            if NOT_COMPONENT.match(r.label) or len(r.nums) != width:
                continue
            comp[category(r.label)] += r.nums[-1]
            n += 1
        _reconcile(comp, tot.nums[-1], n, f"FY{fy} {y}")
        out[y] = {**comp, "total": tot.nums[-1], "portfolio_upb": tot.nums[0]}
    if sorted(out) != [fy - 1, fy]:
        raise ValueError(f"FY{fy}: expected year ends {fy - 1} and {fy}, found {sorted(out)}")
    return out
