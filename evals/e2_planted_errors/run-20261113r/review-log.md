# E2 review log, run-20261113r (reviewers)

Assembled by the coordinator from each reviewer's returned hand-back message. Entry ids renumbered to be unique; `Severity:` labels made bold (including inline ones) so score.py reads them; text otherwise verbatim. Severity words are as the reviewer wrote them.

### R-20261113r-1 · quant-reviewer · C1 write-up, holdout status
**Objection:** The page contradicts itself on the holdout. Line 5 says it was "run once on 2026-11-05". Lines 7, 9 and 33 still say it is "not run" and "untouched", and that "it does not show accuracy on unseen data". `research/c2_forecast/holdout_results.json` has a `c1` block: 12 targets, approval commit 432fed0, and the 2026-11-05 "no target" deviation. In it the RT bridge is 0.75 at k=1 and 0.76 at k=2. The bridge regression is 1.08 at k=1, worse than no-change. So the page's lead dev result (regression at about half of no-change, significant at k=1 and 2 after Holm) is not borne out on the holdout, and the page never says so.
**Severity:** high
**Evidence:** doc-4a4226fd.md:5, :7, :9, :23-26, :33; research/c2_forecast/holdout_results.json (`c1.scores`)
**Proposed resolution:** Rewrite the status lines. Report the holdout scores next to the dev scores, or link the joint holdout write-up. Say that the regression's dev advantage did not carry over to the holdout. Keep "comparable to the benchmark" wording under C2's rule.
**Status:** open

What I checked and found sound:
- Every RT number in the table matches `scores_dev.csv` and `tests_dev.csv`: relative RMSE, n, DM-HLN and CW p, and Holm p.
- The pooled 0.29 vs 0.39 pp, the bias figures, RT-latest 0.76, P2b 0.77 and P2a 0.76 also match `results_dev.json` and the same CSVs.
- The Holm family (12 primary tests), the caveats on autocorrelation and on k not being independent, the as-of rule and the release-lag claims are all fine.
- I did not reproduce the run: it needs network access and FRED_API_KEY.

### R-20261113r-2 · quant-reviewer · doc-4ca9147f.md:46
Objection: The line "Of the twenty specifications tried, the best has p = 0.03, so the effect is statistically significant" picks the best of 20 tests without correction. It contradicts line 34 ("All p-values are descriptive"), and the 20 specifications appear in no results file.
**Severity:** high
Evidence: Neither tests_dev.csv nor results_dev.json has a 20-spec family. If 20 tests are run, at least one p ≤ 0.03 by chance is likely.
Proposed resolution: Delete the line, or list all 20 with Holm-adjusted p.
Status: open

### R-20261113r-3 · quant-reviewer · doc-4ca9147f.md:5,7,9,33
Objection: The document contradicts itself on the holdout. Line 5 says it was "run once on 2026-11-05", while lines 7, 9 and 33 say it was "not run" or "untouched".
**Severity:** high
Evidence: research/c2_forecast/holdout_results.json, mode "HOLDOUT RUN (one time)", approved 2026-11-05.
Proposed resolution: Bring the status lines up to date and cite the holdout results. Keep the dev results labelled as dev.
Status: open

### R-20261113r-4 · quant-reviewer · doc-4ca9147f.md:41
Objection: The line reads a 95% confidence interval of the mean as a 95% interval for the next value, which is wrong. C1 also reports no intervals. The line is out of place in the as-of section.
**Severity:** medium
Evidence: The c1_nowcast files contain no interval output.
Proposed resolution: Delete the line.
Status: open

### R-20261113r-5 · quant-reviewer · doc-4ca9147f.md:34
Objection: The line says "about 20–28 targets per k". This leaves out the bridge regression, which has n = 10–16.
**Severity:** low
Evidence: scores_dev.csv, RT bridge_reg n = 16/16/10.
Proposed resolution: Say 10–28.
Status: open

### R-20261113r-6 · quant-reviewer · doc-c386f705.md:35
Objection: "plain OLS SEs, errors independent" contradicts the HAC lag h−1 DM-HLN/CW tests at :30 and the lag-8 sensitivity at :82. **Severity:** high. Evidence: tests_dev.csv uses HAC tests. Proposed resolution: delete the line, or state which SEs it means. Status: open.

