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
- `stale_claims.txt`: script output, unedited, re-run on 2026-11-04 once `claims/register.csv` (task 0.5) existed
  (104 rows). Result: 0 changed, 12 unchanged, 2 cannot compare (`count` rows: no validation check reports a
  count), 90 with no check. Zero changes is the expected answer here: the register was built from the September
  vintage, the same vintage as `validation/results.json`. So this run tests the unit handling (shares stored as
  fractions, e.g. `0.5638`, compared as percent at display precision), not detection. Detection of a changed
  number is covered by the synthetic tests in `tests/` (`test_stale_detects_only_display_changes`,
  `test_register_units_share_fraction_and_vocabulary`). A June-vintage `results.json` could not be regenerated
  for a true June-to-September scan: www.federalreserve.gov was blocked by this session's network policy.
  The first real detection run will be the 10 Dec 2026 release.

Steps 1 to 4 and 7 (detect, download, transform, export, commit) were not replayed: they need the network, write
`data/` and `web/public/data/`, and the September data is already in the repo.
