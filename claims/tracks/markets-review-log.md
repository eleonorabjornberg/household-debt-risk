# Markets track review log

Entries from the markets track after the coordinator's fold of 2026-11-04 (51a0b6a). Same format as `claims/review-log.md`; the coordinator moves them there on merge.

## Status updates to entries already in `claims/review-log.md`

- **R-20261104-mkt-q10**: **Status:** open (design, for Eleonora): Clark–West for nested benchmarks, as-of benchmarks and a pre-registered holdout added to Q-C1 item 6; pre-2019 target vintages stated as needing the Fed archive.

- **R-20261104-coord-q1**: resolved (2026-11-04, by Claude, markets track): catalog-level correction added to METHOD.md "Changes after results" with date and effect (D −0.08 to −0.57); METHOD.md's apportionment sentence and the b1.py docstring corrected.
- **R-20261104-coord-q2**: resolved (2026-11-04, by Claude, markets track): README now compares each levels row with its own EG 5% value (N=7 −5.10; N=8 −5.38 for the dummy row) and states the N=3 heuristic (−3.80) and its untested assumption, naming the rows that reject under it (headline, pre-2022, dummy). Constants stored in results.json with their source.
- **R-20261104-coord-q3**: resolved (2026-11-04, by Claude, markets track): power stated as the 80%-power MDE (about 1.00 pp), benchmarked against the 0.61 pp rise in the mean spread; "any plausible" removed; short-run/long-run assumption and the 1986Q4 fragility noted.
- **R-20261104-coord-q4**: resolved (2026-11-04, by Claude, markets track): reworded to "coincides with the period from 2022Q4 on" (method change and other conditions), with the checks marked as chosen after the first result; Fannie+Freddie row caveated (sub-series overstate 1986Q1–Q3).

## New entries

### R-20261104-mkt-q11 · quant-reviewer · research/c1_nowcast
- **Objection:** Pooling the fourth instant with k = 3 duplicates targets, so the k = 3 tests break the spec's own premise ("one target per quarter, HAC lag 0"). Every Q2 target (June release to late-September release: instants on 15 Jun, Jul, Aug and Sep) enters k = 3 twice, with near-identical forecasts and the same actual. In RT, k = 3 has 25 scored rows but 20 distinct targets. The bridge regression at k = 3 has 13 rows but 11 targets. P2b has 34 rows and 27 targets; P2a has 53 rows and 41 targets. The duplicates also give Q2 pairs double weight in the k = 3 regression's training set. README reports n = 25 and n = 13, and says "25–26 targets per k".
- **Severity:** major
- **Evidence:** nowcast.py `k = min(k_of[q], 3)`; nowcasts_dev.csv, e.g. RT 2019Q2 at t = 2019-08-15 and 2019-09-15, both k = 3; groupby(sample, k, q) counts.
- **Proposed resolution:** Keep one instant per (q, k) in the tests (e.g. the last before the next release), or score the fourth instant as k = 4, descriptive only. Record this as a dated deviation before the holdout run, re-run, and correct the n in the README.
- **Status:** resolved (2026-11-04, by Claude, markets track): one row per target and k; a 4th instant is k=4, kept in nowcasts_dev.csv, not scored or tested. Declared in EVALUATION.md Deviations; the k=3 n is now 22 (RT, with the 2017-03-09 release restored).