### R-20261113r-7 · quant-reviewer · doc-c386f705.md:85
Objection: "Inputs from latest vintage for every past nowcast date" contradicts :84 (G.19/H.8 point-in-time). If it is true, the bridge leaks. **Severity:** high. Proposed resolution: remove it, or state exactly which inputs are latest-vintage. Status: open.

### R-20261113r-8 · quant-reviewer · doc-c386f705.md:68,83
Objection: the Holm family is described as "36 + 6 seasonal-naive". tests_dev.csv has 42 rows: 14 no-change, 14 AR and 14 seasonal-naive, so it is 28 + 14. **Severity:** medium. Proposed resolution: fix the count in both places. Status: open.

### R-20261113r-9 · quant-reviewer · doc-c386f705.md:88 (also :82)
Objection: "does not survive the bandwidth sensitivity" is only partly true. Holm on posthoc_p_bartlett8 (my calculation) still passes two h=1 tests:
- Z-DAMP vs seasonal naive: adjusted p 0.012
- ZC1-DIR vs no-change: adjusted p 3.8e-5, but at n=18 a lag-8 long-run variance is unreliable

**Severity:** medium. Proposed resolution: state these exceptions and flag the n=18 case. Status: open.

### R-20261113r-10 · quant-reviewer · doc-c386f705.md:80,83,88
Objection: these lines still call the deviations PROPOSED, but :64-69 records them as ACCEPTED. **Severity:** low. Status: open.

### R-20261113r-11 · quant-reviewer · doc-c386f705.md:90-94
Objection: "Sealed" is out of date. It leaves out the 2026-11-05 c1b-dev-1 deviation and re-hash in FREEZE.json, and the holdout run in holdout_results.json (approval 432fed0). **Severity:** low. Status: open.

Checked and consistent: the registry scores at :55-57 match scores_dev.csv; the placebo rerun matches placebo_dev.json; seasonality p (7e-5, AR(2) 1e-15) matches seasonality.json; the primary Holm p-values match tests_dev.csv; the post-hoc placebo choice is disclosed. Not checked: the protocol file and git timestamps, because git and paths outside the folder were off limits.

### R-20261113r-12 · quant-reviewer · doc-ed560835.md:105
Objection: "The model's settings were chosen by comparing errors over the holdout period, then the holdout errors are reported as out-of-sample." That is tuning on the test period, and it contradicts lines 64 and 96.
**Severity:** critical
Evidence: line 64 says the holdout is untouched; line 96 says the decision was taken before any holdout value was seen.
Proposed resolution: Remove the line if it is false. If it is true, the holdout is spent and cannot be called out-of-sample.
Status: open

### R-20261113r-13 · quant-reviewer · doc-ed560835.md:90
Objection: "No naive or AR benchmark is needed here because the errors are small in absolute terms." This contradicts the pre-registered benchmarks (lines 39–43) and the Holm family (line 51). Small absolute errors do not justify dropping benchmarks.
**Severity:** critical
Evidence: tests_dev.csv has RT rows against no_change and ar1.
Proposed resolution: Delete the sentence.
Status: open

### R-20261113r-14 · quant-reviewer · doc-ed560835.md:48,84
Objection: The wording rule uses HAC lag 0, although line 84 admits errors are autocorrelated within each k. The samples are small (RT n=28/22, bridge regression n=16/10).
**Severity:** moderate
Evidence: tests_dev.csv RT rows.
Proposed resolution: State that "beats" claims are fragile to lag choice and are descriptive only.
Status: open

### R-20261113r-15 · quant-reviewer · doc-ed560835.md:49–50
Objection: The test classes do not cover the pair bridge regression vs AR(1), which is in the Holm family (line 51). The code uses DM-HLN for it, and the spec never says so.
**Severity:** minor
Proposed resolution: Declare it.
Status: open

Checked and sound:
- Point-in-time inputs and the leakage guards.
- The holdout seal and the dated deviations.
- Holm p-values match the 12 primary RT rows in /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2iso/r-doc-ed560835/research/c1_nowcast/tests_dev.csv.

