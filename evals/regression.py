"""E3 regression suite (PLAN E3): one command to see whether the evals need rerunning and to chart them.

    uv run --project pipeline python evals/regression.py status   # what changed since each eval's last run
    uv run --project pipeline python evals/regression.py chart    # results over time via chart-from-sql

An eval needs rerunning when anything it measures has changed: the reviewer prompts (.claude/agents/*.md),
their model tier (agent frontmatter), the error catalogue or the planting and scoring code. `status` hashes
those inputs into a fingerprint and compares it with the fingerprint stored on the eval's last result line
(results.jsonl, appended only). E1 (question-to-SQL) is not built yet: it needs Eleonora's cost approval run,
so it is reported as NOT BUILT, never as passing. E2 runs need the frozen pre-registration and a human scoring
pass, so `status` says what to run; it does not start reviewers itself.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = {
    "E2": {
        "results": ROOT / "evals" / "e2_planted_errors" / "results" / "results.jsonl",
        "inputs": [".claude/agents/skeptic.md", ".claude/agents/quant-reviewer.md",
                   "evals/e2_planted_errors/catalogue.yaml", "evals/e2_planted_errors/plant.py",
                   "evals/e2_planted_errors/score.py", "docs/decisions/e2-prereg.md"],
        "run": "see evals/e2_planted_errors/README.md (plant -> reviewers -> score.py match -> human -> summarise)",
    },
    "E1": {"results": ROOT / "evals" / "e1_sql_benchmark" / "results.jsonl",
           "inputs": [".claude/agents/analyst.md", "docs/decisions/e1-prereg.md",
                      "evals/e1_sql_benchmark/questions.yaml", "evals/e1_sql_benchmark/gold.json",
                      "evals/e1_sql_benchmark/run_e1.py", "evals/e1_sql_benchmark/verify.py",
                      "evals/e1_sql_benchmark/spec.py", "evals/e1_sql_benchmark/analyze_e1.py"],
           "run": "see evals/e1_sql_benchmark/RESULTS.md (run_e1.py needs an e1-spend approval and ANTHROPIC_API_KEY)"},
}


def fingerprint(inputs: list[str], root: Path = ROOT) -> dict:
    parts = {}
    for rel in inputs:
        p = root / rel
        parts[rel] = hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "missing"
    models = {}
    for rel in inputs:
        if rel.startswith(".claude/agents/") and (root / rel).exists():
            m = re.search(r"^model:\s*(\S+)", (root / rel).read_text(), re.M)
            models[Path(rel).stem] = m.group(1) if m else "inherit"
    digest = hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]
    return {"digest": digest, "files": parts, "models": models}


def last_result(path: Path) -> dict | None:
    if not path.exists():
        return None
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else None


def status(root: Path = ROOT) -> list[dict]:
    out = []
    for name, ev in EVALS.items():
        if not ev["inputs"]:
            out.append({"eval": name, "state": "NOT BUILT", "why": ev["run"]})
            continue
        fp = fingerprint(ev["inputs"], root)
        last = last_result(ev["results"])
        if last is None:
            state, why = "NEVER RUN", ev["run"]
        elif not last.get("fingerprint"):
            state = "RUN, UNFINGERPRINTED"
            why = (f"last run {last.get('scored_at')} ({last.get('run')}) predates input fingerprinting; "
                   "the next run records one")
        elif last.get("fingerprint", {}).get("digest") != fp["digest"]:
            old = last.get("fingerprint", {}).get("files", {})
            changed = [f for f, h in fp["files"].items() if old.get(f) != h]
            state, why = "RERUN NEEDED", "changed since last run: " + ", ".join(changed)
        else:
            state, why = "UP TO DATE", f"last run {last.get('scored_at')}"
        out.append({"eval": name, "state": state, "why": why, "fingerprint": fp})
    return out


def chart(root: Path = ROOT) -> str:
    rows = []
    path = EVALS["E2"]["results"]
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                for agent, v in r.get("by_agent", {}).items():
                    lo, hi = v.get("cluster_bootstrap95") or v.get("wilson95")
                    rows.append({"scored_at": r["scored_at"][:10], "agent": agent, "recall": v["recall"], "lo": lo, "hi": hi})
    if not rows:
        return "no E2 results yet: nothing to chart (results are appended by score.py summarise after a real run)"
    out_dir = root / "evals" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "e2_recall_over_time.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # chart-from-sql needs matplotlib, which is not in the pipeline env: added per run, as its SKILL.md says.
    cmd = ["uv", "run", "-q", "--project", str(root / "pipeline"), "--with", "matplotlib", "python",
           str(root / ".claude/skills/chart-from-sql/scripts/chart.py"), "--file", str(csv_path),
           "--kind", "line", "--x", "scored_at", "--y", "recall", "--group", "agent", "--as-percent",
           "--ylabel", "Recall, % of planted errors caught", "--title", "E2: reviewer recall over time",
           "--source", "evals/e2_planted_errors/results/results.jsonl", "--vintage", rows[-1]["scored_at"],
           "--out", str(out_dir / "e2_recall_over_time")]
    subprocess.run(cmd, check=True)
    return f"wrote {out_dir / 'e2_recall_over_time'}.png/.svg"


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "status":
        for s in status():
            print(f"{s['eval']}: {s['state']}: {s['why']}")
        return 0
    if len(argv) == 2 and argv[1] == "chart":
        print(chart())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
