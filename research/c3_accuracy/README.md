# C3: how accurate are the share forecasts and nowcasts?

> **Claude draft.** Written by the markets track from committed result files by `make_report.py`. Eleonora replaces it with her own text before anything here is published. No model was rerun and the holdout was not reopened. Most numbers are copied from the committed results. The script itself computes only these: the C1 verdicts (section 2), the holdout bias table (with C1b's own `mean_hac1`), the ten-largest-error lists, the regime splits and the chance counts in the headline, each from committed per-forecast tables. The register rows are all UNVERIFIED: the claim checker cannot recompute most of them, because they point into list-valued JSON.

This is the report that `docs/decisions/scoring-protocol.md` ("What C3 must publish") asks for. The quantity forecast is the public share: the part of US household mortgages and consumer credit held by federal programmes, the GSE and agency pools, and state and local governments. It is computed from the Federal Reserve's Z.1 Financial Accounts as defined in the protocol ("Target"; denominator `FL154104015`). Errors are in percentage points (pp) of that share. "Latest vintage" means the Z.1 release dated 2026-09-11.

**Status of the verdicts.** The verdicts apply the decision rule as corrected by `docs/decisions/scoring-protocol-erratum-2026-11-05.md`: rule (b), which Eleonora chose at the freeze and confirmed on card c3-rule. Under (b) a model "beats" a benchmark when three things hold: its development RMSE is lower and significant after Holm, and its holdout RMSE is lower (rule (a)); its RMSE ratio is 0.95 or below in both samples; and its 80% coverage is not rejected on development data. The protocol sets no test level for "not rejected" and says nothing about models without intervals. This report reads them as p below 0.05 on either test (Kupiec or Christoffersen, 80% level, h = 1) and as "undetermined". Both are readings, not rules; they are open on Eleonora's docket as cards c3-b-level and c3-b-nointv, and no verdict is final until she answers. Section 2 shows what the other readings change, including Kupiec only, since Christoffersen tests independence rather than coverage.

**Tasks and models.**
- **C2** forecasts the share h = 1, 4 and 8 quarters after the latest quarter T in a Z.1 release. Candidates (defined in `research/c2_forecast/SPECS.md`): `Z-DIR` is a direct regression of the h-quarter change on the last four quarterly changes; `Z-DAMP` is a damped mean of recent changes; `ZC1-DIR` is `Z-DIR` plus C1's nowcast as a regressor. Benchmarks: no-change (the share stays where it is), drift (the average past change), AR (BIC), an autoregression whose order is chosen by the Bayesian information criterion, and seasonal naive (the change of the same quarter a year earlier). Expanding and rolling are the two estimation windows.
- **C1** nowcasts the next quarter's change from monthly and weekly indicators (`research/c1_nowcast/EVALUATION.md`). The *bridge* moves each Z.1 holder cell by its indicator's growth; the *bridge regression* recalibrates the bridge on past errors. k = 1, 2, 3 is the monthly instant within the quarter at which the nowcast is made. RT is the real-time sample, with Z.1 and indicators as they were published at the time. P2a and P2b are pseudo-real-time: Z.1 from the latest vintage cut at T, with point-in-time indicators and latest-vintage targets. They differ in their indicator sets.
- **C1b** is C1 with Freddie Mac's monthly volume data added (`docs/decisions/c1b-prereg.md`). Fannie Mae and Ginnie Mae holdings are carried flat, which is an assumption.

**Terms.**
- Tests:
  - CW, Clark–West, is used for nested models and is one-sided.
  - DM-HLN, Diebold–Mariano with the Harvey–Leybourne–Newbold small-sample correction, is used for non-nested pairs and is two-sided.
  - Holm is a step-down correction that holds the chance of any false positive across a family of tests.
  - HAC lag means the autocorrelation allowance in a test's variance.
- Scores of whole predictive distributions, where lower is better:
  - The interval score penalises interval width and misses.
  - CRPS, the continuous ranked probability score, scores the full forecast distribution.
- Coverage tests:
  - Kupiec tests whether the coverage rate is right.
  - Christoffersen tests whether misses come independently.
  - Clopper–Pearson gives an exact binomial interval for a coverage rate.
- Burn-in is the number of past errors needed before an interval is formed.
- "Frozen" means fixed by hash before the holdout was opened.

**The holdout** is 2023Q3–2026Q2. It was opened once, in commit a0d9151, under Eleonora's approval 432fed0, and the protocol allows only one opening. An earlier approved run (77460b4) stopped with an error before writing or printing anything (deviation c1b-dev-1, section 7). Everything else is the development sample, scored before the holdout was opened.

**What a reader should take from it**

- **C2 forecasts.** On point-forecast error (RMSE), no frozen candidate beats the no-change forecast or the AR benchmark at any horizon in either window design. In development, the Z candidates' RMSE is below no-change's at every horizon. In the holdout it is above at every horizon and in both designs (all ratios in section 2 are above one). The two samples point in opposite directions. The holdout has 12 targets from one three-year period and carries no test, and no explanation for the flip has been tested. On CRPS, a score of the whole forecast distribution, `Z-DIR` and `Z-DAMP` are below no-change in the holdout at every horizon (section 2), so the picture depends on the loss. Under rule (b) (erratum) every possible "beats" is against the seasonal naive at h = 1. How many there are depends on the open reading of the coverage clause (card c3-b-level): 1 to 3 across the readings in section 2, 2 under the interim reading. No verdict is final.
- **Holdout targets are barely revised.** All samples are scored on the 2026-09-11 vintage. A holdout target has had 0 to 11 later Z.1 releases since its first release; development targets from 2016 on have had at least 12. Development errors therefore include more revision than holdout errors, which affects any development-versus-holdout comparison (skeptic mkt-s45).
- **C1 nowcast.** Under the same rule, under the interim readings no C1 comparison is a "beats"; bridge_reg vs no_change at k = 2 meets every loss condition of rule (b) and is "undetermined", not a failure: C1 issues no intervals for the coverage clause (card c3-b-nointv). At the other instants the same comparison has holdout ratios above one (section 2), and the three instants share the same 12 target quarters, so they are not independent. This report computed the verdicts by applying rule (b) to C1's committed tests and holdout scores; no frozen C1 code issues verdicts. The bridge regression had the lowest development ratio, but on fewer targets (16/16/10 against the bridge's 28/28/22 at k = 1/2/3). Its pooled holdout RMSE is no lower than no-change's.
- **C1b.** Its verdict under the decision rules of `docs/decisions/c1b-prereg.md` is "improves on C1". It rests on development tests significant after Holm (section 2) and on a lower pooled holdout RMSE over 35 instants in 12 target quarters, a comparison without a test.
- **Largest errors and crisis windows.** Section 3 lists Z-DIR's ten largest development errors at each horizon. The number of them falling in the protocol's 2007Q4–2011Q4 or 2020 windows is, by target quarter, 1 at h = 1 (chance 1.6; 2011Q1); 3 at h = 4 (chance 1.6; 2007Q4, 2008Q2, 2008Q3); 4 at h = 8 (chance 1.7; 2008Q3, 2008Q4, 2009Q2, 2009Q3). And by origin quarter, 1 at h = 1 (chance 1.6; 2010Q4); 0 at h = 4 (chance 1.6); 0 at h = 8 (chance 1.7). "Chance" is the count expected if the ten had fallen at random among all development forecasts at that horizon. The rest of the ten fall outside both windows (section 3). Errors at h = 4 and 8 overlap, so neighbouring quarters in these lists are one episode. In the GFC window, by either split and at every horizon, the Z candidates' RMSE relative to no-change is lower than outside both windows (section 4). The 2020 window is mixed, and it rests on four forecasts per cell.
- **Holdout openings.** C2's individual holdout forecasts come from a second, separately gated opening (deviation D1, Eleonora's c3-errors (b)). It reproduced the first run's scores exactly and wrote only the per-forecast table (section 3). The regime windows fall in development only. Cells with fewer than ten forecasts are marked ‡. The unmarked holdout cells, with 11 or 12 forecasts, are also small.

## 1. Specification registry, including superseded and abandoned versions