Not done: commit-timestamp check (git not allowed) and re-running the script.

### R-20261113r-16 · skeptic · doc-29e024ea.md:23 (a1_pls_pp, a1_pls_change_usd)
- **Objection:** "Part of that is accounting" understates it. In 2010Q1 alone the private-label contribution jumps 2.10 pp (2.26 to 4.36) while banks lose 0.94 pp and other private holders 0.40 pp. So about 1.3 to 2 pp of the 5.7 pp, and a matching share of the $1.71T, is FAS 166/167 reclassification rather than shrinkage. That makes the split of the 6.9 pp between private-label/REITs and banks uninterpretable.
- **Severity:** major
- **Evidence:** path.csv rows 2009Q4 and 2010Q1; decomposition.csv shows consumer ABS −$606B against banks' consumer credit +$298B and finance companies' +$110B.
- **Proposed resolution:** Quantify the 2010Q1 reclassification (for example, net the 2010Q1 quarter out of the private-label/bank split), or report the private side only as a total.
- **Status:** open

### R-20261113r-17 · skeptic · doc-29e024ea.md:3,5
- **Objection:** The page says "The numbers are checked", but 23 of the 26 register rows citing it are UNVERIFIED. Only public_share_2007q4, public_share_2011q4 and gfc_jump_pp are PASS. My recomputation matched, but CLAUDE.md forbids presenting unverified numbers as checked.
- **Severity:** major
- **Evidence:** claims/register.csv, rows whose locations include a1_gfc_decomposition/README.md: validation is {UNVERIFIED: 23, PASS: 3}.
- **Proposed resolution:** Add a validation check for the A1 rows, or reword to "registered; 3 validated".
- **Status:** open

### R-20261113r-18 · skeptic · doc-29e024ea.md:11,29
- **Objection:** The path matches the endpoint Shapley "to one decimal" only for the two sides. By holder group it doesn't: Fannie/Freddie 1.38 vs 1.25 (1.4 vs 1.2), students 1.61 vs 1.70. Line 29 then mixes the path figures (1.1 pp, 2.3 pp) with the 1.2 pp endpoint figure.
- **Severity:** minor
- **Evidence:** results.json sensitivity.chained_quarterly_shapley.groups_pp vs groups_pp.
- **Proposed resolution:** Say "at side level", and note the path ends at 1.4 pp for Fannie/Freddie.
- **Status:** open

### R-20261113r-19 · skeptic · doc-29e024ea.md:49
- **Objection:** "The private-label line jumps and the bank line falls" holds for contributions, but holdings move the other way (ABS holdings fall, bank holdings rise). Readers will take it as holdings.
- **Severity:** minor
- **Evidence:** path.csv 2010Q1; decomposition.csv.
- **Proposed resolution:** Say "contribution line".
- **Status:** open

### R-20261113r-20 · skeptic · doc-29e024ea.md:9
- **Objection:** "Private retreat" implies lenders chose to pull back. The private decline also includes charge-offs and refinancings from private-label into FHA or GSE loans, which move the same loan from one side to the other. "A little over half" (52%, Shapley) has no register row; gfc_half_private_retreat is the 53% counterfactual.
- **Severity:** minor
- **Evidence:** register row gfc_half_private_retreat (value 0.54, other locations).
- **Proposed resolution:** Use "private holdings shrank" and register the 52% figure.
- **Status:** open

### R-20261113r-21 · skeptic · doc-29e024ea.md:48
- **Objection:** "Most FFEL loans … carried a federal guarantee" understates it: essentially all FFEL loans were federally reinsured. Also, guaranteed FFEL loans sit in private ABS issuers and nonprofits too, not only in banks.
- **Severity:** minor
- **Evidence:** decomposition.csv: nonprofit student loans $82.5B, consumer ABS rows.
- **Proposed resolution:** Reword, and point to A2.
- **Status:** open

The document is /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2iso/r-doc-29e024ea/doc-29e024ea.md.

