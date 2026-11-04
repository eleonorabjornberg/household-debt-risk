#!/usr/bin/env python3
"""PLAN task A3, part 2: the public share 1925-1944 from Historical Statistics (1975), spliced onto Z.1 at 1945.

    uv run --project pipeline python research/a3_pre1952/pre1945.py

Inputs: hist_stats_1925_1951.csv (values read by hand from page images of Historical Statistics of the United States,
Colonial Times to 1970, vol. 2, on FRASER; sources.md) and z1_annual_share.csv (z1_1945.py, with $M components).

Public share (historical sources) = (HOLC + FNMA) / (1-4 family mortgage debt + consumer credit)
  numerator    N 270 Home Owners' Loan Corp. + N 271 Federal National Mortgage Assn. (residential nonfarm, $M;
               FNMA's figure includes some multifamily loans)
  denominator  N 273 1- to 4-family residential nonfarm mortgage debt ($bn, one decimal, "As of December 31")
               + X 551 short- and intermediate-term consumer credit ($M, "as of end of year")

Overlap: both sources exist for 1945-1951 (1952 is printed twice in N 262-272 on two footnoted bases and is left out).
For each overlap year the gap in the share and the Z.1/historical ratio of each component (federal holdings, mortgages,
consumer credit) are reported; nothing is asserted against a tolerance, because the gap is not small in every year.

Two variants for 1925-1944, both reported:
  unadjusted  the historical share as printed (main series)
  adjusted    each component scaled by its mean Z.1/historical ratio over 1945-1947 (the three years nearest the
              splice), so the level matches Z.1's definitions; an estimate, labelled as one
The splice switches to Z.1 at 1945 with no rescaling.

Reliability labels: A = Z.1; B = federal holdings from HOLC and FNMA reports, totals from Grebler-Blank-Winnick via
Historical Statistics ("must be used with caution"); C = no HOLC or FNMA yet (federal share set to zero); other public
holders before 1945 (state and local, other federal agencies) are not measured in the source.
Output: public_share_1925_1952.csv, overlap_1945_1951.csv, results_pre1945.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ADJ_YEARS = [1945, 1946, 1947]


def historical(hs: pd.DataFrame) -> pd.DataFrame:
    hs = hs.set_index("year")
    fed = hs["n270_holc_musd"].fillna(0) + hs["n271_fnma_musd"].fillna(0)
    # Blank means "no such holder" only outside each body's life: HOLC 1933-1950 (liquidated), FNMA from 1938.
    assert hs.loc[1933:1950, "n270_holc_musd"].notna().all(), "HOLC missing while it existed"
    assert hs.loc[1938:, "n271_fnma_musd"].notna().all(), "FNMA missing after 1938"
    assert hs.loc[:1932, ["n270_holc_musd", "n271_fnma_musd"]].isna().all().all()
    mort = hs["n273_mortgages_1to4_family_busd"] * 1e3
    cc = hs["x551_consumer_credit_musd"]
    out = pd.DataFrame({"federal_musd": fed, "mortgages_musd": mort, "consumer_credit_musd": cc,
                        "public_share_pct": 100 * fed / (mort + cc)})
    out["reliability"] = ["C" if y < 1933 else "B" for y in out.index]
    return out


def overlap(h: pd.DataFrame, z: pd.DataFrame) -> pd.DataFrame:
    yrs = [y for y in h.index if y in z.index]
    o = pd.DataFrame(index=pd.Index(yrs, name="year"))
    o["hist_share_pct"] = h.loc[yrs, "public_share_pct"]
    o["z1_share_pct"] = z.loc[yrs, "public_share_pct"]
    o["gap_pp"] = o["hist_share_pct"] - o["z1_share_pct"]
    o["ratio_federal"] = z.loc[yrs, "federal_mortgages_musd"] / h.loc[yrs, "federal_musd"]
    o["ratio_mortgages"] = z.loc[yrs, "mortgages_musd"] / h.loc[yrs, "mortgages_musd"]
    o["ratio_consumer_credit"] = z.loc[yrs, "consumer_credit_musd"] / h.loc[yrs, "consumer_credit_musd"]
    return o


def adjusted(h: pd.DataFrame, o: pd.DataFrame) -> pd.Series:
    r = o.loc[ADJ_YEARS, ["ratio_federal", "ratio_mortgages", "ratio_consumer_credit"]].mean()
    return 100 * h["federal_musd"] * r["ratio_federal"] / (
        h["mortgages_musd"] * r["ratio_mortgages"] + h["consumer_credit_musd"] * r["ratio_consumer_credit"])


def main() -> int:
    h = historical(pd.read_csv(HERE / "hist_stats_1925_1951.csv"))
    z = pd.read_csv(HERE / "z1_annual_share.csv").set_index("year")
    o = overlap(h, z)
    adj = adjusted(h, o)
    o.round(4).to_csv(HERE / "overlap_1945_1951.csv")
    pre = pd.DataFrame({"public_share_pct": h.loc[:1944, "public_share_pct"],
                        "adjusted_estimate_pct": adj.loc[:1944],
                        "source": "Historical Statistics 1975 (N 270-271, N 273, X 551)",
                        "reliability": h.loc[:1944, "reliability"]})
    post = pd.DataFrame({"public_share_pct": z.loc[1945:, "public_share_pct"], "adjusted_estimate_pct": float("nan"),
                         "source": "Fed Z.1 annual (z1_1945.py)", "reliability": "A"})
    out = pd.concat([pre, post])
    out.round(4).to_csv(HERE / "public_share_1925_1952.csv", index_label="year")
    s = out["public_share_pct"]
    res = {"label": "1925-1944 from Historical Statistics (B/C), with a component-adjusted estimate; 1945-1952 Z.1 (A)",
           "overlap": {"years": [int(o.index.min()), int(o.index.max())],
                       "gap_pp": {int(y): round(float(v), 4) for y, v in o["gap_pp"].items()},
                       "max_abs_gap_pp": round(float(o["gap_pp"].abs().max()), 4),
                       "ratio_federal_mean_1945_47": round(float(o.loc[ADJ_YEARS, "ratio_federal"].mean()), 4),
                       "ratio_consumer_credit_mean_1945_47": round(float(o.loc[ADJ_YEARS, "ratio_consumer_credit"].mean()), 4),
                       "ratio_mortgages_mean_1945_47": round(float(o.loc[ADJ_YEARS, "ratio_mortgages"].mean()), 4)},
           "share_1935_pct": round(float(s[1935]), 4), "share_1935_adjusted_pct": round(float(adj[1935]), 4),
           "peak_pre1945_year": int(s.loc[:1944].idxmax()), "peak_pre1945_pct": round(float(s.loc[:1944].max()), 4),
           "share_1944_pct": round(float(s[1944]), 4), "share_1944_adjusted_pct": round(float(adj[1944]), 4)}
    (HERE / "results_pre1945.json").write_text(json.dumps(res, indent=1) + "\n")
    print(o.round(3).to_string())
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
