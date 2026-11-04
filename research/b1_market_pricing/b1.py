#!/usr/bin/env python3
"""PLAN task B1: mortgage-rate spreads over Treasuries and the public share of household mortgages.

    uv run --project pipeline python research/b1_market_pricing/b1.py [--z1-zip PATH]

Specification fixed in METHOD.md before this script was first run. Reads:
  - Z.1 zip (default data/validation/FRB_Z1_csv.zip, as validation/run.py downloads it); shares at catalog
    level, as validation/run.py computes them (since 6a161c7; see public_shares);
  - FRED series through research/common/fred.py (raw JSON cached in data/fred/ with a SHA-256 manifest).

Writes next to this file: regressions.csv (every specification, every coefficient), spreads_summary.csv
(descriptive means by period), results.json (headline numbers for the claims register).
The quarterly panel (third-party rates: Freddie Mac, Optimal Blue, Moody's) is written to data/b1/panel.csv,
outside git: FRED series from those publishers are linked, not redistributed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "common"))
sys.path.insert(0, str(ROOT / "validation"))
import fred  # noqa: E402
import zparse  # noqa: E402

_spec = importlib.util.spec_from_file_location("a1", ROOT / "research" / "a1_gfc_decomposition" / "decompose.py")
a1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a1)

FRED_IDS = ["MORTGAGE30US", "DGS10", "DGS5", "T10Y2Y", "BAA10Y", "OBMMIJUMBO30YF", "OBMMIC30YF", "OBMMIFHA30YF"]
START = "1986Q1"


# ---------------------------------------------------------------- statistics (numpy only, tested)
def nw_lag(T: int) -> int:
    return int(math.floor(4 * (T / 100) ** (2 / 9)))


def ols_hac(y: np.ndarray, X: np.ndarray, lags: int):
    """OLS with Newey-West (Bartlett) HAC covariance, no small-sample correction (statsmodels' default)."""
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    u = y - X @ beta
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for l in range(1, lags + 1):
        w = 1 - l / (lags + 1)
        G = Xu[l:].T @ Xu[:-l]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    r2 = 1 - (u @ u) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, u, r2


def adf_stat(u: np.ndarray, lags: int = 4) -> float:
    """ADF t-statistic on a residual series: du_t = c + g*u_{t-1} + sum_k d_k du_{t-k}. Plain OLS t on g."""
    du = np.diff(u)
    T = len(du)
    rows = range(lags, T)
    Y = np.array([du[t] for t in rows])
    X = np.array([[1.0, u[t]] + [du[t - k] for k in range(1, lags + 1)] for t in rows])
    b = np.linalg.lstsq(X, Y, rcond=None)[0]
    e = Y - X @ b
    s2 = e @ e / (len(Y) - X.shape[1])
    V = s2 * np.linalg.inv(X.T @ X)
    return float(b[1] / math.sqrt(V[1, 1]))


# ---------------------------------------------------------------- data
def public_shares(zip_path: Path) -> pd.DataFrame:
    """Public shares, computed at catalog level exactly as validation/run.py does.

    Not from A1's finer cells: in 1974Q3-1986Q3 the Z.1 pool sub-series (FL413065110/123/133/143) sum to
    more than the pool total FL413065105 (by about $14.6B in 1980Q4), so cell-based shares are overstated
    there (found 2026-11-04 while cross-checking C1's vintages). The Fannie+Freddie share still needs the
    sub-series; it is a post-hoc check only.
    """
    df, mh, ch, public, labels = a1.load(zip_path)
    a = df["FL153165105"] / df["FL893065105"]
    pub_m = sum(df[s["id"]] for s in mh if s["risk_bucket"] in public) * a
    pub_c = sum(df[s["id"]].fillna(0.0) if s["id"] == "FL403066005" else df[s["id"]]
                for s in ch if s["risk_bucket"] in public)
    gse = (a1.combo(df, a1.PUBLIC_MORT["Fannie Mae (portfolio + pools)"])
           + a1.combo(df, a1.PUBLIC_MORT["Freddie Mac (portfolio + pools)"])) * a
    out = pd.DataFrame({
        "mort_share": pub_m / df["FL153165105"],
        "gse_share": gse / df["FL153165105"],
        "headline_share": (pub_m + pub_c) / (df["FL153165105"] + df["FL153166000"]),
    })
    out.index = pd.PeriodIndex(out.index, freq="Q")
    return out.dropna()


def quarterly(s: pd.Series) -> pd.Series:
    s = s.dropna()
    return s.groupby(s.index.to_period("Q")).mean()


def realized_vol(d: pd.Series) -> pd.Series:
    d = d.dropna()
    ch = d.diff().dropna()
    g = ch.groupby(ch.index.to_period("Q"))
    return g.std() * math.sqrt(252)


def build_panel(zip_path: Path) -> pd.DataFrame:
    raw = {s: fred.observations(s) for s in FRED_IDS}
    p = public_shares(zip_path)
    q = pd.DataFrame({s: quarterly(raw[s]) for s in FRED_IDS})
    q["vol10"] = realized_vol(raw["DGS10"])
    # Coverage: a quarter counts only if its daily/weekly series are present for most of it.
    n_mort = raw["MORTGAGE30US"].dropna().groupby(raw["MORTGAGE30US"].dropna().index.to_period("Q")).size()
    q["n_pmms_weeks"] = n_mort
    panel = p.join(q, how="inner")
    panel["S1"] = panel["MORTGAGE30US"] - panel["DGS10"]
    panel["S1_blend"] = panel["MORTGAGE30US"] - (panel["DGS5"] + panel["DGS10"]) / 2
    panel["refi"] = panel["DGS10"] - panel["DGS10"].rolling(20, min_periods=20).mean()
    panel["S2_jumbo_conf"] = panel["OBMMIJUMBO30YF"] - panel["OBMMIC30YF"]
    panel["S2_fha_conf"] = panel["OBMMIFHA30YF"] - panel["OBMMIC30YF"]
    # refi uses the trailing 20 quarters of DGS10, so it needs data before START: compute on the full q.
    full_refi = q["DGS10"] - q["DGS10"].rolling(20, min_periods=20).mean()
    panel["refi"] = full_refi.reindex(panel.index)
    return panel


# ---------------------------------------------------------------- regressions
CONTROLS = ["DGS10", "vol10", "T10Y2Y", "BAA10Y", "refi"]


def spec_list(last_q: str):
    out = []
    for share in ["mort_share", "headline_share"]:
        for dep in ["S1", "S1_blend"]:
            for end in [last_q, "2022Q3"]:
                tag = []
                if share != "mort_share":
                    tag.append("headline share")
                if dep != "S1":
                    tag.append("5y/10y blend")
                if end == "2022Q3":
                    tag.append("ends 2022Q3")
                # METHOD.md: robustness checks vary one thing at a time
                if len(tag) <= 1:
                    out.append(dict(share=share, dep=dep, end=end, variant=", ".join(tag) or "main"))
    # Post-hoc checks added after the first results, in response to review (METHOD.md "Changes after
    # results"). Reported, but the verdict rule is applied to the pre-specified variants only.
    out += [
        dict(share="mort_share", dep="S1", end=last_q, variant="post-hoc: HAC lag 8", lags=8),
        dict(share="gse_share", dep="S1", end=last_q, variant="post-hoc: Fannie+Freddie share"),
        dict(share="mort_share", dep="S1", end=last_q, variant="post-hoc: PMMS 2022Q4+ dummy", dummy="2022Q4"),
    ]
    return out


def run_specs(panel: pd.DataFrame, last_q: str) -> pd.DataFrame:
    rows = []
    for sp in spec_list(last_q):
        cols = [sp["dep"], sp["share"]] + CONTROLS
        d = panel.loc[pd.Period(START, "Q"):pd.Period(sp["end"], "Q"), cols].copy()
        if sp.get("dummy"):
            d["pmms_2022q4"] = (d.index >= pd.Period(sp["dummy"], "Q")).astype(float)
            cols = cols + ["pmms_2022q4"]
        assert not d.isna().any().any(), f"missing values in {sp}: {d.isna().sum()[d.isna().sum() > 0].to_dict()}"
        for form in ["L", "D"]:
            dd = d if form == "L" else d.diff().dropna()
            y = dd[sp["dep"]].to_numpy()
            X = np.column_stack([np.ones(len(dd))] + [dd[c].to_numpy() for c in cols[1:]])
            L = sp.get("lags", nw_lag(len(dd)))
            b, se, u, r2 = ols_hac(y, X, L)
            adf = adf_stat(u) if form == "L" else float("nan")
            names = ["const", "public_share"] + cols[2:]
            for n, bi, si in zip(names, b, se):
                rows.append(dict(variant=sp["variant"], form=form, dep=sp["dep"], share=sp["share"],
                                 start=str(dd.index[0]), end=str(dd.index[-1]), T=len(dd), hac_lags=L,
                                 term=n, coef=bi, se=si, t=bi / si, ci_lo=bi - 1.96 * si, ci_hi=bi + 1.96 * si,
                                 r2=r2, adf_resid=adf))
    return pd.DataFrame(rows)


def verdict(reg: pd.DataFrame, variant: str) -> str:
    r = reg[(reg.variant == variant) & (reg.term == "public_share")].set_index("form")
    sig_neg = {f: (r.loc[f, "ci_hi"] < 0) for f in ["L", "D"]}
    sig_pos = {f: (r.loc[f, "ci_lo"] > 0) for f in ["L", "D"]}
    if all(sig_neg.values()):
        return "compression (b<0, 95% CI excludes 0 in L and D)"
    if all(sig_pos.values()):
        return "widening (b>0, 95% CI excludes 0 in L and D)"
    return "no robust association"


def summary(panel: pd.DataFrame) -> pd.DataFrame:
    periods = {
        "1986Q1-2008Q2": ("1986Q1", "2008Q2"),
        "2008Q3-2019Q4": ("2008Q3", "2019Q4"),
        "2020Q1-latest": ("2020Q1", str(panel.index[-1])),
        "2017Q1-latest (Optimal Blue)": ("2017Q1", str(panel.index[-1])),
    }
    rows = []
    for name, (a, b) in periods.items():
        d = panel.loc[pd.Period(a, "Q"):pd.Period(b, "Q")]
        for v in ["mort_share", "S1", "S1_blend", "S2_jumbo_conf", "S2_fha_conf", "BAA10Y"]:
            x = d[v].dropna()
            if len(x):
                rows.append(dict(period=name, variable=v, n=len(x), mean=x.mean(), min=x.min(), max=x.max()))
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    a = ap.parse_args(argv)
    if not a.z1_zip.exists():
        print(f"{a.z1_zip} not found; run validation/run.py first (it downloads the zip).", file=sys.stderr)
        return 2
    panel = build_panel(a.z1_zip)
    panel = panel.loc[pd.Period("1981Q1", "Q"):]
    last_q = str(panel.dropna(subset=["S1", "mort_share"] + CONTROLS).index[-1])

    # Checks
    assert (panel["mort_share"].between(0, 1)).all() and (panel["headline_share"].between(0, 1)).all()
    assert panel.loc[pd.Period(START, "Q"):pd.Period(last_q, "Q"), "n_pmms_weeks"].min() >= 11, "PMMS gap"
    vint = zparse.zip_member_info(a.z1_zip)
    vint = vint[0] if isinstance(vint, tuple) else vint
    # The headline share must reproduce validation (C2: 56.4% in 2026Q2, register public_share_2026q2)
    if pd.Period("2026Q2", "Q") in panel.index:
        assert abs(panel.loc[pd.Period("2026Q2", "Q"), "headline_share"] - 0.5638) < 5e-4

    reg = run_specs(panel, last_q)
    reg.to_csv(HERE / "regressions.csv", index=False, float_format="%.6g")
    summ = summary(panel)
    summ.to_csv(HERE / "spreads_summary.csv", index=False, float_format="%.6g")
    (ROOT / "data" / "b1").mkdir(parents=True, exist_ok=True)
    panel.to_csv(ROOT / "data" / "b1" / "panel.csv", float_format="%.6g")

    def coef(variant, form, term="public_share"):
        r = reg[(reg.variant == variant) & (reg.form == form) & (reg.term == term)].iloc[0]
        return {k: (None if pd.isna(r[k]) else float(r[k])) for k in ["coef", "se", "ci_lo", "ci_hi", "r2", "adf_resid"]} | {"T": int(r["T"]), "hac_lags": int(r["hac_lags"]), "start": r["start"], "end": r["end"]}

    def sm(period, var, k="mean"):
        r = summ[(summ.period == period) & (summ.variable == var)]
        return float(r[k].iloc[0]) if len(r) else None

    man = {m["tag"]: m for m in fred.manifest()}
    res = {
        "z1_vintage": str(vint),
        "fred_retrieved_utc": {s: man.get(f"obs_{s}", {}).get("retrieved_utc") for s in FRED_IDS},
        "fred_sha256": {s: man.get(f"obs_{s}", {}).get("sha256") for s in FRED_IDS},
        "sample": {"start": START, "end": last_q},
        "main_L": coef("main", "L"),
        "main_D": coef("main", "D"),
        "verdicts": {v: verdict(reg, v) for v in reg.variant.unique() if not v.startswith("post-hoc")},
        # Engle-Granger 5% critical values, constant, no trend, 157 effective ADF observations; from
        # statsmodels.tsa.adfvalues.mackinnoncrit (MacKinnon 2010), checked 2026-11-04 (coord-q2).
        # N counts the dependent variable plus regressors in the cointegrating regression.
        "eg_crit_5pct": {"N7": -5.10, "N8": -5.38, "N3": -3.80},
        "pmms_dummy_coef": coef("post-hoc: PMMS 2022Q4+ dummy", "L", "pmms_2022q4"),
        "public_share_coef": {v: {f: coef(v, f) for f in ["L", "D"]} for v in reg.variant.unique()},
        "S1_mean_1986_2008q2": sm("1986Q1-2008Q2", "S1"),
        "S1_mean_2008q3_2019": sm("2008Q3-2019Q4", "S1"),
        "S1_mean_2020_latest": sm("2020Q1-latest", "S1"),
        "mort_share_mean_1986_2008q2": sm("1986Q1-2008Q2", "mort_share"),
        "mort_share_mean_2008q3_2019": sm("2008Q3-2019Q4", "mort_share"),
        "S2_jumbo_conf_mean_2017_latest": sm("2017Q1-latest (Optimal Blue)", "S2_jumbo_conf"),
        "S2_jumbo_conf_min_2017_latest": sm("2017Q1-latest (Optimal Blue)", "S2_jumbo_conf", "min"),
        "S2_jumbo_conf_max_2017_latest": sm("2017Q1-latest (Optimal Blue)", "S2_jumbo_conf", "max"),
        "S2_fha_conf_mean_2017_latest": sm("2017Q1-latest (Optimal Blue)", "S2_fha_conf"),
        "mort_share_mean_2020_latest": sm("2020Q1-latest", "mort_share"),
        # Power: how large a spread change over the 1986-2008Q2 -> 2020+ rise in the share the D interval allows
        "D_halfwidth_over_rise_pp": (lambda x: (x["ci_hi"] - x["ci_lo"]) / 2)(coef("main", "D"))
            * (sm("2020Q1-latest", "mort_share") - sm("1986Q1-2008Q2", "mort_share")),
        # Minimum detectable effect at 5% size and 80% power (2.8 SE of the main D coefficient), scaled by the
        # same rise in the share (coord-q3). Assumes the short-run (D) response equals the long-run one.
        "D_mde80_over_rise_pp": 2.8 * coef("main", "D")["se"]
            * (sm("2020Q1-latest", "mort_share") - sm("1986Q1-2008Q2", "mort_share")),
        "S1_mean_change_first_to_last_pp": sm("2020Q1-latest", "S1") - sm("1986Q1-2008Q2", "S1"),
        "mort_share_latest": float(panel.loc[pd.Period(last_q, "Q"), "mort_share"]),
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: res[k] for k in ["sample", "main_L", "main_D", "verdicts"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
