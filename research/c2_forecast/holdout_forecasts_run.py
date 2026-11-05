#!/usr/bin/env python3
"""Second, separately gated opening of the C2 holdout: writes only the per-forecast table (card c3-errors (b)).

Eleonora approved one second run of the frozen C2 holdout step. It writes the individual holdout forecasts that the
one joint run (a0d9151) did not save, so that C3 can publish the ten largest holdout errors and the origin-based subset
(cards c3-errors (b), c3-hcount (b); PLAN.md "Decisions taken", 2026-11-05, recorded at ccc1fc6). The dated
deviation is docs/decisions/scoring-protocol-deviations-2026-11-05.md, committed before this script ever runs.

    uv run --project pipeline python research/c2_forecast/holdout_forecasts_run.py --prereg 192d60c --approval ccc1fc6

Gates, all checked before any holdout data is read:
  * --prereg must be the frozen protocol commit (forecast.FROZEN);
  * --approval must be a commit whose PLAN.md has an Eleonora row naming c3-errors and a "second" run, that commit
    must come after the last change to FREEZE.json and be an ancestor of HEAD (holdout_run.check_order);
  * the working tree is clean, and every frozen file matches FREEZE.json (holdout_run.check_freeze);
  * run once: refuses if either output exists, or if any commit has ever touched either output path.

The forecasts come from the frozen code paths only (forecast.backtest_latest, forecast.add_intervals, the same split as
holdout_run.c2_holdout). As a check, the frozen holdout_run.c2_holdout is recomputed in memory and must reproduce the
committed c2 block of holdout_results.json exactly, and the table must reproduce the committed holdout scores. Those
recomputed scores and verdicts are compared, never written. If any check fails, nothing is written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "holdout_forecasts.csv"
RECORD = HERE / "holdout_forecasts_run.json"
COMMITTED = HERE / "holdout_results.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check_approval(commit: str) -> str:
    plan = subprocess.run(["git", "show", f"{commit}:PLAN.md"], cwd=ROOT, capture_output=True, text=True)
    if plan.returncode != 0:
        raise SystemExit(f"cannot read PLAN.md at {commit}")
    rows = [l for l in plan.stdout.splitlines() if l.startswith("| 20") and "c3-errors" in l and "second" in l.lower()
            and "| Eleonora" in l]
    if not rows:
        raise SystemExit(f"no Eleonora decision row approving the second (c3-errors) run in PLAN.md at {commit}")
    return rows[-1]


def check_once() -> None:
    for p in (OUT, RECORD):
        if p.exists():
            raise SystemExit(f"{p.relative_to(ROOT)} exists: this run is allowed once only")
        hist = subprocess.run(["git", "log", "--all", "--format=%h", "--", str(p.relative_to(ROOT))], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
        if hist:
            raise SystemExit(f"{p.relative_to(ROOT)} was committed before ({hist.split()[0]}): run once only")


def gates(a) -> tuple:
    hr = _load("c2holdout", HERE / "holdout_run.py")
    fc = hr.fc
    if a.prereg != fc.FROZEN:
        raise SystemExit(f"--prereg {fc.FROZEN} required")
    if not a.approval:
        raise SystemExit("--approval <commit with Eleonora's c3-errors decision in PLAN.md> required")
    row = check_approval(a.approval)
    hr.check_order(a.approval)
    hr.clean_tree()
    check_once()
    fz = hr.check_freeze()
    return hr, fc, row, fz


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prereg")
    ap.add_argument("--approval")
    a = ap.parse_args(argv)
    hr, fc, row, fz = gates(a)                     # every gate before any holdout data is read
    import pandas as pd

    share = fc.load_latest(holdout=True, prereg=a.prereg)
    cal = pd.read_csv(fc.C1 / "z1_calendar.csv")
    bridge = fc.Bridge()
    tests_dev = pd.read_csv(HERE / "tests_dev.csv")
    committed = json.loads(COMMITTED.read_text())

    # Check 1: the frozen holdout step, recomputed in memory, reproduces the committed results exactly (not written).
    again = json.loads(json.dumps(hr.clean(hr.c2_holdout(share, fc.DEV_END, tests_dev, cal, bridge)), allow_nan=False))
    if again != committed["c2"]:
        diff = sorted(k for k in committed["c2"] if again.get(k) != committed["c2"][k])
        raise SystemExit(f"STOP: the recomputed holdout step does not reproduce holdout_results.json (keys: {diff}); "
                         "nothing written")

    # The per-forecast table, by the same frozen steps and split as holdout_run.c2_holdout.
    df = pd.concat([fc.backtest_latest(share, w, bridge if w == "expanding" else None, cal) for w in ("expanding", "rolling")],
                   ignore_index=True)
    df = fc.add_intervals(df, [m for m in list(fc.CANDIDATES) + list(fc.BENCH) if m != "ZC1-DIR"])
    Tq = df["T"].map(lambda x: pd.Period(x, "Q"))
    hold = df[Tq + df["h"] > fc.DEV_END].reset_index(drop=True)

    # Check 2: the table reproduces the committed holdout scores (same scoring calls as holdout_run.c2_holdout).
    zmods = ["Z-DIR", "Z-DAMP", "no_change", "drift", "ar_bic", "seasonal_naive"]
    sc = pd.concat([fc.scores(hold, zmods, "Z family, holdout"),
                    fc.scores(hold[hold["ZC1-DIR"].notna()], ["ZC1-DIR", "Z-DIR", "no_change", "ar_bic"], "Z+C1 holdout")],
                   ignore_index=True)
    if json.loads(json.dumps(hr.clean(sc.to_dict(orient="records")), allow_nan=False)) != committed["c2"]["scores_holdout"]:
        raise SystemExit("STOP: the per-forecast table does not reproduce the committed holdout scores; nothing written")

    hold.to_csv(OUT, index=False)
    rec = {"mode": "SECOND HOLDOUT OPENING (per-forecast table only; card c3-errors (b))",
           "approval_commit": a.approval, "approval_row": row, "freeze": fz,
           "deviation": "docs/decisions/scoring-protocol-deviations-2026-11-05.md",
           "checks": {"c2_block_reproduced_exactly": True, "table_reproduces_scores_holdout": True},
           "rows": int(len(hold)), "output": str(OUT.relative_to(ROOT)),
           "output_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}
    RECORD.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"{len(hold)} holdout forecasts written to {OUT.relative_to(ROOT)}; both checks passed. Commit as one "
          "commit; do not rerun.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
