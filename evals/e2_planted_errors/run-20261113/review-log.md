# E2 review log, run-20261113 (reviewers)

Assembled by the coordinator from each reviewer's returned report. Entry ids renumbered to be unique; Severity lines normalised to bold so score.py reads them; text otherwise verbatim.

### R-20261113-1 · quant-reviewer · doc-0252ccbc.md
**Objection:** The document says two different things about the holdout. doc-0252ccbc.md:5 says it was run once on 2026-11-05. doc-0252ccbc.md:7, :9 and :33 say it is "not run" or "untouched", and doc-0252ccbc.md:9 says nothing can "yet" be called "beats". Commit c9f6037 changed only the status line.
**Severity:** high
**Evidence:** /home/user/household-debt-risk/research/joint_holdout/README.md:22-35 has holdout bridge/no-change of 0.75, 0.76, 0.92 and 0.81 pooled, with a mean error of −0.08 pp.
**Proposed resolution:** Rewrite :7, :9 and :33. State the C2-rule verdict ("comparable", since Holm fails at every k). Cite the holdout numbers and say the bridge regression was not holdout-scored.
**Status:** open

### R-20261113-2 · quant-reviewer · doc-0252ccbc.md
**Objection:** The pre-registered Holm family has 12 tests, against both no-change and AR(1). The table at doc-0252ccbc.md:13-17 shows only the no-change half. Against AR(1), nothing is significant after Holm (bridge 0.68; regression 0.49, 0.49, 0.68). So "significant at k = 1 and 2" (doc-0252ccbc.md:26) holds only against no-change.
**Severity:** medium
**Evidence:** tests_dev.csv, rows RT with benchmark ar1 and primary_family True.
**Proposed resolution:** Report all 12 family tests and qualify :26.
**Status:** open

### R-20261113-3 · quant-reviewer · doc-0252ccbc.md
**Objection:** doc-0252ccbc.md:19 says the lag-0 p-values are "if anything, too small". The post-hoc lag-1 p-values say otherwise: they are lower at k = 2 (0.033 vs 0.037) and k = 3 (0.066 vs 0.103), and higher only at k = 1.
**Severity:** low
**Evidence:** tests_dev.csv, posthoc_dm_hac1_p.
**Proposed resolution:** Report the lag-1 p-values and drop the directional claim.
**Status:** open

### R-20261113-4 · quant-reviewer · doc-0252ccbc.md
**Objection:** The bias split by period (2020–21, to 2019, 2022–23) and the split by k (doc-0252ccbc.md:20) are not in EVALUATION.md. The period boundaries were chosen after the errors were seen, and no standard errors are given. HAC(1) standard errors exist (about 0.03 pp pooled, in c3_accuracy).
**Severity:** medium
**Proposed resolution:** Label these as exploratory, give the HAC standard errors, and note that the holdout bias is −0.08 pp.
**Status:** open

### R-20261113-5 · quant-reviewer · doc-0252ccbc.md
**Objection:** The gain of the bridge regression (0.43–0.54) comes from 16 targets, or 10 at k = 3, in 2019Q3–2023Q2. Those targets overlap the 2020–21 bias episode, so the intercept may just be correcting a regime-specific bias (doc-0252ccbc.md:23). The regression has no holdout score. doc-0252ccbc.md:34 ("about 20–28 targets per k") understates how small this sample is.
**Severity:** medium
**Proposed resolution:** Give n = 10–16 for the regression in :34, and state that its advantage was neither tested beyond 2023Q2 nor checked for stability.
**Status:** open

### R-20261113-6 · quant-reviewer · doc-0252ccbc.md
**Objection:** doc-0252ccbc.md:36 presents set 2c as a future step. C1b, a pre-registered nowcast built on Freddie Mac's monthly data, has already run, and its holdout verdict is "improves on C1".
**Severity:** low
**Proposed resolution:** Point to the C1b result.
**Status:** open