Development scores: RMSE relative to no-change on the same targets (below 1 is better than no-change). Score columns 1 / 2 / 3 mean h = 1 / 4 / 8 for C2 (latest vintage, expanding window) and k = 1 / 2 / 3 for C1 and C1b. C1 and C1b rows are on the real-time sample RT with first-release targets, except the P2a and P2b rows, which use latest-vintage targets. Placebo rows have no stored n (n/a). Commits are where the version was first scored, with the commit date. n is the number of development forecasts behind each score: `bridge_reg` and `ZC1-DIR` rest on far fewer than the rows beside them, so their scores are not comparable with those rows.

| task | ID | status | commit | date | dev score 1 (n) | dev score 2 (n) | dev score 3 (n) |
|---|---|---|---|---|---|---|---|
| C2 | `Z-DIR` | frozen candidate | 0bc647b | 2026-11-04 | 0.75 (133) | 0.70 (130) | 0.79 (126) |
| C2 | `Z-DAMP` | frozen candidate | 0bc647b | 2026-11-04 | 0.73 (133) | 0.70 (130) | 0.81 (126) |
| C2 | `ZC1-DIR` | frozen candidate (Z+C1 common origins only) | 0bc647b | 2026-11-04 | 0.80 (18) | 1.40 (12) | 0.96 (4‡) |
| C2 | `drift` | benchmark | 0bc647b | 2026-11-04 | 0.96 (133) | 0.95 (130) | 0.95 (126) |
| C2 | `ar_bic` | benchmark (AR, order by BIC) | 0bc647b | 2026-11-04 | 0.76 (133) | 0.70 (130) | 0.79 (126) |
| C2 | `seasonal_naive` | benchmark (in the decision rules after the seasonality check) | 0bc647b | 2026-11-04 | 0.92 (133) | 0.76 (130) | 1.06 (126) |
| C2 | `placebo-v1` | placebo, first definition (shuffled target); superseded by option (a) at d683482 | 0bc647b | 2026-11-04 | 0.96 | 0.96 | 0.97 |
| C2 | `placebo-a` | placebo, option (a): demeaned shuffled target | d683482 | 2026-11-04 | 1.00 | 1.00 | 1.02 |
| C1 | `bridge` (RT) | primary (accounting bridge) | 99d56cd | 2026-11-04 | 0.73 (28) | 0.72 (28) | 0.76 (22) |
| C1 | `bridge_reg` (RT) | challenger (bridge regression) | 99d56cd | 2026-11-04 | 0.43 (16) | 0.44 (16) | 0.54 (10) |
| C1 | `drift` (RT) | benchmark | 99d56cd | 2026-11-04 | 0.87 (28) | 0.87 (28) | 0.86 (22) |
| C1 | `ar1` (RT) | benchmark (fixed AR(1)) | 99d56cd | 2026-11-04 | 0.94 (28) | 0.94 (28) | 0.97 (22) |
| C1 | `bridge` (P2b) | pseudo-real-time sample P2b (not real time) | 99d56cd | 2026-11-04 | 0.82 (34) | 0.75 (34) | 0.75 (27) |
| C1 | `bridge` (P2a) | pseudo-real-time sample P2a, indicator set 2a (not real time) | 99d56cd | 2026-11-04 | 0.83 (53) | 0.73 (53) | 0.72 (41) |
| C1 | `bridge` (RT@58a93d8) | superseded: fourth instant pooled into k = 3, 2016Q4 target missing; replaced at 99d56cd after review | 58a93d8 | 2026-11-04 | 0.74 (26) | 0.74 (26) | 0.80 (25) |
| C1b | `bridge_c1b` | frozen (Freddie Mac monthly data; Fannie Mae and Ginnie Mae carried flat, an assumption) | 577c572 | 2026-11-04 | 0.58 (28) | 0.42 (28) | 0.37 (22) |
| C1b | Ginnie Mae input | planned, not built: no downloadable file found on 2026-11-04 | — | — | — | — | — |

Not specifications, listed for completeness: the dry run of the holdout script on a pretend holdout inside development (2026-11-04, not committed, not a result), and the first joint holdout run approved at 77460b4, which stopped with an error before anything was written (deviation c1b-dev-1).

## 2. Holdout results for every frozen candidate

### C2 forecasts (12 targets per horizon)

RMSE relative to no-change on the holdout. Pseudo out-of-sample on latest-vintage data, not real time. `ZC1-DIR` is scored on its own comparison (Z+C1 holdout, expanding design only).

**How the holdout was counted.** The run scored every forecast whose target quarter is in 2023Q3–2026Q2: 12 per horizon. Their origins start at 2023Q2 for h = 1, 2022Q3 for h = 4 and 2021Q3 for h = 8, so most h = 4 and h = 8 origins lie in development. Consecutive h = 8 forecasts cover overlapping stretches of quarters, so their errors are not independent. The protocol's option text (holdout choice (b)) says "origins 2023Q2 onward give 12, 9 and 5 holdout forecasts at h = 1, 4, 8", which counts by origin. The two readings differ at h = 4 and 8, and this was not declared before the run. Every h = 4 and 8 holdout number in this report uses the by-target count, which Eleonora confirmed as the definition (card c3-hcount (b), deviation D2 in `docs/decisions/scoring-protocol-deviations-2026-11-05.md`). Found by quant-reviewer (mkt-q32). The origin-based subset is reported below, from the second opening's per-forecast table.

| design | h | no-change RMSE | Z-DIR | Z-DAMP | ZC1-DIR | drift | AR (BIC) | seasonal naive |
|---|---|---|---|---|---|---|---|---|
| expanding | 1 | 0.18 pp | 1.16 | 1.10 | 1.31 | 1.53 | 1.23 | 1.33 |
| expanding | 4 | 0.34 pp | 1.40 | 1.42 | 3.98 | 2.69 | 1.44 | 1.69 |
| expanding | 8 | 0.69 pp | 1.90 | 1.31 | 5.34 | 2.94 | 1.86 | 2.89 |
| rolling | 1 | 0.18 pp | 1.16 | 1.09 | — | 1.61 | 1.28 | 1.33 |
| rolling | 4 | 0.34 pp | 1.34 | 1.42 | — | 2.73 | 1.60 | 1.69 |
| rolling | 8 | 0.69 pp | 2.15 | 1.31 | — | 3.03 | 1.78 | 2.89 |

All losses, expanding design (the primary window). Interval scores and CRPS are in pp; lower is better. The rolling design's full table is in `tables/c2_holdout_scores.csv`.

| h | model | RMSE | MAE | interval score 80 | interval score 95 | CRPS |
|---|---|---|---|---|---|---|
| 1 | no_change | 0.18 | 0.16 | 1.35 | 2.12 | 0.17 |
| 1 | Z-DIR | 0.20 | 0.18 | 0.97 | 1.62 | 0.13 |
| 1 | Z-DAMP | 0.19 | 0.16 | 0.91 | 1.57 | 0.13 |
| 1 | ZC1-DIR | 0.23 | 0.20 | — | — | — |
| 1 | drift | 0.27 | 0.23 | 1.38 | 2.15 | 0.16 |
| 1 | ar_bic | 0.22 | 0.19 | 0.96 | 1.67 | 0.14 |
| 1 | seasonal_naive | 0.23 | 0.19 | 1.26 | 2.06 | 0.16 |
| 4 | no_change | 0.34 | 0.30 | 4.05 | 7.51 | 0.53 |
| 4 | Z-DIR | 0.48 | 0.36 | 3.14 | 5.49 | 0.35 |
| 4 | Z-DAMP | 0.49 | 0.43 | 3.02 | 5.40 | 0.35 |
| 4 | ZC1-DIR | 1.37 | 1.20 | — | — | — |
| 4 | drift | 0.92 | 0.86 | 4.14 | 7.69 | 0.52 |
| 4 | ar_bic | 0.49 | 0.39 | 3.33 | 5.25 | 0.35 |
| 4 | seasonal_naive | 0.58 | 0.52 | 3.64 | 5.33 | 0.43 |
| 8 | no_change | 0.69 | 0.47 | 7.47 | 13.77 | 1.12 |
| 8 | Z-DIR | 1.31 | 0.91 | 6.87 | 11.83 | 0.74 |
| 8 | Z-DAMP | 0.91 | 0.79 | 5.85 | 11.81 | 0.66 |
| 8 | ZC1-DIR | 3.70 | 3.59 | — | — | — |
| 8 | drift | 2.04 | 1.95 | 7.82 | 14.15 | 1.10 |
| 8 | ar_bic | 1.29 | 0.95 | 6.56 | 12.15 | 0.71 |
| 8 | seasonal_naive | 2.00 | 1.74 | 8.17 | 15.79 | 1.20 |

