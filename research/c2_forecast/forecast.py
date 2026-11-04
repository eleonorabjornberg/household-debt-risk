#!/usr/bin/env python3
"""PLAN task C2: forecasts of the public share 1, 4 and 8 quarters ahead, scored under the frozen protocol.

    uv run --project pipeline python research/c2_forecast/forecast.py                         # development only
    uv run --project pipeline python research/c2_forecast/forecast.py --holdout --prereg 192d60c   # the one holdout run

Protocol: docs/decisions/scoring-protocol.md (frozen 192d60c). Implementation choices: SPECS.md (opened before
any score). Inputs: research/c1_nowcast/z1_share_vintages.csv and first_release.csv (Z.1 vintages), C1's
point-in-time machinery for the Z+C1 family. Outputs next to this file: forecasts_dev.csv, scores_dev.csv,
coverage_dev.csv, tests_dev.csv, seasonality.json, placebo_dev.json, results_dev.json.
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
C1 = ROOT / "research" / "c1_nowcast"
sys.path.insert(0, str(C1))
sys.path.insert(0, str(ROOT / "research" / "common"))

_s = importlib.util.spec_from_file_location("c1nowcast", C1 / "nowcast.py")
nc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(nc)

FROZEN = "192d60c"
LATEST = "2026-09-11"
DEV_END = pd.Period("2023Q2", "Q")
FIRST_ORIGIN = pd.Period("1990Q1", "Q")
HORIZONS = (1, 4, 8)
EMBARGO = 4
ROLL = 80
NLAGS = 4
PHI_GRID = (0.0, 0.25, 0.5, 0.75, 0.9, 1.0)
BURN_IN = 40
MIN_ZC1 = 12
CANDIDATES = ("Z-DIR", "Z-DAMP", "ZC1-DIR")
BENCH = ("no_change", "drift", "ar_bic", "seasonal_naive")


class LeakError(AssertionError):
    pass


# ------------------------------------------------------------------ data and guards
def load_latest(holdout: bool = False, prereg: str | None = None) -> pd.Series:
    """Latest-vintage share by quarter. Cut at DEV_END unless the holdout is explicitly opened (protocol rule)."""
    sv = pd.read_csv(C1 / "z1_share_vintages.csv")
    s = sv[sv.release == LATEST].set_index("quarter")["share"]
    s.index = pd.PeriodIndex(s.index, freq="Q")
    s = s.sort_index()
    if holdout:
        if prereg != FROZEN:
            raise SystemExit(f"holdout needs --prereg {FROZEN}")
        return s
    return s[s.index <= DEV_END]


def fit_window_check(target_quarters, T: pd.Period, e: int = EMBARGO) -> None:
    """Leakage test 4: no training target may be later than T - e."""
    if len(target_quarters) and max(target_quarters) > T - e:
        raise LeakError(f"training target {max(target_quarters)} beyond T-e = {T - e}")


def feature_check(source_quarter: pd.Period, s: pd.Period) -> None:
    """Leakage test 1: a feature at s may use data up to s only."""
    if source_quarter > s:
        raise LeakError(f"feature at {s} uses data from {source_quarter}")


# ------------------------------------------------------------------ features and pairs
def lags(d: pd.Series, s: pd.Period, n: int = NLAGS):
    q = [s - k for k in range(n)]
    for x in q:
        feature_check(x, s)
    return d.reindex(q).to_numpy()


def pairs(share: pd.Series, T: pd.Period, h: int, window: str, extra=None):
    """Training pairs allowed at origin T: s + h <= T - e (purge + embargo); rolling keeps the last ROLL rows."""
    d = share.diff()
    last_s = T - EMBARGO - h
    s_all = [s for s in share.index if s - (NLAGS - 1) - 1 >= share.index[0] and s <= last_s]
    if window == "rolling":
        s_all = s_all[-ROLL:]
    X, y, used = [], [], []
    for s in s_all:
        row = lags(d, s)
        if extra is not None:
            ex = extra(s)
            if ex is None or not np.isfinite(ex):
                continue
            row = np.append(row, ex)
        if np.isnan(row).any():
            continue
        X.append(row)
        y.append(share[s + h] - share[s])
        used.append(s + h)
    fit_window_check(used, T)
    return np.array(X), np.array(y), used


def ols(X, y):
    Z = np.column_stack([np.ones(len(X)), X])
    return np.linalg.lstsq(Z, y, rcond=None)[0]


# ------------------------------------------------------------------ models
def f_zdir(share, T, h, window, extra=None, extra_T=None):
    X, y, _ = pairs(share, T, h, window, extra)
    if extra is not None and len(y) < MIN_ZC1:
        return math.nan
    b = ols(X, y)
    x = lags(share.diff(), T)
    if extra is not None:
        if extra_T is None or not np.isfinite(extra_T):
            return math.nan
        x = np.append(x, extra_T)
    return float(b[0] + x @ b[1:])


def f_zdamp(share, T, h, window):
    X, y, _ = pairs(share, T, h, window)
    m = X.mean(axis=1)
    best = min(PHI_GRID, key=lambda p: float(((m * sum(p ** j for j in range(1, h + 1)) - y) ** 2).sum()))
    mT = float(np.nanmean(lags(share.diff(), T)))
    return mT * sum(best ** j for j in range(1, h + 1)), best


def ar_bic(share, T, h, window):
    """AR(p) on quarterly changes, p in 0..4 by BIC on a common training sample, iterated h steps."""
    d = share.diff().dropna()
    last_t = T - EMBARGO
    t_all = [t for t in d.index if t <= last_t]
    if window == "rolling":
        t_all = t_all[-ROLL:]
    fit_window_check(t_all, T)
    pmax = 4
    t_fit = t_all[pmax:]
    y = d.reindex(t_fit).to_numpy()
    best = None
    for p in range(0, pmax + 1):
        Z = np.column_stack([np.ones(len(t_fit))] + [d.reindex([t - k for t in t_fit]).to_numpy() for k in range(1, p + 1)])
        b = np.linalg.lstsq(Z, y, rcond=None)[0]
        res = y - Z @ b
        n = len(y)
        bic = n * math.log(res @ res / n) + (p + 1) * math.log(n)
        if best is None or bic < best[0]:
            best = (bic, p, b)
    _, p, b = best
    hist = list(d[d.index <= T].to_numpy())
    cum = 0.0
    for _ in range(h):
        nxt = b[0] + sum(b[k] * hist[-k] for k in range(1, p + 1))
        hist.append(nxt)
        cum += nxt
    return float(cum), p


def drift(share, T, h, window):
    d = share.diff().dropna()
    t_all = [t for t in d.index if t <= T - EMBARGO]
    if window == "rolling":
        t_all = t_all[-ROLL:]
    fit_window_check(t_all, T)
    return float(h * d.reindex(t_all).mean())


def seasonal_naive(share, T, h):
    L = 4 if h <= 4 else 8
    return float(share[T - L + h] - share[T - L])


# ------------------------------------------------------------------ C1 bridge feature at an origin date
class Bridge:
    """C1's accounting-bridge nowcast of the change from T to T+1, computed point-in-time at a given date."""

    def __init__(self):
        self.z = nc.Z1()
        inputs = [i for i in nc.pit.load_inputs() if i["id"] in nc.FREQ]
        self.vint, _ = nc.pit.load_vintages(inputs)

    def at(self, t, T: pd.Period, cells_release: str) -> float:
        Ts = str(T)
        q_end = (T + 1).end_time.normalize()
        t_end = T.end_time.normalize()
        cells = self.z.cells_at(cells_release, Ts)
        if not cells:
            return math.nan
        g = {}
        for sid in sorted(set(nc.MAP_2B.values()) | {nc.CC_TOTAL}):
            g[sid], _ = nc.indicator_growth(self.vint[sid], t, t_end, q_end, nc.FREQ[sid])
        return nc.bridge_share(cells, g, g[nc.CC_TOTAL], nc.MAP_2B) - nc.share_of(cells)