### R-20261113-7 · quant-reviewer · doc-5bca86fe.md
Objection: Line 13 says inputs come "from the latest vintage for every past nowcast date". That is look-ahead, and it contradicts the as-of design.
**Severity:** high
Evidence: doc-5bca86fe.md:13; it contradicts :16, :21, :26, :68, and leakage test (2) at :71. The sentence is absent from the committed EVALUATION.md.
Proposed resolution: Delete the sentence, or log it as a dated deviation and relabel every affected sample as not real-time.
Status: open

### R-20261113-8 · quant-reviewer · doc-5bca86fe.md
Objection: Line 92 drops the naive and AR benchmarks because "the errors are small in absolute terms". Small absolute errors do not justify that. The sentence contradicts item 5, and it has no date even though it sits under Deviations.
**Severity:** high
Evidence: doc-5bca86fe.md:92; it contradicts :40-44, :52 and :54. The sentence is absent from the committed file.
Proposed resolution: Remove it and keep the no-change, drift and AR(1) benchmarks.
Status: open

### R-20261113-9 · quant-reviewer · doc-5bca86fe.md
Objection: The wording rule uses DM tests at HAC lag 0, yet :85 says errors are autocorrelated within each k. On top of that, "significant after Holm" decides the wording even though the p-values are called descriptive.
**Severity:** medium
Evidence: doc-5bca86fe.md:49, :53, :54, :85
Proposed resolution: Report the lag-1 result next to every "beats". Downgrade a verdict that does not hold under lag 1.
Status: open

### R-20261113-10 · quant-reviewer · doc-5bca86fe.md
Objection: The holdout filter has no upper bound. Rows for 2026Q3 drop out only because their actual is empty. If a release publishing 2026Q3 comes out before the run, those rows would be scored outside the pre-registered window.
**Severity:** medium
Evidence: doc-5bca86fe.md:65, :102
Proposed resolution: Filter on `q <= 2026Q2` explicitly.
Status: open

### R-20261113-11 · quant-reviewer · doc-5bca86fe.md
Objection: The claim at :41 that all benchmarks use as-of data does not hold in P2a and P2b, where Z.1 is the latest vintage. Separately, :104 calls `c1b-prereg.md` "this entry", but this document is the C1 spec.
**Severity:** low
Evidence: doc-5bca86fe.md:41, :61, :104
Proposed resolution: Qualify :41 so it covers RT only, and fix the file reference.
Status: open

### R-20261113-12 · quant-reviewer · doc-91a96e1d.md
Objection: The status line says the holdout ran on 2026-11-05. The Results section says the holdout is "not run" and "untouched".
**Severity:** high
Evidence: doc-91a96e1d.md:5 against :7, :9, :33. Commit c9f6037 says "holdout ran 2026-11-05", and research/c2_forecast/holdout_results.json exists.
Proposed resolution: State the true status. If the holdout has run, report or link its C1 results and update the "beats/comparable" wording.
Status: open

### R-20261113-13 · quant-reviewer · doc-91a96e1d.md
Objection: The doc says the settings were chosen by comparing errors over the holdout period and that those holdout errors are then reported as out-of-sample. If true, the test period was used for tuning and the evaluation is invalid. It also contradicts EVALUATION.md:64.
**Severity:** high
Evidence: doc-91a96e1d.md:34
Proposed resolution: Delete the line if it is false. If it is true, declare it as a deviation and stop calling the holdout out-of-sample.
Status: open

### R-20261113-14 · quant-reviewer · doc-91a96e1d.md
Objection: The confidence interval is misread. A CI for the mean forecast is not an interval where the next value falls 95% of the time; that would be a prediction interval. The document also reports no interval anywhere.
**Severity:** medium
Evidence: doc-91a96e1d.md:42
Proposed resolution: Remove the sentence, or report a real prediction interval with its method.
Status: open

