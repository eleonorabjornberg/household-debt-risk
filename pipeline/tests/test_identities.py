"""Z.1 accounting identities on the extracted source data (every quarter, 1945+)."""
import pandas as pd
import pytest

from hhdebt import config

TOL = 0.5  # $ millions; Z.1 levels are integers


def _sum(w, ids):
    return w[ids].fillna(0).sum(axis=1)


def test_mortgage_holders_sum_to_all_sector_total(z1_wide):
    ids = config.series_ids("z1", "mortgage_holder")
    assert len(ids) == 17
    diff = (_sum(z1_wide, ids) - z1_wide["FL893065105"]).abs()
    assert z1_wide["FL893065105"].notna().all()
    assert diff.max() <= TOL, diff.idxmax()


def test_consumer_credit_holders_sum_to_liability(z1_wide):
    ids = config.series_ids("z1", "cc_holder")
    assert len(ids) == 9
    diff = (_sum(z1_wide, ids) - z1_wide["FL153166000"]).abs()
    assert diff.max() <= TOL, diff.idxmax()


def test_consumer_credit_types_sum_to_liability(z1_wide):
    ids = config.series_ids("z1", "cc_type")
    assert len(ids) == 4
    diff = (_sum(z1_wide, ids) - z1_wide["FL153166000"]).abs()
    assert diff.max() <= TOL, diff.idxmax()


def test_scope_total_is_mortgages_plus_consumer_credit(z1_wide):
    diff = (z1_wide["FL153165105"] + z1_wide["FL153166000"] - z1_wide["FL154104015"]).abs()
    assert diff.max() <= TOL


def test_history_covers_1945_to_2026(z1_wide):
    assert z1_wide.index.min() <= pd.Timestamp("1945-12-31")
    assert z1_wide.index.max() >= pd.Timestamp("2026-06-30")


@pytest.mark.parametrize("sid,expected", [("FL153165105", 13_976_938), ("FL153166000", 5_120_258)])
def test_spot_values_2026q2(z1_wide, sid, expected):
    # Values from the 2026-09-11 Z.1 release. 2% tolerance absorbs routine revisions in later
    # releases while still catching a wrong series or unit.
    assert z1_wide.loc["2026-06-30", sid] == pytest.approx(expected, rel=0.02)
