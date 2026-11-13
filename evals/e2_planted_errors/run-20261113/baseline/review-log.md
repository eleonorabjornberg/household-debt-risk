# E2 review log, run-20261113 (baseline)

Assembled by the coordinator from each reviewer's returned report. Entry ids renumbered to be unique; Severity lines normalised to bold so score.py reads them; text otherwise verbatim.

### R-20261113-B1 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:21
**Problem:** The sentence "Adding the Fed's own agency MBS holdings on top of the agency pools gives the full public book" contradicts the method stated elsewhere. Section 4 (doc-01bab658.md:170) says "the Fed's MBS are inside the public share, not on top of it", and finding 7 (doc-01bab658.md:15) says the same. Adding Fed MBS on top would count about $1.96T (10.3 pp) twice. None of the public-book figures in the document ($10.77T, 56.4%) include such an add-on.
**Fix:** Delete the line, or reword it to say the Fed's holdings are already part of the GSE/agency bucket.

### R-20261113-B2 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:196
**Problem:** The 2006Q1 numbers don't add up. "Other non-revolving" fell from $640.8B to $233.1B, a drop of $407.7B, yet the text says $481.0B of student loans was carved out. That would mean the series grew by about $73B in the same quarter, which is implausible. The stated jump in the uncollateralized share (7.6% to 11.5%, +3.9 pp of roughly $12.3T of scope debt, so about $480B) fits $481B. So one of the two levels ($640.8B or $233.1B) is probably wrong.
**Fix:** Recheck the FL153166205 levels against the source data.

### R-20261113-B3 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:3
**Problem:** The data line reads "Fed NY Fed credit-report Financial Accounts", which mixes up two sources. The Financial Accounts (Z.1) come from the Federal Reserve Board and are built from lender balance sheets. The NY Fed's credit-report data (the Consumer Credit Panel, used for the Household Debt and Credit report) is a separate source, and section 7 (doc-01bab658.md:253-259) explicitly contrasts the two.
**Fix:** "Federal Reserve Z.1 Financial Accounts".

### R-20261113-B4 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:42
**Problem:** The identity "FL153165105 + FL153166000 = FL154104015" is listed as exact from 1952 to 2026, but caveat 3 (doc-01bab658.md:270) says the scope leaves out commercial mortgages and other loans. Any Z.1 total-debt or total-liabilities series for households includes those, so mortgages plus consumer credit cannot equal it exactly. The series ID also looks wrong: the household debt totals are FL154104005 and FL154190005.
**Fix:** Check which series the identity really targets, then correct the ID or drop the "exact" claim.

### R-20261113-B5 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:212
**Problem:** "2020 is unusual: unsecured debt fell during a recession" is contradicted by the table above it. In the 2001 window the uncollateralized share fell from 10.5% to 10.2% to 7.7% (doc-01bab658.md:208), and the sentence just before says card balances shrank relative to total debt in every crisis since 2001.
**Fix:** Drop "unusual", or say what is actually different about 2020.

### R-20261113-B6 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:11
**Problem:** "52% of quarters and 50% of the rise, which is exactly proportional" overstates it: 50% against 52% is roughly proportional, not exactly. Section 1 (doc-01bab658.md:108) gives the same two figures without the word "exactly".
**Fix:** "roughly proportional".

### R-20261113-B7 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:264
**Problem:** "the federal government already holds 86% of it" names the wrong holder. The 86.4% figure (doc-01bab658.md:14, 237) is the share held by the whole public sector, which also includes GSEs and state and local governments. Before 2004 Sallie Mae was a GSE, and the student-loan share of the public book counts GSE holdings.
**Fix:** "the public sector (almost all of it federal) holds 86%", or give the federal-only figure from a register row.

### R-20261113-B8 · baseline · doc-01bab658.md
**Location:** doc-01bab658.md:265
**Problem:** "Private-sector stress shows in cards and autos" has no support in the document.
- **Cards:** the uncollateralized share is 16.6% against 16.5% a year ago, and cards are not shown rising.
- **Autos:** the durables proxy (5.8×) is above its 2007Q4 level (5.6×) and its 2017Q3 low (4.77×), and the document itself says the proxy overstates collateral severalfold (doc-01bab658.md:274).

