#!/usr/bin/env python3
"""PLAN task A8 (Eleonora, 2026-11-04: Q5 option c, both measures, risk bearer as headline).

    uv run --project pipeline python research/a8_international/compare.py

Reads national_figures.csv (each value transcribed from a national source, with URL and SHA-256; sources.md) and the
US figures from research/a2_net_exposure/results.json, and computes only the shares for which a national source gives
both the numerator and the denominator. A share that cannot be computed is recorded as null, never as zero.

  (b) risk bearer, headline: share of household credit on which a public body takes the credit loss
  (a) holder: share of household credit held by publicly owned lenders (ownership is not a guarantee)

Germany's publicly owned banks (Eleonora, 2026-11-04, Q7 card q7-2, option c): on the risk-bearer measure their
lending is a third category, "publicly owned, not guaranteed", reported in its own column (no US counterpart) and
never added to the public (b) share or subtracted from it. Evidence: Q7_EVIDENCE.md. The end of state guarantees in
2005 is sourced for public-law banks (savings banks, Landesbanken); for promotional banks no source on guarantees was
read, so their part is reported separately (de_promotional_banks_share) until Eleonora confirms the scope.

Output: comparison.csv, results.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path: Path = HERE / "national_figures.csv") -> pd.DataFrame:
    f = pd.read_csv(path)
    num = f[f["unit"] != "text"]
    assert num["url"].str.startswith("https://").all() and num["sha256"].str.fullmatch(r"[0-9a-f]{64}").all(), \
        "every number needs a URL and a SHA-256"
    return f


def v(f: pd.DataFrame, country: str, item: str) -> float:
    r = f[(f.country == country) & (f.item == item)]
    assert len(r) == 1, (country, item)
    return float(r["value"].iloc[0])


# US holder measure (a): not computed. The project's public bucket counts GSE and agency MBS as public because they
# are guaranteed, but most of those securities are held by private investors. Since FAS 166/167 (2010Q1) Z.1 carries
# the Enterprises' consolidated MBS trusts inside their own balance-sheet lines (A1, Limits), so the series used here
# cannot separate retained holdings from guaranteed MBS held by investors. A first attempt that subtracted only the
# pool sector (sector 41) gave a figure that still included most investor-held MBS; it was discarded before use.


def compare(f: pd.DataFrame, a2: dict) -> pd.DataFrame:
    rows = []
    # US: Z.1 holder share; risk-bearer range net of CRT from A2 (FHA/VA loans held privately are not added back).
    rows.append(dict(country="US", date="2025Q4", holder_a=math.nan,
                     public_bucket_incl_pools=a2["public_share_gross_pct_last"] / 100,
                     risk_b_low=a2["public_share_net_lower_pct_last"] / 100,
                     risk_b_high=a2["freddie_10k"]["public_share_net_freddie_crt_pct_last"] / 100,
                     note="(a) not computable from Z.1 after FAS 166/167; (b) public bucket (holders and guaranteed pools), net of CRT (A2)"))
    # Canada: CMHC states its insured share of residential mortgages; no national source converts it to household credit.
    ca_total = v(f, "CA", "mortgages_household") + v(f, "CA", "consumer_credit_household")
    rows.append(dict(country="CA", date="2025-12", holder_a=math.nan, risk_b_low=math.nan, risk_b_high=math.nan,
                     cmhc_share_of_residential_mortgages=v(f, "CA", "cmhc_share_of_residential_mortgages"),
                     household_credit_lcu_m=ca_total,
                     note="(b) not computed: CMHC insurance-in-force includes multi-unit rental and private insurers' "
                          "federally backed cover is not sourced; CMHC's own share of residential mortgages shown instead"))
    # Denmark: mortgage-bank loans carry no public credit risk (Nationalbank); the state lends to households only via SU loans (not sourced).
    dk_mb, dk_b = v(f, "DK", "mortgage_bank_loans_households"), v(f, "DK", "bank_loans_households")
    rows.append(dict(country="DK", date="2025-12", holder_a=math.nan, risk_b_low=math.nan, risk_b_high=math.nan,
                     private_mortgage_bank_share=dk_mb / (dk_mb + dk_b), household_credit_lcu_m=dk_mb + dk_b,
                     note="(a), (b) not computed: SU student loans (state) not sourced; mortgage-bank and bank loans carry no public credit risk"))
    rows.append(dict(country="UK", date="2025-12", holder_a=math.nan, risk_b_low=math.nan, risk_b_high=math.nan,
                     household_credit_lcu_m=v(f, "UK", "lending_to_individuals_excl_student_loans"),
                     note="not computed: student loans (government) are excluded from the BoE total and their stock is not sourced (gov.uk blocked)"))
    de_tot = v(f, "DE", "bank_lending_individuals_all_banks")
    de_pub = (v(f, "DE", "savings_banks_lending_individuals") + v(f, "DE", "landesbanken_lending_individuals")
              + v(f, "DE", "promotional_banks_lending_individuals"))
    assert 0 < de_pub < de_tot
    # Q7 (c): the same banks' lending is the third category on the risk-bearer measure; it stays out of risk_b_*.
    de_promo = v(f, "DE", "promotional_banks_lending_individuals")
    rows.append(dict(country="DE", date="2025Q4", holder_a=de_pub / de_tot, risk_b_low=math.nan, risk_b_high=math.nan,
                     public_owned_not_guaranteed=de_pub / de_tot,
                     public_owned_excl_promotional=(de_pub - de_promo) / de_tot,
                     promotional_banks_share=de_promo / de_tot,
                     household_credit_lcu_m=de_tot,
                     note="(a) savings banks + Landesbanken + promotional banks (public building-savings banks not separable), bank lending to employees and other individuals; "
                          "(b) these banks' lending is a third category, publicly owned, not guaranteed (Q7 c); public (b) share not computed: "
                          "BAföG not sourced; KfW loans carry the on-lending bank's liability"))
    t = pd.DataFrame(rows).set_index("country")
    for c in ("holder_a", "risk_b_low", "risk_b_high", "public_owned_not_guaranteed",
              "public_owned_excl_promotional", "promotional_banks_share"):
        ok = t[c].dropna()
        assert ((ok >= 0) & (ok <= 1)).all(), c
    de = t.loc["DE"]
    assert math.isclose(de.public_owned_excl_promotional + de.promotional_banks_share, de.public_owned_not_guaranteed)
    us = t.loc["US"]
    assert us.risk_b_low <= us.risk_b_high <= us.public_bucket_incl_pools
    return t


def main() -> int:
    f = load()
    a2 = json.loads((ROOT / "research" / "a2_net_exposure" / "results.json").read_text())
    t = compare(f, a2)
    t.round(4).to_csv(HERE / "comparison.csv")
    res = {"label": "A8 comparison, 2025 year end; a missing key = not computable from a national source",
           **{f"{c.lower()}_{k}": (None if pd.isna(x) else round(float(x), 4))
              for c, row in t.iterrows() for k, x in row.items() if k not in ("note", "date") and not pd.isna(x)}}
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
