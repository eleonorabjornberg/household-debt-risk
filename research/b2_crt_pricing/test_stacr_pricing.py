import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stacr_pricing", HERE / "stacr_pricing.py")
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)


def test_items_lines_and_same_line_and_missing_colon():
    assert sp.items("M-1: 1.35%\nM-2: 1.55%") == {"M-1": "1.35%", "M-2": "1.55%"}
    assert sp.items("M-1: $169,000,000        B-1: $84,000,000") == {"M-1": "$169,000,000", "B-1": "$84,000,000"}
    assert sp.items("A-H: 4.00%\nM-1 3.00%") == {"A-H": "4.00%", "M-1": "3.00%"}
    assert sp.items(float("nan")) == {}
    with pytest.raises(ValueError):
        sp.items("no tranche here")


def test_values():
    assert sp.money("$209,600,000") == 209_600_000
    assert sp.money("–") is None and sp.money("$80,000,000/$20,000,000/–") is None
    assert sp.pct("1.35%") == pytest.approx(0.0135)
    assert sp.pct("0.80% (Indicative)") == pytest.approx(0.008)
    assert sp.pct("0.0") == 0.0 and sp.pct("2.45%/1.250%/–") is None
    with pytest.raises(ValueError):
        sp.pct("abc")


def test_detach_points():
    ce = {"AH": "4.50%", "M1A": "3.00%", "M1B": "2.00%", "M2": "1.25%", "B1": "0.75%", "B2": "0.25%"}
    out = sp.detach_points(ce)
    assert out["M1A"] == (pytest.approx(0.045), "AH")
    assert out["B2"] == (pytest.approx(0.0075), "B1")
    assert "AH" not in out
    bad = sp.detach_points({"AH": "3.00%", "M1": "3.50%", "M2": "2.00%"})
    assert bad["M1"][0] is None and bad["M1"][1].startswith("none: CE out of order")
    assert bad["M2"] == (pytest.approx(0.035), "M1")