### R-20261104-mkt-q12 · quant-reviewer · research/c1_nowcast (README Results)
- **Objection:** The README overclaims the bridge regression. (a) Its scored forecasts are 2020Q1–2023Q2 only (14 quarters, 11 at k = 3). That is one regime (COVID, then rate shock), and it is not the 26-quarter window the bridge is scored on. No-change RMSE there is 0.47 pp, against 0.37 over the full sample. (b) The table puts the regression's 0.43–0.52 (n = 14) beside the bridge's 0.74–0.80 (n = 26). C2 requires the common set of origins. On those 14 quarters, the bridge's relative RMSE is 0.71, 0.72 and 0.82. (c) "Significant after Holm at every k" is one result on the same targets, not three confirmations. (d) The regression's edge comes from carrying the 2017–19 bias into 2020–21. In 2023 its RMSE (0.22) is worse than the bridge's (0.09), because the bias had gone. (e) The Holm family mixes one-sided normal CW p-values with two-sided t(n−1) DM p-values. The result survives CW on t(n−1) (p < 0.01), but the README should say which was used.
- **Severity:** major
- **Evidence:** nowcasts_dev.csv recomputed by year and on the common subset; tests_dev.csv RT rows; scoring-protocol.md "common set of origins".
- **Proposed resolution:** Report every pair on common origins and give the regression's scoring window. Describe the result as one development-period finding on about 14 quarters, descriptive. Drop "at every k" as if it were independent evidence. Add per-year errors.
- **Status:** resolved (2026-11-04, by Claude, markets track): README adds the bridge scored on the regression's own targets (0.72–0.86), states the 2019Q3–2023Q2 span and that it includes the 2020–21 bias, and says the per-k results are the same targets, not independent. After the q11 fix the regression is Holm-significant at k=1 and 2 only.

### R-20261104-mkt-q13 · quant-reviewer · research/c1_nowcast (README bias)
- **Objection:** The bias statement and its explanation are incomplete. The bias is robust to autocorrelation (Newey–West, 3 lags: t = −3.0, −4.1, −4.5 at k = 1, 2, 3). It is not stable over time, though. At k = 1 it is −0.13 to −0.19 pp in 2017–19, −0.43 in 2020, −0.33 in 2021, and about 0 in 2022–23. By quarter of year it is −0.33 (Q1), −0.05 (Q2), −0.24 (Q3) and −0.11 (Q4). That pattern also fits a second explanation: NSA cells carried flat through seasonal swings. The "agency pools carried flat" story has a rival, and the bias's disappearance from 2022 matters for any intercept-corrected model in a 2023Q3+ holdout.
- **Severity:** moderate
- **Evidence:** nowcasts_dev.csv, RT, bridge minus first-release actual, grouped by year and by quarter.
- **Proposed resolution:** Report the bias by year and by quarter of year. Run an ex-post decomposition of the bridge error by cell on development data (first-release growth of the carried cells), which is cheap and needs no new data. Present both explanations as untested.
- **Status:** resolved (2026-11-04, by Claude, markets track): bias by period reported (2020–21 −0.40 pp; to 2019 −0.18; 2022–23 −0.09) and the NSA-seasonality rival named; neither explanation tested.

### R-20261104-mkt-q14 · quant-reviewer · research/c1_nowcast
- **Objection:** The lag-0 variance in DM-HLN and Clark–West rests on h = 1 errors being serially uncorrelated within k. They are not. The bridge's first-order error autocorrelation is 0.38, 0.65 and 0.72 at k = 1, 2, 3. The loss differential against no-change has ρ1 ≈ 0.21 at k = 1, the k with the smallest raw p (0.018). The CW adjusted term has ρ1 ≈ 0.24 at k = 1. With the persistent bias, lag 0 understates the standard errors.
- **Severity:** moderate
- **Evidence:** nowcast.py dm_hln and clark_west (formulas otherwise correct: HLN factor √((n−1)/n), t(n−1); CW adjustment e_s² − (e_b² − (f_s − f_b)²)); recomputed autocorrelations.
- **Proposed resolution:** Keep lag 0 as pre-registered, and add a declared sensitivity with Newey–West lag 1–2 (or a block bootstrap). State that the p-values are descriptive.
- **Status:** resolved (2026-11-04, by Claude, markets track): post-hoc DM with Newey–West lag-1 variance added (tests_dev.csv posthoc_dm_hac1_p), declared, not used for wording; README notes lag-0 p-values are, if anything, too small.

