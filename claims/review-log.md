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

### R-20261104-1 · quant-reviewer · research/a1_gfc_decomposition/README.md (growth vs retreat split)
- **Objection:** The headline "public growth 7.1 pp, private retreat 6.0 pp" depends on the chosen weighting and the ordering reverses under the alternatives. The endpoint identity weights by the start share P0 (36.1%), which favours the public term while P rises. Chaining the same identity by quarter (the script's own path.csv) gives public 6.27 pp, private 6.83 pp; a Shapley split of the two counterfactuals gives public 6.25, private 6.87. The README says the split "is exact" but does not mention that it depends on the path. The docstring says "chained and endpoint totals both equal P1 - P0", which holds only for the grand total, not for groups. The results.json groups and the 2011Q4 row of path.csv disagree with no note: Ginnie 3.81 vs 3.29, PLS/mREITs 4.93 vs 5.71, student loans 1.94 vs 1.62. The decision doc rejected Shapley for "no gain", but here it changes the headline.
- **Severity:** major
- **Evidence:** Reran in the scratchpad by importing decompose.py; no repo files were written. Endpoint public/private 7.127/5.979; chained 6.274/6.832; the Shapley public term is 6.245. path.csv 2011Q4 row: ginnie_pools 3.2879, private_label_and_mreits 5.7088.
- **Proposed resolution:** Report endpoint, chained and Shapley side by side, or call the split "roughly even (6.0-6.9 pp private, by method)". State that group totals depend on the path, and fix the docstring.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session, on Eleonora's decision): Eleonora chose Shapley (2026-11-04). README headline is now Shapley public 6.2 / private 6.9 pp, with the endpoint identity (7.1/6.0) and chained Shapley (6.2/6.9) reported in results.json `sensitivity` and named in the README. Docstring fixed.

### R-20261104-2 · quant-reviewer · docs/decisions/a1-decomposition.md
- **Objection:** The design was not set before the results. The decision doc was added in the same commit as decompose.py, results.json and the CSVs (f8b7ddc, 2026-11-04T00:30:57Z). It quotes the result (+13.1 pp) and is "Decided by: Claude", so it is not Eleonora's design (the authorship rule). The README cites it as "Method decision" and declares neither point.
- **Severity:** major
- **Evidence:** `git log --name-status -- docs/decisions research/a1_gfc_decomposition`.
- **Proposed resolution:** Say in the README that the method was chosen at the same time as the results, by Claude, and is awaiting Eleonora's decision. Record her choice in PLAN.md "Decisions taken".
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session, on Eleonora's decision): Decision note rewritten: decided by Eleonora, 2026-11-04 (Shapley); notes the first draft was Claude's choice made alongside the results. Decision added to PLAN.md "Decisions taken".

### R-20261104-3 · quant-reviewer · research/a1_gfc_decomposition/README.md (counterfactual comparison)
- **Objection:** The comparison with findings.md item 4 is not like for like. The 6.1 pp counterfactual (private held at 2007Q4) measures the public-growth side; it reproduces at 6.11. Under it, private retreat is the remaining 6.99 pp, not 6.0. The README puts 6.1 right after the 6.0 private figure, which invites reading the two as the same quantity. "Both say about half" holds only loosely (46% vs 53%).
- **Severity:** minor
- **Evidence:** pub_t1/(pub_t1+priv_t0) - P0 = 6.115 pp; residual 6.991 pp.
- **Proposed resolution:** State that 6.1 pp is the counterpart of the 7.1 pp public term, and give the counterfactual's private piece (7.0 pp).
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README Limits item now says 6.1 pp is the public side of a private-held-fixed split and both views put about half on private retreat.

### R-20261104-4 · quant-reviewer · research/a1_gfc_decomposition/README.md (causal wording)
- **Objection:** An accounting split cannot carry causal or counterfactual statements, but the README makes some. "Conservatorship ... didn't change how much they held" and "doesn't fit these data" need a counterfactual (the GSEs' holdings without conservatorship), which this method cannot supply and the README itself defers to A7. "Their share rose mostly because private holders shrank around them" is the own-share view (3.9 pp vs 1.4 pp growth term) restated as a cause. The README's limit "accounting, not a causal estimate" is contradicted in "What this changes".
- **Severity:** major
- **Evidence:** README "What this changes", bullets 2-3.
- **Proposed resolution:** Rephrase descriptively. For example: "GSE balances rose $278B; most of their own-share gain is arithmetic from a shrinking denominator; whether conservatorship changed holdings is A7."
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Reworded: conservatorship bullet now says the data cannot test the claim; GSE balances (+$278B) and the chained path are stated descriptively.

### R-20261104-5 · quant-reviewer · research/a1_gfc_decomposition/test_decompose.py, decompose.py
- **Objection:** The tests would not catch a missing holder. They exercise contrib() only, on synthetic data, and do catch a flipped sign through the exact-sum check. cells(), the PUBLIC_* lists, the group partition and the own-share view are untested. The README says the script "asserts ... that the cells reproduce the scope total", but scope_gap is only recorded, not asserted. A dropped public holder would move the share with no error. The gap is in fact about 0, at most 4e-9 $M across the window.
- **Severity:** minor
- **Evidence:** decompose.py main(): `scope_gap = ...` with no assert; tests cover contrib() only. Both tests pass.
- **Proposed resolution:** Assert scope_gap < tolerance at every quarter in [t0, t1]. Add a test that the groups partition the cell columns, and one that removing a cell trips the scope check.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): decompose.py now asserts the scope reconstruction at every quarter in [t0, t1] and that the groups partition the cells; two Shapley tests added. The remove-a-cell test is not added (the per-quarter scope assert covers it at run time).

### R-20261104-6 · skeptic · a1_ff_chained_2008q3 (research/a1_gfc_decomposition/README.md, "What this changes" bullet 2)
- **Objection:** "Fannie and Freddie had contributed 1.3 pp by 2008Q3, before the September 2008 conservatorship" gets the timing wrong. 2008Q3 is the 30 Sep 2008 stock, more than three weeks after the 6 Sep conservatorship and 7 Sep PSPAs. The last quarter-end before conservatorship is 2008Q2, at 1.1 pp. The conclusion ("came early") survives, but the sentence and the register row both attach a post-event number to a pre-event label.
- **Severity:** major
- **Evidence:** path.csv: 2008Q2 fannie_freddie 1.0971; 2008Q3 1.3412. sources.md FHFA row: conservatorship 6 Sep 2008.
- **Proposed resolution:** Say "1.1 pp by 2008Q2, the last quarter-end before conservatorship". Update the register row, and note that quarterly stocks cannot place within-quarter events.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README and register now say 1.1 pp by 2008Q2, the last quarter-end before conservatorship (row a1_ff_chained_2008q2).

### R-20261104-7 · skeptic · a1_pls_change_usd, a1_pls_pp (README "Which private holders shrank")
- **Objection:** The Result section presents "private-label securitization and mortgage REITs held $1.71T less ... 4.9 pp" with no qualifier, but a large part is FAS 166/167 consolidation onto banks and finance companies, not a retreat. The README's own Limits bullet says the split between private lines around 2010Q1 is accounting. The headline sentence and both register rows ignore that bullet. Only the private total (6.0 pp under this weighting) is robust to the reclassification.
- **Severity:** major
- **Evidence:** path.csv 2009Q4 to 2010Q1: private_label_and_mreits 2.236 to 4.330 (+2.09 pp in one quarter), banks_and_credit_unions 0.869 to -0.064, other_private 0.679 to 0.278. decomposition.csv: consumer-credit ABS issuers 652.5 to 46.2 $bn (-606), while bank consumer credit rose +298 and finance-company consumer credit +110.
- **Proposed resolution:** Report only the private total as a finding. If the PLS line is kept, give it net of the 2010Q1 step, or caveat it in the same sentence. Re-word the register claim text.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): PLS sentence now carries the FAS 166/167 caveat in place and says the private total is unaffected; register claim text reworded.