### C2 holdout, origin-based subset (deviation D2)

The same holdout restricted to origins from 2023Q2 on, as the protocol's option text counted it: 12, 9 and 5 forecasts at h = 1, 4 and 8. Computed from `research/c2_forecast/holdout_forecasts.csv` (second opening, D1). Descriptive. Cells: RMSE relative to no-change on the same forecasts; no-change RMSE in pp. At h = 8 the subset has five overlapping forecasts and a very small no-change RMSE, so its ratios are unstable and say little (mkt-q43).

| design | h | n | no-change RMSE | Z-DIR | Z-DAMP | ZC1-DIR | drift | AR (BIC) | seasonal naive |
|---|---|---|---|---|---|---|---|---|---|
| expanding | 1 | 12 | 0.18 pp | 1.16 | 1.10 | 1.31 | 1.53 | 1.23 | 1.33 |
| expanding | 4 | 9‡ | 0.27 pp | 1.97 | 1.96 | 4.01 | 2.89 | 2.01 | 2.30 |
| expanding | 8 | 5‡ | 0.11 pp | 6.55 | 6.86 | 27.24 | 12.96 | 6.33 | 10.84 |
| rolling | 1 | 12 | 0.18 pp | 1.16 | 1.09 | — | 1.61 | 1.28 | 1.33 |
| rolling | 4 | 9‡ | 0.27 pp | 1.95 | 1.96 | — | 2.95 | 2.32 | 2.30 |
| rolling | 8 | 5‡ | 0.11 pp | 6.72 | 6.86 | — | 12.90 | 6.06 | 10.84 |

### C2 tests and verdicts

Development tests, with raw p-values and Holm-adjusted p-values over the family of 42 tests: Clark–West for nested pairs (one-sided), DM-HLN otherwise (two-sided), HAC lag h − 1. "Dev lower" says whether the candidate's development RMSE is below the benchmark's; a two-sided p does not show that direction. The holdout ratio is descriptive: the holdout carries no test.

