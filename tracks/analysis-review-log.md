Review entries from the analysis track; the coordinator moves them into `claims/review-log.md` on merge (renumbering if ids collide).

### R-20261104-1 · skeptic · research/a2_net_exposure/README.md:16 (a2_public_share_net_lower_2025q4, a2_net_ff_lower_hh)
- **Objection:** The table labels G − cumulative CRT RIF as "Net, lower bound" and the public share as "at least 55.2%". That is a lower bound only on net-of-CRT exposure. Once mortgage insurance is netted (FHFA PMI RIF is 12.5% of 2023 gross by the same method), true net exposure can be well below $6.05T and 55.2%. Read alone, the table row says the public share cannot be below 55.2%.
- **Severity:** major
- **Evidence:** README.md:13-16 table header "Net, lower bound (all issued CRT still in force)"; README.md:21 and net_exposure.csv 2023 pmi_issued_pct_of_gross = 12.5191; register rows 4 and 8 say "at least".
- **Proposed resolution:** Relabel as "net of CRT only, before mortgage insurance" in the table and in register claims 4 and 8, and add one sentence saying PMI could lower net further.
- **Status:** open

### R-20261104-2 · skeptic · research/a2_net_exposure/README.md:16,19 (a2_public_share_gap_pp)
- **Objection:** "Public share net" is (public principal − RIF)/S. That mixes loss capacity with principal and treats $1 of RIF as $1 of principal moved to the private side, so 55.2% is not a share of anything observable. Line 19 adds a caveat, but the table cell at line 16 (and register row 8) carries the number without it.
- **Severity:** major
- **Evidence:** net_exposure.py:85 `100 * (pub - crt["cum_rif_musd"] * a) / s`; METHOD.md:15.
- **Proposed resolution:** Put the "loss capacity against principal" caveat in the table and in the register claim text, or report the gap as RIF/S rather than as a "share".
- **Status:** open

### R-20261104-3 · skeptic · research/a2_net_exposure/README.md:20
- **Objection:** The FHFA "majority" quote is attributed to CRT ("the share transferred on covered loans is much larger"). FHFA says "Through CRT **and mortgage insurance**, the majority…". The claim that the CRT slice is "where most stress losses fall" is unsourced.
- **Severity:** major
- **Evidence:** sources.md:9 (4Q2019 quote); same wording in the Dec 2016 extract, line 38.
- **Proposed resolution:** Quote FHFA in full, including "and mortgage insurance", and source the stress-loss statement or label it as an assumption.
- **Status:** open

### R-20261104-4 · skeptic · research/a2_net_exposure/README.md:21 (a2_pmi_cum_rif)
- **Objection:** "Mortgage insurance is larger than CRT in RIF terms" contradicts the project's own source: FHFA 4Q23 p.8 says "the RIF figures for these two categories are not strictly comparable".
- **Severity:** minor
- **Evidence:** sources.md:13 quote.
- **Proposed resolution:** Drop the comparison or carry FHFA's caveat next to it.
- **Status:** open

### R-20261104-5 · skeptic · research/a2_net_exposure/README.md:22, METHOD.md:14 (a2_crt_ref_upb_over_gross)
- **Objection:** The 1.1× is explained only "because refinanced loans are counted again". FHFA's own footnote says the same reference UPB may back both a STACR and an ACIS deal, and cumulative UPB also keeps loans that have paid off without refinancing.
- **Severity:** minor
- **Evidence:** CRT-Progress-Report-4Q22 extract, Freddie table footnote 5: "The same reference pool UPB may back STACR and ACIS transactions."
- **Proposed resolution:** List all three causes; drop "because".
- **Status:** open

### R-20261104-6 · skeptic · research/a2_net_exposure/crt_fhfa.csv:7-8
- **Objection:** The PMI UPB for 2018 and 2019 uses the rounded text figures ($1.2T, $1.6T). The chart boxes in the same reports give $1,231B and $1,570B, and 2020 onward uses the boxes. The column is not used in any output; RIF values match.
- **Severity:** minor
- **Evidence:** 4Q18 extract line 611 "Total $1,231"; 4Q2019 extract shows "Total $1,570".
- **Proposed resolution:** Use the box values, or document the mixed basis.
- **Status:** open