# ------------------------------------------------------------------ distributions and tests
def betainc_inv(a, b, p):
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if nc.betainc(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else betainc_inv(k, n - k + 1, alpha / 2)
    hi = 1.0 if k == n else betainc_inv(k + 1, n - k, 1 - alpha / 2)
    return lo, hi


def chi2_1_sf(x):
    return math.erfc(math.sqrt(max(x, 0) / 2))


def kupiec(hits, p):
    n, x = len(hits), int(sum(hits))
    if n == 0:
        return math.nan
    pi = x / n
    ll0 = (n - x) * math.log(1 - p) + x * math.log(p)
    ll1 = ((n - x) * math.log(1 - pi) if pi < 1 else 0) + (x * math.log(pi) if pi > 0 else 0)
    return chi2_1_sf(-2 * (ll0 - ll1))


def christoffersen(hits):
    h = list(map(int, hits))
    n = {(a, b): 0 for a in (0, 1) for b in (0, 1)}
    for a, b in zip(h[:-1], h[1:]):
        n[(a, b)] += 1
    n0, n1 = n[(0, 0)] + n[(0, 1)], n[(1, 0)] + n[(1, 1)]
    if n0 == 0 or n1 == 0:
        return math.nan
    p01, p11 = n[(0, 1)] / n0, n[(1, 1)] / n1
    p = (n[(0, 1)] + n[(1, 1)]) / (n0 + n1)
    L = lambda q, k, m: (k * math.log(q) if k else 0) + (m * math.log(1 - q) if m else 0)
    ll0 = L(p, n[(0, 1)] + n[(1, 1)], n[(0, 0)] + n[(1, 0)])
    ll1 = L(p01, n[(0, 1)], n[(0, 0)]) + L(p11, n[(1, 1)], n[(1, 0)])
    return chi2_1_sf(-2 * (ll0 - ll1))


def lrv(x, lag):
    """Long-run variance: rectangular kernel to `lag` (DM), Bartlett if that is not positive."""
    u = x - x.mean()
    n = len(u)
    g = [u @ u / n] + [u[k:] @ u[:-k] / n for k in range(1, lag + 1)]
    v = g[0] + 2 * sum(g[1:])
    if v <= 0:
        v = g[0] + 2 * sum((1 - k / (lag + 1)) * g[k] for k in range(1, lag + 1))
    return v


def dm_hln(e_bench, e_cand, h):
    d = e_bench ** 2 - e_cand ** 2
    n = len(d)
    stat = d.mean() / math.sqrt(lrv(d, h - 1) / n)
    stat *= math.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return float(stat), float(2 * nc.t_sf(abs(stat), n - 1))


def clark_west(e_small, e_big, f_small, f_big, h):
    adj = e_small ** 2 - (e_big ** 2 - (f_small - f_big) ** 2)
    n = len(adj)
    stat = adj.mean() / math.sqrt(lrv(adj, h - 1) / n)
    return float(stat), float(nc.norm_sf(stat))


def holm(p: pd.Series) -> pd.Series:
    return nc.holm(p)


# ------------------------------------------------------------------ the backtest
def backtest_latest(share: pd.Series, window: str, bridge: Bridge | None, cal: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rel_of = {}
    for r, q in sorted(zip(cal.z1_release, cal.latest_quarter_published)):
        rel_of.setdefault(pd.Period(q, "Q"), pd.Timestamp(r))     # a quarter's origin date is its first release
    for T in share.index:
        if T < FIRST_ORIGIN:
            continue
        for h in HORIZONS:
            if T + h > share.index[-1]:
                continue
            r = {"design": f"latest-{window}", "T": str(T), "h": h, "actual": share[T + h] - share[T], "share_T": share[T]}
            r["Z-DIR"] = f_zdir(share, T, h, window)
            r["Z-DAMP"], r["phi"] = f_zdamp(share, T, h, window)
            r["no_change"] = 0.0
            r["drift"] = drift(share, T, h, window)
            r["ar_bic"], r["ar_p"] = ar_bic(share, T, h, window)
            r["seasonal_naive"] = seasonal_naive(share, T, h)
            r["ZC1-DIR"] = math.nan
            if bridge is not None and T in rel_of and rel_of[T] >= pd.Timestamp("2015-03-01"):
                ex = lambda s: bridge_feature(bridge, s, rel_of)
                r["ZC1-DIR"] = f_zdir(share, T, h, window, extra=ex, extra_T=ex(T))
            rows.append(r)
    return pd.DataFrame(rows)


_bridge_cache: dict = {}


def bridge_feature(bridge: Bridge, s: pd.Period, rel_of: dict) -> float:
    """C1 bridge nowcast of s -> s+1, at the release date of s (cells from the latest vintage: pseudo P2b)."""
    if s not in rel_of or rel_of[s] < pd.Timestamp("2015-03-01"):
        return math.nan
    if s not in _bridge_cache:
        _bridge_cache[s] = bridge.at(rel_of[s], s, LATEST)
    return _bridge_cache[s]


def backtest_realtime(fr: pd.DataFrame, sv: pd.DataFrame, latest_full: pd.Series) -> pd.DataFrame:
    """Real-time check: origins at archived releases from 2016-09-16; Z family and benchmarks on that vintage."""
    rows = []
    for rel, g in sv.groupby("release"):
        s = g.set_index("quarter")["share"]
        s.index = pd.PeriodIndex(s.index, freq="Q")
        s = s.sort_index()
        T = s.index[-1]
        for h in HORIZONS:
            q = T + h
            if q > DEV_END or str(q) not in fr.index:
                continue
            fr_q = fr.loc[str(q)]
            first_level = fr_q["share_first"]
            r = {"design": "realtime-expanding", "origin_release": rel, "T": str(T), "h": h, "share_T": s[T],
                 "actual_first": first_level - s[T], "actual_latest": latest_full[q] - latest_full[T]}
            r["Z-DIR"] = f_zdir(s, T, h, "expanding")
            r["Z-DAMP"], r["phi"] = f_zdamp(s, T, h, "expanding")
            r["no_change"] = 0.0
            r["drift"] = drift(s, T, h, "expanding")
            r["ar_bic"], r["ar_p"] = ar_bic(s, T, h, "expanding")
            rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ scoring
def add_intervals(df: pd.DataFrame, models) -> pd.DataFrame:
    """Empirical-quantile intervals from each model's own past errors at the same horizon (target <= T - e)."""
    out = df.copy()
    for m in models:
        for lv, (ql, qh) in {"80": (0.10, 0.90), "95": (0.025, 0.975)}.items():
            out[f"{m}_lo{lv}"], out[f"{m}_hi{lv}"] = np.nan, np.nan
        out[f"{m}_crps"] = np.nan
    for (design, h), g in out.groupby(["design", "h"]):
        g = g.sort_values("T")
        Tq = g["T"].map(lambda x: pd.Period(x, "Q"))
        for m in models:
            err = (g["actual"] - g[m]).to_numpy()
            for i, idx in enumerate(g.index):
                T = Tq.iloc[i]
                past = [err[j] for j in range(len(g)) if Tq.iloc[j] + h <= T - EMBARGO and np.isfinite(err[j])]
                if len(past) < BURN_IN or not np.isfinite(g.loc[idx, m]):
                    continue
                past = np.array(past)
                f = g.loc[idx, m]
                for lv, (ql, qh) in {"80": (0.10, 0.90), "95": (0.025, 0.975)}.items():
                    out.loc[idx, f"{m}_lo{lv}"] = f + np.quantile(past, ql)
                    out.loc[idx, f"{m}_hi{lv}"] = f + np.quantile(past, qh)
                ens = f + past
                y = g.loc[idx, "actual"]
                out.loc[idx, f"{m}_crps"] = float(np.abs(ens - y).mean() - 0.5 * np.abs(ens[:, None] - ens[None, :]).mean())
    return out


def interval_score(lo, hi, y, alpha):
    return (hi - lo) + (2 / alpha) * np.maximum(lo - y, 0) + (2 / alpha) * np.maximum(y - hi, 0)


def scores(df: pd.DataFrame, models, label=None) -> pd.DataFrame:
    rows = []
    for (design, h), g in df.groupby(["design", "h"]):
        g = g.dropna(subset=[m for m in models if m in g] + ["actual"])   # common origins of the models compared
        if g.empty:
            continue
        e0 = 100 * (g["no_change"] - g["actual"])
        for m in models:
            e = 100 * (g[m] - g["actual"])
            r = {"design": design, "comparison": label or "all", "h": h, "model": m, "n": len(g),
                 "first_T": g["T"].min(), "last_T": g["T"].max(),
                 "rmse_pp": math.sqrt((e ** 2).mean()), "mae_pp": e.abs().mean(),
                 "rel_rmse_vs_no_change": math.sqrt((e ** 2).mean() / (e0 ** 2).mean())}
            if f"{m}_lo80" in g:
                gi = g.dropna(subset=[f"{m}_lo80"])
                r["n_intervals"] = len(gi)
                for lv, a in [("80", 0.2), ("95", 0.05)]:
                    if len(gi):
                        r[f"interval_score{lv}_pp"] = 100 * interval_score(gi[f"{m}_lo{lv}"], gi[f"{m}_hi{lv}"], gi["actual"], a).mean()
                r["crps_pp"] = 100 * gi[f"{m}_crps"].mean() if len(gi) else math.nan
            rows.append(r)
    return pd.DataFrame(rows)


def coverage(df: pd.DataFrame, models) -> pd.DataFrame:
    rows = []
    for (design, h), g in df.groupby(["design", "h"]):
        for m in models:
            for lv, nominal in [("80", 0.8), ("95", 0.95)]:
                gi = g.dropna(subset=[f"{m}_lo{lv}"]).sort_values("T")
                if gi.empty:
                    continue
                hit = ((gi["actual"] >= gi[f"{m}_lo{lv}"]) & (gi["actual"] <= gi[f"{m}_hi{lv}"])).to_numpy()
                k, n = int(hit.sum()), len(hit)
                lo, hi = clopper_pearson(k, n)
                miss = ~hit
                rows.append({"design": design, "h": h, "model": m, "level": nominal, "n": n, "coverage": k / n,
                             "cp_lo": lo, "cp_hi": hi,
                             "kupiec_p": kupiec(miss, 1 - nominal) if h == 1 else math.nan,
                             "christoffersen_p": christoffersen(miss) if h == 1 else math.nan})
    return pd.DataFrame(rows)


def tests(df: pd.DataFrame, seasonal: bool = False) -> pd.DataFrame:
    """Development tests. If the pre-scoring seasonality check passes, the protocol puts seasonal naive into the
    decision rules; its comparisons (non-nested, DM-HLN) are then added to the Holm family (stricter reading)."""
    benches = [("no_change", "CW"), ("ar_bic", "DM-HLN")] + ([("seasonal_naive", "DM-HLN")] if seasonal else [])
    rows = []
    for (design, h), g in df.groupby(["design", "h"]):
        if not design.startswith("latest-"):
            continue
        for cand in CANDIDATES:
            for bench, kind in benches:
                d = g.dropna(subset=[cand, bench, "actual"])
                if len(d) < 8:
                    continue
                ec, eb = 100 * (d[cand] - d["actual"]).to_numpy(), 100 * (d[bench] - d["actual"]).to_numpy()
                if kind == "CW":
                    stat, p = clark_west(eb, ec, 100 * d[bench].to_numpy(), 100 * d[cand].to_numpy(), h)
                else:
                    stat, p = dm_hln(eb, ec, h)
                rows.append({"design": design, "h": h, "candidate": cand, "benchmark": bench, "test": kind, "n": len(d),
                             "stat": stat, "p": p, "candidate_lower_rmse": bool((ec ** 2).mean() < (eb ** 2).mean())})
    t = pd.DataFrame(rows)
    t["p_holm"] = holm(t["p"]).values
    return t


def seasonality_check(share: pd.Series) -> dict:
    """Protocol: seasonal naive enters the decision rules only if the training sample shows seasonality.
    F-test of quarter dummies on quarterly changes, development data only (to DEV_END)."""
    d = share.diff().dropna()
    y = d.to_numpy()
    Q = np.array([p.quarter for p in d.index])
    X1 = np.column_stack([np.ones(len(y))] + [(Q == k).astype(float) for k in (2, 3, 4)])
    r0 = y - y.mean()
    b = np.linalg.lstsq(X1, y, rcond=None)[0]
    r1 = y - X1 @ b
    d1, d2 = 3, len(y) - 4
    F = ((r0 @ r0 - r1 @ r1) / d1) / (r1 @ r1 / d2)
    p = nc.betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * F))
    return {"F": float(F), "p": float(p), "n": len(y), "seasonal": bool(p < 0.05),
            "sample": f"{d.index[0]}-{d.index[-1]}", "rule": "p < 0.05 => seasonal naive enters the decision rules"}


