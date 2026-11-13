"""E2 tooling on synthetic documents: planting, key commitment, scoring (no reviewer runs, no results)."""
import csv
import importlib.util
import json
import random
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


plant, score = _load("plant"), _load("score")

DATA_DOC = """# Synthetic
The public share rose from 36.1% in 2007Q4 to 49.2% in 2011Q4 (Z.1).

Agency pools and GSE portfolios hold most of it, 65.6% of mortgages.

Vintage z1:2026-09-11, data for 2026Q2.

The public share of consumer credit was 31.3% in 2026Q2 (Z.1).

Banks held 18.5% of the total in 2026Q2.
"""
METHOD_DOC = """# Nowcast
The nowcast is evaluated out-of-sample on a holdout period.

A test of equal accuracy compares the model with the forecast error of the benchmark.

Its error bands are an interval from the regression model.

Inputs use real-time vintages from ALFRED.
"""


def test_catalogue_covers_both_agents():
    cat = plant.load_catalogue()
    assert {e["agent"] for e in cat} == {"skeptic", "quant-reviewer"}
    assert len({e["id"] for e in cat}) == len(cat)


def test_plant_is_deterministic_and_records_lines():
    data = [e for e in plant.load_catalogue() if e["agent"] == "skeptic"]
    a = plant.plant_doc(DATA_DOC, data, 3, random.Random(7))
    b = plant.plant_doc(DATA_DOC, data, 3, random.Random(7))
    assert a == b and len(a[1]) == 3
    lines = a[0].split("\n")
    for e in a[1]:
        assert lines[e["line"] - 1] == e["planted"]


def test_refuses_unless_frozen(tmp_path):
    src = tmp_path / "d.md"
    src.write_text(DATA_DOC)
    draft = tmp_path / "prereg.md"
    draft.write_text("Status: **draft** (2026-11-04).\n")
    frozen = tmp_path / "frozen.md"
    frozen.write_text("Status: **frozen** (2026-11-04).\n")
    assert not plant.is_frozen(draft) and plant.is_frozen(frozen)
    old = plant.PREREG
    plant.PREREG = draft
    try:
        with pytest.raises(SystemExit):
            plant.run([src], [], 1, 1, 0, 1, tmp_path / "run")
    finally:
        plant.PREREG = old


def test_per_agent_counts(tmp_path):
    d, m = tmp_path / "d.md", tmp_path / "m.md"
    d.write_text(DATA_DOC)
    m.write_text(METHOD_DOC)
    run = tmp_path / "run"
    plant.run([d], [m], {"skeptic": 2, "quant-reviewer": 1}, 1,
              {"skeptic": 1, "quant-reviewer": 1}, 5, run, rehearsal=True)
    key = json.loads((run / "key.json").read_text())
    planted = [(v["agent"], v["control"]) for v in key["variants"]]
    assert sorted(planted) == sorted([("skeptic", False)] * 2 + [("quant-reviewer", False)] +
                                     [("skeptic", True), ("quant-reviewer", True)])


def test_real_prereg_is_frozen():
    """E2 was frozen 2026-11-04 (CHOICE-11 (a)); plant.py may run without --rehearsal."""
    assert plant.is_frozen()


def _rehearse(tmp_path):
    d, m = tmp_path / "d.md", tmp_path / "m.md"
    d.write_text(DATA_DOC)
    m.write_text(METHOD_DOC)
    run = tmp_path / "run"
    plant.run([d], [m], 4, 2, 2, 11, run, rehearsal=True)
    return run, json.loads((run / "key.json").read_text())


def test_key_commitment_and_controls(tmp_path):
    run, key = _rehearse(tmp_path)
    assert sum(v["control"] for v in key["variants"]) == 2
    assert all(not v["errors"] for v in key["variants"] if v["control"])
    assert score.load_key(run)["seed"] == 11
    (run / "key.json").write_text((run / "key.json").read_text().replace('"seed": 11', '"seed": 12'))
    with pytest.raises(SystemExit):
        score.load_key(run)


def test_match_and_summarise(tmp_path):
    jsonl = HERE / "results" / "results.jsonl"
    before = jsonl.read_bytes() if jsonl.exists() else None
    run, key = _rehearse(tmp_path)
    v = next(v for v in key["variants"] if v["errors"])
    e = v["errors"][0]
    ctrl = next(v for v in key["variants"] if v["control"])
    (run / "review-log.md").write_text(
        f"### R-20261105-1 · {e['agent']} · {v['doc']}\n- **Objection:** wrong.\n- **Severity:** major\n"
        f"- **Evidence:** {v['doc']}:{e['line']}\n- **Status:** open\n\n"
        f"### R-20261105-2 · skeptic · {ctrl['doc']}\n- **Objection:** odd.\n- **Severity:** major\n"
        f"- **Evidence:** {ctrl['doc']}:2\n- **Status:** open\n")
    n, located = score.match(run)
    assert located >= 1
    rows = list(csv.DictReader((run / "scoring.csv").open()))
    for r in rows:
        if r["located"] == "yes":
            r["same_fix"] = "yes"
    with (run / "scoring.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    objs = list(csv.DictReader((run / "objections.csv").open()))
    for o in objs:
        o["real_problem"] = "no"
    with (run / "objections.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(objs[0]))
        w.writeheader()
        w.writerows(objs)
    res = score.summarise(run)
    assert res["rehearsal"] and (run / "rehearsal_summary.json").exists()
    assert (jsonl.read_bytes() if jsonl.exists() else None) == before  # rehearsals never reach results/
    assert res["false_alarms"]["objections_on_controls"] == 1
    lo, hi = res["by_agent"][e["agent"]]["wilson95"]
    assert 0 <= lo <= hi <= 1


def test_wilson_known_value():
    lo, hi = score.wilson(18, 36)
    assert abs(lo - 0.3442) < 1e-3 and abs(hi - 0.6558) < 1e-3


def test_stratified_plants_each_category_equally(tmp_path):
    """CHOICE-10 (b): every category of an agent is planted the same number of times."""
    cat = plant.load_catalogue()
    n_s = sum(e["agent"] == "skeptic" for e in cat)
    # one planted data document per category with k = 1: each skeptic category exactly once
    docs = [DATA_DOC] * n_s
    groups = plant.stratify(docs, [e for e in cat if e["agent"] == "skeptic"], 1, random.Random(3))
    counts = {}
    for g in groups:
        for e in g:
            counts[e["id"]] = counts.get(e["id"], 0) + 1
    fits = [e["id"] for e in cat if e["agent"] == "skeptic" and plant.plant_doc(DATA_DOC, [e], 1, random.Random(0))[1]]
    if len(fits) < n_s:
        pytest.skip("synthetic data document does not fit every category")
    assert set(counts.values()) == {1} and len(counts) == n_s
    assert groups == plant.stratify(docs, [e for e in cat if e["agent"] == "skeptic"], 1, random.Random(3))


def test_stratified_rejects_uneven_split():
    cat = [e for e in plant.load_catalogue() if e["agent"] == "skeptic"]
    with pytest.raises(SystemExit):
        plant.stratify([DATA_DOC], cat, 3, random.Random(0))