### Responses (analysis track, 2026-11-04)
- R-20261104-1: accepted. Table header and register rows now say "net of CRT only, mortgage insurance not netted"; README states 55.2% is not a floor once MI is netted.
- R-20261104-2: accepted. Table header now says principal less CRT loss capacity; register claims say "RIF subtracted from principal".
- R-20261104-3: accepted. The FHFA "majority" quote is now attributed to CRT and mortgage insurance together; the unsourced "most stress losses fall" clause is removed.
- R-20261104-4: accepted. README quotes FHFA's "not strictly comparable".
- R-20261104-5: accepted. README and METHOD now give all three reasons (paid-off loans kept at issuance balance, refinanced loans counted again, STACR/ACIS sharing a pool).
- R-20261104-6: noted, not changed. The column is unused; the basis column already says the 2018–19 PMI UPB is the rounded text figure.

### R-20261104-7 · skeptic · research/a5_distribution/README.md:15 (a5_top10_mortgage_2026q2)
- **Objection:** The top 10% share of home mortgages is the sum of three rounded shares (0.8 + 3.2 + 24.4 = 28.4). Computed from the levels file it is 28.48%, which displays as 28.5%. The printed number is wrong at display precision. The same rounding is why the table's mortgage column sums to 99.9.
- **Severity:** blocker
- **Evidence:** distribution.py:165,180 sums `dfa-networth-shares.csv` (published to 0.1). Recompute from `dfa-networth-levels.csv` 2026:Q2: (117243+453093+3410241)/13976937 = 0.28480. Top 10% net worth by the same method is 0.68918, so 68.9% is unaffected.
- **Proposed resolution:** Compute group sums from the levels (or from shares-detail) and not from rounded shares, then rerun and update README:15, results.json and the register row. Apply the same fix to `top20_mortgages`, which happens to be right (0.53159, so 53.2%).
- **Status:** open

### R-20261104-8 · skeptic · research/a5_distribution/AVAILABILITY.md:13
- **Objection:** The row label "Who holds (and so carries) the risk by loan type" treats holding as bearing risk. Holding and risk differ in both directions: GSE pools shed part of the risk through CRT and private MI (A2), and privately held FFEL student loans are federally guaranteed. The 65.6% and 31.3% public shares (README:23) are shares of holdings, not of risk.
- **Severity:** major
- **Evidence:** AVAILABILITY.md:13. A2 shows net-of-CRT and MI exposure below gross. The README:23 wording ("hold") is correct; the availability note is not.
- **Proposed resolution:** Change it to "Who holds the loans, by loan type". Add one README sentence saying holding is not bearing risk and pointing to A2.
- **Status:** open

### R-20261104-9 · skeptic · research/a5_distribution/README.md:17-19
- **Objection:** The groups are ranked by net worth, and debt lowers net worth. So "the bottom half owes half the consumer credit" and its high leverage partly restate how the bottom 50% is defined. Membership also changes with house prices. The bottom-50 mortgage share was 34.6% in 2010Q3 and 22.1% in 2021Q1: underwater owners fell into the bottom half and then rose out of it. The 1989-vs-2026 endpoint comparison hides this. Read as "who borrows", it suggests a fixed population that changed its borrowing.
- **Severity:** major
- **Evidence:** figures/dfa_bottom50_shares.alt.txt (high 34.6% in 2010Q3; low 22.1% in 2021Q1). README:19 already notes the house-price effect on the ratios but not on group membership.
- **Proposed resolution:** Add a caveat that wealth groups are re-ranked each quarter and that debt enters the ranking. Show income groups (less endogenous) next to them, or say the 1989 comparison runs between different populations.
- **Status:** open

### R-20261104-10 · skeptic · research/a5_distribution/README.md:19 (a5_b50_leverage_2007q4)
- **Objection:** "Lower than in 2007" uses 2007Q4 as the reference. Bottom-50 liabilities/assets peaked at 95.3% in 2010Q4, not in 2007. The sentence is true, but readers will take 81.5% as the peak.
- **Severity:** minor
- **Evidence:** From dfa-networth-levels.csv, the Bottom50 Liabilities/Assets maximum is 2010:Q4 = 0.9530 (2007:Q4 = 0.8149, 2026:Q2 = 0.5836).
- **Proposed resolution:** Either state the 2010Q4 peak as well (it needs a register row) or say "down from 81.5% on the eve of the crisis".
- **Status:** open

