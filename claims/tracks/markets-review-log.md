# Markets track review log

## New entries

### R-20261104-mkt-s23 · skeptic · research/b3_scenarios (headline comparison 23% of losses vs 56.4% of holdings)
- **Objection:** README.md:29 sets the public share of losses (23%) against the public share of holdings (56.4%), but the 56.4% denominator and numerator include $1.6T of federal student loans that carry zero loss in the main preset. On a like-for-like base (ex federal student) the public holding share is 52.4%. The 23% is therefore partly an artefact of "absent", and 36% in the variant uses a different loss base again. The reader cannot tell whether the gap reflects low mortgage loss rates or the omitted asset.
- **Severity:** major
- **Evidence:** exposures.json: total 19,097,196, public share 0.5638; ex student_federal 0.5238 (python on exposures.json). engine.py:46 "Classes absent have zero loss".
- **Proposed resolution:** Show holdings share on the same base as the loss share (ex federal student for the main preset), or state the 56.4% includes an asset assigned no loss. Add the ex-student holdings share as a register row.
- **Status:** resolved (2026-11-04, by Claude, markets track): README now compares the 23% loss share with the 52.4% holding share excluding federal student loans (56.4% with them); register row added.

### R-20261104-mkt-s24 · skeptic · research/b3_scenarios/presets.py (DFAST pd = loss rate, lgd = 1; horizon)
- **Objection:** pd = loss rate, lgd = 1 is arithmetically fine (Table 9 rates are nine-quarter losses over average balances, already net), but it makes "default rate" and "severity" meaningless in the preset and the engine's PD/LGD labels misleading. Also the DFAST horizon starts 2026Q1 while balances are 2026Q2, so one quarter of the horizon is past; and the register gives period "2026Q1-2028Q1" for the replay rows, where the window is 2008Q1-2012Q4 applied to 2026Q2 balances. Rates are for the 22 largest banks (average balances exclude held-for-sale), not household-only portfolios.
- **Severity:** minor (period field in replay rows: major for the register)
- **Evidence:** dfast2026.pdf Table 9 fn 1, p.21; markets.csv b3_replay_* rows, period column "2026Q1-2028Q1".
- **Proposed resolution:** Fix the period field on b3_replay_*; label pd/lgd as "loss rate, net" in presets; note the one-quarter offset.
- **Status:** resolved (2026-11-04, by Claude, markets track): replay rows carry period "2008Q1-2012Q4 path on 2026Q2 balances"; DFAST rows "2026Q1-2028Q1 rates on 2026Q2 balances".

### R-20261104-mkt-s25 · skeptic · research/b3_scenarios/presets.py (junior liens in Z.1 mortgages)
- **Objection:** Applying 1.5% (first lien) to all Z.1 1-4 family mortgages is a bias that is stated but not bounded. Z.1 mortgages include home-equity loans and HELOCs (3.2% rate). Table 9 has $22.5B first-lien and $5.5B junior-lien losses, so junior liens are a large share of bank mortgage losses; the share in Z.1 held by GSEs is near zero (GSE pools are first liens), whereas bank and nonbank holders hold most junior liens. So the understatement falls on the private side and the public share of losses (23%) is biased upward, not just the total down. README says only "mortgage losses are understated".
- **Severity:** major
- **Evidence:** Table 9 rows; exposures.json mortgage balances (GSE 8.98T of 13.98T).
- **Proposed resolution:** Report a bound: junior-lien/HELOC balance (Z.1 or NY Fed HELOC) at 3.2% on private holders, and the resulting public share. Say the direction of bias for the share.
- **Status:** resolved (2026-11-04, by Claude, markets track): bias stated: first-lien rate for all mortgages understates junior-lien losses, mostly bank-held, so the public loss share is biased up.

