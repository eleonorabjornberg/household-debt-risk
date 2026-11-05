#!/usr/bin/env python3
"""E1 full set: verify every gold answer two ways (no model) and draw the E3 holdout.

    uv run --project pipeline python evals/e1_sql_benchmark/verify_set.py

Path 1: each question's check evaluated on the snapshot the MCP server serves (spec.load_snapshot).
Path 2: its claims/register.csv or claims/tracks/infra.csv row, which must be validation PASS (its check
recomputes the value from the raw sources; validation/e1_gold.py, or A1/A2/C4 for pre-existing rows).
The two must agree to the register value's written precision, and the quarter must match where asked.
Unanswerable questions have gold "refuse".

Holdout (CHOICE-E1-13 (b)): 20 of the 100 questions, drawn with random.Random(20261104) (CHOICE-E1-10 (a)),
stratified by family in proportion (PS/HB/CW/CC/NY/UN 3 each, RG 2), uniformly within a family. Held-out
questions are not run in E1; they are first run at the first E3 rerun.

Writes gold.json. Exits 1 on any disagreement.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import spec  # noqa: E402

SEED = 20261104
HOLDOUT_PER_FAMILY = {"PS": 3, "HB": 3, "CW": 3, "CC": 3, "NY": 3, "RG": 2, "UN": 3}
REGISTERS = [ROOT / "claims" / "register.csv", ROOT / "claims" / "tracks" / "infra.csv"]


def precision(value: str) -> float:
    exp = Decimal(value).as_tuple().exponent
    return 0.5 * 10 ** exp if exp < 0 else 0.5


def holdout(questions: list[dict], seed: int = SEED) -> set[str]:
    rng = random.Random(seed)
    out = set()
    for fam, k in HOLDOUT_PER_FAMILY.items():
        ids = sorted(q["id"] for q in questions if q["family"] == fam)
        out |= set(rng.sample(ids, k))
    return out


def verify(qfile: Path = HERE / "questions.yaml", registers=REGISTERS, snap=None) -> list[dict]:
    qs = yaml.safe_load(qfile.read_text())["questions"]
    reg = {}
    for p in registers:
        if p.exists():
            reg.update({r["claim_id"]: r for r in csv.DictReader(p.open())})
    snap = snap or spec.load_snapshot()
    held = holdout(qs)
    out = []
    for q in qs:
        rec = {"id": q["id"], "family": q["family"], "difficulty": q["difficulty"], "question": q["question"],
               "holdout": q["id"] in held}
        if q.get("refuse"):
            out.append({**rec, "gold": "refuse", "reason": q["reason"], "ok": True, "problems": []})
            continue
        problems = []
        val, qtr = spec.evaluate(q["check"], snap)
        if q.get("quarter") and not qtr:
            problems.append("question asks for a quarter but the check gives none")
        rid = q.get("register") or f"e1_{q['id']}"
        r = reg.get(rid)
        if r is None:
            problems.append(f"no register row {rid}")
        else:
            if r["validation"] != "PASS":
                problems.append(f"register {rid} is {r['validation']}, not PASS")
            tol = precision(r["value"])
            if abs(val - float(r["value"])) > tol + 1e-12:
                problems.append(f"snapshot {val!r} vs register {r['value']} (precision {tol:g})")
        out.append({**rec, "unit": q["unit"], "tolerance": q["tolerance"], "gold": val,
                    "quarter": qtr if q.get("quarter") else None, "register": rid,
                    "register_value": r["value"] if r else None, "check_id": r["check_id"] if r else None,
                    "ok": not problems, "problems": problems})
    return out


def main() -> int:
    res = verify()
    (HERE / "gold.json").write_text(json.dumps({"seed": SEED, "holdout_per_family": HOLDOUT_PER_FAMILY,
                                                "questions": res}, indent=1) + "\n")
    bad = [r for r in res if not r["ok"]]
    for r in bad:
        print(r["id"], "; ".join(r["problems"]))
    n_ans = sum(r["gold"] != "refuse" for r in res)
    held = sum(r["holdout"] for r in res)
    print(f"{len(res) - len(bad)}/{len(res)} verified ({n_ans} answerable, {len(res) - n_ans} refusals); "
          f"holdout {held}, scored in E1 {len(res) - held}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
