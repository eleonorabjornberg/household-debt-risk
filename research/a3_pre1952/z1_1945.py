#!/usr/bin/env python3
"""PLAN task A3, part 1: the public share 1945-1951 from Z.1 annual levels, spliced onto the quarterly series at 1952.

    uv run --project pipeline python research/a3_pre1952/z1_1945.py

Same cells and apportioning as A1 (research/a1_gfc_decomposition/decompose.py), fed with the annual (.A) versions of
the same Z.1 series. Splice check: for every year where both exist (1952 onward), each annual level must equal the Q4
quarterly level exactly, and so must the public share; no adjustment is applied at the splice. Every series must be
present from 1945 (no gaps filled). Output: z1_annual_share.csv (1945-1952, by holder group), results.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from z1_annual import load_annual  # noqa: E402

_spec = importlib.util.spec_from_file_location("a1d", ROOT / "research" / "a1_gfc_decomposition" / "decompose.py")
a1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a1)
Z1 = ROOT / "data" / "validation" / "FRB_Z1_csv.zip"


def shares(c: pd.DataFrame) -> pd.DataFrame:
    pub = c.xs("public", level="side", axis=1)
    tot = c.sum(axis=1)
    g = {"federal_direct_mortgages": [k for k in pub.columns if "Federal government (direct)" in k[1]],
         "gse_and_agency": [k for k in pub.columns if any(s in k[1] for s in ("Fannie", "Freddie", "Ginnie", "Home Loan", "Other GSEs", "Sallie"))],
         "state_and_local": [k for k in pub.columns if "State and local" in k[1]],
         "federal_student_loans": [k for k in pub.columns if "student loans" in k[1] and "Federal" in k[1]]}
    assert sum(len(v) for v in g.values()) == pub.shape[1], "every public cell must be in exactly one group"
    out = pd.DataFrame({k: 100 * pub[v].sum(axis=1) / tot for k, v in g.items()})
    out["public_share_pct"] = 100 * pub.sum(axis=1) / tot
    out["scope_musd"] = tot
    return out


def main() -> int:
    dfq, mh, ch, public, labels = a1.load(Z1)
    dfa = load_annual(Z1, list(dfq.columns))
    assert dfa.index.min().year == 1945 and not dfa.loc[:"1952-12-31"].isna().any().any(), "gap in annual Z.1 1945-52"
    q4 = dfq[dfq.index.month == 12]
    common = q4.index.intersection(dfa.index)
    splice_gap = float((dfa.loc[common, dfq.columns] - q4.loc[common]).abs().max().max())
    assert splice_gap == 0.0, f"annual and Q4 levels differ by up to {splice_gap} $M"
    ca, cq = a1.cells(dfa, mh, ch, public, labels), a1.cells(dfq, mh, ch, public, labels)
    sa, sq = shares(ca), shares(cq)
    assert abs((ca.sum(axis=1) - dfa["FL154104015"]).loc[:"1952-12-31"]).max() < 1e-6, "cells do not reproduce scope"
    share_gap = float((sa.loc[common, "public_share_pct"] - sq.loc[common, "public_share_pct"]).abs().max())
    assert share_gap < 1e-9
    early = sa.loc[:"1952-12-31"]
    early.index = early.index.year
    early.round(4).to_csv(HERE / "z1_annual_share.csv", index_label="year")
    vintage = a1.zparse.zip_member_info(Z1)[0].isoformat(sep=" ")
    res = {"vintage_z1_csv": vintage, "public_share_pct": {int(y): round(float(v), 4) for y, v in early["public_share_pct"].items()},
           "min_year": int(early["public_share_pct"].idxmin()), "min_pct": round(float(early["public_share_pct"].min()), 4),
           "federal_direct_1945_pct": round(float(early.at[1945, "federal_direct_mortgages"]), 4),
           "federal_direct_1947_pct": round(float(early.at[1947, "federal_direct_mortgages"]), 4),
           "checks": {"splice_max_abs_level_gap_musd": splice_gap, "splice_max_share_gap_pp": share_gap, "years_overlap": len(common)}}
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(early.round(3).to_string())
    print(json.dumps(res["checks"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
