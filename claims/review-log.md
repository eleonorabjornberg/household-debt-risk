# Review log

Objections raised by the review subagents (`.claude/agents/skeptic.md`, `quant-reviewer.md`, `editor.md`) and by people, with their resolutions. Append only: entries are never deleted or rewritten; a resolution is added under the entry.

Entry format:

```
### R-<YYYYMMDD>-<n> · <reviewer> · <target file or claim_id>
- **Objection:**
- **Severity:** blocker / major / minor
- **Evidence:**
- **Proposed resolution:**
- **Status:** open | resolved (<date>, by <who>): <what was done> | rejected (<date>, by <who>): <why>
```

Resolutions are written by the main session or Eleonora, never by the reviewer that raised the objection.

---

### R-20261104-mkt-q1 · quant-reviewer · research/b1_market_pricing
- **Objection:** The levels (L) regressions do not pass the cointegration test, so their HAC intervals cannot be trusted. The README never reports the residual ADF result and still presents the significant positive L coefficient as a finding ("a higher public share goes with a *wider* spread").
- **Severity:** major
- **Evidence:** Residual ADF for main L is -3.77 (regressions.csv `adf_resid`). The Engle-Granger (MacKinnon) 5% critical value for 7 variables is -5.10 (10%: -4.79). Even counting only the I(1) series (S1, mort_share, DGS10; N=3), the 5% value is -3.79, so the test does not reject no-cointegration. The share (ADF with trend, p=0.21), S1 (p=0.19) and DGS10 (p=0.52) all look I(1). Residual AR(1) is 0.81, so the pre-registered lag of 4 is short: with statsmodels HAC the main-L SE on public_share goes 0.535 (4 lags), 0.627 (8), 0.684 (12), 0.718 (16), and at 8 lags the 95% CI is about -0.01 to 2.44, which includes zero.
- **Proposed resolution:** Report each L residual ADF next to its EG critical value. Describe L inference as unreliable (possibly spurious) and treat L as descriptive. Add a HAC lag-sensitivity table, declared under "Changes after results" in METHOD.md. The verdict ("no robust association") does not change.
- **Status:** resolved (2026-11-04, by Claude, markets track): README reports each levels residual ADF against EG 5% values and treats levels as possibly spurious; HAC lag 8 added as a declared post-hoc check (METHOD.md, Changes after results). EG constants still to verify against MacKinnon (2010) before publication.

### R-20261104-mkt-q2 · quant-reviewer · research/b1_market_pricing
- **Objection:** The positive full-sample L coefficient comes from the level shift after 2022Q4. The README says the coefficient merely "loses significance" before the PMMS method change, but in fact it changes sign. The sentence "the 2020s rise in the spread lines up with rate volatility ... not with the public share" overclaims.
- **Severity:** major
- **Evidence:** In the ends-2022Q3 L spec b is -0.31 (CI -1.10 to 0.47). Re-running main L with a 2022Q4+ step dummy (from data/b1/panel.csv, maxlags 4) gives b = -0.31 (CI -1.06 to 0.45) and a dummy of +0.87 pp, which is left over after the vol10 control. So vol10 does not explain the post-2022 level. The cause could be the method break or the 2023 agency-MBS spread blowout; this design cannot separate them.
- **Proposed resolution:** Say the sign flips. State that the full-sample L estimate depends on the 15 quarters from 2022Q4 on. Drop or soften the volatility attribution. Optionally report the dummy version as a declared post-results robustness check.
- **Status:** resolved (2026-11-04, by Claude, markets track): README states that the sign flips once 2022Q4+ is excluded or dummied; post-hoc dummy reported (0.87 pp); the "lines up with volatility" sentence removed.

### R-20261104-mkt-q3 · quant-reviewer · research/b1_market_pricing
- **Objection:** The first-differences test has almost no power, so "no robust association" means the result is inconclusive, not that there is no association. The reading rule needs significance in both L and D, which makes "compression" close to unreachable with these data. Readers should be told that.
- **Severity:** minor
- **Evidence:** The quarterly change in the share has an SD of 0.60 pp. Main D gives b = -0.08 with SE 1.82, so the 95% CI (-3.66 to 3.49) is about three times wider than the L point estimate is large. The ends-2022Q3, blend and headline D intervals are similar or wider.
- **Proposed resolution:** Keep the pre-registered verdict. Add a minimum detectable effect for D (about 2.8 x SE, roughly 5 pp of spread per unit of share) and use the word "inconclusive" in the result paragraph.
- **Status:** resolved (2026-11-04, by Claude, markets track): headline now reads "inconclusive"; power stated (about 0.64 pp either way over the rise in the share).

