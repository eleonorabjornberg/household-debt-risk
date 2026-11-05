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

### R-20261104-mkt-q25 · quant-reviewer · research/c1b_nowcast/nowcast_c1b.py (holdout gate)
- **Objection:** The prereg (Decisions: "one joint C1 + C1b + C2 holdout run") and the frozen joint runner disagree with the C1b holdout path. `--holdout` calls `nc.run("RT", ..., True)` directly, bypassing C1's own holdout refusal, and writes C1's holdout bridge (`bridge_c1`) to nowcasts_holdout.csv. Run before or apart from research/c2_forecast/holdout_run.py (frozen in research/c2_forecast/FREEZE.json, which knows nothing of C1b), it unseals C1's holdout outside the frozen joint run. Run after it, the "one run" is two runs. research/c1b_nowcast/FREEZE.json does not exist yet, so `check_freeze` has no file list. `check_approval` does not check that the approval commit is a descendant of the C1b freeze commit and an ancestor of HEAD (the C2 pattern has the same gap).
- **Severity:** blocking-before-freeze
- **Evidence:** nowcast_c1b.py:236-263; research/c1_nowcast/nowcast.py:366-367; research/c2_forecast/holdout_run.py:2-7, 141-174.
- **Proposed resolution:** Before freezing, write down the joint procedure in the prereg: one approval commit, both scripts run back to back in one clean commit, and C1b's `--holdout` refuses unless research/c2_forecast/FREEZE.json also verifies. Create FREEZE.json listing nowcast_c1b.py, freddie_mvs.py, both Freddie CSVs, the prereg, and C1's frozen files plus data/c1/z1_cells.csv. In check_approval, add `git merge-base --is-ancestor` checks: freeze commit before the approval commit, and the approval commit before HEAD.
- **Status:** resolved (2026-11-04, by main session, before the freeze): prereg gains a "Joint holdout run" section (C2 runner first, then C1b with the same approval, one commit); `--holdout` now checks both FREEZE.json files, that the tree differs only by C2's fresh result from the same approval, and that the approval commit lies between C1b's freeze commit and HEAD. FREEZE.json lists the files named.

### R-20261104-mkt-q26 · quant-reviewer · research/c1b_nowcast/nowcast_c1b.py (pre-registered outputs)
- **Objection:** Two pre-registered outputs are missing. (1) "Bias: reported as mean error with its HAC standard error": no HAC SE is computed. (2) H2 "supported at k when significant after Holm and |mean e(C1b)| < |mean e(C1)|": there is no h2_supported flag. Only p_holm and c1b_better are reported separately.
- **Severity:** minor (fix before freeze, or it becomes a dated deviation)
- **Evidence:** c1b-prereg.md:51, 58; nowcast_c1b.py:140-155, 185-197.
- **Proposed resolution:** Add the Newey-West lag-1 SE of the mean error per model and k, and an `h2_supported` column, to tests/summary.
- **Status:** resolved (2026-11-04, by main session, before the freeze): `bias_dev.csv` (mean error, Newey–West lag-1 s.e.) and a `supported` column in `tests_dev.csv`; both written into the prereg as [implementation] lines.

### R-20261104-mkt-q27 · quant-reviewer · nowcast_c1b.py verdict()
- **Objection:** The decision-rule edge cases are not in the prereg. (a) A holdout RMSE that is not lower returns "comparable". The prereg does not say this, and "does not improve" is arguable. (b) Exact RMSE ties fall through to "improves on C1", although the rule needs "lower at every k". (c) The prereg's "comparable" (sign differs across k) overlaps its "does not improve". The code gives priority to "does not improve" without saying so.
- **Severity:** minor
- **Evidence:** c1b-prereg.md:54-57; nowcast_c1b.py:158-170.
- **Proposed resolution:** Add [implementation] lines to the prereg fixing (a)-(c) before the freeze. Use `<=` for the tie test.
- **Status:** resolved (2026-11-04, by main session, before the freeze): rule order and tie handling written into the prereg; `verdict()` treats an exact tie as not lower; tests added (`test_verdict_rules`).

