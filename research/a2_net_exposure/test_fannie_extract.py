"""Tests for the Fannie Mae sentence extractor on verbatim sentences from its 10-K filings (FY2025, FY2021)."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("fe", Path(__file__).with_name("fannie_extract.py"))
fe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fe)

FY2025 = ("The risk in force of our back-end single-family credit risk transfer transactions, which refers to the maximum amount of "
          "losses that could be absorbed by credit risk transfer investors, was approximately $39 billion as of December 31, 2025, "
          "compared with approximately $43 billion as of December 31, 2024. As of December 31, 2025, our total mortgage insurance "
          "risk in force was $201.4 billion, ")
FY2021 = ("The risk in force of these transactions, which refers to the maximum amount of losses that could be absorbed by credit risk "
          "transfer investors, was approximately $35 billion as of December 31, 2021 compared with approximately $40 billion as of "
          "December 31, 2020.")


def test_fy2025_sentence():
    e = fe.extract(FY2025, 2025)
    assert e["crt_rif_bn"] == 39.0 and e["crt_prior"] == (2024, 43.0) and e["mi_rif_bn"] == 201.4


def test_fy2021_sentence_without_comma():
    e = fe.extract(FY2021, 2021)
    assert e["crt_rif_bn"] == 35.0 and e["crt_prior"] == (2020, 40.0) and "mi_rif_bn" not in e


def test_wrong_year_is_refused():
    with pytest.raises(AssertionError):
        fe.extract(FY2025, 2024)