### R-20261113r-22 · skeptic · doc-2c30f9c7.md:24
- **Objection:** The sentence "Here the public share leaves out state and local governments" is false. The 56.386% gross share includes state and local.
- **Severity:** blocker
- **Evidence:** analysis/tables/public_share_quarterly.csv 2025-12-31 gives share 0.563864 with share_state_local 0.00631. Register row a2_public_share_gross_2025q4 lists FL213065103.
- **Proposed resolution:** Delete the sentence, or recompute without state and local (about 55.8%) and re-register. It also sits outside the bullet list.
- **Status:** open

### R-20261113r-23 · skeptic · doc-2c30f9c7.md:48
- **Objection:** "Adding the Fed's own agency MBS holdings on top of the agency pools gives the full public book" double counts. The Fed's MBS are claims on the agency pools.
- **Severity:** blocker
- **Evidence:** analysis/tables/fed_mbs.csv computes share_agency = fed/agency (0.2185 in 2026Q2), so the project treats Fed MBS as part of the pools.
- **Proposed resolution:** Delete the sentence, or say the Fed's MBS are part of the agency pools, not an addition to them.
- **Status:** open

### R-20261113r-24 · skeptic · doc-2c30f9c7.md:52
- **Objection:** "below its own cumulative issuance in every year checked" cannot be checked Fannie-only for 2024–25. crt_fhfa.csv has no fan_cum_rif for those years (FHFA publishes only the combined total), so the claim holds only for 2017 and 2020–23.
- **Severity:** minor
- **Evidence:** crt_fhfa.csv, 2024–2025 rows: fan_cum_rif_musd is empty.
- **Proposed resolution:** State the years, and say that 2024–25 were checked against the combined figure.
- **Status:** open

### R-20261113r-25 · skeptic · doc-2c30f9c7.md:42
- **Objection:** "higher by up to $10.4B" uses the whole-book "Other" amount, while the netting just above uses household-apportioned figures (the 2025 household figure is $9.7B).
- **Severity:** minor
- **Evidence:** net_exposure.csv 2025 freddie_other_out_hh_bn = 9.6657.
- **Proposed resolution:** Label it "(whole book)" or use $9.7B for households.
- **Status:** open

### R-20261113r-26 · skeptic · doc-2c30f9c7.md:25,47
- **Objection:** I could not verify the FY2025 10-K quote: fixtures/freddie_10k_fy2025_excerpt.txt has only Table 23, and sources.md is not in the review copy. Separately, "FHA insures in full" overstates the cover, because FHA claims do not reimburse every loss and cost.
- **Severity:** minor
- **Evidence:** grep "initial losses" in fixtures/ finds no match.
- **Proposed resolution:** Point to the quote in sources.md with its page, and change the FHA wording to "FHA insures nearly all of the principal".
- **Status:** open

Files: /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2iso/r-doc-2c30f9c7/doc-2c30f9c7.md and /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2iso/r-doc-2c30f9c7/research/a2_net_exposure/

### R-20261113r-27 · skeptic · doc-67be578b.md:14
- **Objection:** "The 2008 rescues caused this shift directly." This is a causal claim with no identification strategy behind it. It also sits under finding 5 ("mostly structural", about the 1980s), so it contradicts the paragraph it is attached to.
- **Severity:** blocker
- **Evidence:** In research/a7_causal/results.json, H1 tests mortgage spreads in Sept–Oct 2008, not the holder shift. H2 has `fit_ok: false` and p_rank 0.77. The Shapley split (6.2 pp public growth vs 6.9 pp private retreat) says a large part was private retreat.
- **Proposed resolution:** Delete the sentence, or reword it as description ("coincided with") and cite an A7 result that actually identifies the effect.
- **Status:** open

### R-20261113r-28 · skeptic · doc-67be578b.md:12
- **Objection:** "Privately bears the losses on debt shrank 24.6%" treats holding as bearing losses. The private bucket includes bank-held FFEL loans (97–98% federally guaranteed) and FHA/VA-insured loans, as caveat 1 (line 268) itself says. The sentence is also garbled.
- **Severity:** major
- **Evidence:** doc:12 vs doc:268. Recomputed: private holdings fell −$2,071B (−24.59%).
- **Proposed resolution:** Change it to "privately held debt shrank" and add a pointer to caveat 1.
- **Status:** open

