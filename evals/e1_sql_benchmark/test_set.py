"""Offline tests for the E1 question set: evaluator, two-path verification, holdout, NY Fed parser. No network."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "validation")]
import spec  # noqa: E402


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


verify_set = _load("e1_verify_set", HERE / "verify_set.py")
QS = yaml.safe_load((HERE / "questions.yaml").read_text())["questions"]

T = {"ps": [{"date": "2000-03-31", "x": 1.0, "k": "a"}, {"date": "2000-03-31", "x": 2.0, "k": "b"},
            {"date": "2000-06-30", "x": 4.0, "k": "a"}, {"date": "2000-06-30", "x": None, "k": "b"}]}


def test_evaluator_ops():
    at = {"table": "ps", "field": "x", "op": "at", "date": "2000-03-31"}
    assert spec.evaluate(at, T) == (3.0, None)  # rows on one date are summed
    with pytest.raises(KeyError):  # a missing value on a date is never treated as zero
        spec.evaluate({**at, "date": "2000-06-30"}, T)
    a = {"table": "ps", "field": "x", "where": {"k": "a"}}
    assert spec.evaluate({**a, "op": "diff", "from": "2000-03-31", "to": "2000-06-30"}, T) == (3.0, None)
    assert spec.evaluate({**a, "op": "pct_change", "from": "2000-03-31", "to": "2000-06-30"}, T)[0] == pytest.approx(300)
    assert spec.evaluate({**a, "op": "argmax"}, T) == (4.0, "2000Q2")
    assert spec.evaluate({**a, "op": "mean"}, T) == (2.5, None)
    c = {"combine": {"op": "div", "scale": 10, "args": [{**a, "op": "at", "date": "2000-06-30"}, at]}}
    assert spec.evaluate(c, T)[0] == pytest.approx(40 / 3)


def test_set_shape_matches_her_choices():
    fams = {f: [q for q in QS if q["family"] == f] for f in ("PS", "HB", "CW", "CC", "NY", "RG", "UN")}
    assert len(QS) == 100 and len({q["id"] for q in QS}) == 100
    assert len(fams["UN"]) == 15 and all(q.get("refuse") and q.get("reason") for q in fams["UN"])
    for f in ("PS", "HB", "CW", "CC", "NY"):
        assert sorted(q["difficulty"] for q in fams[f]) == ["C"] * 5 + ["L"] * 5 + ["M"] * 5
    pilot = {q["question"] for q in yaml.safe_load((HERE / "pilot_questions.yaml").read_text())["questions"]}
    assert not pilot & {q["question"] for q in QS}  # pilot questions are not reused


def test_every_gold_answer_verifies_two_ways():
    res = verify_set.verify()
    assert all(r["ok"] for r in res), [r for r in res if not r["ok"]]
    committed = json.loads((HERE / "gold.json").read_text())["questions"]
    num = lambda rs: [r["gold"] for r in rs if r["gold"] != "refuse"]
    assert num(committed) == pytest.approx(num(res), rel=1e-12)  # gold.json is up to date
    assert {r["id"]: r["holdout"] for r in committed} == {r["id"]: r["holdout"] for r in res}


def test_holdout_is_seeded_and_stratified():
    h1, h2 = verify_set.holdout(QS), verify_set.holdout(QS)
    assert h1 == h2 and len(h1) == 20
    by = {q["id"]: q["family"] for q in QS}
    assert {f: sum(by[i] == f for i in h1) for f in verify_set.HOLDOUT_PER_FAMILY} == verify_set.HOLDOUT_PER_FAMILY
    assert verify_set.holdout(QS, seed=1) != h1


def test_disagreement_is_caught(tmp_path):
    import csv
    src = ROOT / "claims" / "register.csv"  # the E1 rows were folded in here on merge
    rows = list(csv.DictReader(src.open()))
    for r in rows:
        if r["claim_id"] == "e1_q101":
            r["value"] = f"{float(r['value']) + 0.001:.6f}"
    bad = tmp_path / "register.csv"
    with bad.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    res = verify_set.verify(registers=[bad])
    assert [r["id"] for r in res if not r["ok"]] == ["q101"]


def test_nyfed_quarter_labels():
    e1_gold = _load("e1_gold_t", ROOT / "validation" / "e1_gold.py")
    assert e1_gold._qdate("03:Q1") == "2003-03-31"
    assert e1_gold._qdate("26:Q2") == "2026-06-30"
    assert e1_gold._qdate("Total") is None