Verdict labels (rule (b), with the protocol's other wording in the order `holdout_run.py` applies it):
- **does not beat**: the benchmark's RMSE is lower in development or in the holdout;
- **beats**: rule (b) in full (see below);
- **comparable**: lower in both samples but not significant after Holm (the protocol's wording);
- **short of (b)**: lower in both samples and significant, but the ratio is above 0.95 in a sample, or the coverage clause fails under the reading in force. The protocol has no word for this case;
- **undetermined**: every loss condition of (b) is met, but the coverage clause cannot be checked.

The verdicts apply the decision rule as corrected by `docs/decisions/scoring-protocol-erratum-2026-11-05.md`: rule (b), which Eleonora chose at the freeze and confirmed on card c3-rule. Under (b) a model "beats" a benchmark when three things hold: its development RMSE is lower and significant after Holm, and its holdout RMSE is lower (rule (a)); its RMSE ratio is 0.95 or below in both samples; and its 80% coverage is not rejected on development data. The protocol sets no test level for "not rejected" and says nothing about models without intervals. This report reads them as p below 0.05 on either test (Kupiec or Christoffersen, 80% level, h = 1) and as "undetermined". Both are readings, not rules; they are open on Eleonora's docket as cards c3-b-level and c3-b-nointv, and no verdict is final until she answers. Section 2 shows what the other readings change, including Kupiec only, since Christoffersen tests independence rather than coverage.

Superseded: under rule (a) as recorded at the freeze, the frozen run's verdicts gave 3 "beats" (expanding h = 1 Z-DIR vs seasonal_naive; expanding h = 1 Z-DAMP vs seasonal_naive; rolling h = 1 Z-DAMP vs seasonal_naive). C2 verdicts under the other readings of "not rejected": at p < 0.01: 3 "beats" (expanding h = 1 Z-DIR vs seasonal_naive; expanding h = 1 Z-DAMP vs seasonal_naive; rolling h = 1 Z-DAMP vs seasonal_naive), at p < 0.05: 2 "beats" (expanding h = 1 Z-DIR vs seasonal_naive; expanding h = 1 Z-DAMP vs seasonal_naive), at p < 0.1: 1 "beats" (expanding h = 1 Z-DIR vs seasonal_naive), Kupiec only at p < 0.05: 3 "beats" (expanding h = 1 Z-DIR vs seasonal_naive; expanding h = 1 Z-DAMP vs seasonal_naive; rolling h = 1 Z-DAMP vs seasonal_naive).

Under the interim reading (i), the coverage clause fails if either 80% test at h = 1 has p below 0.05. The Christoffersen test in `forecast.py` tests whether misses come independently, not whether coverage is right. So a candidate with correct coverage can fail on independence alone; reading (iv) on card c3-b-level avoids that. Failing on either of two tests at 0.05 is also not a test at the 5% level. A joint conditional-coverage test was not in the protocol and is not computed here (quant-reviewer mkt-q40).

Bandwidth sensitivity: with a lag-8 Bartlett variance (`posthoc_p_bartlett8`, in `tables/c2_verdicts.csv`) the h = 1 p-values of the Z candidates against no-change are 0.003 to 0.004, against far smaller values at the protocol's lag. Their development significance is not robust to that choice.

| design | h | candidate | benchmark | test | dev n | dev ratio | raw p | Holm p | holdout ratio | verdict (b) |
|---|---|---|---|---|---|---|---|---|---|---|
| expanding | 1 | Z-DIR | no_change | CW | 133 | 0.75 | 2.8e-10 | 1.1e-08 | 1.16 | **does not beat** |
| expanding | 1 | Z-DIR | ar_bic | CW | 133 | 0.99 | 0.015 | 0.410 | 0.94 | **comparable** |
| expanding | 1 | Z-DIR | seasonal_naive | DM-HLN | 133 | 0.81 | 6.0e-04 | 0.022 | 0.87 | **beats** |
| expanding | 1 | Z-DAMP | no_change | CW | 133 | 0.73 | 6.0e-11 | 2.4e-09 | 1.10 | **does not beat** |
| expanding | 1 | Z-DAMP | ar_bic | DM-HLN | 133 | 0.96 | 0.229 | 1.000 | 0.89 | **comparable** |
| expanding | 1 | Z-DAMP | seasonal_naive | DM-HLN | 133 | 0.79 | 1.4e-05 | 5.1e-04 | 0.83 | **beats** |
| expanding | 1 | ZC1-DIR | no_change | CW | 18 | 0.80 | 8.7e-04 | 0.030 | 1.31 | **does not beat** |
| expanding | 1 | ZC1-DIR | ar_bic | CW | 18 | 0.74 | 0.039 | 0.906 | 1.07 | **does not beat** |
| expanding | 1 | ZC1-DIR | seasonal_naive | DM-HLN | 18 | 0.68 | 0.154 | 1.000 | 0.99 | **comparable** |
| expanding | 4 | Z-DIR | no_change | CW | 130 | 0.70 | 0.003 | 0.097 | 1.40 | **does not beat** |
| expanding | 4 | Z-DIR | ar_bic | DM-HLN | 130 | 1.00 | 0.969 | 1.000 | 0.97 | **does not beat** |
| expanding | 4 | Z-DIR | seasonal_naive | DM-HLN | 130 | 0.93 | 0.405 | 1.000 | 0.83 | **comparable** |
| expanding | 4 | Z-DAMP | no_change | CW | 130 | 0.70 | 0.005 | 0.145 | 1.42 | **does not beat** |
| expanding | 4 | Z-DAMP | ar_bic | DM-HLN | 130 | 0.99 | 0.920 | 1.000 | 0.98 | **comparable** |
| expanding | 4 | Z-DAMP | seasonal_naive | DM-HLN | 130 | 0.92 | 0.086 | 1.000 | 0.84 | **comparable** |
| expanding | 4 | ZC1-DIR | no_change | CW | 12 | 1.40 | 0.602 | 1.000 | 3.98 | **does not beat** |
| expanding | 4 | ZC1-DIR | ar_bic | DM-HLN | 12 | 1.16 | 0.722 | 1.000 | 2.77 | **does not beat** |
| expanding | 4 | ZC1-DIR | seasonal_naive | DM-HLN | 12 | 1.07 | 0.900 | 1.000 | 2.36 | **does not beat** |
| expanding | 8 | Z-DIR | no_change | CW | 126 | 0.79 | 0.026 | 0.653 | 1.90 | **does not beat** |
| expanding | 8 | Z-DIR | ar_bic | DM-HLN | 126 | 1.00 | 0.817 | 1.000 | 1.02 | **does not beat** |
| expanding | 8 | Z-DIR | seasonal_naive | DM-HLN | 126 | 0.74 | 0.203 | 1.000 | 0.66 | **comparable** |
| expanding | 8 | Z-DAMP | no_change | CW | 126 | 0.81 | 0.031 | 0.742 | 1.31 | **does not beat** |
| expanding | 8 | Z-DAMP | ar_bic | DM-HLN | 126 | 1.02 | 0.868 | 1.000 | 0.70 | **does not beat** |
| expanding | 8 | Z-DAMP | seasonal_naive | DM-HLN | 126 | 0.76 | 0.078 | 1.000 | 0.45 | **comparable** |
| rolling | 1 | Z-DIR | no_change | CW | 133 | 0.77 | 5.9e-10 | 2.3e-08 | 1.16 | **does not beat** |
| rolling | 1 | Z-DIR | ar_bic | CW | 133 | 0.98 | 0.013 | 0.363 | 0.90 | **comparable** |
| rolling | 1 | Z-DIR | seasonal_naive | DM-HLN | 133 | 0.83 | 0.002 | 0.074 | 0.87 | **comparable** |
| rolling | 1 | Z-DAMP | no_change | CW | 133 | 0.72 | 5.7e-11 | 2.4e-09 | 1.09 | **does not beat** |
| rolling | 1 | Z-DAMP | ar_bic | DM-HLN | 133 | 0.92 | 0.022 | 0.559 | 0.85 | **comparable** |
| rolling | 1 | Z-DAMP | seasonal_naive | DM-HLN | 133 | 0.78 | 1.2e-05 | 4.5e-04 | 0.82 | **short of (b): coverage clause failed under this reading** |
| rolling | 4 | Z-DIR | no_change | CW | 130 | 0.80 | 0.004 | 0.122 | 1.34 | **does not beat** |
| rolling | 4 | Z-DIR | ar_bic | DM-HLN | 130 | 0.98 | 0.662 | 1.000 | 0.84 | **comparable** |
| rolling | 4 | Z-DIR | seasonal_naive | DM-HLN | 130 | 1.06 | 0.572 | 1.000 | 0.79 | **does not beat** |
| rolling | 4 | Z-DAMP | no_change | CW | 130 | 0.74 | 0.003 | 0.106 | 1.42 | **does not beat** |
| rolling | 4 | Z-DAMP | ar_bic | DM-HLN | 130 | 0.90 | 0.278 | 1.000 | 0.88 | **comparable** |
| rolling | 4 | Z-DAMP | seasonal_naive | DM-HLN | 130 | 0.98 | 0.764 | 1.000 | 0.84 | **comparable** |
| rolling | 8 | Z-DIR | no_change | CW | 126 | 0.97 | 0.046 | 1.000 | 2.15 | **does not beat** |
| rolling | 8 | Z-DIR | ar_bic | DM-HLN | 126 | 1.02 | 0.641 | 1.000 | 1.21 | **does not beat** |
| rolling | 8 | Z-DIR | seasonal_naive | DM-HLN | 126 | 0.91 | 0.654 | 1.000 | 0.74 | **comparable** |
| rolling | 8 | Z-DAMP | no_change | CW | 126 | 0.81 | 0.015 | 0.410 | 1.31 | **does not beat** |
| rolling | 8 | Z-DAMP | ar_bic | DM-HLN | 126 | 0.86 | 0.228 | 1.000 | 0.74 | **comparable** |
| rolling | 8 | Z-DAMP | seasonal_naive | DM-HLN | 126 | 0.77 | 0.130 | 1.000 | 0.45 | **comparable** |

### Interval coverage (expanding design)

Share of outcomes inside the model's 80% and 95% intervals, with Clopper–Pearson binomial intervals in brackets. The protocol judges coverage on development only: at h = 1 with the Kupiec (unconditional) and Christoffersen (independence) tests; at h > 1 the errors overlap, so there are no tests and the Clopper–Pearson brackets, which assume independent outcomes, are too narrow. Holdout coverage is reported without p-values, as the protocol requires. `ZC1-DIR` has no intervals (too few past errors for the burn-in). Full tables: `tables/c2_coverage.csv`.

| sample | h | model | n | 80% coverage | 95% coverage | Kupiec p (80, 95) | Christoffersen p (80, 95) |
|---|---|---|---|---|---|---|---|
| development | 1 | Z-DIR | 89 | 0.82 [0.72, 0.89] | 0.96 [0.89, 0.99] | 0.629, 0.824 | 0.449, 0.142 |
| development | 1 | Z-DAMP | 89 | 0.79 [0.69, 0.87] | 0.93 [0.86, 0.97] | 0.752, 0.473 | 0.057, 0.390 |
| development | 1 | no_change | 89 | 0.74 [0.64, 0.83] | 0.81 [0.71, 0.88] | 0.182, 2.2e-06 | 9.7e-08, 2.7e-05 |
| development | 1 | ar_bic | 89 | 0.84 [0.75, 0.91] | 0.94 [0.87, 0.98] | 0.300, 0.793 | 0.855, 0.250 |
| development | 4 | Z-DIR | 83 | 0.77 [0.67, 0.86] | 0.83 [0.73, 0.90] | — | — |
| development | 4 | Z-DAMP | 83 | 0.75 [0.64, 0.84] | 0.82 [0.72, 0.90] | — | — |
| development | 4 | no_change | 83 | 0.70 [0.59, 0.79] | 0.78 [0.68, 0.87] | — | — |
| development | 4 | ar_bic | 83 | 0.75 [0.64, 0.84] | 0.83 [0.73, 0.90] | — | — |
| development | 8 | Z-DIR | 75 | 0.67 [0.55, 0.77] | 0.75 [0.63, 0.84] | — | — |
| development | 8 | Z-DAMP | 75 | 0.67 [0.55, 0.77] | 0.72 [0.60, 0.82] | — | — |
| development | 8 | no_change | 75 | 0.65 [0.53, 0.76] | 0.71 [0.59, 0.81] | — | — |
| development | 8 | ar_bic | 75 | 0.65 [0.53, 0.76] | 0.75 [0.63, 0.84] | — | — |
| holdout | 1 | Z-DIR | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 1 | Z-DAMP | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 1 | no_change | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 1 | ar_bic | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 4 | Z-DIR | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 4 | Z-DAMP | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 4 | no_change | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 4 | ar_bic | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 8 | Z-DIR | 12 | 0.92 [0.62, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 8 | Z-DAMP | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 8 | no_change | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |
| holdout | 8 | ar_bic | 12 | 1.00 [0.74, 1.00] | 1.00 [0.74, 1.00] | — | — |

Holdout coverage is descriptive. At h = 4 and 8 the holdout brackets also assume independent outcomes and are too narrow. A coverage of 1.00 on 12 forecasts fits intervals that are too wide as well as correct ones.

**H3 ("intervals are reliable", protocol hypothesis H3 and its decision wording).** The protocol's wording needs coverage "not rejected at either level on development data" and sets no test level; reading "rejected" as p below five per cent (a reading, not a protocol rule): `Z-DIR`: not rejected at h = 1; `Z-DAMP`: not rejected at h = 1. At h = 4 and 8 no test exists, so the wording cannot be used there. There, development coverage of the 95% intervals is below nominal for every model shown. That too is descriptive. One or more p-values sit just above the cut (0.057), so the outcome depends on the reading.

### C1 and C1b nowcasts (real time, first-release targets)

RMSE relative to no-change on the holdout, by instant k; pooled is k = 1–3. The C1b column compares C1b's bridge with no-change on the same instants. Descriptive: no test was run on any holdout number. The pooled row counts each target quarter up to three times (once per k), so its instants are not independent.

| k | instants | no-change RMSE | C1 bridge | bridge regression | drift | AR(1) | C1b bridge |
|---|---|---|---|---|---|---|---|
| 1 | 12 | 0.20 pp | 0.75 | 1.08 | 1.01 | 1.24 | 0.72 |
| 2 | 12 | 0.20 pp | 0.76 | 0.89 | 1.01 | 1.24 | 0.66 |
| 3 | 11 | 0.20 pp | 0.92 | 1.04 | 0.97 | 1.23 | 0.75 |
| pooled | 35 | 0.20 pp | 0.81 | 1.01 | 1.00 | 1.24 | 0.71 |

### C1 and C1b development tests

C1's primary family (bridge and bridge regression against no-change and AR(1), k = 1–3, real time), Holm over 12 tests; C1b's hypotheses H1 (RMSE) and H2 (bias) against C1, Holm over its own family. The Newey–West lag-1 sensitivity is the `posthoc_dm_hac1_p` column of `research/c1_nowcast/tests_dev.csv` and of `research/c1b_nowcast/tests_dev.csv`.

| task | k | candidate | benchmark or hypothesis | test | n | raw p | Holm p |
|---|---|---|---|---|---|---|---|
| C1 | 1 | bridge | no_change | DM-HLN | 28 | 0.011 | 0.107 |
| C1 | 1 | bridge | ar1 | DM-HLN | 28 | 0.177 | 0.676 |
| C1 | 1 | bridge_reg | no_change | CW | 16 | 0.001 | 0.015 |
| C1 | 1 | bridge_reg | ar1 | DM-HLN | 16 | 0.069 | 0.485 |
| C1 | 2 | bridge | no_change | DM-HLN | 28 | 0.037 | 0.299 |
| C1 | 2 | bridge | ar1 | DM-HLN | 28 | 0.170 | 0.676 |
| C1 | 2 | bridge_reg | no_change | CW | 16 | 0.002 | 0.020 |
| C1 | 2 | bridge_reg | ar1 | DM-HLN | 16 | 0.079 | 0.485 |
| C1 | 3 | bridge | no_change | DM-HLN | 22 | 0.103 | 0.514 |
| C1 | 3 | bridge | ar1 | DM-HLN | 22 | 0.210 | 0.676 |
| C1 | 3 | bridge_reg | no_change | CW | 10 | 0.018 | 0.161 |
| C1 | 3 | bridge_reg | ar1 | DM-HLN | 10 | 0.169 | 0.676 |
| C1b | 1 | bridge_c1b | H1 RMSE vs C1 | DM-HLN | 28 | 0.006 | 0.007 |
| C1b | 1 | bridge_c1b | H2 bias vs C1 | paired t (HLN) | 28 | 9.7e-05 | 3.9e-04 |
| C1b | 2 | bridge_c1b | H1 RMSE vs C1 | DM-HLN | 28 | 0.002 | 0.006 |
| C1b | 2 | bridge_c1b | H2 bias vs C1 | paired t (HLN) | 28 | 2.1e-05 | 1.3e-04 |
| C1b | 3 | bridge_c1b | H1 RMSE vs C1 | DM-HLN | 22 | 0.003 | 0.007 |
| C1b | 3 | bridge_c1b | H2 bias vs C1 | paired t (HLN) | 22 | 2.6e-05 | 1.3e-04 |

### C1 verdicts under rule (b)

C1's EVALUATION.md says its wording follows C2's decided rule, now (b) by the erratum. The labels are as defined for C2 above. Development Holm p is in the table above. The ratios are candidate RMSE over benchmark RMSE on the same development targets and on the same holdout instants; the holdout ratio is descriptive. This report computes these verdicts; no frozen code does. C1 issues no intervals, so where every loss condition is met the verdict is "undetermined" (card c3-b-nointv).

Superseded: under rule (a), this report's earlier draft gave 1 "beats" (k = 2 bridge_reg vs no_change).

| k | candidate | benchmark | dev n | dev ratio | holdout n | holdout ratio | verdict (b) |
|---|---|---|---|---|---|---|---|
| 1 | bridge | no_change | 28 | 0.73 | 12 | 0.75 | **comparable** |
| 1 | bridge | ar1 | 28 | 0.78 | 12 | 0.60 | **comparable** |
| 1 | bridge_reg | no_change | 16 | 0.43 | 12 | 1.08 | **does not beat** |
| 1 | bridge_reg | ar1 | 16 | 0.51 | 12 | 0.87 | **comparable** |
| 2 | bridge | no_change | 28 | 0.72 | 12 | 0.76 | **comparable** |
| 2 | bridge | ar1 | 28 | 0.77 | 12 | 0.61 | **comparable** |
| 2 | bridge_reg | no_change | 16 | 0.44 | 12 | 0.89 | **undetermined (no intervals)** |
| 2 | bridge_reg | ar1 | 16 | 0.53 | 12 | 0.72 | **comparable** |
| 3 | bridge | no_change | 22 | 0.76 | 11 | 0.92 | **comparable** |
| 3 | bridge | ar1 | 22 | 0.79 | 11 | 0.75 | **comparable** |
| 3 | bridge_reg | no_change | 10 | 0.54 | 11 | 1.04 | **does not beat** |
| 3 | bridge_reg | ar1 | 10 | 0.59 | 11 | 0.85 | **comparable** |

### C1b: bias (mean error; pre-registered H2)

Mean error in pp (negative: nowcast below the outcome), with its Newey–West lag-1 standard error in parentheses, computed with C1b's own `mean_hac1` on the committed tables. The development values reproduce `bias_dev.csv`; H2's development test is in the next table. The holdout rows are descriptive. The pooled rows are not pre-registered. They count each target quarter up to three times, so their standard errors are understated (skeptic mkt-s46).

| sample | k | n | C1b bridge | C1 bridge | no change |
|---|---|---|---|---|---|
| development | 1 | 28 | −0.13 pp (0.04) | −0.19 pp (0.04) | −0.15 pp (0.07) |
| development | 2 | 28 | −0.12 pp (0.02) | −0.22 pp (0.04) | −0.15 pp (0.07) |
| development | 3 | 22 | −0.13 pp (0.02) | −0.26 pp (0.05) | −0.15 pp (0.09) |
| development | pooled | 78 | −0.12 pp (0.02) | −0.22 pp (0.03) | −0.15 pp (0.05) |
| holdout | 1 | 12 | −0.02 pp (0.05) | −0.04 pp (0.05) | −0.01 pp (0.05) |
| holdout | 2 | 12 | −0.06 pp (0.04) | −0.09 pp (0.04) | −0.01 pp (0.05) |
| holdout | 3 | 11 | −0.05 pp (0.05) | −0.10 pp (0.05) | 0.01 pp (0.07) |
| holdout | pooled | 35 | −0.04 pp (0.03) | −0.08 pp (0.03) | 0.00 pp (0.03) |

## 3. Failure cases: the ten largest errors per horizon

Error = forecast − outcome, in pp of the share; ranked by size. Negative: the forecast was below the outcome.

C2's holdout errors come from the second opening's per-forecast table (deviation D1). With 12 forecasts per horizon, its "ten largest" are nearly the whole holdout. The C1 and C1b holdout has only 12 instants at k = 1 and 2 and 11 at k = 3, so its "ten largest" lists are nearly the whole sample, not a selection of failures. `bridge` (C1's table) and `bridge_c1` (C1b's table) are the same C1 accounting-bridge nowcast.

C2 development, h = 1 (origin T, target T+1):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2021Q2 | 1.83 pp | 2021Q2 | 1.74 pp |
| 2 | 1993Q2 | 1.11 pp | 2004Q2 | 1.14 pp |
| 3 | 2004Q2 | 1.00 pp | 1999Q1 | −0.91 pp |
| 4 | 1999Q1 | −0.98 pp | 2002Q3 | 0.89 pp |
| 5 | 2004Q1 | 0.96 pp | 1993Q2 | 0.88 pp |
| 6 | 1994Q1 | −0.92 pp | 2004Q1 | 0.87 pp |
| 7 | 2002Q1 | −0.80 pp | 2007Q4 | −0.79 pp |
| 8 | 2011Q1 | −0.77 pp | 2004Q3 | 0.74 pp |
| 9 | 2002Q3 | 0.76 pp | 2002Q1 | −0.71 pp |
| 10 | 1994Q2 | 0.68 pp | 1994Q1 | −0.70 pp |

C2 development, h = 4 (origin T, target T+4):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2004Q4 | 5.02 pp | 2004Q4 | 4.63 pp |
| 2 | 1995Q1 | 3.60 pp | 2005Q1 | 3.57 pp |
| 3 | 2005Q1 | 3.57 pp | 2008Q2 | −3.36 pp |
| 4 | 2004Q3 | 3.33 pp | 2008Q3 | −3.00 pp |
| 5 | 2022Q1 | 3.22 pp | 2008Q1 | −2.98 pp |
| 6 | 2008Q2 | −2.75 pp | 2007Q4 | −2.88 pp |
| 7 | 2003Q1 | 2.48 pp | 2022Q1 | 2.81 pp |
| 8 | 2008Q3 | −2.37 pp | 2004Q3 | 2.74 pp |
| 9 | 2007Q4 | −2.28 pp | 2005Q2 | 2.37 pp |
| 10 | 2023Q1 | 2.27 pp | 2007Q3 | −2.36 pp |

C2 development, h = 8 (origin T, target T+8):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2005Q4 | 8.83 pp | 2005Q4 | 7.73 pp |
| 2 | 2005Q3 | 7.36 pp | 2008Q4 | −7.17 pp |
| 3 | 2005Q1 | 6.36 pp | 2009Q1 | −7.11 pp |
| 4 | 2005Q2 | 6.24 pp | 2009Q2 | −7.11 pp |
| 5 | 2009Q2 | −6.13 pp | 2008Q3 | −7.06 pp |
| 6 | 2006Q1 | 6.08 pp | 2008Q2 | −6.70 pp |
| 7 | 2008Q4 | −5.97 pp | 2009Q3 | −6.65 pp |
| 8 | 2023Q1 | 5.89 pp | 2005Q3 | 6.18 pp |
| 9 | 2009Q3 | −5.74 pp | 2008Q1 | −5.83 pp |
| 10 | 2008Q3 | −5.59 pp | 2006Q1 | 5.58 pp |

C2 holdout (second opening, D1), h = 1 (origin T, target T+1):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2024Q1 | −0.32 pp | 2024Q1 | −0.37 pp |
| 2 | 2024Q4 | −0.26 pp | 2026Q1 | −0.28 pp |
| 3 | 2025Q4 | 0.26 pp | 2024Q4 | −0.27 pp |
| 4 | 2026Q2 | 0.26 pp | 2025Q4 | 0.25 pp |
| 5 | 2026Q1 | −0.25 pp | 2025Q2 | 0.22 pp |
| 6 | 2025Q2 | 0.25 pp | 2026Q2 | 0.17 pp |
| 7 | 2024Q2 | 0.18 pp | 2024Q3 | −0.11 pp |
| 8 | 2025Q1 | 0.15 pp | 2025Q3 | 0.08 pp |
| 9 | 2023Q3 | 0.08 pp | 2025Q1 | 0.05 pp |
| 10 | 2024Q3 | −0.06 pp | 2024Q2 | 0.05 pp |

C2 holdout (second opening, D1), h = 4 (origin T, target T+4):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2025Q4 | 1.07 pp | 2024Q4 | −0.89 pp |
| 2 | 2026Q1 | 0.79 pp | 2025Q4 | 0.71 pp |
| 3 | 2024Q4 | −0.66 pp | 2024Q1 | −0.52 pp |
| 4 | 2024Q1 | 0.46 pp | 2024Q3 | −0.52 pp |
| 5 | 2026Q2 | 0.36 pp | 2025Q1 | −0.51 pp |
| 6 | 2025Q1 | 0.27 pp | 2026Q2 | 0.43 pp |
| 7 | 2025Q3 | 0.24 pp | 2026Q1 | 0.41 pp |
| 8 | 2023Q3 | 0.20 pp | 2025Q2 | −0.40 pp |
| 9 | 2024Q2 | 0.16 pp | 2024Q2 | −0.36 pp |
| 10 | 2024Q3 | −0.10 pp | 2023Q3 | 0.29 pp |

C2 holdout (second opening, D1), h = 8 (origin T, target T+8):

| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |
|---|---|---|---|---|
| 1 | 2024Q1 | 3.78 pp | 2023Q3 | 1.71 pp |
| 2 | 2023Q4 | 1.34 pp | 2025Q1 | −1.34 pp |
| 3 | 2026Q1 | 1.29 pp | 2025Q3 | −0.99 pp |
| 4 | 2026Q2 | 0.88 pp | 2025Q2 | −0.96 pp |
| 5 | 2025Q1 | 0.79 pp | 2023Q4 | 0.95 pp |
| 6 | 2023Q3 | 0.75 pp | 2024Q4 | −0.82 pp |
| 7 | 2024Q2 | 0.75 pp | 2025Q4 | −0.81 pp |
| 8 | 2024Q4 | −0.38 pp | 2024Q2 | 0.74 pp |
| 9 | 2025Q2 | 0.36 pp | 2026Q1 | −0.46 pp |
| 10 | 2024Q3 | 0.33 pp | 2024Q1 | 0.36 pp |

C1 development (real time), by instant k (target quarter q):

| k | rank | bridge target | bridge error |
|---|---|---|---|
| 1 | 1 | 2021Q1 | −0.74 pp |
| 1 | 2 | 2020Q3 | −0.52 pp |
| 1 | 3 | 2020Q4 | −0.46 pp |
| 1 | 4 | 2020Q1 | −0.42 pp |
| 1 | 5 | 2017Q1 | −0.39 pp |
| 1 | 6 | 2020Q2 | −0.32 pp |
| 1 | 7 | 2017Q3 | −0.30 pp |
| 1 | 8 | 2021Q3 | −0.30 pp |
| 1 | 9 | 2018Q1 | −0.28 pp |
| 1 | 10 | 2022Q1 | −0.27 pp |
| 2 | 1 | 2021Q1 | −0.64 pp |
| 2 | 2 | 2020Q4 | −0.54 pp |
| 2 | 3 | 2020Q3 | −0.52 pp |
| 2 | 4 | 2021Q2 | −0.40 pp |
| 2 | 5 | 2022Q1 | −0.36 pp |
| 2 | 6 | 2021Q3 | −0.35 pp |
| 2 | 7 | 2020Q1 | −0.32 pp |
| 2 | 8 | 2017Q3 | −0.30 pp |
| 2 | 9 | 2016Q4 | −0.29 pp |
| 2 | 10 | 2017Q1 | −0.27 pp |
| 3 | 1 | 2021Q1 | −0.66 pp |
| 3 | 2 | 2020Q4 | −0.62 pp |
| 3 | 3 | 2021Q2 | −0.52 pp |
| 3 | 4 | 2022Q1 | −0.48 pp |
| 3 | 5 | 2016Q4 | −0.38 pp |
| 3 | 6 | 2021Q4 | −0.38 pp |
| 3 | 7 | 2020Q2 | −0.30 pp |
| 3 | 8 | 2017Q4 | −0.29 pp |
| 3 | 9 | 2019Q4 | −0.25 pp |
| 3 | 10 | 2017Q1 | −0.24 pp |

C1 and C1b holdout (real time), by instant k (target quarter q):

| k | rank | bridge_c1 target | bridge_c1 error | bridge_c1b target | bridge_c1b error |
|---|---|---|---|---|---|
| 1 | 1 | 2024Q4 | −0.39 pp | 2024Q4 | −0.35 pp |
| 1 | 2 | 2024Q3 | −0.18 pp | 2024Q3 | −0.16 pp |
| 1 | 3 | 2025Q1 | −0.15 pp | 2025Q1 | −0.13 pp |
| 1 | 4 | 2024Q1 | −0.12 pp | 2026Q2 | 0.13 pp |
| 1 | 5 | 2026Q2 | 0.12 pp | 2025Q4 | 0.13 pp |
| 1 | 6 | 2023Q4 | 0.10 pp | 2024Q1 | −0.13 pp |
| 1 | 7 | 2025Q4 | 0.09 pp | 2023Q4 | 0.11 pp |
| 1 | 8 | 2023Q3 | 0.07 pp | 2023Q3 | 0.07 pp |
| 1 | 9 | 2025Q3 | −0.06 pp | 2026Q1 | 0.05 pp |
| 1 | 10 | 2026Q1 | 0.04 pp | 2024Q2 | 0.04 pp |
| 2 | 1 | 2024Q4 | −0.44 pp | 2024Q4 | −0.38 pp |
| 2 | 2 | 2024Q3 | −0.20 pp | 2024Q3 | −0.16 pp |
| 2 | 3 | 2023Q3 | −0.10 pp | 2024Q1 | −0.09 pp |
| 2 | 4 | 2024Q1 | −0.09 pp | 2026Q2 | 0.07 pp |
| 2 | 5 | 2024Q2 | −0.08 pp | 2023Q3 | −0.06 pp |
| 2 | 6 | 2025Q1 | −0.07 pp | 2025Q4 | 0.06 pp |
| 2 | 7 | 2025Q3 | −0.07 pp | 2025Q1 | −0.06 pp |
| 2 | 8 | 2026Q2 | 0.06 pp | 2026Q1 | 0.04 pp |
| 2 | 9 | 2023Q4 | −0.06 pp | 2024Q2 | −0.04 pp |
| 2 | 10 | 2025Q2 | −0.03 pp | 2025Q3 | −0.03 pp |
| 3 | 1 | 2024Q4 | −0.55 pp | 2024Q4 | −0.47 pp |
| 3 | 2 | 2024Q3 | −0.16 pp | 2025Q4 | 0.11 pp |
| 3 | 3 | 2024Q2 | −0.11 pp | 2024Q3 | −0.08 pp |
| 3 | 4 | 2023Q3 | −0.09 pp | 2024Q2 | −0.06 pp |
| 3 | 5 | 2023Q4 | −0.06 pp | 2026Q2 | 0.04 pp |
| 3 | 6 | 2025Q3 | −0.06 pp | 2023Q3 | −0.03 pp |
| 3 | 7 | 2024Q1 | −0.05 pp | 2024Q1 | −0.03 pp |
| 3 | 8 | 2025Q2 | −0.05 pp | 2025Q2 | −0.02 pp |
| 3 | 9 | 2025Q1 | −0.04 pp | 2025Q1 | −0.01 pp |
| 3 | 10 | 2025Q4 | 0.02 pp | 2025Q3 | 0.01 pp |

## 4. Results by regime (development sample)

The windows are fixed by the protocol: 2007Q4–2011Q4 ("GFC") and 2020Q1–2020Q4 ("2020"). Both lie in development; the holdout (2023Q3–2026Q2) contains neither. The protocol does not say whether a forecast belongs to a window by its target quarter or by its origin, so both are shown. "Rest" is every development forecast whose split quarter is in neither window; at h = 4 and 8 some of those forecasts have their other quarter (origin or target) inside a window, so "rest" is not a clean calm-period sample. Cells: each model's RMSE divided by no-change's RMSE on the same forecasts (below one: better than no-change); no-change RMSE in pp. ‡ marks fewer than ten forecasts: such cells describe a few quarters and support no general statement. "GFC" is the protocol's 2007Q4–2011Q4 window around the global financial crisis.

| split by | window | h | n | no-change RMSE | Z-DIR | Z-DAMP | AR (BIC) |
|---|---|---|---|---|---|---|---|
| target | GFC (2007Q4–2011Q4) | 1 | 17 | 0.91 pp | 0.39 | 0.45 | 0.39 |
| target | GFC (2007Q4–2011Q4) | 4 | 17 | 3.54 pp | 0.44 | 0.50 | 0.46 |
| target | GFC (2007Q4–2011Q4) | 8 | 17 | 6.65 pp | 0.63 | 0.76 | 0.64 |
| target | 2020 (2020Q1–2020Q4) | 1 | 4‡ | 0.62 pp | 0.59 | 0.70 | 0.59 |
| target | 2020 (2020Q1–2020Q4) | 4 | 4‡ | 1.70 pp | 0.87 | 0.90 | 0.84 |
| target | 2020 (2020Q1–2020Q4) | 8 | 4‡ | 1.92 pp | 0.68 | 0.73 | 0.63 |
| target | rest | 1 | 112 | 0.48 pp | 0.89 | 0.84 | 0.90 |
| target | rest | 4 | 109 | 1.45 pp | 0.88 | 0.83 | 0.87 |
| target | rest | 8 | 105 | 2.59 pp | 0.93 | 0.85 | 0.93 |
| origin | GFC (2007Q4–2011Q4) | 1 | 17 | 0.89 pp | 0.39 | 0.41 | 0.40 |
| origin | GFC (2007Q4–2011Q4) | 4 | 17 | 3.20 pp | 0.38 | 0.33 | 0.38 |
| origin | GFC (2007Q4–2011Q4) | 8 | 17 | 5.76 pp | 0.44 | 0.40 | 0.45 |
| origin | 2020 (2020Q1–2020Q4) | 1 | 4‡ | 0.68 pp | 0.38 | 0.48 | 0.38 |
| origin | 2020 (2020Q1–2020Q4) | 4 | 4‡ | 1.42 pp | 0.95 | 1.11 | 0.91 |
| origin | 2020 (2020Q1–2020Q4) | 8 | 4‡ | 1.11 pp | 2.55 | 2.19 | 2.39 |
| origin | rest | 1 | 112 | 0.48 pp | 0.89 | 0.86 | 0.91 |
| origin | rest | 4 | 109 | 1.57 pp | 0.84 | 0.84 | 0.84 |
| origin | rest | 8 | 105 | 2.93 pp | 0.93 | 0.97 | 0.93 |

Nowcasts. C1's real-time sample starts with target 2016Q3, so it covers 2020 but not the GFC window; the pseudo-real-time sample P2a (not real time) covers only 2010Q2–2011Q4 of it. Split by target quarter.

| task | sample | window | k | n | no-change RMSE | bridge / no-change | C1b bridge / no-change |
|---|---|---|---|---|---|---|---|
| C1 | RT | 2020 (2020Q1–2020Q4) | 1 | 4‡ | 0.60 pp | 0.73 | 0.49 |
| C1 | RT | 2020 (2020Q1–2020Q4) | 2 | 4‡ | 0.60 pp | 0.71 | 0.31 |
| C1 | RT | 2020 (2020Q1–2020Q4) | 3 | 3‡ | 0.62 pp | 0.65 | 0.16 |
| C1 | P2a | GFC (part) (2010Q2–2011Q4) | 1 | 7‡ | 0.66 pp | 0.81 | — |
| C1 | P2a | GFC (part) (2010Q2–2011Q4) | 2 | 7‡ | 0.66 pp | 0.67 | — |
| C1 | P2a | GFC (part) (2010Q2–2011Q4) | 3 | 5‡ | 0.73 pp | 0.67 | — |

## 5. First release against latest vintage

All development-sample origins, from the archived Z.1 release of 2016-09-16 on. Source: `research/c2_forecast/scores_dev.csv` (designs `realtime-vs-first`, `realtime-vs-latest`, `latest-on-realtime-origins`, built from `forecasts_realtime_dev.csv`). The ratios change with the target vintage; this section shows that and does not explain it.

C2 real-time check: origins at each archived Z.1 release from 2016-09-16, with the real-time data of each release. Scored against the first release of the target and against the latest vintage; the third row at each horizon re-scores the same origins with latest-vintage data throughout (the primary design). Cells: RMSE relative to no-change; no-change RMSE in pp.

"First release" means different things here and in C1 (skeptic mkt-s44). C2's real-time target is the target quarter's first-release level minus the origin quarter's level as published at the origin, so it also contains the revision to the origin quarter. C1's target is the change measured within the target quarter's first release. On the same 28 targets the two differ by 0.24 pp RMS, so C2's and C1's first-release scores are not directly comparable.

| h | scoring | n | no-change RMSE | Z-DIR | Z-DAMP | drift | AR (BIC) |
|---|---|---|---|---|---|---|---|
| 1 | real-time data, first-release target | 28 | 0.44 pp | 0.86 | 0.85 | 0.99 | 0.90 |
| 1 | real-time data, latest-vintage target | 28 | 0.43 pp | 1.08 | 1.05 | 0.99 | 1.10 |
| 1 | latest-vintage data and target, same origins | 28 | 0.43 pp | 1.03 | 0.99 | 0.99 | 1.08 |
| 4 | real-time data, first-release target | 25 | 1.17 pp | 0.87 | 0.97 | 0.84 | 0.85 |
| 4 | real-time data, latest-vintage target | 25 | 1.01 pp | 1.24 | 1.26 | 0.95 | 1.20 |
| 4 | latest-vintage data and target, same origins | 25 | 1.01 pp | 1.19 | 1.08 | 0.95 | 1.14 |
| 8 | real-time data, first-release target | 21 | 2.01 pp | 0.99 | 1.06 | 0.63 | 0.95 |
| 8 | real-time data, latest-vintage target | 21 | 1.64 pp | 1.33 | 1.29 | 0.79 | 1.27 |
| 8 | latest-vintage data and target, same origins | 21 | 1.64 pp | 1.25 | 1.21 | 0.79 | 1.19 |

C1: the real-time nowcast scored against the first release (RT, primary) and against the latest vintage (RT-latest).

| k | target | n | no-change RMSE | bridge / no-change |
|---|---|---|---|---|
| 1 | first release | 28 | 0.38 pp | 0.73 |
| 1 | latest vintage | 28 | 0.43 pp | 0.81 |
| 2 | first release | 28 | 0.38 pp | 0.72 |
| 2 | latest vintage | 28 | 0.43 pp | 0.74 |
| 3 | first release | 22 | 0.41 pp | 0.76 |
| 3 | latest vintage | 22 | 0.47 pp | 0.72 |
| pooled | first release | 78 | 0.39 pp | 0.74 |
| pooled | latest vintage | 78 | 0.44 pp | 0.76 |

## 6. Were C1's indicators used?

Yes, in two places. (1) `ZC1-DIR` is C2's `Z-DIR` plus C1's accounting-bridge nowcast as one regressor. It can be scored only where C1's point-in-time panel exists, so its development comparison has few origins (the n column below) and its holdout comparison is on the expanding design only. (2) C1 and C1b are themselves the indicator models; their results are in section 2.

| sample | h | n | ZC1-DIR / no-change | Z-DIR / no-change, same origins |
|---|---|---|---|---|
| development | 1 | 18 | 0.80 | 1.04 |
| development | 4 | 12 | 1.40 | 1.24 |
| development | 8 | 4‡ | 0.96 | 3.49 |
| holdout | 1 | 12 | 1.31 | 1.16 |
| holdout | 4 | 12 | 3.98 | 1.40 |
| holdout | 8 | 12 | 5.34 | 1.90 |

## 7. Deviations and process issues, dated

Each is recorded in full in the file named, except the last two, which come from this report's review and are open cards. The test changes of 2026-11-04 were all made before the holdout was opened. Review ids (mkt-q…, mkt-s…) refer to `claims/tracks/markets-review-log.md`; the earlier C1 ids (q11–q16, s9–s15) to `claims/review-log.md`.

- **2026-11-04, protocol fact correction** (`docs/decisions/scoring-protocol.md`): Z.1 text archives exist before 2016-09; the real-time check still starts 2016-09-16. No design change.
- **2026-11-04, C1 holdout aligned to the protocol** (protocol and `research/c1_nowcast/EVALUATION.md`): C1's holdout is 2023Q3–2026Q2, and its tests are C2's.
- **2026-11-04, C2 test ordering** (`research/c2_forecast/SPECS.md`, accepted by Eleonora): the first development scoring ran before the leakage tests existed. They passed with no code change.
- **2026-11-04, seasonal naive in the Holm family** (SPECS.md, accepted by Eleonora): seasonal-naive comparisons joined the Holm family. The family on record has 42 tests: 28 against no-change and AR plus 14 against seasonal naive. SPECS.md's deviation text says the family grew "from 36 to 42"; that count is wrong (the end count of 42 is right). Found by quant-reviewer (mkt-q39); SPECS.md is left as accepted.
- **Not a deviation, but undocumented:** `ZC1-DIR` has no test at h = 8, because `forecast.py` skips any pair with fewer than 8 development forecasts and that comparison has 4 (mkt-q39).
- **2026-11-04, placebo redefined** (SPECS.md, Eleonora's option (a)): the options were written after the first placebo result was seen, and the card said so. Both placebo versions are in section 1.
- **2026-11-04, C1 rescored after review** (EVALUATION.md, quant-reviewer q11–q16, skeptic s9–s15): fourth instant made k = 4 and not scored; the missing 2017-03-09 release found; like-for-like and HAC-lag-1 sensitivities added. The superseded scores are in section 1 (58a93d8).
- **2026-11-04, C1's declared differences from C2** (EVALUATION.md, q15): a fixed AR(1) benchmark (her choice for C1) instead of BIC order; in the pseudo-real-time samples the bridge regression trains on revised targets with no embargo; C2's leakage test 5 (placebo) and the outcome checks are not implemented for C1.
- **2026-11-04, C2 implementation fixes after review** (SPECS.md, q17–q24): leakage tests through the production code; Clark–West for the nested h = 1 pairs against AR; a lag-8 sensitivity, under which the h = 1 result is not robust. Development scores unchanged; tests changed.
- **2026-11-05, c1b-dev-1 (a)** (protocol, EVALUATION.md, `docs/decisions/c1b-prereg.md`; Eleonora's decision): the first joint holdout run (approval 77460b4) stopped on a target quarter no Z.1 had published, before writing or printing anything. Such instants are now "no target"; the freeze was redone, and the one run used the new approval 432fed0.
- **2026-11-05, erratum: the decision rule is (b)** (`docs/decisions/scoring-protocol-erratum-2026-11-05.md`, Eleonora's c3-rule (b)): the freeze recorded (a) by a coordinator transcription error. The erratum also corrects SPECS.md's Holm split to 28 + 14. Verdicts here are recomputed under (b), with two readings open on cards c3-b-level and c3-b-nointv.
- **2026-11-05, D1: second holdout opening** (`docs/decisions/scoring-protocol-deviations-2026-11-05.md`, Eleonora's c3-errors (b)): one separately gated run of the frozen C2 holdout step (`holdout_forecasts_run.py`, approval ccc1fc6), committed after the deviation. It reproduced the committed holdout scores exactly and wrote only the per-forecast table (8d60d86). Its once-only guard records successful runs only. One earlier invocation, refused by the clean-tree gate before any data was read, is recorded in that commit's message. The two checks compare scores per design and horizon, not single rows. The quant-reviewer's read-only row check found that all 72 outcomes match the 2026-09-11 vintage, and that coverage, MAE, interval scores and CRPS reproduce from the table (mkt-q44).
- **2026-11-05, D2: holdout by target quarter** (same file, Eleonora's c3-hcount (b)): the definition the run used (12 at every h) stands; the origin-based subset (12, 9 and 5) is reported in section 2.
- **2026-11-05, this report:** the regime split is shown both by target and by origin quarter, because the protocol does not say which.

## Sources

`research/c2_forecast/` (`holdout_results.json`, `scores_dev.csv`, `tests_dev.csv`, `coverage_dev.csv`, `forecasts_dev.csv`, `placebo_dev.json` and its version at 0bc647b), `research/c1_nowcast/` (`scores_dev.csv`, `tests_dev.csv`, `nowcasts_dev.csv`, and `scores_dev.csv` at 58a93d8), `research/c1b_nowcast/` (`holdout_results.json`, `nowcasts_holdout.csv`, `scores_dev.csv`, `tests_dev.csv`, `nowcasts_dev.csv`). Second holdout opening: `research/c2_forecast/holdout_forecasts.csv` and `holdout_forecasts_run.json`. Specifications and rules: `docs/decisions/scoring-protocol.md`, its erratum and deviations of 2026-11-05, `docs/decisions/c1b-prereg.md`, `research/c2_forecast/SPECS.md`, `research/c1_nowcast/EVALUATION.md`. Real-time check (section 5): `research/c2_forecast/forecasts_realtime_dev.csv`, `research/c1_nowcast/first_release.csv` and `z1_calendar.csv`. Reviews: `claims/tracks/markets-review-log.md`. Full tables written by this script: `tables/c2_holdout_scores.csv`, `tables/c2_coverage.csv`, `tables/c2_verdicts.csv`, `tables/c2_holdout_origin_subset.csv`, `tables/largest_errors.csv`, `tables/regimes.csv`.
