#!/usr/bin/env python3
"""Joint C1 + C2 holdout run (Q-C1c, decided by Eleonora 2026-11-04: one run, after C2 is frozen).

SEALED. The real run needs, all of them:
    --prereg 192d60c                 the frozen C2 protocol commit
    --approval <commit>              a commit whose PLAN.md "Decisions taken" has an Eleonora row that says
                                     "unseal" and "holdout" (e.g. "Unseal the joint C1+C2 holdout and run it once")
and a clean working tree whose frozen files match FREEZE.json. It writes holdout_results.json and one commit.

Dry run (no holdout data read): pretends the holdout is 2019Q3-2023Q2, inside the development sample, and runs
every step of the holdout code on that split. Output goes to data/holdout_dryrun/ (not committed):
    uv run --project pipeline python research/c2_forecast/holdout_run.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "FREEZE.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fc = _load("c2forecast", HERE / "forecast.py")
nc = fc.nc


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze() -> dict:
    fz = json.loads(FREEZE.read_text())
    bad = {p: (h, sha(ROOT / p)) for p, h in fz["files"].items() if sha(ROOT / p) != h}
    if bad:
        raise SystemExit(f"frozen files changed since the freeze: {sorted(bad)}")
    return fz


def check_approval(commit: str) -> str:
    plan = subprocess.run(["git", "show", f"{commit}:PLAN.md"], cwd=ROOT, capture_output=True, text=True)
    if plan.returncode != 0:
        raise SystemExit(f"cannot read PLAN.md at {commit}")
    # The row must say "unseal" explicitly: decisions about *how* the holdout runs (e.g. Q-C1c) are not a go.
    rows = [l for l in plan.stdout.splitlines() if l.startswith("| 20") and "holdout" in l.lower()
            and "unseal" in l.lower() and "| Eleonora" in l]
    if not rows:
        raise SystemExit(f"no Eleonora decision row approving the holdout run in PLAN.md at {commit}")
    return rows[-1]


def check_order(approval: str) -> None:
    """Deviation c1b-dev-1 (mkt-q29): the approval commit must come after the last commit that touched FREEZE.json
    (so an approval given before a re-freeze cannot open the holdout) and be an ancestor of HEAD, as C1b checks."""
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    fz = git("log", "-1", "--format=%H", "--", str(FREEZE.relative_to(ROOT))).stdout.strip()
    ap = git("rev-parse", "--verify", f"{approval}^{{commit}}").stdout.strip()
    if not fz or not ap:
        raise SystemExit("cannot resolve the freeze commit or the approval commit")
    if ap == fz or git("merge-base", "--is-ancestor", fz, ap).returncode != 0:
        raise SystemExit("the approval commit must come after the last commit that changed C2's FREEZE.json")
    if git("merge-base", "--is-ancestor", ap, "HEAD").returncode != 0:
        raise SystemExit("the approval commit is not an ancestor of HEAD")


def clean_tree() -> None:
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if st.strip():
        raise SystemExit("working tree not clean: the holdout run must be one clean commit")


# ------------------------------------------------------------------ C2
def c2_holdout(share: pd.DataFrame, dev_end: pd.Period, tests_dev: pd.DataFrame | None, cal, bridge) -> dict:
    """Run the frozen C2 candidates and benchmarks on all origins; score rows with T+h > dev_end (descriptive)."""
    df = pd.concat([fc.backtest_latest(share, w, bridge if w == "expanding" else None, cal) for w in ("expanding", "rolling")],
                   ignore_index=True)
    models = list(fc.CANDIDATES) + list(fc.BENCH)
    df = fc.add_intervals(df, [m for m in models if m != "ZC1-DIR"])
    Tq = df["T"].map(lambda x: pd.Period(x, "Q"))
    dev, hold = df[Tq + df["h"] <= dev_end], df[Tq + df["h"] > dev_end]
    if tests_dev is None:      # dry run: development tests on the pretend development sample
        seas = fc.seasonality_check(share[share.index <= dev_end])
        tests_dev = fc.tests(dev, seasonal=seas["seasonal"])
    zmods = ["Z-DIR", "Z-DAMP", "no_change", "drift", "ar_bic", "seasonal_naive"]
    sc_h = pd.concat([fc.scores(hold, zmods, "Z family, holdout"),
                      fc.scores(hold[hold["ZC1-DIR"].notna()], ["ZC1-DIR", "Z-DIR", "no_change", "ar_bic"], "Z+C1 holdout")],
                     ignore_index=True)
    sc_d = fc.scores(dev, zmods, "Z family, development")
    cov = fc.coverage(hold, zmods)
    verdicts = []
    for _, t in tests_dev.iterrows():
        g = hold[(hold.design == t.design) & (hold.h == t.h)].dropna(subset=[t.candidate, t.benchmark, "actual"])
        if g.empty:
            verdicts.append({**t.to_dict(), "n_holdout": 0, "verdict": "absent (no holdout forecasts)"})
            continue
        lc = float(((g[t.candidate] - g.actual) ** 2).mean())
        lb = float(((g[t.benchmark] - g.actual) ** 2).mean())
        dev_ok = bool(t.p_holm < 0.05 and t.candidate_lower_rmse)
        hold_lower = lc < lb
        # Protocol wording: "beats" = rule (a); "does not beat" = benchmark lower in either sample; else "comparable"
        if dev_ok and hold_lower:
            v = "beats"
        elif (not t.candidate_lower_rmse) or (not hold_lower):
            v = "does not beat"
        else:
            v = "comparable"
        verdicts.append({**t.to_dict(), "n_holdout": len(g), "holdout_rel_rmse": float(np.sqrt(lc / lb)),
                         "holdout_candidate_lower": hold_lower, "verdict": v})
    return {"scores_holdout": sc_h.to_dict(orient="records"), "scores_dev": sc_d.to_dict(orient="records"),
            "coverage_holdout": cov.to_dict(orient="records"), "verdicts": verdicts,
            "n_holdout": hold.groupby(["design", "h"]).size().rename("n").reset_index().to_dict(orient="records")}


# ------------------------------------------------------------------ C1
def c1_holdout(dev_end: str, read_holdout: bool) -> dict:
    """C1 real-time nowcasts; score targets after dev_end (descriptive: the holdout carries no tests)."""
    z = nc.Z1()
    inputs = [i for i in nc.pit.load_inputs() if i["id"] in nc.FREQ]
    vint, _ = nc.pit.load_vintages(inputs)
    df = nc.run("RT", z, vint, holdout=read_holdout)
    df = df[df["k"] <= 3]
    hold = df[df["q"] > dev_end]
    sc = nc.score(hold)
    scored = hold[hold["actual"].notna()]          # deviation c1b-dev-1 (a): "no target" rows are not targets
    return {"n_targets": int(scored["q"].nunique()), "n_no_target_instants": int(hold["actual"].isna().sum()),
            "no_target_quarters": sorted(hold.loc[hold["actual"].isna(), "q"].unique().tolist()),
            "scores": sc.to_dict(orient="records"),
            "bridge_mean_error_pp": float(100 * (hold["bridge"] - hold["actual"]).mean()) if len(hold) else None}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return clean(o.item())
    return o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prereg")
    ap.add_argument("--approval")
    a = ap.parse_args(argv)
    if not a.dry_run:                   # every gate before any data is touched
        if a.prereg != fc.FROZEN:
            raise SystemExit(f"--prereg {fc.FROZEN} required")
        if not a.approval:
            raise SystemExit("--approval <commit with Eleonora's go in PLAN.md> required")
        row = check_approval(a.approval)
        check_order(a.approval)
        clean_tree()
    fz = check_freeze()
    cal = pd.read_csv(fc.C1 / "z1_calendar.csv")
    bridge = fc.Bridge()
    if a.dry_run:
        dev_end = pd.Period("2019Q2", "Q")
        share = fc.load_latest()                       # cut at 2023Q2: no holdout quarter is read
        out = {"mode": "DRY RUN: pretend holdout 2019Q3-2023Q2, inside the development sample; not a result",
               "freeze": fz["frozen_commit_note"],
               "c2": c2_holdout(share, dev_end, None, cal, bridge),
               "c1": c1_holdout(str(dev_end), read_holdout=False)}
        d = ROOT / "data" / "holdout_dryrun"
        d.mkdir(parents=True, exist_ok=True)
        (d / "dryrun_results.json").write_text(json.dumps(clean(out), indent=1, allow_nan=False) + "\n")
        print(f"dry run written to {d / 'dryrun_results.json'} (not a result; not committed)")
        return 0
    # ---- the real run (gates passed above)
    share = fc.load_latest(holdout=True, prereg=a.prereg)
    tests_dev = pd.read_csv(HERE / "tests_dev.csv")
    out = {"mode": "HOLDOUT RUN (one time)", "approval_commit": a.approval, "approval_row": row,
           "freeze": fz, "c2": c2_holdout(share, fc.DEV_END, tests_dev, cal, bridge),
           "c1": c1_holdout(str(fc.DEV_END), read_holdout=True)}
    (HERE / "holdout_results.json").write_text(json.dumps(clean(out), indent=1, allow_nan=False) + "\n")
    print("holdout results written; commit them as one commit, then do not rerun")
    return 0


if __name__ == "__main__":
    sys.exit(main())
