"""Compare regenerated outputs with the committed ones (PLAN F2: fresh clone + `make all` reproduces
the published numbers).

    python tools/repro_check.py [--ref HEAD] [--rtol 1e-9]

For every tracked results file (validation, analysis, research/*, web/public/data/*.json) it loads the
committed version (`git show <ref>:<path>`) and the working-tree version and compares them value by
value. Run-time metadata (timestamps, run times, local paths) is ignored. Exit 1 if any published value
differs. Reports; never edits anything.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ["validation/results.json", "analysis/results.json"]
GLOBS = ["research/*/results.json", "web/public/data/*.json"]
# Keys that change on every run or every machine, not published numbers.
VOLATILE = {"run_at", "generated_at", "prev_path", "previous_vintage_urls_tried", "snapshot_source"}


def tracked(ref: str) -> list[str]:
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref], cwd=ROOT, capture_output=True, text=True, check=True)
    names = set(out.stdout.split())
    paths = [f for f in FILES if f in names]
    for g in GLOBS:
        paths += sorted(str(p.relative_to(ROOT)) for p in ROOT.glob(g) if str(p.relative_to(ROOT)) in names)
    return paths


def not_run(x) -> bool:
    return isinstance(x, dict) and x.get("status") == "NOT RUN"


def diff(a, b, path: str, rtol: float, out: list[str]) -> None:
    # A validation check that did not run (no database, no previous vintage reachable) has no result
    # to reproduce; its note only says why, which depends on the machine.
    if not_run(a) and not_run(b):
        return
    if isinstance(a, str) and isinstance(b, str) and path.endswith(".note") and (a.startswith("URLs tried") or b.startswith("URLs tried") or not a or not b):
        return
    # The NY Fed vintage is the retrieval date (the HHDC file carries no release stamp), so it moves on
    # every download even when nyfed_by_type.json, compared separately, is identical.
    if path == ".vintages.nyfed":
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in VOLATILE:
                continue
            if k not in a or k not in b:
                out.append(f"{path}.{k}: {'added' if k not in a else 'missing'}")
            else:
                diff(a[k], b[k], f"{path}.{k}", rtol, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} -> {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", rtol, out)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if not math.isclose(a, b, rel_tol=rtol, abs_tol=1e-12):
            out.append(f"{path}: {a} -> {b}")
    elif a != b:
        out.append(f"{path}: {a!r} -> {b!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--rtol", type=float, default=1e-9)
    args = ap.parse_args(argv)
    bad = 0
    for p in tracked(args.ref):
        committed = json.loads(subprocess.run(["git", "show", f"{args.ref}:{p}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
        current = json.loads((ROOT / p).read_text())
        out: list[str] = []
        diff(committed, current, "", args.rtol, out)
        print(f"{'OK  ' if not out else 'DIFF'} {p}" + (f" ({len(out)} values)" if out else ""))
        for line in out[:15]:
            print(f"     {line}")
        bad += bool(out)
    print("reproduced: every committed result matches" if not bad else f"NOT reproduced: {bad} file(s) differ (a new source vintage also shows up here)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
