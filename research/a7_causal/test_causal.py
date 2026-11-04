"""Synthetic tests for A7 (no FRED or Z.1 data)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("causal", Path(__file__).with_name("causal.py"))
c = importlib.util.module_from_spec(spec)
sys.modules["causal"] = c
spec.loader.exec_module(c)


def test_weekly_s1_uses_same_week_up_to_pmms_date():
    pmms = pd.Series({pd.Timestamp("2008-09-11"): 6.0})  # a Thursday
    dgs = pd.Series({pd.Timestamp("2008-09-08"): 3.0, pd.Timestamp("2008-09-10"): 4.0, pd.Timestamp("2008-09-12"): 9.0,
                     pd.Timestamp("2008-09-05"): 9.0})
    assert c.weekly_s1(pmms, dgs).iloc[0] == 6.0 - 3.5  # Mon and Wed only; Fri after and prior week excluded


def test_event_study_finds_planted_drop():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2005-01-06", "2009-12-31", freq="W-THU")
    s = pd.Series(np.cumsum(rng.normal(0, 0.02, len(idx))) + 1.5, index=idx)
    w0 = int(np.searchsorted(idx.values, c.EVENT.to_datetime64(), side="right"))
    s.iloc[w0:] -= 0.8  # planted fall in the event window
    r = c.event_study(s)
    assert r["week0"] == "2008-09-11" and r["abnormal_constant_mean_pp"] < -0.5 and r["p_rank_one_sided"] < 0.05


def test_its_null_on_a_straight_line_and_flags_a_break():
    q = pd.period_range("1999Q1", "2012Q4", freq="Q")
    rng = np.random.default_rng(2)
    y = pd.Series(np.arange(len(q)) * 0.5 + rng.normal(0, 0.1, len(q)), index=q)
    assert c.its(y)["fit_ok"]
    y2 = y.copy()
    y2.loc["2008Q3":] -= 5.0
    r = c.its(y2)
    assert r["mean_post_deviation"] < -4 and r["p_rank"] <= 1 / 13 + 1e-9
