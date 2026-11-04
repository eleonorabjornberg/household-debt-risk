#!/usr/bin/env python3
"""Rebuild the three gallery charts from committed data. Run from the repo root:
uv run --project pipeline --with matplotlib python .claude/skills/chart-from-sql/examples/build_gallery.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import pandas as pd  # noqa: E402
from chart import load_file, make_chart  # noqa: E402

ROOT = HERE.parents[3]
A1 = ROOT / "research/a1_gfc_decomposition"
meta = json.loads((ROOT / "web/public/data/meta.json").read_text())
z1 = meta["vintages"]["z1"]
rel = lambda p: str(Path(p).relative_to(ROOT))  # noqa: E731

# 1. Public share, recession shading
p = ROOT / "web/public/data/public_share.json"
make_chart(load_file(p), kind="line", x="date", y="public_share", as_percent=True,
           title="Public share of U.S. household mortgage and consumer debt",
           subtitle="Share of home mortgages and consumer credit held or backed by the public sector (federal, GSEs and agency pools, state and local)",
           source="Fed Z.1 Financial Accounts (HH&NP mortgages and consumer credit, holders by sector), pipeline mart.public_share",
           vintage=z1, out=HERE / "public_share_1952_2026", recessions=True,
           ylabel="Percent of mortgage and consumer credit (%)", labels={"public_share": "Public share"},
           data_source={"type": "file", "path": rel(p)}, mode="both")

# 2. A1 contributions, 7 groups, signed horizontal bars
d = pd.read_csv(A1 / "decomposition.csv")
res = json.loads((A1 / "results.json").read_text())


def grp(r):
    h = r.holder
    if r.side == "public":
        if "Fannie" in h or "Freddie" in h:
            return "Fannie Mae and Freddie Mac"
        if "Ginnie" in h:
            return "Ginnie Mae pools"
        if h == "Federal government (student loans)":
            return "Federal student loans"
        return "Other public holders"
    if "Private securitization" in h:
        return "Private-label securitization and mortgage REITs"
    if "Banks" in h:
        return "Banks and credit unions"
    return "Other private holders"


d["group"] = d.apply(grp, axis=1)
g = d.groupby(["group", "side"], as_index=False).contribution_pp.sum()
keys = {"Fannie Mae and Freddie Mac": "fannie_freddie", "Ginnie Mae pools": "ginnie_pools",
        "Federal student loans": "federal_student_loans", "Other public holders": "other_public",
        "Private-label securitization and mortgage REITs": "private_label_and_mreits",
        "Banks and credit unions": "banks_and_credit_unions", "Other private holders": "other_private"}
# the grouping must reproduce results.json groups_pp (rounded to 3 dp there)
for _, r in g.iterrows():
    assert abs(r.contribution_pp - res["groups_pp"][keys[r.group]]) < 0.002, (r.group, r.contribution_pp)
g = g.sort_values("contribution_pp", ascending=False)
make_chart(g, kind="hbar", x="group", y="contribution_pp", group="side",
           title=f"What moved the public share, {res['t0']} to {res['t1']}: contribution by holder group",
           subtitle="Percentage-point contribution of each holder group to the change in the public share of mortgage and consumer debt",
           source="Fed Z.1 Financial Accounts; research/a1_gfc_decomposition (A1)", vintage=z1,
           out=HERE / "a1_contributions", ylabel="Contribution to change in public share (percentage points)",
           data_source={"type": "file", "path": rel(A1 / "decomposition.csv"),
                        "note": "rows grouped to the 7 groups in results.json groups_pp; totals asserted equal to it"},
           decimals=2, unit="pp")

# 3. A1 cumulative path
p = A1 / "path.csv"
cols = ["fannie_freddie", "ginnie_pools", "federal_student_loans", "other_public",
        "private_label_and_mreits", "banks_and_credit_unions", "other_private", "total"]
make_chart(load_file(p), kind="line", x="quarter", y=cols, ink_series=["total"],
           title=f"Cumulative change in the public share since {res['t0']}",
           subtitle="By holder group: chained quarterly contributions in percentage points; the dark line is the total",
           source="Fed Z.1 Financial Accounts; research/a1_gfc_decomposition/path.csv (A1)", vintage=z1,
           out=HERE / "a1_cumulative_path", ylabel="Cumulative contribution (percentage points)",
           labels={"fannie_freddie": "Fannie/Freddie", "ginnie_pools": "Ginnie Mae pools",
                   "federal_student_loans": "Federal student loans", "other_public": "Other public",
                   "private_label_and_mreits": "Private label and mREITs", "banks_and_credit_unions": "Banks and CUs",
                   "other_private": "Other private", "total": "Total"},
           data_source={"type": "file", "path": rel(p)}, decimals=2, unit="pp")
print("ok")