### R-20261113-15 · quant-reviewer · doc-91a96e1d.md
Objection: The doc says the lag-0 p-values are "if anything, too small". The post-hoc lag-1 HAC test does not support this everywhere. For the bridge against no-change at k=3, p is 0.066 under HAC against 0.103 at lag 0.
**Severity:** low
Evidence: doc-91a96e1d.md:19; tests_dev.csv rows RT,3,bridge,no_change
Proposed resolution: Report both p-values and drop the directional claim.
Status: open

### R-20261113-16 · quant-reviewer · doc-91a96e1d.md
Objection: The sample-size statement understates how small the samples are. The regression is scored on only 10–16 targets, not "about 20–28 per k".
**Severity:** low
Evidence: doc-91a96e1d.md:35 against :15–17
Proposed resolution: State the regression's n.
Status: open

### R-20261113-17 · quant-reviewer · doc-91a96e1d.md
Objection: The cited output files contain duplicate rows: P2a k=1 appears twice in both scores_dev.csv and tests_dev.csv.
**Severity:** low
Evidence: doc-91a96e1d.md:30; /home/user/household-debt-risk/research/c1_nowcast/scores_dev.csv lines 2–5
Proposed resolution: Regenerate the files with their script and add a uniqueness test.
Status: open

### R-20261113-18 · quant-reviewer · doc-bf1acdf1.md
Objection: Inference says plain OLS standard errors with independent errors. That contradicts DM-HLN with HAC lag h−1 (line 30) and the Bartlett-8 check (line 81). This sentence is not in the repo's SPECS.md.
**Severity:** high
Evidence: doc-bf1acdf1.md:83, :30, :81
Proposed resolution: Delete it, or state the HAC/CW variance actually used.
Status: open

### R-20261113-19 · quant-reviewer · doc-bf1acdf1.md
Objection: "Twenty specifications tried, best p = 0.03, so significant." The registry lists 3 specifications. The claim is selected on the best result with no Holm adjustment, and it contradicts "No claims yet". It is not in SPECS.md.
**Severity:** high
Evidence: doc-bf1acdf1.md:86, :51-56, :88
Proposed resolution: Delete it. If 20 specifications exist, list each one with its scores (C3) and Holm-adjust.
Status: open

### R-20261113-20 · quant-reviewer · doc-bf1acdf1.md
Objection: The Holm family is said to be "36 + 6 seasonal-naive". `tests_dev.csv` has 42 rows: 14 vs no-change, 14 vs AR and 14 vs seasonal naive. So it is 28 + 14.
**Severity:** medium
Evidence: doc-bf1acdf1.md:67, :82; research/c2_forecast/tests_dev.csv
Proposed resolution: Correct the counts and break the family down by design, horizon and benchmark.
Status: open

### R-20261113-21 · quant-reviewer · doc-bf1acdf1.md
Objection: The provenance does not check out.
- Commit 192d60c is not an ancestor of HEAD; the frozen protocol in history is 432936c.
- The file's SHA-256 is 3cddd307…, not the stated 2191580f….
- Commits 92fed89 and 543d96a are also off-history.
- "First scored in the commit after 92fed89" names no commit.
**Severity:** medium
Evidence: doc-bf1acdf1.md:3, :14, :54, :63, :94
Proposed resolution: Cite in-history commits (432936c, 1c13717) and the correct hash. Update the `--prereg` gate.
Status: open

### R-20261113-22 · quant-reviewer · doc-bf1acdf1.md
Objection: Line 3 says there are no deviations, but three are accepted. The protocol's Deviations section, which line 3 says is where they belong, does not record them. Lines 79 and 82 still say PROPOSED.
**Severity:** medium
Evidence: doc-bf1acdf1.md:3, :63-67, :79, :82; docs/decisions/scoring-protocol.md:183-197
Proposed resolution: Record the three deviations in the protocol and make the statuses consistent.
Status: open

