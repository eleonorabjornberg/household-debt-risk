#!/usr/bin/env python3
"""Gate for a research memo (PLAN D3). Read-only.

    uv run --project pipeline python .claude/skills/research-memo/scripts/memo_check.py MEMO.md [--max-words 1000] [--json]

A memo passes only if:
  1. it starts with the "Claude draft" banner (CLAUDE.md authorship rule) and names its audience
     ("**Audience:** ...") within the first 8 lines;
  2. it has the sections Bottom line, What the data show, What it means for you, Caveats, What to watch,
     Sources;
  3. the body (everything before "## Sources") has at most --max-words words (two pages ≈ 1,000);
  4. every number in the body passes claim-check: MATCH, or AMBIGUOUS where exactly one candidate row is
     listed in the Sources section; UNTRACED, MISMATCH and NOT RECOMPUTABLE fail; so does a row marked
     STALE. A row marked ESTIMATE must have the word "estimate" on the line that prints it;
  5. every claim id in the Sources section exists in the register, and every row a body number resolved
     to is listed there, so a reader can trace each number.
Exit 0 pass, 1 fail, 2 usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CLAIM_CHECK = ROOT / ".claude" / "skills" / "claim-check" / "scripts" / "claim_check.py"
SECTIONS = ["Bottom line", "What the data show", "What it means for you", "Caveats", "What to watch", "Sources"]
ID_RE = re.compile(r"`([a-z0-9_]+)`")


def register_ids(root: Path) -> dict[str, dict]:
    rows = {}
    files = [root / "claims" / "register.csv", *sorted((root / "claims" / "tracks").glob("*.csv"))]
    for f in files:
        if f.exists():
            for r in csv.DictReader(f.open(encoding="utf-8")):
                rows[r["claim_id"]] = r
    return rows


def run_claim_check(path: Path, root: Path) -> dict:
    p = subprocess.run([sys.executable, str(CLAIM_CHECK), "--file", str(path), "--json"],
                       capture_output=True, text=True, cwd=root)
    if p.returncode == 2 or not p.stdout.strip():
        raise SystemExit(f"claim-check failed: {p.stderr.strip()[:400]}")
    return json.loads(p.stdout)


def check(path: Path, max_words: int, root: Path = ROOT, cc: dict | None = None) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []

    head = "\n".join(lines[:8])
    if "claude draft" not in head.lower():
        errors.append('no "Claude draft" banner in the first 8 lines')
    if not re.search(r"\*\*Audience:\*\*\s*\S", head):
        errors.append('no "**Audience:** ..." line in the first 8 lines')
    for s in SECTIONS:
        if not re.search(rf"^##\s+{re.escape(s)}\b", text, re.M):
            errors.append(f'missing section "## {s}"')

    m = re.search(r"^##\s+Sources\b", text, re.M)
    body, sources = (text[: m.start()], text[m.start():]) if m else (text, "")
    body_start_line, sources_line = 1, (text[: m.start()].count("\n") + 1 if m else len(lines) + 1)
    words = len(re.findall(r"\b[\w$%.,−+-]+\b", re.sub(r"^#.*$", "", body, flags=re.M)))
    if words > max_words:
        errors.append(f"body is {words} words, over the {max_words}-word limit (two pages)")

    reg = register_ids(root)
    listed = set(ID_RE.findall(sources))
    for cid in sorted(listed - set(reg)):
        errors.append(f"Sources lists `{cid}`, which is not a register row")

    cc = cc if cc is not None else run_claim_check(path, root)
    used: set[str] = set()
    for it in cc["items"]:
        if not (body_start_line <= it["line"] < sources_line):
            continue
        tok, v, rows = it["token"], it["verdict"], it.get("rows", [])
        ids = [r["claim_id"] for r in rows]
        where = f'line {it["line"]} "{tok}"'
        if v == "AMBIGUOUS":
            pick = [i for i in ids if i in listed]
            if len(pick) == 1:
                ids, v = pick, "MATCH" if next(r for r in rows if r["claim_id"] == pick[0]).get("verdict", "MATCH") == "MATCH" else "MISMATCH"
            else:
                errors.append(f"{where}: AMBIGUOUS between {', '.join(ids)}; list exactly one of them in Sources")
                continue
        if v != "MATCH":
            errors.append(f"{where}: claim-check {v}" + (f" ({', '.join(ids)})" if ids else ""))
            continue
        for cid in ids:
            used.add(cid)
            status = reg.get(cid, {}).get("validation", "")
            if status == "STALE":
                errors.append(f"{where}: register row `{cid}` is STALE; do not publish it")
            if status == "ESTIMATE" and "estimate" not in lines[it["line"] - 1].lower():
                errors.append(f'{where}: `{cid}` is an ESTIMATE; say "estimate" where it is printed')
    for cid in sorted(used - listed):
        errors.append(f"body uses `{cid}` but Sources does not list it")
    for cid in sorted(listed - used):
        if cid in reg:
            warnings.append(f"Sources lists `{cid}`, which no body number resolved to")

    summary = {k: v for k, v in cc["summary"].items()}
    return {"memo": str(path), "words": words, "max_words": max_words, "claim_check": summary,
            "rows_used": sorted(used), "errors": errors, "warnings": warnings, "pass": not errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("memo", type=Path)
    ap.add_argument("--max-words", type=int, default=1000)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.memo.is_file():
        print(f"{a.memo}: not a file")
        return 2
    r = check(a.memo.resolve(), a.max_words)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['memo']}: {'PASS' if r['pass'] else 'FAIL'} · {r['words']}/{r['max_words']} words · "
              f"claim-check {r['claim_check']} · {len(r['rows_used'])} register rows")
        for e in r["errors"]:
            print(f"  ERROR {e}")
        for w in r["warnings"]:
            print(f"  warn  {w}")
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