Comparing it with 1990 (6.9×) does not show current stress. The finding also clashes with the rule against presenting proxy readings as fact.
**Fix:** Soften the claim or cite a stress measure such as delinquency rates.

### R-20261113-B9 · baseline · doc-2677667e.md
`doc-2677667e.md:10`: The period is wrong. It says the total "$19.10T in **2027Q2**", but the register row `scope_usd_2026q2` and the memo's sources table (line 40) give 2026Q2. 2027Q2 is in the future (today is 2026-11-13). It should read 2026Q2.

### R-20261113-B10 · baseline · doc-2677667e.md
`doc-2677667e.md:28`: The vintage is wrong. It says "these figures are the **2025-12-11** vintage", but the banner (line 1), the header (line 4) and every Z.1 row in the sources table give Z.1 vintage 2026-09-11. It should read 2026-09-11.

### R-20261113-B11 · baseline · doc-2677667e.md
`doc-2677667e.md:44`, `:47`, `:48`, `:49`: The sources table shows the wrong validation status for four rows. It lists them as UNVERIFIED, but the register has PASS for each: `public_share_of_student_loans`, `public_share_of_uncoll_2026q2`, `public_share_of_uncoll_2007q4` and `home_coverage_2026q2`.

### R-20261113-B12 · baseline · doc-2677667e.md
`doc-2677667e.md:12`, `:13`, `:14`, `:15`, `:16`, `:25`, `:33`: The body states numbers whose register rows are UNVERIFIED as plain fact, which breaks the project rule "never present an unverified number as fact". The numbers are:
- the FFEL 97-98% guarantee (`ffel_guarantee`, which the register notes still needs a primary source)
- the 16.6% uncollateralized share
- the 1.85x low in 2012Q1
- the $1.71T private-label change
- all the CRT figures on line 16 (55.2%, 1.2 pp, 56.2%, $40.0B, $181.5B)
- NY Fed $18.77T
- Fed-held MBS $1.90T

Only the student-loan split (line 13) carries a proxy label. These numbers need labels in the text, or they should be held back until validated. As a two-page memo, this also fails the research-memo gate, which requires every number to pass claim-check.

### R-20261113-B13 · baseline · doc-2677667e.md
`doc-2677667e.md:15`: A caveat is missing, and the sentence misleads without it. The register note for `a1_pls_change_usd` says the $1.71T fall "includes card ABS moved onto bank balance sheets by FAS 166/167 in 2010Q1 (accounting, not retreat)". The memo describes it only as private-label securitization and mortgage REITs holding less household debt, which reads as a market retreat. That matters for a bank treasury reader, because part of the drop is balances that moved onto banks' own books.

### R-20261113-B14 · baseline · doc-2677667e.md
`doc-2677667e.md:1` and `:4`: The source lists in the banner and header are incomplete. Neither names the Freddie Mac 10-K (vintage 2026-02-12), which lines 16, 56, 57 and 58 rely on, or FRED (vintage 2026-10-27), which line 33 and line 60 rely on. Line 1 says only "FHFA Credit Risk Transfer (CRT) reports", but the 56.2%, $40.0B and $181.5B figures come from the Freddie 10-K, not FHFA.

### R-20261113-B15 · baseline · doc-2677667e.md
`doc-2677667e.md:16`: The mortgage insurance figure is described loosely and without its exclusion. The register row `a2_fre_pmi_out_2025` covers *primary* mortgage insurance in force, and it excludes loans whose servicing Freddie does not control (10-K footnote). The memo says only "mortgage insurance in force", which overstates what the $181.5B covers.

### R-20261113-B16 · baseline · doc-2677667e.md
`doc-2677667e.md:25`: A sentence is out of place and its subject is unclear. "It is built from sampled credit reports." comes after a sentence about both sources, so "It" could mean Z.1 or the NY Fed data. It belongs right after the NY Fed sentence ("The NY Fed credit-report data, ... built from sampled credit reports, show ..."), before the warning not to compare the two.

### R-20261113-B17 · baseline · doc-2677667e.md
`doc-2677667e.md:7` and `:15`: Two minor wording problems.
- Line 7 switches tense: public holders "held" 56.4%, then private lenders "hold the rest".
- Line 15's heading "After 2008" sits over a baseline at 2007Q4, the NBER peak. A heading such as "2007Q4 to 2011Q4" would match the content.