### R-20261104-8 · skeptic · README "The largest public piece is FHA/VA, not the GSEs"
- **Objection:** This treats holdings in Ginnie pools as federal risk, and "largest" is ambiguous. (a) "Largest" holds only for the change in the share. In stock terms, Fannie+Freddie held $4.34T in 2011Q4 against Ginnie's $1.13T. (b) "Explicitly federal" overstates the risk transfer. VA and USDA guarantees are partial, and Ginnie issuers/servicers bear losses beyond them. FHA/VA loans held directly by banks, including delinquent loans bought out of Ginnie pools, are federally insured but sit in "private", so Ginnie pool holdings are not the federal FHA/VA exposure.
- **Severity:** major
- **Evidence:** decomposition.csv 2011Q4: Fannie 2680.3 + Freddie 1658.9 vs Ginnie 1129.0 $bn. README Limits bullet 1 concedes the bank-held FHA/VA point, but bullet "What this changes" 1 does not.
- **Proposed resolution:** "The largest public contribution to the change came from Ginnie Mae pools." Drop "explicitly federal", or qualify it (FHA full insurance; VA/USDA partial). Point to A2 for exposure.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README: "the largest public increase was in Ginnie Mae pools", with 2011Q4 holdings ($4.34T GSEs vs $1.13T Ginnie) and the partial VA/USDA guarantee caveat.

### R-20261104-9 · skeptic · README conservatorship bullet ("doesn't fit these data")
- **Objection:** The measure cannot test the claim, which is separate from the causal-wording point in R-20261104-4. The catalog classes GSEs and their pools as public at every date (`risk_buckets.gse_agency.public: true`), so a holdings share cannot register a move of GSE credit risk from shareholders and an implicit guarantee to Treasury under the PSPAs. "Doesn't fit these data" should be "these data cannot speak to it". Also, the PSPAs backed the GSEs' guarantees on about $4T of MBS pools, not only "debt the GSEs already held". The bullet misstates what conservatorship changed.
- **Severity:** major
- **Evidence:** pipeline/series_catalog.yaml:17 (gse_agency public: true) and :50-51 (FL403065105, FL413065105 both gse_agency). README "What this changes" bullet 3.
- **Proposed resolution:** Recast as a definitional limit: "Because GSEs count as public throughout, this decomposition cannot detect a conservatorship ratchet; that is a question about who bears GSE losses (A2/A7)."
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Recast as a definitional limit ("the data are silent, not contrary"); counterfactual left to A7.

### R-20261104-10 · skeptic · README "Dated policy events" table
- **Objection:** The "lines up with" column is assigned by subject, not by any observed change in the path, and some rows do not align. Federal student loans had moved 0.03 pp by 2008Q2 (ECASLA, May 2008) and 0.09 pp by 2008Q4. Most of the component (0.66 to 1.62 pp) came after SAFRA's 30 Jun 2010 cutoff, and the Z.1 line cannot separate ECASLA purchases from Direct Loan originations. Ginnie rises roughly steadily all window, so any date "lines up". Fannie/Freddie rose before HERA and peaked in 2009Q4, after both acts.
- **Severity:** minor
- **Evidence:** path.csv federal_student_loans: 2008Q2 0.0322, 2008Q4 0.0917, 2009Q4 0.5229, 2010Q2 0.6618, 2011Q4 1.6222. ginnie_pools increments roughly 0.15-0.37 pp per quarter throughout.
- **Proposed resolution:** Rename the column "related component". For each component, give the quarters of its largest steps, and state that quarterly stocks cannot date effects within a quarter.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Table intro says events are matched by topic, not by breaks, with the student-loan example (0.03 pp by 2008Q2); column renamed "Component it lines up with".

### R-20261104-11 · skeptic · decompose.py PUBLIC_MORT "Ginnie Mae pools (FHA, VA, USDA)"
- **Objection:** FL413065133 is the Z.1 "FmHA pool, including ... mortgages held by the Federal Financing Bank" line, not a Ginnie Mae pool. It is grouped under the Ginnie label. It is 0 in 2007Q4 and 2011Q4, so no number moves, but the label misdescribes the series if it is ever non-zero.
- **Severity:** minor
- **Evidence:** `unzip -p data/validation/FRB_Z1_csv.zip Z1.csv | grep FL413065133`: "one-to-four-family residential mortgages held in a Federal Farmers Home Administration (FmHA) pool, including ... held by the Federal Financing Bank". Value 0.0 at both endpoints.
- **Proposed resolution:** Relabel the cell "Ginnie Mae and FmHA pools", or split FmHA out.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Label is now "Ginnie Mae pools (FHA, VA, USDA) and FmHA pools"; README Limits notes FmHA is zero at both endpoints.

### R-20261104-12 · skeptic · research/a1_gfc_decomposition (vintage coverage)
- **Objection:** The issuer-level split (Ginnie vs Fannie vs Freddie vs FHLB vs Other GSEs) cannot be checked against the June 2026 vintage. The committed previous file is the per-table zip, which lacks FL403065110/120/130 and FL413065110/123/133/143. The README "Revisions" bullet does not say this. At bucket level nothing moves: total, growth/private split, gse_agency, student loans, PLS and the dollar changes are identical to 3 d.p. across vintages. So the risk is low but unverified.
- **Severity:** minor
- **Evidence:** Scratchpad rerun, nothing written to the repo. Sep vs Jun vintages: P0 36.115/36.115, P1 49.221/49.221, pub 7.127/7.127, gse_agency 5.003/5.003, PLS $-1706.7bn both. load_table_zip reported those 7 issuer ids as missing in prev_z1_csv_files.zip.
- **Proposed resolution:** State in Revisions that the issuer split is checked only at bucket level, or obtain the June Z1.csv long file.
- **Status:** open

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

