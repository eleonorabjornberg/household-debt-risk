"""C1 nowcast harness: leakage guards (C2 tests 1-3 applied to C1), bridge identities, test statistics.
Offline and synthetic; no data needed."""
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nowcast", HERE / "nowcast.py")
nc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nc)

END = pd.Timestamp("2262-04-11")


def _rows(rows):
    df = pd.DataFrame(rows, columns=["date", "realtime_start", "realtime_end", "value"])
    for c in ["date", "realtime_start", "realtime_end"]:
        df[c] = pd.to_datetime(df[c])
    return df


# Monthly indicator: Dec 2019 = 100 (published 2020-02-07), Jan 2020 = 102 (published 2020-03-06)
V = _rows([("2019-12-01", "2020-02-07", END, 100.0), ("2020-01-01", "2020-03-06", END, 102.0)])
T_END, Q_END = pd.Timestamp("2019-12-31"), pd.Timestamp("2020-03-31")


def test_growth_uses_only_published_months():
    g, used = nc.indicator_growth(V, "2020-02-15", T_END, Q_END, "M")
    assert g == 1.0                     # January not yet public on 2020-02-15
    g, used = nc.indicator_growth(V, "2020-03-15", T_END, Q_END, "M")
    assert g == pytest.approx(1.02) and used == "2020-01-01"


def test_guard_trips_on_target_fed_as_indicator():
    # Leakage test 1: the target's first release (published 2020-06-11) passed in as an indicator row at t=2020-03-15
    leaked = pd.concat([V, _rows([("2020-03-01", "2020-06-11", END, 999.0)])])
    with pytest.raises(nc.LeakError):
        nc.growth_from_rows(leaked, "2020-03-15", T_END, Q_END, "M")


def test_guard_trips_on_latest_vintage_in_place_of_as_of():
    # Leakage test 2: a latest-vintage read (every row stamped with the retrieval date) instead of ALFRED as-of rows
    latest = V.assign(realtime_start=pd.Timestamp("2026-11-04"))
    with pytest.raises(nc.LeakError):
        nc.growth_from_rows(latest, "2020-03-15", T_END, Q_END, "M")


def test_guard_trips_on_value_published_one_day_after_origin():
    # Leakage test 3: January published 2020-03-16, one day after the instant
    late = _rows([("2019-12-01", "2020-02-07", END, 100.0), ("2020-01-01", "2020-03-16", END, 102.0)])
    with pytest.raises(nc.LeakError):
        nc.growth_from_rows(late, "2020-03-15", T_END, Q_END, "M")
    assert nc.indicator_growth(late, "2020-03-15", T_END, Q_END, "M")[0] == 1.0   # the as-of path never sees it


def test_guard_on_z1_release_dates():
    nc.guard([pd.Timestamp("2020-03-12")], "2020-03-15")
    with pytest.raises(nc.LeakError):
        nc.guard([pd.Timestamp("2020-03-16")], "2020-03-15")


CELLS = {("mortgages", "public", "mort_pools"): 60.0, ("mortgages", "private", "mort_banks"): 40.0,
         ("consumer credit", "public", "cc_federal"): 10.0, ("consumer credit", "private", "cc_depository"): 20.0,
         ("consumer credit", "private", "cc_other_private"): 10.0}
MAP = {"cc_federal": "TOTALGOV", "cc_depository": "TOTALDI", "mort_banks": "RREACBW027NBOG"}


def test_bridge_with_no_growth_is_no_change():
    g = {"TOTALGOV": 1.0, "TOTALDI": 1.0, "RREACBW027NBOG": 1.0}
    assert nc.bridge_share(CELLS, g, 1.0, MAP) == pytest.approx(nc.share_of(CELLS))


def test_bridge_moves_cells_and_keeps_cc_total():
    g = {"TOTALGOV": 1.10, "TOTALDI": 1.0, "RREACBW027NBOG": 0.5}
    s = nc.bridge_share(CELLS, g, 1.05, MAP)
    # mortgages: 60 public + 20 banks; cc total 40*1.05 = 42: federal 11, depository 20, other 11
    assert s == pytest.approx((60 + 11) / (60 + 20 + 42))


def test_ar1_recovers_coefficient():
    rng = np.random.default_rng(0)
    x = np.zeros(4000)
    for t in range(1, len(x)):
        x[t] = 0.1 + 0.6 * x[t - 1] + 0.01 * rng.standard_normal()
    assert nc.ar1_forecast(x) == pytest.approx(0.1 + 0.6 * x[-1], abs=2e-3)


def test_t_and_normal_tails_against_known_values():
    assert nc.norm_sf(1.959963985) == pytest.approx(0.025, abs=1e-9)
    assert 2 * nc.t_sf(2.228138852, 10) == pytest.approx(0.05, abs=1e-8)   # t(10) 97.5% quantile
    assert nc.t_sf(-1.0, 5) == pytest.approx(1 - nc.t_sf(1.0, 5))


def test_t_tail_matches_scipy_if_available():
    stats = pytest.importorskip("scipy.stats")
    for t, df in [(0.3, 3), (1.7, 12), (3.2, 25), (-2.0, 40)]:
        assert nc.t_sf(t, df) == pytest.approx(stats.t.sf(t, df), abs=1e-10)


def test_dm_hln_sign_and_symmetry():
    rng = np.random.default_rng(1)
    e_bad = rng.standard_normal(40) * 2
    e_good = rng.standard_normal(40)
    stat, p = nc.dm_hln(e_bad, e_good)
    assert stat > 0 and p < 0.05
    stat2, p2 = nc.dm_hln(e_good, e_bad)
    assert stat2 == pytest.approx(-stat) and p2 == pytest.approx(p)


def test_clark_west_rewards_informative_nested_model():
    rng = np.random.default_rng(2)
    y = rng.standard_normal(60)
    signal = y + 0.3 * rng.standard_normal(60)
    f_small, f_big = np.zeros(60), 0.8 * signal
    stat, p = nc.clark_west(y - f_small, y - f_big, f_small, f_big)
    assert stat > 0 and p < 0.01


def test_holm():
    p = pd.Series([0.01, 0.04, 0.03], index=list("abc"))
    adj = nc.holm(p)
    assert adj["a"] == pytest.approx(0.03) and adj["c"] == pytest.approx(0.06) and adj["b"] == pytest.approx(0.06)


def test_unpublished_target_is_no_target_not_keyerror():
    # deviation c1b-dev-1 (a): a target quarter missing from the latest vintage gives no actual, labelled
    latest = pd.Series([0.50, 0.51], index=["2026Q1", "2026Q2"])
    r = nc.target_latest(latest, "2026Q3", "2026Q2")
    assert math.isnan(r["actual_latest"]) and r["target"] == nc.NO_TARGET
    r = nc.target_latest(latest, "2026Q2", "2026Q1")
    assert r["actual_latest"] == pytest.approx(0.01) and "target" not in r
