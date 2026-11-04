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

### R-20261104-mkt-s16 · skeptic · research/c1_nowcast → research/b2_crt_pricing (EL engine, annualisation)
- **Objection:** `tranche_el_bp` divides cumulative slice loss by the average outstanding balance times 10 years, so EL is bps per year of *outstanding* balance (about CDR x LGD = 5.0 bps), not "a share of original UPB" as METHOD.md item 2 says. The credit cost is bps per year of reference UPB, which does not shrink with the pool (the tranche is locked out or amortises slowly). On original UPB the full-pool EL is 30.8 / 10 = 3.08 bps a year, and the median multiple is about 10.4, not 6.4. The headline "6.4 times (5.0 to 8.6)" mixes two denominators. Because every zero-attach deal has the same EL (the baseline loss 31 bps is below every detach point), the "range" is just the range of c divided by a constant. It carries no information about pricing per unit of risk across deals.
- **Severity:** major (headline number depends on an undocumented choice, 6.4 vs 10.4)
- **Evidence:** b2.py `return 1e4 * slice_loss / (avg_bal * years)`; METHOD.md item 2 "Annualising"; recomputed median of credit_cost_bp / (30.82/10) over zero-attach deals = 10.38; results.json el_full_pool_bp_per_year = 5.0046.
- **Proposed resolution:** State the denominator in README and register, show both footings (or use tranche-level units: annual EL as % of tranche notional vs the implied spread), and drop "range 5.0 to 8.6" as evidence of anything beyond c's range. Date the change in METHOD.md.
- **Status:** resolved (2026-11-04, by Claude, markets track): both EL bases reported: outstanding (main; guarantee fees accrue on the outstanding balance, and mkt-s18 shows the cost is on the fee footing) gives median multiple 6.4, original-UPB basis 10.4; README states that the multiple range is the cost range because all zero-attach slices share one EL.

### R-20261104-mkt-s17 · skeptic · research/b2_crt_pricing (cost per dollar sold, 4.0-10.1%)
- **Objection:** The headline "cost per dollar of bonds sold 4.0-10.1% a year" divides FHFA's cost, which assumes the whole tranche (detach minus attach) is sold, by the bonds actually sold. For zero-attach deals sold is only 48-84% of the tranche (median 63%). FHFA's own note says a 100% sale is hypothetical. The caveat is stated but the figure is still shown as a headline, and the bias is not constant over time. Sold / tranche falls over the period, so part of the 2014 to 2016 rise (4.0 to 10.1) is the retention share, not price. On FHFA's own base (tranche size = (detach - attach) x UPB) the series is 3.3, 4.6, 5.3, 6.9%.
- **Severity:** major
- **Evidence:** recomputed from deals.csv: sum(annual_cost_musd) / sum((detach-attach)/1e4 x ref_upb) by year = 4.63 (2013), 3.28 (2014), 5.29 (2015), 6.86 (2016); sold/tranche for attach = 0: min 0.48, median 0.63, max 0.84. README line 31 "investors earned about 4.0-10.1%".
- **Proposed resolution:** Replace by the consistent base (cost / tranche size), or show both and do not call the sold-based figure "what investors earned". The register note "Overstated where the Enterprise retained part" needs a magnitude (up to about 1.5x in 2016).
- **Status:** resolved (2026-11-04, by Claude, markets track): price now per dollar of tranche on FHFA's 100%-sold basis (3.3–6.9% a year by year); sold share of tranche (68–82%) reported for context.

