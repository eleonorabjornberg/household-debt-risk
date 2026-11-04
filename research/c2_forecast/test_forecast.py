"""C2 leakage tests 1-5 (frozen protocol, "Leakage tests") and statistics checks. Synthetic data; offline."""
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("forecast", HERE / "forecast.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


def synth(n=200, seed=0):
    rng = np.random.default_rng(seed)
    d = np.zeros(n)
    for t in range(1, n):
        d[t] = 0.0005 + 0.5 * d[t - 1] + 0.002 * rng.standard_normal()
    idx = pd.period_range("1960Q1", periods=n, freq="Q")
    return pd.Series(0.3 + np.cumsum(d), index=idx)


S = synth()
T = S.index[150]


# ---- Leakage test 1: future target as a feature
def test_guard_trips_on_future_target_feature():
    leak = lambda s: S[s + 4] - S[s]          # the h=4 target itself, as a feature at s
    def leaky_extra(s):
        fc.feature_check(s + 4, s)            # the feature reads quarter s+4
        return leak(s)
    with pytest.raises(fc.LeakError):
        fc.pairs(S, T, 4, "expanding", extra=leaky_extra)


def test_outcome_guard_off_leak_reaches_model():
    # Guard switched off: the leaked feature makes in-sample error at h=4 fall to about zero
    X, y, _ = fc.pairs(S, T, 4, "expanding", extra=lambda s: S[s + 4] - S[s])
    Z = np.column_stack([np.ones(len(X)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    assert np.abs(y - Z @ b).max() < 1e-10


# ---- Leakage test 2: revised (latest-vintage) series in place of point-in-time, C1 input
def _rows(rows):
    df = pd.DataFrame(rows, columns=["date", "realtime_start", "realtime_end", "value"])
    for c in ["date", "realtime_start", "realtime_end"]:
        df[c] = pd.to_datetime(df[c])
    return df


END = pd.Timestamp("2262-04-11")


def test_guard_trips_on_latest_vintage_input():
    v = _rows([("2019-12-01", "2026-11-04", END, 100.0), ("2020-01-01", "2026-11-04", END, 102.0)])
    with pytest.raises(fc.nc.LeakError):
        fc.nc.growth_from_rows(v, "2020-03-12", pd.Timestamp("2019-12-31"), pd.Timestamp("2020-03-31"), "M")


# ---- Leakage test 3: a G.19 value published one day after the origin
def test_guard_trips_on_value_published_day_after_origin():
    v = _rows([("2019-12-01", "2020-02-07", END, 100.0), ("2020-01-01", "2020-03-13", END, 102.0)])
    with pytest.raises(fc.nc.LeakError):
        fc.nc.growth_from_rows(v, "2020-03-12", pd.Timestamp("2019-12-31"), pd.Timestamp("2020-03-31"), "M")


# ---- Leakage test 4: full-sample preprocessing (fit window)
def test_fit_window_check_trips_on_full_sample_fit():
    with pytest.raises(fc.LeakError):
        fc.fit_window_check(list(S.index), T)          # AR order or scaler fitted on all data


def test_pairs_respect_purge_and_embargo():
    for h in fc.HORIZONS:
        _, _, used = fc.pairs(S, T, h, "expanding")
        assert max(used) == T - fc.EMBARGO


def test_no_model_reads_data_after_the_origin():
    """Perturb every quarter after T: no forecast made at T may change."""
    S2 = S.copy()
    S2[S2.index > T] += 0.05
    for h in fc.HORIZONS:
        assert fc.f_zdir(S2, T, h, "expanding") == fc.f_zdir(S, T, h, "expanding")
        assert fc.f_zdamp(S2, T, h, "expanding") == fc.f_zdamp(S, T, h, "expanding")
        assert fc.ar_bic(S2, T, h, "expanding") == fc.ar_bic(S, T, h, "expanding")
        assert fc.drift(S2, T, h, "rolling") == fc.drift(S, T, h, "rolling")


def test_estimation_ignores_quarters_inside_the_embargo():
    """Perturb quarters T-3..T-1 (inside the embargo, not used as features at T): estimated parameters unchanged,
    so the drift forecast (no features at T) is unchanged."""
    S2 = S.copy()
    for q in [T - 3, T - 2, T - 1]:
        S2[q] += 0.01
    # drift uses changes up to T-e = T-4; the change at T-4 is unaffected, T-3 is not used
    assert fc.drift(S2, T, 4, "expanding") == pytest.approx(fc.drift(S, T, 4, "expanding"))


# ---- Leakage test 5 (outcome): placebo on a time-shuffled target shows no skill
def test_placebo_no_skill_on_synthetic():
    p = fc.placebo(S.loc[: S.index[-1]])
    assert all(v["rel_rmse_vs_no_change"] > 0.9 for v in p.values())


# ---- holdout loader
def test_holdout_needs_frozen_hash():
    with pytest.raises(SystemExit):
        fc.load_latest(holdout=True, prereg="wrong")


# ---- statistics
def test_clopper_pearson_known_values():
    lo, hi = fc.clopper_pearson(8, 10)
    assert lo == pytest.approx(0.4439, abs=1e-3) and hi == pytest.approx(0.9748, abs=1e-3)


def test_kupiec_correct_rate_not_rejected():
    hits = [1] * 20 + [0] * 80
    assert fc.kupiec(hits, 0.2) == pytest.approx(1.0, abs=1e-9)


def test_dm_hln_reduces_to_lag0_for_h1():
    rng = np.random.default_rng(3)
    a, b = rng.standard_normal(50) * 2, rng.standard_normal(50)
    stat, p = fc.dm_hln(a, b, 1)
    d = a ** 2 - b ** 2
    raw = d.mean() / math.sqrt(d.var() / 50)
    assert stat == pytest.approx(raw * math.sqrt(49 / 50))


def test_interval_score():
    assert fc.interval_score(0.0, 1.0, 0.5, 0.2) == 1.0
    assert fc.interval_score(0.0, 1.0, 2.0, 0.2) == pytest.approx(1.0 + 10 * 1.0)
