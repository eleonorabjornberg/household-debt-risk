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


def test_ratchet_recession_flags(built):
    tables, out = built
    r = out["ratchet"]
    assert r.recession.dtype.kind == "i" and set(r.recession.unique()) <= {0, 1}
    assert ((r.recession == 1) == (r.crisis_id != "")).all()
    dates = pd.to_datetime(r.date)
    nber = tables["core.dim_crisis"].query("kind == 'nber_recession'")
    for c in nber.itertuples():
        inside = (dates >= pd.Timestamp(c.start_q)) & (dates <= pd.Timestamp(c.end_q))
        assert (r.crisis_id[inside] == c.crisis_id).all(), c.crisis_id
    # every recession row is inside some NBER window; policy shocks never set the flag
    assert set(r.crisis_id[r.recession == 1]) <= set(nber.crisis_id)
    gfc = r[(dates == "2008-12-31")]
    assert (gfc.recession == 1).all() and (gfc.crisis_id == "gfc_2007").all()
    assert (r[dates == "2006-12-31"].recession == 0).all()


def test_panel_and_collateral_labels(built):
    _, out = built
    cw = out["crisis_windows"]
    panels = cw.drop_duplicates("crisis_id").sort_values("start_q")
    labels = list(panels.panel_label)
    assert labels == sorted(labels), labels  # alphabetical == chronological
    assert len(set(labels)) == len(labels) and max(map(len, labels)) <= 22
    assert (cw.groupby("crisis_id").panel_label.nunique() == 1).all()
    assert labels[0] == "1953 Recession" and "2019 COVID-19" in labels and "2020 CARES Act" in labels
    pp = out["payment_priority"]
    assert set(pp.collateral_label) == {"Home-backed", "Vehicle-backed", "No collateral", "Other"}
    assert (pp.groupby("collateral_class").collateral_label.nunique() == 1).all()