### R-20261104-mkt-s18 · skeptic · research/b2_crt_pricing (cost_share_of_est_gfee, 57%)
- **Objection:** "Credit cost about 57% of the estimated guarantee fee" is an accounting identity, not a finding. FHFA's footnote builds the guarantee fee as credit cost + TCCA 10 + G&A 7 + residual 4 or 13. In all 21 rows with both, est_gfee - credit_cost is exactly 21 (11 rows) or 30 (10 rows). The ratio is cost / (cost + 21 or 30). It also settles the unit question: the cost is bps a year on the same footing as the fee (METHOD.md still calls this an assumption, and the README repeats it). The share is not independent evidence about CRT being "expensive".
- **Severity:** minor (framing) / major if used as evidence of price
- **Evidence:** `deals.csv`: (est_gfee_bp - credit_cost_bp).value_counts() gives 21: 11, 30: 10. FHFA report p.13 footnote 2/3 (pdftotext lines 521-526).
- **Proposed resolution:** Describe it as a decomposition by construction, or drop it. Upgrade the unit from "assumption" to "consistent with the fee decomposition", citing the footnote. The unit is still bps a year of loan balance, not tranche notional.
- **Status:** resolved (2026-11-04, by Claude, markets track): identity asserted in b2.py (fee − cost ∈ {21, 30} bps on every row); "share of guarantee fee" figure dropped; unit stated as bps a year on the fee footing.

### R-20261104-mkt-s19 · skeptic · research/b2_crt_pricing/README.md ("Investors were paid", cause of the 2016 rise)
- **Objection:** (a) "Investors were paid several times FHFA's own baseline expected loss" reads as realised payments. The cost is a model-implied ex-ante figure at issuance under a hypothetical scenario, and no realised loss or return is shown. (b) "The weighted cost rose ... as the GSEs began selling the first loss, which costs more" is causal and uses only the CAS half of FHFA's explanation. For STACR FHFA says costs rose "primarily due to widening spreads in the credit markets" and then moderated, which is a market-price effect. The year weights also mix the zero-attach share, deal size and spread level. Nothing separates them. (c) The same reading of the baseline as "expected loss" gives a "risk premium" label that the METHOD already says cannot be separated from beliefs about losses.
- **Severity:** major
- **Evidence:** README lines "Result" and "By issue year"; FHFA report p.13-14 intro paragraphs (pdftotext lines 485-487 and 536-537).
- **Proposed resolution:** Say "FHFA's issuance-date estimate of the cost implies...". Quote both FHFA explanations and mark the composition effect (zero-attach share by year) as descriptive. No "because". Do not write "paid".
- **Status:** resolved (2026-11-04, by Claude, markets track): "investors were paid" replaced by "priced at … ex-ante model estimates, not realised payments"; both FHFA reasons for 2016 quoted (CAS first-loss sale; STACR spread widening).

### R-20261104-mkt-s20 · skeptic · research/b2_crt_pricing (coverage: "14 of 14", priced share, A2 tie)
- **Objection:** n_deals counts come from the cost table, so STACR 2015-DNA1 and 2015-HQ2 (removed by FHFA for seasoned collateral, in the deal table at 31,876 and 2015-HQ2) are not in the denominator. "2015: 14 of 14 deals priced" is really 14 of 16 in FHFA's deal table. "Priced share of CRT reference UPB" (80%, 71%) also divides by A2's `annual_ref_upb_musd`, whose year attribution and inclusion of the removed deals, CIRT and ACIS were not reconciled here. Where the CRT year is the same, the claim holds only if A2's dates are issue dates. 2016: CAS 2016-6 has no printed cost, so 2016 weighted cost and sold exclude the largest... a 33,124 UPB deal, which may bias the year.
- **Severity:** minor
- **Evidence:** fixture lines `STACR 2015-DNA1 04/28/15 31,876`; `2016-6 11/09/16 0/400` with blank cost (pdftotext line 515); EXPECTED_ROWS stacr_deals 25 vs stacr_cost 23; register b2_2015_n_priced.
- **Proposed resolution:** Report n priced of n in the deal tables, or label "of the deals FHFA priced". Note that the exclusion removed seasoned deals that FHFA says lower the implied cost, so the pricing level is biased up. Say whether A2 uses the same year definition.
- **Status:** resolved (2026-11-04, by Claude, markets track): "deals priced" defined (cost-table deals with a printed cost; the two seasoned STACR deals FHFA excluded are not counted; CAS 2016-6 blank); A2 tie stated as not reconciled deal by deal.