### R-20261104-11 · skeptic · research/a5_distribution/README.md:27; figures/state_mortgage_pc_2025.*
- **Objection:** The "3.8× spread" across states comes from DC, a city-jurisdiction outlier. Among the 50 states the spread is CO/WV = 3.5×. DC is also the maximum for student loans (12,650 against GA 7,120 next). On the sextile maps DC sits in the same top bin as every state from $55.6k up ($6.1k up for student loans), so the map understates DC while the text headline leans on it.
- **Severity:** minor
- **Evidence:** state_2025.csv: 72210/20770 = 3.48; mortgage sextile breaks [20770, 30540, 33813, 40310, 46350, 55600, 78140].
- **Proposed resolution:** Give the 50-state spread next to the figure that includes DC, or footnote that DC is a city. Optionally mark DC as an outlier in the map legend.
- **Status:** open

### R-20261104-12 · skeptic · research/a5_distribution/README.md:27-28, 34
- **Objection:** The extremes are single sample-based values with no stated uncertainty. WY's student-loan minimum comes from a 1% sample (about 5k people) and fell 10% in one year (3,530 to 3,180), which suggests noise. Separately, README:27 says "mortgage debt" without "excluding HELOC". The DFA and Z.1 home mortgages used two sections earlier include HELOCs, so the three mortgage measures in the README are not the same object.
- **Severity:** minor
- **Evidence:** area_report_by_year.xlsx Info sheet: "Mortgage Debt Balance per Capita (excluding HELOC)", "Student Loan ... 1% of the population". The studentloan sheet row WY reads Q4_2024 3530, Q4_2025 3180. HI 3,810 is next lowest.
- **Proposed resolution:** Write "mortgage debt (excluding HELOCs)" at README:27 and in the map title. Add "single-year sample estimates; rankings near the extremes may not be significant".
- **Status:** open

### R-20261104-13 · skeptic · claims/tracks/analysis.csv (a5_ rows); README.md:23
- **Objection:** Two register gaps. (1) README:23 prints 65.6%, but no a5 row covers it, and the main row `public_share_mortgage_2026q2` lists only analysis/findings.md and recommendation.md as locations. (2) The NY Fed rows give vintage `nyfedstate:2026-02-01`, but the workbook gives only "February 2026", so the day is invented.
- **Severity:** minor
- **Evidence:** `grep 0.6555 claims/tracks/analysis.csv` finds nothing. claims/register.csv:11 has the locations. The Info sheet citation reads "...Federal Reserve Bank of New York, February 2026".
- **Proposed resolution:** Add README:23 as a location for public_share_mortgage_2026q2 on merge, like the CC fold note. Use `nyfedstate:2026-02` or the file's Last-Modified date, with its source stated.
- **Status:** open

### Responses to R-20261104-7 to -13 (analysis track, 2026-11-04)
- R-7 (blocker): accepted. Group sums now come from DFA levels in `distribution.py`; the top 10% share reads 28.5%; register row corrected.
- R-8: accepted. AVAILABILITY.md now says holding is not bearing the risk, with CRT, mortgage insurance and FFEL as examples.
- R-9: accepted. README says groups are ranked by net worth (debt lowers it), that membership moves with house prices, and gives the 2010Q3 peak.
- R-10: accepted. README gives the 2010Q4 leverage peak next to the 2007Q4 figure.
- R-11: accepted. README gives the spread across the 50 states alone (3.5×, Colorado) and notes that DC shares the top map band.
- R-12: accepted. README says the extremes are single sample estimates and that the NY Fed mortgage series excludes HELOCs.
- R-13: partly. The vintage day is a placeholder the checker's format requires; register notes now say so. The 65.6% location belongs on the existing register row for the public share of mortgages (claims/register.csv, coordinator-owned); listed under "Proposed changes to shared files".