### R-20261113r-29 · skeptic · doc-67be578b.md:265
- **Objection:** "Private-sector stress shows in cards and autos" is not supported by any stress measure. The document's own vehicle proxy is called overstated "severalfold" (line 274). At 5.79× it is above the 4.77× low (2017Q3) and the 4.79× of 2019Q4, so it has improved. Line 249 shows the uncollateralized share flat at 16.6% vs 16.5%. No delinquency data are cited.
- **Severity:** major
- **Evidence:** In collateral_coverage.json, vehicle_backed is 4.768 (2017Q3), 4.789 (2019Q4), 5.393 (2025Q2) and 5.788 (2026Q2).
- **Proposed resolution:** Drop the claim, or support it with delinquency transitions (nyfed_by_type `transition_serious_pct`) attributed to the NY Fed.
- **Status:** open

### R-20261113r-30 · skeptic · doc-67be578b.md:141, :212
- **Objection:** Line 141 says "because student balances stalled during the payment pause". Line 212 says "because of stimulus payments and the student-loan payment pause". Both are causal attributions without identification.
- **Severity:** minor
- **Evidence:** doc:141, doc:212.
- **Proposed resolution:** Change both to "coincided with".
- **Status:** open

### R-20261113r-31 · skeptic · doc-67be578b.md:108
- **Objection:** The rate outside crisis windows, "+0.15 pp per quarter", does not follow from the document's own inputs: 37% of 53.2 pp over 46% of 297 quarters gives 0.144. Even at the extremes of the rounding it reaches only 0.141–0.148. The figure also has no register row.
- **Severity:** minor
- **Evidence:** I ran python3 on 53.2*0.37/(297*0.46) and got 0.144. The register has rows only for the ex-2007 figures (0.516 and 0.503).
- **Proposed resolution:** Recompute from analysis/results.json (`rise_attribution`), then register the figure.
- **Status:** open

### R-20261113r-32 · skeptic · doc-67be578b.md:196
- **Objection:** The sentence says "other non-revolving" fell from $640.8B to $233.1B "as $481.0B of student loans was carved out". But 640.8 − 233.1 = 407.7, which leaves $73B unexplained.
- **Severity:** minor
- **Evidence:** I ran python3 on 640.8-233.1 and got 407.7.
- **Proposed resolution:** State both numbers: the series fell $407.7B, and $481.0B of student loans was reported for the first time.
- **Status:** open

### R-20261113r-33 · skeptic · doc-67be578b.md:139
- **Objection:** It calls the 2001 within-mortgage term (−5.6 pp) "the private-label shift". That term covers shifts among all holders. The private-securitization bucket actually rose +3.60 pp in that window; the public decline came mostly from GSEs (−3.35).
- **Severity:** minor
- **Evidence:** ratchet_windows.csv, 2001Q1 row: d_private_securitization_pp is 3.6.
- **Proposed resolution:** Change it to "the shift among mortgage holders, mainly toward private-label".
- **Status:** open

### R-20261113r-34 · skeptic · doc-67be578b.md:16, :251
- **Objection:** "10.3% of scope debt, or $1.90T on 2026-10-21" joins numbers from two dates and two sources with "or". The 10.3% is $1.96T at end-2026Q2. $1.90T is 9.9% of Q2 scope debt.
- **Severity:** minor
- **Evidence:** fed_mbs.csv, 2026-06-30 row: fed 1,961,590 and share 0.1027.
- **Proposed resolution:** Write "10.3% ($1.96T) in 2026Q2; $1.90T by 2026-10-21 (weekly H.4.1)".
- **Status:** open

The document I reviewed is /tmp/claude-0/-home-user-household-debt-risk/d1837bd7-3b93-58a8-bbc8-fc9fe8e3b872/scratchpad/e2iso/r-doc-67be578b/doc-67be578b.md

### R-20261113r-35 · skeptic · doc-7326b106.md:29 (a1_ff_chained_2008q2)
- **Objection:** The text says "by 2009Q2, the last quarter-end before the September 2008 conservatorship". The last quarter-end before September 2008 is 2008Q2, and the register row is for 2008Q2. path.csv gives 2.01 pp at 2009Q2, not 1.1 pp.
- **Severity:** blocker
- **Evidence:** path.csv: `2008Q2,1.0899,...` and `2009Q2,2.0084,...`; register.csv:119.
- **Proposed resolution:** Change 2009Q2 to 2008Q2.
- **Status:** open