### R-20261113-B18 · baseline · doc-432a89ed.md
**Location:** doc-432a89ed.md:10 (conflicts with doc-432a89ed.md:22)
**Problem:** The scope of "public" contradicts itself. Line 10 says the public share here leaves out state and local governments. Line 22 then lists "state and local" among "all other public holders combined". Only one of these can be true. If state and local are out of scope, remove them from line 22. If they are in scope, line 10 is wrong. The 36.1% and 49.2% figures depend on which one is right.

### R-20261113-B19 · baseline · doc-432a89ed.md
**Location:** doc-432a89ed.md:31
**Problem:** "The 2008 rescues caused this shift directly." is a causal claim with no support. It contradicts the rest of the document:
- line 26: the decomposition "says nothing about cause"
- line 32: "These data cannot test whether the conservatorship ratcheted risk onto the public"
- line 36: "The decomposition is an accounting; the causal estimate is A7"

It also sits on its own line outside the bullet structure, so it looks like a stray insertion. Delete it, or rewrite it as a timing observation with no causal language.

### R-20261113-B20 · baseline · doc-432a89ed.md
**Location:** doc-432a89ed.md:51
**Problem:** The FAS 166/167 effect is described backwards. Consolidation moved card ABS off the securitization/ABS (private-label) line and onto bank balance sheets. So in 2010Q1 the private-label line falls and the bank line jumps. The text says "the private-label line jumps and the bank line falls". Line 24 describes the direction correctly ("onto bank balance sheets"), so the two passages also disagree with each other.

### R-20261113-B21 · baseline · doc-432a89ed.md
**Location:** doc-432a89ed.md:50
**Problem (minor):** "Most FFEL loans held by banks before 2010 already carried a federal guarantee" understates it. FFEL loans are federally guaranteed (reinsured) by definition, so "all", or "essentially all", is accurate. The conclusion that the student-loan component overstates the shift in credit risk is right, and the correct wording makes it stronger.

### R-20261113-B22 · baseline · doc-432a89ed.md
**Location:** doc-432a89ed.md:56
**Problem (minor, ambiguous):** "by up to $21.4B ($14.6B in 1980Q4)". The parenthetical gives a quarter and an amount that is not the maximum, so it reads as if the date of the $21.4B maximum was meant and either the number or the quarter is wrong. Either give the quarter of the $21.4B maximum or explain why 1980Q4 is cited. A smaller point: the gap ends in 1986Q3, so "1987 onwards" is cautious rather than exact (1986Q4 is already clean). Worth saying so explicitly.

### R-20261113-B23 · baseline · doc-4af129f3.md
**Location:** doc-4af129f3.md:44
**Problem:** The range "between 56.2% and 56.2%" has the same number at both ends. By the sentence's own definition, the lower end nets all CRT issued by both Enterprises (the FHFA issuance bound). Lines 20 and 23 put that at 55.2% (56.4% gross less at most 1.2 pp). The upper end is 56.2%, which fits: Freddie's $37.3B is about 0.2 pp. So the bullet should read "between 55.2% and 56.2%". As written, the range looks like a point estimate. It also hides that line 11's combined figure, 56.0%, sits inside the range.

### R-20261113-B24 · baseline · doc-4af129f3.md
**Location:** doc-4af129f3.md:59
**Problem:** The text says Freddie's caveat means "a smaller maximum coverage need not mean less protection". The caveat it points to (line 24) says the reverse. Freddie now keeps higher initial losses, so its benefits "may be lower ... even if the maximum coverage ... is similar". In other words, similar or equal maximum coverage can still mean *less* protection. The caveat does not support the claim that smaller coverage need not mean less protection. The limit should say that maximum coverage overstates protection when Freddie keeps more first loss. That is the conservative direction for the net figures.

### R-20261113-B25 · baseline · doc-4af129f3.md
**Location:** doc-4af129f3.md:23
**Problem:** "The bound bears the losses on in every year 2013–2025" does not make sense; it looks like an editing slip. The intended meaning is probably "The bound holds in every year 2013–2025 (`net_exposure.csv`)", i.e. net ≤ gross and the lower bound stays positive, as line 69 describes.

### R-20261113-B26 · baseline · doc-4af129f3.md
**Location:** doc-4af129f3.md:37
**Problem (minor, rounding):** Using the figures as shown, "$2.93T less $37.3B" is $2.8927T, which rounds to $2.89T, not $2.90T. The $2.90T is only right if unrounded gross is at least about $2.9323T. A reader checking the arithmetic will get a different answer. Either show more precision or note that the inputs are rounded.

