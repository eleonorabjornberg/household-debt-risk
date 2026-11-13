# E2 review log, run-20261113r (baseline)

Assembled by the coordinator from each reviewer's returned hand-back message. Entry ids renumbered to be unique; `Severity:` labels made bold (including inline ones) so score.py reads them; text otherwise verbatim. Severity words are as the reviewer wrote them.

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

### R-20261113r-B6 · baseline · doc-2c30f9c7.md
**Location:** doc-2c30f9c7.md:24
Problem: The line says the public share here "leaves out state and local governments, unlike elsewhere in the project." That is false. The register rows for the A2 public share (a2_public_share_gross_2025q4, a2_public_share_net_lower_2025q4, a2_public_share_gap_pp) list FL213065103, the state and local series. The project's main definition is "federal direct + GSE/agency pools + state & local". The line is also an unbulleted sentence inside a bullet list. It looks inserted: the register's README line numbers for every row after it are shifted by one.
Fix: Delete the line. If a scope note is wanted, say the A2 public share uses the same definition as the rest of the project, state and local included.

### R-20261113r-B7 · baseline · doc-2c30f9c7.md
**Location:** doc-2c30f9c7.md:48
Problem: "Adding the Fed's own agency MBS holdings on top of the agency pools gives the full public book." This would count the same mortgages twice. Agency MBS held by the Fed are claims on the same agency pools already counted at gross. Nothing in A2 computes such a figure. It is also an unbulleted stray line, and the register line numbers after it shift by a second line, so it looks inserted too.
Fix: Delete the line, or say the reverse: the Fed's agency MBS holdings are claims on the same pools and must not be added on top.

### R-20261113r-B8 · baseline · doc-2c30f9c7.md
**Location:** doc-2c30f9c7.md:60
Problem: "2013–2016 cumulative RIF is the sum of FHFA's annual totals" is wrong for 2016. In crt_fhfa.csv only 2013–2015 are built as sums of published annual totals. The 2016 row's basis is "published cumulative totals" from the Dec 2016 report.
Fix: "2013–2015 cumulative RIF is the sum of FHFA's annual totals (2016 is FHFA's published cumulative), 2017 is derived from the 4Q 2018 report, …"

### R-20261113r-B9 · baseline · doc-2c30f9c7.md
**Location:** doc-2c30f9c7.md:61
Problem: The sentence gets Freddie's caveat backwards. Line 25 quotes it: the revised deals' benefits "may be lower … even if the maximum coverage … is similar". That means equal maximum coverage need not mean equal protection. It says nothing about a smaller maximum coverage still giving the same protection, and the direction it warns about is the opposite.
Fix: "Per Freddie's own caveat above, the same maximum coverage need not mean the same protection (newer deals may protect less)."

### R-20261113r-B10 · baseline · doc-2c30f9c7.md
**Location:** doc-2c30f9c7.md:7
Problem: The register is named as `claims/tracks/analysis.csv`. The A2 rows (a2_* rows, about lines 127–182, 242 and 557–560) are in `claims/register.csv`, which is also the register CLAUDE.md names. No `claims/tracks/` file is in the working folder. Low confidence: the full repo may have track files that I could not see.
   Fix: "Every number below has a register row (`claims/register.csv`)."

The other numbers match the data files after rounding. Lines 11, 19–23, 26–27, 35–46 and 52 match results.json and net_exposure.csv. The combined net share sits inside its bounds in 2017 and every year 2020–2025. Every Freddie row in freddie_ce_outstanding.csv sums to its total. The quotes and the 2018–19 first-loss statement match the fixtures and fannie_ce_outstanding.csv.

### R-20261113r-B11 · baseline · doc-67be578b.md
**Location:** doc-67be578b.md:12
- **Problem:** The sentence is garbled: "Privately bears the losses on debt **shrank 24.6% (−$2.07T)**". It has no clear subject. The register's claim for this figure reads "Privately held household debt shrank 24.6% from 2007Q4 to 2011Q4", and `ratchet_windows.csv` gives private_dollar_growth_pct = −24.6 for 2007Q4.
- **Fix:** "Privately held debt **shrank 24.6% (−$2.07T)**, led by private-label securitization, …"

