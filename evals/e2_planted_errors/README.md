# E2: planted-error test

Design: `docs/decisions/e2-prereg.md`, frozen 2026-11-04 (commit `5986353`) with Eleonora's choices; later changes are dated deviations in that file. `plant.py` refuses to run unless the pre-registration is frozen.

Runs:
- `run-20261113/`: first run. Disclosed isolation breach (the reviewers could read the whole repository, including the unplanted originals), found by a Fable 5.2 judge; kept for the record, not used for the headline.
- `run-20261113r/`: rerun with a fresh seed and isolated folders, chosen by Eleonora. Results and caveats: [`run-20261113r/results-note.md`](run-20261113r/results-note.md) (Claude draft, UNVERIFIED). Register rows `e2_r13r_*`.


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