### R-20261104-14 · skeptic · research/a2_net_exposure/tenk.py:18-23; README.md:31,34,39; METHOD.md:34
- **Objection:** "CRT" is coded as STACR + ACIS (insurance/reinsurance) only, but Freddie's own FY2025 10-K lists "Other" under "CRT transactions" (Table 22), and in FY2017-FY2020 the "other" bucket is mostly senior/subordinate and lender risk sharing, which FHFA's CRT totals (the issuance bound) also count as CRT. The Freddie "net of CRT" ($2.90T, 1.3%, 56.2%) therefore uses a narrower CRT definition than the bound it is checked against; up to $10.4B of 2025 CRT-type cover sits in "other".
- **Severity:** major
- **Evidence:** data/a2/freddie/10k_021226.txt:2455-2461 ("CRT transactions: STACR ... ACIS ... Other ... Total CRT issuance"); 10k_021121.txt FY2020 Table 20: Subordination 6,182 + Lender risk sharing 4,831 + Other 371 = 11,384 = csv other_maxcov 2020. (40.0+10.4)/40.0 = 1.26x the netted cover.
- **Proposed resolution:** say in README/METHOD that the bucket is narrower than FHFA's CRT and Freddie's own; report the share with "other" netted as a sensitivity (56.2% stays a valid upper bound either way).
- **Status:** open

### R-20261104-15 · skeptic · research/a2_net_exposure/README.md:20 vs 10-K first-loss columns
- **Objection:** README says the tranches sold "sit above a retained first-loss slice". Freddie's FY2018-19 tables show third parties holding first-loss coverage (2019: STACR $5.9B, insurance/reinsurance $2.5B), and the FY2025 10-K says Freddie has recently moved to retaining more initial loss, so "benefits ... may be lower ... even if the maximum coverage ... is similar". Maximum coverage is therefore not comparable over time as protection, which affects the 1.8% to 1.3% reading.
- **Severity:** major
- **Evidence:** research/a2_net_exposure/fixtures/freddie_10k_fy2019_excerpt.txt (First Loss column); data/a2/freddie/10k_021226.txt:2444-2448.
- **Proposed resolution:** correct line 20; add the 10-K caveat beside line 36 that a fall (or a flat line) in maximum coverage does not mean a fall (or no change) in risk transferred.
- **Status:** open

### R-20261104-16 · skeptic · research/a2_net_exposure/README.md:28-34
- **Objection:** The table mixes bases without saying so. Gross and net are household-apportioned, but CRT ($40.0B), mortgage insurance ($181.5B) and other ($10.4B) are not. A reader computing $2.93T - $40.0B gets $2.89T, not the $2.90T shown (apportioned CRT is $37.3B).
- **Severity:** minor
- **Evidence:** results.json freddie_10k: crt_out_bn_unapportioned_last 40.0, crt_out_hh_bn_last 37.3, net 2895.4.
- **Proposed resolution:** label those rows "all borrowers, not apportioned", or show the $37.3B household figure.
- **Status:** open

### R-20261104-17 · skeptic · research/a2_net_exposure/README.md:36-38; claims/tracks/analysis.csv
- **Objection:** Line 36 ("cover runs off as notes pay down and Freddie has issued less since 2022") explains the fall with no decomposition and no registered source for Freddie's 2024-25 issuance (crt_fhfa.csv has no Freddie figure after 2023). Also unregistered: "more than four times" (l.38) and the 55.2% at l.39 (its row's locations do not include README:39).
- **Severity:** minor
- **Evidence:** crt_fhfa.csv fre_cum_rif_musd empty for 2024-2025; `grep "README.md:39" claims/tracks/analysis.csv` returns only a2_share_net_freddie_crt_2025.
- **Proposed resolution:** cite 10-K FY2025 Table 22 (issuance 2023-25: $4.2B, $6.0B, $5.7B) or drop the explanation; add the register locations.
- **Status:** open

### R-20261104-18 · skeptic · research/a5_distribution/README.md:37
- **Objection:** "By either method the public sector holds about half or more of every wealth group's debt" is presented as a finding, but it follows from the uniform-mortgage-share assumption: each group's percentage is just its own mortgage/consumer-credit mix weighted by 65.6% and 31.3%. The assumption also biases the top, not only the bottom. Jumbo loans are not GSE-eligible and are held mostly by banks, so the top 1% figure (51-58%) is probably overstated. Line 27 mentions only the bottom-side bias.
- **Severity:** major
- **Evidence:** public_by_group.py:108-109 (public_b = M*p_M + CC*p_CC); results_public_by_group.json Top1 public_b_pct_of_debt 0.5793.
- **Proposed resolution:** reword as an implication of the assumption, and add the top-end (jumbo) bias to the caveat at l.27.
- **Status:** open

