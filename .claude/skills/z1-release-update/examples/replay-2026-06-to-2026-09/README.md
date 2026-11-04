# Replay: June 2026 to September 2026 Z.1

A real run of steps 5 and 6 of the skill, to test it before the next live release (10 Dec 2026).

- Previous vintage: `data/validation/prev_z1_csv_files.zip`, the Fed's archived per-table files from
  https://www.federalreserve.gov/releases/z1/20260611/z1_csv_files.zip (newest member dated 2026-06-10; latest quarter 2026Q1).
- Current vintage: `data/validation/FRB_Z1_csv.zip` (`Z1.csv` dated 2026-09-11; latest quarter 2026Q2).
- Validation input: `validation/results.json` from `validation/run.py --prev-z1-zip data/validation/prev_z1_csv_files.zip`
  (41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN).

Command (repo root):
```bash
uv run --project pipeline python .claude/skills/z1-release-update/scripts/what_moved.py \
  --prev data/validation/prev_z1_csv_files.zip --curr data/validation/FRB_Z1_csv.zip \
  --results validation/results.json \
  --out .claude/skills/z1-release-update/examples/replay-2026-06-to-2026-09/what_moved.md
uv run --project pipeline python .claude/skills/z1-release-update/scripts/stale_claims.py \
  > .claude/skills/z1-release-update/examples/replay-2026-06-to-2026-09/stale_claims.txt
```

Files:
- `what_moved.md`: script output, unedited. Its headline (56.4%, $10.77T of $19.10T) and largest scope revision
  (2025Q3, +$5,272M) agree with validation checks C2, C3 and F1.
- `stale_claims.txt`: script output, unedited. At the time of the replay `claims/register.csv` (task 0.5) did not exist,
  so the scan skipped with a message. Re-run it once the register exists; nothing in this folder was hand-written.

Steps 1 to 4 and 7 (detect, download, transform, export, commit) were not replayed: they need the network, write
`data/` and `web/public/data/`, and the September data is already in the repo.