### R-20261104-mkt-q4 · quant-reviewer · research/b1_market_pricing
- **Objection:** The controls leave out the main administrative price that moved with the public share: GSE guarantee fees and LLPAs. These rose from 2008 to 2014, including the 10 bp TCCA increase in 2012, while the public share rose from 0.45 to 0.60. This biases b upward in levels. Separately, in D, `refi` is almost collinear with ΔDGS10: the DGS10 SE is 0.18 in D against 0.019 in L.
- **Severity:** minor
- **Evidence:** METHOD.md and README name g-fees as part of S1 but do not control for them. FHFA's annual Single-Family Guarantee Fee reports (free, 2009 onward) give average g-fees.
- **Proposed resolution:** As a declared extension, add an average g-fee series (FHFA, annual and interpolated, labelled as a proxy) from 2009, or subtract it from S1. Also note the refi/DGS10 collinearity in D.
- **Status:** open: g-fee and LLPA control (FHFA annual g-fee reports, 2009+) listed as an extension for Eleonora to decide; refi/DGS10 collinearity in D noted, not yet tested.

### R-20261104-mkt-q5 · quant-reviewer · research/b1_market_pricing
- **Objection:** The README results table shows 3 of the 8 public-share estimates. It leaves out the headline-share L estimate, which is significant and positive (1.80, CI 0.41 to 3.19), and the blend L estimate (1.11, CI -0.04 to 2.25). With 8 correlated specifications, the one significant positive L result per share definition should be shown, and labelled as descriptive.
- **Severity:** minor
- **Evidence:** regressions.csv, term=public_share, rows for "headline share" and "5y/10y blend".
- **Proposed resolution:** Show all 8 public-share rows in the README table, or link them with a one-line summary.
- **Status:** resolved (2026-11-04, by Claude, markets track): table now lists headline-share and 5y/10y-blend levels rows.

### R-20261104-mkt-s1 · skeptic · research/b1_market_pricing
- **Objection:** The PMMS method change of 2022-11-17 shows up in the data as a persistent level step of about +0.17 pp in S1. README handles it only by dropping the post-2022Q3 sample in one variant. The 2020Q1–2026Q2 mean spread (2.27 pp), the sentence "the spread did not fall", and the positive, significant main levels coefficient all include 15 quarters measured under the new method. Without the break quarters the levels coefficient changes sign (1.22 to −0.31), which is more than "loses significance" (README:19).
- **Severity:** major
- **Evidence:** From data/b1/panel.csv, quarterly MORTGAGE30US − OBMMIC30YF (Optimal Blue conforming, whose method did not change): 2021Q3–2022Q3 runs −0.20/−0.20/−0.25/−0.21/−0.20, then 2022Q4–2023Q2 runs −0.03/−0.04/−0.04. Annual means: 2017–2019 about −0.29, 2024–2026 about +0.01. Applied to 15 of 26 quarters, a 0.17 pp shift adds about 0.10 pp to the 2020s mean.
- **Proposed resolution:** Add a post-2022Q4 PMMS dummy, or splice PMMS onto its pre-break level using the Optimal Blue overlap, as a reported variant. Caveat the descriptive table. Replace "loses significance" with "reverses sign". Logged as a change after results in METHOD.md.
- **Status:** resolved (2026-11-04, by Claude, markets track): see mkt-q2; README attributes part of the 2020s mean to the method change.

### R-20261104-mkt-s2 · skeptic · research/b1_market_pricing
- **Objection:** The regressor does not match the price population. PMMS prices conventional conforming loans, but `mort_share` also counts Ginnie Mae pools (FHA/VA/USDA), the FHLBs, Farm Credit and state and local holders. The Ginnie share rose from 11.3% to 17.1% across the periods, and PMMS does not price those loans. With a Fannie+Freddie-only share, the main levels coefficient is no longer significant. So the README sentence "a higher public share goes with a *wider* spread" depends on that definition.
- **Severity:** major
- **Evidence:** A scratch script reusing b1.ols_hac and a1.cells, with Fannie+Freddie (portfolio + pools)/total as the share: L coefficient 0.46, CI −1.97 to 2.89; D 0.32, CI −4.27 to 4.91; ends-2022Q3 L −1.13, CI −2.90 to 0.64. Period means of GSE-only vs Ginnie share: 34.4/11.3, 44.5/13.3, 47.4/17.1%.
- **Proposed resolution:** Report a GSE-only share variant, or state that the positive levels result rests on including FHA/VA pools. The verdict ("no robust association") does not change.
- **Status:** resolved (2026-11-04, by Claude, markets track): Fannie+Freddie-only share added as a declared post-hoc check and reported (after the 2026-11-04 catalog-level correction: 0.50, interval −1.92 to 2.92).

