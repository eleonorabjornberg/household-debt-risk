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

<!-- Analysis-track entries (A2, A5), merged 2026-11-04 from tracks/analysis-review-log.md; renumbered with an ana- infix because the track's R-20261104-1..13 collided with the coordinator's A1 entries. -->

Review entries from the analysis track; the coordinator moves them into `claims/review-log.md` on merge (renumbering if ids collide).

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
- R-ana-20261104-ana-1: accepted. Table header and register rows now say "net of CRT only, mortgage insurance not netted"; README states 55.2% is not a floor once MI is netted.
- R-ana-20261104-ana-2: accepted. Table header now says principal less CRT loss capacity; register claims say "RIF subtracted from principal".
- R-ana-20261104-ana-3: accepted. The FHFA "majority" quote is now attributed to CRT and mortgage insurance together; the unsourced "most stress losses fall" clause is removed.
- R-ana-20261104-ana-4: accepted. README quotes FHFA's "not strictly comparable".
- R-ana-20261104-ana-5: accepted. README and METHOD now give all three reasons (paid-off loans kept at issuance balance, refinanced loans counted again, STACR/ACIS sharing a pool).
- R-ana-20261104-ana-6: noted, not changed. The column is unused; the basis column already says the 2018–19 PMI UPB is the rounded text figure.

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
