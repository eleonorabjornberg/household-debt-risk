"""Offline tests for run_e1.py: plan, refusal scoring, new units, stops, freeze gate. No network, no key."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec_ = importlib.util.spec_from_file_location("e1_run", HERE / "run_e1.py")
run_e1 = importlib.util.module_from_spec(spec_)
sys.modules["e1_run"] = run_e1
spec_.loader.exec_module(run_e1)
pilot = run_e1.pilot
TOOLS = [{"name": "public_share", "description": "x", "input_schema": {"type": "object", "properties": {}}}]


def call_tool(name, args):
    return {"ok": True}


def test_plan_excludes_holdout_and_is_seeded():
    gold = json.loads(run_e1.GOLD.read_text())
    p1, p2 = run_e1.plan(gold), run_e1.plan(gold)
    assert [q["id"] for q in p1] == [q["id"] for q in p2] and len(p1) == 80
    assert not any(q["holdout"] for q in p1)
    assert sum(q["gold"] == "refuse" for q in p1) == 20


@pytest.mark.parametrize("text,ok", [
    ("The data cannot answer this: Z.1 gives holders or types, never both.\nANSWER: none\nQUARTER: none", True),
    ("ANSWER: 12.5%\nQUARTER: none", False),
    ("Here is my best guess.\nANSWER: none", False),
])
def test_refusal_scoring(text, ok):
    assert pilot.score(text, {"gold": "refuse"})["correct"] is ok


@pytest.mark.parametrize("text,unit,gold,tol,ok", [
    ("ANSWER: $1,263 billion", "usd_bn", 1263.0, 1, True),
    ("ANSWER: 1.263 trillion", "usd_bn", 1263.0, 1, True),
    ("ANSWER: 7.83%", "pct", 7.83, 0.01, True),
    ("ANSWER: 3.56x", "ratio", 3.5624, 0.01, True),
    ("ANSWER: 299 quarters", "count", 299, 0, True),
    ("ANSWER: 298", "count", 299, 0, False),
])
def test_new_units(text, unit, gold, tol, ok):
    assert pilot.score(text, {"unit": unit, "gold": gold, "tolerance": tol})["correct"] is ok


def test_fake_run_uses_no_top_level_cache(tmp_path):
    seen = []

    class C(pilot.FakeClient):
        def create(self, **kw):
            seen.append(kw)
            return super().create(**kw)

    s = run_e1.run(C(), TOOLS, call_tool, tmp_path, reps=1)
    assert s["stop"] is None and s["loops_done"] == 240
    assert seen and all("cache_control" not in kw for kw in seen)
    assert all(kw["system"][0]["cache_control"] == {"type": "ephemeral"} for kw in seen)


def test_baseline_sends_no_tools(tmp_path):
    seen = []

    class C(pilot.FakeClient):
        def create(self, **kw):
            seen.append(kw)
            return type("R", (), {"usage": dict(self.usage), "stop_reason": "end_turn",
                                  "content": [{"type": "text", "text": "ANSWER: none"}]})()

    s = run_e1.run(C(), TOOLS, call_tool, tmp_path, reps=1, baseline="claude-haiku-5-5")
    assert s["loops_done"] == 80 and all("tools" not in kw for kw in seen)


def test_checkpoint_stops_on_projection(tmp_path):
    b = pilot.Budget(cap=5.0, assumed={m: 10.0 for m in pilot.MODELS})  # guard clear at 10%; projection ~$15 > $5
    s = run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, budget=b)
    assert s["stop"] and s["stop"]["reason"].startswith("checkpoint")


def test_overrun_stop_uses_planning_figure():
    b = pilot.Budget(cap=31, assumed=dict(run_e1.PLANNING))
    b.start_loop("claude-opus-5-5")
    b.add("claude-opus-5-5", 0.12)  # 2.98x the pilot mean: under 3x
    with pytest.raises(pilot.Stop, match="overrun"):
        b.add("claude-opus-5-5", 0.01)  # 3.23x


def test_live_refuses_until_frozen(tmp_path):
    draft, frozen = tmp_path / "d.md", tmp_path / "f.md"
    draft.write_text("# x\nStatus: **draft**, not frozen.\n")
    frozen.write_text("# x\nStatus: **frozen** on 2026-11-05.\n")
    assert not run_e1.is_frozen(draft) and run_e1.is_frozen(frozen)
    assert run_e1.snapshot_ok() == []  # snapshot, questions and gold match the recorded hashes


PLAN_ROWS = """| Date | Decision | Who |
|---|---|---|
| 2026-11-05 | E1 no-tools baseline model (e1-base): **Opus**. Not a spend OK. | Eleonora |
| 2026-11-05 | E1 cost cap (e1-cap): **$31**. The cap card sets the ceiling only. | Eleonora |
"""


@pytest.mark.parametrize("row,ok", [
    ("| 2026-11-06 | E1 full-run spend (e1-spend): **go**, cap $31, main run and Opus baseline. | Eleonora |", True),
    ("| 2026-11-06 | E1 spend (e1-spend, docket round 28): **approved**. | Eleonora |", True),
    ("| 2026-11-06 | E1 spend (e1-spend): **no**, not now. | Eleonora |", False),
    ("| 2026-11-06 | E1 spend (e1-spend): **later**. | Eleonora |", False),
    ("| 2026-11-06 | E1 spend (e1-spend): **go**. | Coordinator |", False),  # must be her row
])
def test_spend_row(row, ok):
    assert (run_e1.spend_row(PLAN_ROWS + row + "\n") is not None) is ok


def test_existing_rows_are_not_a_spend_ok():
    assert run_e1.spend_row(PLAN_ROWS) is None
    assert run_e1.spend_row((run_e1.ROOT / "PLAN.md").read_text()) is None  # no spend OK recorded yet


def test_approval_must_postdate_the_freeze():
    with pytest.raises(SystemExit, match="after the freeze"):
        run_e1.check_spend_approval(run_e1.FREEZE_COMMIT)
    with pytest.raises(SystemExit, match="after the freeze"):
        run_e1.check_spend_approval("134ee11")  # before the freeze


def test_head_has_no_approval_yet():
    with pytest.raises(SystemExit, match="no Eleonora row"):
        run_e1.check_spend_approval("HEAD")


OPT_A = "| 2026-11-05 | E1 spend (e1-spend, chosen 19:40 UTC): **OK** (a): the main run and the Opus baseline, within $31. | Eleonora |"
OPT_B = "| 2026-11-05 | E1 spend (e1-spend, chosen 19:40 UTC): **OK** (b): OK for the main run only; baseline later. | Eleonora |"
BASE_LATER = "| 2026-11-07 | E1 baseline spend (e1-baseline-spend, chosen 09:00 UTC): **OK**, Opus, remaining cap. | Eleonora |"


def test_option_a_covers_main_and_baseline():
    plan = PLAN_ROWS + OPT_A + "\n"
    assert run_e1.spend_row(plan) and run_e1.spend_row(plan, baseline=True)


def test_option_b_covers_main_run_only():
    plan = PLAN_ROWS + OPT_B + "\n"
    assert run_e1.spend_row(plan) == OPT_B
    assert run_e1.spend_row(plan, baseline=True) is None
    assert run_e1.spend_row(plan + BASE_LATER + "\n", baseline=True) == BASE_LATER  # a later explicit baseline OK


def test_baseline_row_alone_does_not_approve_the_main_run():
    assert run_e1.spend_row(PLAN_ROWS + BASE_LATER + "\n") is None


def test_ok_without_mentioning_the_baseline_does_not_cover_it():
    row = "| 2026-11-05 | E1 spend (e1-spend): **go**, cap $31. | Eleonora |"
    assert run_e1.spend_row(PLAN_ROWS + row + "\n") and run_e1.spend_row(PLAN_ROWS + row + "\n", baseline=True) is None
