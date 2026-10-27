"""tableau/data CSVs: flat, pre-joined, same row counts as their source marts."""
import pandas as pd
import pytest

from hhdebt import config, tableau_export, transform

SOURCES = {"ratchet": "mart.debt_by_risk_holder", "crisis_windows": "mart.crisis_event_window",
           "collateral": "mart.collateral_coverage", "payment_priority": "mart.nyfed_by_type",
           "crises": "core.dim_crisis"}


@pytest.fixture(scope="module")
def built():
    if not (config.OUT_DIR / "mart.public_share.csv").exists():
        pytest.skip("no transform output in data/out")
    tables = transform.read_out()
    return tables, tableau_export.build(tables)


def test_columns_and_row_counts(built):
    tables, out = built
    for name, df in out.items():
        assert list(df.columns) == tableau_export.COLUMNS[name]
        assert len(df) == len(tables[SOURCES[name]]), name


def test_joins_fill_labels(built):
    _, out = built
    assert out["ratchet"].bucket_label.notna().all()
    assert out["ratchet"].public_share.notna().all()
    assert out["crisis_windows"].crisis_name.notna().all()
    assert out["collateral"].class_label.notna().all()
    pp = out["payment_priority"]
    assert pp.loan_label.notna().all()
    # stress index averages ~1 over the 2003-06 baseline by construction
    base = pp[pd.to_datetime(pp.date).dt.year <= 2006].groupby("loan_type").stress_index.mean()
    assert base.between(0.999, 1.001).all()