### R-20261104-ana-1 · skeptic · research/a2_net_exposure/README.md:16 (a2_public_share_net_lower_2025q4, a2_net_ff_lower_hh)
- **Objection:** The table labels G − cumulative CRT RIF as "Net, lower bound" and the public share as "at least 55.2%". That is a lower bound only on net-of-CRT exposure. Once mortgage insurance is netted (FHFA PMI RIF is 12.5% of 2023 gross by the same method), true net exposure can be well below $6.05T and 55.2%. Read alone, the table row says the public share cannot be below 55.2%.
- **Severity:** major
- **Evidence:** README.md:13-16 table header "Net, lower bound (all issued CRT still in force)"; README.md:21 and net_exposure.csv 2023 pmi_issued_pct_of_gross = 12.5191; register rows 4 and 8 say "at least".
- **Proposed resolution:** Relabel as "net of CRT only, before mortgage insurance" in the table and in register claims 4 and 8, and add one sentence saying PMI could lower net further.
- **Status:** open

### R-20261104-ana-2 · skeptic · research/a2_net_exposure/README.md:16,19 (a2_public_share_gap_pp)
- **Objection:** "Public share net" is (public principal − RIF)/S. That mixes loss capacity with principal and treats $1 of RIF as $1 of principal moved to the private side, so 55.2% is not a share of anything observable. Line 19 adds a caveat, but the table cell at line 16 (and register row 8) carries the number without it.
- **Severity:** major
- **Evidence:** net_exposure.py:85 `100 * (pub - crt["cum_rif_musd"] * a) / s`; METHOD.md:15.
- **Proposed resolution:** Put the "loss capacity against principal" caveat in the table and in the register claim text, or report the gap as RIF/S rather than as a "share".
- **Status:** open

### R-20261104-ana-3 · skeptic · research/a2_net_exposure/README.md:20
- **Objection:** The FHFA "majority" quote is attributed to CRT ("the share transferred on covered loans is much larger"). FHFA says "Through CRT **and mortgage insurance**, the majority…". The claim that the CRT slice is "where most stress losses fall" is unsourced.
- **Severity:** major
- **Evidence:** sources.md:9 (4Q2019 quote); same wording in the Dec 2016 extract, line 38.
- **Proposed resolution:** Quote FHFA in full, including "and mortgage insurance", and source the stress-loss statement or label it as an assumption.
- **Status:** open

### R-20261104-ana-4 · skeptic · research/a2_net_exposure/README.md:21 (a2_pmi_cum_rif)
- **Objection:** "Mortgage insurance is larger than CRT in RIF terms" contradicts the project's own source: FHFA 4Q23 p.8 says "the RIF figures for these two categories are not strictly comparable".
- **Severity:** minor
- **Evidence:** sources.md:13 quote.
- **Proposed resolution:** Drop the comparison or carry FHFA's caveat next to it.
- **Status:** open

### R-20261104-ana-5 · skeptic · research/a2_net_exposure/README.md:22, METHOD.md:14 (a2_crt_ref_upb_over_gross)
- **Objection:** The 1.1× is explained only "because refinanced loans are counted again". FHFA's own footnote says the same reference UPB may back both a STACR and an ACIS deal, and cumulative UPB also keeps loans that have paid off without refinancing.
- **Severity:** minor
- **Evidence:** CRT-Progress-Report-4Q22 extract, Freddie table footnote 5: "The same reference pool UPB may back STACR and ACIS transactions."
- **Proposed resolution:** List all three causes; drop "because".
- **Status:** open

### R-20261104-ana-6 · skeptic · research/a2_net_exposure/crt_fhfa.csv:7-8
- **Objection:** The PMI UPB for 2018 and 2019 uses the rounded text figures ($1.2T, $1.6T). The chart boxes in the same reports give $1,231B and $1,570B, and 2020 onward uses the boxes. The column is not used in any output; RIF values match.
- **Severity:** minor
- **Evidence:** 4Q18 extract line 611 "Total $1,231"; 4Q2019 extract shows "Total $1,570".
- **Proposed resolution:** Use the box values, or document the mixed basis.
- **Status:** open

### Responses (analysis track, 2026-11-04)
- R-20261104-ana-1: accepted. Table header and register rows now say "net of CRT only, mortgage insurance not netted"; README states 55.2% is not a floor once MI is netted.
- R-20261104-ana-2: accepted. Table header now says principal less CRT loss capacity; register claims say "RIF subtracted from principal".
- R-20261104-ana-3: accepted. The FHFA "majority" quote is now attributed to CRT and mortgage insurance together; the unsourced "most stress losses fall" clause is removed.
- R-20261104-ana-4: accepted. README quotes FHFA's "not strictly comparable".
- R-20261104-ana-5: accepted. README and METHOD now give all three reasons (paid-off loans kept at issuance balance, refinanced loans counted again, STACR/ACIS sharing a pool).
- R-20261104-ana-6: noted, not changed. The column is unused; the basis column already says the 2018–19 PMI UPB is the rounded text figure.

### R-20261104-ana-7 · skeptic · research/a5_distribution/README.md:15 (a5_top10_mortgage_2026q2)
- **Objection:** The top 10% share of home mortgages is the sum of three rounded shares (0.8 + 3.2 + 24.4 = 28.4). Computed from the levels file it is 28.48%, which displays as 28.5%. The printed number is wrong at display precision. The same rounding is why the table's mortgage column sums to 99.9.
- **Severity:** blocker
- **Evidence:** distribution.py:165,180 sums `dfa-networth-shares.csv` (published to 0.1). Recompute from `dfa-networth-levels.csv` 2026:Q2: (117243+453093+3410241)/13976937 = 0.28480. Top 10% net worth by the same method is 0.68918, so 68.9% is unaffected.
- **Proposed resolution:** Compute group sums from the levels (or from shares-detail) and not from rounded shares, then rerun and update README:15, results.json and the register row. Apply the same fix to `top20_mortgages`, which happens to be right (0.53159, so 53.2%).
- **Status:** open

### R-20261104-ana-8 · skeptic · research/a5_distribution/AVAILABILITY.md:13
- **Objection:** The row label "Who holds (and so carries) the risk by loan type" treats holding as bearing risk. Holding and risk differ in both directions: GSE pools shed part of the risk through CRT and private MI (A2), and privately held FFEL student loans are federally guaranteed. The 65.6% and 31.3% public shares (README:23) are shares of holdings, not of risk.
- **Severity:** major
- **Evidence:** AVAILABILITY.md:13. A2 shows net-of-CRT and MI exposure below gross. The README:23 wording ("hold") is correct; the availability note is not.
- **Proposed resolution:** Change it to "Who holds the loans, by loan type". Add one README sentence saying holding is not bearing risk and pointing to A2.
- **Status:** open

### R-20261104-ana-9 · skeptic · research/a5_distribution/README.md:17-19
- **Objection:** The groups are ranked by net worth, and debt lowers net worth. So "the bottom half owes half the consumer credit" and its high leverage partly restate how the bottom 50% is defined. Membership also changes with house prices. The bottom-50 mortgage share was 34.6% in 2010Q3 and 22.1% in 2021Q1: underwater owners fell into the bottom half and then rose out of it. The 1989-vs-2026 endpoint comparison hides this. Read as "who borrows", it suggests a fixed population that changed its borrowing.
- **Severity:** major
- **Evidence:** figures/dfa_bottom50_shares.alt.txt (high 34.6% in 2010Q3; low 22.1% in 2021Q1). README:19 already notes the house-price effect on the ratios but not on group membership.
- **Proposed resolution:** Add a caveat that wealth groups are re-ranked each quarter and that debt enters the ranking. Show income groups (less endogenous) next to them, or say the 1989 comparison runs between different populations.
- **Status:** open