### R-20261104-mkt-q28 · quant-reviewer · Freddie publication dates and re-issued reports
- **Objection:** None blocking; recorded so the checks are on file. (1) The strict rule holds: guard(pub_date+1) <= t. No pub_date falls on the 5th-14th (all lags are 17-33 days), so every report month m is first used at the 15th of m+2 under any lag from 16 to 45 days, and the a2 choice does not move timing. (2) Content of the 21 re-issued reports: across 273 overlapping row-months they match contemporaneous plausible reports. For example, the 2020-03 to 2020-06 re-issues carry the pre-restatement levels of the 2020-07 report, not the 2021 restatement. There is no sign of later revisions. (3) Dev result without the 17 re-issue instants: RMSE ratio C1b/C1 0.63 (re-issue instants 0.67), H1 p_holm 0.023 at every k, verdict unchanged. (4) The lag-1 HAC sensitivity under Holm is about 0.043, which is marginal. The p-values are descriptive (n = 22-28 overlapping targets).
- **Severity:** note
- **Evidence:** freddie_mvs_reports.csv, freddie_mvs_rows.csv, nowcasts_dev.csv, tests_dev.csv (reproduced from nowcasts_dev.csv with tests()); pytest 8 passed.
- **Proposed resolution:** State (1)-(3) as descriptive robustness in the C1b README, and report the lag-1 Holm values next to the lag-0 values.
- **Status:** resolved (2026-11-04, by main session): `results_dev.json` `robustness_reissued` reports it (ratio 0.67 on the 17 instants that used a re-issued report, 0.63 on the rest); to be stated in the C1b README.

### R-20261104-mkt-s33 · skeptic · research/b4_policy_scenarios/README.md:10,25 (b4_gse_pubshare_lo/hi, b4_gse_*_pubshare)
- **Objection:** The GSE section calls the result "the public share of all household-credit losses", and the 7%–42% range is presented without qualification. In both B3 presets federal student loans ($1,605B, public) carry no loss rate, so they add zero loss. The range is a share of mortgage + other-consumer losses only. B3's README says this (its variant with student loans at 7.3% moves the DFAST public share from 23% to 36%); B4's README does not.
- **Severity:** major
- **Evidence:** presets/dfast2026.json and replay_2008_2012.json classes = {mortgage, consumer_other} only; exposures.json student_federal/federal_direct balance 1605134; research/b3_scenarios/README.md:22,26-27.
- **Proposed resolution:** Say "of mortgage and other consumer credit losses (federal student loans excluded, as in B3's main presets)" in the scenario table, the Result line and the register claim text. Optionally add the B3 student-loan variant as a sensitivity row.
- **Status:** resolved (2026-11-04, by main session): README and register text now say mortgage and other consumer-credit losses, federal student loans excluded (also on the recession row). B3's student-loan variant not added (not part of the card).

### R-20261104-mkt-s34 · skeptic · research/b4_policy_scenarios/README.md:18,42 (0% point; "Release is not the same as loss-bearing")
- **Objection:** The README reads as if CRT and capital would arrive only with release ("A released GSE would hold capital and buy CRT"). In fact, Fannie and Freddie already transfer part of their credit losses today through CRT, and through private MI on loans above 80% LTV (A2). So "0% = the implicit guarantee holds" is not the status quo: part of the 0–100% axis has already happened, and the 0% public figures overstate today's public loss-bearing. The general "No transfer" bullet does not link this to the GSE axis.
- **Severity:** major
- **Evidence:** README.md:18 "0% (the implicit guarantee holds)"; README.md:42; research/a2_net_exposure (net-of-CRT and MI exposure below gross; R-20261104-ana-1..16).
- **Proposed resolution:** State that the share turning private is measured gross of existing CRT and MI. Today's arrangement already sits at some share above 0%. Point to A2 for the size.
- **Status:** resolved (2026-11-04, by main session): 0% relabelled (losses stay on the GSEs' and Treasury's side); caveat added that shares are gross of CRT and mortgage insurance, so today's arrangement sits above 0% net, pointing to A2.