### R-20261104-mkt-s21 · skeptic · research/b2_crt_pricing (join and dates)
- **Objection:** I checked the two nameless deal rows and the one date mismatch. The join is sound but fragile. CAS 2016-3 (1) and (2) share attach/detach 0/400 and the same date, so the fallback "name is NaN, same attach/detach" works only because (2) is named. The match of cost 31 to UPB 11,862 and cost 32 to UPB 25,391 rests on row order, not on printed identifiers. The one date disagreement (STACR 2016-DNA1: 01/21/16 in the deal table, 01/01/16 in the cost table) is a typo in FHFA's cost table. The code keeps the deal-table date, which is right, and flags it, but only the year is used so it cannot affect results.
- **Severity:** minor
- **Evidence:** pdftotext lines 206-207 (unnamed row UPB 11,862, 397 sold; named (2) 25,391, 769), 511-512, 556; deals.csv date_tables_disagree = 1.
- **Proposed resolution:** Add the order assumption to sources.md. Check the (1)/(2) assignment against Fannie Mae's CAS 2016-C03 offering documents when reachable. Swapping would change per-deal annual cost only by (31-32) x the difference in UPB, about 0.1 bn a year; no year-level headline moves at display precision.
- **Status:** resolved (2026-11-04, by Claude, markets track): nameless-row match now also asserts date agreement; the 2016-DNA1 date mismatch kept as published and flagged.

### R-20261104-mkt-s22 · skeptic · research/b2_crt_pricing (register rows)
- **Objection:** (a) `b2_multiple_*`, `b2_baseline_el` and `b2_cost_share_gfee` are tied to the choices in s16 and s18. The display "6.4" is stable under the stated engine but not under the alternative footing (10.4). (b) `b2_cost_zero_attach`, `b2_cost_pos_attach` and all counts are marked UNVERIFIED although the transcription was checked against rendered pages. The statuses may be right, but the validation column is empty. (c) `b2_per_sold_lo/hi` and `b2_20xx_per_sold` display the headline of s17. (d) The `b2_2014_n_priced` and `b2_2015_n_priced` rows cite README lines 27-28 together. Line refs for `b2_baseline_cum_loss` (15) were not checked against the final README.
- **Severity:** minor
- **Evidence:** `grep '^b2_' claims/tracks/markets.csv`; displays match results.json at display precision (6.39->6.4, 0.101->10.1%, 30.82->31) in the rows I recomputed.
- **Proposed resolution:** After s16/s17 are settled, regenerate the rows, add the engine footing to the notes, and recheck the line numbers.
- **Status:** resolved (2026-11-04, by Claude, markets track): B2 register rows regenerated from results.json after the fixes; derived quantities marked ESTIMATE.

### R-20261104-mkt-q17 · quant-reviewer · research/c2_forecast (leakage tests 1-4 and 5)
- **Objection:** Under passing rule (c), the guard tests do not test the harness. (1) Z.1 data carry no `available_at`. `feature_check` only runs inside `lags()`, on quarters that `lags()` builds itself. Test 1 trips only because the leaky function in the test calls `feature_check(s + 4, s)` itself, so the test is circular: a real leaked `extra` passes `pairs()` with no error, as the outcome test shows. (2) Tests 2 and 3 call C1's `growth_from_rows` directly. The production path (`indicator_growth`, through `Bridge.at`) filters rows by `realtime_start <= t` first, so its guard can never trip. Test 2 is test 3 with a later date, not a vintage mismatch. The one real latest-vintage input in the harness, the Z.1 cells in `Bridge.at` (see q22), trips nothing. (3) Test 4 passes a hand-made list to `fit_window_check`. It never fits a scaler, seasonal factor or AR order on all data through the code. (4) The synthetic placebo test only asserts rel. RMSE > 0.9. The failing real-data placebo (0.961) would pass it. The tests were also written after the first scoring run, which is a protocol deviation not yet entered in the protocol's Deviations section.
- **Severity:** blocker
- **Evidence:** test_forecast.py lines 30-36, 58-74, 105-107; forecast.py `lags`, `pairs`, `Bridge.at`; c1_nowcast/nowcast.py lines 74-76 (pre-filter before `guard`).
- **Proposed resolution:** Attach `available_at` to every datum the harness reads: Z.1 shares and cells by release date, ALFRED rows by `realtime_start`. Assert at the point of use in `pairs`, `f_zdir` and `Bridge.at`. Make each test inject the leak through the production entry points (`backtest_latest`, `Bridge.at`, `ar_bic`). Make the placebo unit test use the protocol criterion. Log the ordering as a dated deviation through the coordinator. C2 is not done until then, per the protocol.
- **Status:** resolved (2026-11-04, by Claude, markets track): leakage tests 1–4 rewritten to go through production paths (pairs/f_zdir feature check; indicator_growth_pit with a broken as-of filter; embargo broken inside pairs/ar_bic/drift); test-1 outcome check switches the production guard off. The ordering issue is recorded as a PROPOSED deviation for Eleonora (SPECS.md).