### R-20261113r-B12 · baseline · doc-67be578b.md
**Location:** doc-67be578b.md:14
- **Problem:** The stray sentence "The 2008 rescues caused this shift directly." makes a causal claim that nothing in the analysis supports. It also contradicts its own finding:
  - Line 13's heading says the long climb is "mostly structural", from the GSE build-out (1980s, +18.8 pp).
  - Line 13 also says 1990 was "the trend continuing".
  - Line 107 calls the student-loan move "structural, not a crisis response".
  - Line 12 says even the 2007–11 jump is about half private retreat (Shapley: 6.9 pp private, 6.2 pp public).

  The sentence also breaks the numbered list between items 5 and 6.
- **Fix:** Delete the sentence.

### R-20261113r-B13 · baseline · doc-7326b106.md
**Location:** doc-7326b106.md:5
**Problem:** The vintage is wrong. The doc says the data is "`Z1.csv` dated 2025-12-11". But results.json `vintage_z1_csv` is "2026-09-11 10:41:06", validation/results.json gives vintage "2026-09-11 10:41", and every register row says z1:2026-09-11. The doc itself says 2026-09-11 at lines 54–55.
**Fix:** Change it to "`Z1.csv` dated 2026-09-11".

### R-20261113r-B14 · baseline · doc-7326b106.md
**Location:** doc-7326b106.md:29
**Problem:** The quarter is wrong. "1.1 pp by 2009Q2, the last quarter-end before the September 2008 conservatorship" can't be right: 2009Q2 comes after September 2008. In path.csv, fannie_freddie is 1.0899 at 2008Q2 and 2.0084 at 2009Q2. Register row a1_ff_chained_2008q2 says "By 2008Q2…".
**Fix:** Replace 2009Q2 with 2008Q2.

### R-20261113r-B15 · baseline · doc-7326b106.md
**Location:** doc-7326b106.md:3 (the banner; the same claim is implied at line 5)
**Problem:** The banner says "The numbers are checked and registered". They are registered, but almost none are checked. Every A1 register row (a1_public_growth_pp through a1_student_chained_2008q2, rows 106–126) has validation_status UNVERIFIED, and so does gfc_counterfactual_pp, which line 53 cites. Only the 36.1%, 49.2% and +13.1 pp figures have passed validation (C4/C5). CLAUDE.md forbids presenting unverified numbers as fact.
**Fix:** Say the numbers are registered, and that only the endpoint shares and the 13.1 pp jump (C4/C5) are validated so far. Or run claim-check and update the register statuses before keeping the claim.

### R-20261113r-B16 · baseline · doc-7326b106.md
**Location:** doc-7326b106.md:48
**Problem:** "Most FFEL loans held by banks before 2010 already carried a federal guarantee" understates the case. FFEL loans are federally guaranteed by design (through reinsured guaranty agencies, typically 97–98% of principal), so "most" suggests some weren't.
**Fix:** "FFEL loans held by banks before 2010 already carried a federal guarantee (typically 97–98% of principal)…"

### R-20261113r-B17 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:16
Problem: The doc says that net of all issued CRT the public share was "at least 56.2%". The register row a2_public_share_net_lower_2025q4 gives 55.2% (0.55236), and results.json gives public_share_net_lower_pct_last = 55.236. As written, the lower bound equals the Freddie-only upper bound (56.2%) later in the same bullet, so the range collapses. It also contradicts the 1.2 pp gap (56.386 - 55.236).
Fix: Change it to "the public share was at least 55.2% at end 2025".

### R-20261113r-B18 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:11
Problem: The bullet is labelled "(NY Fed credit-report)", but the 65.6% and 31.3% shares come from Z.1. Rows public_share_mortgage_2026q2 and public_share_cc_2026q2 use FL series with vintage z1:2026-09-11, and the Sources table on lines 42-43 says the same. The label also undercuts the caveat on line 25 about not mixing the two sources.
Fix: Change the label to "(Z.1)".

### R-20261113r-B19 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:13 and doc-ed3e7abc.md:26
Problem: Both lines say the student-loan split is imputed and should be treated as a proxy. That is only true before 2006: register row uncoll_break_2005q4 says "Pre-2006 student loans are imputed by a linear ramp". The 2026Q2 and 2007Q4 figures use the direct Z.1 series FL153166220 and FL313066220, and rows H12 to H14 are PASS with no imputation note.
Fix: Delete the proxy sentence on line 13. On line 26, either say the split is imputed only before 2006 (no figure in this memo uses that period) or remove the sentence.

