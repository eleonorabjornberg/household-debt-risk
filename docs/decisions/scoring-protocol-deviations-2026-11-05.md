# Dated deviations from the frozen scoring protocol (2026-11-05, after the one joint holdout run)

> **Claude draft.** Written by the markets track on Eleonora's decisions on cards c3-errors and c3-hcount (PLAN.md "Decisions taken", 2026-11-05, chosen 15:55 UTC, recorded by the coordinator at ccc1fc6). The frozen files are left unedited: `docs/decisions/scoring-protocol.md` (192d60c plus its earlier dated deviations), `research/c2_forecast/SPECS.md`, `research/c2_forecast/FREEZE.json` and `research/c2_forecast/holdout_run.py`. The correction of the decision rule is a separate file, `scoring-protocol-erratum-2026-11-05.md`.

## D1. A second opening of the C2 holdout, to write the per-forecast table (c3-errors (b))

*Written and committed before the run.*

**Why.** The protocol allows one holdout opening. That opening was the joint run of 2026-11-05 (commit a0d9151, approval 432fed0). It wrote C2's holdout scores, coverage and verdicts, but not the individual forecasts. So C3 could not publish the protocol's "ten largest errors per horizon" for the C2 holdout, or score the origin-based subset of D2.

**Decision.** Eleonora approved one second, separately gated run of the frozen C2 holdout step, with these limits:
- it writes only the per-forecast table;
- it uses the same frozen code and hashes;
- it produces no new scores or verdicts.

This is recorded as a second opening of the holdout.

**How it runs.** Script: `research/c2_forecast/holdout_forecasts_run.py`. It is a new file and leaves every frozen file unchanged.
- **Gates.** It checks all of these before any holdout data is read:
  - `--prereg 192d60c`;
  - `--approval ccc1fc6`, whose PLAN.md has her c3-errors row;
  - that the approval commit comes after the last change to `FREEZE.json` and is an ancestor of HEAD, using the frozen `holdout_run.check_order`;
  - a clean working tree;
  - every frozen file against `FREEZE.json`, using the frozen `holdout_run.check_freeze`;
  - that neither output exists now or was ever committed.
- **Forecasts.** They come from the frozen `forecast.backtest_latest` and `forecast.add_intervals`, with the same holdout split as `holdout_run.c2_holdout`: rows with T + h > 2023Q2.
- **Checks, compared and never written:**
  - (1) the frozen `holdout_run.c2_holdout`, recomputed in memory, must reproduce the committed `c2` block of `holdout_results.json` exactly;
  - (2) the table must reproduce the committed `scores_holdout` exactly.

  If either check fails, nothing is written and the run is reported to the coordinator.
- **Outputs**, committed as one commit:
  - `research/c2_forecast/holdout_forecasts.csv`, the per-forecast table;
  - `research/c2_forecast/holdout_forecasts_run.json`, the run record.

  The run is allowed once only. C1's and C1b's holdout steps are not rerun; their per-instant table already exists (`research/c1b_nowcast/nowcasts_holdout.csv`).

**What changes.** No score, coverage figure, test or verdict is computed for publication by this run. C3 uses the table only for:
- the ten largest C2 holdout errors per horizon;
- the origin-based subset in D2;

and states that these numbers come from the second opening.

## D2. The holdout is defined by target quarter (c3-hcount (b))

**The discrepancy.** The protocol's holdout option (b), "The last 12 quarters, 2023Q3–2026Q2", adds: "Origins 2023Q2 onward give 12, 9 and 5 holdout forecasts at h = 1, 4, 8." That counts by origin. The frozen code (`holdout_run.c2_holdout`) and the one joint run count by target quarter. Every forecast whose target T + h lies in 2023Q3–2026Q2 is a holdout forecast, which gives 12 at each horizon. Those origins start at 2023Q2 (h = 1), 2022Q3 (h = 4) and 2021Q3 (h = 8). The difference was not declared before the run. It was found by the quant-reviewer in the C3 review (mkt-q32).

**Decision.** Eleonora chose (b):
- the holdout is defined by **target quarter**, 2023Q3–2026Q2. This matches `SPECS.md` ("The holdout is 2023Q3–2026Q2") and the committed results, which stand as reported;
- C3 also reports the **origin-based subset**, the forecasts with origin T ≥ 2023Q2, which gives 12, 9 and 5 at h = 1, 4 and 8. It is computed from the D1 table and labelled as a subset of the same opening. It is descriptive, with no test, like every holdout number.

**What does not change.** The development sample (targets up to 2023Q2), the frozen code, the tests and the decision rule (see the erratum) are all unchanged.