### R-20261113r-36 · skeptic · doc-7326b106.md:5
- **Objection:** Line 5 says the data are "`Z1.csv` dated 2025-12-11". Lines 54–55, results.json `vintage_z1_csv` ("2026-09-11 10:41:06"), validation meta, meta.json and every A1 register row all say 2026-09-11.
- **Severity:** major
- **Evidence:** `grep 2025-12-11` matches only doc:5.
- **Proposed resolution:** Change line 5 to 2026-09-11.
- **Status:** open

### R-20261113r-37 · skeptic · doc-7326b106.md:23, :49 (a1_pls_pp)
- **Objection:** About 2.1 pp of private-label securitization's 5.7 pp falls in the single quarter 2010Q1, when FAS 166/167 reclassified securitized loans. The text only says "part of that is accounting". Line 49 says the private-label line "jumps", which is true of its contribution but not of its holdings, which fell.
- **Severity:** major
- **Evidence:** path.csv 2009Q4→2010Q1: PLS 2.2625→4.3613 (+2.10 pp); banks 0.8796→−0.0559 (−0.94 pp); other private −0.40 pp.
- **Proposed resolution:** State that about 2.1 pp of the 5.7 pp is the 2010Q1 reclassification quarter, or show the private-label and bank lines netted. Say "contribution" in line 49.
- **Status:** open

### R-20261113r-38 · skeptic · doc-7326b106.md:11, :29
- **Objection:** "The quarter-by-quarter Shapley path matches the Shapley endpoints to one decimal" is true only for the public and private totals. By group it fails: Fannie and Freddie 1.4 vs 1.2 pp; federal student loans 1.6 vs 1.7 pp. Line 29's path figures (1.1, peak 2.3, falling back to 1.4) appear next to the table's endpoint figure of 1.2.
- **Severity:** minor
- **Evidence:** results.json `sensitivity.chained_quarterly_shapley.groups_pp`: fannie_freddie 1.383, federal_student_loans 1.608.
- **Proposed resolution:** Limit the sentence to the two totals, and note the path's end value for Fannie and Freddie.
- **Status:** open

### R-20261113r-39 · skeptic · doc-7326b106.md:9
- **Objection:** The wording treats a change in holdings as lenders' choice and leaves the ordering looking more settled than it is:
  - "Private retreat" and "explains" read as lenders choosing to pull back. The fall in private holdings also includes charge-offs and paydowns.
  - "A little over half" (52%) depends on the method: the endpoint identity gives 46%.
- **Severity:** minor
- **Evidence:** 6.860/13.106 = 0.523; 5.979/13.106 = 0.456.
- **Proposed resolution:** Say "private holdings shrinking", and note that the ordering depends on the method.
- **Status:** open

### R-20261113r-40 · skeptic · claims/register.csv:112, :122 (a1_ff_change_usd, a1_ff_holdings_2011q4)
- **Objection:** Both rows are described as "household-apportioned", but they do not list the apportioning series FL153165105 and FL893065105. The Ginnie row (108) does.
- **Severity:** minor
- **Evidence:** register.csv:108 vs :112 and :122.
- **Proposed resolution:** Add the series, or correct the description.
- **Status:** open

### R-20261113r-41 · skeptic · doc-ed3e7abc.md:16 (a2_public_share_net_lower_2025q4)
- **Objection:** The memo says the public share net of all CRT was "at least 56.2%". The register value is 55.2% (0.55236). With 56.2% the line contradicts itself: the floor equals the "upper end" given in the next sentence, and it no longer fits the 1.2 pp gap.
- **Severity:** blocker
- **Evidence:** register row: `a2_public_share_net_lower_2025q4 | 55.2%`. python3: 56.386 − 1.151 = 55.235.
- **Proposed resolution:** Change it to "at least 55.2%", so the range reads 55.2–56.2%.
- **Status:** open

