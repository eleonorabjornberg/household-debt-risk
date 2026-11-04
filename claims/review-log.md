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
- **Status:** resolved (2026-11-04, by Claude, markets track): Fannie+Freddie-only share added as a declared post-hoc check and reported (0.46, interval −1.97 to 2.89).

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