### R-20261104-mkt-q15 · quant-reviewer · research/c1_nowcast (agreement with C2)
- **Objection:** Some departures from the frozen C2 protocol are undeclared. (a) In P2a and P2b, the bridge regression trains on latest-vintage (2026-09-11) actuals, dated as published at their first release. That builds revisions into the training pairs. C2 sets an embargo of e = 4 for latest-vintage training. EVALUATION.md waives the embargo "since real-time vintages make an embargo unnecessary", which is true only for RT. (b) C2 decision (c) requires guard tests 1–4 plus outcome checks 1 and 5 (in-sample error collapse with the guard off; a placebo on a shuffled target). C1 has only guard tests 1–3, though its heading says "tests 1–4". (c) EVALUATION.md calls AR(1) "as in C2's primary design". C2's AR order is chosen by BIC over 0–4. AR(1) is Eleonora's C1 item 5, so this is a C1/C2 difference to declare.
- **Severity:** moderate
- **Evidence:** EVALUATION.md "Bridge regression", "Leakage guards", "Benchmarks"; scoring-protocol.md purge/embargo, leakage tests, AR order.
- **Proposed resolution:** Either apply e = 4 to the P2 regression or label it as using revised targets. Add the fit-window, outcome and placebo tests. Record (a)–(c) as dated deviations before the holdout run.
- **Status:** resolved (2026-11-04, by Claude, markets track): declared in EVALUATION.md Deviations: fixed AR(1) per Eleonora's Q-C1 item 5 (C2 uses BIC); pseudo-real-time regressions train on revised targets; C2 tests 4–5 and outcome checks not implemented for C1 (left to C2).

### R-20261104-mkt-q16 · quant-reviewer · research/c1_nowcast
- **Objection:** Minor reproduction and wording issues. (a) A re-run reproduces scores_dev.csv, tests_dev.csv and results_dev.json byte for byte. nowcasts_dev.csv changes column order between runs, because the `latest_*` columns come from iterating a set (string hash randomisation), so every regeneration shows a spurious diff. (b) EVALUATION.md lists only 2016Q4 as excepted from the RT development targets. 2017Q1 is lost too, because its base release (2017-03-09) has no CSV. The README states this correctly.
- **Severity:** minor
- **Evidence:** Re-run on 2026-11-04 compared against commit 58a93d8. nowcast.py `for sid in set(mapping.values()) | {CC_TOTAL}`.
- **Proposed resolution:** Iterate in sorted order. Note 2017Q1 in EVALUATION.md (as a deviation).
- **Status:** resolved (2026-11-04, by Claude, markets track): column order made deterministic (sorted indicators, commit 1e095be); EVALUATION.md updated for the 2017 release (now not lost, see mkt-s9).

### R-20261104-mkt-s9 · skeptic · research/c1_nowcast
- **Objection:** The 2016Q4 Z.1 release (2017-03-09) is not missing from the Fed archive. It sits in a folder named for a different date: `/releases/z1/20170305/z1_csv_files.zip`, which is linked from `release-dates.htm`. `z1_vintages.fetch` builds the URL from the release date, so it got a 404 and recorded the release as absent. The RT sample therefore loses its three instants based on that release and the 2016Q4 first-release target. The README line "has no archived CSV", the EVALUATION.md "Missing release" rule, `z1_vintage_notes.csv` and `test_first_release_has_no_quarter_from_missing_release` all rest on a false premise.
- **Severity:** major
- **Evidence:** `curl -I .../z1/20170309/z1_csv_files.zip` → 404; `.../z1/20170305/z1_csv_files.zip` → 200 (6,249,231 bytes, members dated 2017-03-08, l222 ends 2016:Q4). `z1_vintages.vintage_cells(<that zip>)` parses with the same codes (cc_depository=FL763066000) and gives a 2016Q4 share of 0.532866. Every other calendar date matches its Fed folder name.
- **Proposed resolution:** Take each release's folder from `release-dates.htm` instead of its date. Add 2017-03-09 and rerun z1_vintages.py. Because the absence was pre-registered, record the fix as a dated deviation in EVALUATION.md before re-scoring, and report the RT numbers both ways.
- **Status:** resolved (2026-11-04, by Claude, markets track): confirmed: folder 20170305 holds the 2017-03-09 release (last quarter 2016Q4, share 0.5329; 6249231 bytes, sha256 1b730b3a…). z1_vintages.FOLDER_OVERRIDE with an assert on the last quarter; test changed to require 2016Q4 from that release; all 41 releases parse; RT rescored. Declared in Deviations.