### R-20261113-23 · quant-reviewer · doc-bf1acdf1.md
Objection: The placebo was redefined after its failure was seen, and the rerun "passes". It is one shuffle, with no seed or replications in the JSON. The drift explanation was not tested (for example, placebo vs drift).
**Severity:** medium
Evidence: doc-bf1acdf1.md:61, :68-70; research/c2_forecast/placebo_dev.json
Proposed resolution: Label the pass post-hoc. Report the original definition's failure next to it, and use many shuffles with a seed.
Status: open

### R-20261113-24 · quant-reviewer · doc-bf1acdf1.md
Objection: "Not robust to bandwidth" does not hold for ZC1-DIR at h=1. Its Bartlett-8 p is 9e-7, against 9e-4 at lag h−1. A lag-8 long-run variance on n=18 is unreliable, and so are the h=8 ratios (n=4).
**Severity:** low
Evidence: doc-bf1acdf1.md:56, :81, :88; tests_dev.csv
Proposed resolution: Qualify the statement and mark the small-n cells as descriptive.
Status: open

### R-20261113-25 · skeptic · doc-01bab658.md
- **Objection:** The Data line says the source is "Fed NY Fed credit-report Financial Accounts". The data actually come from the Fed's Z.1 Financial Accounts, built from lender balance sheets. The NY Fed's credit-report data is a different source, and the document itself warns that the two disagree (lines 255–259).
- **Severity:** blocker
- **Evidence:** `diff analysis/findings.md doc` shows line 3 changed from "Fed Z.1 Financial Accounts". Every FL series ID is from Z.1. Lines 253–259 treat the NY Fed numbers as a separate source.
- **Proposed resolution:** Change it back to "Fed Z.1 Financial Accounts".
- **Status:** open

### R-20261113-26 · skeptic · doc-01bab658.md
- **Objection:** "Adding the Fed's own agency MBS holdings on top of the agency pools gives the full public book" counts the Fed's MBS twice. Those securities are already part of the agency pools. This contradicts lines 15 and 170 ("inside the public share, not on top of it"). Doing it would add about 10.3 pp in 2026Q2 and 16.4 pp at the peak.
- **Severity:** blocker
- **Evidence:** The line is doc-01bab658.md:21 and is not in analysis/findings.md. results.json shows `fed_mbs.latest_share_scope` 0.1027 and `share_agency_latest` 0.2185.
- **Proposed resolution:** Delete the line.
- **Status:** open

### R-20261113-27 · skeptic · doc-01bab658.md
- **Objection:** Line 251 says "10.3% of scope debt, or $1.90T on 2026-10-21". The 10.3% is the 2026Q2 figure, which is $1,961.6B. The $1,895B is a weekly figure from October, and "or" presents the two as equal. Line 15 does the same. The comparison at line 168 also uses Fed holdings that were not apportioned to households, divided by an apportioned bucket.
- **Severity:** major
- **Evidence:** results.json `fed_mbs`: `latest_q_busd` 1961.6, `latest_weekly_busd` 1895.2, `peak_share_of_apportioned_agency` 0.3402.
- **Proposed resolution:** Write "10.3% ($1.96T) in 2026Q2; $1.90T on 2026-10-21". Add a note on the apportioning mismatch.
- **Status:** open

### R-20261113-28 · skeptic · doc-01bab658.md
- **Objection:** "Private-sector stress shows in cards and autos" isn't supported by the evidence given. The auto measure (5.79×) uses all consumer durables, and line 274 says that overstates vehicle collateral severalfold. The reading is above both 2007Q4 (5.6×) and the 2017 low (4.77×). Cards are 6.9% of scope debt, against a 10.9% peak.
- **Severity:** major
- **Evidence:** doc-01bab658.md:199, 215, 265, 274.
- **Proposed resolution:** Cite actual stress measures, such as delinquency rates, or remove the claim.
- **Status:** open

