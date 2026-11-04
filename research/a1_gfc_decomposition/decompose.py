#!/usr/bin/env python3
"""PLAN task A1: decompose the 2007Q4-2011Q4 jump in the public share by loan type x holder.

    uv run --project pipeline python research/a1_gfc_decomposition/decompose.py [--z1-zip PATH] [--t0 2007Q4] [--t1 2011Q4]

Reads the Fed's Z.1 zip (default data/validation/FRB_Z1_csv.zip, as validation/run.py downloads it) with
validation/zparse.py, and the holder -> bucket mapping from pipeline/series_catalog.yaml. Shares are computed
exactly as validation/run.py `compute` does (mortgage holders apportioned to the household liability with
FL153165105 / FL893065105), so the total reproduces validation check C5.

Method (decided by Eleonora, 2026-11-04): Shapley. With public P = Pub/S, scope S = Pub + Priv, and
f(a, b) = a / (a + b), the public side's contribution is the average of its two possible orderings:
    C_pub  = 1/2 * [ (f(Pub1, Priv0) - f(Pub0, Priv0)) + (f(Pub1, Priv1) - f(Pub0, Priv1)) ]
    C_priv = (P1 - P0) - C_pub        (the same formula with the roles swapped)
Exact, and independent of which side is counted first. Within each side, the share depends on the cells only
through the side's total, so each cell gets the side's contribution in proportion to its change in holdings
(dx_i / dPub or dx_j / dPriv; the Aumann-Shapley allocation for a function of a sum). A private retreat
raises the share.
Sensitivity (results.json "sensitivity"): the endpoint-weighted identity
    P1 - P0 = (1 - P0) * dPub / S1  -  P0 * dPriv / S1
and the quarterly-chained Shapley path. All are exact for the total; they split it differently (review-log
R-20261104-1), which is why the method was fixed before the write-up.
Per-quarter paths chain the Shapley split quarter by quarter, so each component's timing can be read against
policy dates. Group totals in path.csv at t1 differ from the endpoint figures in results.json.

Outputs (next to this file): decomposition.csv (endpoint, one row per cell), path.csv (cumulative chained
contributions by quarter), results.json (headline numbers for the claims register).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "validation"))
import zparse  # noqa: E402

# Public cells, finer than the catalog's buckets. Each is a sum of Z.1 holder series (asset side, $M).
# Mortgage cells are apportioned to households like every other mortgage holder.
# Fannie/Freddie combine portfolio and pools because FAS 166/167 (2010Q1) moved pool MBS onto the GSEs'
# balance sheets (sector 41 -> 40); split apart, the two lines would show a +/-$4T accounting swap.
PUBLIC_MORT = {
    "Fannie Mae (portfolio + pools)": ["+FL403065110", "+FL413065143"],
    "Freddie Mac (portfolio + pools)": ["+FL403065120", "+FL413065123"],
    "Ginnie Mae pools (FHA, VA, USDA) and FmHA pools": ["+FL413065110", "+FL413065133"],
    "Federal Home Loan Banks": ["+FL403065130"],
    "Other GSEs (Farm Credit System and unallocated)": ["+FL403065105", "-FL403065110", "-FL403065120", "-FL403065130"],
    "Federal government (direct)": ["+FL313065105"],
    "State and local governments": ["+FL213065103"],
}
PUBLIC_CC = {
    "Federal government (student loans)": ["+FL313066220"],
    "Sallie Mae as a GSE": ["+FL403066005"],
}
TOTALS = ["FL154104015", "FL153165105", "FL153166000", "FL893065105"]


def q(ts) -> str:
    ts = pd.Timestamp(ts)
    return f"{ts.year}Q{ts.quarter}"


def q_end(label: str) -> pd.Timestamp:
    return pd.Period(label, freq="Q").end_time.normalize()


def load(zip_path: Path):
    cat = yaml.safe_load((ROOT / "pipeline" / "series_catalog.yaml").read_text())
    rows = [s for s in cat["series"] if s["source"] == "z1"]
    public = {k for k, v in cat["risk_buckets"].items() if v["public"]}
    labels = {k: v["label"] for k, v in cat["risk_buckets"].items()}
    mh = [s for s in rows if s["role"] == "mortgage_holder"]
    ch = [s for s in rows if s["role"] == "cc_holder"]
    ids = set(TOTALS) | {s["id"] for s in mh + ch}
    for spec in list(PUBLIC_MORT.values()) + list(PUBLIC_CC.values()):
        ids |= {x[1:] for x in spec}
    ser = zparse.load_z1_zip(zip_path, sorted(ids))
    if isinstance(ser, tuple):
        ser = ser[0]
    df = pd.DataFrame(ser).sort_index()
    df.index = pd.to_datetime(df.index)
    return df, mh, ch, public, labels


def combo(df, spec):
    out = 0.0
    for x in spec:
        out = out + (df[x[1:]] if x[0] == "+" else -df[x[1:]])
    return out


def cells(df, mh, ch, public, labels) -> pd.DataFrame:
    """$M held by each cell, household-apportioned. Columns: (loan, side, holder)."""
    a = df["FL153165105"] / df["FL893065105"]
    out = {}
    for name, spec in PUBLIC_MORT.items():
        out[("mortgages", "public", name)] = combo(df, spec) * a
    for name, spec in PUBLIC_CC.items():
        out[("consumer credit", "public", name)] = combo(df, spec)
    for s in mh:
        if s["risk_bucket"] not in public:
            out[("mortgages", "private", f'{labels[s["risk_bucket"]]}: {s["desc"]}')] = df[s["id"]] * a
    for s in ch:
        if s["risk_bucket"] not in public:
            out[("consumer credit", "private", f'{labels[s["risk_bucket"]]}: {s["desc"]}')] = df[s["id"]]
    c = pd.DataFrame(out)
    c.columns = pd.MultiIndex.from_tuples(c.columns, names=["loan", "side", "holder"])
    return c


def identity(c0: pd.Series, c1: pd.Series) -> pd.Series:
    """Endpoint-weighted identity (sensitivity only): exact contributions (pp) to P1 - P0."""
    pub0 = c0.xs("public", level="side").sum()
    s0, s1 = c0.sum(), c1.sum()
    p0 = pub0 / s0
    d = c1 - c0
    w = pd.Series([(1 - p0) if side == "public" else -p0 for side in d.index.get_level_values("side")], index=d.index)
    return 100 * w * d / s1


def shapley(c0: pd.Series, c1: pd.Series) -> pd.Series:
    """Shapley contributions (pp) of each cell to P1 - P0: two-player Shapley between the public and private
    totals, then pro rata within each side by the change in holdings."""
    side = c0.index.get_level_values("side")
    pub0, priv0 = c0[side == "public"].sum(), c0[side == "private"].sum()
    pub1, priv1 = c1[side == "public"].sum(), c1[side == "private"].sum()
    f = lambda a, b: a / (a + b)  # noqa: E731
    total = f(pub1, priv1) - f(pub0, priv0)
    c_pub = 0.5 * ((f(pub1, priv0) - f(pub0, priv0)) + (f(pub1, priv1) - f(pub0, priv1)))
    c_priv = total - c_pub
    d = c1 - c0
    out = pd.Series(0.0, index=d.index)
    for name, c_side, d_side in (("public", c_pub, pub1 - pub0), ("private", c_priv, priv1 - priv0)):
        m = side == name
        if d_side != 0:
            out[m] = c_side * d[m] / d_side
        else:
            assert abs(c_side) < 1e-15
    return 100 * out


contrib = shapley  # the method used for every headline figure


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    ap.add_argument("--t0", default="2007Q4")
    ap.add_argument("--t1", default="2011Q4")
    a = ap.parse_args(argv)
    if not a.z1_zip.exists():
        print(f"{a.z1_zip} not found; run validation/run.py first (it downloads the zip).", file=sys.stderr)
        return 2
    vintage = zparse.zip_member_info(a.z1_zip)
    df, mh, ch, public, labels = load(a.z1_zip)
    c = cells(df, mh, ch, public, labels)
    t0, t1 = q_end(a.t0), q_end(a.t1)

    # Checks: cells reproduce scope and the public share exactly as validation computes them.
    scope_gap = (c.sum(axis=1) - df["FL154104015"]).loc[t0:t1].abs().max()  # every quarter in the window
    share = c.xs("public", level="side", axis=1).sum(axis=1) / c.sum(axis=1)
    p0, p1 = share.loc[t0], share.loc[t1]
    total_pp = 100 * (p1 - p0)
    assert scope_gap < 1e-3, f"cells do not reproduce the scope total: {scope_gap} $M"

    con = contrib(c.loc[t0], c.loc[t1])
    gap = abs(con.sum() - total_pp)
    assert gap < 1e-9, f"decomposition does not sum: {gap}"

    tab = pd.DataFrame({
        f"usd_bn_{a.t0}": c.loc[t0] / 1e3,
        f"usd_bn_{a.t1}": c.loc[t1] / 1e3,
        "change_usd_bn": (c.loc[t1] - c.loc[t0]) / 1e3,
        "contribution_pp": con,
    }).reset_index()
    tab = tab[(tab[f"usd_bn_{a.t0}"].abs() > 0.05) | (tab[f"usd_bn_{a.t1}"].abs() > 0.05)]
    tab = tab.sort_values(["side", "contribution_pp"], ascending=[False, False])
    tab.round(4).to_csv(HERE / "decomposition.csv", index=False)

    # Chained quarterly path, cumulative from t0.
    idx = c.loc[t0:t1].index
    steps = [contrib(c.loc[idx[i - 1]], c.loc[idx[i]]) for i in range(1, len(idx))]
    path = pd.DataFrame(steps, index=[q(t) for t in idx[1:]]).cumsum()
    groups = {
        "fannie_freddie": [k for k in path.columns if k[1] == "public" and ("Fannie" in k[2] or "Freddie" in k[2])],
        "ginnie_pools": [k for k in path.columns if k[1] == "public" and "Ginnie" in k[2]],
        "federal_student_loans": [k for k in path.columns if k[2] == "Federal government (student loans)"],
        "other_public": [k for k in path.columns if k[1] == "public" and not any(
            s in k[2] for s in ("Fannie", "Freddie", "Ginnie", "student loans"))],
        "private_label_and_mreits": [k for k in path.columns if k[1] == "private" and "Private securitization" in k[2]],
        "banks_and_credit_unions": [k for k in path.columns if k[1] == "private" and "Banks" in k[2]],
        "other_private": [k for k in path.columns if k[1] == "private" and "Private securitization" not in k[2] and "Banks" not in k[2]],
    }
    flat = [k for cols in groups.values() for k in cols]
    assert len(flat) == len(set(flat)) == len(path.columns), "groups must partition the cells"
    gpath = pd.DataFrame({g: path[cols].sum(axis=1) for g, cols in groups.items()})
    gpath["total"] = gpath.sum(axis=1)
    gpath["public_share_pct"] = [100 * share.loc[t] for t in idx[1:]]
    assert abs(gpath["total"].iloc[-1] - total_pp) < 1e-9
    gpath.round(4).to_csv(HERE / "path.csv", index_label="quarter")

    # View 2: each public cell's own share change, d(x_i / S). Sums exactly to P1 - P0 over public cells;
    # the private retreat is folded into every public cell through the shared denominator.
    own = 100 * (c.loc[t1] / c.loc[t1].sum() - c.loc[t0] / c.loc[t0].sum())
    own_pub = own.xs("public", level="side", drop_level=False)
    assert abs(own_pub.sum() - total_pp) < 1e-9
    tab_own = own_pub.rename("own_share_change_pp").reset_index()
    tab_own = tab_own[tab_own["own_share_change_pp"].abs() > 1e-6].sort_values("own_share_change_pp", ascending=False)
    tab_own.round(4).to_csv(HERE / "own_share_change.csv", index=False)

    endpoint_groups = {g: float(con[cols].sum()) for g, cols in groups.items()}
    ident = identity(c.loc[t0], c.loc[t1])
    assert abs(ident.sum() - total_pp) < 1e-9
    sides = lambda s_: {"public_pp": round(float(s_.xs("public", level="side").sum()), 6),  # noqa: E731
                        "private_pp": round(float(s_.xs("private", level="side").sum()), 6)}
    chained_end = path.iloc[-1]
    res = {
        "vintage_z1_csv": vintage[0].isoformat(sep=" "),
        "t0": a.t0, "t1": a.t1,
        "public_share_t0": round(float(p0), 6), "public_share_t1": round(float(p1), 6),
        "total_pp": round(float(total_pp), 6),
        "sum_of_cells_minus_total_pp": float(gap),
        "scope_reconstruction_max_abs_musd": float(scope_gap),
        "from_public_growth_pp": round(float(con.xs("public", level="side").sum()), 6),
        "from_private_change_pp": round(float(con.xs("private", level="side").sum()), 6),
        "groups_pp": {k: round(v, 6) for k, v in endpoint_groups.items()},
        "method": "shapley (public vs private totals; pro rata within each side)",
        "sensitivity": {
            "endpoint_identity": {**sides(ident),
                                  "groups_pp": {g: round(float(ident[cols].sum()), 6) for g, cols in groups.items()}},
            "chained_quarterly_shapley": {**sides(chained_end),
                                          "groups_pp": {g: round(float(chained_end[cols].sum()), 6) for g, cols in groups.items()}},
        },
        "own_share_change_pp": {k: round(float(own_pub[cols].sum()), 6) for k, cols in groups.items() if k in
                                ("fannie_freddie", "ginnie_pools", "federal_student_loans", "other_public")},
        "change_usd_bn": {
            "fannie_freddie": round(float(sum((c.loc[t1] - c.loc[t0])[k] for k in groups["fannie_freddie"]) / 1e3), 3),
            "ginnie_pools": round(float(sum((c.loc[t1] - c.loc[t0])[k] for k in groups["ginnie_pools"]) / 1e3), 3),
            "federal_student_loans": round(float(sum((c.loc[t1] - c.loc[t0])[k] for k in groups["federal_student_loans"]) / 1e3), 3),
            "private_label_and_mreits": round(float(sum((c.loc[t1] - c.loc[t0])[k] for k in groups["private_label_and_mreits"]) / 1e3), 3),
        },
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