### R-20261104-mkt-s10 · skeptic · research/c1_nowcast/z1_vintages.py
- **Objection:** The alias description is wrong, though the alias itself is sound. The old code FL763066000 is not a "2016 table" code: it is used in every parsed release from 2016-09-16 to 2025-06-12. FL763066005 replaces it only from 2025-09-11. Only one holder in CELLS has an alias, not "two". The other code change at that release (FL103066005 → FL103066003, nonfinancial corporate business) falls in the residual.
- **Severity:** minor
- **Evidence:** In the data dictionaries of 20250612 and 20250911, both codes are labelled "U.S.-chartered depository institutions; consumer credit; asset" on L.222 line 7. Values agree where the two releases overlap: 2023Q2 is 2,033,983 under both codes, and 2025Q1 is 1,949,773 vs 1,949,329 (an ordinary revision). See `z1_vintage_notes.csv` lines 2–37.
- **Proposed resolution:** Correct the docstring and the CELLS comment to "code renamed at 2025-09-11; label and line unchanged; values checked equal on overlap".
- **Status:** resolved (2026-11-04, by Claude, markets track): docstring corrected: the depository consumer-credit code changed to FL763066005 with the 2025-09-11 release.

### R-20261104-mkt-s11 · skeptic · research/c1_nowcast/README.md (Results; c1_rt_k*_relrmse_bridge_reg)
- **Objection:** The table and bullets compare the bridge regression (0.43, 0.45, 0.52) with the bridge (0.74, 0.74, 0.80) as if both were scored on the same targets. They are not. The regression is scored only on targets 2020Q1–2023Q2 (2020Q2 for k=3), where no-change errors are about 2.5 times larger. On those same targets the bridge's relative RMSE is 0.71, 0.72 and 0.82. "About half of no-change's" holds for a COVID-era subsample, not for the 2016–2023 sample the table header implies.
- **Severity:** major
- **Evidence:** On nowcasts_dev.csv RT rows, at k=1: no-change RMSE is 0.47 pp on the regression's targets and 0.19 pp on the earlier ones. The bridge's relative RMSE is 0.706 on the regression's subset and 0.933 on the rest. The bridge's mean error on that subset is −0.21/−0.27/−0.34 pp, against −0.00/−0.07/−0.11 for the regression.
- **Proposed resolution:** State the regression's target window in the table. Add the bridge's relative RMSE on the same targets, or footnote that the two columns cover different periods.
- **Status:** resolved (2026-11-04, by Claude, markets track): see mkt-q12.

