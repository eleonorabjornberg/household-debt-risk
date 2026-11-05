#!/usr/bin/env python3
"""E1 full run (docs/decisions/e1-prereg.md): 80 scored questions x 3 models x 3 repetitions, plus the baseline.

    # offline rehearsal, fake client, no network, no key, no spend:
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --fake
    # live: REFUSES unless the prereg is frozen, the files match their hashes, and --approval names a commit whose
    # PLAN.md "Decisions taken" has Eleonora's dated row approving card e1-spend (after the freeze, an ancestor of HEAD)
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --live --approval COMMIT
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/run_e1.py --live --approval COMMIT \
        --baseline claude-opus-5-5 --cap <31 minus the main run's spend>

Settings are Eleonora's choices of 2026-11-05 (prereg "Decisions" and "Deviations"): turn limit 4, effort medium,
3 repetitions, top-level cache restored (deviation, e1-cost (b)), all 10 tools, seed 20261104, pilot scoring rule, holdout of 20 not run, cap $31 shared by the main
run and the baseline. Stops: the cap (with a pre-call guard), a model's mean cost per loop above 1.5x its planning
figure (2x the pilot mean, so 3x the pilot), applied only after 24 loops per model (deviation, e1-stoprule (a)), and a
projection checkpoint after 10% of loops.
Key and client handling are pilot.py's (HHDEBT_ANTHROPIC_API_KEY, explicit first-party base URL, nothing logged).
This script records answers and scores only; the hypothesis tests (T, R, McNemar, Holm) are a separate analysis
step under the frozen prereg.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
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
FREEZE_COMMIT = "e0ae2d6"  # "prereg: E1 (frozen)", 2026-11-05
GOLD = HERE / "gold.json"
HASHES = HERE / "snapshot_hashes.json"
SEED = 20261104
REPS = 3
CAP_USD = 31.0
PILOT_MEAN = {"claude-opus-5-5": 0.040264, "claude-sonnet-5-5": 0.010154, "claude-haiku-5-5": 0.000821}
PLANNING = {m: 2 * v for m, v in PILOT_MEAN.items()}  # stop at 1.5x this = 3x the pilot mean
# Deviations of 2026-11-05 (Eleonora, PLAN 32ec93a): e1-stoprule (a) the overrun stop applies only after 24 loops per
# model; e1-cost (b) the top-level prompt cache is restored (reverses CHOICE-E1-5 (b)).
MIN_LOOPS = 24
TOP_CACHE = True
# Deviation of 2026-11-05 21:40 UTC (Eleonora, e1-stop2 "recal", PLAN 74cdbb5): each model's overrun stop is reset to
# 1.5x its measured mean cost per loop over the first 27 loops of run-2026-11-05b. Cap, guard and checkpoint unchanged.
RECAL_STOP = {"claude-sonnet-5-5": 0.047, "claude-opus-5-5": 0.098, "claude-haiku-5-5": 0.0020}
STOP_BASIS = {m: v / 1.5 for m, v in RECAL_STOP.items()}  # Budget stops at overrun (1.5) x this = RECAL_STOP


def e1_spend_so_far(root: Path = HERE, exclude: Path | None = None) -> float:
    """Spend logged in every live E1 run directory (run-*, not fake runs), except `exclude`."""
    total = 0.0
    for d in sorted(root.glob("run-*")):
        if "fake" in d.name or (exclude is not None and d.resolve() == exclude.resolve()):
            continue
        f = d / "calls.jsonl"
        if f.exists():
            total += sum(json.loads(l).get("cost_usd", 0) for l in f.read_text().splitlines() if l.strip())
    return total
CHECKPOINT = 0.10


def is_frozen(path: Path = PREREG) -> bool:
    return bool(re.search(r"^Status: \*\*frozen\*\*", path.read_text(), flags=re.M))


SPEND_ROW = re.compile(r"\(e1-spend\b[^)]*\)[^|]*?\*\*\s*(go|yes|ok|approved?)\b", re.I)
# A separate, explicit OK for the baseline (if she approves the main run only first): card e1-baseline-spend.
BASELINE_ROW = re.compile(r"\(e1-baseline-spend\b[^)]*\)[^|]*?\*\*\s*(go|yes|ok|approved?)\b", re.I)
# An e1-spend OK that limits itself to the main run (card option (b)) does not cover the baseline.
MAIN_ONLY = re.compile(r"main[- ]run only|only (?:for |the )*main[- ]run|baseline (?:later|not|excluded)|"
                       r"not (?:for )?the baseline|without the baseline|no baseline", re.I)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _her_rows(plan_text: str) -> list[str]:
    return [l for l in plan_text.splitlines()
            if re.match(r"\| 20\d\d-\d\d-\d\d \|", l) and l.rstrip().endswith("| Eleonora |")]


def spend_row(plan_text: str, baseline: bool = False) -> str | None:
    """Eleonora's dated "Decisions taken" row approving this spend, or None.
    Main run: a row naming card e1-spend with an approving verdict in bold (go / yes / ok / approve(d)); her other E1
    rows ("Not a spend OK") do not match.
    Baseline: either an e1-spend OK row that names the baseline and does not limit itself to the main run (card
    option (a)), or a separate OK row naming card e1-baseline-spend. Option (b), "OK for the main run only; baseline
    later", approves the main run but not the baseline."""
    rows = _her_rows(plan_text)
    if not baseline:
        ok = [l for l in rows if SPEND_ROW.search(l)]
    else:
        ok = [l for l in rows if BASELINE_ROW.search(l)
              or (SPEND_ROW.search(l) and re.search(r"baseline", l, re.I) and not MAIN_ONLY.search(l))]
    return ok[-1] if ok else None


