"""Tests for the Freddie Mac 10-K coverage parser on verbatim excerpts of real filings (fixtures/)."""
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("tenk", HERE / "tenk.py")
tenk = importlib.util.module_from_spec(spec)
sys.modules["tenk"] = tenk  # dataclasses need the module registered
spec.loader.exec_module(tenk)

# Expected maximum coverage ($M) read off the filings by hand (see the fixture files).
EXPECTED = {
    2013: {2013: dict(crt=1183, pmi=50823, total=63678), 2012: dict(crt=0, pmi=46685, total=59646)},
    2015: {2015: dict(crt=14916, pmi=65760, total=89770), 2014: dict(crt=6657, pmi=57938, total=75315)},
    2017: {2017: dict(crt=17788 + 6736, pmi=85429, total=118345), 2016: dict(crt=14507 + 5355, pmi=74345, total=102185)},
    2019: {2019: dict(crt=25112 + 10157, pmi=107690, total=155066)},
    2025: {2025: dict(crt=24935 + 15081, pmi=181462, total=231839), 2024: dict(crt=28471 + 16474, pmi=174445, total=230033)},
}


def _fixture(fy):
    return (HERE / "fixtures" / f"freddie_10k_fy{fy}_excerpt.txt").read_text()


@pytest.mark.parametrize("fy", sorted(EXPECTED))
def test_parse_matches_filing(fy):
    out = tenk.parse(_fixture(fy), fy, tenk.FILINGS[fy][1])
    assert sorted(out) == [fy - 1, fy]
    for y, exp in EXPECTED[fy].items():
        for k, v in exp.items():
            assert out[y][k] == pytest.approx(v), (fy, y, k)
        assert out[y]["crt"] + out[y]["pmi"] + out[y]["other"] == pytest.approx(out[y]["total"], abs=10)


def test_wrapped_label_keeps_its_category():
    # FY2015: "STACR debt note and ACIS" / "transactions(3)  241,450 ..." must count as CRT, not "other".
    out = tenk.parse(_fixture(2015), 2015, "upb2_max2")
    assert out[2015]["crt"] == pytest.approx(14916)


def test_planted_error_is_caught():
    bad = _fixture(2025).replace("24,935", "34,935", 1)
    with pytest.raises(AssertionError):
        tenk.parse(bad, 2025, "blocks3")


def test_wrong_layout_is_refused():
    with pytest.raises((ValueError, AssertionError)):
        tenk.parse(_fixture(2025), 2025, "upb2_max2")
