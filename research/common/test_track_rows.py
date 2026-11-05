"""track_rows.write_track_rows: folded rows are never re-added, changed folded rows fail loudly, new rows go to the track file."""
import csv
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("track_rows", Path(__file__).resolve().parent / "track_rows.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
H = ["claim_id", "claim", "display", "value", "locations", "notes"]


def _reg(tmp_path, rows):
    p = tmp_path / "register.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=H)
        w.writeheader()
        w.writerows(rows)
    return p


def row(i, disp="1%", val="0.01", loc="x.md:1"):
    return {"claim_id": i, "claim": "c", "display": disp, "value": val, "locations": loc, "notes": ""}


def test_folded_rows_are_skipped_and_no_empty_track_file(tmp_path):
    reg, track = _reg(tmp_path, [row("b4_a")]), tmp_path / "markets.csv"
    assert tr.write_track_rows([row("b4_a")], "b4_", reg, track) == []
    assert not track.exists()


def test_changed_folded_row_fails_loudly(tmp_path):
    reg, track = _reg(tmp_path, [row("b4_a")]), tmp_path / "markets.csv"
    with pytest.raises(tr.FoldedRowChanged):
        tr.write_track_rows([row("b4_a", disp="2%")], "b4_", reg, track)
    assert not track.exists()


def test_new_rows_written_with_register_header_and_other_tasks_kept(tmp_path):
    reg, track = _reg(tmp_path, [row("b4_a")]), tmp_path / "markets.csv"
    tr.write_track_rows([row("b2_x")], "b2_", reg, track)
    new = tr.write_track_rows([row("b4_a"), row("b4_b")], "b4_", reg, track)
    assert [r["claim_id"] for r in new] == ["b4_b"]
    got = list(csv.DictReader(open(track)))
    assert [r["claim_id"] for r in got] == ["b2_x", "b4_b"] and list(got[0].keys()) == H