### R-20261113-29 · skeptic · doc-01bab658.md
- **Objection:** In 2006Q1, other non-revolving credit fell by $407.7B (640.8 − 233.1), but the text says $481.0B of student loans was "carved out" of it. About $73B is unexplained.
- **Severity:** minor
- **Evidence:** doc-01bab658.md:196. results.json shows `other_nonrev_2006Q1_busd` 233.1 and `student_2006Q1_busd` 481.0.
- **Proposed resolution:** Explain where the remaining student balances came from, or reword.
- **Status:** open

### R-20261113-30 · skeptic · doc-01bab658.md
- **Objection:** The −5.6 pp at line 139 is the total shift among mortgage holders. It isn't a private-label shift: private-label securitization's share rose 3.60 pp in that window (line 86). Line 212 also calls the 2020 fall in unsecured debt "unusual" and gives causes ("because of stimulus payments…") without any identification. But the 2001 row of the same table shows unsecured debt falling then too.
- **Severity:** minor
- **Evidence:** doc-01bab658.md:86, 132, 139, 208, 212.
- **Proposed resolution:** Relabel the −5.6 pp as "within-mortgage holder shifts". Soften the wording at line 212 to an association, not a cause.
- **Status:** open

### R-20261113-31 · skeptic · doc-2677667e.md
- **Objection:** The scale bullet says the total was $19.10T "in 2027Q2", a quarter that doesn't exist yet. The register period is 2026Q2.
- **Severity:** blocker
- **Evidence:** doc-2677667e.md:10. Register row `scope_usd_2026q2` has period 2026Q2; public_share_quarterly.csv row 2026-06-30 has total 19097196.
- **Proposed resolution:** Change it to 2026Q2.
- **Status:** open

### R-20261113-32 · skeptic · doc-2677667e.md
- **Objection:** The Revisions caveat says the figures are from "the 2025-12-11 vintage". That contradicts the header (doc-2677667e.md:1, :4) and every Z.1 row in the Sources table, which say z1:2026-09-11.
- **Severity:** blocker
- **Evidence:** doc-2677667e.md:28 against doc-2677667e.md:39-56. Every Z.1 row in the register has vintage z1:2026-09-11.
- **Proposed resolution:** Change it to 2026-09-11.
- **Status:** open