### R-20261104-mkt-q18 · quant-reviewer · research/c2_forecast (placebo, leakage test 5)
- **Objection:** The placebo failure comes from how the protocol defines the placebo, not from a harness leak. Shuffling y keeps its mean, so OLS gives an intercept near the mean h-change and slopes near 0. The placebo is therefore the drift forecast. Its rel. RMSE vs no-change is 0.961 / 0.964 / 0.966, against drift's 0.962 / 0.951 / 0.950. Against no-change, any model with an intercept "has skill" because the share trends. The placebo also uses one permutation (seed 0), so the p-value comes from a single draw.
- **Severity:** major
- **Evidence:** placebo_dev.json; scores_dev.csv (latest-expanding, drift rows); forecast.py `placebo`.
- **Proposed resolution:** Agree a dated protocol deviation with the coordinator and Eleonora before rescoring: measure placebo skill against drift, or demean the target in each training window. Use many permutations (e.g. 200) and report the share of permutations with CW p < 0.05. Until then, test 5 stands as failed. The write-up should state that CW wins over no-change partly reflect the drift.
- **Status:** open (for Eleonora): agreed that it is a definition problem; options stated in SPECS.md (stated after the result was seen); nothing changed, as the coordinator asked.

### R-20261104-mkt-q19 · quant-reviewer · research/c2_forecast (Z-DIR vs AR at h = 1 is nested)
- **Objection:** At h = 1, Z-DIR is OLS of d(s+1) on an intercept and d(s..s-3). AR(p) is fitted by the same estimator on the same sample (targets 1953Q2 to T-4; BIC picks p in {1, 2, 3} at every origin). So AR is nested in Z-DIR, and the protocol requires Clark-West, not DM-HLN. SPECS says "Candidates are not nested" against AR, which is wrong for Z-DIR at h = 1. The choice matters: CW gives one-sided p = 0.015 (expanding) and 0.0125 (rolling), against DM-HLN's 0.19 and 0.31. The h = 4 and 8 pairs (direct vs iterated) and Z-DAMP vs AR are not nested.
- **Severity:** major
- **Evidence:** forecast.py `pairs`/`ar_bic` sample bounds; forecasts_dev.csv ar_p counts at h = 1 (expanding: p=1: 21, 2: 103, 3: 9); CW recomputed from forecasts_dev.csv.
- **Proposed resolution:** Use CW for Z-DIR vs ar_bic at h = 1 in both designs, rerun Holm, and correct SPECS's nesting section. This is a correction to match the protocol, not a deviation.
- **Status:** resolved (2026-11-04, by Claude, markets track): Clark–West for Z-DIR and ZC1-DIR vs AR at h=1 (nested). Z-DIR vs AR h=1: p 0.015, Holm 0.41.

