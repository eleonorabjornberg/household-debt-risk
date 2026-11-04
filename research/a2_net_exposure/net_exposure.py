#!/usr/bin/env python3
"""PLAN task A2: gross vs net public exposure to household mortgage credit risk, 2013-2025 (year ends).

    uv run --project pipeline python research/a2_net_exposure/net_exposure.py [--z1-zip PATH]

Gross: what the public sector holds, from the Fed's Z.1 exactly as A1 builds it (household-apportioned cells,
reusing research/a1_gfc_decomposition/decompose.py). Fannie Mae + Freddie Mac = portfolio + pools.

Transferred: Fannie and Freddie single-family credit risk transfer (CRT: STACR, CAS, CIRT, ACIS, lender risk
sharing, senior/subordinate), from FHFA's CRT Progress Reports and Reports to Congress, transcribed in
crt_fhfa.csv. FHFA publishes risk in force (RIF) AT ISSUANCE, cumulative since 2013. It does not publish how much
of that RIF is still outstanding (that is in the Enterprises' 10-K/10-Q and deal data, not reachable from this
environment). RIF only falls after issuance (principal paydown, write-downs, calls, terminations), so

    outstanding CRT RIF at t  <=  cumulative issued CRT RIF through t                      (1)

and therefore, with G = gross Fannie/Freddie holdings,

    G - cumulative CRT RIF  <=  net Fannie/Freddie exposure  <=  G                        (2)

This script reports the two sides of (2), in dollars and as shares of household mortgages + consumer credit
(the project's scope S). It does NOT estimate where inside the bounds the truth lies; that needs a runoff
assumption, which is a design choice left to Eleonora (README, "Questions").

Primary mortgage insurance (PMI) is reported alongside, but NOT as a bound: FHFA's PMI figures are RIF at
acquisition for loans acquired 2013-2023 only, so they leave out PMI on loans acquired before 2013 (understates)
and keep PMI on loans that have paid off or cancelled cover (overstates). The Enterprise also keeps the
counterparty risk on PMI (FHFA, CRT Progress Report 4Q23 p.12).

Both CRT and PMI amounts are apportioned to households with the same ratio as the Z.1 holdings
(FL153165105 / FL893065105), assuming the CRT-covered book has the same household/business mix.

Units: RIF is a maximum loss-absorbing amount; G is unpaid principal. Subtracting one from the other answers
"how much of the principal could lose money for the public sector at most", not "how much expected loss was
transferred". See METHOD.md.

Outputs (next to this file): net_exposure.csv (one row per year end), results.json (headline numbers).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

_spec = importlib.util.spec_from_file_location("a1_decompose", ROOT / "research" / "a1_gfc_decomposition" / "decompose.py")
a1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a1)  # also puts validation/ on sys.path for zparse

FF = ("Fannie Mae (portfolio + pools)", "Freddie Mac (portfolio + pools)")


def load_crt(path: Path = HERE / "crt_fhfa.csv") -> pd.DataFrame:
    crt = pd.read_csv(path).set_index("year")
    # Internal consistency of the transcription: cumulative RIF must not fall, and where both a cumulative and the
    # next year's annual flow are published, cum[t-1] + annual[t] must equal cum[t] within revision/rounding noise.
    rif = crt["cum_rif_musd"]
    assert rif.is_monotonic_increasing, "cumulative CRT RIF falls in the transcription"
    for y in crt.index[1:]:
        ann = crt.at[y, "annual_rif_musd"]
        if pd.notna(ann):
            gap = abs(rif[y - 1] + ann - rif[y])
            tol = max(1000.0, 0.01 * rif[y])  # $1bn or 1%: 2024-25 cumulative figures are published rounded to $1bn
            assert gap <= tol, f"CRT transcription inconsistent at {y}: gap {gap:.0f} $M"
    pmi = crt["cum_pmi_rif_musd"].dropna()
    assert pmi.is_monotonic_increasing, "cumulative PMI RIF falls in the transcription"
    return crt


def bounds(g: pd.Series, pub: pd.Series, s: pd.Series, a: pd.Series, crt: pd.DataFrame) -> pd.DataFrame:
    """Year-end table. g, pub, s in $M (household-apportioned), a = household apportionment ratio, indexed by year."""
    out = pd.DataFrame(index=crt.index)
    out["gross_ff_bn"] = g / 1e3
    out["cum_crt_rif_hh_bn"] = crt["cum_rif_musd"] * a / 1e3
    out["net_ff_lower_bn"] = out["gross_ff_bn"] - out["cum_crt_rif_hh_bn"]
    out["net_ff_upper_bn"] = out["gross_ff_bn"]
    out["crt_bound_pct_of_gross"] = 100 * out["cum_crt_rif_hh_bn"] / out["gross_ff_bn"]
    out["public_share_gross_pct"] = 100 * pub / s
    out["public_share_net_lower_pct"] = 100 * (pub - crt["cum_rif_musd"] * a) / s
    out["cum_pmi_rif_hh_bn"] = crt["cum_pmi_rif_musd"] * a / 1e3
    out["pmi_issued_pct_of_gross"] = 100 * out["cum_pmi_rif_hh_bn"] / out["gross_ff_bn"]
    out["cum_crt_ref_upb_over_gross"] = crt["cum_ref_upb_musd"] * a / g
    out["hh_apportion_ratio"] = a
    return out


def check(t: pd.DataFrame) -> None:
    assert (t["net_ff_lower_bn"] <= t["gross_ff_bn"] + 1e-9).all(), "net exceeds gross"
    assert (t["net_ff_lower_bn"] > 0).all(), "lower bound on net exposure is negative"
    assert (t["public_share_net_lower_pct"] <= t["public_share_gross_pct"] + 1e-12).all()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    ns = ap.parse_args(argv)
    if not ns.z1_zip.exists():
        print(f"{ns.z1_zip} not found; run validation/run.py first (it downloads the zip).", file=sys.stderr)
        return 2
    vintage = a1.zparse.zip_member_info(ns.z1_zip)
    df, mh, ch, public, labels = a1.load(ns.z1_zip)
    c = a1.cells(df, mh, ch, public, labels)
    crt = load_crt()

    # Same scope and share as A1 / validation: the cells must reproduce the scope total at every year end used.
    ends = [a1.q_end(f"{y}Q4") for y in crt.index]
    scope_gap = (c.sum(axis=1) - df["FL154104015"]).loc[ends].abs().max()
    assert scope_gap < 1e-3, f"cells do not reproduce the scope total: {scope_gap}"
    pub_cols = [k for k in c.columns if k[1] == "public"]
    ff_cols = [k for k in pub_cols if k[2] in FF]
    assert len(ff_cols) == 2
    yr = pd.Index(crt.index, name="year")
    g = pd.Series(c.loc[ends, ff_cols].sum(axis=1).values, index=yr)
    pub = pd.Series(c.loc[ends, pub_cols].sum(axis=1).values, index=yr)
    s = pd.Series(c.loc[ends].sum(axis=1).values, index=yr)
    a = pd.Series((df["FL153165105"] / df["FL893065105"]).loc[ends].values, index=yr)

    t = bounds(g, pub, s, a, crt)
    check(t)
    t.round(4).to_csv(HERE / "net_exposure.csv")

    last = int(t.index.max())
    pmi_last = int(t["cum_pmi_rif_hh_bn"].last_valid_index())
    r = lambda x, n=4: round(float(x), n)  # noqa: E731
    res = {
        "vintage_z1_csv": vintage[0].isoformat(sep=" "),
        "crt_source": "FHFA CRT Progress Reports Dec 2016-4Q23; FHFA Reports to Congress 2024, 2025 (crt_fhfa.csv)",
        "years": [int(t.index.min()), last],
        "last_year": last,
        "gross_ff_bn_last": r(t.at[last, "gross_ff_bn"], 1),
        "cum_crt_rif_bn_last_unapportioned": r(crt.at[last, "cum_rif_musd"] / 1e3, 1),
        "cum_crt_rif_hh_bn_last": r(t.at[last, "cum_crt_rif_hh_bn"], 1),
        "net_ff_lower_bn_last": r(t.at[last, "net_ff_lower_bn"], 1),
        "crt_bound_pct_of_gross_last": r(t.at[last, "crt_bound_pct_of_gross"], 3),
        "crt_bound_pct_of_gross_max": r(t["crt_bound_pct_of_gross"].max(), 3),
        "crt_bound_pct_of_gross_max_year": int(t["crt_bound_pct_of_gross"].idxmax()),
        "public_share_gross_pct_last": r(t.at[last, "public_share_gross_pct"], 3),
        "public_share_net_lower_pct_last": r(t.at[last, "public_share_net_lower_pct"], 3),
        "public_share_gap_pp_last": r(t.at[last, "public_share_gross_pct"] - t.at[last, "public_share_net_lower_pct"], 3),
        "public_share_gross_pct_2013": r(t.at[2013, "public_share_gross_pct"], 3),
        "pmi_last_year": pmi_last,
        "cum_pmi_rif_bn_unapportioned_pmi_last": r(crt.at[pmi_last, "cum_pmi_rif_musd"] / 1e3, 1),
        "pmi_issued_pct_of_gross_pmi_last": r(t.at[pmi_last, "pmi_issued_pct_of_gross"], 3),
        "cum_crt_ref_upb_over_gross_last": r(t.at[last, "cum_crt_ref_upb_over_gross"], 3),
        "checks": {
            "net_le_gross_all_years": True,
            "net_lower_positive_all_years": True,
            "scope_reconstruction_max_abs_musd": float(scope_gap),
        },
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