### R-20261104-mkt-s12 · skeptic · research/c1_nowcast/nowcast.py MAP_2B (mort_banks → RREACBW027NBOG)
- **Objection:** The H.8 indicator measures a different population from its Z.1 cell. It covers all commercial banks, including foreign-related ones, and excludes savings institutions. FL763065105 covers U.S.-chartered depository institutions, thrifts included. H.8 levels are also not adjusted for structure breaks such as charter conversions, and the series is read at the last Wednesday on or before quarter end rather than at quarter end. The share error this causes is small (about 0.03 pp), but README line 20 presents the mapping as clean. The other mappings checked out: there is no SA/NSA mixing (all six indicators are NSA), H.8 weekly values are Wednesday levels, not averages, and the G.19 cells equal their Z.1 cells exactly.
- **Severity:** minor
- **Evidence:** In the latest vintages, 2015Q1–2023Q2, H.8 minus Z.1 (household-apportioned) quarterly log growth has a mean of +0.11 pp, an RMSE of 0.33 pp and a correlation of 0.96. The largest gaps are 0.88 (2017Q4), 0.74 (2015Q3) and 0.64 (2015Q4). The weekly H.8 series jumps 1.24% on 2015-11-04 and 1.12% on 2018-05-16. TOTALGOV, TOTALDI, TOTALFC, TOTALTCU and TOTALNS against their Z.1 cells give a level ratio of 1.000 and a growth RMSE of 0.00 pp.
- **Proposed resolution:** Add a caveat on the coverage difference and the unadjusted breaks. If it is pre-registered, consider the H.8 break-adjusted flows.
- **Status:** open (minor, accepted as a stated limitation): H.8 all-commercial-bank coverage and structure breaks differ from the Z.1 U.S.-chartered depository cell; effect on the share estimated by the skeptic at about 0.03 pp; not adjusted.

### R-20261104-mkt-s13 · skeptic · research/c1_nowcast/README.md (bias by k)
- **Objection:** k=3 is not "the third instant" for every target. In 2016–2021 the Q3 Z.1 release came after the 15th of September. Six Q3 targets therefore have no k=3 row, while five Q2 targets have two k=3 rows, one of them six days before the release. As a result, "−0.18 at k=1, −0.26 at k=3" compares different sets of targets, and the k=3 tests carry duplicate, dependent pairs. The pooling is documented in EVALUATION.md, but the README does not mention it. The conclusion holds on matched targets.
- **Severity:** minor
- **Evidence:** RT k=3 has 25 scored rows: 20 true third instants and 5 fourth instants. On the 20 targets that have k=1, 2 and 3, the mean error is −0.15, −0.20 and −0.26 pp, and the relative RMSE is 0.65, 0.65 and 0.78.
- **Proposed resolution:** Add one sentence to the README, and add a matched-target row as a descriptive check.
- **Status:** resolved (2026-11-04, by Claude, markets track): see mkt-q11; bias by k now uses one row per target and k.

### R-20261104-mkt-s14 · skeptic · research/c1_nowcast/sources.md
- **Objection:** The archive-depth table rests partly on date errors. 2011-09-28 is not a Z.1 release date: the calendar and the Fed archive both give 2011-09-16, and `20110916/z1r-1.zip` returns 200, so the "to recheck" 404 is explained. "CSV from 2017" should read "from 2016-09-16". The 2017-03 release folder is 20170305 (see mkt-s9).
- **Severity:** minor
- **Evidence:** `curl -I .../z1/20110916/z1r-1.zip` → 200; the folder list in `release-dates.htm`.
- **Proposed resolution:** Correct the dates and the table row.
- **Status:** resolved (2026-11-04, by Claude, markets track): sources.md: CSV archive from 2016-09-16 (not 2017); the 2011-09-28 probe date explained (an HHMSDODNS ALFRED vintage, not a Z.1 release; release is 2011-09-16); archive manifest section added.

### R-20261104-mkt-s15 · skeptic · claims/tracks/markets.csv (c1_*)
- **Objection:** The `series_ids` column omits cells that the bridge moves or that feed the residuals: FL763065105, FL763066000/FL763066005, FL613066005 and FL473066000. The P2a rows list the indicators of set 2b, although P2a uses only TOTALGOV and TOTALNS. Displays and values match results_dev.json at display precision in all 29 rows.
- **Severity:** minor
- **Evidence:** `grep '^c1_' claims/tracks/markets.csv`, compared with z1_vintages.py CELLS and nowcast.py MAP_2A.
- **Proposed resolution:** Complete `series_ids`, and give the P2a rows their own list.
- **Status:** resolved (2026-11-04, by Claude, markets track): C1 register rows regenerated with the full cell code list (FL763065105, FL763066005/FL763066000, FL613066005, FL473066000 added); signs checked by script.
