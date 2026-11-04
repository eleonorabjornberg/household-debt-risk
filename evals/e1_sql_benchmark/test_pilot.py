"""Offline tests for the E1 pilot runner: cost arithmetic, hard stops, scoring. No network, no key."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("e1_pilot", HERE / "pilot.py")
pilot = importlib.util.module_from_spec(spec)
sys.modules["e1_pilot"] = pilot
spec.loader.exec_module(pilot)

TOOLS = [{"name": "public_share", "description": "x", "input_schema": {"type": "object", "properties": {}}}]


def call_tool(name, args):
    return {"ok": True, "tool": name}


def test_call_cost_uses_all_four_token_kinds():
    u = {"input_tokens": 1_000_000, "output_tokens": 1_000_000,
         "cache_read_input_tokens": 1_000_000, "cache_creation_input_tokens": 1_000_000}
    assert pilot.call_cost("claude-opus-5-5", u) == pytest.approx(4 + 20 + 0.20 + 5)
    assert pilot.call_cost("claude-sonnet-5-5", u) == pytest.approx(2 + 10 + 0.10 + 2.50)
    assert pilot.call_cost("claude-haiku-5-5", u) == pytest.approx(0.10 + 0.50 + 0.01 + 0.125)


def test_fake_run_completes_under_assumption(tmp_path):
    s = pilot.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path)
    assert s["stop"] is None
    assert {m: v["loops_scored"] for m, v in s["per_model"].items()} == {m: 10 for m in pilot.MODELS}
    lines = (tmp_path / "calls.jsonl").read_text().splitlines()
    assert len(lines) == 60  # 10 questions x 3 models x 2 turns
    assert s["total_usd"] == pytest.approx(sum(json.loads(x)["cost_usd"] for x in lines), abs=1e-5)


def test_overrun_stops_after_first_expensive_call(tmp_path):
    # 30k uncached input + 1k output on Haiku = $0.0035 per call; two calls per loop = $0.007 > 1.5 x $0.0033
    fat = {"input_tokens": 30_000, "output_tokens": 1_000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    c = pilot.FakeClient(usage=fat)
    s = pilot.run(c, TOOLS, call_tool, tmp_path)
    assert s["stop"] and s["stop"]["reason"].startswith("overrun: claude-haiku-5-5")
    assert c.calls == 2 and s["stop"]["at"]["turn"] == 2
    assert (tmp_path / "summary.json").exists()


def test_cap_stops_before_crossing(tmp_path):
    b = pilot.Budget(cap=0.05)
    s = pilot.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, budget=b)
    assert s["stop"] is not None
    assert s["total_usd"] < 0.05  # the pre-call guard stops before a call could cross the cap


def test_cap_hit_after_call_is_reported():
    b = pilot.Budget(cap=1.0)
    b.start_loop("claude-opus-5-5")
    with pytest.raises(pilot.Stop, match="cap"):
        b.add("claude-opus-5-5", 1.0)


@pytest.mark.parametrize("text,unit,gold,ok", [
    ("blah\nANSWER: 56.38%\nQUARTER: none", "share", 0.5638311569, True),
    ("ANSWER: 0.5638\nQUARTER: none", "share", 0.5638311569, True),
    ("ANSWER: 56.0%", "share", 0.5638311569, False),
    ("ANSWER: 7.31 trillion", "usd_tn", 7.312, True),
    ("ANSWER: 7,312 billion", "usd_tn", 7.312, True),
    ("ANSWER: $7,312,000 million", "usd_tn", 7.312, True),
    ("I cannot answer that.", "share", 0.5, False),
])
def test_scoring_rule(text, unit, gold, ok):
    tol = {"share": 0.0005, "usd_tn": 0.01}[unit]
    assert pilot.score(text, {"unit": unit, "gold": gold, "tolerance": tol})["correct"] is ok


def test_quarter_must_match():
    g = {"unit": "share", "gold": 0.6, "tolerance": 0.0005, "quarter": "2021Q1"}
    assert pilot.score("ANSWER: 60.0%\nQUARTER: 2021Q1", g)["correct"]
    assert not pilot.score("ANSWER: 60.0%\nQUARTER: 2020Q4", g)["correct"]


def test_no_secret_in_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("HHDEBT_ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    pilot.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path)
    for f in tmp_path.iterdir():
        txt = f.read_text()
        assert "sk-test" not in txt and "x-api-key" not in txt.lower()
