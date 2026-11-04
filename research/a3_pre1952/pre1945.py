#!/usr/bin/env python3
"""PLAN task A3, part 2: the public share 1925-1944 from Historical Statistics (1975), spliced onto Z.1 at 1945.

    uv run --project pipeline python research/a3_pre1952/pre1945.py

Inputs: hist_stats_1925_1945.csv (values read by hand from page images of Historical Statistics of the United States,
Colonial Times to 1970, vol. 2, on FRASER; sources.md) and z1_annual_share.csv (z1_1945.py).

Public share (historical sources) = (HOLC + FNMA) / (1-4 family mortgage debt + consumer credit)
  numerator    N 270 Home Owners' Loan Corp. + N 271 Federal National Mortgage Assn. (residential nonfarm, $M)
  denominator  N 273 1- to 4-family residential nonfarm mortgage debt ($bn, one decimal, "As of December 31")
               + X 551 short- and intermediate-term consumer credit ($M, "as of end of year")
Before 1933 no federal mortgage holder existed (HOLC: Home Owners' Loan Act, approved 13 June 1933), so N 270-271 are
blank in the source and the federal share is zero by construction; state and local holdings are not measured.

Splice: the series switches from the historical sources (1925-1944) to Z.1 (1945 on) with no rescaling. Overlap check
at 1945, the only year both exist: the two shares must agree within TOL_PP, and the gap is reported. A ratio-adjusted
variant (historical shares scaled by Z.1/historical at 1945) is reported as a sensitivity, not used.

Reliability labels: A = Z.1; B = federal holdings from agency reports, denominator from Grebler-Blank-Winnick via
Historical Statistics, which warns the estimates "must be used with caution"; C = zero by construction (no federal
holder yet), state and local not measured.
Output: public_share_1925_1952.csv, results_pre1945.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TOL_PP = 0.25


def historical(hs: pd.DataFrame) -> pd.DataFrame:
    hs = hs.set_index("year")
    fed = hs["n270_holc_musd"].fillna(0) + hs["n271_fnma_musd"].fillna(0)
    # Blank cells mean "no such holder yet" only before each body existed; a blank after creation would be a gap.
    assert hs.loc[1933:, "n270_holc_musd"].notna().all(), "HOLC missing after 1933"
    assert hs.loc[1938:, "n271_fnma_musd"].notna().all(), "FNMA missing after 1938"
    assert hs.loc[:1932, ["n270_holc_musd", "n271_fnma_musd"]].isna().all().all()
    denom = hs["n273_mortgages_1to4_family_busd"] * 1e3 + hs["x551_consumer_credit_musd"]
    out = pd.DataFrame({"federal_musd": fed, "scope_musd": denom, "public_share_pct": 100 * fed / denom})
    out["source"] = "Historical Statistics 1975 (N 270-271, N 273, X 551)"
    out["reliability"] = ["C" if y < 1933 else "B" for y in out.index]
    return out


def splice(h: pd.DataFrame, z: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    z = z.set_index("year")
    gap = float(h.at[1945, "public_share_pct"] - z.at[1945, "public_share_pct"])
    assert abs(gap) <= TOL_PP, f"overlap gap at 1945 is {gap:.3f} pp > {TOL_PP}"
    ratio = float(z.at[1945, "public_share_pct"] / h.at[1945, "public_share_pct"])
    zz = pd.DataFrame({"public_share_pct": z["public_share_pct"], "scope_musd": z["scope_musd"],
                       "source": "Fed Z.1 annual (z1_1945.py)", "reliability": "A"})
    out = pd.concat([h.loc[:1944, ["public_share_pct", "scope_musd", "source", "reliability"]], zz])
    out["ratio_adjusted_sensitivity_pct"] = [v * ratio if y < 1945 else v for y, v in out["public_share_pct"].items()]
    checks = {"overlap_year": 1945, "hist_share_1945_pct": round(float(h.at[1945, "public_share_pct"]), 4),
              "z1_share_1945_pct": round(float(z.at[1945, "public_share_pct"]), 4), "gap_pp": round(gap, 4),
              "hist_federal_1945_musd": float(h.at[1945, "federal_musd"]),
              "hist_scope_1945_musd": float(h.at[1945, "scope_musd"]), "z1_scope_1945_musd": float(z.at[1945, "scope_musd"]),
              "ratio_z1_over_hist_1945": round(ratio, 4), "tolerance_pp": TOL_PP}
    return out, checks


def main() -> int:
    h = historical(pd.read_csv(HERE / "hist_stats_1925_1945.csv"))
    out, checks = splice(h, pd.read_csv(HERE / "z1_annual_share.csv"))
    out.round(4).to_csv(HERE / "public_share_1925_1952.csv", index_label="year")
    s = out["public_share_pct"]
    res = {"label": "1925-1944 from Historical Statistics (reliability B/C), 1945-1952 Z.1 (A)",
           "checks": checks,
           "share_1932_pct": round(float(s[1932]), 4), "share_1935_pct": round(float(s[1935]), 4),
           "peak_pre1945_year": int(s.loc[:1944].idxmax()), "peak_pre1945_pct": round(float(s.loc[:1944].max()), 4),
           "share_1944_pct": round(float(s[1944]), 4),
           "holc_1935_musd": float(h.at[1935, "federal_musd"])}
    (HERE / "results_pre1945.json").write_text(json.dumps(res, indent=1) + "\n")
    print(out.loc[:1946, ["public_share_pct", "reliability"]].round(3).T.to_string())
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
