# E2: planted-error test (tooling only; **not run**)

Design: `docs/decisions/e2-prereg.md`, a **draft** with Eleonora's choices open. `plant.py` refuses to run unless that
file says it is frozen. Only `--rehearsal` dry runs are possible before then, and they never write to `results/`.

| File | What |
|---|---|
| `catalogue.yaml` | 14 error types: 8 data (skeptic), 6 method (quant-reviewer); each with the fix a correct objection names |
| `plant.py` | Plants k errors per document copy, adds controls, gives the variants neutral names, writes `key.json` (hidden) and `key.sha256` (commit before reviewers run) |
| `score.py` | `match`: objections ↔ planted errors by location (±2 lines or a 20-character quote) → `scoring.csv` for the human "same fix" call and `objections.csv` for false alarms; `summarise`: recall per agent and category with Wilson and cluster-bootstrap 95% intervals, false-alarm rate, misses; **appends** to `results/results.jsonl` |
| `tests/` | Synthetic documents only (6 tests) |

Run order after the freeze:
1. Run `plant.py` with the frozen settings, then commit `key.sha256` only.
2. Run the reviewers on `run-<id>/docs/` only, writing to `run-<id>/review-log.md` (isolation per CHOICE-5).
3. Run `score.py match`, then the human scoring, then `score.py summarise`.
4. Write `misses.md`.

Rehearsal, 2026-11-04 (scratchpad, not kept): 12 planted × 3 errors + 4 controls on six write-ups planted all 36
errors. The categories were uneven: `period_shift` never found an eligible line, and `number_change` fit once. See
CHOICE-10 in the pre-registration.
