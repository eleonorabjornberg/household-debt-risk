"""Tests for stacr_2017.py: class mapping, LIBOR adjustment, detachment points, and the multiple."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stacr_2017", HERE / "stacr_2017.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def rows(deal, date, bench, tranches):
    """tranches: (name, spread, attach, detach, detach_from, indicative)"""
    return [dict(deal=deal, closing_date=date, benchmark=bench, tranche=n, issued_usd=1e8, issued_note="",
                 spread=sp, spread_indicative=ind, initial_ce=a, detach=d, detach_from=f)
            for n, sp, a, d, f, ind in tranches]


DF = pd.DataFrame(
    rows("2016-DNA4", "2016-09-30", "1M LIBOR", [("B", 0.086, 0.0, 0.01, "M3", False)])
    + rows("2018-DNA2", "2018-06-20", "1M LIBOR", [("M1", 0.008, 0.025, 0.04, "AH", False),
                                                    ("B2", 0.105, 0.0, 0.005, "B1", True)])
    + rows("2019-FTR1", "2019-12-17", "1M LIBOR", [("B-2", 0.05, 0.001, 0.0375, "AH", False)])
    + rows("2022-DNA2", "2022-02-11", "SOFR", [("M-1A", 0.013, 0.034, 0.045, "AH", False),
                                               ("B-2", 0.085, 0.0025, 0.0075, "B1", False)])
    + rows("2024-DNA1", "2024-02-09", "SOFR", [("A-1", 0.0135, 0.0425, 0.055, "AH", False)]))


def test_scope_classes_and_flags():
    t = s.frame(DF).set_index(["deal", "tranche"])
    assert "2016-DNA4" not in t.index.get_level_values(0)              # before 2017
    assert t.loc[("2018-DNA2", "M1"), "cls"] == "M-1" and t.loc[("2022-DNA2", "M-1A"), "cls"] == "M-1"
    assert t.loc[("2018-DNA2", "B2"), "cls"] == "B" and t.loc[("2018-DNA2", "B2"), "retained_indicative"]
    assert not t.loc[("2024-DNA1", "A-1"), "in_her_classes"]
    assert not t.loc[("2019-FTR1", "B-2"), "detach_known"]              # B-2 straight under A-H
    assert t.loc[("2018-DNA2", "M1"), "detach_known"]                   # top mezzanine under A-H is fine


def test_unknown_tranche_name_raises():
    bad = DF.copy()
    bad.loc[1, "tranche"] = "X-9"
    with pytest.raises(ValueError):
        s.frame(bad)


def test_libor_adjustment_only_on_libor_deals():
    t = s.frame(DF).set_index(["deal", "tranche"])
    assert pd.isna(t.loc[("2018-DNA2", "M1"), "spread_sofr_bp"])       # pending: no value invented
    assert t.loc[("2022-DNA2", "B-2"), "spread_sofr_bp"] == pytest.approx(850)
    t = s.frame(DF, adj_bp=11.448).set_index(["deal", "tranche"])
    assert t.loc[("2018-DNA2", "M1"), "spread_sofr_bp"] == pytest.approx(80 + 11.448)
    assert t.loc[("2022-DNA2", "B-2"), "spread_sofr_bp"] == pytest.approx(850)


def test_multiple():
    t = s.frame(DF).set_index(["deal", "tranche"])
    m1 = t.loc[("2018-DNA2", "M1")]
    assert m1["el_pool_out_bp"] == 0 and pd.isna(m1["multiple_out"]) and m1["multiple_note"].startswith("absent")
    b = t.loc[("2022-DNA2", "B-2")]
    el = s.b2.tranche_el_bp(25, 75)
    assert b["el_tranche_out_bp"] == pytest.approx(el / 0.005)
    assert b["multiple_out"] == pytest.approx(850 / (el / 0.005))
    assert b["multiple_orig"] > b["multiple_out"]                       # original-balance EL is smaller
    # a zero-attach slice thicker than the baseline loss takes all of it
    z = t.loc[("2018-DNA2", "B2")]
    assert z["el_pool_out_bp"] == pytest.approx(s.b2.tranche_el_bp(0, 10000))
