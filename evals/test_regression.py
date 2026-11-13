"""E3 regression runner (evals/regression.py) on a synthetic repo root. No eval is run."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("regression", HERE / "regression.py")
reg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reg)


def _root(tmp_path, prompt="v1"):
    (tmp_path / ".claude/agents").mkdir(parents=True)
    (tmp_path / ".claude/agents/skeptic.md").write_text(f"---\nmodel: opus\n---\n{prompt}\n")
    return tmp_path


def test_fingerprint_changes_with_prompt_and_reads_model(tmp_path):
    root = _root(tmp_path)
    a = reg.fingerprint([".claude/agents/skeptic.md", "missing.yaml"], root)
    assert a["models"] == {"skeptic": "opus"} and a["files"]["missing.yaml"] == "missing"
    (root / ".claude/agents/skeptic.md").write_text("---\nmodel: sonnet\n---\nv2\n")
    b = reg.fingerprint([".claude/agents/skeptic.md", "missing.yaml"], root)
    assert a["digest"] != b["digest"] and b["models"] == {"skeptic": "sonnet"}


def test_status_never_run_then_up_to_date_then_rerun(tmp_path, monkeypatch):
    root = _root(tmp_path)
    res = root / "results.jsonl"
    monkeypatch.setitem(reg.EVALS, "E2", {"results": res, "inputs": [".claude/agents/skeptic.md"], "run": "x"})
    state = lambda: next(s for s in reg.status(root) if s["eval"] == "E2")["state"]
    assert state() == "NEVER RUN"
    res.write_text(json.dumps({"scored_at": "2026-11-05", "fingerprint": reg.fingerprint([".claude/agents/skeptic.md"], root)}) + "\n")
    assert state() == "UP TO DATE"
    (root / ".claude/agents/skeptic.md").write_text("---\nmodel: opus\n---\nchanged\n")
    assert state() == "RERUN NEEDED"
    monkeypatch.setitem(reg.EVALS, "E1", {"results": root / "e1.jsonl", "inputs": [".claude/agents/skeptic.md"], "run": "x"})
    (root / "e1.jsonl").write_text(json.dumps({"run": "r", "scored_at": "2026-11-05", "fingerprint": None}) + "\n")
    assert next(s for s in reg.status(root) if s["eval"] == "E1")["state"] == "RUN, UNFINGERPRINTED"


def test_chart_without_results_says_so(tmp_path, monkeypatch):
    monkeypatch.setitem(reg.EVALS, "E2", {"results": tmp_path / "none.jsonl", "inputs": [], "run": "x"})
    assert reg.chart(tmp_path).startswith("no E2 results yet")