def check_spend_approval(commit: str, baseline: bool = False) -> str:
    """The approval commit comes after the freeze, is an ancestor of HEAD, and its PLAN.md has her e1-spend row."""
    if git("merge-base", "--is-ancestor", FREEZE_COMMIT, commit).returncode != 0 or \
            git("rev-parse", FREEZE_COMMIT).stdout.strip() == git("rev-parse", commit).stdout.strip():
        raise SystemExit(f"refusing: the approval commit must come after the freeze commit {FREEZE_COMMIT}")
    if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
        raise SystemExit("refusing: the approval commit is not an ancestor of HEAD")
    plan = git("show", f"{commit}:PLAN.md")
    if plan.returncode != 0:
        raise SystemExit(f"refusing: cannot read PLAN.md at {commit}")
    row = spend_row(plan.stdout, baseline=baseline)
    if not row:
        what = ("the E1 baseline spend (an e1-spend OK covering the baseline, or card e1-baseline-spend)" if baseline
                else "the E1 spend (card e1-spend)")
        raise SystemExit(f"refusing: no Eleonora row in PLAN.md at {commit} approving {what}")
    return row


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
        baseline: str | None = None, approval: dict | None = None, resume: bool = False,
        carried: float = 0.0) -> dict:
    """carried: E1 spend in OTHER run directories, counted against the cap (and the guard) from the start.
    resume: continue `outdir` after its last completed loop, in the same seeded order (e1-resume, 2026-11-05)."""
    gold = json.loads(GOLD.read_text())
    qs = plan(gold)
    if baseline:
        models, tools = [baseline], []
    order = [(rep, q, m) for rep in range(1, reps + 1) for q in qs for m in models]
    total_loops = len(order)
    budget = budget or pilot.Budget(cap=CAP_USD, assumed=dict(STOP_BASIS), min_loops=MIN_LOOPS)
    budget.total += carried
    prior: list[dict] = []
    if resume:
        if not (outdir / "calls.jsonl").exists() or not (outdir / "results.jsonl").exists():
            raise SystemExit(f"refusing: nothing to resume in {outdir}")
        prior = [json.loads(l) for l in (outdir / "results.jsonl").read_text().splitlines() if l.strip()]
        expect = [(r, q["id"], m) for r, q, m in order[:len(prior)]]
        if [(x["rep"], x["qid"], x["model"]) for x in prior] != expect:
            raise SystemExit("refusing: completed loops do not match the seeded plan's first loops")
        old_calls = [json.loads(l) for l in (outdir / "calls.jsonl").read_text().splitlines() if l.strip()]
        for m in models:  # spend of this run so far (incl. any interrupted loop), loops = completed loops
            spent = sum(c.get("cost_usd", 0) for c in old_calls if c.get("model") == m)
            budget.by_model[m] = [spent, sum(1 for x in prior if x["model"] == m)]
            budget.total += spent
        if (outdir / "summary.json").exists():
            part = 1
            while (outdir / f"summary_part{part}.json").exists():
                part += 1
            (outdir / "summary.json").rename(outdir / f"summary_part{part}.json")
        calls = (outdir / "calls.jsonl").open("a")
    else:
        if (outdir / "calls.jsonl").exists():  # results are append-only: never overwrite a run
            raise SystemExit(f"refusing: {outdir} already holds a run; pass a new --out")
        outdir.mkdir(parents=True, exist_ok=True)
        calls = (outdir / "calls.jsonl").open("w")
    results, stop, done = list(prior), None, len(prior)

    def log(rec):
        rec["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        calls.write(json.dumps(rec) + "\n")
        calls.flush()

    if resume:
        log({"resume": {"from_loop": done + 1, "of": total_loops, "carried_usd": round(budget.total, 6),
                        "stops": RECAL_STOP, "approval": approval}})
    try:
        for i, (rep, q, m) in enumerate(order):
            if i < len(prior):
                continue
            loop = pilot.run_loop(client, m, q, tools, call_tool, budget, log, top_cache=TOP_CACHE, rep=rep)
            s = pilot.score(loop["final_text"], q)
            results.append({"qid": q["id"], "model": m, "rep": rep, "family": q["family"],
                            "difficulty": q["difficulty"], **{k: v for k, v in loop.items() if k != "final_text"},
                            "truncated": loop["stop_reason"] == "tool_use", **s})
            done += 1
            if done == max(1, int(total_loops * CHECKPOINT)):
                # project this run's own spend; spend carried in from other runs is added once, not scaled
                proj = carried + (budget.total - carried) / done * total_loops
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
    summary = {"mode": "baseline (no tools)" if baseline else "main", "approval": approval, "cap_usd": budget.cap,
               "resumed_from_loop": len(prior) + 1 if resume else None, "carried_usd": round(carried, 6),
               "stops_usd": {m: round(budget.overrun * budget.assumed[m], 6) for m in models},
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
    ap.add_argument("--approval", help="commit whose PLAN.md has Eleonora's e1-spend approval row (live runs)")
    ap.add_argument("--cap", type=float, default=CAP_USD,
                    help="spend cap for this invocation (the baseline gets $31 minus the main run's spend)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--resume", action="store_true", help="continue --out after its last completed loop (e1-resume)")
    a = ap.parse_args()
    if a.cap > CAP_USD:
        raise SystemExit(f"refusing: cap ${a.cap} is above Eleonora's ${CAP_USD}")
    approval = None
    if a.live:
        if not is_frozen():
            raise SystemExit("refusing: docs/decisions/e1-prereg.md is not frozen")
        bad = snapshot_ok()
        if bad:
            raise SystemExit(f"refusing: files differ from the recorded hashes: {bad}")
        if not a.approval:
            raise SystemExit("refusing: --live needs --approval COMMIT (her e1-spend row in PLAN.md)")
        approval = {"commit": git("rev-parse", a.approval).stdout.strip(), "row": check_spend_approval(a.approval, baseline=bool(a.baseline))}
    tools, call_tool = pilot.mcp_tools()
    date = datetime.now(timezone.utc).date().isoformat()
    tag = ("baseline-" if a.baseline else "") + ("" if a.live else "fake-")
    out = a.out or (HERE / f"run-{tag}{date}")
    client = pilot.live_client() if a.live else pilot.FakeClient()
    if a.resume and not a.out:
        raise SystemExit("refusing: --resume needs --out RUN_DIR")
    budget = pilot.Budget(cap=a.cap, assumed=dict(STOP_BASIS), min_loops=MIN_LOOPS)
    carried = e1_spend_so_far(exclude=out) if a.live else 0.0  # all E1 spend counts against the one $31 cap
    print(json.dumps(run(client, tools, call_tool, out, budget=budget, baseline=a.baseline, approval=approval,
                         resume=a.resume, carried=carried), indent=1))


if __name__ == "__main__":
    main()
