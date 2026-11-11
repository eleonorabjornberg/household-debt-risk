"""B4 volume side (docket 56 b4-student-proxy-map (b)): transcription of ED's RIA Table 3.1 and its identities."""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ed_volume", HERE / "ed_volume.py")
ed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ed)
TEXT = ed.FIXTURE.read_text()

# Hand-checked by Claude against the rendered PDF page (91 FR 23855), not only the text layer, 2026-11-11.
HAND = {"undergrad": (94.5, 93.4, 355842, 352085), "grad_stafford_plus": (22.2, 13.9, 436437, 265542),
        "parent_plus": (7.9, 7.3, 154140, 104881), "consolidation": (12.8, 8.4, 454638, 338687)}


def test_transcription_matches_hand_check():
    t = ed.parse(TEXT)
    for k, (lp, lq, dp, dq) in HAND.items():
        assert (t[k]["loans_pre_m"], t[k]["loans_post_m"], t[k]["disbursed_pre_musd"], t[k]["disbursed_post_musd"]) == (lp, lq, dp, dq)
    assert t["noncons_difference"] == {"loans_m": -9.9, "disbursed_musd": -223911}


def test_identities_and_text():
    r = ed.compute(ed.parse(TEXT))
    assert r["noncons_fall_musd"] == 223911
    assert round(r["noncons_fall_musd"] / 1e2) / 10 == 223.9          # "$223.9 billion" in the rule's text
    assert "not an estimate of lending moving to private lenders" in r["label"]


def test_planted_typo_fails():
    with pytest.raises(ValueError):
        ed.compute(ed.parse(TEXT.replace("265,542", "256,542")))


def test_committed_json_is_current():
    assert json.loads((HERE / "ed_volume.json").read_text()) == json.loads(json.dumps(ed.compute(ed.parse(TEXT))))


def test_sources_md_records_the_pdf():
    src = (HERE / "sources.md").read_text()
    assert "21ef3bab376f85734582ebd3e10e7c89133c00c99e6be5d2c1aec671483f56ac" in src