### R-20261104-ana-10 · skeptic · research/a5_distribution/README.md:19 (a5_b50_leverage_2007q4)
- **Objection:** "Lower than in 2007" uses 2007Q4 as the reference. Bottom-50 liabilities/assets peaked at 95.3% in 2010Q4, not in 2007. The sentence is true, but readers will take 81.5% as the peak.
- **Severity:** minor
- **Evidence:** From dfa-networth-levels.csv, the Bottom50 Liabilities/Assets maximum is 2010:Q4 = 0.9530 (2007:Q4 = 0.8149, 2026:Q2 = 0.5836).
- **Proposed resolution:** Either state the 2010Q4 peak as well (it needs a register row) or say "down from 81.5% on the eve of the crisis".
- **Status:** open

### R-20261104-ana-11 · skeptic · research/a5_distribution/README.md:27; figures/state_mortgage_pc_2025.*
- **Objection:** The "3.8× spread" across states comes from DC, a city-jurisdiction outlier. Among the 50 states the spread is CO/WV = 3.5×. DC is also the maximum for student loans (12,650 against GA 7,120 next). On the sextile maps DC sits in the same top bin as every state from $55.6k up ($6.1k up for student loans), so the map understates DC while the text headline leans on it.
- **Severity:** minor
- **Evidence:** state_2025.csv: 72210/20770 = 3.48; mortgage sextile breaks [20770, 30540, 33813, 40310, 46350, 55600, 78140].
- **Proposed resolution:** Give the 50-state spread next to the figure that includes DC, or footnote that DC is a city. Optionally mark DC as an outlier in the map legend.
- **Status:** open

### R-20261104-ana-12 · skeptic · research/a5_distribution/README.md:27-28, 34
- **Objection:** The extremes are single sample-based values with no stated uncertainty. WY's student-loan minimum comes from a 1% sample (about 5k people) and fell 10% in one year (3,530 to 3,180), which suggests noise. Separately, README:27 says "mortgage debt" without "excluding HELOC". The DFA and Z.1 home mortgages used two sections earlier include HELOCs, so the three mortgage measures in the README are not the same object.
- **Severity:** minor
- **Evidence:** area_report_by_year.xlsx Info sheet: "Mortgage Debt Balance per Capita (excluding HELOC)", "Student Loan ... 1% of the population". The studentloan sheet row WY reads Q4_2024 3530, Q4_2025 3180. HI 3,810 is next lowest.
- **Proposed resolution:** Write "mortgage debt (excluding HELOCs)" at README:27 and in the map title. Add "single-year sample estimates; rankings near the extremes may not be significant".
- **Status:** open

### R-20261104-ana-13 · skeptic · claims/tracks/analysis.csv (a5_ rows); README.md:23
- **Objection:** Two register gaps. (1) README:23 prints 65.6%, but no a5 row covers it, and the main row `public_share_mortgage_2026q2` lists only analysis/findings.md and recommendation.md as locations. (2) The NY Fed rows give vintage `nyfedstate:2026-02-01`, but the workbook gives only "February 2026", so the day is invented.
- **Severity:** minor
- **Evidence:** `grep 0.6555 claims/tracks/analysis.csv` finds nothing. claims/register.csv:11 has the locations. The Info sheet citation reads "...Federal Reserve Bank of New York, February 2026".
- **Proposed resolution:** Add README:23 as a location for public_share_mortgage_2026q2 on merge, like the CC fold note. Use `nyfedstate:2026-02` or the file's Last-Modified date, with its source stated.
- **Status:** open

### Responses to R-20261104-ana-7 to -ana-13 (analysis track, 2026-11-04)
- R-ana-7 (blocker): accepted. Group sums now come from DFA levels in `distribution.py`; the top 10% share reads 28.5%; register row corrected.
- R-ana-8: accepted. AVAILABILITY.md now says holding is not bearing the risk, with CRT, mortgage insurance and FFEL as examples.
- R-ana-9: accepted. README says groups are ranked by net worth (debt lowers it), that membership moves with house prices, and gives the 2010Q3 peak.
- R-ana-10: accepted. README gives the 2010Q4 leverage peak next to the 2007Q4 figure.
- R-ana-11: accepted. README gives the spread across the 50 states alone (3.5×, Colorado) and notes that DC shares the top map band.
- R-ana-12: accepted. README says the extremes are single sample estimates and that the NY Fed mortgage series excludes HELOCs.
- R-ana-13: partly. The vintage day is a placeholder the checker's format requires; register notes now say so. The 65.6% location belongs on the existing register row for the public share of mortgages (claims/register.csv, coordinator-owned); listed under "Proposed changes to shared files".

### R-20261104-ana-14 · skeptic · research/a2_net_exposure/tenk.py:18-23; README.md:31,34,39; METHOD.md:34
- **Objection:** "CRT" is coded as STACR + ACIS (insurance/reinsurance) only, but Freddie's own FY2025 10-K lists "Other" under "CRT transactions" (Table 22), and in FY2017-FY2020 the "other" bucket is mostly senior/subordinate and lender risk sharing, which FHFA's CRT totals (the issuance bound) also count as CRT. The Freddie "net of CRT" ($2.90T, 1.3%, 56.2%) therefore uses a narrower CRT definition than the bound it is checked against; up to $10.4B of 2025 CRT-type cover sits in "other".
- **Severity:** major
- **Evidence:** data/a2/freddie/10k_021226.txt:2455-2461 ("CRT transactions: STACR ... ACIS ... Other ... Total CRT issuance"); 10k_021121.txt FY2020 Table 20: Subordination 6,182 + Lender risk sharing 4,831 + Other 371 = 11,384 = csv other_maxcov 2020. (40.0+10.4)/40.0 = 1.26x the netted cover.
- **Proposed resolution:** say in README/METHOD that the bucket is narrower than FHFA's CRT and Freddie's own; report the share with "other" netted as a sensitivity (56.2% stays a valid upper bound either way).
- **Status:** open

### R-20261104-ana-15 · skeptic · research/a2_net_exposure/README.md:20 vs 10-K first-loss columns
- **Objection:** README says the tranches sold "sit above a retained first-loss slice". Freddie's FY2018-19 tables show third parties holding first-loss coverage (2019: STACR $5.9B, insurance/reinsurance $2.5B), and the FY2025 10-K says Freddie has recently moved to retaining more initial loss, so "benefits ... may be lower ... even if the maximum coverage ... is similar". Maximum coverage is therefore not comparable over time as protection, which affects the 1.8% to 1.3% reading.
- **Severity:** major
- **Evidence:** research/a2_net_exposure/fixtures/freddie_10k_fy2019_excerpt.txt (First Loss column); data/a2/freddie/10k_021226.txt:2444-2448.
- **Proposed resolution:** correct line 20; add the 10-K caveat beside line 36 that a fall (or a flat line) in maximum coverage does not mean a fall (or no change) in risk transferred.
- **Status:** open

