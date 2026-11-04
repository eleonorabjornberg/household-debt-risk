#!/usr/bin/env python3
"""A5 Q4 (Eleonora, 2026-11-04: option c, with option b beside it): ESTIMATED public exposure by borrower group, 2026Q2.

    uv run --project pipeline python research/a5_distribution/public_by_group.py [--z1-zip PATH]

No source crosses borrower group with holder (AVAILABILITY.md). This script IMPUTES it, two ways, and labels both as
estimates:

  (b) uniform holder mix: public_g = M_g * p_M + CC_g * p_CC
        M_g, CC_g  DFA home mortgages and consumer credit owed by group g (2026Q2)
        p_M, p_CC  Z.1 public share of household mortgages and of consumer credit (2026Q2)
  (c) student loans split out: public_g = M_g * p_M + S_g * SL * p_SL
        SL         Z.1 household student loans (FL153166220), p_SL = federal (FL313066220 + FL403066005) / SL
        S_g        group g's share of student-loan debt in the 2025 Survey of Consumer Finances (EDN_INST, weighted)
      In the project's scope all public consumer credit is student loans, so (c) moves public consumer credit to the
      groups that owe student loans instead of spreading it over all consumer credit.

Assumptions shared by both (stated in the README, not tested here): within mortgages the public share is the same
for every group (FHA/VA borrowers, who skew lower-income, are not separated: this understates public exposure at the
bottom); in (c) the federal share of student loans is the same for every group. Groups: wealth (DFA Bottom50, Next40,
Next9, Top1 = RemainingTop1 + TopPt1) and income (DFA quintiles with the top split 80-99 / 99-100). SCF groups are cut
at the same weighted percentiles of NETWORTH or INCOME across all five implicates.

Checks: group exposures add up to the Z.1 public total for mortgages + consumer credit (both methods); (c)'s imputed
student loans S_g * SL never exceed the group's DFA consumer credit; SCF and DFA consumer-credit group shares are
reported side by side as a plausibility check (not asserted: DFA is calibrated to earlier SCF waves).

Output: public_by_group.csv, and results_public_by_group.json (results.json is distribution.py's).
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from distribution import DATA, a1, fetch, read_dfa, sha256  # noqa: E402

SCF_URL = "https://www.federalreserve.gov/econres/files/scfp2025excel.zip"
WHEN = "2026:Q2"
GROUPS = {
    "wealth": ("networth", "NETWORTH", [("Bottom50", ["Bottom50"], 0, 50), ("Next40", ["Next40"], 50, 90),
                                         ("Next9", ["Next9"], 90, 99), ("Top1", ["RemainingTop1", "TopPt1"], 99, 100)]),
    "income": ("income", "INCOME", [("pct00to20", ["pct00to20"], 0, 20), ("pct20to40", ["pct20to40"], 20, 40),
                                     ("pct40to60", ["pct40to60"], 40, 60), ("pct60to80", ["pct60to80"], 60, 80),
                                     ("pct80to99", ["pct80to99"], 80, 99), ("pct99to100", ["pct99to100"], 99, 100)]),
}
SCF_CC = ["CCBAL", "VEH_INST", "EDN_INST", "OTH_INST"]


def wquantile(x: np.ndarray, w: np.ndarray, q: float) -> float:
    o = np.argsort(x)
    cw = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(cw, q / 100.0)]) if q < 100 else float(np.inf)


def scf_shares(scf: pd.DataFrame, var: str, groups) -> pd.DataFrame:
    x, w = scf[var].to_numpy(float), scf["WGT"].to_numpy(float)
    out = {}
    for name, _, lo, hi in groups:
        a = -np.inf if lo == 0 else wquantile(x, w, lo)
        b = wquantile(x, w, hi)
        m = (x >= a) & (x < b) if hi < 100 else (x >= a)
        out[name] = {"student": (scf.loc[m, "EDN_INST"] * scf.loc[m, "WGT"]).sum(),
                     "cc": (scf.loc[m, SCF_CC].sum(axis=1) * scf.loc[m, "WGT"]).sum(),
                     "pop": scf.loc[m, "WGT"].sum()}
    t = pd.DataFrame(out).T
    for c in ("student", "cc", "pop"):
        t[c] = t[c] / t[c].sum()
    return t


def z1_inputs(z1_zip: Path) -> dict:
    df, mh, ch, public, labels = a1.load(z1_zip)
    c = a1.cells(df, mh, ch, public, labels)
    t = a1.q_end("2026Q2")
    row = c.loc[t]
    mort, cc = row.xs("mortgages", level="loan"), row.xs("consumer credit", level="loan")
    from distribution import a1 as _a1  # noqa: F401  (same module)
    sl = a1.zparse.load_z1_zip(z1_zip, ["FL153166220", "FL313066220", "FL403066005"])
    sl = pd.DataFrame(sl[0] if isinstance(sl, tuple) else sl).sort_index()
    sl.index = pd.to_datetime(sl.index)
    s = sl.loc[t]
    return {"p_M": mort.xs("public", level="side").sum() / mort.sum(),
            "p_CC": cc.xs("public", level="side").sum() / cc.sum(),
            "public_cc": cc.xs("public", level="side").sum(),
            "public_mort": mort.xs("public", level="side").sum(),
            "SL": s["FL153166220"], "SL_public": s["FL313066220"] + s["FL403066005"]}


def estimate(dfa_levels: pd.DataFrame, scf_t: pd.DataFrame, groups, z: dict) -> pd.DataFrame:
    lv = dfa_levels[dfa_levels["Date"] == WHEN].set_index("Category")
    rows = []
    for name, cats, _, _ in groups:
        M, CC = lv.loc[cats, "Home mortgages"].sum(), lv.loc[cats, "Consumer credit"].sum()
        S = scf_t.at[name, "student"]
        sl_g = S * z["SL"]
        rows.append({"group": name, "mortgages_musd": M, "consumer_credit_musd": CC, "scf_student_share": S,
                     "imputed_student_loans_musd": sl_g,
                     "public_b_musd": M * z["p_M"] + CC * z["p_CC"],
                     "public_c_musd": M * z["p_M"] + sl_g * z["SL_public"] / z["SL"]})
    t = pd.DataFrame(rows).set_index("group")
    for k in ("b", "c"):
        t[f"public_{k}_share_of_total"] = t[f"public_{k}_musd"] / t[f"public_{k}_musd"].sum()
        t[f"public_{k}_pct_of_group_debt"] = t[f"public_{k}_musd"] / (t["mortgages_musd"] + t["consumer_credit_musd"])
    return t


def check(t: pd.DataFrame, z: dict) -> None:
    target_b = z["public_mort"] + z["public_cc"]
    assert abs(t["public_b_musd"].sum() - target_b) / target_b < 1e-6, "(b) does not add up to the Z.1 public total"
    # (c) allocates all Z.1 public student loans; in scope, public consumer credit = public student loans.
    assert abs(z["SL_public"] - z["public_cc"]) < 1.0, "public consumer credit is not all student loans"
    assert abs(t["public_c_musd"].sum() - target_b) / target_b < 1e-6, "(c) does not add up to the Z.1 public total"
    over = t["imputed_student_loans_musd"] > t["consumer_credit_musd"]
    assert not over.any(), f"imputed student loans exceed DFA consumer credit for {list(t.index[over])}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    ns = ap.parse_args(argv)
    scf_zip = fetch(SCF_URL, DATA / "scfp2025excel.zip")
    dfa_zip = DATA / "dfa.zip"
    with zipfile.ZipFile(scf_zip) as zf:
        scf = pd.read_csv(io.BytesIO(zf.read("SCFP2025.csv")), usecols=["WGT", "NETWORTH", "INCOME"] + SCF_CC)
    z = z1_inputs(ns.z1_zip)
    tables, res = [], {"label": "ESTIMATE (imputed across DFA, SCF 2025 and Z.1; see public_by_group.py)",
                       "sha256_scf_zip": sha256(scf_zip), "vintage_scf": "SCF 2025 summary extract (scfp2025excel.zip)",
                       "p_M": round(float(z["p_M"]), 4), "p_CC": round(float(z["p_CC"]), 4),
                       "federal_share_of_student_loans": round(float(z["SL_public"] / z["SL"]), 4)}
    for grouping, (stem, var, groups) in GROUPS.items():
        st = scf_shares(scf, var, groups)
        t = estimate(read_dfa(dfa_zip, f"dfa-{stem}-levels.csv"), st, groups, z)
        check(t, z)
        dfa_cc_share = t["consumer_credit_musd"] / t["consumer_credit_musd"].sum()
        t["scf_cc_share"] = st["cc"]
        t["dfa_cc_share"] = dfa_cc_share
        t.insert(0, "grouping", grouping)
        tables.append(t)
        res[grouping] = {g: {"public_b_share": round(float(t.at[g, "public_b_share_of_total"]), 4),
                             "public_c_share": round(float(t.at[g, "public_c_share_of_total"]), 4),
                             "public_b_pct_of_debt": round(float(t.at[g, "public_b_pct_of_group_debt"]), 4),
                             "public_c_pct_of_debt": round(float(t.at[g, "public_c_pct_of_group_debt"]), 4),
                             "scf_student_share": round(float(t.at[g, "scf_student_share"]), 4)}
                         for g in t.index}
    out = pd.concat(tables)
    out.round(4).to_csv(HERE / "public_by_group.csv")
    (HERE / "results_public_by_group.json").write_text(json.dumps(res, indent=1) + "\n")
    print(out[["grouping", "scf_student_share", "public_b_share_of_total", "public_c_share_of_total",
               "public_b_pct_of_group_debt", "public_c_pct_of_group_debt", "scf_cc_share", "dfa_cc_share"]].round(3).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