### R-20261104-mkt-s3 · skeptic · research/b1_market_pricing
- **Objection:** Holding is not bearing risk. The question ("did the public takeover compress the price of household credit risk") and the descriptive text treat the holder-based public share as the share of credit risk borne publicly. GSE credit-risk transfer (CAS/STACR) and private mortgage insurance on loans above 80% LTV move risk on GSE-held loans to private parties. FHA/VA-insured loans held by banks outside pools carry federal credit risk but count as private. CRT grew after 2013, inside the window where the share "rose".
- **Severity:** major
- **Evidence:** pipeline/series_catalog.yaml risk_buckets classify by holder. research/a1_gfc_decomposition/decompose.py:40-48. README:1 title, README:29.
- **Proposed resolution:** Add a caveat that the share counts holders, not who bears the risk, and name CRT, MI and insured loans held in bank portfolios. Or call the regressor "public holder share" throughout.
- **Status:** resolved (2026-11-04, by Claude, markets track): caveat "Who holds the loan is not who bears the risk" added, pointing to A2.

### R-20261104-mkt-s4 · skeptic · research/b1_market_pricing
- **Objection:** "No robust association" is not evidence of no compression. The first-differences interval allows large effects in either direction. The README's "the spread did not fall" and the line that the 2020s rise lines up with volatility "not with the public share" read stronger than the data allow, given that the main levels coefficient is positive and significant and the PMMS break (R-20261104-mkt-s1) falls in the same years.
- **Severity:** major
- **Evidence:** results.json public_share_coef.main.D: CI −3.66 to 3.49 pp per unit of share. Over the 17.9 pp rise in the mean share, that is about −65 to +62 bp of spread. Full-sample S1 ranges 1.21–2.93 pp (spreads_summary.csv).
- **Proposed resolution:** State the interval in bp per 10 pp of share and say the test cannot rule out compression of that size. Drop "not with the public share", or qualify it.
- **Status:** resolved (2026-11-04, by Claude, markets track): see mkt-q3.

### R-20261104-mkt-s5 · skeptic · research/b1_market_pricing
- **Objection:** The levels residual ADF statistics (−3.77 main, −4.46 pre-2022) are reported in results.json but not in README. Against Engle–Granger/MacKinnon critical values for about 7 variables with a constant (roughly −4.7 to −5.0 at 5%), they do not reject a unit root in the residuals. The significant levels coefficient may therefore be spurious.
- **Severity:** minor
- **Evidence:** results.json public_share_coef.*.L.adf_resid: main −3.771, blend −3.669, headline −3.873, ends 2022Q3 −4.464.
- **Proposed resolution:** Report the ADF statistic with the proper EG critical value in README next to the levels row. This adds weight to the D specification.
- **Status:** resolved (2026-11-04, by Claude, markets track): see mkt-q1.

### R-20261104-mkt-s6 · skeptic · research/b1_market_pricing
- **Objection:** Stock-versus-flow and timing mismatch. `mort_share` is a quarter-end share of the outstanding stock, while S1 is a quarterly mean of rates on new originations. Changes in who holds the stock lag changes in who guarantees new loans, so the share can be a poor proxy for the marginal guarantor, and the timing within the quarter is misaligned.
- **Severity:** minor
- **Evidence:** b1.py public_shares (quarter-end Z.1 levels) vs quarterly() (means of weekly/daily data).
- **Proposed resolution:** Name this in the "does not show" list. Optionally add a variant with the share lagged one quarter, or a flow measure such as GSE share of originations (HMDA, free) as a later extension.
- **Status:** resolved (2026-11-04, by Claude, markets track): stock-versus-flow caveat added.

### R-20261104-mkt-s7 · skeptic · research/b1_market_pricing
- **Objection:** The jumbo sentence "Loans that the GSEs cannot guarantee were not priced materially above loans they can" (README:31) comes before its confounding caveat. It also leaves out that the quarterly S2 range (−0.48 to +0.38 pp) is wide relative to the 0.03 mean, with jumbo above conforming in the 2020 stress period. Private pricing of jumbo loans does respond to conditions, and bank deposit funding is a further confound.
- **Severity:** minor
- **Evidence:** spreads_summary.csv, S2_jumbo_conf 2017Q1-latest: mean 0.032, min −0.485, max 0.384. 2017Q1–2019Q4 mean −0.091.
- **Proposed resolution:** Put the confounding caveat in the same sentence. Add that jumbo risk sits mainly on bank balance sheets funded by deposits.
- **Status:** resolved (2026-11-04, by Claude, markets track): jumbo caveat now precedes the numbers.

