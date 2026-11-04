"""Offline tests for A3 (committed transcription; no downloads)."""
import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("pre1945", HERE / "pre1945.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def _hs():
    return pd.read_csv(HERE / "hist_stats_1925_1951.csv")


def test_transcription_spot_values_and_structure():
    hs = _hs().set_index("year")
    assert list(hs.index) == list(range(1925, 1952))
    assert hs.at[1935, "n270_holc_musd"] == 2897 and hs.at[1945, "n271_fnma_musd"] == 7
    assert hs.at[1945, "n273_mortgages_1to4_family_busd"] == 18.6 and hs.at[1940, "x551_consumer_credit_musd"] == 8338


def test_zero_before_1933_and_blank_after_creation_is_refused():
    h = m.historical(_hs())
    assert (h.loc[:1932, "public_share_pct"] == 0).all() and (h.loc[:1932, "reliability"] == "C").all()
    bad = _hs()
    bad.loc[bad.year == 1940, "n270_holc_musd"] = None  # a gap after HOLC existed must not become zero
    with pytest.raises(AssertionError):
        m.historical(bad)


def test_overlap_reports_every_common_year_and_adjusted_variant():
    h = m.historical(_hs())
    z = pd.DataFrame({"year": [1945, 1946, 1947], "public_share_pct": [3.5, 2.1, 1.6], "federal_mortgages_musd": [900.0, 650.0, 620.0],
                      "mortgages_musd": [18700.0, 23100.0, 28300.0], "consumer_credit_musd": [6800.0, 9800.0, 13300.0]}).set_index("year")
    o = m.overlap(h, z)
    assert list(o.index) == [1945, 1946, 1947]
    adj = m.adjusted(h, o)
    assert adj[1932] == 0 and adj[1935] != h.at[1935, "public_share_pct"]