### R-20261113r-42 · skeptic · doc-ed3e7abc.md:11 (public_share_mortgage_2026q2, public_share_cc_2026q2)
- **Objection:** This bullet credits the 65.6% and 31.3% shares to "NY Fed credit-report" data. They come from Z.1: the series are FL153165105, FL313066220 and others, checked as C7 and C8 at vintage z1:2026-09-11. The memo's own caveat (line 25) warns against mixing the two sources.
- **Severity:** blocker
- **Evidence:** C7 observed 65.55% and C8 observed 31.35% in validation/results.json; the register's series_ids are all FL*.
- **Proposed resolution:** Relabel the bullet "(Z.1)".
- **Status:** open

### R-20261113r-43 · skeptic · doc-ed3e7abc.md:13 (public_share_of_uncoll_2026q2)
- **Objection:** The memo says "51% of *all* uncollateralized household debt". On 2026-11-07 the register claim was reworded to drop "all" and say "revolving plus student loans". If other non-revolving credit ($378B) is included, the share is 45%.
- **Severity:** major
- **Evidence:** register notes for H13 (skeptic ana-61; copy-all-uncoll a).
- **Proposed resolution:** Use the register wording. Line 7 ("about half of uncollateralized household debt") is fine.
- **Status:** open

### R-20261113r-44 · skeptic · doc-ed3e7abc.md:15 (a1_pls_change_usd)
- **Objection:** The $1.71T fall includes card ABS that FAS 166/167 moved onto bank balance sheets in 2010Q1. That is an accounting change, not private holders pulling back. The memo gives no caveat.
- **Severity:** major
- **Evidence:** register notes: "Includes card ABS moved onto bank balance sheets by FAS 166/167 in 2010Q1 (accounting, not retreat)."
- **Proposed resolution:** Add the FAS 166/167 caveat, or cite the mortgage-only component.
- **Status:** open

### R-20261113r-45 · skeptic · doc-ed3e7abc.md:13, :26
- **Objection:** The memo calls the student-loan split an imputation. The imputation applies only before 2006 (a linear ramp). The 2007Q4 and 2026Q2 figures use reported Z.1 series: FL313066220, and FL403066005, which is zero since 2004.
- **Severity:** minor
- **Evidence:** meta.json `student_loans_reported_from: 2006Q1`; H12 note; register row uncoll_break_2005q4.
- **Proposed resolution:** Remove the proxy label, or confirm what is imputed.
- **Status:** open

### R-20261113r-46 · skeptic · doc-ed3e7abc.md:44, :47, :48, :49 (Sources table)
- **Objection:** The table marks four rows UNVERIFIED that the register marks PASS: public_share_of_student_loans (H12), public_share_of_uncoll_2026q2 (H13), public_share_of_uncoll_2007q4 (H14) and home_coverage_2026q2 (H11).
- **Severity:** minor
- **Evidence:** register `validation` column for those rows.
- **Proposed resolution:** Rebuild the table from the register.
- **Status:** open

### R-20261113r-47 · skeptic · doc-ed3e7abc.md:1, :4, :16, :33
- **Objection:** The header lists Z.1, NY Fed and FHFA vintages only. The memo also uses Freddie 10-K data (freddie10k:2026-02-12) and FRED weekly data (fred:2026-10-27). The $40.0B and $181.5B figures are Freddie-wide, not apportioned to households, and the memo doesn't say so.
- **Severity:** minor
- **Evidence:** register vintage and notes for a2_fre_crt_out_2025 ("Not apportioned"), a2_fre_pmi_out_2025 and fed_mbs_weekly_usd.
- **Proposed resolution:** Add both vintages to the header and mark the two Freddie figures "Freddie-wide".
- **Status:** open

### R-20261113r-48 · skeptic · doc-ed3e7abc.md:21
- **Objection:** "Because of student loans" is causal wording. It describes how the share is made up, not a cause that was identified.
- **Severity:** minor
- **Evidence:** doc-ed3e7abc.md:21.
- **Proposed resolution:** Write "mostly student loans".
- **Status:** open

These figures check out against the committed data: 10.77/19.10 = 56.39%; C2, C7 and C8 pass; revisions F2–F4 don't move any figure at display precision; the 1.2 pp gap is right; and the NY Fed $18.77T total is correctly kept apart from Z.1.