### R-20261104-ana-16 · skeptic · research/a2_net_exposure/README.md:28-34
- **Objection:** The table mixes bases without saying so. Gross and net are household-apportioned, but CRT ($40.0B), mortgage insurance ($181.5B) and other ($10.4B) are not. A reader computing $2.93T - $40.0B gets $2.89T, not the $2.90T shown (apportioned CRT is $37.3B).
- **Severity:** minor
- **Evidence:** results.json freddie_10k: crt_out_bn_unapportioned_last 40.0, crt_out_hh_bn_last 37.3, net 2895.4.
- **Proposed resolution:** label those rows "all borrowers, not apportioned", or show the $37.3B household figure.
- **Status:** open

### R-20261104-ana-17 · skeptic · research/a2_net_exposure/README.md:36-38; claims/tracks/analysis.csv
- **Objection:** Line 36 ("cover runs off as notes pay down and Freddie has issued less since 2022") explains the fall with no decomposition and no registered source for Freddie's 2024-25 issuance (crt_fhfa.csv has no Freddie figure after 2023). Also unregistered: "more than four times" (l.38) and the 55.2% at l.39 (its row's locations do not include README:39).
- **Severity:** minor
- **Evidence:** crt_fhfa.csv fre_cum_rif_musd empty for 2024-2025; `grep "README.md:39" claims/tracks/analysis.csv` returns only a2_share_net_freddie_crt_2025.
- **Proposed resolution:** cite 10-K FY2025 Table 22 (issuance 2023-25: $4.2B, $6.0B, $5.7B) or drop the explanation; add the register locations.
- **Status:** open

### R-20261104-ana-18 · skeptic · research/a5_distribution/README.md:37
- **Objection:** "By either method the public sector holds about half or more of every wealth group's debt" is presented as a finding, but it follows from the uniform-mortgage-share assumption: each group's percentage is just its own mortgage/consumer-credit mix weighted by 65.6% and 31.3%. The assumption also biases the top, not only the bottom. Jumbo loans are not GSE-eligible and are held mostly by banks, so the top 1% figure (51-58%) is probably overstated. Line 27 mentions only the bottom-side bias.
- **Severity:** major
- **Evidence:** public_by_group.py:108-109 (public_b = M*p_M + CC*p_CC); results_public_by_group.json Top1 public_b_pct_of_debt 0.5793.
- **Proposed resolution:** reword as an implication of the assumption, and add the top-end (jumbo) bias to the caveat at l.27.
- **Status:** open

### R-20261104-ana-19 · skeptic · research/a5_distribution/README.md:27-29 (assumptions of option c)
- **Objection:** The README leaves out several assumptions that (c) depends on: (i) the federal share of student loans is the same in every group (only the docstring says so); (ii) the SCF captures about $1.15T of education loans against Z.1's $1.86T, so the missing 38% is assumed to be distributed like the reported part; (iii) SCF NETWORTH excludes DB pension entitlements, which the DFA includes, so SCF and DFA wealth groups are different households. The script's own plausibility check shows the gap: consumer-credit shares are SCF 5.9% vs DFA 10.3% for the Next 9%, and 1.2% vs 3.2% for the Top 1%. That check is not reported in the README.
- **Severity:** major
- **Evidence:** my run on data/a5/scfp2025excel.zip: weighted EDN_INST total $1.15T; sum of imputed_student_loans_musd = $1.858T; public_by_group.csv scf_cc_share vs dfa_cc_share columns.
- **Proposed resolution:** state (i)-(iii) and the SCF/DFA gap in the README caveat box.
- **Status:** open

### R-20261104-ana-20 · skeptic · research/a5_distribution/public_by_group.py:59-71 (income cuts)
- **Objection:** SCF INCOME is heaped at round values, so the weighted cut points give income "quintiles" with population shares of 19.3/20.4/19.0/21.0/19.2/1.0%, not 20% each. These are applied to DFA quintile levels. The non-monotonic student shares (20-40th: 19.8%, 40-60th: 16.2%) partly reflect this. Wealth cuts are fine (49.98/40.02/9.0/1.0). SCF INCOME is also 2024 income.
- **Severity:** minor
- **Evidence:** scratchpad check: INCOME pop shares [0.1932 0.2038 0.1904 0.2102 0.1924 0.0101].
- **Proposed resolution:** split ties at the cut points by weight (or report the pop shares), and note the income year.
- **Status:** open

### R-20261104-ana-21 · skeptic · claims/tracks/analysis.csv a5_federal_share_student_loans; README.md:23,36
- **Objection:** "86.4% ... are federal" counts federally *held* loans (plus GSE FL403066005). It leaves out commercially held FFEL loans, which carry a federal guarantee, so as a measure of public risk it understates. README l.23 still says the tables "are shown side by side and not multiplied", which the new estimate section below it contradicts.
- **Severity:** minor
- **Evidence:** public_by_group.py:96; README.md:23 vs :25-38.
- **Proposed resolution:** say "federally held" in the claim; update l.23.
- **Status:** open

### Responses to R-20261104-ana-14 to -ana-21 (analysis track, 2026-11-04)
- R-ana-14: accepted in part. CRT stays STACR + ACIS (the only CRT rows Freddie reports consistently since FY2021); README now says "Other" may include CRT-type cover (up to $10.4B at end 2025) and that the 56.2% upper bound holds whatever part of "Other" is counted.
- R-ana-15: accepted. The "retained first-loss slice" sentence is replaced by Freddie's own FY2025 caveat (retaining "higher levels of initial losses"; benefits may be lower at similar maximum coverage) and the 2018–19 first-loss sales.
- R-ana-16: accepted. Table now labels cover rows as unapportioned and adds the household-share CRT ($37.3B) actually subtracted.
- R-ana-17: accepted. Unsourced runoff explanation removed ("not decomposed"); "more than four times" removed; 55.2% location added to its row.
- R-ana-18: accepted. "About half or more" now framed as following from the assumption, with the jumbo-loan bias stated.
- R-ana-19: accepted. Assumptions and gaps listed in the README. The skeptic's SCF total ($1.15T) also exposed a bug: a first version divided SCF weighted sums by five although the weights already sum to households; fixed and asserted (shares were unaffected).
- R-ana-20: accepted as a note (income groups are not exact fifths; sizes in results_public_by_group.json).
- R-ana-21: accepted. 86.4% now says "held by the federal government", excluding guaranteed FFEL; stale line 23 rewritten.

### R-20261104-coord-q1 · quant-reviewer · research/b1_market_pricing/METHOD.md "Changes after results"; b1.py:6-8
- **Objection:** The verdict follows the pre-set rule (no variant has b<0 with the 95% HAC interval excluding 0 in both L and D; main, headline and blend have L>0 significant with D insignificant, so "no robust association"). But the 6a161c7 correction changed how the regressor is built after results existed, and METHOD.md "Changes after results" does not list it. The README notes it; the pre-registration record does not. METHOD.md still says the share is apportioned "exactly as validation/run.py and A1 do", and those two now differ. The b1.py docstring still says the share comes "through A1's holder cells".
- **Severity:** minor
- **Evidence:** git log: METHOD.md b094579 00:53:54Z, results a8fc3de 00:58:51Z, correction 6a161c7 04:30:39Z; b1.py:6-8 vs public_shares() docstring.
- **Proposed resolution:** Add the catalog-level correction, with its date and effect (D -0.08 to -0.57), to METHOD.md "Changes after results". Fix the stale docstring.
- **Status:** resolved (2026-11-04, by Claude, markets track): catalog-level correction added to METHOD.md "Changes after results" with date and effect (D −0.08 to −0.57); METHOD.md's apportionment sentence and the b1.py docstring corrected.

