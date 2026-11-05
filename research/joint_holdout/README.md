# Joint holdout results (C2 forecast, C1 and C1b nowcasts)

> **Claude draft.** Written by the markets track from the result files. Eleonora replaces it with her own text before anything here is published.

The holdout is 2023Q3–2026Q2. It was opened once, in commit a0d9151, under Eleonora's approval 432fed0 and after deviation c1b-dev-1 (cddd3ca). Source files: `research/c2_forecast/holdout_results.json`, `research/c1b_nowcast/holdout_results.json` and `research/c1b_nowcast/nowcasts_holdout.csv`. Every number below comes from those files through `make_readme_and_rows.py`; none was typed by hand.

Each cell rests on 12 targets or fewer, so these are small-sample numbers.

## C1b: does Freddie Mac's monthly data improve the real-time nowcast?

RMSE in percentage points of the public share, real-time first-release targets. k is the nowcast instant within the quarter.

| k | scored instants | C1b bridge | C1 bridge | no change |
|---|---|---|---|---|
| k = 1 | 12 | 0.14 pp | 0.15 pp | 0.20 pp |
| k = 2 | 12 | 0.13 pp | 0.15 pp | 0.20 pp |
| k = 3 | 11 | 0.15 pp | 0.18 pp | 0.20 pp |
| pooled k = 1–3 | 35 | 0.14 pp | 0.16 pp | 0.20 pp |

Pre-registered verdict (`docs/decisions/c1b-prereg.md`, decision rules): **improves on C1**. The rule needs lower RMSE at every k on development, significant after Holm at one or more k, and a lower pooled RMSE in the holdout. The holdout part is a comparison of RMSEs, with no test.

## C1: the accounting bridge in real time

Bridge RMSE relative to no-change on the same instants. The holdout carries no tests.

| k | instants | bridge / no change |
|---|---|---|
| k = 1 | 12 | 0.75 |
| k = 2 | 12 | 0.76 |
| k = 3 | 11 | 0.92 |
| pooled k = 1–3 | 35 | 0.81 |

Mean bridge error over the holdout instants: −0.08 pp (negative: the bridge nowcast is below the outcome).

Targets scored: 12 quarters. The 2 instants that target 2026Q3 are recorded as "no target" (deviation c1b-dev-1): no Z.1 has published that quarter, and it lies outside the holdout window.

## C2: the share forecasts (h = 1, 4 and 8 quarters ahead) against their benchmarks

Holdout RMSE of the candidate divided by the benchmark's, with the pre-registered verdict (`docs/decisions/scoring-protocol.md`, option (a)): "beats" needs a lower loss on development, significant after Holm, and a lower loss in the holdout. "Does not beat" means the benchmark's loss is lower in either sample, so it can sit beside a holdout ratio below 1 when the development loss was higher. Pseudo out-of-sample on latest-vintage data, not real time.

| design | h | candidate | vs no change | vs AR (BIC) | vs seasonal naive |
|---|---|---|---|---|---|
| expanding | 1 | Z-DIR | 1.16 (does not beat) | 0.94 (comparable) | 0.87 (beats) |
| expanding | 1 | Z-DAMP | 1.10 (does not beat) | 0.89 (comparable) | 0.83 (beats) |
| expanding | 1 | ZC1-DIR | 1.31 (does not beat) | 1.07 (does not beat) | 0.99 (comparable) |
| expanding | 4 | Z-DIR | 1.40 (does not beat) | 0.97 (does not beat) | 0.83 (comparable) |
| expanding | 4 | Z-DAMP | 1.42 (does not beat) | 0.98 (comparable) | 0.84 (comparable) |
| expanding | 4 | ZC1-DIR | 3.98 (does not beat) | 2.77 (does not beat) | 2.36 (does not beat) |
| expanding | 8 | Z-DIR | 1.90 (does not beat) | 1.02 (does not beat) | 0.66 (comparable) |
| expanding | 8 | Z-DAMP | 1.31 (does not beat) | 0.70 (does not beat) | 0.45 (comparable) |
| rolling | 1 | Z-DIR | 1.16 (does not beat) | 0.90 (comparable) | 0.87 (comparable) |
| rolling | 1 | Z-DAMP | 1.09 (does not beat) | 0.85 (comparable) | 0.82 (beats) |
| rolling | 4 | Z-DIR | 1.34 (does not beat) | 0.84 (comparable) | 0.79 (does not beat) |
| rolling | 4 | Z-DAMP | 1.42 (does not beat) | 0.88 (comparable) | 0.84 (comparable) |
| rolling | 8 | Z-DIR | 2.15 (does not beat) | 1.21 (does not beat) | 0.74 (comparable) |
| rolling | 8 | Z-DAMP | 1.31 (does not beat) | 0.74 (comparable) | 0.45 (comparable) |

No candidate beats no-change at any horizon or design (0 "beats" verdicts against no-change). The 3 "beats" verdicts are all against the seasonal naive at h = 1. Coverage of the intervals and the full score tables are in the results file.
