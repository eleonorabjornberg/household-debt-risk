#!/usr/bin/env python3
"""E1 full run (docs/decisions/e1-prereg.md): 80 scored questions x 3 models x 3 repetitions, plus the baseline.

    # offline rehearsal, fake client, no network, no key, no spend:
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --fake
    # live: REFUSES unless the prereg is frozen; also needs Eleonora's separate spend OK (recorded by the coordinator)
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --live
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --live --baseline MODEL

Settings are Eleonora's choices of 2026-11-05 (prereg "Decisions"): turn limit 4, effort medium, 3 repetitions, no
top-level cache, all 10 tools, seed 20261104, pilot scoring rule, holdout of 20 not run, cap $31 shared by the main
run and the baseline. Stops: the cap (with a pre-call guard), a model's mean cost per loop above 1.5x its planning
figure (2x the pilot mean, so 3x the pilot), and a projection checkpoint after 10% of loops.
Key and client handling are pilot.py's (HHDEBT_ANTHROPIC_API_KEY, explicit first-party base URL, nothing logged).
This script records answers and scores only; the hypothesis tests (T, R, McNemar, Holm) are a separate analysis
step under the frozen prereg.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import pilot  # noqa: E402

PREREG = ROOT / "docs" / "decisions" / "e1-prereg.md"
GOLD = HERE / "gold.json"
HASHES = HERE / "snapshot_hashes.json"
SEED = 20261104
REPS = 3
CAP_USD = 31.0
PILOT_MEAN = {"claude-opus-5-5": 0.040264, "claude-sonnet-5-5": 0.010154, "claude-haiku-5-5": 0.000821}
PLANNING = {m: 2 * v for m, v in PILOT_MEAN.items()}  # stop at 1.5x this = 3x the pilot mean
CHECKPOINT = 0.10


def is_frozen(path: Path = PREREG) -> bool:
    return bool(re.search(r"^Status: \*\*frozen\*\*", path.read_text(), flags=re.M))


def snapshot_ok(hashes: Path = HASHES) -> list[str]:
    bad = []
    for rel, h in json.loads(hashes.read_text()).items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != h:
            bad.append(rel)
    return bad


def plan(gold: dict, seed: int = SEED) -> list[dict]:
    qs = [q for q in gold["questions"] if not q["holdout"]]
    random.Random(seed).shuffle(qs)
    return qs


def run(client, tools, call_tool, outdir: Path, models=pilot.MODELS, reps: int = REPS, budget=None,
        baseline: str | None = None) -> dict:
    gold = json.loads(GOLD.read_text())
    qs = plan(gold)
    if baseline:
        models, tools = [baseline], []
    total_loops = len(qs) * len(models) * reps
    budget = budget or pilot.Budget(cap=CAP_USD, assumed=dict(PLANNING))
    outdir.mkdir(parents=True, exist_ok=True)
    calls = (outdir / "calls.jsonl").open("w")
    results, stop, done = [], None, 0

    def log(rec):
        rec["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        calls.write(json.dumps(rec) + "\n")
        calls.flush()

    try:
        for rep in range(1, reps + 1):
            for q in qs:
                for m in models:
                    loop = pilot.run_loop(client, m, q, tools, call_tool, budget, log, top_cache=False, rep=rep)
                    s = pilot.score(loop["final_text"], q)
                    results.append({"qid": q["id"], "model": m, "rep": rep, "family": q["family"],
                                    "difficulty": q["difficulty"], **{k: v for k, v in loop.items() if k != "final_text"},
                                    "truncated": loop["stop_reason"] == "tool_use", **s})
                    done += 1
                    if done == max(1, int(total_loops * CHECKPOINT)):
                        proj = budget.total / done * total_loops
                        log({"checkpoint": done, "of": total_loops, "spent_usd": round(budget.total, 6),
                             "projected_usd": round(proj, 4)})
                        if proj > budget.cap:
                            raise pilot.Stop(f"checkpoint: projected ${proj:.2f} > cap ${budget.cap:.2f} "
                                             f"after {done}/{total_loops} loops")
    except pilot.Stop as e:
        lines = (outdir / "calls.jsonl").read_text().splitlines()
        stop = {"reason": str(e), "at": json.loads(lines[-1]) if lines else None}
    finally:
        calls.close()
    summary = {"mode": "baseline (no tools)" if baseline else "main", "cap_usd": budget.cap,
               "total_usd": round(budget.total, 6), "loops_planned": total_loops, "loops_done": done,
               "stop": stop, "per_model": {}}
    for m, (spent, loops) in budget.by_model.items():
        rs = [r for r in results if r["model"] == m]
        summary["per_model"][m] = {
            "loops": loops, "spent_usd": round(spent, 6), "mean_per_loop_usd": round(spent / loops, 6) if loops else None,
            "correct": sum(r["correct"] for r in rs), "scored": len(rs), "truncated": sum(r["truncated"] for r in rs)}
    (outdir / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    (outdir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fake", action="store_true")
    g.add_argument("--live", action="store_true")
    ap.add_argument("--baseline", choices=pilot.MODELS, help="no-tools baseline on this model (CHOICE-E1-16)")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.live:
        if not is_frozen():
            raise SystemExit("refusing: docs/decisions/e1-prereg.md is not frozen")
        bad = snapshot_ok()
        if bad:
            raise SystemExit(f"refusing: files differ from the recorded hashes: {bad}")
    tools, call_tool = pilot.mcp_tools()
    date = datetime.now(timezone.utc).date().isoformat()
    tag = ("baseline-" if a.baseline else "") + ("" if a.live else "fake-")
    out = a.out or (HERE / f"run-{tag}{date}")
    client = pilot.live_client() if a.live else pilot.FakeClient()
    print(json.dumps(run(client, tools, call_tool, out, baseline=a.baseline), indent=1))


if __name__ == "__main__":
    main()
