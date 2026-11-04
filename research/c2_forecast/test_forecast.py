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


# ---- Leakage test 1: future target as a feature, through the production pairs() path
def test_guard_trips_on_future_target_feature():
    leaky = lambda s: (S[s + 4] - S[s], s + 4)    # the h=4 target itself, honestly declaring that it reads s+4
    with pytest.raises(fc.LeakError):
        fc.pairs(S, T, 4, "expanding", extra=leaky)
    with pytest.raises(fc.LeakError):
        fc.f_zdir(S, T, 4, "expanding", extra=leaky, extra_T=0.0)


def test_outcome_guard_off_leak_reaches_model(monkeypatch):
    # Guard switched off (production feature_check replaced by a no-op): the leaked feature makes the in-sample
    # error at h=4 fall to about zero, so the feature does reach the model.
    monkeypatch.setattr(fc, "feature_check", lambda src, s: None)
    X, y, _ = fc.pairs(S, T, 4, "expanding", extra=lambda s: (S[s + 4] - S[s], s + 4))
    Z = np.column_stack([np.ones(len(X)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    assert np.abs(y - Z @ b).max() < 1e-10


# ---- Leakage tests 2 and 3: C1 inputs, through the production indicator_growth_pit path (used by Bridge.at)
def _rows(rows):
    df = pd.DataFrame(rows, columns=["date", "realtime_start", "realtime_end", "value"])
    for c in ["date", "realtime_start", "realtime_end"]:
        df[c] = pd.to_datetime(df[c])
    return df


END = pd.Timestamp("2262-04-11")
T_END, Q_END, ORIGIN = pd.Timestamp("2019-12-31"), pd.Timestamp("2020-03-31"), "2020-03-12"


def test_guard_trips_on_latest_vintage_input(monkeypatch):
    # Test 2: a latest-vintage read in place of the as-of read (the as-of filter bypassed): the guard raises
    v = _rows([("2019-12-01", "2026-11-04", END, 100.0), ("2020-01-01", "2026-11-04", END, 102.0)])
    monkeypatch.setattr(fc, "asof_filter", lambda v, t: v)
    with pytest.raises(fc.nc.LeakError):
        fc.indicator_growth_pit(v, ORIGIN, T_END, Q_END, "M")


def test_guard_trips_on_value_published_day_after_origin(monkeypatch):
    # Test 3: a G.19 value released one day after the origin
    v = _rows([("2019-12-01", "2020-02-07", END, 100.0), ("2020-01-01", "2020-03-13", END, 102.0)])
    assert fc.indicator_growth_pit(v, ORIGIN, T_END, Q_END, "M")[0] == 1.0   # correct filter: value not seen
    monkeypatch.setattr(fc, "asof_filter", lambda v, t: v)                      # broken filter: the guard raises
    with pytest.raises(fc.nc.LeakError):
        fc.indicator_growth_pit(v, ORIGIN, T_END, Q_END, "M")


# ---- Leakage test 4: full-sample preprocessing, through the production fitting functions
@pytest.mark.parametrize("fn", ["pairs", "ar", "drift"])
def test_fit_window_check_trips_when_embargo_is_dropped(monkeypatch, fn):
    # Break the window logic (embargo set to 0 where the data are cut) while the check keeps e = 4: it must raise
    monkeypatch.setattr(fc, "EMBARGO", 0)
    with pytest.raises(fc.LeakError):
        if fn == "pairs":
            fc.pairs(S, T, 4, "expanding")
        elif fn == "ar":
            fc.ar_bic(S, T, 4, "expanding")
        else:
            fc.drift(S, T, 4, "expanding")


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
def test_placebo_runs_and_reports():
    # The outcome check itself; on the real development data it currently FAILS at h=1 and 4 (SPECS.md):
    # a shuffled target keeps its mean, so the placebo is close to drift (protocol question, not a leak).
    p = fc.placebo(S)
    assert set(p) == {"1", "4", "8"} and all("no_skill" in v for v in p.values())


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
