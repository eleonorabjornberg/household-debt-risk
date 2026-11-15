# Joint holdout results (C2 forecast, C1 and C1b nowcasts)

> Written by the markets track from the result files.

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

## C2: the share forecasts (h = 1, 4 and 8 quarters ahead) against their benchmarks

Holdout RMSE of the candidate divided by the benchmark's, with the pre-registered verdict (`docs/decisions/scoring-protocol.md`, option (a)): "beats" needs a lower loss on development, significant after Holm, and a lower loss in the holdout. "Does not beat" means the benchmark's loss is lower in either sample, so it can sit beside a holdout ratio below 1 when the development loss was higher. Pseudo out-of-sample on latest-vintage data, not real time.

No candidate beats no-change at any horizon or design (0 "beats" verdicts against no-change). The 3 "beats" verdicts are all against the seasonal naive at h = 1. Coverage of the intervals and the full score tables are in the results file.

Full write-up, with every table and check: via the MCP and Ask API (`get_research_writeup`) or on GitHub ([README](https://github.com/eleonorabjornberg/household-debt-risk/blob/main/research/joint_holdout/README.md)).