### R-20261113-B27 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:3`, `doc-cc89f643.md:5`
**Severity:** high
The banner says "The numbers are checked and registered". Line 5 implies the same. In `claims/register.csv`, only three of the numbers here have validation status PASS: 36.1%, 49.2% and 13.1 pp (checks C4 and C5). The other 23 register rows that cite this README are UNVERIFIED. That covers the 6.2/6.9 split, every table row, the own-share figures, the path figures, $4.34T, $1.13T, the $20B bound and the pool-gap figures. The project rule is never to present an unverified number as fact. The text should either say most figures are registered but not yet verified, or label them.

### R-20261113-B28 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:53`
**Severity:** medium
The 6.1 pp counterfactual quoted from `analysis/findings.md` has no register row for this location. Row `gfc_counterfactual_pp` lists only `analysis/findings.md:12`, and that row is also UNVERIFIED. Line 5 says "Every number here has a row", and this number breaks that.

### R-20261113-B29 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:11` (and `doc-cc89f643.md:29`)
**Severity:** medium
"The quarter-by-quarter Shapley path matches the Shapley endpoints to one decimal" holds only for the public and private totals: 6.21 vs 6.25, and 6.89 vs 6.86. It fails for components:

| Component | Chained path | Endpoint Shapley |
|---|---|---|
| Fannie and Freddie | 1.38 (1.4) | 1.25 (1.2) |
| Federal student loans | 1.61 (1.6) | 1.70 (1.7) |

Line 29 then mixes the two methods. Its 1.1 pp in 2008Q2, 2.3 pp peak and "fell back" come from the chained `path.csv`, which ends at 1.4 pp. The table at line 19 gives 1.2 pp, from endpoint Shapley. The sentence should be limited to the side totals, and line 29 should say which method its figures come from.

### R-20261113-B30 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:23`
**Severity:** medium
The $1.71T / 5.7 pp group is called "Private-label securitization and mortgage REITs". It also includes consumer-credit ABS issuers. In `decomposition.csv`, consumer-credit ABS issuers held $606B less, which is 2.0 pp of the 5.7. That is the card ABS that FAS 166/167 moved onto bank and finance-company balance sheets. With a mortgage-sounding label, readers will take the 5.7 pp as a retreat from private mortgage lending, when about a third of it is consumer ABS, much of it the 2010Q1 consolidation. The label should be "private securitization (mortgage and consumer ABS) and mortgage REITs", and the consumer ABS part should be stated.

### R-20261113-B31 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:49`
**Severity:** low
"The private-label line jumps and the bank line falls in that quarter" is only right for the contribution lines in `path.csv`: private-label goes from 2.26 to 4.36, and banks from 0.88 to -0.06. In holdings, which is what the sentence is about ("Card ABS moved onto bank balance sheets"), the opposite happens: securitized holdings fall and bank holdings rise. The sentence should say it means contribution lines in `path.csv`.

### R-20261113-B32 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:48`
**Severity:** low
"Most FFEL loans held by banks before 2010 already carried a federal guarantee" understates the guarantee. Every FFEL loan was guaranteed by a guaranty agency and reinsured by the Department of Education, usually for 97–98% of principal. The accurate wording is "all, at 97–98% of principal". That makes the overstatement of risk transfer in the student-loan component stronger than the text says.

### R-20261113-B33 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:54`
**Severity:** low
The gap runs to 1986Q3, so data from 1986Q4 onward is clean, and "stay inside 1987 onwards" is one quarter too strict. The sentence "A1 should stay inside 1987 onwards with these cells until the gap is explained" is also garbled. Suggested: "Uses of these cells should start in 1986Q4 or later until the gap is explained."

### R-20261113-B34 · baseline · doc-cc89f643.md
Location: `doc-cc89f643.md:43`
**Severity:** low
The policy table is meant to run in date order, but the "2010Q1" FAS 166/167 row sits before the 30 Mar 2010 row. Its only specific date is the Z.1 release of 10 Jun 2010, and it takes effect from 1 Jan 2010. It should go either first in 2010 (effective date) or after 30 Mar (release date), with the date basis stated.
