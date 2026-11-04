---
name: z1-release-update
description: Runs the update for a new Federal Reserve Z.1 Financial Accounts release end to end (detect, extract, transform, validation gate, "what moved" note, stale-copy list, draft commit) and stops for human approval before anything is committed, loaded or published. Use when the Fed has published a new Z.1 (quarterly, about the second week of Mar, Jun, Sep, Dec) or someone asks to refresh the project's data for a new Z.1 / Financial Accounts release. Not for NY Fed HHDC-only or FRED-only refreshes, data questions or code changes.
---

# Z.1 release update

Goal: bring the repo from one Z.1 vintage to the next, show a human exactly what moved and which published numbers are now stale, and stop. Nothing is committed, loaded into a database or deployed without an explicit yes at the gates marked **ASK**.

Run everything from the repo root unless stated. `uv run hhdebt ...` runs from `pipeline/`. Python helpers run as `uv run --project pipeline python <script>`.

## Hard rules
- Never edit a number, snapshot value, register `value` or page copy to make a check pass or to "apply" the release. Validation reports; humans decide.
- Never run `hhdebt load` (or `hhdebt run` without `--no-load`) without an explicit yes. Never touch the production Vercel deployment or database; preview deployments only, and only if asked.
- Raw downloads stay immutable under `data/raw/`; `data/` is gitignored. Do not delete or overwrite anything there.
- Stop at the first FAIL. Report it; do not work around it.
- Secrets never go through chat.

## Steps

### 1. Detect
```bash
uv run --project pipeline python .claude/skills/z1-release-update/scripts/detect_release.py
```
It HEADs `https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip` and compares Content-Length and Last-Modified with the latest `"source": "z1"` line of `data/manifest.jsonl` (its `bytes`, `vintage` = the `Z1.csv` member date) and with `vintages.z1` in `web/public/data/meta.json`. Exit 0: say "no new Z.1 release" with the numbers it printed, and stop. Exit 10: continue. Exit 2: report why and stop. If it said "possibly new" (same size, later date), the Z1.csv member date after step 3 decides: if it equals the old vintage, say nothing is new and stop.

### 2. Keep the previous vintage
The script prints the previous zip, e.g. `data/raw/z1/83b8eded0bc7f9b7_FRB_Z1_csv.zip`. Raw files are stored by content hash and never overwritten, so it stays. Note its path as `PREV`. Do not rely on `data/z1/FRB_Z1_csv.zip`: that cache is overwritten by the new download. `PREV` must be read before step 3 if this is the first time the step is done in a fresh clone; if `data/raw/z1/` is empty, say so and ask the human for the previous zip (do not guess a URL; the Fed's archive pattern is `https://www.federalreserve.gov/releases/z1/<YYYYMMDD>/z1_csv_files.zip`, which `validation/zparse.py` also reads).

### 3. Extract and transform (no load)
```bash
cd pipeline
uv run hhdebt extract --sources z1 --force-download
uv run hhdebt transform
cd ..
```
Do not add `fred` / `nyfed` sources unless the human asks. Never `hhdebt load` here. Confirm the new manifest line (`tail -n 1 data/manifest.jsonl`: new sha256, `vintage` = new Z1.csv date) and record it as `CURR`: the new file in `data/raw/z1/`, plus `data/z1/FRB_Z1_csv.zip`.

### 4. Validation gate
```bash
uv run --project pipeline python validation/run.py --z1-zip CURR --prev-z1-zip PREV
```
It writes `validation/REPORT.md` and `validation/results.json`; exit 1 means at least one FAIL. On any FAIL: stop, show the failing rows (`id`, `observed`, `note`), say which identity or headline broke, and wait. Do not edit the data, the catalog, the thresholds or the check to get a pass. WARN and NOT RUN do not stop the run but are carried into the note (NOT RUN is never a PASS; D2 needs `DATABASE_URL_READONLY`, say so).

### 5. "What moved" note
```bash
uv run --project pipeline python .claude/skills/z1-release-update/scripts/what_moved.py \
  --prev PREV --curr CURR --results validation/results.json
```
Writes `data/releases/<current vintage date>/what_moved.md` (gitignored): new quarters; headline public share, public $ and scope $ (level, q/q, y/y); risk-bucket shares and changes; the ten largest revisions to history beyond a threshold (0.05 pp of share or $1,000M of scope or public debt; `--thr-pp`, `--thr-musd`, `--top`); non-PASS validation checks and recent unexplained jumps. Formats follow the site: one decimal for %, two for $T. Read it before presenting it; if the new quarter or the headline disagrees with validation C2/C3, stop and investigate.

### 6. Stale copy
```bash
uv run --project pipeline python .claude/skills/z1-release-update/scripts/stale_claims.py
```
Reads `claims/register.csv` and `validation/results.json`; for each row whose `check_id` is in the new results it compares the register `value` to the newly observed number at the precision of `display`, and lists the claims that would change, with their `locations`. If the register does not exist yet it says so and exits 0: report that "stale copy not checked: no register". It never edits copy. Rows reported as "cannot compare" or "ambiguous match" need a human look. Claims without a `check_id` are not covered by this scan: say how many.

### 7. Draft, don't publish
```bash
cd pipeline && uv run hhdebt export-snapshot --source local && cd ..
git status --short
git diff --stat
```
`--source local` writes `web/public/data/*.json` from the local transform output, not the database (so `meta.json` will say "local transform output"; flag that in the summary, since the committed snapshots normally say "database"). Then present, in this order: the `git diff --stat`; the what-moved note (paste the headline, buckets and top revisions; link the file); the stale-claims list; validation WARN/NOT RUN items. Propose a commit message, for example:

```
data: Z.1 <YYYY-MM-DD> release (<latest quarter>)

Public share <x.x%> (<+/-x.x pp> q/q); scope $<x.xx>T. Validation: <n> PASS, <n> WARN, 0 FAIL.
Snapshots exported from local transform output; database not loaded.
```

**ASK** and wait for an answer to each, separately:
1. Commit the snapshot change? (Never push or deploy as part of this skill.)
2. Load the database (`cd pipeline && uv run hhdebt load`)? Needs `DATABASE_URL`; state that it replaces core and mart tables. Production only on an explicit yes.
3. Update the stale copy / register rows listed in step 6? That is a separate task done with the human.
4. Anything reaching production (merge, deploy, promote): not done by this skill.

Also remind the human to add the session to `docs/building-with-claude.md` per `CLAUDE.md`.

## Files
- `scripts/detect_release.py`, `scripts/what_moved.py`, `scripts/stale_claims.py`: the three helpers above.
- `tests/test_what_moved.py`: synthetic tests, no network: `uv run --project pipeline pytest -q .claude/skills/z1-release-update/tests`.
- `examples/triggers.md`: prompts that should and should not trigger this skill.
- `examples/replay-2026-06-to-2026-09/`: a real run of steps 5 and 6 on the June to September 2026 releases.

## When NOT to use
- NY Fed Household Debt and Credit Report or FRED-only refreshes (`hhdebt extract --sources nyfed|fred`): they have their own sources and no Z.1 validation gate.
- Questions about the data or the numbers ("what was the public share in 1990?"): query `mart.public_share` or the snapshot; do not run a release.
- Code changes to the pipeline, validation suite, catalog or sites, including fixing a failing check: that is ordinary development.
- Loading or deploying already-approved data: run the single command asked for.
- Re-running validation on the current vintage with nothing new: just run `validation/run.py`.