### R-20261104-mkt-s26 · skeptic · research/b3_scenarios (consumer blend, private student loans, FFEL)
- **Objection:** "Private student = Z.1 student minus federal" (FL153166220 - FL313066220) includes FFEL loans still held by banks, Sallie Mae and nonprofits, which are federally guaranteed. They are put in the "private" consumer_other class at 7.3%/10.9%, so private losses are overstated by holdings that bear little credit risk (holding is not bearing risk). The 37% revolving weight also treats all non-revolving, mostly auto and student, as "other consumer", while the DFAST "other consumer" line is bank-owned and the weight is on Z.1 stocks across all holders. Weight 0.3724 and blend 10.949% recompute correctly.
- **Severity:** major
- **Evidence:** presets.py cc_mix(): v["student"] - fed; presets/dfast2026.json cc_mix_musd; recomputed w=0.37238, blend 10.949.
- **Proposed resolution:** Estimate FFEL outstanding (ED/FSA data) and report it as guaranteed, outside the private loss base, or flag the private figure as an upper bound. Add to README.
- **Status:** resolved (2026-11-04, by Claude, markets track): stated: Z.1 private student loans include federally guaranteed FFEL; public share biased down on that count; split needs ED data (blocked).

### R-20261104-mkt-s27 · skeptic · research/b3_scenarios (replay: sum of rates on changing balances)
- **Objection:** Quarter loss = rate/400 is right for each quarter. But summing 20 quarterly rates gives cumulative loss over each quarter's own average balance, not over the start balance. In 2008-12 bank card and mortgage balances moved (charge-offs, run-off, new originations), so 8.7% and 18.9% are not the share of a fixed starting book lost. Applying the sum to 2026Q2 balances also assumes no amortisation, run-off or origination over five years, and applies it to a book that is not the 2008 book (credit mix, LTV, scores). The "consumer_other" series COROCLACBS is the bank "other consumer" line (autos included), weighted with cards by today's Z.1 revolving share, not 2008's. The replay is 20 quarters against 9 for DFAST, so the B4 range mixes horizons without saying so.
- **Severity:** major
- **Evidence:** presets.py:build_replay (path.sum()); results_replay: cumulative 8.7375% / 18.90%; DFAST QUARTERS = 9.
- **Proposed resolution:** State that the figure is a "sum of annualised-rate/4 over average balances", not a share of a start balance. Show a sensitivity (e.g. first 9 quarters, or the 2008Q1-2010Q1 peak window) so the range compares like horizons.
- **Status:** resolved (2026-11-04, by Claude, markets track): stated in B3 and B4: the replay sums 20 quarterly rates over changing balances (an approximation) and differs in horizon from DFAST's 9 quarters.

### R-20261104-mkt-s28 · skeptic · research/b3_scenarios (holder vs risk: GSE/Ginnie, FHA/VA, bank-style rates on public book)
- **Objection:** The public bucket "gse_agency" ($8.98T) includes Ginnie Mae pools (FHA/VA/USDA loans), where credit risk sits with FHA/VA insurance funds and servicers, and GSE pools with CRT and mortgage insurance. Losses are counted as public by holder bucket, which treats holding/guarantee as bearing. FHA/VA loans in bank portfolios are counted as private losses at bank rates although insured. Conversely, bank 2008-12 charge-offs applied to the GSE book (replay) give public mortgage loss about $800B (8.74% of $9.16T), far above the GSEs' own realised credit losses over that period (not checked here; the README only says "likely overstates"). The 42% headline appears in B4 README without that caveat.
- **Severity:** major
- **Evidence:** exposures.json gse_agency 8,977,330; replay public 800,570 = 0.087375 x public mortgage balances.
- **Proposed resolution:** Split Ginnie from Fannie/Freddie if Z.1 allows; add the GSE realised-loss comparison from 10-Ks; carry the overstatement caveat into the B4 README row and label 42% an upper bound.
- **Status:** resolved (2026-11-04, by Claude, markets track): stated: the 42% replay public share is probably an upper bound (bank loss rates on Ginnie/GSE books).

### R-20261104-mkt-s29 · skeptic · research/b3_scenarios/README.md header and sources.md
- **Objection:** README line 3 and the status line say the 2008-12 replay is "still to come" and "not yet built", while the same file reports its results; the "Not done here" section repeats it. sources.md has a stray blank line splitting the table, so the FRED rows render outside it. Stale status text next to published numbers is misleading.
- **Severity:** minor
- **Evidence:** README.md lines 3, 5 and "Not done here" vs the replay section.
- **Proposed resolution:** Update status text; fix the table.
- **Status:** resolved (2026-11-04, by Claude, markets track): B3 status text updated; stray blank line in the sources table removed.