### R-20261104-mkt-q20 · quant-reviewer · research/c2_forecast (HAC lag h-1; lrv fallback)
- **Objection:** HAC lag h-1 matches the protocol, but its assumption fails in the data. The CW loss differential vs no-change at h = 1 has autocorrelation 0.75 at lag 1 and still 0.40 at lag 5. At h = 4 it is 0.57 at lag 4, beyond the h-1 = 3 window. Squared changes cluster (2008-11, 2020), so the differential is not a martingale difference even near the null. The headline h = 1 p-values depend on the bandwidth. With Bartlett lag 8, Z-DIR goes from p = 2.8e-10 to 0.0037, and Z-DAMP from 6e-11 to 0.003. Times m = 42, that no longer passes Holm at 5%. `lrv()` fallback: the rectangular estimate was positive in every pair, so the Bartlett switch never fired. Even so, a kernel switch that depends on the data is not in the protocol or SPECS. At h = 1 a zero variance would divide by zero.
- **Severity:** major
- **Evidence:** loss-differential autocorrelations and Newey-West sensitivity recomputed from forecasts_dev.csv (latest-expanding); forecast.py `lrv`, `clark_west`.
- **Proposed resolution:** Keep lag h-1 as the primary. Report a declared bandwidth sensitivity (e.g. Bartlett at 4 / 8 / 12, or a block bootstrap), and treat the p-values as descriptive where the two disagree. Write the fallback into SPECS.
- **Status:** resolved (2026-11-04, by Claude, markets track): post-hoc Bartlett lag-8 p-values added (posthoc_p_bartlett8); lag h−1 stays primary as frozen; SPECS states the headline is not robust to bandwidth.

### R-20261104-mkt-q21 · quant-reviewer · research/c2_forecast (Holm family)
- **Objection:** The Holm family is neither the frozen one nor fixed in advance. (a) Seasonal-naive comparisons were added (m = 42, not 36), but the protocol's Deviations section does not record this. SPECS's header still says "there are none". (b) An undeclared rule (n < 8) silently drops ZC1-DIR at h = 8. ZC1 is not run under rolling at all. (c) m therefore depends on what data are present. Rerunning with --no-c1 gives m = 36 and changes 13 adjusted p-values, e.g. Z-DIR vs no-change at h = 4 goes from 0.097 to 0.082. (d) One-sided CW p-values are pooled with two-sided DM p-values, but H2 is one-sided.
- **Severity:** moderate
- **Evidence:** tests_dev.csv; rerun with --no-c1 compared with committed outputs (forecasts and raw p identical, p_holm differs); forecast.py `tests`.
- **Proposed resolution:** Enter the family in the protocol's Deviations section through the coordinator, listing every member, before any further scoring. Members that cannot be computed stay in m with p = 1, or are dropped by a written rule. Use one-sided DM to match H1/H2, or state why not.
- **Status:** resolved (2026-11-04, by Claude, markets track): --no-c1 now writes *_noc1 files only; the family on record is the full run (42 tests, seasonal naive PROPOSED).

### R-20261104-mkt-q22 · quant-reviewer · research/c2_forecast (ZC1-DIR bridge feature)
- **Objection:** The indicator side is point-in-time, and I found no look-ahead there. `indicator_growth` uses ALFRED rows known at rel_of[s], and s <= T-5, so the training features predate the origin. The origin feature uses rel_of[T]. But `Bridge.at` takes the Z.1 cells for every s from the 2026-09-11 vintage (`cells_at(LATEST, s)`). The bridge output therefore embeds holder composition revised after the date of the feature. The protocol says C1 features are "always read point-in-time". Cell vintages exist from 2016-09-16. Separately, 6 parameters are fitted on 12-18 pairs. The h = 1 test (n = 18, origins 2018Q4-2023Q1, which include COVID) gives Holm p = 0.030, and the h = 4 test uses n = 12. Neither can carry inference.
- **Severity:** moderate
- **Evidence:** forecast.py `bridge_feature` docstring and `Bridge.at`; c1_nowcast `Z1.cells_at`, `release_at`; tests_dev.csv ZC1 rows.
- **Proposed resolution:** Label ZC1-DIR "not real-time (latest-vintage Z.1 cells)" wherever it appears, or use `release_at(rel_of[s])` cells where vintages exist. Report the ZC1 tests as descriptive.
- **Status:** resolved (2026-11-04, by Claude, markets track): labelled: the Z+C1 bridge uses latest-vintage cells (pseudo-real-time), with point-in-time ALFRED inputs; no real-time Z+C1 run.

