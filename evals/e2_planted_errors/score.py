#!/usr/bin/env python3
"""E2 scoring (PLAN E2; rules fixed in docs/decisions/e2-prereg.md, "Scoring").

    # 1. after the reviewers ran: match objections to planted errors by location; writes a sheet to judge
    uv run --project pipeline python evals/e2_planted_errors/score.py match RUN_DIR
    # 2. after a human filled `same_fix` (yes/no) in RUN_DIR/scoring.csv and `real_problem` in
    #    RUN_DIR/objections.csv: recall and false alarms with intervals; appends to results/
    uv run --project pipeline python evals/e2_planted_errors/score.py summarise RUN_DIR

Location match: an objection mentions the variant's name (doc-xxxxxxxx.md) and either cites a line within
±2 of the planted line, or quotes at least 20 characters of the planted text. Category ("same fix") is
judged by a human (CHOICE-7 (b)); the sheet shows the catalogue's `fix` next to the objection. The key's
SHA-256 is checked against key.sha256 first.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY_RE = re.compile(r"^### (R-\S+) · (\S+) · (.*)$", re.M)
DOC_RE = re.compile(r"(doc-[0-9a-f]{8})\.md(?::(\d+)(?:[-–](\d+))?)?")
TOL = 2
QUOTE = 20


def load_key(run: Path) -> dict:
    raw = (run / "key.json").read_bytes()
    want = (run / "key.sha256").read_text().split()[0]
    if hashlib.sha256(raw).hexdigest() != want:
        raise SystemExit("key.json does not match key.sha256: the key changed after it was committed")
    return json.loads(raw)


def parse_log(text: str) -> list[dict]:
    out = []
    heads = list(ENTRY_RE.finditer(text))
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        whole = m.group(3) + "\n" + body
        refs = [(d, int(a) if a else None, int(b) if b else (int(a) if a else None)) for d, a, b in DOC_RE.findall(whole)]
        sev = re.search(r"\*\*Severity:\*\*\s*(\w+)", body)
        out.append({"id": m.group(1), "agent": m.group(2), "target": m.group(3).strip(), "text": whole,
                    "refs": refs, "severity": sev.group(1).lower() if sev else ""})
    return out


def located(err: dict, doc: str, obj: dict) -> bool:
    stem = doc.removesuffix(".md")
    hits = [r for r in obj["refs"] if r[0] == stem]
    if not hits:
        return False
    if any(a is not None and a - TOL <= err["line"] <= b + TOL for _, a, b in hits):
        return True
    q = err["planted"].strip()
    return len(q) >= QUOTE and any(q[i:i + QUOTE] in obj["text"] for i in range(0, len(q) - QUOTE + 1, 5))


def match(run: Path) -> tuple[int, int]:
    key = load_key(run)
    objs = parse_log((run / "review-log.md").read_text(encoding="utf-8"))
    rows = []
    for v in key["variants"]:
        for j, e in enumerate(v["errors"]):
            hits = [o for o in objs if located(e, v["doc"], o)]
            rows.append({"error": f"{v['doc']}#{j}", "doc": v["doc"], "agent": e["agent"], "category": e["category"],
                         "line": e["line"], "planted": e["planted"][:160], "fix": e["fix"],
                         "objections": " ".join(o["id"] for o in hits),
                         "objection_text": " || ".join(re.sub(r"\s+", " ", o["text"])[:300] for o in hits),
                         "located": "yes" if hits else "no", "same_fix": "" if hits else "no"})
    with (run / "scoring.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["error"])
        w.writeheader()
        w.writerows(rows)
    controls = {v["doc"].removesuffix(".md") for v in key["variants"] if v["control"]}
    orows = [{"objection": o["id"], "agent": o["agent"], "severity": o["severity"],
              "control": "yes" if any(r[0] in controls for r in o["refs"]) else "no",
              "text": re.sub(r"\s+", " ", o["text"])[:300], "real_problem": ""} for o in objs]
    with (run / "objections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["objection", "agent", "severity", "control", "text", "real_problem"])
        w.writeheader()
        w.writerows(orows)
    return len(rows), sum(r["located"] == "yes" for r in rows)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cluster_bootstrap(rows: list[dict], reps: int = 2000, seed: int = 20261104) -> tuple[float, float]:
    docs: dict[str, list[int]] = {}
    for r in rows:
        docs.setdefault(r["doc"], []).append(1 if r["caught"] else 0)
    keys = sorted(docs)
    if not keys:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    stats = []
    for _ in range(reps):
        pick = [docs[rng.choice(keys)] for _ in keys]
        n = sum(len(x) for x in pick)
        stats.append(sum(map(sum, pick)) / n if n else float("nan"))
    stats.sort()
    return (stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1])


def summarise(run: Path) -> dict:
    key = load_key(run)
    rows = list(csv.DictReader((run / "scoring.csv").open(encoding="utf-8")))
    todo = [r["error"] for r in rows if r["located"] == "yes" and r["same_fix"].strip().lower() not in ("yes", "no")]
    if todo:
        raise SystemExit(f"{len(todo)} located errors still need a same_fix yes/no in scoring.csv")
    for r in rows:
        r["caught"] = r["located"] == "yes" and r["same_fix"].strip().lower() == "yes"
    res: dict = {"run": run.name, "seed": key["seed"], "rehearsal": key["rehearsal"],
                 "source_commit": key.get("source_commit"), "scored_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "by_agent": {}, "by_category": {}}
    for agent in sorted({r["agent"] for r in rows}):
        sub = [r for r in rows if r["agent"] == agent]
        k = sum(r["caught"] for r in sub)
        res["by_agent"][agent] = {"caught": k, "planted": len(sub), "recall": k / len(sub),
                                  "wilson95": wilson(k, len(sub)), "cluster_bootstrap95": cluster_bootstrap(sub)}
    for cat in sorted({r["category"] for r in rows}):
        sub = [r for r in rows if r["category"] == cat]
        k = sum(r["caught"] for r in sub)
        res["by_category"][cat] = {"caught": k, "planted": len(sub)}
    objs = list(csv.DictReader((run / "objections.csv").open(encoding="utf-8")))
    ctrl = [o for o in objs if o["control"] == "yes" and o["severity"] in ("blocker", "major")]
    if any(o["real_problem"].strip().lower() not in ("yes", "no") for o in ctrl):
        raise SystemExit("objections.csv: every blocker/major objection on a control needs real_problem yes/no")
    fa = sum(o["real_problem"].strip().lower() == "no" for o in ctrl)
    res["false_alarms"] = {"false": fa, "objections_on_controls": len(ctrl), "wilson95": wilson(fa, len(ctrl))}
    res["misses"] = [r["error"] for r in rows if not r["caught"]]
    if key["rehearsal"]:  # a dry run before the freeze is never a result
        (run / "rehearsal_summary.json").write_text(json.dumps(res, indent=1) + "\n")
        return res
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    with (out / "results.jsonl").open("a", encoding="utf-8") as f:  # appended, never overwritten (PLAN E3)
        f.write(json.dumps(res) + "\n")
    return res


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "match":
        n, loc = match(Path(argv[2]))
        print(f"{n} planted errors, {loc} located; fill same_fix in scoring.csv and real_problem in objections.csv")
        return 0
    if len(argv) == 3 and argv[1] == "summarise":
        print(json.dumps(summarise(Path(argv[2])), indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
