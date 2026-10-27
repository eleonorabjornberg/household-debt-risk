"""Invariants of the transform output (core + mart tables)."""
import numpy as np
import pandas as pd
import pytest

from hhdebt import config, transform

REL = 1e-6


def test_no_duplicate_keys(out):
    for name, keys in transform.PRIMARY_KEYS.items():
        df = out[name]
        assert not df.duplicated(keys).any(), name
        assert df[keys].notna().all().all(), name


def test_columns_match_schema(out):
    for name, cols in transform.COLUMNS.items():
        assert list(out[name].columns) == cols, name


def test_buckets_sum_to_scope_total_each_quarter(out, scope_total):
    d = out["mart.debt_by_risk_holder"]
    assert set(d.risk_bucket) == set(config.risk_buckets())
    assert d.groupby("date").size().eq(len(config.risk_buckets()) * 2).all()
    total = d.groupby("date")["nominal_musd"].sum()
    np.testing.assert_allclose(total, scope_total.reindex(total.index), rtol=REL)
    np.testing.assert_allclose(d.groupby("date")["share_of_total"].sum(), 1.0, atol=1e-6)


def test_bucket_debt_types_match_liabilities(out, z1_wide):
    d = out["mart.debt_by_risk_holder"].groupby(["date", "debt_type"])["nominal_musd"].sum().unstack()
    np.testing.assert_allclose(d["mortgage"], z1_wide["FL153165105"].reindex(d.index), rtol=REL)
    np.testing.assert_allclose(d["consumer_credit"], z1_wide["FL153166000"].reindex(d.index), rtol=REL, atol=0.01)


def test_collateral_classes_sum_to_scope_total(out, scope_total):
    c = out["mart.collateral_coverage"]
    assert c.groupby("date").size().eq(4).all()
    total = c.groupby("date")["debt_musd"].sum()
    np.testing.assert_allclose(total, scope_total.reindex(total.index), rtol=REL)
    np.testing.assert_allclose(c.groupby("date")["share_of_debt"].sum(), 1.0, atol=1e-6)
    assert (c.debt_musd >= 0).all()


def test_collateral_estimates_only_before_student_split(out, z1_wide):
    c = out["mart.collateral_coverage"]
    first = z1_wide.index[z1_wide["FL153166220"] > 0].min()
    assert first == pd.Timestamp("2006-03-31")
    est = c[c.is_estimated]
    assert (est.date < first).all()
    assert set(est.collateral_class) == {"uncollateralized", "other_nonrevolving"}
    assert not c[(c.date >= first)].is_estimated.any()
    # coverage only for collateralized classes
    assert c[c.collateral_class.isin(["uncollateralized", "other_nonrevolving"])].coverage_ratio.isna().all()
    assert c[c.collateral_class == "home_backed"].coverage_ratio.notna().all()


SHARE_COLS = {
    "mart.debt_by_risk_holder": ["share_of_total"],
    "mart.public_share": ["public_share", "public_share_mortgage", "public_share_cc", "fed_mbs_share_of_scope"],
    "mart.collateral_coverage": ["share_of_debt"],
}


@pytest.mark.parametrize("table", list(SHARE_COLS))
def test_shares_in_unit_interval(out, table):
    for col in SHARE_COLS[table]:
        s = out[table][col].dropna()
        assert ((s >= 0) & (s <= 1)).all(), (table, col, s.min(), s.max())


def test_event_window_shares_in_unit_interval(out):
    w = out["mart.crisis_event_window"]
    s = w[w.metric.str.startswith("share:") | (w.metric == "public_share")]
    assert s.value.between(0, 1).all() and s.value_at_t0.between(0, 1).all()


def test_public_share_headline(out):
    p = out["mart.public_share"].set_index("date")
    np.testing.assert_allclose(p.public_musd / p.scope_total_musd, p.public_share, rtol=1e-6)
    # Quick check (README) gave ~0.355 / ~0.558; those figures exclude state & local (~0.6 pp).
    assert p.loc["2007-12-31", "public_share"] == pytest.approx(0.355, abs=0.01)
    assert p.loc["2026-06-30", "public_share"] == pytest.approx(0.558, abs=0.01)
    assert p.loc[p.index < "2009-01-01", "fed_mbs_musd"].isna().all()
    assert p.loc["2026-06-30", "fed_mbs_musd"] > 0


def test_real_dollars_and_dpi(out):
    d = out["mart.debt_by_risk_holder"]
    assert d[d.date < "1947-01-01"].real_musd.isna().all()
    assert d[d.date >= "1947-03-31"].real_musd.notna().all()
    assert d[d.date < "1959-01-01"].pct_of_dpi.isna().all()
    assert d[d.date >= "1959-03-31"].pct_of_dpi.notna().all()


def test_crisis_event_window(out):
    w, crises = out["mart.crisis_event_window"], out["core.dim_crisis"]
    assert w.q_offset.between(config.WINDOW_MIN, config.WINDOW_MAX).all()
    assert set(w.crisis_id) <= set(crises.crisis_id)
    expected = {"public_share", "coverage:home_backed", "coverage:vehicle_backed"} \
        | {f"share:{b}" for b in config.risk_buckets()} | {f"share:{c}" for c in config.collateral_classes()}
    assert set(w.metric) == expected
    t0 = w[w.q_offset == 0]
    np.testing.assert_allclose(t0.value, t0.value_at_t0)
    np.testing.assert_allclose(w.delta_from_t0, w.value - w.value_at_t0, atol=1e-9)
    # date = start_q + q_offset quarters
    start = w.crisis_id.map(crises.set_index("crisis_id").start_q)
    exp = [(s.to_period("Q") + k).end_time.normalize() for s, k in zip(start, w.q_offset)]
    assert (pd.DatetimeIndex(exp) == pd.DatetimeIndex(w.date)).all()
    gfc = w[(w.crisis_id == "gfc_2007") & (w.metric == "public_share")]
    assert gfc.q_offset.min() == -8 and gfc.q_offset.max() == 16


def test_dims(out):
    c = out["core.dim_crisis"]
    assert len(c) == 14 and set(c.kind) == {"nber_recession", "policy_shock"}
    assert c[c.kind == "policy_shock"].end_q.isna().all()
    assert (c.start_q.dt.is_quarter_end).all()
    assert set(out["core.fact_quarterly"].series_id) <= set(out["core.dim_series"].series_id)
    rb = out["core.dim_risk_bucket"]
    assert set(rb[rb.is_public].risk_bucket) == {"federal_direct", "gse_agency", "state_local"}


def test_fact_quarterly_quarter_end_dates(out):
    f = out["core.fact_quarterly"]
    assert f.date.dt.is_quarter_end.all()
    cpi = f[f.series_id == "CPIAUCSL"]
    assert cpi.date.min() == pd.Timestamp("1947-03-31")


def test_nyfed_by_type(out):
    n = out["mart.nyfed_by_type"]
    if n.empty:
        pytest.skip("NY Fed extract not available")
    assert set(n.loan_type) == {"mortgage", "heloc", "auto", "credit_card", "student", "other"}
    assert n.date.min() == pd.Timestamp("2003-03-31")
    last = n[n.date == n.date.max()].set_index("loan_type")
    assert 10_000 < last.loc["mortgage", "balance_busd"] < 20_000   # ~$13T in 2026
    assert n.transition_serious_pct.dropna().between(0, 100).all()
