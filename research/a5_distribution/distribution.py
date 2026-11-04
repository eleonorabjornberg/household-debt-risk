#!/usr/bin/env python3
"""PLAN task A5: who borrows (by wealth, income, age; by state) and who holds the loans (by loan type).

    uv run --project pipeline python research/a5_distribution/distribution.py [--z1-zip PATH]

Inputs (downloaded into data/a5/ if absent; raw files stay out of git, see sources.md for hashes):
  * Fed Distributional Financial Accounts, dfa.zip (shares and levels by wealth/income/age percentile group)
  * NY Fed State Level Household Debt Statistics, area_report_by_year.xlsx (per-capita balances, 90+ day delinquency)
  * Fed Z.1 zip (as A1), for the public share of each loan type

What this script does NOT do: cross borrower groups with holders. No free source does (AVAILABILITY.md), and the
assumption needed to impute it is Eleonora's call (tracks/analysis.md, Q4). Borrower tables and holder tables are
reported side by side, never multiplied together here.

Outputs (next to this file): dfa_shares.csv, dfa_leverage.csv, state_2025.csv, loan_type_public_share.csv,
results.json.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "a5"
DFA_URL = "https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip"
STATE_URL = "https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/area_report_by_year.xlsx"

_spec = importlib.util.spec_from_file_location("a1_decompose", ROOT / "research" / "a1_gfc_decomposition" / "decompose.py")
a1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a1)

DEBT = ["Liabilities", "Home mortgages", "Consumer credit"]
GROUPINGS = {"wealth": "networth", "income": "income", "age": "age"}
ORDER = {
    "wealth": ["TopPt1", "RemainingTop1", "Next9", "Next40", "Bottom50"],
    "income": ["pct99to100", "pct80to99", "pct60to80", "pct40to60", "pct20to40", "pct00to20"],
}
DATES = ["1989:Q3", "2007:Q4", "2026:Q2"]
STATES = 51  # 50 states + DC


def fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "household-debt-risk research"})
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
    return dest


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_dfa(zip_path: Path, name: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as z:
        return pd.read_csv(io.BytesIO(z.read(name)))


def dfa_tables(zip_path: Path):
    shares, lev = [], []
    for grouping, stem in GROUPINGS.items():
        sh = read_dfa(zip_path, f"dfa-{stem}-shares.csv")
        lv = read_dfa(zip_path, f"dfa-{stem}-levels.csv")
        # Shares are percent of the aggregate: each date's groups must add to 100 (rounding in the file: 0.1 per group).
        tot = sh.groupby("Date")[DEBT + ["Assets", "Net worth"]].sum()
        n_groups = sh["Category"].nunique()
        assert (tot.sub(100).abs() <= 0.1 * n_groups + 1e-9).all().all(), f"{grouping} shares do not add to 100"
        s = sh[sh["Date"].isin(DATES)][["Date", "Category"] + DEBT + ["Assets", "Net worth"]].copy()
        s.insert(0, "grouping", grouping)
        shares.append(s)
        v = lv[lv["Date"].isin(DATES)][["Date", "Category", "Assets", "Liabilities", "Home mortgages", "Real estate"]].copy()
        v["liabilities_to_assets"] = v["Liabilities"] / v["Assets"]
        v["mortgages_to_real_estate"] = v["Home mortgages"] / v["Real estate"]
        v.insert(0, "grouping", grouping)
        lev.append(v)
    return pd.concat(shares, ignore_index=True), pd.concat(lev, ignore_index=True)


def read_state(xlsx: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(xlsx, sheet_name=sheet, header=None)
    hdr = raw.index[raw.iloc[:, 0].astype(str).str.strip().str.lower() == "state"][0]
    df = raw.iloc[hdr + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[hdr]]
    df = df[df["state"].astype(str).str.fullmatch(r"[A-Z]{2}")].set_index("state")
    df = df.loc[:, [c for c in df.columns if c.startswith("Q4_")]].apply(pd.to_numeric, errors="coerce")
    df.columns = [int(c[3:]) for c in df.columns]
    return df


def state_table(xlsx: Path, year: int = 2025) -> pd.DataFrame:
    cols = {}
    for sheet in ["mortgage", "studentloan", "auto", "creditcard", "total"]:
        d = read_state(xlsx, sheet)
        cols[f"{sheet}_pc_{year}"] = d[year]
        if sheet in ("mortgage", "total"):
            cols[f"{sheet}_pc_2007"] = d[2007]
    for sheet in ["mortgage_delinq", "studentloan_delinq"]:
        cols[f"{sheet}_{year}"] = read_state(xlsx, sheet)[year]
    t = pd.DataFrame(cols)
    # Puerto Rico is in the file; comparisons here are across the 50 states and DC (README, Limits).
    t = t.drop(index="PR")
    assert len(t) == STATES, f"expected {STATES} states + DC, got {len(t)}"
    assert t.notna().all().all(), "missing state values"
    # Per-capita parts cannot exceed the total (HELOC and 'other' are in total only).
    parts = t[[f"{s}_pc_{year}" for s in ["mortgage", "studentloan", "auto", "creditcard"]]].sum(axis=1)
    assert (parts <= t[f"total_pc_{year}"] + 1).all(), "per-capita parts exceed total"
    return t


def loan_type_shares(z1_zip: Path, when: str = "2026Q2") -> pd.DataFrame:
    df, mh, ch, public, labels = a1.load(z1_zip)
    c = a1.cells(df, mh, ch, public, labels)
    t = a1.q_end(when)
    row = c.loc[t]
    out = []
    for loan in ["mortgages", "consumer credit"]:
        x = row.xs(loan, level="loan")
        pub = x.xs("public", level="side").sum()
        out.append({"loan_type": loan, "quarter": when, "total_bn": x.sum() / 1e3, "public_bn": pub / 1e3,
                    "public_share": pub / x.sum()})
    out = pd.DataFrame(out)
    # Ties to the overall public share (C2 at 2026Q2) when weighted back together.
    overall = out["public_bn"].sum() / out["total_bn"].sum()
    whole = c.loc[t].xs("public", level="side").sum() / c.loc[t].sum()
    assert abs(overall - whole) < 1e-12
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    ns = ap.parse_args(argv)
    dfa_zip = fetch(DFA_URL, DATA / "dfa.zip")
    state_xlsx = fetch(STATE_URL, DATA / "area_report_by_year.xlsx")

    shares, lev = dfa_tables(dfa_zip)
    shares.round(2).to_csv(HERE / "dfa_shares.csv", index=False)
    lev.round(4).to_csv(HERE / "dfa_leverage.csv", index=False)
    st = state_table(state_xlsx)
    st.sort_index().to_csv(HERE / "state_2025.csv")
    lt = loan_type_shares(ns.z1_zip)
    lt.round(4).to_csv(HERE / "loan_type_public_share.csv", index=False)

    def sh(grouping, cat, col, date="2026:Q2"):
        r = shares[(shares.grouping == grouping) & (shares.Category == cat) & (shares.Date == date)]
        assert len(r) == 1
        return float(r[col].iloc[0])

    def lv(grouping, cat, col, date="2026:Q2"):
        r = lev[(lev.grouping == grouping) & (lev.Category == cat) & (lev.Date == date)]
        assert len(r) == 1
        return float(r[col].iloc[0])

    top10 = lambda col, d="2026:Q2": sh("wealth", "TopPt1", col, d) + sh("wealth", "RemainingTop1", col, d) + sh("wealth", "Next9", col, d)  # noqa: E731
    pc = st["mortgage_pc_2025"]
    sl = st["studentloan_pc_2025"]
    res = {
        "vintage_dfa": "dfa.zip files dated 2026-09-15 (data through 2026:Q2)",
        "sha256_dfa_zip": sha256(dfa_zip),
        "vintage_state": "NY Fed State Level Household Debt Statistics 2003-2025, February 2026",
        "sha256_state_xlsx": sha256(state_xlsx),
        "vintage_z1_csv": a1.zparse.zip_member_info(ns.z1_zip)[0].isoformat(sep=" "),
        "wealth_2026q2_pct": {
            "bottom50_mortgages": sh("wealth", "Bottom50", "Home mortgages"),
            "bottom50_consumer_credit": sh("wealth", "Bottom50", "Consumer credit"),
            "bottom50_net_worth": sh("wealth", "Bottom50", "Net worth"),
            "next40_mortgages": sh("wealth", "Next40", "Home mortgages"),
            "next40_consumer_credit": sh("wealth", "Next40", "Consumer credit"),
            "top10_mortgages": round(top10("Home mortgages"), 2),
            "top10_net_worth": round(top10("Net worth"), 2),
            "bottom50_mortgages_1989q3": sh("wealth", "Bottom50", "Home mortgages", "1989:Q3"),
            "bottom50_consumer_credit_1989q3": sh("wealth", "Bottom50", "Consumer credit", "1989:Q3"),
        },
        "income_2026q2_pct": {
            "bottom20_consumer_credit": sh("income", "pct00to20", "Consumer credit"),
            "bottom20_mortgages": sh("income", "pct00to20", "Home mortgages"),
            "top20_mortgages": round(sh("income", "pct80to99", "Home mortgages") + sh("income", "pct99to100", "Home mortgages"), 2),
        },
        "leverage_2026q2": {
            "bottom50_liabilities_to_assets": round(lv("wealth", "Bottom50", "liabilities_to_assets"), 4),
            "top1_liabilities_to_assets": round(lv("wealth", "TopPt1", "liabilities_to_assets"), 4),
            "bottom50_mortgages_to_real_estate": round(lv("wealth", "Bottom50", "mortgages_to_real_estate"), 4),
            "bottom50_liabilities_to_assets_2007q4": round(lv("wealth", "Bottom50", "liabilities_to_assets", "2007:Q4"), 4),
        },
        "state_2025": {
            "mortgage_pc_max_state": pc.idxmax(), "mortgage_pc_max": int(pc.max()),
            "mortgage_pc_min_state": pc.idxmin(), "mortgage_pc_min": int(pc.min()),
            "mortgage_pc_max_over_min": round(float(pc.max() / pc.min()), 2),
            "studentloan_pc_max_state": sl.idxmax(), "studentloan_pc_max": int(sl.max()),
            "studentloan_pc_min_state": sl.idxmin(), "studentloan_pc_min": int(sl.min()),
            "studentloan_pc_max_over_min": round(float(sl.max() / sl.min()), 2),
        },
        "loan_type_public_share_2026q2": {r.loan_type: round(float(r.public_share), 4) for r in lt.itertuples()},
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