### R-20261104-mkt-s35 · skeptic · research/b4_policy_scenarios/README.md:20, METHOD.md section 2 ("Ginnie ... explicit federal guarantee", "stay public in every case")
- **Objection:** The Ginnie guarantee is explicit to MBS investors. It does not make every credit loss on the underlying loans public. VA and USDA guaranties are partial, and Ginnie issuers and servicers bear losses beyond them. That is the same holder-vs-risk point as R-20261104-8, which was fixed in A1's README but is repeated here. FmHA pools are $0 at 2026Q2, so naming them has no effect.
- **Severity:** minor
- **Evidence:** Z1.csv 2026-06-30: FL413065110 = 2,798,659; FL413065133 = 0. R-20261104-8 resolution text.
- **Proposed resolution:** "Ginnie Mae pools (federal guarantee to investors; FHA insurance full, VA/USDA partial, with issuers bearing the remainder)". Note that the public share at each point is therefore an upper bound on that count.
- **Status:** resolved (2026-11-04, by main session): Ginnie wording qualified (VA and USDA guaranties partial; holder-based simplification, A1's caveat).

### R-20261104-mkt-s36 · skeptic · claims/tracks/markets.csv rows b4_gse_bal_* (29-34)
- **Objection:** The balance rows carry vintage "z1:2026-09-11 fred:2026-11-04", but they use only Z.1. They are also left UNVERIFIED although they reproduce independently. I recomputed all of them from the raw Z1.csv: a = 13,976,938/14,983,477 = 0.932823; released 6,728,906×a = 6,276,881; Ginnie 2,610,655; FHLB+other 89,795 (FHLB 83,106 + FCS 7,915 + 5,240 unallocated, ×a); total 8,977,330 = B3 bucket. The series labels match the Z.1 descriptions: FL413065143 is Fannie pools, FL413065133 is FmHA pools, and the post-2010 consolidated trusts sit in FL403065110/120. No double count with the pools sector.
- **Severity:** minor
- **Evidence:** grep of Z1.csv descriptions and 2026-06-30 values (scratchpad); split identical to A1 decompose.py PUBLIC_MORT.
- **Proposed resolution:** Drop "fred:" from the vintage of rows 29-34 and record this independent recompute in their validation/notes.
- **Status:** resolved (2026-11-04, by main session): b4_gse_bal_* vintage now z1:2026-09-11 only; note records the skeptic's independent recompute (status stays UNVERIFIED: no validation check id).

### R-20261104-mkt-s37 · skeptic · research/b4_policy_scenarios/README.md:18 ("0% (the implicit guarantee holds)")
- **Objection:** Under conservatorship the backstop is the explicit Treasury PSPA commitment, not an implicit guarantee. Losses also hit the GSEs' own retained capital before any Treasury draw. Counting all 0%-point losses as "public" therefore means "on the GSEs' or Treasury's books", not taxpayer outlay. Under the DFAST proxy the released book loses $94B (1.5% × $6,277B), which may sit within the GSEs' own capital (not sourced here).
- **Severity:** note
- **Evidence:** presets/dfast2026.json mortgage pd 0.015, lgd 1.0; results.json dfast 0% minus 100% public = 137.4 - 43.3 = 94.2 $B.
- **Proposed resolution:** Reword to "0% (losses stay with the GSEs and Treasury, as in conservatorship)" and define "public" this way in the caveats. Option (b) stays unchosen.
- **Status:** resolved (2026-11-04, by main session): Caveat 'What "public" means here' added: GSE capital first, PSPA behind; public is not taxpayer outlay.

### R-20261105-mkt-s38 · skeptic · research/b2_crt_pricing/README.md:75 (explanation of the rising last column; b2_fre_2022_ce_rate, b2_fre_2023_ce_rate)
- **Objection:** The README gives one reason for the rise in credit-enhancement expense per dollar of cover (the move from debt notes to trust and insurance structures). Freddie names two others. For 2022 it cites "higher spreads on transactions executed during 2022", a price effect. For 2023 it cites "higher losses on STACR Trust note repurchases", a one-off buyback cost, not a protection premium. So the 4.5% for 2023 is not a running cost of cover. Also, in 2017–2020 the STACR coverage in the denominator includes debt-note coverage whose cost (interest) is left out of this numerator. The column is therefore not one consistent measure across the seven years, though the README calls it "the one measure that runs through all seven years".
- **Severity:** major
- **Evidence:** data/a2/freddie/10k_022223.txt:1216-1219 ("higher spreads on transactions executed during 2022"); 10k_021424.txt:1191-1193 ("higher losses on STACR Trust note repurchases"); 10k_021320.txt:3537ff and A2 freddie_10k.py: crt_maxcov = STACR (debt + trust) + insurance/reinsurance (2019: 25,112 + 10,157 = 35,269).
- **Proposed resolution:** Quote Freddie's stated drivers for 2021–2023 next to the structural-shift sentence. Flag 2023 as including repurchase losses that are not premium. Reword "the one measure that runs through all seven years" to say that before 2021 its numerator leaves out the debt-note cost while its denominator includes that coverage.
- **Status:** resolved (2026-11-05, by main session): README now quotes Freddie's reasons (2022 spreads; 2023 STACR Trust note repurchase losses, flagged one-off), says the expense covers all freestanding enhancements incl. lender risk sharing, and drops 'the one measure that runs through all seven years'.

### R-20261105-mkt-s39 · skeptic · research/b2_crt_pricing/README.md:80 ("Against 2013–2016"; b2_fre_1720_rate_lo/hi)
- **Objection:** The consistency check sets Freddie's gross total (credit-enhancement expense plus gross interest on STACR debt, which includes LIBOR) against FHFA's credit cost per dollar of tranche. FHFA's cost sits on the guarantee-fee footing (README:21) and is a spread cost, not a gross coupon. Net of Freddie's own reinvestment estimate, the 2017–2020 figures are 3.8–4.4%, not 4.6–5.2%. Both sets fall inside 3.3–6.9%, so the conclusion survives. But the stated numbers use the less comparable basis, and a 2x-wide range is a weak check.
- **Severity:** major
- **Evidence:** `uv run -q --project pipeline python -I -` on freddie_crt_cost.csv: net_cost_musd / avg_crt_maxcov_musd = 0.0401, 0.0383, 0.0416, 0.0443 (2017–2020).
- **Proposed resolution:** Lead the comparison with the net column (3.8–4.4%), keep the gross figure as a second number, and add register rows for the net rates. Say that a value inside a 3.3–6.9% band is only weak support.
- **Status:** resolved (2026-11-05, by main session): Comparison now leads with the net-of-reinvestment rate (3.8–4.4% in 2017–2020, new column and rows), gross in brackets, and calls it weak support (the band's top is about twice its bottom).

### R-20261105-mkt-s40 · skeptic · research/b2_crt_pricing/README.md:59-61,75 (Freddie scope; b2_fre_2021..2023_ce, _ce_rate)
- **Objection:** The numerator is broader than the denominator. Credit-enhancement expense covers every freestanding enhancement, including lender risk sharing (cover 5,657 at end-2019, not in crt_maxcov). From 2022 it also includes multifamily (MCIP etc.), while the denominator stays single-family STACR + insurance only. The table also switches scope between adjacent rows. It shows 2021 single-family at 1,470, but the consolidated 2021 figure is 1,518, so part of the 2021→2022 rise is the scope change. The multifamily share was 2.1% in 2020 and 3.2% in 2021, which is "small" but growing. The denominator also changes definition: from FY2022 the row is "ACIS", with about 531 of 2021 cover moved into "Other" (48,850 first published vs 48,319 restated).
- **Severity:** minor
- **Evidence:** 10k_021022.txt:11219 (2021: SF 1,470, MF 48, total 1,518; 2020: 1,036 / 22 / 1,058); 10k_021320.txt:3410, 9917; 10k_022223.txt:3125-3150 vs 10k_021022.txt:3592-3593.
- **Proposed resolution:** Show the consolidated 2021 figure (1,518; 3.4% of cover) next to the 2022–2023 figures, and give the multifamily shares for 2019–2021. State that lender risk-sharing and multifamily costs sit in the numerator but not in the denominator, and note the relabelling of the denominator row in FY2022.
- **Status:** resolved (2026-11-05, by main session): Consolidated 2021 ($1,518 million, 3.4% of cover) and the $48 million multifamily part stated; FY2022 relabelling of $531 million of 2021 cover disclosed. 2022–23 split not printed in the statements read (stated).

### R-20261105-mkt-s41 · skeptic · research/b2_crt_pricing/README.md:57,79-80 (b2_fre_2019_ce_rate, b2_fre_2019_gross_rate, b2_fre_1720_rate_hi)
- **Objection:** The latest vintage changes displayed numbers. Freddie restated 2019 credit-enhancement expense from 693 to 734 (FY2020 and FY2021 10-Ks). On the latest figures, the 2019 credit-enhancement rate becomes 2.2% (shown as 2.1%), the 2019 total becomes 5.4% (shown as 5.2%), and the top of the "4.6%–5.2%" range becomes 5.4%. Keeping first publication is a valid choice, but the README does not say that it moves the headline range.
- **Severity:** minor
- **Evidence:** freddie_crt_cost.csv latest_ce_expense 2019 = 734; (734+1060)/33507 = 0.0535; 734/33507 = 0.0219.
- **Proposed resolution:** Add "(latest filing: 2.2% and 5.4%)" to the restatement bullet, or record the latest-vintage values in the notes of the three register rows.
- **Status:** resolved (2026-11-05, by main session): Restated 2019 rates (5.4% total, 2.2% expense only) stated in the README with rows.

### R-20261105-mkt-s42 · skeptic · research/b2_crt_pricing/README.md:71-73,77 (b2_fnm_2021..2023_cirt, _rate)
- **Objection:** Fannie's 10-Ks footnote that 2021–2023 CIRT cash "includes cancellation fees paid on certain CIRT transactions", which are one-off exit costs and not premium. The README does not mention them. Separately, risk in force is printed as "approximately $X billion". Rounding of ±0.5bn at each year end gives ranges of 2.8–2.9% (2021), 3.3–3.4% (2022) and 3.2–3.3% (2023).
- **Severity:** minor
- **Evidence:** fnma_10k_fy2021/2022/2023.htm, footnote under "Credit Risk Transfer Transactions ... Cash paid or transferred for"; recomputation 1315/40500 = 0.0325, 1315/41500 = 0.0317 (2023 low end), 1207/36000 = 0.0335.
- **Proposed resolution:** Add a bullet: "CIRT cash for 2021–2023 includes cancellation fees (amount not printed); risk in force is rounded to $1B, so the rate is ±0.05 pp."
- **Status:** resolved (2026-11-05, by main session): Bullet added: CIRT cancellation fees (quoted footnote) and the rounding bound (< 0.05 pp, computed).

### R-20261105-mkt-s43 · skeptic · claims/register.csv b2_per_tranche_lo, b2_per_tranche_hi
- **Objection:** README:80 republishes the FHFA "3.3–6.9%" range, but the register rows for those figures list only README.md:34.
- **Severity:** note
- **Evidence:** `grep -n "b2_per_tranche_" claims/register.csv`: locations = research/b2_crt_pricing/README.md:34 only.
- **Proposed resolution:** Add README.md:80 to both rows' locations (through make_readme_and_rows.py or the main register's generator).
- **Status:** open (routed to the coordinator 2026-11-05): Not editable by the track (claims/register.csv is the coordinator's); sent to the coordinator to add README.md:80 to b2_per_tranche_lo/hi.
