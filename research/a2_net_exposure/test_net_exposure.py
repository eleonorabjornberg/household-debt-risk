"""Offline tests for A2 (no Z.1 data, no network): the FHFA transcription and the bound arithmetic."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("net_exposure", Path(__file__).with_name("net_exposure.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_transcription_is_internally_consistent():
    crt = m.load_crt()  # asserts monotone cumulative RIF and cum[t-1] + annual[t] == cum[t]
    assert crt.index.min() == 2013 and crt.index.is_monotonic_increasing
    # Spot values against the FHFA reports (sources.md).
    assert crt.at[2023, "cum_rif_musd"] == 210218 and crt.at[2023, "cum_ref_upb_musd"] == 6664614
    assert crt.at[2019, "cum_rif_musd"] == 115070
    assert crt.at[2023, "cum_pmi_rif_musd"] == 835000


def test_transcription_error_is_caught(tmp_path):
    crt = pd.read_csv(Path(__file__).with_name("crt_fhfa.csv"))
    crt.loc[crt.year == 2020, "cum_rif_musd"] = 147002  # planted $10bn typo
    p = tmp_path / "crt.csv"
    crt.to_csv(p, index=False)
    with pytest.raises(AssertionError):
        m.load_crt(p)


def test_bounds_net_le_gross_and_share_arithmetic():
    crt = pd.DataFrame({"cum_rif_musd": [100.0, 300.0], "cum_ref_upb_musd": [1000.0, 5000.0],
                        "cum_pmi_rif_musd": [50.0, float("nan")]}, index=pd.Index([2013, 2014], name="year"))
    g = pd.Series([4000.0, 4000.0], index=crt.index)
    pub = pd.Series([6000.0, 6000.0], index=crt.index)
    s = pd.Series([10000.0, 10000.0], index=crt.index)
    a = pd.Series([0.5, 0.5], index=crt.index)
    t = m.bounds(g, pub, s, a, crt)
    m.check(t)
    assert t.at[2014, "cum_crt_rif_hh_bn"] == pytest.approx(0.15)
    assert t.at[2014, "net_ff_lower_bn"] == pytest.approx(4.0 - 0.15)
    assert t.at[2014, "public_share_net_lower_pct"] == pytest.approx(100 * (6000 - 150) / 10000)
    assert pd.isna(t.at[2014, "cum_pmi_rif_hh_bn"])  # absent stays absent, never a default


def test_check_rejects_net_above_gross():
    t = pd.DataFrame({"gross_ff_bn": [1.0], "net_ff_lower_bn": [1.5], "public_share_net_lower_pct": [1.0],
                      "public_share_gross_pct": [1.0]})
    with pytest.raises(AssertionError):
        m.check(t)