### R-20261104-mkt-s8 · skeptic · claims/tracks/markets.csv (b1_*)
- **Objection:** Register hygiene. (a) The display column drops the sign on every negative B1 number (b1_main_d_coef, _d_lo, _pre2022_l_coef, _pre2022_l_lo, b1_s2_jumbo_min, b1_s2_fha_mean), and claim-check does not verify signs. In B1 the sign is the result (compression is defined as b < 0). (b) Z.1-only rows carry a `fred:` vintage and FRED-only S2 rows carry a `z1:` vintage. (c) series_ids list the catalog-level FL403065105/FL413065105, but the code uses the finer cells (FL403065110/120/130, FL413065110/123/133/143). DGS5 is listed on main rows that do not use it. (d) The b1_main_l_bp_per_pp note refers to "b1_main_L_coef", but the row id is lower-case.
- **Severity:** minor
- **Evidence:** claims/tracks/markets.csv rows above. .claude/skills/claim-check (step 3: "Signs are not verified"). research/a1_gfc_decomposition/decompose.py:40-48. Every value matches results.json; results.json reproduces byte-identically on rerun.
- **Proposed resolution:** Sign-check the B1 rows by hand before publication, and correct the vintage, series_ids and note fields.
- **Status:** resolved (2026-11-04, by Claude, markets track): register rows regenerated with signed displays, per-source vintages, A1 fine-cell series ids, no DGS5 on rows that do not use it; signs checked by script against the README.

### R-20261104-mkt-q6 · quant-reviewer · research/c1_nowcast
- **Objection:** The as-of panel cannot support the sample proposed in Q-C1 (rolling origin from 2010Q2), and it drops the gap silently. ALFRED's first vintage is after 2010Q2 for most inputs: TOTALDI 2012-06, CLSACBW027NBOG 2012-08, FGCCSAQ027S 2013-06, RREACBW027NBOG 2015-02, and all BOGZ1 holder series 2019-03. `panel(t)` omits a series with no row on t, so a bridge or fallback could quietly run on a smaller indicator set in early years, and results across origins would not be comparable. Option 2(b) is feasible only from 2015.
- **Severity:** major
- **Evidence:** release_lags.csv `first_vintage` column; `pit.panel` (`if len(s)`); Q-C1 items 2 and 6.
- **Proposed resolution:** Have the evaluation fail loudly (or log a per-origin availability table) when a pre-registered input is absent. Set the sample start from the latest first_vintage of the chosen set, or pre-register a shorter sample. State this in Q-C1 item 6.
- **Status:** open (design, for Eleonora): sample-start constraint per indicator set now stated in tracks/markets.md Q-C1 item 6; feasible start 2015Q1 for option 2b.

### R-20261104-mkt-q7 · quant-reviewer · research/c1_nowcast
- **Objection:** `first_release()` is not safe as the "first-release share" target (Q-C1 option 1a). (a) Every observation present in a series' first ALFRED vintage is stamped with that vintage date, so for ALFRED-start dates it returns the value as of 2010 or 2019, not the first release. `release_lags` and `revision_size` filter this out, `first_release` itself does not. (b) `groupby().first()` skips NaN per column, so a date whose first vintage was "." would get an earlier `published` paired with a later value. No current impact (the 18 NaN rows are 1946-47 dates added 2015), but the first-release value is used as a score target. (c) Q-C1 does not say whether the target change is first release of q minus q-1 in the same Z.1 vintage or minus the previously published q-1. Z.1 revises earlier quarters, so these differ, and the no-change benchmark must be defined consistently with it.
- **Severity:** moderate
- **Evidence:** pit.py:57-60 versus 63-95; Z.1 vintage stamps in z1_calendar.csv; units NaN check on alfred_HMLBSHNO.
- **Proposed resolution:** Add a `since`/first-vintage guard (or flag column) to first_release and use `.nth(0)`/head(1). Add a test with a NaN first value. Specify the target change definition in Q-C1 item 1.
- **Status:** resolved in part (2026-11-04, by Claude, markets track): first_release now keeps NaN rows (nth(0)) and documents that dates in ALFRED's first vintage are not true first releases; the change definition is a design question (Q-C1 item 9).

