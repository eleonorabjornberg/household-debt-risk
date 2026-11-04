"""Synthetic tests for the C1 point-in-time plumbing (no data, no network)."""
import importlib.util
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
import fred  # noqa: E402

spec = importlib.util.spec_from_file_location("pit", HERE / "pit.py")
pit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pit)

END = pd.Timestamp("2262-04-11")


def _v(rows):
    df = pd.DataFrame(rows, columns=["date", "realtime_start", "realtime_end", "value"])
    for c in ["date", "realtime_start", "realtime_end"]:
        df[c] = pd.to_datetime(df[c])
    return df


# Jan value first published 2020-02-07 as 100, revised on 2020-03-06 to 101; Feb first published 2020-03-06.
V = _v([
    ("2020-01-01", "2020-02-07", "2020-03-05", 100.0),
    ("2020-01-01", "2020-03-06", END, 101.0),
    ("2020-02-01", "2020-03-06", END, 102.0),
])


def test_as_of_returns_only_what_was_public():
    assert pit.as_of(V, "2020-02-06").empty                     # nothing published yet
    s = pit.as_of(V, "2020-02-07")
    assert s.to_dict() == {pd.Timestamp("2020-01-01"): 100.0}   # first release, no Feb yet
    s = pit.as_of(V, "2020-03-05")
    assert s.to_dict() == {pd.Timestamp("2020-01-01"): 100.0}   # day before revision
    s = pit.as_of(V, "2020-03-06")
    assert s.to_dict() == {pd.Timestamp("2020-01-01"): 101.0, pd.Timestamp("2020-02-01"): 102.0}


def test_leaked_future_vintage_is_detected():
    # A deliberately leaked row (value published in the future) must not appear in an earlier as-of read.
    leaked = pd.concat([V, _v([("2020-03-01", "2020-04-07", END, 999.0)])])
    assert pd.Timestamp("2020-03-01") not in pit.as_of(leaked, "2020-04-06").index
    assert pit.as_of(leaked, "2020-04-07")[pd.Timestamp("2020-03-01")] == 999.0


def test_first_release_and_lags():
    f = pit.first_release(V)
    assert f.set_index("date")["value"].to_dict() == {pd.Timestamp("2020-01-01"): 100.0, pd.Timestamp("2020-02-01"): 102.0}
    lag = pit.release_lags(V, "M")
    # Jan is the first vintage's observation (excluded: no earlier vintage to date it against);
    # Feb ends 2020-02-29, published 2020-03-06 -> 6 days.
    assert lag["n_obs"] == 1 and lag["lag_days_median"] == 6


def test_backfilled_history_is_not_a_lag():
    v = pd.concat([V, _v([("1990-01-01", "2020-03-06", END, 5.0)])])   # history extended back on 2020-03-06
    assert pit.release_lags(v, "M")["lag_days_max"] == 6


def test_to_millions_uses_units_in_force_at_publication():
    units = pd.DataFrame({"realtime_start": pd.to_datetime(["2020-01-01", "2020-03-01"]),
                          "realtime_end": pd.to_datetime(["2020-02-29", "2262-04-11"]),
                          "units": ["Billions of Dollars", "Millions of Dollars"]})
    out, n = fred.to_millions(V, units)
    assert n == 1
    assert out["value"].tolist() == [100000.0, 101.0, 102.0]


def test_to_millions_leaves_percent_series_alone():
    units = pd.DataFrame({"realtime_start": [pd.Timestamp("2000-01-01")], "realtime_end": [END], "units": ["Percent"]})
    out, n = fred.to_millions(V, units)
    assert n == 0 and out.equals(V)
