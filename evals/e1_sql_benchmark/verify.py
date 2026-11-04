#!/usr/bin/env python3
"""E1: verify the pilot questions' gold answers without any model (two independent paths).

    uv run --project pipeline python evals/e1_sql_benchmark/verify.py

For each question in pilot_questions.yaml: recompute the answer from the snapshot JSON the MCP server serves,
compare it with the claims/register.csv row (which must be validation PASS) to the register's precision, and
check the quarter where one is asked. Writes pilot_gold.json (gold = the snapshot value, plus the register
value, vintage and quarter). Exits 1 on any disagreement. No network, no API.
"""
from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SNAP = ROOT / "web" / "public" / "data"
REGISTER = ROOT / "claims" / "register.csv"


def quarter(date: str) -> str:
    y, m = int(date[:4]), int(date[5:7])
    return f"{y}Q{(m - 1) // 3 + 1}"


def recompute(check: dict, snap: Path = SNAP) -> tuple[float, str | None]:
    """Return (value, quarter or None) for a check spec."""
    rows = json.loads((snap / f"{check['table']}.json").read_text())
    f, scale, op = check["field"], check.get("scale", 1.0), check.get("op", "at")
    if op == "at":
        (r,) = [r for r in rows if r["date"] == check["date"]]
        return r[f] * scale, None
    if op == "argmax":
        r = max(rows, key=lambda r: r[f])
        return r[f] * scale, quarter(r["date"])
    if op == "argmin_after":
        r = min((r for r in rows if r["date"] > check["after"]), key=lambda r: r[f])
        return r[f] * scale, quarter(r["date"])
    if op == "diff_pp":
        by = {r["date"]: r[f] for r in rows}
        return (by[check["to"]] - by[check["from"]]) * 100, None
    raise ValueError(f"unknown op {op}")


def precision(value: str) -> float:
    """Half a unit in the last place of the register value as written (0.5638 -> 0.00005)."""
    exp = Decimal(value).as_tuple().exponent
    return 0.5 * 10 ** exp


def verify(qpath: Path = HERE / "pilot_questions.yaml", register: Path = REGISTER, snap: Path = SNAP) -> list[dict]:
    reg = {r["claim_id"]: r for r in csv.DictReader(register.open())}
    vintage = json.loads((snap / "meta.json").read_text()).get("vintages", {})
    out = []
    for q in yaml.safe_load(qpath.read_text())["questions"]:
        r = reg[q["register"]]
        val, qtr = recompute(q["check"], snap)
        problems = []
        if r["validation"] != "PASS":
            problems.append(f"register row {q['register']} is {r['validation']}, not PASS")
        if abs(val - float(r["value"])) > precision(r["value"]) + 1e-12:
            problems.append(f"snapshot {val:.6g} vs register {r['value']}")
        if "quarter" in q and qtr != q["quarter"]:
            problems.append(f"quarter {qtr} vs expected {q['quarter']}")
        if "quarter" in q and q["quarter"] != r["period"] and q["quarter"] not in r["claim"]:
            problems.append(f"register row does not name {q['quarter']}")
        out.append({"id": q["id"], "question": q["question"], "gold": val, "unit": q["unit"],
                    "tolerance": q["tolerance"], "quarter": q.get("quarter"), "register": q["register"],
                    "register_value": r["value"], "vintage_z1": vintage.get("z1"), "ok": not problems,
                    "problems": problems})
    return out


def main() -> int:
    res = verify()
    for r in res:
        print(f"{r['id']}  {'OK ' if r['ok'] else 'BAD'}  gold {r['gold']:.6g} {r['unit']}"
              f"{' ' + r['quarter'] if r['quarter'] else ''}  register {r['register_value']}"
              + ("" if r["ok"] else "  " + "; ".join(r["problems"])))
    (HERE / "pilot_gold.json").write_text(json.dumps(res, indent=1) + "\n")
    bad = sum(not r["ok"] for r in res)
    print(f"{len(res) - bad}/{len(res)} verified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
