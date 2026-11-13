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
    ("ANSWER: 27.7%", "ratio", 0.277022, 0.01, True),  # the 2026-11-05 run's first answer (q128): stated in percent
    ("ANSWER: 27.7", "ratio", 0.277022, 0.01, False),  # no unit stated: read as written
    ("ANSWER: 7.83%", "pct", 7.83, 0.01, True),
    ("ANSWER: 299 quarters", "count", 299, 0, True),
    ("ANSWER: 298", "count", 299, 0, False),
])
def test_new_units(text, unit, gold, tol, ok):
    assert pilot.score(text, {"unit": unit, "gold": gold, "tolerance": tol})["correct"] is ok


def test_fake_run_uses_the_restored_top_level_cache(tmp_path):
    seen = []

    class C(pilot.FakeClient):
        def create(self, **kw):
            seen.append(kw)
            return super().create(**kw)

    s = run_e1.run(C(), TOOLS, call_tool, tmp_path, reps=1)
    assert s["stop"] is None and s["loops_done"] == 240
    assert seen and all(kw.get("cache_control") == {"type": "ephemeral"} for kw in seen)  # e1-cost (b)
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
    b = pilot.Budget(cap=31, assumed=dict(run_e1.PLANNING))  # min_loops 0: the rule as frozen
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
    # her real approval (e1-spend (a), 2026-11-05 20:59 UTC) is the only matching row
    row = run_e1.spend_row((run_e1.ROOT / "PLAN.md").read_text())
    assert row and "chosen 20:59 UTC" in row and "(a)" in row


def test_approval_must_postdate_the_freeze():
    with pytest.raises(SystemExit, match="after the freeze"):
        run_e1.check_spend_approval(run_e1.FREEZE_COMMIT)
    with pytest.raises(SystemExit, match="after the freeze"):
        run_e1.check_spend_approval("134ee11")  # before the freeze


def test_approval_commit_and_an_earlier_commit():
    assert "chosen 20:59 UTC" in run_e1.check_spend_approval("6172f48")            # her e1-spend (a); 6172f48 is 4b0fd66 after the 2026-11-09 history rewrite
    assert "chosen 20:59 UTC" in run_e1.check_spend_approval("6172f48", baseline=True)
    with pytest.raises(SystemExit, match="no Eleonora row"):
        run_e1.check_spend_approval("eeede17")  # after the freeze, before her answer (post-rewrite SHA)


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


def test_never_overwrites_a_run(tmp_path):
    (tmp_path / "calls.jsonl").write_text("{}\n")
    with pytest.raises(SystemExit, match="already holds a run"):
        run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1)


def test_overrun_stop_waits_for_24_loops():  # e1-stoprule (a)
    b = pilot.Budget(cap=31, assumed=dict(run_e1.PLANNING), min_loops=run_e1.MIN_LOOPS)
    m = "claude-haiku-5-5"
    for _ in range(24):  # the first loop of the stopped run cost $0.003634, over the $0.0025 stop: no stop now
        b.start_loop(m)
        b.add(m, 0.003634)
    b.start_loop(m)
    with pytest.raises(pilot.Stop, match="overrun"):
        b.add(m, 0.003634)  # loop 25: the mean is over the stop, and the rule now applies


def test_cache_tokens_are_logged_and_priced(tmp_path):
    u = {"input_tokens": 100, "output_tokens": 10, "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 2000}
    run_e1.run(pilot.FakeClient(usage=u), TOOLS, call_tool, tmp_path, reps=1)
    rec = json.loads((tmp_path / "calls.jsonl").read_text().splitlines()[0])
    assert rec["usage"] == u
    assert rec["cost_usd"] == pytest.approx(pilot.call_cost(rec["model"], u), abs=1e-6)


# ---------------------------------------------------------------- e1-resume and e1-stop2 (2026-11-05, offline only)

def test_recalibrated_stops_are_hers():
    b = pilot.Budget(cap=31, assumed=dict(run_e1.STOP_BASIS))
    assert {m: round(b.overrun * b.assumed[m], 6) for m in pilot.MODELS} == {
        "claude-sonnet-5-5": 0.047, "claude-opus-5-5": 0.098, "claude-haiku-5-5": 0.002}


def _stop_midway(tmp_path, cap):
    b = pilot.Budget(cap=cap, assumed=dict(run_e1.STOP_BASIS), min_loops=run_e1.MIN_LOOPS)
    return run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1, budget=b)