### R-20261104-mkt-q8 · quant-reviewer · research/c1_nowcast
- **Objection:** Timing and date conventions are not fixed in code. (a) `as_of(v, t)` includes anything with realtime_start == t, so a nowcast "on day t" sees same-day releases (Z.1, G.19, H.8 come out at different times of day). ALFRED's realtime_start is also FRED's ingestion date, not the Fed's release time. (b) Date conventions differ: FRED marks G.19 months and Z.1 quarters by period start (2024-12-01 = end-December level; 2024-10-01 = Q4 level), H.8 and H.4.1 by Wednesday. There is no helper that maps each to "level at quarter end", and a naive merge on date or a join of month-start to quarter-start would misalign by up to two months. (c) release_lags.csv is full-sample summary (min/median/max over all years, including the 172-day outlier) and must not be used to simulate availability; the panel correctly does not. (d) Growth bridges must use same-vintage growth (G.19 is rebenchmarked to Z.1 after the Z.1 release).
- **Severity:** moderate
- **Evidence:** pit.py:40-54; inputs.yaml freq/desc; Z.1 2026-09-11 value absent on 2026-09-10 and present on 2026-09-11 (checked).
- **Proposed resolution:** State "end of day t, inclusive" or use a strict `< t` plus a stated cutoff in the README. Add a tested `level_at(series, quarter_end)` helper and a rule that bridge growth uses a single vintage. Mark release_lags.csv descriptive only.
- **Status:** resolved in part (2026-11-04, by Claude, markets track): same-day inclusion rule documented in pit.as_of. Same-vintage growth is the recommended rule in Q-C1 item 9; period-start helper to add when the model is built.

### R-20261104-mkt-q9 · quant-reviewer · research/common/fred.py
- **Objection:** Silent-failure paths. (a) The pagination guard uses `d.get("count", 0)`, so a response without `count` passes. (b) `to_millions` returns the frame unchanged (0 rows) if any units label lacks a scale word, and leaves uncovered rows at factor 1, with no check. (c) Cache never refreshes, so "current" rows (the 2262-04-11 sentinel) mean current on the fetch date, not today; this is safe for as-of use, but the fetch date should be in the README. (d) The sentinel 2262-04-11 is exactly Timestamp.max's date and works in ns precision only. Verified: counts equal returned rows for all 15 series; post-rescale vintage-to-vintage ratios show no unit jump (raw G.19 jumps, 983 per series, disappear), intervals are contiguous, sentinel and rescale add no look-ahead.
- **Severity:** minor
- **Evidence:** fred.py:85, 124-137, 90; scratch check over data/fred/alfred_*.json.
- **Proposed resolution:** Require `count`; add an assertion in load_vintages that no consecutive-vintage ratio exceeds 5 for dollar series (the H.8 CLSACBW 2015-01 and TOTALTCU 2012-07 vintages do have large level restatements, worth a note); record the fetch date.
- **Status:** resolved (2026-11-04, by Claude, markets track): fred.vintages raises if count is missing; to_millions raises on mixed dollar/non-dollar labels. Retrieval time is in data/fred/manifest.jsonl per download.

### R-20261104-mkt-q10 · quant-reviewer · research/c1_nowcast (Q-C1 options)
- **Objection:** Q-C1 covers target vintage, holdout and benchmarks only partly. (1) Inference: the Diebold-Mariano test is invalid for nested comparisons (bridge regression vs no-change/AR); use Clark-West or report descriptively, and note two instants per quarter are dependent. (2) Holdout: eight quarters (2024Q3-2026Q2) spans the 2025-26 unit changes and the 2026-01-09 delayed release and is tiny; freeze indicators, model, windows and metrics in a dated docs/decisions entry (preregister) before the holdout is scored, and report failed specifications. (3) Benchmarks must be built from as-of data (the drift window and AR must use vintages public at the instant). (4) Target: the first-release series needs the unparsed Fed archive for 2010-2018 (see q7); add a fall-back that scores only 2019+ in ALFRED. (5) Q-C1 item 3 "15th of the month" ignores that the Z.1 date shifts across the year; check z1_calendar.csv for each instant.
- **Severity:** moderate
- **Evidence:** tracks/markets.md Q-C1 items 1-6; no docs/decisions entry for C1 yet.
- **Proposed resolution:** Add these to Q-C1 before Eleonora chooses.
- **Status:** open (design, for Eleonora): Clark–West for nested benchmarks, as-of benchmarks and a pre-registered holdout added to Q-C1 item 6; pre-2019 target vintages stated as needing the Fed archive.

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