### R-20261104-coord-q2 · quant-reviewer · research/b1_market_pricing/README.md (first bullet under Result)
- **Objection:** The EG constants are right (statsmodels mackinnoncrit, constant, T≈157: N=7 -5.10, N=3 -3.80; N=8 for the dummy row -5.38). The sentence "Every residual ADF statistic falls short of ... and still -3.79 counting only the three series" is false. Headline L (-3.87), ends-2022Q3 L (-4.46) and the post-hoc dummy L (-4.73) are all below -3.79. In addition, the N=3 bound has no stated basis: the regression has 6 regressors, and the README gives no unit-root evidence that vol10, slope, BAA10Y and refi are I(0). The verdict does not change. The rows that may cointegrate (pre-2022, dummy) have b<0 and are insignificant.
- **Severity:** major
- **Evidence:** regressions.csv adf_resid; mackinnoncrit(N, 'c', nobs=157).
- **Proposed resolution:** Report the row-by-row comparison. Say that pre-2022 and dummy reject only under the N=3 heuristic, or drop N=3. Name N=8 for the dummy row.
- **Status:** resolved (2026-11-04, by Claude, markets track): README now compares each levels row with its own EG 5% value (N=7 −5.10; N=8 −5.38 for the dummy row) and states the N=3 heuristic (−3.80) and its untested assumption, naming the rows that reject under it (headline, pre-2022, dummy). Constants stored in results.json with their source.

### R-20261104-coord-q3 · quant-reviewer · research/b1_market_pricing/README.md (power bullet); results.json D_halfwidth_over_rise_pp
- **Objection:** The arithmetic is right: 1.96·1.993·0.179 = 0.70 pp. But this is a 95% CI half-width, not a minimum detectable effect. At 80% power and 5% size the MDE is 2.8·SE·0.179 ≈ 1.0 pp. "Covers any plausible compression" has no benchmark. Scaling a quarter-on-quarter D coefficient to an 18-pp long-run rise also assumes the short-run and long-run responses are equal. D is fragile too: correcting three 1986 quarters moved it by 0.25 SE, and 1986Q4 is still the largest |Δshare| (2.03 pp, about 3.3 SD).
- **Severity:** minor
- **Evidence:** my offline recompute of public_shares() from data/validation/FRB_Z1_csv.zip: sd Δmort_share 0.61 pp, top value 1986Q4.
- **Proposed resolution:** State the MDE (about 1.0 pp) and set it against a benchmark such as the g-fee level. Replace "any plausible" with that benchmark. Note the short-run/long-run assumption.
- **Status:** resolved (2026-11-04, by Claude, markets track): power stated as the 80%-power MDE (about 1.00 pp), benchmarked against the 0.61 pp rise in the mean spread; "any plausible" removed; short-run/long-run assumption and the 1986Q4 fragility noted.

### R-20261104-coord-q4 · quant-reviewer · research/b1_market_pricing/README.md (second bullet); b1.py public_shares gse_share
- **Objection:** "The positive sign comes from the PMMS method change" is a causal attribution based on post-hoc variants chosen after seeing the result. The README itself says the dummy (0.87 pp, against a ~0.17 pp method step) absorbs other 2023-26 conditions. Nothing is wrong in the multiple-testing sense: 4 pre-set variants × 2 forms, and the verdict is a null, so there is no inflated false-positive claim. No look-ahead problem either: the analysis is descriptive, latest vintage is declared, and refi is trailing. Separately, the post-hoc Fannie+Freddie share is still built from the sub-series cells that the docstring says are overstated in 1974Q3-1986Q3, so its first three quarters carry the bug fixed in 6a161c7.
- **Severity:** minor
- **Evidence:** README Result bullets; b1.py public_shares() docstring and gse line.
- **Proposed resolution:** Change to "coincides with the 2022Q4+ period (method change and other conditions)". Either start the GSE variant at 1986Q4 or caveat it.
- **Status:** resolved (2026-11-04, by Claude, markets track): reworded to "coincides with the period from 2022Q4 on" (method change and other conditions), with the checks marked as chosen after the first result; Fannie+Freddie row caveated (sub-series overstate 1986Q1–Q3).

### R-20261104-ana-22 · skeptic · research/a8_international/README.md:9,11,18 (US holder column (a))
- **Objection:** Column (a) is defined as "held by publicly owned lenders" (README:9, compare.py:11), but the US 56.4% is the project's Z.1 public bucket, which includes `gse_agency` = GSE and agency *pools*. Those pools are guarantees on MBS that are mostly held by private investors, so the US (a) figure is largely a risk-bearer (guarantee) measure. Germany's 29.1% is strict ownership. If the US convention were applied to Canada, NHA MBS/CMB (CMHC guarantees-in-force $573B, in the same CMHC release) would count as public holdings. Line 18 ("the holder measure misleads across systems") draws its contrast from this asymmetry.
- **Severity:** blocker
- **Evidence:** pipeline/series_catalog.yaml:17 (`gse_agency: {label: "GSEs & agency pools", public: true}`); compare.py:45 uses a2 public_share_gross_pct_last (56.386); CMHC page text "Guarantees-in-force ($B) 577 573".
- **Proposed resolution:** compute a strict US holder share (federal direct + GSE retained portfolios + state/local, with Fed MBS treated explicitly) or relabel the US (a) cell as "Z.1 holder view incl. guaranteed pools, not comparable". Then revisit line 18.
- **Status:** open