def placebo(share: pd.Series, seed: int = 0) -> dict:
    """Leakage test 5 (outcome): Z-DIR trained on a time-shuffled target should show no skill over no-change."""
    rng = np.random.default_rng(seed)
    out = {}
    for h in HORIZONS:
        f, a = [], []
        for T in share.index:
            if T < FIRST_ORIGIN or T + h > share.index[-1]:
                continue
            X, y, _ = pairs(share, T, h, "expanding")
            b = ols(X, rng.permutation(y))
            x = lags(share.diff(), T)
            f.append(float(b[0] + x @ b[1:]))
            a.append(share[T + h] - share[T])
        f, a = np.array(f), np.array(a)
        stat, p = clark_west(100 * a, 100 * (a - f), np.zeros_like(f), 100 * f, h)
        out[str(h)] = {"rel_rmse_vs_no_change": float(math.sqrt(((f - a) ** 2).mean() / (a ** 2).mean())),
                       "cw_p": p, "no_skill": bool(p > 0.05)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--prereg")
    ap.add_argument("--no-c1", action="store_true", help="skip the Z+C1 family (no ALFRED cache)")
    a = ap.parse_args(argv)
    if a.holdout:
        raise SystemExit("holdout run not cleared in this session (Q-C1c / coordinator); development only")
    share = load_latest()
    assert share.index[-1] == DEV_END
    seas = seasonality_check(share)
    (HERE / "seasonality.json").write_text(json.dumps(seas, indent=2) + "\n")   # written before any scoring
    cal = pd.read_csv(C1 / "z1_calendar.csv")
    bridge = None if a.no_c1 else Bridge()
    df = pd.concat([backtest_latest(share, w, bridge if w == "expanding" else None, cal) for w in ("expanding", "rolling")],
                   ignore_index=True)
    models = list(CANDIDATES) + list(BENCH)
    df = add_intervals(df, [m for m in models if m != "ZC1-DIR"])
    assert (df["T"].map(lambda x: pd.Period(x, "Q")) + df["h"] <= DEV_END).all()
    df.to_csv(HERE / "forecasts_dev.csv", index=False, float_format="%.8g")

    zmods = ["Z-DIR", "Z-DAMP", "no_change", "drift", "ar_bic", "seasonal_naive"]
    sc = pd.concat([scores(df, zmods, "Z family, all origins"),
                    scores(df[df["ZC1-DIR"].notna()], ["ZC1-DIR", "Z-DIR", "no_change", "ar_bic"], "Z+C1 common origins")],
                   ignore_index=True)
    cov = coverage(df, [m for m in zmods])
    ts = tests(df, seasonal=seas["seasonal"])

    # Real-time check (descriptive): archived vintages, first-release and latest targets
    sv = pd.read_csv(C1 / "z1_share_vintages.csv")
    fr = pd.read_csv(C1 / "first_release.csv").set_index("quarter")
    latest_full = load_latest()   # dev-cut latest vintage
    rt = backtest_realtime(fr, sv, latest_full)
    rt_sc = []
    for tgt in ["actual_first", "actual_latest"]:
        x = rt.assign(actual=rt[tgt], design=f"realtime-vs-{tgt.split('_')[1]}")
        rt_sc.append(scores(x, ["Z-DIR", "Z-DAMP", "no_change", "drift", "ar_bic"], "real-time check"))
    # Same origins, latest-vintage design: the revision effect is the gap between the two
    lat_same = df[(df.design == "latest-expanding") & df["T"].isin(rt["T"])]
    rt_sc.append(scores(lat_same.assign(design="latest-on-realtime-origins"), ["Z-DIR", "Z-DAMP", "no_change", "drift", "ar_bic"], "real-time check"))
    sc = pd.concat([sc] + rt_sc, ignore_index=True)
    rt.to_csv(HERE / "forecasts_realtime_dev.csv", index=False, float_format="%.8g")
    sc.to_csv(HERE / "scores_dev.csv", index=False, float_format="%.6g")
    cov.to_csv(HERE / "coverage_dev.csv", index=False, float_format="%.6g")
    ts.to_csv(HERE / "tests_dev.csv", index=False, float_format="%.6g")
    pl = placebo(share)
    (HERE / "placebo_dev.json").write_text(json.dumps(pl, indent=2) + "\n")

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, float) and o != o:
            return None
        if isinstance(o, (np.floating, np.integer, np.bool_)):
            return clean(o.item())
        return o
    res = {"protocol": f"docs/decisions/scoring-protocol.md @ {FROZEN}", "specs": "research/c2_forecast/SPECS.md",
           "dev_end": str(DEV_END), "pseudo_oos": "latest-vintage designs are pseudo out-of-sample",
           "seasonality": seas, "placebo": pl,
           "n_forecasts": df.groupby(["design", "h"]).size().rename("n").reset_index().to_dict(orient="records"),
           "scores": sc.to_dict(orient="records"), "tests": ts.to_dict(orient="records"),
           "coverage": cov.to_dict(orient="records")}
    (HERE / "results_dev.json").write_text(json.dumps(clean(res), indent=1, allow_nan=False) + "\n")
    show = sc[(sc.design == "latest-expanding") & (sc.comparison == "Z family, all origins")]
    print(show[["h", "model", "n", "rmse_pp", "rel_rmse_vs_no_change", "interval_score80_pp", "crps_pp"]].round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
