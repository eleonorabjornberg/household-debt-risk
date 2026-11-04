#!/usr/bin/env python3
"""List claims-register rows a memo can use (PLAN D3). Read-only.

    uv run --project pipeline python .claude/skills/research-memo/scripts/facts.py [WORD ...] [--all]

Prints id, display spellings, period, validation status, vintage and the claim, for rows whose claim,
id or notes contain every WORD (case-insensitive). STALE rows are hidden unless --all.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def rows(root: Path = ROOT):
    for f in [root / "claims" / "register.csv", *sorted((root / "claims" / "tracks").glob("*.csv"))]:
        if f.exists():
            yield from csv.DictReader(f.open(encoding="utf-8"))


def main(argv: list[str]) -> int:
    show_all = "--all" in argv
    words = [w.lower() for w in argv if w != "--all"]
    n = 0
    for r in rows():
        if r["validation"] == "STALE" and not show_all:
            continue
        hay = f"{r['claim_id']} {r['claim']} {r['notes']}".lower()
        if all(w in hay for w in words):
            n += 1
            print(f"{r['claim_id']} | {r['display']} | {r['period']} | {r['validation']} | {r['vintage']}\n    {r['claim']}")
    print(f"-- {n} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
