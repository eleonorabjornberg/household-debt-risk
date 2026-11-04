"""B4 GSE release: offline checks on the committed B3 exposures and presets (no Z.1 zip needed)."""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b4", HERE / "b4.py")
b4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b4)
EX = json.loads((b4.B3 / "exposures.json").read_text())
BUCKET = next(e["balance"] for e in EX["exposures"] if e["class"] == "mortgage" and e["holder"] == "gse_agency")


def _split(released):
    return {"as_of": EX["as_of"], "bucket_total": BUCKET, "released_total": released}


def test_zero_share_equals_b3_and_total_is_invariant():
    res = b4.gse_release(_split(0.7 * BUCKET))
    for name, grid in res.items():
        b3 = json.loads((b4.B3 / ("results_dfast2026.json" if "dfast" in name else "results_replay_2008_2012.json")).read_text())[name]
        assert grid[0]["public_musd"] == pytest.approx(b3["public_musd"])
        assert all(g["total_musd"] == pytest.approx(b3["total_musd"]) for g in grid)
        pub = [g["public_musd"] for g in grid]
        assert pub == sorted(pub, reverse=True)
        # linear in the share: the step equals 25% of the released book's losses
        steps = [a - b for a, b in zip(pub, pub[1:])]
        assert max(steps) == pytest.approx(min(steps))


def test_no_released_book_changes_nothing():
    res = b4.gse_release(_split(0.0))
    for grid in res.values():
        assert grid[-1]["public_musd"] == pytest.approx(grid[0]["public_musd"])