def test_resume_skips_completed_loops_and_finishes_in_order(tmp_path):
    s1 = _stop_midway(tmp_path, cap=1.0)  # the pre-call guard stops it part-way
    assert s1["stop"] and 0 < s1["loops_done"] < 240
    first = (tmp_path / "calls.jsonl").read_text()
    n1 = s1["loops_done"]
    s2 = run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1, resume=True)
    assert s2["stop"] is None and s2["loops_done"] == 240 and s2["resumed_from_loop"] == n1 + 1
    res = [json.loads(l) for l in (tmp_path / "results.jsonl").read_text().splitlines()]
    gold = json.loads(run_e1.GOLD.read_text())
    order = [(1, q["id"], m) for q in run_e1.plan(gold) for m in pilot.MODELS]
    assert [(x["rep"], x["qid"], x["model"]) for x in res] == order  # every loop once, in the seeded order
    assert (tmp_path / "calls.jsonl").read_text().startswith(first)  # appended, never overwritten
    assert (tmp_path / "summary_part1.json").exists()
    assert any("resume" in json.loads(l) for l in (tmp_path / "calls.jsonl").read_text().splitlines())


def test_resume_carries_spend_into_cap_and_guard(tmp_path):
    s1 = _stop_midway(tmp_path, cap=1.0)
    spent = s1["total_usd"]
    b = pilot.Budget(cap=31, assumed=dict(run_e1.STOP_BASIS), min_loops=run_e1.MIN_LOOPS)
    carried = 31 - spent - 0.001  # less headroom than any model's worst-case call (Haiku: about $0.007)
    s2 = run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1, resume=True, budget=b, carried=carried)
    assert s2["stop"]["reason"].startswith("pre-call guard") and s2["loops_done"] == s1["loops_done"]
    assert b.total == pytest.approx(spent + carried, abs=1e-6)  # this run's spend + other runs' spend


def test_resume_refuses_a_mismatched_plan(tmp_path):
    _stop_midway(tmp_path, cap=1.0)
    lines = (tmp_path / "results.jsonl").read_text().splitlines()
    first = json.loads(lines[0])
    first["qid"] = "q999"
    (tmp_path / "results.jsonl").write_text("\n".join([json.dumps(first)] + lines[1:]) + "\n")
    with pytest.raises(SystemExit, match="do not match the seeded plan"):
        run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1, resume=True)


def test_refuses_a_mismatched_prereg_hash(tmp_path):
    hashes = json.loads(run_e1.HASHES.read_text())
    assert "docs/decisions/e1-prereg.md" in hashes  # the prereg (with its Deviations) is pinned
    hashes["docs/decisions/e1-prereg.md"] = "0" * 64
    f = tmp_path / "h.json"
    f.write_text(json.dumps(hashes))
    assert run_e1.snapshot_ok(f) == ["docs/decisions/e1-prereg.md"]


def test_e1_spend_so_far_counts_live_runs_only(tmp_path):
    for name, cost in (("run-a", 1.5), ("run-b", 0.25), ("run-fake-x", 9.0)):
        (tmp_path / name).mkdir()
        (tmp_path / name / "calls.jsonl").write_text(json.dumps({"cost_usd": cost}) + "\n" + json.dumps({"checkpoint": 1}) + "\n")
    assert run_e1.e1_spend_so_far(tmp_path) == pytest.approx(1.75)
    assert run_e1.e1_spend_so_far(tmp_path, exclude=tmp_path / "run-b") == pytest.approx(1.5)
    # the real live runs: the same as summing every non-fake run directory's logged costs directly
    direct = sum(json.loads(l).get("cost_usd", 0) for d in run_e1.HERE.glob("run-*") if "fake" not in d.name
                 for l in (d / "calls.jsonl").read_text().splitlines() if (d / "calls.jsonl").exists() and l.strip())
    assert run_e1.e1_spend_so_far() == pytest.approx(direct, abs=1e-9) and direct >= 2.590335


def test_checkpoint_does_not_scale_carried_spend(tmp_path):
    # the 2026-11-05 baseline stopped at a false checkpoint: $17.90 carried from other runs was divided by 24 loops
    # and scaled to 240 (projected $181). The projection must add carried spend once.
    s = run_e1.run(pilot.FakeClient(), TOOLS, call_tool, tmp_path, reps=1, baseline="claude-haiku-5-5", carried=17.9)
    cp = [json.loads(l) for l in (tmp_path / "calls.jsonl").read_text().splitlines() if "checkpoint" in l][0]
    assert s["stop"] is None and cp["projected_usd"] < 31