### R-20261104-mkt-s30 · skeptic · research/b4_policy_scenarios/sources.md (FHFA status claim)
- **Objection:** The "in conservatorship" status rests on an undated page. The cached FHFA page shows no update date; its most recent dated item is the "2025 Scorecard" in November 2026, and its text is the same generic statement, so it cannot show status at 2026-11-04. The news-list check covers only a 10-item page (2026-03-31 to 2026-10-27), news releases only (not statements, speeches or Treasury/SPSPA notices), and the first page is mostly HPI releases. It cannot show absence of an exit announcement for the whole year. sources.md says this once; the README table states "No release about an exit was found" and "as looked up, 2026-11-04" with no such caveat. Also the byte count for the news page in sources.md (98472) matches rel.htm, but the file labelled news.htm (81913 bytes) is a different page; the hash for the cached files was not checked.
- **Severity:** major
- **Evidence:** cons.htm text: dates found only 2008; "2025 Scorecard priorities"; rel.htm lists 10 items, Oct 27 to Mar 31 2026, all releases.
- **Proposed resolution:** Use "FHFA page (undated) says ...; first page of news releases (10 items to Oct 27 2026) lists none about exit". Check the Statements list and Treasury/SPSPA before calling the status current. Verify hashes.
- **Status:** resolved (2026-11-04, by Claude, markets track): B4 README now says the FHFA page is undated, only the first 10-item news page was checked, and the status is unconfirmed beyond those two pages.

### R-20261104-mkt-s31 · skeptic · research/b4_policy_scenarios/README.md (P.L. 119-21 wording)
- **Objection:** The quote in sources.md is accurate to GovInfo ("Subject to paragraph (8) and notwithstanding..." is omitted but the ellipsis marks it), and "Approved July 4, 2025" matches. But the README paraphrase "no Federal Direct PLUS loans for graduate and professional students from July 1, 2026" drops the paragraph (8) exception (interim treatment of students already enrolled and receiving loans), so as stated it is stronger than the statute. "a Repayment Assistance Plan" is in the text, but the statement is only that the law refers to it, not that it is implemented (ED unreachable).
- **Severity:** minor
- **Evidence:** pl119-21.htm: "Subject to paragraph (8) and notwithstanding any provision of this part or part B, for any period of instruction beginning on or after July 1, 2026, a graduate or professional student shall not be eligible to receive a Federal Direct PLUS Loan".
- **Proposed resolution:** Add "for new borrowers, subject to a transition exception (para (8))" and read para (8).
- **Status:** resolved (2026-11-04, by Claude, markets track): "Subject to paragraph (8)" exception added (verified in the statute text).

### R-20261104-mkt-s32 · skeptic · research/b4_policy_scenarios/results.json and markets.csv b4_* / b3_* rows
- **Objection:** Register rows match the results files at display precision (595/1,886; 23%/42%; 457/137/255/712). Problems are not numbers but labels: b4_recession_pubshare_lo/hi take public share of losses as a min/max of two presets, a range of ratios not of dollars on one base, and results.json "public_musd" range is not registered. b4 vintage cells say "2026Q2 balances" in the period column, b3 replay rows say "2026Q1-2028Q1"; status is ESTIMATE for the 595 but b3_dfast_rate_* and b3_rev_weight are UNVERIFIED. The "range" of $595B-$1,886B joins a 9-quarter proxy to a 20-quarter proxy, wide enough that no policy conclusion follows.
- **Severity:** minor
- **Evidence:** python comparison of README/results/markets.csv values: all agree to display precision.
- **Proposed resolution:** Fix period cells; add the horizon difference to the b4 note; say the range is two proxies, not a confidence interval.
- **Status:** resolved (2026-11-04, by Claude, markets track): see s24; register regenerated, values unchanged.
