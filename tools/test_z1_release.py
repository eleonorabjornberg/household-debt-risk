"""Tests for tools/z1_release.py (PLAN F3)."""
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import z1_release  # noqa: E402


def _zip(tmp: Path, when: tuple) -> Path:
    p = tmp / "FRB_Z1_csv.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(zipfile.ZipInfo("Z1.csv", date_time=when + (12, 0, 0)), "series_name,date,value\n")
    return p


def _meta(tmp: Path, z1: str) -> Path:
    p = tmp / "meta.json"
    p.write_text(json.dumps({"vintages": {"z1": z1, "fred": "2026-10-27", "nyfed": "2026-10-27"}}))
    return p


def test_detect_new_release(tmp_path):
    out = z1_release.detect(_zip(tmp_path, (2026, 12, 11)), _meta(tmp_path, "2026-09-11"))
    assert out["new"] == "true" and out["vintage"] == "2026-12-11" and out["previous"] == "2026-09-11"
    assert out["prev_url"].endswith("/releases/z1/20260911/z1_csv_files.zip")


def test_detect_same_release(tmp_path):
    assert z1_release.detect(_zip(tmp_path, (2026, 9, 11)), _meta(tmp_path, "2026-09-11"))["new"] == "false"


def test_pr_body_says_nothing_is_published(tmp_path):
    (tmp_path / "what_moved.md").write_text("# What moved\nPublic share 56.4%\n")
    body = z1_release.pr_body(tmp_path)
    assert "Nothing is published or loaded until Eleonora reviews and merges" in body
    assert "Public share 56.4%" in body and "stale_claims.txt was not produced" in body
