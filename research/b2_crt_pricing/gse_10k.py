#!/usr/bin/env python3
"""B2 for 2017-2023: aggregate annual CRT cost from the GSEs' 10-K filings (the coarser measure; EDGAR has no per-deal
STACR/CAS pricing, research/b2_crt_pricing/edgar.py discover).

    uv run --project pipeline python research/a2_net_exposure/freddie_10k.py    # fetches Freddie's 10-K PDFs + text
    uv run --project pipeline python research/b2_crt_pricing/gse_10k.py

Freddie Mac (www.freddiemac.com PDFs, the same files A2 uses; data/a2/freddie/, outside git). What each filing prints:
  FY2019 10-K, Table 22 "Details of Single-Family Credit Enhancement Expense": 2017-2019, credit enhancement expense,
      interest expense related to CRT debt (STACR debt notes), estimated reinvestment income on CRT debt proceeds.
  FY2020 10-K, Table 24 "... Expenses and Recoveries": 2018-2020, same three lines.
  FY2021 10-K, segment results: Single-Family credit enhancement expense, 2019-2021. CRT-debt interest not printed.
  FY2022, FY2023 10-K: consolidated credit enhancement expense only (single-family plus a small multifamily part).
Each year's value is taken from the earliest filing that prints it; every later filing that prints the same year is
kept as a restatement column, never averaged. Lines are matched by their exact labels inside an anchored table or
statement; a label not found where expected raises (nothing is filled in).

Output: freddie_crt_cost.csv (committed). Cost per dollar of protection uses A2's outstanding CRT maximum coverage
(research/a2_net_exposure/freddie_ce_outstanding.csv, average of the two year ends).
Fannie Mae (SEC EDGAR, fetched by research/a2_net_exposure/fannie_10k.py with SEC_USER_AGENT given per command and
never written to a file; data/a2/fannie/): every 10-K from FY2018 prints "Credit Risk Transfer Transactions ... Cash
paid or transferred for: CAS transactions / CIRT transactions [/ Lender risk-sharing transactions]" for two years; the
FY2017 10-K gives 2017 and 2016 in a sentence ("we paid approximately $X million in interest expense, net of LIBOR, on
our outstanding CAS debt and approximately $Y million in CIRT premiums"). CAS cash is interest net of LIBOR/SOFR plus
CAS REMIC and CLN payments. Both filings that print a year must agree, or the script stops. Output: fannie_crt_cost.csv,
with cost per dollar of CRT risk in force where A2's year-end risk in force (rounded $B) exists at both ends.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRE = ROOT / "data" / "a2" / "freddie"
A2 = ROOT / "research" / "a2_net_exposure" / "freddie_ce_outstanding.csv"
NUM = r"\(?\$?\(?[\d,]+\)?"

# filing -> (fiscal year, anchor regex, {field: label regex}, how many year columns, scope)
SPECS = [
    ("10k_021320", 2019, r"^Table 22 - Details of Single-Family Credit Enhancement Expense\s*$",
     {"ce_expense": r"^\s*Credit enhancement expense\s", "crt_debt_interest": r"^\s*Interest expense related to CRT debt\s",
      "reinvestment_income": r"^\s*Estimated reinvestment income from proceeds of CRT debt issuance\s"}, 3, "single-family"),
    ("10k_021121", 2020, r"^Table 24 - Details of Single-Family Credit Enhancement Expenses and Recoveries\s*$",
     {"ce_expense": r"^\s*Credit enhancement expense\s", "crt_debt_interest": r"^\s*Interest expense related to CRT debt\s",
      "reinvestment_income": r"^\s*Estimated reinvestment income from proceeds of CRT debt issuance\s"}, 3, "single-family"),
    ("10k_021022", 2021, r"^Table \d+ - Single-Family Segment Financial Results\s*$",
     {"ce_expense": r"^\s*Credit enhancement expense\s{2,}\("}, 3, "single-family"),
    ("10k_022223", 2022, r"^Non-interest expense consists of", {"ce_expense": r"^Credit enhancement expense\s{2,}\("}, 3, "consolidated"),
    ("10k_021424", 2023, r"^Non-interest expense consists of", {"ce_expense": r"^Credit enhancement expense\s{2,}\("}, 3, "consolidated"),
]


def values(line: str, n: int) -> list[float]:
    """First n numbers after the label; '(1,234)' and '($1,234)' are costs, returned as positive $M."""
    toks = re.findall(r"\(?\$?[\d,]+\)?", line.split("  ", 1)[1] if "  " in line else line)
    out = [float(t.strip("()$").replace(",", "")) for t in toks[:n]]
    if len(out) < n:
        raise ValueError(f"fewer than {n} numbers: {line.strip()[:120]}")
    return out


def parse(stem: str, fy: int, anchor: str, fields: dict, n: int, scope: str) -> list[dict]:
    lines = (FRE / f"{stem}.txt").read_text(errors="replace").splitlines()
    starts = [i for i, l in enumerate(lines) if re.search(anchor, l)]
    if not starts:
        raise ValueError(f"{stem}: anchor not found")
    i0 = starts[0]
    window = lines[i0:i0 + 40]
    rows = []
    for field, lab in fields.items():
        hit = [l for l in window if re.search(lab, l)]
        if not hit:
            raise ValueError(f"{stem}: {field} not found after the anchor")
        for k, v in enumerate(values(hit[0], n)):
            rows.append({"year": fy - k, "field": field, "musd": v, "scope": scope, "filing": f"{stem}.pdf",
                         "filing_fy": fy, "sha256": hashlib.sha256((FRE / f"{stem}.pdf").read_bytes()).hexdigest()})
    return rows


FNM = ROOT / "data" / "a2" / "fannie"
FNM_RIF = ROOT / "research" / "a2_net_exposure" / "fannie_ce_outstanding.csv"
NUMB = r"\$?\s*([\d,]+)"


def fannie_text(fy: int) -> str:
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", (FNM / f"fnma_10k_fy{fy}.htm").read_text(errors="replace"))
    import html
    return re.sub(r"[\s|]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def fannie_rows(fy: int) -> list[dict]:
    t = fannie_text(fy)
    sha = hashlib.sha256((FNM / f"fnma_10k_fy{fy}.htm").read_bytes()).hexdigest()
    base = {"filing": f"fnma_10k_fy{fy}.htm", "filing_fy": fy, "sha256": sha}
    m = re.search(r"Credit Risk Transfer Transactions For the Year Ended December 31, (\d{4}) (\d{4}) Cash paid or transferred "
                  r"for: \(Dollars in millions\) (.{0,200}?)\(1\) Consists of", t)
    if m:
        y1, y0, body = int(m.group(1)), int(m.group(2)), m.group(3)
        assert y1 == fy and y0 == fy - 1, (fy, y1, y0)
        out = []
        for field, lab in [("cas", r"CAS transactions \(1\)"), ("cirt", r"CIRT transactions"),
                           ("lender_risk_sharing", r"Lender risk-sharing transactions")]:
            mm = re.search(lab + r" " + NUMB + r" " + NUMB, body)
            if not mm:
                if field == "lender_risk_sharing" and fy == 2018:
                    continue                     # not printed in the FY2018 table
                raise ValueError(f"FY{fy}: {field} not found")
            for yr, v in [(y1, mm.group(1)), (y0, mm.group(2))]:
                out.append(base | {"year": yr, "field": field, "musd": float(v.replace(",", ""))})
        return out
    if fy == 2017:
        ss = re.findall(r"we paid approximately \$(\d+) million in interest expense, net of LIBOR, on our outstanding CAS debt "
                        r"and approximately \$(\d+) million in CIRT premiums[^.]*?(?:December 31, (\d{4}))?[;.]", t)
        assert len(ss) >= 2, ss
        out = []
        for (cas, cirt, _), yr in zip(ss[:2], (2017, 2016)):
            out += [base | {"year": yr, "field": "cas", "musd": float(cas)}, base | {"year": yr, "field": "cirt", "musd": float(cirt)}]
        return out
    raise ValueError(f"FY{fy}: CRT cash table not found")


def fannie() -> pd.DataFrame:
    long = pd.DataFrame([r for fy in range(2017, 2024) for r in fannie_rows(fy)])
    chk = long.groupby(["year", "field"])["musd"].nunique()
    if (chk > 1).any():
        raise SystemExit(f"Fannie filings disagree: {chk[chk > 1].index.tolist()}")
    first = long.sort_values("filing_fy").groupby(["year", "field"], as_index=False).first()
    df = first.pivot(index="year", columns="field", values="musd")
    df = df.join(first[first["field"] == "cas"].set_index("year")[["filing", "sha256"]])
    df = df[(df.index >= 2017) & (df.index <= 2023)]
    df["cas_cirt_musd"] = df["cas"] + df["cirt"]
    rif = pd.read_csv(FNM_RIF).set_index("year_end")["crt_rif_bn"] * 1000
    df["avg_crt_rif_musd"] = [(rif.get(y - 1) + rif.get(y)) / 2 if pd.notna(rif.get(y - 1)) and pd.notna(rif.get(y)) else float("nan")
                              for y in df.index]
    df["cas_cirt_per_rif"] = df["cas_cirt_musd"] / df["avg_crt_rif_musd"]
    df.reset_index().to_csv(HERE / "fannie_crt_cost.csv", index=False, float_format="%.6g")
    return df


def main() -> int:
    long = pd.DataFrame([r for s in SPECS for r in parse(*s)])
    first = long.sort_values("filing_fy").groupby(["year", "field"], as_index=False).first()
    same = long.merge(first[["year", "field", "scope"]], on=["year", "field", "scope"])   # restatements, same scope only
    last = same.sort_values("filing_fy").groupby(["year", "field"], as_index=False).last()
    wide = first.pivot(index="year", columns="field", values="musd")
    rest = last.pivot(index="year", columns="field", values="musd").add_prefix("latest_")
    meta = first[first["field"] == "ce_expense"].set_index("year")[["scope", "filing", "sha256"]]
    df = wide.join(rest).join(meta)
    df = df[df.index >= 2017]
    df["gross_cost_musd"] = df["ce_expense"] + df["crt_debt_interest"]          # NaN where interest is not printed
    df["net_cost_musd"] = df["gross_cost_musd"] - df["reinvestment_income"]
    cov = pd.read_csv(A2).set_index("year_end")["crt_maxcov_musd"]
    df["avg_crt_maxcov_musd"] = [(cov[y - 1] + cov[y]) / 2 for y in df.index]
    df["ce_expense_per_maxcov"] = df["ce_expense"] / df["avg_crt_maxcov_musd"]
    df["gross_cost_per_maxcov"] = df["gross_cost_musd"] / df["avg_crt_maxcov_musd"]
    # Checks: the 2019 table's own total, and restatements stated (not smoothed)
    assert abs(df.loc[2019, "ce_expense"] + df.loc[2019, "crt_debt_interest"] - 1753) < 0.5
    df.reset_index().to_csv(HERE / "freddie_crt_cost.csv", index=False, float_format="%.6g")
    fn = fannie()
    print(fn[["cas", "cirt", "lender_risk_sharing", "cas_cirt_musd", "avg_crt_rif_musd", "cas_cirt_per_rif"]].to_string())
    print(df[["scope", "ce_expense", "latest_ce_expense", "crt_debt_interest", "gross_cost_musd",
              "avg_crt_maxcov_musd", "ce_expense_per_maxcov", "gross_cost_per_maxcov"]].to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