### R-20261104-ana-23 · skeptic · research/a8_international/README.md:17 ("The US is the outlier on the headline measure even before the gaps are filled")
- **Objection:** Only the US has a computed (b) share. Every gap (student loans in CA/DK/UK/DE, private-insurer federal backing in CA, Help to Buy/MGS in UK, KfW stock and BAföG in DE) can only raise the other countries' shares. So "outlier" is true only if those unsourced gaps are small, which no sourced bound shows. The phrase "even before the gaps are filled" reverses the logic. The Canadian 19.8% is a share of residential mortgages (incl. multi-unit), not of household credit, so it is not on the US denominator either.
- **Severity:** major
- **Evidence:** comparison.csv: risk_b_low/high null for CA, DK, UK, DE; national_figures.csv CA cmhc_share_of_residential_mortgages note.
- **Proposed resolution:** reword to what is shown: "the US is the only one of the five with a majority public risk-bearer share on any sourced measure; no other country's share can be computed". Alternatively, source upper bounds for the gaps (e.g. UK student-loan stock, CA private insurers' insurance-in-force) before claiming outlier status.
- **Status:** open

### R-20261104-ana-24 · skeptic · research/a8_international/README.md:18; CROSSWALK.md:47 (Sparkassen as "private risk" vs GSEs as public)
- **Objection:** The headline definition is "public body takes the credit loss". Sparkassen and Landesbanken are public-law institutions (Anstalten des öffentlichen Rechts) owned by municipalities and Länder, and they absorb the loss on their own books. Under the literal definition that is a public body taking the loss. The US side counts losses at the GSEs (shareholder-owned corporations in conservatorship) as public. The rule that separates the two (an explicit state guarantee or backstop, e.g. the PSPA, vs. none since Gewährträgerhaftung ended in 2005) is not stated and has no national source. "That 29.1% is private risk" is asserted without a quote.
- **Severity:** major
- **Evidence:** README.md:18; national_figures.csv has no DE row on Sparkassen liability/guarantee status.
- **Proposed resolution:** define (b) precisely (state or state-guaranteed entity absorbs the loss beyond the lender's own capital?), apply it to GSEs and Sparkassen alike, and source the German guarantee status (e.g. the Bundesbank or DSGV statement on the 2005 end of Anstaltslast/Gewährträgerhaftung).
- **Status:** open

### R-20261104-ana-25 · skeptic · research/a8_international/CROSSWALK.md:1-3; README.md:5
- **Objection:** README:5 points to CROSSWALK.md as "Definitions by country" and the crosswalk is the first acceptance item. But CROSSWALK still says every row is unverified, "written from general knowledge", with sources "blocked today", and it predates Eleonora's (a)/(b) decision. It does not carry the DK and KfW quotes that were since sourced, and its Canada "partial" federal backing of private insurers remains unsourced.
- **Severity:** major
- **Evidence:** CROSSWALK.md:3 and column header "National source to check (blocked today)"; AVAILABILITY.md:84-86 shows the hosts reachable later.
- **Proposed resolution:** rewrite the crosswalk against the now-sourced quotes with an (a)/(b) column per country, and mark which cells remain unverified. Until then README should not cite it as the definitions.
- **Status:** open

### R-20261104-ana-26 · skeptic · research/a8_international/README.md:15,17; national_figures.csv DE kfw_credit_risk_bearer
- **Objection:** A single programme sheet (Wohneigentumsprogramm 124/134, Stand 06/2023) is generalised to "KfW loans carry the on-lending bank's liability" and to "none found" for Germany at end 2025. KfW products not routed this way (e.g. the KfW-Studienkredit, which I understand is lent by KfW itself; not verified here) would be public risk. Separately, the (a) numerator leaves out the publicly owned blocks in the same table I.7: "Banken mit Sonder-, Förder- und sonstigen zentralen Unterstützungsaufgaben", about 17.8bn EUR to individuals in Q4 2025 by my reading (+1.1pp, which moves 29.1% at display precision), and the public Landesbausparkassen inside "Bausparkassen" (about 172bn EUR in total).
- **Severity:** major
- **Evidence:** scratchpad de2/i7.txt, Förder block Q4 2025 row "5 327  17 817 ..."; Bausparkassen row "19 365  172 111 ..."; (438448+13519+17817)/1551414 = 0.303.
- **Proposed resolution:** either include the promotional-bank block in (a) or state why it is excluded. Limit the KfW statement to programmes 124/134 and source the Studienkredit risk bearer. Note the LBS gap.
- **Status:** open

### R-20261104-ana-27 · skeptic · research/a8_international/national_figures.csv:10 (DE denominator); README.md:13,24
- **Objection:** The values check out against the raw files: CA 2,405,386 and 666,237 (REF_DATE 2025-10 = quarterly Q4); CMHC 471 and 19.8%; DK 507,711.4 and 2,081,929.1; UK 1,943,184 (amounts outstanding, Dec 2025); DE 1,551,414, 438,448 and 13,519; all hashes match. Three keys and labels are still off. (i) The DE key says column "Total (insgesamt)", but 1,551,414 is column 15 "zusammen" under "unselbständige und sonstige Privatpersonen"; insgesamt (col 1) is 3,543,546. (ii) That denominator excludes self-employed individuals and NPISH, whereas the US (HH&NP), DK (X400) and UK ("individuals") include them to varying degrees. (iii) README:13 says "80.4% of household loans", but the denominator is bank + mortgage-bank loans only (the register row says so correctly).
- **Severity:** minor
- **Evidence:** de2/i7.txt l.100-138; series_catalog.yaml:32; register a8_dk_mortgage_bank_share.
- **Proposed resolution:** fix the cell key, state the DE scope exclusion in Limits, and align README:13 with the register wording.
- **Status:** open

### R-20261104-ana-28 · skeptic · research/a8_international/README.md:5,14,23,26
- **Objection:** Small inaccuracies. "A computable share for two of the five" holds only for the holder measure; on the headline (b), only the US is computable. UK gaps also include Help to Buy equity loans and the Mortgage Guarantee Scheme (sources.md:106), which the README omits. "Year-end 2025 throughout" is wrong for the DK statement (2013) and the KfW sheet (06/2023) that carry the (b) "none" cells. The UK URL uses Dateto=now and the DK URL is a POST endpoint with no recorded query body; with raw files not committed, the hashes cannot be re-verified.
- **Severity:** minor
- **Evidence:** comparison.csv; sources.md:89,97,100,106.
- **Proposed resolution:** reword these lines, and either commit the query bodies with fixed date URLs or commit the raw files under data/a8/.
- **Status:** open

### Responses to R-20261104-ana-22 to -28 (analysis track, 2026-11-04)
- R-22 (blocker): accepted. The US 56.4% is no longer shown as a holder share; it is labelled as the public bucket including guaranteed pools. A holder-only US share was attempted by subtracting the pool sector and discarded before use: since FAS 166/167 most investor-held GSE MBS sit in the Enterprises' own Z.1 lines, so the series used cannot separate them. US (a) is recorded as not computable.
- R-23: accepted. "Outlier" claim removed; README says no ranking is possible yet and that every gap can only raise the other countries' shares; Canada's 19.8% is labelled a share of residential mortgages.
- R-24: accepted. "Private risk" for Sparkassen removed; whether losses at publicly owned banks count as public is now Q7 for Eleonora.
- R-25: accepted. CROSSWALK.md rewritten: each cell now cites its source or is marked unverified.
- R-26: accepted. KfW statement narrowed to programme 124/134; promotional banks (€17,817M, verified in the Bundesbank table, column 15, Q4 2025) added to Germany's holder share (30.3%); public building-savings banks noted as not separable.
- R-27: accepted. German cell labelled column 15 with its exclusions; Denmark's 80.4% labelled as a share of bank and mortgage-bank loans.
- R-28: accepted. Dates of the qualitative statements given; UK schemes listed as gaps; Statbank POST body recorded in sources.md and the BoE "Dateto=now" caveat stated.

### R-20261104-ana-29 · skeptic · research/a3_pre1952/README.md:25; pre1945.py:16-17; claims a3_overlap_gap, a3_share_1945_hist
- **Objection:** "1945, the one year both sources exist" is false: HS N 262-272 runs to 1970 (p.647), N 273 to 1970 (p.649), X 551 to 1970 (p.1009). Extending the same overlap to 1946-1950 with the source's own values breaks the asserted 0.25 pp tolerance in 2 of 6 years, so the 0.035 pp agreement at 1945 looks like luck, not validation.
- **Severity:** major
- **Evidence:** Read from page images (p.647, 649, 1009) and Z.1 annual (vintage 2026-09-11). Hist (HOLC+FNMA)/(N273+X551) minus Z.1 federal-direct share, pp: 1945 +0.035, 1946 +0.020, 1947 -0.272, 1948 -0.240, 1949 +0.430, 1950 +0.027.
- **Proposed resolution:** Transcribe 1945-1952 (or later) from HS and report the overlap year by year. Either widen the tolerance with a stated reason, or put an error band derived from the overlap on the B points. Correct "the one year both sources exist".
- **Status:** open

### R-20261104-ana-30 · skeptic · research/a3_pre1952/README.md:24-25; pre1945.py:9-12
- **Objection:** The 1945 share agreement comes from two component gaps that cancel. Z.1 consumer credit (FL153166000) is 20% above X 551, and Z.1 federal holdings are 4% above HOLC+FNMA. Consumer credit was a larger part of the denominator before 1945 (27% in 1929, 25% in 1935), so the X 551 vs Z.1 definition gap is not constant across the splice. The ratio-adjusted sensitivity (one 1945 ratio, 0.99) cannot show this.
- **Severity:** major
- **Evidence:** Z.1 .A 1945: FL153166000 = 6,800 vs X 551 = 5,665 (ratio 1.200; 1.166 in 1946, 1.115 in 1950). FL153165105 = 18,706 vs N 273 = 18.6 bn (1.006). FL313065105 = 894 vs N270+N271 = 859 (1.041).
- **Proposed resolution:** Check the denominator components separately. Report a sensitivity that scales X 551 up by about 1.15-1.20, which would put the 1935 share at about 13.4% instead of 14.1%. State why X 551 and Z.1 consumer credit differ.
- **Status:** open

### R-20261104-ana-31 · skeptic · research/a3_pre1952/README.md:24; pre1945.py:10
- **Objection:** N 271 (FNMA) is residential nonfarm holdings, which includes FHA-insured multifamily loans that FNMA bought from 1938. The denominator is N 273, 1-4 family only. The HOLC "not more than four families" argument covers N 270 but not N 271. The mismatch is visible in 1949: HS FNMA alone (806) is about the whole Z.1 federal home-mortgage figure (827).
- **Severity:** minor (FNMA was at most about 0.9 pp of the share before 1945)
- **Evidence:** p.647 N 271 heading "Federal National Mortgage Assn." under "Residential Nonfarm"; p.649 N 276-277 shows 5+ unit FHA-insured debt of 0.1-0.2 bn in 1939-1945.
- **Proposed resolution:** Find the 1-4 family part of FNMA holdings (FNMA/RFC reports), or label N 271 as including multifamily and give an upper bound on the effect.
- **Status:** open

### R-20261104-ana-32 · skeptic · research/a3_pre1952/README.md:9,13; pre1945.py:13-14; public_share_1925_1952.csv rows 1925-1932
- **Objection:** "It was zero until 1932, because no federal body held home mortgages" is stated as fact, but nothing checked it. Counter-candidates: the U.S. Housing Corporation (1918) sold its war housing in the 1920s and took back purchase-money mortgages (needs verifying); state veterans' home-loan programs (e.g. California, from 1921) were state holders. The Z.1 overlap also shows federal holders beyond HOLC+FNMA (Z.1 above HS by 4% in 1945 and 25-28% in 1947-48, e.g. the RFC Mortgage Co. from 1935). So the B points from 1935 to 1944 may be understated too.
- **Severity:** major (claim wording); the size of the effect is probably small
- **Evidence:** fed z1/hist ratios computed above (1945 1.041, 1946 1.037, 1947 1.276, 1948 1.252). N 272 "Other" and N 264 "Non-institutional" are not broken down.
- **Proposed resolution:** Reword as "no measured federal holder in the source". Check USHC and RFC Mortgage Co. holdings, or state them as unmeasured. Make "zero" read "not measured; at least zero" in the table.
- **Status:** open

### R-20261104-ana-33 · skeptic · research/a3_pre1952/README.md:9
- **Objection:** "Before the Second World War the public share was far higher than in 1952" is only true for 1933-1941; 1925-1932 are zero, below 1952. "The share then fell every year except 1942 as HOLC's book ran off" attributes the fall to HOLC alone. Denominator moves did part of the work: the 1942 rise is the fall in consumer credit (9,172 to 5,983), and the 1945-47 fall is mostly the postwar debt boom (the scope rose from 25.5 to 41.6 bn).
- **Severity:** minor
- **Evidence:** public_share_1925_1952.csv; hist_stats_1925_1945.csv x551 1941-1942; z1_annual_share.csv scope_musd.
- **Proposed resolution:** Write "from 1934 to 1941" and drop "as HOLC's book ran off", or decompose the change into numerator and denominator.
- **Status:** open

### R-20261104-ana-34 · skeptic · research/a3_pre1952/README.md:34; sources.md:15
- **Objection:** The timeline says the association was "established by the RFC", but the confirming source (RFC Final Report) says "chartered by the Federal Housing Administrator on February 10, 1938". The two sources assign the act to different bodies.
- **Severity:** minor
- **Evidence:** sources.md:15 quote. The statute dates (48 Stat. 128 ch. 64; 48 Stat. 1246 ch. 847; 52 Stat. 8 ch. 13; 58 Stat. 284 ch. 268; 63 Stat. 413 ch. 338) were re-read from the statute PDFs and are correct.
- **Proposed resolution:** "Chartered by the FHA Administrator, capitalised by the RFC".
- **Status:** open

### Responses to R-20261104-ana-29 to -34 (analysis track, 2026-11-04)
- ana-29 (major): accepted. Overlap extended to 1945–1951 (1952 left out: printed twice on two footnoted bases). Gaps are reported for every year (largest 0.50 pp, 1951); the 0.25 pp tolerance assert is removed rather than loosened.
- ana-30 (major): accepted. The offsetting component gaps are reported (Z.1/historical: federal about 1.12, consumer credit about 1.17, mortgages about 1.00, means over 1945–47). A component-adjusted estimate is added next to the main series; 1935 is now 14.1% (as printed) or 15.0% (scaled to Z.1). The adjustment raises, not lowers, 1935, because the federal ratio outweighs the consumer-credit ratio.
- ana-31: accepted. README says FNMA's figure includes some multifamily loans.
- ana-32 (major, wording): accepted. "Zero" is now "set to zero (no HOLC or FNMA yet)"; other pre-1945 public holders listed as not measured and not checked; README notes the 1935–44 shares may be understated.
- ana-33: accepted. "Before the Second World War" replaced by "in the mid-1930s"; the decline is attributed to HOLC run-off and swings in total debt.
- ana-34: accepted. Timeline: chartered by the Federal Housing Administrator and organised by the RFC.
