"""Offline unit tests of parsing / aggregation helpers (no data files needed)."""
import datetime as dt
import decimal

import pandas as pd
import pytest

from hhdebt import transform
from hhdebt.export import _json_value
from hhdebt.extract import nyfed, z1


def test_z1_line_filter():
    lines = [
        b'Z1/Z1/FL153165105.Q,"Households; mortgages, 1-4",x,y,Quarterly,a,b,c,d,Currency,Millions,2026-06-30,13976938\n',
        b'Z1/Z1/FL153165105.A,"annual",x,y,Annual,a,b,c,d,Currency,Millions,2025-12-31,1\n',
        b'Z1/Z1/FL999999999.Q,"other",x,y,Quarterly,a,b,c,d,Currency,Millions,2026-06-30,5\n',
        b'Z1/Z1/FL153166000.Q,"cc",x,y,Quarterly,a,b,c,d,Currency,Millions,2026-03-31,ND\n',
    ]
    rows = z1._parse_lines(lines, {b"FL153165105", b"FL153166000"})
    assert rows == [("FL153165105", "2026-06-30", 13976938.0)]


def test_fred_quarterize_monthly_mean_and_weekly_last():
    v = pd.Timestamp("2026-10-27")
    monthly = pd.DataFrame({"series_id": "CPIAUCSL", "date": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]),
                            "value": [1.0, 2.0, 3.0, 4.0], "vintage": v})
    weekly = pd.DataFrame({"series_id": "WSHOMCB", "date": pd.to_datetime(["2026-03-18", "2026-03-25", "2026-04-01", "2026-04-08"]),
                           "value": [10.0, 11.0, 12.0, 13.0], "vintage": v})
    q = transform.quarterize_fred(pd.concat([monthly, weekly]))
    cpi = q[q.series_id == "CPIAUCSL"]
    assert list(cpi.date) == [pd.Timestamp("2026-03-31")] and cpi.value.iloc[0] == 2.0  # Q2 incomplete -> dropped
    mbs = q[q.series_id == "WSHOMCB"]
    assert list(mbs.date) == [pd.Timestamp("2026-03-31")] and mbs.value.iloc[0] == 11.0  # Q2 not over -> dropped


@pytest.mark.parametrize("label,expected", [("03:Q1", "2003-03-31"), ("99:Q4", "1999-12-31"), ("26:Q2", "2026-06-30"),
                                            (dt.datetime(2003, 6, 1), "2003-06-30"), ("Total", None)])
def test_nyfed_quarter_labels(label, expected):
    got = nyfed._quarter_end(label)
    assert (got is None and expected is None) or got == pd.Timestamp(expected)


def test_latest_vintage_wins():
    raw = pd.DataFrame({"series_id": ["A", "A"], "date": pd.to_datetime(["2020-03-31"] * 2),
                        "value": [1.0, 2.0], "vintage": pd.to_datetime(["2026-09-11", "2026-06-12"]), "source": "z1"})
    assert transform.latest_vintage(raw).value.tolist() == [1.0]


def test_student_imputation_preserves_totals():
    dates = pd.date_range("1964-12-31", "2007-12-31", freq="QE")
    w = pd.DataFrame(index=dates)
    w[transform.STUDENT] = [0.0 if d < pd.Timestamp("2006-03-31") else 60.0 for d in dates]
    w[transform.OTHER_NR] = [100.0 if d < pd.Timestamp("2006-03-31") else 40.0 for d in dates]
    w[transform.REVOLVING] = 5.0
    w[transform.AUTO] = 7.0
    for s in transform.STUDENT_FLOOR:
        w[s] = 0.0
    w.loc["1990-12-31", "FL313066220"] = 50.0   # floor binds
    sp = transform.split_consumer_credit(w, dates)
    assert (sp.student + sp.other_nonrevolving == w[transform.STUDENT] + w[transform.OTHER_NR]).all()
    assert sp.loc["1965-12-31", "student"] == 0
    assert sp.loc["1990-12-31", "student"] == 50.0
    assert sp.loc["2005-12-31", "student"] == pytest.approx(60.0, rel=0.02)
    assert sp.is_estimated.sum() == (dates < pd.Timestamp("2006-03-31")).sum()


def test_json_values():
    assert _json_value(decimal.Decimal("13976938")) == 13976938
    assert _json_value(decimal.Decimal("0.5638312")) == pytest.approx(0.5638312)
    assert _json_value(float("nan")) is None
    assert _json_value(pd.Timestamp("2026-06-30")) == "2026-06-30"
    assert _json_value(dt.date(2026, 6, 30)) == "2026-06-30"
    assert _json_value(True) is True