### R-20261104-mkt-q23 · quant-reviewer · research/c2_forecast (what tests_dev.csv supports)
- **Objection:** Limits on any write-up. (1) Decision rule (a) needs the holdout, so no "beats" claim can be made yet. (2) In development, after Holm, only these comparisons pass: h = 1 vs no-change (Z-DIR and Z-DAMP, both designs, but fragile, see q20), ZC1 at h = 1 (n = 18), and a few comparisons vs seasonal naive at h = 1. Nothing passes vs no-change at h = 4 or 8 (p_holm 0.097-1.0), and nothing passes vs AR at any h. So "comparable to the AR benchmark" is the most that can be said, pending q19. (3) The real-time check (origins 2016-09 to 2023-06) points the other way. Z-DIR's rel. RMSE vs no-change is 1.08 / 1.24 / 1.34 against the latest vintage, and 1.03 / 1.19 / 1.25 on the same origins in the latest design. The development wins come from before 2016. The protocol's regime split (2007Q4-2011Q4, 2020) and the ten largest errors are not produced yet. (4) Coverage: 95% intervals under-cover at h = 4 (Z-DIR 0.83, CP upper bound 0.905) and h = 8 (0.75, 0.84) for every model, so "intervals are reliable" cannot be said for h > 1. At h = 1, Z-DIR and AR are not rejected. (5) Every result must carry the label "pseudo out-of-sample, latest vintage".
- **Severity:** major
- **Evidence:** tests_dev.csv, coverage_dev.csv, scores_dev.csv (real-time-check rows).
- **Proposed resolution:** Phrase C3 using the protocol's fixed wording. Add the regime split and the largest-error tables. Report the post-2016 reversal with the same weight as the full-sample result.
- **Status:** resolved (2026-11-04, by Claude, markets track): no "beats" claim made; SPECS states what development does and does not allow; no write-up until Eleonora rules.

### R-20261104-mkt-q24 · quant-reviewer · research/c2_forecast (minor implementation points)
- **Objection:** (a) The seasonality gate (F-test, p = 7e-5) uses iid errors, but quarterly changes are AR(2) (BIC). Its p-value is overstated, although the gate probably still passes. (b) "Rolling 80" means 80 training pairs for Z-DIR and Z-DAMP, 80 changes for drift, and 76 fitted observations for AR. Small, but not stated. Checked and found sound: target as a change; 1990Q1 first origin; development targets <= 2023Q2 (asserted); `--holdout` disabled; purge and embargo s+h <= T-4 in pairs, AR and drift; AR by BIC 0-4 on a common sample; the interval purge (T_j+h <= T-4, burn-in 40); the CRPS ensemble f+past errors (correct formula); Clopper-Pearson, and Kupiec and Christoffersen at h = 1 only; the HLN factor and t(n-1). A --no-c1 rerun reproduces every Z-family forecast, score and raw p exactly, and the 14 tests pass.
- **Severity:** minor
- **Evidence:** seasonality.json; forecast.py `seasonality_check`, `pairs`, `ar_bic`, `drift`, `add_intervals`; rerun on 2026-11-04 (outputs restored, no file changed).
- **Proposed resolution:** Add a HAC or AR-augmented version of the seasonality F-test as a check, and state the rolling-window convention in SPECS.
- **Status:** resolved (2026-11-04, by Claude, markets track): AR(2)-augmented seasonality check recorded (p ≈ 1e-15; gate unchanged); rolling-window conventions stated in SPECS.