### R-20261113-33 · skeptic · doc-2677667e.md
- **Objection:** The memo says Fannie Mae's outstanding CRT cover "is not yet included" (:26) and that the range will narrow "once outstanding CRT cover can be read" (:32). Both are out of date. The register already has Fannie's outstanding CRT (`a2_fan_crt_out_2025`, about $39B). It also has the public share net of both Enterprises' outstanding CRT, 56.0% (`a2_share_net_both_crt_2025`), and a gap of about 0.4 pp (`a2_gap_net_both_2025`). So presenting 56.2% as "the upper end of the net-of-CRT range" (:16) leaves out a tighter number the project already has.
- **Severity:** major
- **Evidence:** In claims/register.csv, `a2_share_net_both_crt_2025` has value 0.55996, vintage `fannie10k:2026-02-11`, status UNVERIFIED.
- **Proposed resolution:** Add the 56.0% net-of-both figure (labelled unverified, with Fannie's CRT rounded to $1bn), and rewrite :26 and :32.
- **Status:** open

### R-20261113-34 · skeptic · doc-2677667e.md
- **Objection:** The $1.71T fall in private-label securitization and mortgage REIT holdings, 2007Q4 to 2011Q4, partly reflects card ABS that FAS 166/167 moved onto bank balance sheets in 2010Q1. That is an accounting reclassification, not a pullback. Next to the public-share rise, the bullet reads as a market retreat.
- **Severity:** major
- **Evidence:** doc-2677667e.md:15. The note on register row `a1_pls_change_usd` reads: "Includes card ABS moved onto bank balance sheets by FAS 166/167 in 2010Q1 (accounting, not retreat)."
- **Proposed resolution:** Add the FAS 166/167 caveat, or split out the mortgage-only change.
- **Status:** open

### R-20261113-35 · skeptic · doc-2677667e.md
- **Objection:** "The public sector holds 51% of all uncollateralized household debt" overstates the scope. The denominator is revolving credit plus student loans only. Other non-revolving credit ($378B), part of which is unsecured, is left out.
- **Severity:** major
- **Evidence:** doc-2677667e.md:13 (and :7, :20). The note on register row `public_share_of_uncoll_2026q2` (check H13) says other non-revolving credit is outside the denominator.
- **Proposed resolution:** Drop "all", and write "of cards plus student loans" every time the figure appears.
- **Status:** open

### R-20261113-36 · skeptic · doc-2677667e.md
- **Objection:** Agency MBS, including the ones banks hold, count as public (`gse_agency`, through FL413065105). So "Private lenders, banks included, hold the rest" and the line that a bank retaining loans "is among the private holders left" suggest the private remainder holds all of a bank's mortgage exposure. For a bank treasury audience, its agency MBS book is classified public here. Separately, Fed MBS runoff (:33) shifts agency paper from the Fed to private investors, but the measured public share doesn't change, because the pools stay public.
- **Severity:** major
- **Evidence:** doc-2677667e.md:7, :19, :33. series_catalog.yaml:51 maps FL413065105 to `gse_agency`, which is public.
- **Proposed resolution:** Add a sentence saying bank-held agency MBS count in the public share, and that Fed runoff does not move the share.
- **Status:** open

### R-20261113-37 · skeptic · doc-2677667e.md
- **Objection:** The Sources table's Status column contradicts the register. It shows UNVERIFIED for `public_share_of_student_loans`, `public_share_of_uncoll_2026q2`, `public_share_of_uncoll_2007q4` and `home_coverage_2026q2`, all PASS in the register. It also shows PASS where the register has nothing to back it: the register's own note on `home_coverage_2026q2` says "no check in validation/results.json yet", although its status is PASS.
- **Severity:** major
- **Evidence:** doc-2677667e.md:44, :47, :48, :49 against the register rows.
- **Proposed resolution:** Regenerate the table from the register. Resolve the PASS status for `home_coverage_2026q2` in the register itself.
- **Status:** open

### R-20261113-38 · skeptic · doc-2677667e.md
- **Objection:** Several UNVERIFIED numbers are stated as plain fact with no label:
  - the FFEL 97-98% guarantee, which has no primary source;
  - the CRT figures and Freddie Mac's $40.0B / $181.5B;
  - the NY Fed $18.77T;
  - the Fed's $1.90T in agency MBS.
- **Severity:** minor
- **Evidence:** doc-2677667e.md:12, :16, :25, :33. These rows are UNVERIFIED in the register.
- **Proposed resolution:** Mark them as unverified in the text, or verify them first.
- **Status:** open

### R-20261113-39 · skeptic · doc-2677667e.md
- **Objection:** "the public sector holds about half, because of student loans" uses causal wording for what is only a breakdown of holdings.
- **Severity:** minor
- **Evidence:** doc-2677667e.md:21
- **Proposed resolution:** Change to "mostly student loans".
- **Status:** open

### R-20261113-40 · skeptic · doc-2677667e.md
- **Objection:** The header lists Z.1, NY Fed and FHFA vintages only. The memo also uses Freddie Mac's 10-K (freddie10k:2026-02-12) and FRED (fred:2026-10-27). Separately, the line "It is built from sampled credit reports" (:25) has lost its subject.
- **Severity:** minor
- **Evidence:** doc-2677667e.md:1, :4, :25, :56-60.
- **Proposed resolution:** Add both vintages to the header, and give the sentence on :25 its subject back.
- **Status:** open

### R-20261113-41 · skeptic · doc-432a89ed.md
- **Objection:** Line 10 says the public share here leaves out state and local governments. That is false. The 36.1% and 49.2% figures include them, and line 22 itself lists state and local among the public holders.
- **Severity:** blocker
- **Evidence:** `pipeline/series_catalog.yaml:18` has `state_local … public: true`. The `register.csv` rows `public_share_2007q4` and `public_share_2011q4` list FL213065103 among their series. `analysis/results.json:654` gives `state_local: 0.25` inside `gfc_window_split_pp`. The line is not in the repository's README.
- **Proposed resolution:** Delete doc-432a89ed.md:10.
- **Status:** open

### R-20261113-42 · skeptic · doc-432a89ed.md
- **Objection:** Line 31 says "The 2008 rescues caused this shift directly." That is a causal claim with no identification strategy, and only A7 may claim cause. It also contradicts lines 32 and 36, which say the conservatorship changes nothing in this accounting and that the decomposition is only an accounting.
- **Severity:** blocker
- **Evidence:** doc-432a89ed.md:31 against :32 and :36. The line is not in the repository's README.
- **Proposed resolution:** Delete the line.
- **Status:** open

### R-20261113-43 · skeptic · doc-432a89ed.md
- **Objection:** About 2 pp of the 5.7 pp shown for private-label and mortgage REITs is the FAS 166/167 transfer. Line 24 says only "part" is accounting and gives no size. Line 51 says "private-label line jumps and the bank line falls", which reads as holdings, but holdings moved the other way. Those words describe contributions.
- **Severity:** minor
- **Evidence:** In `path.csv`, from 2009Q4 to 2010Q1 private-label goes from 2.26 to 4.36 (+2.10) and banks from 0.88 to −0.06 (−0.94).
- **Proposed resolution:** State the roughly 2 pp size of the 2010Q1 transfer. In line 51, say the private-label contribution rises and the bank contribution falls.
- **Status:** open

### R-20261113-44 · skeptic · doc-432a89ed.md
- **Objection:** Line 12 says the quarter-by-quarter path matches the Shapley endpoints to one decimal. That holds for the public and private totals (6.2 and 6.9 both ways) but not for the holder groups.
- **Severity:** minor
- **Evidence:** In `results.json` `sensitivity.chained_quarterly_shapley`: Fannie and Freddie 1.38 against 1.25, federal student loans 1.61 against 1.70.
- **Proposed resolution:** Say that only the totals match.
- **Status:** open

### R-20261113-45 · skeptic · doc-4af129f3.md
- **Objection:** The range "between 56.2% and 56.2%" has the wrong lower end. The lower end nets all issued CRT, and that figure is 55.2%. The line as written contradicts doc-4af129f3.md:20 (55.2%) and doc-4af129f3.md:11 (a 56.0% net figure "inside the bounds" cannot sit inside 56.2–56.2).
- **Severity:** blocker
- **Evidence:** doc-4af129f3.md:44. `research/a2_net_exposure/results.json` has `public_share_net_lower_pct_last: 55.236` and `public_share_net_freddie_crt_pct_last: 56.189`. Register rows `a2_public_share_net_lower_2025q4` (55.2%) and `a2_share_net_freddie_crt_2025` (56.2%) agree. `diff` against the committed `research/a2_net_exposure/README.md`:44 shows the committed text says "between 55.2% and 56.2%".
- **Proposed resolution:** Restore "between 55.2% and 56.2%", matching results.json and the committed README.
- **Status:** open

### R-20261113-46 · skeptic · doc-4af129f3.md
- **Objection:** "The bound bears the losses on in every year 2013–2025" does not parse. It also treats a bound on holdings net of CRT as something that bears losses, which mixes up holding risk with bearing losses. The committed README says "The bound holds in every year". The intended claim is that net ≤ gross and the lower bound stays positive every year.
- **Severity:** major
- **Evidence:** doc-4af129f3.md:23; `diff` against `research/a2_net_exposure/README.md`:23. The two `checks` entries in results.json (`net_le_gross_all_years`, `net_lower_positive_all_years`) are true.
- **Proposed resolution:** Restore "The bound holds in every year 2013–2025".
- **Status:** open

### R-20261113-47 · skeptic · doc-cc89f643.md
- **Objection:** doc-cc89f643.md:3 and :5 say "The numbers are checked and registered". Every `a1_*` row in the register is `UNVERIFIED`; only 36.1/49.2/13.1 (C4/C5) are PASS. That presents unverified numbers as checked.
- **Severity:** major
- **Evidence:** I filtered claims/register.csv for rows citing the README. 23 `a1_*` rows have `validation=UNVERIFIED`.
- **Proposed resolution:** Say "registered; the decomposition figures are not yet independently validated", or add validation checks.
- **Status:** open

### R-20261113-48 · skeptic · doc-cc89f643.md
- **Objection:** At :23, about 30% of the "$1.71T / 5.7 pp" private-label figure is the FAS 166/167 move in 2010Q1. "Part of that" gives no size. Of the 5.7 pp, 2.0 pp is consumer-credit ABS, not mortgage private-label securities. At :49, "these reclassifications cancel" holds only for the private total, not for the group split in :23. "Bank line falls" describes the contribution; bank holdings actually rose $321B.
- **Severity:** major
- **Evidence:** I recomputed with the decompose.py functions. In 2010Q1, consumer-credit ABS issuers moved −$513.5B, banks' consumer credit +$320.9B and finance companies +$121.1B. At 0.00331 pp per $B, that is about 1.7 pp. decomposition.csv shows consumer-credit ABS −606.3 for 2.01 pp.
- **Proposed resolution:** Quantify the reclassification in the :23 sentence, or report only the private total. Fix the wording at :49.
- **Status:** open

### R-20261113-49 · skeptic · doc-cc89f643.md
- **Objection:** At :48, "Most FFEL loans ... carried a federal guarantee" should say essentially all; they were federally reinsured. The caveat is applied only to the public side. The private side's 6.9 pp also includes guaranteed FFEL leaving private lines, so "private retreat" overstates the shift in risk too.
- **Severity:** major
- **Evidence:** In 2010Q1, $121B of ABS moved to finance companies. That is likely student-loan trusts, but I have not confirmed it. decomposition.csv: nonprofit student loans −$15.5B. Register row a1_student_change_usd, notes column.
- **Proposed resolution:** Extend the limit to both sides and drop "most". Estimate FFEL in private lines (A2).
- **Status:** open

### R-20261113-50 · skeptic · doc-cc89f643.md
- **Objection:** At :11, "matches ... to one decimal" holds only for the side totals. The group figures differ. At :29, the 2.3 pp peak from the chained path sits next to 1.2 pp from the endpoint table; the path ends at 1.4 pp.
- **Severity:** minor
- **Evidence:** In results.json, chained against endpoint: GSEs 1.38 vs 1.25; student loans 1.61 vs 1.70.
- **Proposed resolution:** Scope the :11 claim to the side totals. At :29, say the path ends at 1.4 pp.
- **Status:** open

### R-20261113-51 · skeptic · doc-cc89f643.md
- **Objection:** The "6.1 pp" at :53 has no register location there. It shares its display text with a1_ginnie_own_pp, so the claim check could credit it to the wrong row.
- **Severity:** minor
- **Evidence:** Register row gfc_counterfactual_pp lists only analysis/findings.md:12.
- **Proposed resolution:** Add README:53 to gfc_counterfactual_pp.
- **Status:** open

### R-20261113-52 · skeptic · doc-cc89f643.md
- **Objection:** The "Revisions" bullet at :55 still does not say that the split by holder was checked against the previous vintage only at bucket level. This was raised as R-20261104-12, which is still open.
- **Severity:** minor
- **Evidence:** claims/review-log.md, entry R-20261104-12.
- **Proposed resolution:** Add that sentence to the bullet.
- **Status:** open

Files:
- /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2r/doc-cc89f643/doc-cc89f643.md
- /home/user/household-debt-risk/research/a1_gfc_decomposition/results.json
- /home/user/household-debt-risk/research/a1_gfc_decomposition/decomposition.csv
- /home/user/household-debt-risk/claims/register.csv