### R-20261104-19 · skeptic · research/a5_distribution/README.md:27-29 (assumptions of option c)
- **Objection:** The README leaves out several assumptions that (c) depends on: (i) the federal share of student loans is the same in every group (only the docstring says so); (ii) the SCF captures about $1.15T of education loans against Z.1's $1.86T, so the missing 38% is assumed to be distributed like the reported part; (iii) SCF NETWORTH excludes DB pension entitlements, which the DFA includes, so SCF and DFA wealth groups are different households. The script's own plausibility check shows the gap: consumer-credit shares are SCF 5.9% vs DFA 10.3% for the Next 9%, and 1.2% vs 3.2% for the Top 1%. That check is not reported in the README.
- **Severity:** major
- **Evidence:** my run on data/a5/scfp2025excel.zip: weighted EDN_INST total $1.15T; sum of imputed_student_loans_musd = $1.858T; public_by_group.csv scf_cc_share vs dfa_cc_share columns.
- **Proposed resolution:** state (i)-(iii) and the SCF/DFA gap in the README caveat box.
- **Status:** open

### R-20261104-20 · skeptic · research/a5_distribution/public_by_group.py:59-71 (income cuts)
- **Objection:** SCF INCOME is heaped at round values, so the weighted cut points give income "quintiles" with population shares of 19.3/20.4/19.0/21.0/19.2/1.0%, not 20% each. These are applied to DFA quintile levels. The non-monotonic student shares (20-40th: 19.8%, 40-60th: 16.2%) partly reflect this. Wealth cuts are fine (49.98/40.02/9.0/1.0). SCF INCOME is also 2024 income.
- **Severity:** minor
- **Evidence:** scratchpad check: INCOME pop shares [0.1932 0.2038 0.1904 0.2102 0.1924 0.0101].
- **Proposed resolution:** split ties at the cut points by weight (or report the pop shares), and note the income year.
- **Status:** open

### R-20261104-21 · skeptic · claims/tracks/analysis.csv a5_federal_share_student_loans; README.md:23,36
- **Objection:** "86.4% ... are federal" counts federally *held* loans (plus GSE FL403066005). It leaves out commercially held FFEL loans, which carry a federal guarantee, so as a measure of public risk it understates. README l.23 still says the tables "are shown side by side and not multiplied", which the new estimate section below it contradicts.
- **Severity:** minor
- **Evidence:** public_by_group.py:96; README.md:23 vs :25-38.
- **Proposed resolution:** say "federally held" in the claim; update l.23.
- **Status:** open

### Responses to R-20261104-14 to -21 (analysis track, 2026-11-04)
- R-14: accepted in part. CRT stays STACR + ACIS (the only CRT rows Freddie reports consistently since FY2021); README now says "Other" may include CRT-type cover (up to $10.4B at end 2025) and that the 56.2% upper bound holds whatever part of "Other" is counted.
- R-15: accepted. The "retained first-loss slice" sentence is replaced by Freddie's own FY2025 caveat (retaining "higher levels of initial losses"; benefits may be lower at similar maximum coverage) and the 2018–19 first-loss sales.
- R-16: accepted. Table now labels cover rows as unapportioned and adds the household-share CRT ($37.3B) actually subtracted.
- R-17: accepted. Unsourced runoff explanation removed ("not decomposed"); "more than four times" removed; 55.2% location added to its row.
- R-18: accepted. "About half or more" now framed as following from the assumption, with the jumbo-loan bias stated.
- R-19: accepted. Assumptions and gaps listed in the README. The skeptic's SCF total ($1.15T) also exposed a bug: a first version divided SCF weighted sums by five although the weights already sum to households; fixed and asserted (shares were unaffected).
- R-20: accepted as a note (income groups are not exact fifths; sizes in results_public_by_group.json).
- R-21: accepted. 86.4% now says "held by the federal government", excluding guaranteed FFEL; stale line 23 rewritten.