### R-20261113r-B20 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:26 and doc-ed3e7abc.md:32
Problem: Both lines say Fannie Mae's outstanding CRT cover is not yet included or cannot yet be read. The register already has a2_fan_crt_out_2025 ($39B, from the Fannie 10-K) and a2_share_net_both_crt_2025 (56.0% net of both Enterprises' outstanding CRT). results.json has fannie_10k.public_share_net_both_crt_pct_last = 55.996 and a gap of 0.39 pp (row a2_gap_net_both_2025).
Fix: Either update the CRT bullet and the caveats to use the both-Enterprises figure (56.0%, about 0.4 pp below gross, Fannie rounded to $1B, labelled UNVERIFIED), or drop the "not yet included" wording. Change the line 32 watch item to something still open, such as rounding in Fannie's disclosure.

### R-20261113r-B21 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:44, 47, 48, 49 (Sources table)
Problem: The table marks four rows UNVERIFIED that are PASS in the register:
- public_share_of_student_loans (check H12)
- public_share_of_uncoll_2026q2 (H13)
- public_share_of_uncoll_2007q4 (H14)
- home_coverage_2026q2 (H11)
Fix: Change the Status of those four rows to PASS.

### R-20261113r-B22 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:12, 13, 14, 15, 16, 25, 33 (body text)
Problem: The body states as plain fact numbers whose register rows are UNVERIFIED:
- 97-98% (ffel_guarantee)
- 16.6% (uncollateralized_share)
- 1.85x (home_coverage_low)
- $1.71T (a1_pls_change_usd)
- all the CRT figures (55.2%, 1.2 pp, 56.2%, $40.0B, $181.5B)
- $18.77T (nyfed_total_2026q2)
- $1.90T (fed_mbs_weekly_usd)
The project rule is that unverified numbers are never presented as fact.
Fix: Mark each one in the text as "(unverified)", or validate it first. ffel_guarantee also needs a primary-source citation.

### R-20261113r-B23 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:15
Problem: The $1.71T drop for private-label securitization and mortgage REITs leaves out a caveat from the register: the change "includes card ABS moved onto bank balance sheets by FAS 166/167 in 2010Q1 (accounting, not retreat)". For a bank treasury reader, presenting it as a pure fall in private holdings is misleading.
Fix: Add something like "(includes card ABS consolidated onto bank balance sheets under FAS 166/167 in 2010, an accounting move, not a sale)".

### R-20261113r-B24 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:13
Problem: "51% of all uncollateralized household debt" overstates the scope. Row public_share_of_uncoll_2026q2 (H13) defines the denominator as revolving credit plus student loans. It leaves out other non-revolving credit ($378B), and including that gives 45%, a point still open for Eleonora.
Fix: Say "51% of uncollateralized household debt (revolving plus student loans)" and drop "all".

### R-20261113r-B25 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:27
Problem: "The register has no row for banks' share of household debt" is not accurate. Row e1_q116 (PASS) gives banks and credit unions 33.6% of household mortgages and consumer credit in 2026Q2. It is E1 benchmark gold, not published copy.
Fix: Reword to "The register has no published-copy row for banks' share..." or cite e1_q116 with its benchmark-only status.

### R-20261113r-B26 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:1 and doc-ed3e7abc.md:4
Problem: The vintage list is incomplete. It leaves out the Freddie Mac 10-K (freddie10k:2026-02-12), which is behind 56.2%, $40.0B and $181.5B, and FRED (fred:2026-10-27), which is behind $1.90T. Line 4 also gives no vintage for the FHFA CRT reports.
Fix: Add "Freddie Mac 10-K FY2025, 2026-02-12; FRED WSHOMCB, 2026-10-27" to both lines and "2026-11-04" to the FHFA entry on line 4. If item 4 is fixed with Fannie data, also add Fannie 10-K 2026-02-11.

### R-20261113r-B27 · baseline · doc-ed3e7abc.md
**Location:** doc-ed3e7abc.md:25
Problem: "It is built from sampled credit reports" comes right after a sentence about "the two" sources, so "It" is ambiguous.
Fix: Change it to "The NY Fed series is built from sampled credit reports" and move it next to the $18.77T sentence.
