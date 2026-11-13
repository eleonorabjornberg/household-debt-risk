# E2 rescore pack (run-20261113r)

You are the second rater. Judge each item on its own. Do not look for anyone else's scoring.

## Part A: planted errors (3, drawn with random.Random(20261104))

Catch rule (prereg): an error is caught if an objection (i) points to its document and to a line within ±2 lines, or quotes its text, and (ii) names a problem of the same category or one that would lead to the same fix. For each error answer located (yes/no, condition i) and same_fix (yes/no, condition ii, for the best matching objection), with one sentence of reason.

### doc-ed3e7abc.md#1
- document: docs/doc-ed3e7abc.md
- category: source_swap
- planted at line 11: - **Mortgages versus consumer credit (NY Fed credit-report).** The public share of household mortgages alone was 65.6% in 2026Q2. The public share of consumer c
- the error and its fix: the figure is Z.1, not NY Fed CCP; sources must not be mixed or mislabelled
- objections on this document near that line:

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

### R-20261113r-45 · skeptic · doc-ed3e7abc.md:13, :26
- **Objection:** The memo calls the student-loan split an imputation. The imputation applies only before 2006 (a linear ramp). The 2007Q4 and 2026Q2 figures use reported Z.1 series: FL313066220, and FL403066005, which is zero since 2004.
- **Severity:** minor
- **Evidence:** meta.json `student_loans_reported_from: 2006Q1`; H12 note; register row uncoll_break_2005q4.
- **Proposed resolution:** Remove the proxy label, or confirm what is imputed.
- **Status:** open

### doc-ed3e7abc.md#0
- document: docs/doc-ed3e7abc.md
- category: number_change
- planted at line 16: - **Credit risk transfer.** Net of all issued CRT only (mortgage insurance not netted), the public share was at least 56.2% at end 2025. Credit risk transfer al
- the error and its fix: the number does not match the register / recompute
- objections on this document near that line:

### R-20261113r-41 · skeptic · doc-ed3e7abc.md:16 (a2_public_share_net_lower_2025q4)
- **Objection:** The memo says the public share net of all CRT was "at least 56.2%". The register value is 55.2% (0.55236). With 56.2% the line contradicts itself: the floor equals the "upper end" given in the next sentence, and it no longer fits the 1.2 pp gap.
- **Severity:** blocker
- **Evidence:** register row: `a2_public_share_net_lower_2025q4 | 55.2%`. python3: 56.386 − 1.151 = 55.235.
- **Proposed resolution:** Change it to "at least 55.2%", so the range reads 55.2–56.2%.
- **Status:** open

### R-20261113r-44 · skeptic · doc-ed3e7abc.md:15 (a1_pls_change_usd)
- **Objection:** The $1.71T fall includes card ABS that FAS 166/167 moved onto bank balance sheets in 2010Q1. That is an accounting change, not private holders pulling back. The memo gives no caveat.
- **Severity:** major
- **Evidence:** register notes: "Includes card ABS moved onto bank balance sheets by FAS 166/167 in 2010Q1 (accounting, not retreat)."
- **Proposed resolution:** Add the FAS 166/167 caveat, or cite the mortgage-only component.
- **Status:** open

### doc-7326b106.md#1
- document: docs/doc-7326b106.md
- category: vintage_label
- planted at line 5: **PLAN task A1. Status: analysis done; method decided by Eleonora (Shapley, 2026-11-04); the write-up is a Claude draft for her to replace.** The skeptic and qu
- the error and its fix: the vintage cited does not match the data used (meta.json / register vintage)
- objections on this document near that line:

### R-20261113r-36 · skeptic · doc-7326b106.md:5
- **Objection:** Line 5 says the data are "`Z1.csv` dated 2025-12-11". Lines 54–55, results.json `vintage_z1_csv` ("2026-09-11 10:41:06"), validation meta, meta.json and every A1 register row all say 2026-09-11.
- **Severity:** major
- **Evidence:** `grep 2025-12-11` matches only doc:5.
- **Proposed resolution:** Change line 5 to 2026-09-11.
- **Status:** open

## Part B: objections on control documents (no planted error)
For each, answer real_problem (yes/no): does the objection point to a real problem in the document as written? One sentence of reason. Check the document.

### R-20261113r-1 · quant-reviewer · doc-4a4226fd.md (C1 write-up, holdout status)
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

### R-20261113r-B1 · baseline · doc-29e024ea.md
**Location:** doc-29e024ea.md:3 (repeated in spirit at :5)
Problem: The banner says "The numbers are checked and registered." Every a1_* row in claims/register.csv has validation status UNVERIFIED or blank. Only the headline jump has a passing check (gfc_jump_pp, C5 PASS). Calling them "checked" presents unverified numbers as verified, which CLAUDE.md forbids.
Fix: "The numbers are registered (claims/register.csv); apart from the headline jump (check C5), they are not yet validated."

### R-20261113r-B2 · baseline · doc-29e024ea.md
**Location:** doc-29e024ea.md:54
Problem: "A1 should stay inside 1987 onwards with these cells until the gap is explained" does not make sense. A1's window (2007Q4–2011Q4) is already far outside the gap; the register note says "Outside A1's window". The warning belongs to any other work that uses the pool sub-series before 1987. The sentence also leaves out that the coordinator confirmed the finding (register: "found by the markets track 2026-11-04 and confirmed by the coordinator").
Fix: "A1 is unaffected. Any work that uses these pool sub-series before 1987 should wait until the gap is explained. The markets track found the gap on 2026-11-04 and the coordinator confirmed it."

### R-20261113r-B3 · baseline · doc-29e024ea.md
**Location:** doc-29e024ea.md:11
Problem: "All three are in `results.json` (`sensitivity`)" is wrong. Only the endpoint identity and the chained quarterly Shapley are under `sensitivity`. The headline Shapley split is at the top level (`from_public_growth_pp`, `from_private_change_pp`, `groups_pp`).
Fix: "All three are in `results.json`: the Shapley split at the top level, the other two under `sensitivity`."

### R-20261113r-B4 · baseline · doc-29e024ea.md
**Location:** doc-29e024ea.md:49
Problem: "the private-label line jumps and the bank line falls in that quarter" is only true of the contribution lines in path.csv (private-label 2.26→4.36 pp, banks 0.88→−0.06 pp). The holdings move the other way: private-label holdings fall and bank holdings rise. Read as holdings, the sentence states the opposite of what happened.
Fix: "Card ABS moved onto bank balance sheets, so in path.csv the private-label contribution jumps and the bank contribution falls in that quarter."

### R-20261113r-B5 · baseline · doc-29e024ea.md
**Location:** doc-29e024ea.md:9
Check C5 covers only the +13.1 pp jump. The levels 36.1% and 49.2% are check C4. Fix: "(validation checks C4, C5)".
