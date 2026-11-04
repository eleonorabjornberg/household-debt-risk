"""Offline tests for A8 (committed national_figures.csv; no downloads)."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("compare", HERE / "compare.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
A2 = {"public_share_gross_pct_last": 56.4, "public_share_net_lower_pct_last": 55.2,
      "freddie_10k": {"public_share_net_freddie_crt_pct_last": 56.2}}


def test_every_number_has_url_and_hash_and_missing_stays_missing():
    t = m.compare(m.load(), A2)
    assert t.at["DE", "holder_a"] == pytest.approx((438448 + 13519 + 17817) / 1551414)
    assert pd.isna(t.at["UK", "holder_a"]) and pd.isna(t.at["CA", "risk_b_low"])  # absent, never zero


def test_number_without_hash_is_refused(tmp_path):
    f = pd.read_csv(HERE / "national_figures.csv")
    f.loc[f.item == "savings_banks_lending_individuals", "sha256"] = "unknown"
    p = tmp_path / "f.csv"
    f.to_csv(p, index=False)
    with pytest.raises(AssertionError):
        m.load(p)


def test_us_ordering_is_checked():
    bad = {**A2, "public_share_net_lower_pct_last": 57.0}  # low above high
    with pytest.raises(AssertionError):
        m.compare(m.load(), bad)
