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
Fannie Mae: needs SEC EDGAR (SEC_USER_AGENT per command, never written to a file); not yet run.
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
    print(df[["scope", "ce_expense", "latest_ce_expense", "crt_debt_interest", "gross_cost_musd",
              "avg_crt_maxcov_musd", "ce_expense_per_maxcov", "gross_cost_per_maxcov"]].to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
