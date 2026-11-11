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
- **Status:** resolved (2026-11-05, by the coordinator, on the markets track's routing): README.md:83 (the line moved from :80 after the s38–s42 edits) added to b2_per_tranche_lo/hi in claims/register.csv (merge 17dfd01).

### R-20261105-mkt-q29 · quant-reviewer · research/c2_forecast/holdout_run.py (approval order after c1b-dev-1)
- **Objection:** The deviation says the rerun needs a NEW approval commit after the fix commit, but only C1b enforces that (`nowcast_c1b.check_order`). `holdout_run.py` checks only that a PLAN.md row at `--approval` contains "unseal", that FREEZE hashes match the tree, and that the tree is clean. After the fix commit, `--approval 77460b4` still passes every C2/C1 gate. It would write C2's and C1's holdout results; C1b's `check_order` would then refuse the same approval, which breaks the "one joint run, one approval" procedure. This is the C2 gap noted in q25, now live.
- **Severity:** major
- **Evidence:** holdout_run.py:55-70, 151-160 (no ancestry check); nowcast_c1b.py:259-267; c1b-prereg.md deviation, last bullet.
- **Proposed resolution:** Before the re-hash, add to holdout_run.py the same check as C1b: the last commit touching research/c2_forecast/FREEZE.json must be a strict ancestor of `--approval`, and `--approval` an ancestor of HEAD. Re-hash, and add a test that fails when the approval predates the freeze. Alternatively, state in the deviation that the order is enforced only on the C1b side.
- **Status:** resolved (2026-11-05, markets track, before the fix commit): `holdout_run.check_order()` added and called before any data is read: the approval must be strictly after the last commit touching C2's FREEZE.json and an ancestor of HEAD. Test `test_refuses_approval_from_before_the_last_freeze`. Recorded in the deviation; FREEZE re-hashed.

### R-20261105-mkt-q30 · quant-reviewer · c1b-dev-1 deviation text (c1b-prereg.md, scoring-protocol.md, EVALUATION.md)
- **Objection:** "Frozen files changed" lists nowcast.py and holdout_run.py only. C1b's FREEZE also re-hashes docs/decisions/c1b-prereg.md, and research/c2_forecast/FREEZE.json still pins `scoring-protocol.md @ 192d60c`, a commit before this appended deviation. The text also does not say that 2026Q3 lies outside the pre-registered holdout window (2023Q3–2026Q2). `hold = q > DEV_END` has no upper bound, so the rows are excluded only because they have no actual. Separately, the C1b holdout table (nowcast_c1b.run copies `actual` but not `target`) will have these rows without the "no target" label.
- **Severity:** minor
- **Evidence:** git diff research/c1b_nowcast/FREEZE.json; research/c2_forecast/FREEZE.json:8; holdout_run.py:123; nowcast_c1b.py:100-118.
- **Proposed resolution:** Add c1b-prereg.md to the list and note the 192d60c pin. Add one sentence that 2026Q3 is outside the holdout window and could never be scored. Carry `target` into C1b's rows (or say in the deviation that it is not carried).
- **Status:** resolved (2026-11-05, markets track): the deviation text now lists c1b-prereg.md, notes the `192d60c` pin, says 2026Q3 is outside the holdout window, and says C1b's table does not carry the `target` label (nowcast_c1b.py left unchanged).

### R-20261105-mkt-q31 · quant-reviewer · research/c3_accuracy/README.md:11 (C2 headline bullet)
- **Objection:** "the seasonal naive at h = 1, the weakest benchmark" is false on the report's own numbers. At h = 1 in development, no-change (1.00) and drift (0.96) are weaker than seasonal naive (0.92). In the holdout, drift (1.53) is weaker than seasonal naive (1.33). The bullet also leaves out the protocol's own outcomes. On H1, every candidate's holdout RMSE is above no-change at every horizon and in both designs (1.09 to 2.15), although development favoured them strongly (CW Holm p 1e-8 at h = 1). Under the protocol's Hypotheses that is a "Null": the sign flips between samples. H3 (coverage) is not mentioned at all. Neither is the real-time check, where Z-DIR/no-change is 1.03 to 1.33 against latest-vintage targets (section 5).
- **Severity:** major
- **Evidence:** README.md:11, 22-27, 50-55, 362-370; scoring-protocol.md:17-21, 162-163.
- **Proposed resolution:** In make_report.py, drop "the weakest benchmark". State the H1/H2/H3 outcome in the protocol's Support/Null/Against wording. Add one clause saying the holdout RMSE exceeds no-change throughout, and one on the real-time check. Regenerate; do not hand-edit.
- **Status:** addressed (2026-11-05, markets track, make_report.py): "weakest benchmark" removed. The headline now states, with an assert, that every candidate's holdout RMSE is above no-change's at every h and in both designs.

### R-20261105-mkt-q32 · quant-reviewer · research/c3_accuracy/README.md:44 ("12 targets per horizon")
- **Objection:** The pre-registration (holdout option (b)) says "Origins 2023Q2 onward give 12, 9 and 5 holdout forecasts at h = 1, 4, 8". The one run scored 12 at every h, with origins back to 2022Q3 (h = 4) and 2021Q3 (h = 8): the holdout was defined by target quarter, not by origin. This may be a defensible reading, but it is not declared anywhere in the report's deviation list. At h = 8 the 12 errors overlap by up to 7 quarters, so they amount to about 1.5 non-overlapping forecasts. Ratios such as 1.90 and 5.34 rest on that.
- **Severity:** major
- **Evidence:** scoring-protocol.md:93; holdout_results.json c2.scores_holdout first_T = 2023Q2 / 2022Q3 / 2021Q3 at h = 1/4/8, n = 12 each; README.md:44-55, 398-410.
- **Proposed resolution:** Route a dated deviation to the coordinator: the holdout is target-based (12/12/12), not origin-based (12/9/5). List it in section 7, and note the overlap at h = 4 and 8 beside the holdout tables. Nothing is rerun.
- **Status:** addressed in the report; protocol side open: a holdout_count_note() paragraph states the run counted by target quarter (12/12/12, origins from 2023Q2/2022Q3/2021Q3) against the protocol's origin-based 12/9/5, flags the overlap, and says it was not declared before the run. A dated item is in section 7. Sent to the coordinator as a proposed card (no rerun; the origin subset cannot be scored without per-forecast errors).

### R-20261105-mkt-q33 · quant-reviewer · research/c3_accuracy/README.md:132-161 (interval coverage)
- **Objection:** (a) Holdout Kupiec p-values (0.021, 0.267) are printed although decided option (b) says holdout results carry "no p-values" and "The holdout only reports" coverage. 0.021 reads as a rejection; it is a 12-of-12 over-coverage that every model shares, no-change included. (b) The Christoffersen p at h = 1, which the protocol requires, is in coverage_dev.csv but not shown. (c) The Clopper–Pearson brackets at h = 4 and 8 assume independent hits. With overlapping errors they are too narrow, yet they sit beside "descriptive" with no caveat. (d) H3's fixed wording ("Intervals are reliable") is never applied. At development h = 4 and 8 the 95% coverage is 0.83 and 0.75, with CP upper bounds of 0.90 and 0.84.
- **Severity:** major
- **Evidence:** README.md:134-161; coverage_dev.csv christoffersen_p column; scoring-protocol.md:119, 141, 162.
- **Proposed resolution:** Show Kupiec only for development. Add the development Christoffersen column. Mark the h > 1 CP brackets "iid, indicative only". State the H3 verdict per horizon and level, and note that 100% holdout coverage is common to all models.
- **Status:** addressed: holdout Kupiec p removed (holdout descriptive, no p-values); Christoffersen p added at h = 1 in development; text says h > 1 Clopper-Pearson brackets assume independence and are too narrow; an H3 paragraph applies the protocol wording, stating the p < 0.05 reading as a reading, not a rule.

### R-20261105-mkt-q34 · quant-reviewer · research/c3_accuracy/README.md:13 (regime counts in the headline)
- **Objection:** The body says the protocol does not fix target versus origin and shows both, but the headline gives only the target-quarter count (1/3/4 of ten). By origin quarter the count is 1/0/0 (recomputed from forecasts_dev.csv). Choosing the split that gives the larger count, after seeing the errors, is the selection the protocol's "fixed now" clause guards against. There is also no base rate (about 16% of development forecasts have a target in a window, so about 1.6 of 10 are expected by chance). And the 4 at h = 8 (2008Q3, 2008Q4, 2009Q2, 2009Q3) are one overlapping episode.
- **Severity:** major
- **Evidence:** README.md:13, 322; make_report.py fail_counts(); my recomputation: origin-split counts 1, 0, 0; window base rate 0.158/0.162/0.167.
- **Proposed resolution:** Give both counts in the headline with the base rate, or drop the count. Say that the h = 8 hits are one episode.
- **Status:** addressed: the headline gives counts by target and by origin quarter, each with its chance base rate (registered), lists the in-window quarters, and says overlapping h = 4/8 errors are one episode.

### R-20261105-mkt-q35 · quant-reviewer · research/c3_accuracy/README.md:332-343 ("rest" comparator)
- **Objection:** "Rest" is not clean. Under the target split it keeps forecasts whose origin lies in a window. Under the origin split it keeps forecasts whose target lies in a window (for example h = 8 origins in 2005Q4–2007Q3, which carry the largest GFC misses). That is 2, 8 and 12 of the rest forecasts at h = 1/4/8. Excluding them moves Z-DIR rest/no-change at h = 8 from 0.93 to 0.96. The cells are also ratios to no-change, whose RMSE differs sixfold between windows (0.48 to 6.65 pp at h = 8 vs h = 1). A low ratio in the GFC rows (0.39) means that no-change did badly, not that the model did well. The text does not say so.
- **Severity:** minor
- **Evidence:** recomputed from research/c2_forecast/forecasts_dev.csv (latest-expanding); README.md:326-343.
- **Proposed resolution:** Define "rest" as neither origin nor target in a window (n = 110/101/93). Alternatively, show it as a sensitivity. Add the model RMSE in pp, or one sentence on reading the ratios.
- **Status:** addressed: "rest" is defined (split quarter in neither window) with the warning that the other quarter can fall in a window; ratios are explained.

### R-20261105-mkt-q36 · quant-reviewer · research/c3_accuracy/README.md:329-354, 391-393, 362-370 (small-n cells)
- **Objection:** Several cells come with no warning and no uncertainty measure: 2020 regime cells with n = 4 (origin split h = 8: 2.55, from 4 overlapping forecasts); C1 2020 with k = 3, n = 3 (C1b 0.16); and ZC1-DIR in development at h = 8 with n = 4 (Z-DIR 3.49, ZC1-DIR 0.96). The real-time check (n = 28/25/21, overlapping) and the holdout ratios at n = 12 are also printed without caveat. These invite readings that the data cannot carry.
- **Severity:** major
- **Evidence:** README.md lines as cited; scores_dev.csv Z+C1 common origins h = 8, n = 4.
- **Proposed resolution:** In make_report.py, flag every cell with n < 10 (or with fewer than about 10 non-overlapping forecasts, roughly n/h) with a marker and a footnote saying it is descriptive only. Add one sentence on overlap at h = 4 and 8.
- **Status:** addressed: cells with n < 10 are marked ‡ (regime tables, the indicator table, the registry), with a note that they are anecdotes.

### R-20261105-mkt-q37 · quant-reviewer · research/c3_accuracy/README.md:20-37 (specification registry)
- **Objection:** (a) The protocol requires "ID, commit, date and development-sample scores", and there is no date column. (b) The rows mix samples in the same columns with no n shown. `bridge_reg` RT scores 0.43/0.44/0.54 on 16/16/10 targets, against `bridge` 0.73 on 28/28/22; the like-for-like `bridge_on_reg_targets` (0.72/0.73/0.86) is omitted. `ZC1-DIR` scores 0.80/1.40/0.96 on 18/12/4 origins, against Z-DIR on 133/130/126; the same-origin Z-DIR figure (1.04/1.24/3.49) is only in section 6. Readers will compare across rows.
- **Severity:** minor
- **Evidence:** research/c1_nowcast/scores_dev.csv RT rows (n, bridge_on_reg_targets); research/c2_forecast/scores_dev.csv "Z+C1 common origins".
- **Proposed resolution:** Add date and n columns. Add `bridge_on_reg_targets` and the same-origin Z-DIR row, or say beside each row that the sample differs.
- **Status:** addressed: date column (commit date from git) and n beside each development score; text warns bridge_reg and ZC1-DIR rest on fewer forecasts.

### R-20261105-mkt-q38 · quant-reviewer · research/c3_accuracy/README.md:163-197 (C1/C1b verdicts and bias)
- **Objection:** EVALUATION.md:53 says C1's wording follows C2's rule (a), but the report gives C1 no verdict. It shows the development tests and the holdout ratios in separate tables. Applied mechanically, the rule gives "does not beat" no-change for `bridge_reg`: 0.43 in development, 1.08/1.04 at k = 1/3 and 1.01 pooled in the holdout. The bridge is at most "comparable", with Holm p 0.107 to 0.514. A reader sees 0.43 in the registry and no reversal statement. C1b's pre-registration also says bias is "reported as mean error with its HAC standard error". H2 is about bias, yet no mean error appears. The development values are in c1b holdout_results.json, and the holdout values can be computed from the committed nowcasts_holdout.csv (my values: C1 −0.037/−0.089/−0.104, C1b −0.022/−0.057/−0.051 pp at k = 1/2/3).
- **Severity:** major
- **Evidence:** EVALUATION.md:53; c1b-prereg.md:51-59; holdout_results.json c1.scores; c1b holdout_results.json development.mean_error_hac1.
- **Proposed resolution:** Add a C1 verdict table under rule (a), generated from the committed files. Add C1/C1b mean errors (development with HAC SE; holdout descriptive) from the committed CSVs. Nothing is rerun.
- **Status:** addressed: C1 verdicts under rule (a) are computed from the committed tests and holdout scores (c1_verdicts(), mirroring holdout_run.py's wording logic), with a table and headline. Result: bridge_reg vs no_change at k = 2 "beats"; the report labels it as computed by C3 and small-n. C1b bias table added (C1b's own mean_hac1 on the committed tables; development reproduces bias_dev.csv by assert).

### R-20261105-mkt-q39 · quant-reviewer · research/c3_accuracy/README.md:85, 405, 398-410 (Holm family and deviations list)
- **Objection:** (a) "The family grew from 36 to 42" cannot be right. The 42 tests are 14 per benchmark (Z-DIR and Z-DAMP × 3 h × 2 designs, plus ZC1-DIR at h = 1 and 4), so seasonal naive added 14 to 28, not 6 to 36. tests_dev.csv has had 42 rows with 14 per benchmark since 0bc647b. The text is copied from SPECS.md:67, 82. (b) ZC1-DIR at h = 8 has no test and no verdict, because forecast.tests() skips pairs with n < 8, a threshold not in SPECS. The report shows its holdout ratio (5.34) without saying it has no verdict. (c) Section 7 omits C1's declared differences from C2 (fixed AR(1), no placebo test 5 for C1, pseudo-real-time samples trained on revised targets with no embargo).
- **Severity:** minor
- **Evidence:** git show 0bc647b:research/c2_forecast/tests_dev.csv (14/14/14); forecast.py:454-455; EVALUATION.md:85-88.
- **Proposed resolution:** Correct the count (28 + 14 = 42) here and route the SPECS.md correction to the track. State that ZC1-DIR h = 8 is untested (n = 4 < 8) and has no verdict. Add C1's q15 differences to section 7.
- **Status:** addressed: section 7 gives the 28 + 14 = 42 count and says SPECS.md's "36 to 42" is a miscount (SPECS.md not edited: accepted text); the ZC1-DIR h = 8 n < 8 skip is documented; C1's declared differences from C2 are added.

### R-20261105-mkt-s44 · skeptic · research/c3_accuracy/README.md:395-422 (section 5, "first release" in C2 vs C1)
- **Objection:** "First release" is defined differently in the two tables of the revision section, and the text does not say so. C1 uses the same-vintage change: share(q) minus share(T), both taken from q's first release (EVALUATION.md:10, item 9a). C2's real-time check uses share(q) from q's first release minus share(T) from the *origin* release (forecast.py:358). So C2's "first-release target" also contains the revision to T between the two releases, which no forecast can see. On the same 28 target quarters, the two targets differ by an RMS of 0.24 pp (maximum 1.09 pp), and no-change RMSE is 0.44 pp (C2) against 0.38 pp (C1). The "latest" targets are identical in both tables. Displayed numbers move under C1's definition: no-change RMSE 0.44/1.17/2.01 becomes 0.38/1.14/1.97; drift goes from 0.99 to 0.93 at h = 1 and from 0.63 to 0.60 at h = 8; Z-DIR goes from 0.86 to 0.85 and from 0.99 to 0.96. The direction of the first-versus-latest gap is unchanged.
- **Severity:** major
- **Evidence:** forecast.py:358 `"actual_first": first_level - s[T]` (s = origin vintage) vs nowcast.py:209 `share_first - z.shares(frel)[T]`. Read-only recomputation from forecasts_realtime_dev.csv, first_release.csv and z1_share_vintages.csv: same q set (28 = 28), `actual_latest` equal, actual_first(C2) − actual_first(C1) RMS 0.236 pp.
- **Proposed resolution:** In make_report.py, label C2's row "first release of the target, origin level as published at the origin" and C1's row "first release, same-vintage change". Add one sentence saying the C2 gap mixes revisions to T+h with revisions to T. Optionally add a development-only C2 row on C1's definition, computed from the committed files. Nothing is rerun.
- **Status:** addressed (make_report.py): section 5 explains the two definitions and gives the RMS gap on the same targets (computed, registered).

### R-20261105-mkt-s45 · skeptic · research/c3_accuracy/README.md:11, 47, 53-58 (C2 holdout targets are barely revised; development targets are mature)
- **Objection:** "Latest vintage" is the 2026-09-11 Z.1 for both samples, but the report never gives the date or says what it implies. Development targets (≤ 2023Q2) have had at least 13 later releases. Holdout targets have had 0 to 11 (2026Q2 is its first release). For one-quarter changes, the latest-minus-first revision has an RMS of 0.25 pp over the 2016Q3–2023Q2 targets and 0.07 pp over 2023Q3–2026Q2. So the development-to-holdout comparison behind rule (a), and the headline reading that development favoured the candidates but the holdout reversed it, sets mature targets against near-first-release ones. Section 5 shows that target vintage alone moves Z-DIR/no-change from 0.86 to 1.08 at h = 1. This is a confound the report should name, not evidence about which way it acts. It interacts with c3-rule, because whichever rule is chosen uses this dev-versus-holdout loss comparison.
- **Severity:** major
- **Evidence:** forecast.py:35 `LATEST = "2026-09-11"`; first_release.csv (2026Q2 first released 2026-09-11). Read-only computation from z1_share_vintages.csv, revisions only, no forecasts scored: later releases per holdout quarter run from 11 (2023Q3) down to 0 (2026Q2); RMS revision is 0.253 pp in development (n = 28) and 0.072 pp in the holdout (n = 12, mostly 2025Q1 at −0.24 pp).
- **Proposed resolution:** In section 2, state the vintage date and add a sentence that holdout targets are 0–11 releases old, against at least 13 for development. Print the two revision RMS values. Note in section 5 that the C2 holdout sits closer to the first-release regime than development does. Do not rescore anything.
- **Status:** addressed: a headline bullet gives the later-release counts (computed from first_release.csv and z1_calendar.csv) and says development-versus-holdout comparisons mix mature and barely revised targets.

### R-20261105-mkt-s46 · skeptic · research/c3_accuracy/README.md:225-236 (C1b bias table, pooled rows)
- **Objection:** The pooled rows count each target quarter up to three times (k = 1, 2, 3 share the outcome; no-change's error is identical across k), and `mean_hac1` on the k-concatenated rows treats the copies as nearly independent. The pre-registration asks for bias "per k" (c1b-prereg.md:52), so the pooled rows are an addition, and their standard errors are too small. With per-quarter means (n = 28 / 12), the SEs are: development C1 −0.23 (0.04), not (0.03); no-change −0.15 (0.08), not (0.05); holdout C1 −0.07 (0.04), not (0.03), which is about 1.7 SE rather than 2.5. The same triple-counting applies to the pooled n = 35 / 78 rows in sections 2 and 5, which are RMSEs, so only their n is overstated.
- **Severity:** minor
- **Evidence:** make_report.py:577 (pools by concatenating k groups); read-only recomputation from c1b nowcasts_dev.csv and nowcasts_holdout.csv. Concatenated: holdout C1 −0.076 (0.027), no-change −0.001 (0.034). By quarter: −0.073 (0.044), −0.006 (0.054).
- **Proposed resolution:** Label the pooled rows "not pre-registered; instants of one quarter share the outcome, so the s.e. is understated", or show the per-quarter-mean s.e. Say beside the pooled n that it counts instants, not targets (12 and 28 quarters).
- **Status:** addressed: the bias table says the pooled rows are not pre-registered and double-count targets, so their s.e. is understated; the C1 holdout table notes the same for its pooled row.

### R-20261105-mkt-s47 · skeptic · research/c3_accuracy/README.md:19, 35-36, 384-393 (P2a/P2b targets are latest vintage)
- **Objection:** The registry heading says the C1 development scores are "real-time sample RT, first-release targets", but the P2a and P2b rows are scored against latest-vintage targets, on different target spans (P2a 2010Q2–2023Q2, P2b 2015Q1–2023Q2). Their rows say "not real time" but not that the target changes. Likewise, the nowcast regime table puts RT rows (first release) and P2a rows (latest vintage) under one header, with no note that the target definition differs.
- **Severity:** minor
- **Evidence:** c1_nowcast/nowcasts_dev.csv: for P2a and P2b, `actual == actual_latest` in 100% of rows and `actual == actual_first` in 0%; for RT, the reverse. nowcast.py:214.
- **Proposed resolution:** In make_report.py, add "latest-vintage targets, 2010Q2– / 2015Q1–2023Q2" to the P2a and P2b registry rows and to the P2a regime rows.
- **Status:** addressed: the registry text says the P2a and P2b rows use latest-vintage targets.

### R-20261105-mkt-s48 · skeptic · research/c3_accuracy/README.md:13 (C1b headline "with no test")
- **Objection:** The headline calls C1b's verdict "a comparison of RMSEs on 12 target quarters, with no test". Under the pre-registered rule (c1b-prereg.md:55-60), "improves on C1" also needs lower development RMSE at every k and an H1 test significant after Holm. The report's own table shows those (Holm p 0.006–0.007). Only the holdout leg has no test. The holdout leg is also 35 instants over 12 quarters (k = 3 has 11), not 12 forecasts.
- **Severity:** minor
- **Evidence:** c1b-prereg.md:55-60; README.md:197-201; c1b holdout_results.json n_scored {1: 12, 2: 12, 3: 11}.
- **Proposed resolution:** Reword to: "development: lower RMSE at every k, H1 significant after Holm; holdout: pooled RMSE lower (35 instants over 12 quarters, descriptive, no test)."
- **Status:** addressed: the C1b bullet says the verdict rests on development Holm tests plus the holdout RMSE comparison over 35 instants in 12 quarters.


### R-20261105-mkt-e1 · editor · research/c3_accuracy/README.md (lines 11, 88, 206)
- **Objection:** Rule (a) presented as settled while c3-rule is open.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): RULE_NOTE added to the banner, the C2 verdict section and the C1 verdict section; the verdicts are labelled provisional and left as computed.

### R-20261105-mkt-e2 · editor · research/c3_accuracy/README.md (lines 11)
- **Objection:** The headline is one-sided: density scores (CRPS) favour the candidates in the holdout.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The headline says the verdicts are on RMSE and adds a computed CRPS statement (asserted).

### R-20261105-mkt-e3 · editor · research/c3_accuracy/README.md (lines 11, 92-133)
- **Objection:** The development/holdout sign flip is never stated.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): A neutral sentence in the headline (asserted from the scores), with its limits and no cause.

### R-20261105-mkt-e4 · editor · research/c3_accuracy/README.md (lines 88-133)
- **Objection:** The verdict labels cannot be reproduced from the columns.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Labels defined, a 'dev lower' column added, one- and two-sided tests stated.

### R-20261105-mkt-e5 · editor · research/c3_accuracy/README.md (lines 5, 19, 47, 88)
- **Objection:** Jargon is undefined.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): A Terms list in the banner (CW, DM-HLN, Holm, HAC, interval score, CRPS, Kupiec, Christoffersen, Clopper-Pearson, burn-in, frozen, RT, P2a/P2b); GFC defined in section 4.

### R-20261105-mkt-e6 · editor · research/c3_accuracy/README.md (lines 5-12, 51)
- **Objection:** The models are undefined.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): A Tasks and models list with pointers to SPECS.md and EVALUATION.md.

### R-20261105-mkt-e7 · editor · research/c3_accuracy/README.md (lines 5)
- **Objection:** The target, source and vintage are unnamed.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The banner names the Z.1 source, the denominator series, pp units and the 2026-09-11 vintage. Seasonal adjustment is not stated, because it is not verified.

### R-20261105-mkt-e8 · editor · research/c3_accuracy/README.md (lines 14)
- **Objection:** 'Where the models fail' is loaded and 'chance' is undefined.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Retitled 'Largest errors and crisis windows'; chance defined; out-of-window errors and the better relative performance inside the windows stated.

### R-20261105-mkt-e9 · editor · research/c3_accuracy/README.md (lines 12-13)
- **Objection:** The C1 'beats' cell lacks context, and the C1b verdict is unlinked.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The headline is singular and gives the other-instant ratios (asserted above one) and target overlap; the C1b bullet links c1b-prereg.md and gives units.

### R-20261105-mkt-e10 · editor · research/c3_accuracy/README.md (lines 168-177, 223-236)
- **Objection:** The holdout C1/C1b numbers are not marked descriptive.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Marked descriptive, with no test; the bias heading reworded.

### R-20261105-mkt-e11 · editor · research/c3_accuracy/README.md (lines 3)
- **Objection:** 'Nothing was rerun' and 'no number typed by hand' overstate.
- **Severity:** major
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The banner lists what the script computes and that the register rows are UNVERIFIED.

### R-20261105-mkt-e12 · editor · research/c3_accuracy/README.md (lines 7)
- **Objection:** 'Opened once' leaves out the crashed run.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The banner mentions 77460b4 and says the protocol allows one opening.

### R-20261105-mkt-e13 · editor · research/c3_accuracy/README.md (lines 49)
- **Objection:** The card is unnamed and the overlap wording is unclear.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Card c3-hcount named; plain wording; says the h = 4/8 numbers use the by-target count.

### R-20261105-mkt-e14 · editor · research/c3_accuracy/README.md (lines 19-38)
- **Objection:** Score columns are ambiguous and the placebo has no n.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Column meanings stated; placebo n/a.

### R-20261105-mkt-e15 · editor · research/c3_accuracy/README.md (lines 38)
- **Objection:** 'Carried flat' is not labelled as an assumption.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Labelled as an assumption in the registry and banner.

### R-20261105-mkt-e16 · editor · research/c3_accuracy/README.md (lines 12)
- **Objection:** The bridge regression's smaller n is not mentioned.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The headline gives the n for both models (from scores_dev.csv).

### R-20261105-mkt-e17 · editor · research/c3_accuracy/README.md (lines 15, 361)
- **Objection:** The ‡ threshold and 'anecdotes' are loose.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Headline notes that the n = 11-12 holdout cells are small too; 'anecdotes' replaced.

### R-20261105-mkt-e18 · editor · research/c3_accuracy/README.md (lines 137-164)
- **Objection:** The holdout coverage caveats are missing.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Text says the holdout brackets assume independence at h > 1 and that 1.00 on 12 is uninformative about too-wide intervals.

### R-20261105-mkt-e19 · editor · research/c3_accuracy/README.md (lines 166)
- **Objection:** H3 hangs on the 0.05 reading; a near-cut p.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): H3 linked to the protocol; computed note when a p falls in [0.05, 0.10); 'below nominal' marked descriptive.

### R-20261105-mkt-e20 · editor · research/c3_accuracy/README.md (lines 88)
- **Objection:** 'Far larger' is vague.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): The lag-8 p range is given (computed, registered) and called not robust.

### R-20261105-mkt-e21 · editor · research/c3_accuracy/README.md (lines 181)
- **Objection:** The NW file and the log paths are unnamed.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Column and files named; review-log paths given in section 7.

### R-20261105-mkt-e22 · editor · research/c3_accuracy/README.md (lines 225, 236)
- **Objection:** Brackets vs parentheses; −0.00.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Fixed (f2 prints 0.00).

### R-20261105-mkt-e23 · editor · research/c3_accuracy/README.md (lines 324-357)
- **Objection:** The C1/C1b holdout 'ten largest' are nearly the whole sample.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Stated; bridge/bridge_c1 equivalence stated.

### R-20261105-mkt-e24 · editor · research/c3_accuracy/README.md (lines 395-422)
- **Objection:** Section 5 heading is causal; source unnamed.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Retitled 'First release against latest vintage'; source files named; neutral sentence.

### R-20261105-mkt-e25 · editor · research/c3_accuracy/README.md (lines 441-456)
- **Objection:** Section 7 claim and Sources are incomplete.
- **Severity:** minor
- **Evidence:** editor pass on the C3 draft at 8e7d86c (suggestions only, logged by the markets track).
- **Proposed resolution:** wording change through make_report.py.
- **Status:** addressed (2026-11-05, markets track, make_report.py): Sentence qualified; specs, real-time files and logs added to Sources; test changes dated before the holdout.

### R-20261105-mkt-q40 · quant-reviewer · research/c3_accuracy/README.md:170 and make_report.py cov_status/label_b (label "80% coverage rejected")
- **Objection:** The only verdict that rule (b)'s coverage clause changes at the primary reading, rolling h = 1 Z-DAMP vs seasonal naive, is labelled "comparable (80% coverage rejected)". Its 80% coverage is not rejected: coverage 0.798 on 89 forecasts, Kupiec p = 0.958. The flip comes from `christoffersen_p` = 0.027, and `forecast.christoffersen` is the independence LR (1 df, the protocol's own "Christoffersen independence test", scoring-protocol.md:119), not a coverage test. Two separate issues follow, and neither is the open level question. (i) The label states a coverage rejection the data do not show. (ii) "p < 0.05 on either test" is not a 5% test. min(p_uc, p_ind) < 0.05 has size up to about 0.10. The standard joint test, Christoffersen conditional coverage (LR_uc + LR_ind, 2 df), can be recovered from the committed p-values. It gives p ≈ 0.086 (rolling Z-DAMP), ≈ 0.156 (expanding Z-DAMP) and ≈ 0.67 (expanding Z-DIR), so none is rejected at 0.05. This is read-only arithmetic on coverage_dev.csv and approximate, because the independence LR uses n − 1 transitions.
- **Severity:** major
- **Evidence:** research/c2_forecast/coverage_dev.csv (latest-rolling,1,Z-DAMP,0.8: kupiec_p 0.957791, christoffersen_p 0.0267287; latest-expanding,1,Z-DAMP,0.8: 0.752456, 0.0571311); forecast.py:249-262 (independence LR, 1 df); make_report.py cov_status (`min(ps) < alpha`), label_b; README.md:7, 130, 133, 170.
- **Proposed resolution:** In make_report.py, name the test that failed in the label, for example "comparable (coverage clause: Christoffersen independence p = 0.027; Kupiec p = 0.96)". In RULE_NOTE, say that the primary reading combines two 5% tests, so its overall level is not 5%. Pass the conditional-coverage reading to the coordinator as one more option for the level card, but do not choose it. Regenerate; nothing is rerun.
- **Status:** addressed (2026-11-05, markets track, make_report.py): the label is now "short of (b): coverage clause failed under this reading". A paragraph says the failure comes from Christoffersen, which tests independence, not coverage, that failing either test at 0.05 is not a 5% test, and that reading (iv) on card c3-b-level avoids this. The joint conditional-coverage test is not computed: it is outside the protocol and the decision is hers on c3-b-level.

### R-20261105-mkt-q41 · quant-reviewer · research/c3_accuracy/README.md:34, 36 (headline verdict counts)
- **Objection:** Both headline bullets state outcomes that depend on readings still open on Eleonora's docket, and they state them as findings. C2 says "the only 'beats' verdicts (2)", but across the readings the report itself computes the count is 1 (p < 0.10), 2 (p < 0.05) or 3 (p < 0.01, and Kupiec only). C1 opens with "no C1 model beats no-change or AR(1) at any instant k". Yet bridge_reg vs no_change at k = 2 meets every loss condition (Holm p 0.020, development ratio 0.44 on 16 targets, holdout ratio 0.89 on 12). Under the reading that the coverage clause does not apply to models without intervals, it would be a "beats". The bullet's later qualification does not undo the opening claim of a null. RULE_NOTE says "no verdict is final until she answers", but the headline is written as if they were final.
- **Severity:** major
- **Evidence:** read-only recomputation of verdicts_b and c1_verdicts: verdict_by_alpha {0.01: 3, 0.05: 2, 0.10: 1, Kupiec 0.05: 3} C2 "beats"; C1 k = 2 bridge_reg vs no_change "undetermined (no intervals)", verdict_a "beats". README.md:7, 34, 36, 136.
- **Proposed resolution:** In headline(), give the C2 count as a range over the readings, with the primary reading named, for example "1 to 3 'beats' depending on the coverage-clause reading, all against seasonal naive at h = 1". For C1, change the opening to "no C1 comparison is a 'beats' under the primary reading; one (k = 2, bridge_reg vs no-change) is undetermined pending card c3-b-nointv". Regenerate.
- **Status:** addressed: the C2 headline gives the range (1 to 3) across readings and the interim count, and says no verdict is final. The C1 bullet says no "beats" under the interim readings and that the k = 2 case is undetermined, not a failure.

### R-20261105-mkt-q42 · quant-reviewer · research/c3_accuracy/README.md:130 and make_report.py label_b ("comparable" widened)
- **Objection:** label_b sends "lower in both samples and significant after Holm, but a ratio above 0.95" to "comparable". The protocol's fixed wording defines "comparable" as "the loss difference is not significant, or its sign flips between samples" (scoring-protocol.md:161), and that case is neither. No row falls in it today: I checked all 42 C2 and 12 C1 rows. The README's label definition (line 130) nevertheless extends the protocol's wording without saying so. The ordering is otherwise sound: "does not beat" comes first, as in holdout_run.py; candidate_lower_rmse agrees with the recomputed development ratio in every row; and the development ratio uses each test's own rows (n matches in all rows).
- **Severity:** minor
- **Evidence:** make_report.py label_b; scoring-protocol.md:158-162; read-only recomputation (no row has p_holm < 0.05, lower in both samples, and a ratio above 0.95 in either sample).
- **Proposed resolution:** Either give that case its own label ("significant but below the 5% margin") or say at line 130 that "comparable" is widened beyond the protocol's wording and that no row currently falls there. Add an assert so a later change cannot hide it.
- **Status:** addressed: a separate label "short of (b)" covers significant-but-above-0.95 and coverage-clause failures; "comparable" keeps the protocol's wording.

### R-20261105-mkt-q43 · quant-reviewer · research/c3_accuracy/README.md:110-121 (origin-based subset, h = 4 and 8)
- **Objection:** The rows, n and ratios are correct. I recomputed them from holdout_forecasts.csv: 12/9/5, origins from 2023Q2, and all 34 values match tables/c2_holdout_origin_subset.csv. At h = 8, however, the no-change RMSE over the 5 forecasts is 0.11 pp, so the ratios (6.3 to 27.2) are mostly a near-zero denominator. The 5 targets (2025Q2 to 2026Q2) come from origins that overlap by up to 7 quarters, so they amount to about one episode. At h = 4 the 9 forecasts overlap by up to 3 quarters. The ‡ mark flags small n, but it does not flag this. A reader could take "ZC1-DIR 27×" as a measure of skill.
- **Severity:** minor
- **Evidence:** read-only recomputation: expanding h = 8 no-change RMSE 0.1104 pp, Z-DIR 6.548, ZC1-DIR 27.242; README.md:114-121.
- **Proposed resolution:** In origin_subset(), add each candidate's RMSE in pp next to the ratio (or instead of it) at h = 4 and 8. Add one sentence: the h = 8 subset is 5 overlapping forecasts from one stretch, and the no-change RMSE is unusually small there, so the ratios are unstable.
- **Status:** addressed: the origin-subset text warns that h = 8 (five overlapping forecasts, tiny no-change RMSE) is unstable.

### R-20261105-mkt-q44 · quant-reviewer · research/c2_forecast/holdout_forecasts_run.py (run-once guard and what the checks prove); README.md:39
- **Objection:** The gates are sound: prereg, approval row, check_order, clean tree and check_freeze all run before any holdout read, the script is unchanged between c783a5a and 8d60d86, and the committed CSV matches the sha256 in the run record. Two gaps remain. (i) The once-only guard looks only at the two output paths, in local refs (`git log --all`). An attempt that stops at check 1 or 2 has already read and processed the holdout, yet it writes nothing and does not block a retry. So the number of openings rests on the coordinator's word, not on the machine. (ii) Both checks compare cell aggregates (RMSE, MAE, interval scores, CRPS, n, first/last T), and those are unchanged by reordering rows within a cell. On their own they do not prove that each row is right, and the ten-largest lists depend on that. I closed most of the gap read-only. In all 72 rows, actual and share_T equal the 2026-09-11 vintage share differences and no_change = 0. From the CSV I recomputed MAE, IS80 and CRPS (48 cells, max diff 2e-15) and coverage_holdout (72 cells, exact). The remaining risk, forecast columns permuted within a cell, would need a bug in the same code that produced the scores.
- **Severity:** minor
- **Evidence:** holdout_forecasts_run.py check_once, main (checks 1 and 2); holdout_forecasts_run.json output_sha256 = sha256 of the committed CSV; read-only checks above.
- **Proposed resolution:** In the README's "Holdout openings" bullet or in section 7, say that the guard records successful runs only and that the coordinator attests a single attempt. In make_report.py check_holdout_table, add the per-row actual/share_T check against z1_share_vintages.csv and the coverage_holdout reproduction, both offline. No rerun.
- **Status:** addressed in the report (section 7): it states that the guard records successful runs only, cites the refused attempt in 8d60d86's message, says the checks are aggregate, and gives the reviewer's row-level confirmation. The committed script and record are not changed (frozen as run).

### R-20261105-mkt-q45 · quant-reviewer · research/c3_accuracy/README.md:34 and make_report.py indep_note ("Under the two-test readings in section 2 it would not count")
- **Objection:** The sentence is false for one of the three two-test readings. Rolling h = 1 Z-DAMP vs seasonal naive has Christoffersen p = 0.027, which is above 0.01, so under the reading "p < 0.01 on either test" it is a "beats". Section 2 (README.md:136) says so: "at p < 0.01: 3 'beats' (... rolling h = 1 Z-DAMP vs seasonal_naive)". The headline contradicts the report's own table. The same bullet adds "Reading (iv) leaves independence out, which is why it is the most lenient", but the 0.01 reading includes independence and gives the same 3 "beats". The verdicts themselves are right: ALPHA = "kupiec 0.05", cov_status keeps only the Kupiec p at 0.05, label_b/verdicts_b give exactly 3 "beats" (tables/c2_verdicts.csv and README section 2 agree), and the reported p-values (Kupiec 0.958, Christoffersen 0.027) match coverage_dev.csv (latest-rolling, h = 1, Z-DAMP, 0.8).
- **Severity:** major
- **Evidence:** research/c2_forecast/coverage_dev.csv latest-rolling,1,Z-DAMP,0.8: kupiec_p 0.957791, christoffersen_p 0.0267287; tables/c2_verdicts.csv verdict_by_alpha for that row {0.01: 'beats', 0.05: 'short of (b)', 0.1: 'short of (b)', 'kupiec 0.05': 'beats'}; README.md:136.
- **Proposed resolution:** In indep_note, compute the sentence from verdict_by_alpha instead of hard-coding it, e.g. "Under the two-test readings at p < 0.05 and p < 0.10 it would not count; at p < 0.01 it would." Drop "which is why it is the most lenient" or replace it with the true reason (see mkt-q46). Eleonora's choice of (iv) is not in question.
- **Status:** addressed (5c8bb4f): the note now says rolling Z-DAMP would still count at p < 0.01 and not at p < 0.05 or p < 0.1 (computed from verdict_by_alpha); the "which is why" clause is gone.

### R-20261105-mkt-q46 · quant-reviewer · research/c3_accuracy/README.md:7, 34, 134, 138 and make_report.py headline assert ("(iv) is the most lenient")
- **Objection:** (iv) is tied for most lenient, not the most lenient. The counts across the readings are p < 0.01: 3, p < 0.05: 2, p < 0.10: 1, (iv): 3, and both 3s are the same three comparisons. The assert (count under ALPHA == max) passes on a tie, so it does not check what the text says ("it gives the most 'beats'"). The readings are also not nested: (iv) applies Kupiec at 0.05, which is stricter than the 0.01 reading's Kupiec threshold, so a model with Kupiec p in [0.01, 0.05) and a high Christoffersen p would pass at 0.01 and fail under (iv). README.md:138 ("That makes (iv) the most lenient of the readings above") gives dropping Christoffersen as the reason, which does not hold against the 0.01 reading. Eleonora asked for (iv) to be flagged as the most lenient; the flag can stay if it is stated accurately.
- **Severity:** minor
- **Evidence:** README.md:136 (alpha_note output); make_report.py:421 assert; cov_status (ps[:1], alpha 0.05 for "kupiec 0.05").
- **Proposed resolution:** Word it as "(iv) gives as many 'beats' as any reading compared (3, tied with p < 0.01 on either test, the same three comparisons); it is the most lenient at the 5% level, because it drops the independence test". Make the assert match the wording, e.g. assert the count equals max and, at 0.05, that the (iv) beats are a superset of the two-test 0.05 beats.
- **Status:** addressed (5c8bb4f): "no reading compared gives more \"beats\" than (iv); p < 0.01 on either test gives the same three", in all four places; the assert now checks the tie and the identical set; "the readings are not nested" added.

### R-20261105-mkt-q47 · quant-reviewer · research/c3_accuracy/README.md:34 ("its misses fail the independence test (Christoffersen p = 0.027)")
- **Objection:** "Fail" states an unadjusted single 5% test result as a finding. The note puts it beside three Kupiec-only "beats". Holm across the three "beats" candidates' Christoffersen p-values (0.027, 0.057, 0.449) gives 0.080 for rolling Z-DAMP, so after adjustment it is not rejected at 5%. An approximate joint conditional-coverage statistic (LR_uc + LR_ind, chi2(2)), backed out of the two p-values, gives p of about 0.09. Both tests are asymptotic chi2 on n = 89 hits and assume a first-order Markov chain of misses, so the p-values are descriptive. Separately, expanding Z-DAMP (Christoffersen p = 0.057) also counts as a "beats" only because independence is left out at the 0.10 reading, and the note omits it because its threshold is 0.05.
- **Severity:** minor
- **Evidence:** coverage_dev.csv h = 1, 0.8 rows for the three "beats" candidates; joint statistic computed by hand from chi2(1) quantiles (4.91 + 0.003 = 4.91, exp(-4.91/2) = 0.086). This is not computed in the repo and is an approximation; mkt-q40 already notes that a joint test was not in the protocol.
- **Proposed resolution:** Write "Christoffersen p = 0.027, below 0.05 on its own test (unadjusted; descriptive)" rather than "fail". Optionally list the Christoffersen p for all three "beats" (0.449, 0.057, 0.027), not only those below 0.05.
- **Status:** addressed (5c8bb4f): "the independence test rejects at 5% ... one test, not corrected for the three \"beats\""; every "beats" candidate's Christoffersen p is shown (0.449, 0.057, 0.027), each with a register row. The Holm and joint-test figures are not added (not computed in the repo).

### R-20261105-mkt-q48 · quant-reviewer · claims/tracks/markets.csv (5 c3_ rows from 392a1bf; reproduction)
- **Objection:** Re-running make_report.py reproduces README.md and tables/ byte for byte. It does not reproduce claims/tracks/markets.csv: the generator appends the 5 new c3_ rows at the end, but the commit has them at the top of the file. The contents are identical; only the order differs. So the committed register is not exactly what the script writes, and the next regeneration will produce a spurious diff.
- **Severity:** minor
- **Evidence:** `uv run --project pipeline python research/c3_accuracy/make_report.py` at 392a1bf: research/c3_accuracy unchanged; `git diff claims/tracks/markets.csv` shows the 5 rows removed at lines 2-6 and re-added at the end (restored afterwards with git checkout).
- **Proposed resolution:** Commit the register exactly as the generator writes it, or make the generator insert new rows in a fixed order.
- **Status:** addressed: running make_report.py then make_readme_and_rows.py reproduces claims/tracks/markets.csv byte for byte in the committed order (checked with cmp). Order is not significant to the register check.

### R-20261105-mkt-s49 · skeptic · research/b2_crt_pricing/README.md:110 ("1 has no spread printed"); claim b2_stacr_no_spread, b2_stacr_above_loss
- **Objection:** Three tranches in her classes have no parsed spread, not one: 2017-HRP1 M-2, B-1 and B-2. All three have a spread printed, as a par/discount/IO split ("2.45%/1.250%/–", "4.60%/2.50%/6.07 Mult", "–/3.00%/–") that `pct()` drops by design. Two of them (M-2, B-1) are counted among the "220 attach at or above the baseline loss" because the note is set before the spread check, and the third is the "1 has no spread printed". So the 220/3/1 split adds up to 274, but "no spread printed" is factually wrong, and 220 includes two tranches whose spread is not in the data. The 2017-HRP1 B-2 attaches at 0 bps (detach 75), so it would have been a multiple candidate. The year table also sums to 271 tranches, not 274, and the text does not say so.
- **Severity:** major
- **Evidence:** stacr_tranches.csv:264-266 (spread_raw columns); stacr_2017_results.json `tranches_no_spread: 3` vs `count_breakdown_her_classes.no_spread: 1`; stacr_2017_tranches.csv 2017-HRP1 M-2/B-1 multiple_note "absent: attaches at or above…" with spread_bp empty; the year-table tranche counts sum to 271.
- **Proposed resolution:** Write "3 (2017-HRP1 M-2, B-1, B-2) print a par/discount/IO split of spreads that is not used". Count no-spread tranches before the attach test so the breakdown reads 50 / 218 / 3 / 3. Say that the year table covers the 271 with a usable spread.
- **Status:** addressed: "no spread printed" now takes precedence over "absent" in stacr_2017.py; counts 50 / 218 / 3 / 3; the README says the table covers 271 and names 2017-HRP1's split prints. METHOD.md corrected.

### R-20261105-mkt-s50 · skeptic · research/b2_crt_pricing/README.md:93, 97-108, 113-117 (indicative tranches inside the multiples)
- **Objection:** 6 of the 50 multiples are on retained "(Indicative)" B-2 tranches, which carry no sale price. That is 3 of the 6 multiples in 2017, 3 of the 7 in 2018, and 6 of the 10 tranches in the "0 bps" row of the attach-point table. Neither the multiple columns nor the attach table flag this. The "(indicative)" count appears only in the B tranche column, so 2 of the 8 indicative tranches (2017-HRP1 and 2018-HRP1 M-1) are invisible in the table. The attach-point argument ("not from a change in price") rests on a 0-bps baseline that is mostly not prices. Keeping indicative tranches is her choice (b). The objection is that the flag does not reach the numbers it affects.
- **Severity:** major
- **Evidence:** stacr_2017_tranches.csv: rows with retained_indicative=True and multiple_out not empty are 2017-DNA3, -HQA2, -HQA3 and 2018-DNA1, -DNA2, -HQA1 (all B-2, attach 0). Sold-only 0-bps row: n=4, median 1.21 (range 1.01–2.96); indicative: 0.96–1.31.
- **Proposed resolution:** Add an "of which indicative" count to the multiple columns and to the attach table (0 bps: 10, 6 indicative). Show the M-1 indicative count too, or footnote it. Optionally give the sold-only median alongside.
- **Status:** addressed: indicative counts shown in the M-1, B and "B with a multiple" columns and in the slice table; the bullet says 6 of the 50 multiples are on retained indicative B-2 tranches.

### R-20261105-mkt-s51 · skeptic · research/b2_crt_pricing/README.md:112 ("Much of the rise in the yearly median multiple comes from that, not from a change in price")
- **Objection:** This is a decomposition claim made without a decomposition, and it is stronger than METHOD.md ("partly reflect"). At a fixed structure (B-2 attaching at 25 bps, detaching at 75), the median multiple is 5.02 in 2020, 3.24 in 2021 and 5.29 in 2022. The 2021→2022 rise in the yearly median (3.2→5.3) happens entirely at an unchanged attach and detach point, so it is price. The 2020 jump (1.4→3.0) is mostly mix: 5 tranches at 10 bps (median 0.78) and 6 at 25 bps (5.02). The attach shift is real, but "not from a change in price" is not supported for the whole period.
- **Severity:** major
- **Evidence:** groupby(year, attach_bp, detach_bp) median of multiple_sofr_out from stacr_2017_tranches.csv: 2019 10/60 n=9 1.22; 2020 10/60 n=4 0.78; 2020 25/75 n=6 5.02; 2021 25/75 n=10 3.24; 2022 25/75 n=6 5.29.
- **Proposed resolution:** Say "part of the rise", or show the median by year within each attach/detach cell (the table above is small) and let the reader see both effects. Drop "comes from … not from a change in price".
- **Status:** addressed: sentence replaced. The bullet now gives medians on the fixed 25–75 bps slice (5.0, 3.2, 5.3 for 2020–2022) and says changes on a fixed slice are changes in spread.

### R-20261105-mkt-s52 · skeptic · research/b2_crt_pricing/README.md:111-117 (attach-point table ignores thickness)
- **Objection:** The multiple divides by the expected loss per dollar of tranche, so it depends on the detach point (thickness) as well as the attach point, but the table groups by attach point only. Inside the 25-bps row, 22 tranches are 25/75 (median 3.9) and 2 are 25/125 (2018-2019, 10.2 and 11.2), and those two set the "11.2" maximum. The 0-bps row's maximum of 3.0 is the single 0/125 tranche. "Baseline loss taken" is the same within a row, while expected loss per dollar differs about 2× (189 vs 95 bps a year). The sentence "a B-2 that attaches higher takes less of the baseline loss, so the same spread gives a higher multiple" is right but incomplete.
- **Severity:** minor
- **Evidence:** groupby(attach_bp, detach_bp) of the 50 multiples: 0/50 n=9 1.11; 0/125 n=1 2.96; 10/60 n=14 1.13; 10/65 n=1; 10/75 n=1; 25/75 n=22 3.94 (el_tranche_out 189); 25/125 n=2 10.70 (el_tranche_out 94.5).
- **Proposed resolution:** Group by attach and detach, or add a detach column and a sentence that a thicker tranche spreads the same slice loss over more dollars.
- **Status:** addressed: the table is now by slice (attach and detach), seven rows; single-tranche rows show the value without a range.

### R-20261105-mkt-s53 · skeptic · research/b2_crt_pricing/README.md:95-108 (class medians across years compare different instruments)
- **Objection:** Grouping by class is her choice (b), but the write-up gives no caveat that what sits in each class changes over the years, which makes the year-to-year columns misleading. The B column mixes B-1 and B-2 in shifting shares: equal 2017-2018 and 2020-2022; 13 B-2 vs 10 B-1 in 2019, because the FTR deals sell only B-2; B-1 only in 2023 and 2026. So 730 (2022) → 788 (2023) → 190 (2026) is not a like-for-like series. B-1 alone went 595 → 788. M-1 in 2022 is 10 M-1A + 10 M-1B (medians 218 and 352), against one M-1 per deal before, so part of the 78 → 258 jump from 2021 is the junior M-1B. Attach points within a class also drift: M-2's median attach moves from 100 bps (2017) to 225 (2024), and B-1's from 50 to 100.
- **Severity:** major
- **Evidence:** stacr_2017_tranches.csv grouped by year and sub_tranche: B-1/B-2 counts 6/6, 7/7, 10/13, 11/11, 10/10, 6/6, 2/0, 0/0, 0/0, 3/0; 2022 M-1A 218, M-1B 352; median attach_bp by year for M-2 100, 115, 112.5, 150, 125, 125, 150, 225, 195, 155.
- **Proposed resolution:** Add a caveat under the table: B mixes B-1/B-2 (shares by year), and M-1 from 2022 includes M-1A/M-1B. Optionally give B-1 and B-2 medians separately in the tranche CSV summary, as an appendix rather than a change to her classes.
- **Status:** addressed: new bullet "Each class's contents change by year" (B-1/B-2 shares, B-1 only in 2023 and 2026, M-1A/M-1B from 2022, attach drift).

### R-20261105-mkt-s54 · skeptic · research/b2_crt_pricing/README.md:89, 92 (wording)
- **Objection:** Two small misstatements. (a) "prints … every sold tranche's spread": the set also includes the 8 retained indicative tranches and the 3 split-priced 2017-HRP1 classes. (b) The multiple is described as "spread ÷ the tranche's expected loss per dollar of tranche". The code divides an annual spread by an annualised expected loss (bps a year per dollar of tranche, METHOD.md), and the README omits "a year", so a reader could take it as a cumulative ten-year loss.
- **Severity:** minor
- **Evidence:** stacr_2017.py comment "bps a year per dollar of tranche"; README.md:89, 92.
- **Proposed resolution:** Write "every listed tranche (sold, and retained with an indicative spread)" and "expected loss per dollar of tranche per year".
- **Status:** addressed: "the spread at issuance and the credit enhancement of every tranche it lists (sold, and a few retained)"; "expected loss a year per dollar of tranche".

### R-20261105-mkt-s55 · skeptic · web/components/scenarios/ScenarioTool.tsx:96-97, 177 ("Public share of balances")
- **Objection:** The page puts "Public share of balances" (computed over every exposure, federal student loans included) next to "Public share of losses" from presets that leave federal student loans out. On the default DFAST preset it shows 23% against 56%, and on the replay 42% against 56%. The like-for-like figure is 52%, which is the one the README uses ("52.4% once federal student loans are excluded"). The same mismatch shows in "Your own" whenever a class is unchecked. A reader will quote the 56 vs 23 gap, which overstates it by about 4 points.
- **Severity:** major
- **Evidence:** Playwright on /scenarios (local `next start`): DFAST shows "Public share of losses 23% | Public share of balances 56%", replay "42% | 56%". Recomputed from web/lib/b3/exposures.json: all classes 0.5638; excluding student_federal 0.5238. README.md "Like for like … 52.4%".
- **Proposed resolution:** Compute the balance share over the classes that are switched on in the active scenario (classes with pd>0 and present in `classes`), and label it as such, e.g. "Public share of balances in the classes covered". Or show both values with labels.
- **Status:** addressed: the tile now covers only the loan classes in the scenario and says which are left out ("Public share of balances, without federal student loans": 52% for the stress-test and replay presets, 56% with student loans), checked in the browser.

### R-20261105-mkt-s56 · skeptic · web/components/scenarios/ScenarioTool.tsx:160-166, page.tsx:46-48; research/b3_scenarios/engine.py:102 (transfer base)
- **Objection:** The transfer applies to the whole `gse_agency` mortgage bucket (transfer_eligible = mortgage and gse_agency). That bucket includes FL413065105 "Agency- and GSE-backed mortgage pools", which holds the Ginnie (FHA/VA) pools. FHA/VA risk is federal and is not covered by GSE CRT or private mortgage insurance. Yet the checkbox says "GSE mortgage losses" and the caveat says "only on GSE mortgages". The share input also goes up to 100% with no cap guidance, so the page can move every public mortgage loss to private hands: replay at 100% with an uncapped limit gives public $16.2B, 1%, and $784B moved. That reads as private investors bearing the losses on FHA/VA books.
- **Severity:** major
- **Evidence:** pipeline/series_catalog.yaml:51 (FL413065105 → gse_agency); engine.py:102; Playwright: replay + transfer share 100, cap 100000 → "Held on public books $16.2B … Public share of losses 1% … Moved by transfer $784B". README "Upper bound" bullet itself says the bucket includes Ginnie (FHA, VA) pools.
- **Proposed resolution:** Either restrict the transfer base to the GSE (Fannie/Freddie) share of the bucket, which needs a split of the pools series, or relabel it "mortgages in GSE and agency pools, including Ginnie (FHA/VA), on which CRT/MI do not apply" and say that the share should reflect cover on the GSE part only. Until A2's caps exist, consider bounding the share or labelling large values as illustrative.
- **Status:** addressed: the transfer is labelled "mortgages held by the GSEs and in agency pools", and the hint says the group includes Ginnie Mae (FHA and VA) pools, so a large uncapped share overstates what transfer can move.

### R-20261105-mkt-s57 · skeptic · web/app/scenarios/page.tsx:49-53 (proxy caveats omit bias directions)
- **Objection:** The page states that the presets are proxies but leaves out the bias directions the README records. The replay's 42% public share is "probably an upper bound" (bank charge-offs from subprime and option-ARM loans applied to GSE and Ginnie books). In DFAST, the first-lien rate on every mortgage biases the public share up, and FFEL loans counted as private bias it down. The presets apply no CRT/MI. A reader of the page sees 42% and 23% as point figures, with no sign that one is an upper bound, and the preset note has no direction either.
- **Severity:** major
- **Evidence:** research/b3_scenarios/README.md "Upper bound", "Junior liens", "FFEL loans", "No transfer" bullets; page.tsx bullet "whose losses would differ" (no direction); preset notes in the Playwright output carry no bound language.
- **Proposed resolution:** Add one line per preset, in the preset note or the caveat list: replay public share likely an upper bound; DFAST public share biased up by junior liens and down by FFEL; no transfer applied.
- **Status:** addressed: a caveat bullet "Known biases in the presets" gives the four bias directions from the README (replay public share probably an upper bound; junior liens push the DFAST public share up; FFEL pushes it down; no transfer), with no figures.

### R-20261105-mkt-s58 · skeptic · web/components/scenarios/ScenarioTool.tsx:131-139 (preset loss rates shown as "Default rate")
- **Objection:** The presets hold loss rates with lgd = 1.0, so the form shows, for example, "Default rate 1.5%, Loss given default 100%" for DFAST mortgages and 10.9% for consumer credit. These are net loss rates, not default rates, and a reader could quote "a 10.9% default rate" or "100% severity".
- **Severity:** minor
- **Evidence:** web/lib/b3/preset_dfast2026.json: mortgage pd 0.015 lgd 1.0; consumer_other pd 0.1095 lgd 1.0; replay pd 0.0874/0.189 lgd 1.0. The preset label itself says "loss rates".
- **Proposed resolution:** When a preset is active, add a hint such as "Presets give a loss rate: entered as the default rate with 100% severity", or relabel the column "Default (or loss) rate".
- **Status:** addressed: with a preset, the column reads "Loss rate, % (as default rate)" and the hint says presets enter a loss rate as a default rate with 100% loss given default.

### R-20261105-mkt-s59 · skeptic · web/app/scenarios/page.tsx:25-27 with ?case= (synthetic balances under a Z.1 header)
- **Objection:** With `?case=` the tool uses synthetic balances, and the b3-case note says so. The header above it still states that the tool applies scenarios to Z.1 balances "as of 2026-06-30", and "Public share of balances" is then synthetic. The hook is reachable on any deployment. The note is adequate, but a screenshot of the totals plus the header could circulate as Z.1 numbers.
- **Severity:** minor
- **Evidence:** ScenarioTool.tsx:62-63, 108; page.tsx header renders unconditionally.
- **Proposed resolution:** Place the test-case note inside or next to the totals block, or render the hook only in non-production builds.
- **Status:** addressed: the test-case note now says the synthetic balances replace the Z.1 balances described above and that nothing shown is Z.1 data. The header stays static (server-rendered); the hook is for tests only.

### R-20261105-mkt-e26 · editor · web/components/scenarios/ScenarioTool.tsx:152-155, 163-168, 172; page.tsx:64-66 (transfer cap)
- **Objection:** The cap input defaults to 0, and in the engine a cap of 0 means no transfer at all (engine.py:64 needs cap_musd > 0). The hint says 'a large share with no cap overstates what transfer can move', which reads as if leaving the cap empty or 0 means uncapped. A reader who ticks the box, enters a 60% share and leaves the cap at 0 sees nothing moved and 'Moved by transfer $0' with no explanation. Also the checkbox says the losses pass 'to private investors', but mortgage insurers are not investors, and 'credit-risk transfer' and 'mortgage insurance' are never defined for a general reader.
- **Severity:** major
- **Evidence:** ScenarioTool.tsx:160-167, 172; engine.py:64-65; README.md:10 ('the cap is 0' in the DFAST bias list means no cover).
- **Proposed resolution:** State what cap 0 does, and how to get 'no cap' (a very large number). Say in plain words what credit-risk transfer and mortgage insurance are, and replace 'investors' with something that covers insurers. Author's wording.
- **Status:** addressed: the transfer is "Move part of the losses ... to private risk-takers"; the hint defines credit-risk transfer and says a cap of zero moves nothing, so set both; "a large share with a high cap" replaces "no cap".

### R-20261105-mkt-e27 · editor · web/app/scenarios/page.tsx:25-26, 50-52; ScenarioTool.tsx:26-31, 118 (preset names and what 'stress test' is)
- **Objection:** Page and README name the same presets differently and the page never says what they are. The page says 'Stress test 2026 (proxy)' and 'the Fed's stress-test projections'; the README says 'DFAST'. A reader cannot tell it is a hypothetical severely adverse scenario for the largest banks, not a Fed forecast or a sector-wide result, so 'Stress test 2026' can be quoted as what the Fed expects. 'Realised charge-offs' (spelled British, README uses the same) and 'proxy' are not explained either: a proxy of what, and why it is used for holders who are not banks. 'Proxy' appears in every label but its meaning is only implicit in the second bullet.
- **Severity:** major
- **Evidence:** page.tsx:50-52; ScenarioTool.tsx:26, 28, 30; README.md:17-19 ('severely adverse', 'largest banks'); rule 'proxies must be labelled as proxies' is met only by the word.
- **Proposed resolution:** Use one name on page and README and expand it once. Say on the page that the stress case is a hypothetical severe recession for the largest banks, and what a charge-off is. Add one sentence on what 'proxy' means here (bank loss rates standing in for rates on the GSE, federal and other books). Author's wording.
- **Status:** addressed: preset labels "Fed stress test 2026, hypothetical (proxy)" and "2008–12 replay of bank write-offs (proxy)"; the caveats explain the severely adverse scenario ("a test, not a forecast"), what write-offs are, and what "proxy" means.

### R-20261105-mkt-e28 · editor · web/app/scenarios/page.tsx:51-52, 66; ScenarioTool.tsx:154; README.md:66-73 (hard-coded figures; horizon caveat)
- **Objection:** Three consistency gaps. (1) The rule is no hard-coded figures in the copy, and the README says 'Every number on the page is computed' (README.md:73), but page.tsx:51-52 writes 'nine quarters' and 'twenty' and the labels hard-code '2026' and '2008-12'. These are not computed from the preset files. (2) The tool hint says 'The default rate is cumulative over the whole horizon' for every scenario, but README.md:51 says the replay's cumulative figure is a sum of twenty quarterly rates applied to today's balances, 'an approximation, not a share of a starting balance'. The page tells the reader about the horizon difference but not that approximation. (3) README.md:73 therefore overstates what the copy does.
- **Severity:** major
- **Evidence:** page.tsx:51-52; ScenarioTool.tsx:26-30, 154; README.md:51, 73.
- **Proposed resolution:** Either derive the quarter counts and years from the preset JSON or change the README sentence to say which labels are fixed text. Add the replay approximation to the horizon bullet or the hint. Author's decision.
- **Status:** addressed: the horizons and the preset years are read from the preset files in page.tsx; the cumulative-rate approximation for the replay is stated; the README says what is computed.

### R-20261105-mkt-e29 · editor · web/app/scenarios/page.tsx:61-63; ScenarioTool.tsx:28 (federal student loans left out)
- **Objection:** 'Federal student loans have no bank loss series. They are left out of the main presets' does not say what leaving out means: a zero loss on the largest public holding after mortgages. A reader will compare the public share of losses with a public share of balances and not see that the omitted class is almost all public, so the main-preset public share is biased down on that count (the README says so only for the weak-proxy variant, and for FFEL the other way). The page also does not say which rate the 'weak proxy' uses (the 'other consumer' rate, README.md:22), so the label cannot be judged.
- **Severity:** minor
- **Evidence:** page.tsx:61-63; README.md:22, 29-32 (23% vs 36%); exposures.json (student_federal is all federal_direct).
- **Proposed resolution:** Say that the omission lowers the public share of losses and name the stand-in rate. Author's wording.
- **Status:** addressed: the student-loan bullet says leaving them out lowers the public share of losses and names the stand-in rate (the stress test's other-consumer rate).

### R-20261105-mkt-e30 · editor · web/components/scenarios/ScenarioTool.tsx:181-186, 213 (totals tiles and table note carry no estimate label)
- **Objection:** The proxy and estimate label sits only in the preset note above the form. The totals ('Total losses', 'Held on public books', 'Public share of losses') are the numbers most likely to be screenshotted and carry no 'estimate' or 'proxy' marker and no unit basis. The table note 'dollars of today's balances' does not say that they are nominal, undiscounted and not a forecast, and 'Held on public books' next to 'Public share of losses' invites reading the share as who bears it, which the page itself warns against. 'Your own' mode shows the totals with no label that they are illustrative.
- **Severity:** minor
- **Evidence:** ScenarioTool.tsx:181-186, 213; page.tsx:45-47 ('Who holds is not who bears').
- **Proposed resolution:** Put an 'estimate under a proxy' marker (or 'illustrative' in Your own) in or next to the totals block and state nominal dollars in the table note. Author's wording.
- **Status:** addressed: tiles are "Losses on public/private books" and "Public books' share of losses/balances", with a note under them (estimates, today's dollars, not discounted, holder not bearer); the table note says not discounted.

### R-20261105-mkt-e31 · editor · web/components/scenarios/ScenarioTool.tsx:123, 127-129; page.tsx:26-29 (undefined terms)
- **Objection:** Terms a general reader will not know and the page never defines: 'loss given default' (field label, aria-labels, hint), 'GSEs' and 'agency pools' (intro, transfer legend), 'Z.1' and 'Financial Accounts' (intro), 'Ginnie Mae (FHA and VA)', 'FFEL' is avoided but 'federally guaranteed student loans held by private lenders' is not linked to the Z.1 'private' class, and 'private securitization'. 'Spread over quarters' is a column of counts of quarters, so the heading does not match its content. The intro also says 'Pick a scenario' for what the bullets say are proxies applied to today's balances; 'scenario' is fine but the heading 'whose books take the loss?' again reads as who bears.
- **Severity:** minor
- **Evidence:** page.tsx:25-29; ScenarioTool.tsx:123, 127-129, 152-155, 164-166.
- **Proposed resolution:** Gloss each term once, in plain words, or link to a short glossary. Rename the quarters column. Author's wording.
- **Status:** addressed: the intro explains Z.1, GSEs, agency pools (incl. Ginnie Mae) and private securitization; the hint defines default rate and loss given default; the column reads "Number of quarters"; the heading asks which lenders' books record the losses.

### R-20261105-mkt-e32 · editor · web/app/scenarios/page.tsx:69-72; research/b3_scenarios/README.md:66-78 (closing line and README section)
- **Objection:** The closing line says the engine 'is the same code that is tested there against the Python version, case by case'. The tests cover five fixed cases plus the presets to 1e-9, and README.md:72 records that one timing weight reaches the page one unit in the last place away from the file, so 'the same code ... case by case' is slightly stronger than what was tested, and it says nothing of the bundler's re-serialising. The path 'research/b3_scenarios/' is not a link a visitor to the site can open, and the README it points to is itself a Claude draft. In the README section, 'unit in the last place' is unexplained and the 'In the browser' text does not say that the page's presets are still proxies pending her review.
- **Severity:** minor
- **Evidence:** page.tsx:69-72; README.md:70-73; web/lib/b3/engine.test.ts as described in README.md:71.
- **Proposed resolution:** Say what was compared and to what tolerance, and link or name where the method is published. Define or drop 'unit in the last place'. Author's wording.
- **Status:** addressed: the closing line says the page runs a copy of the tested code that matches the Python version on fixed test cases up to computer rounding; the README explains "unit in the last place". The repository path stays text (no public link is known to be available).

### R-20261111-mkt-s60 · skeptic · research/b4_policy_scenarios/README.md:48; METHOD.md:34; claims b4_student_cbo_* (program-account outlays called "the subsidy cost")
- **Objection:** Under FCRA a credit program account pays out only positive subsidy (plus upward reestimates and positive modifications). Negative subsidies, downward reestimates and negative modifications are paid from the financing account into a receipt account, which a spending-by-account file does not carry. So these outlays are the gross positive-subsidy cost, not "the subsidy cost" of direct loans. A shift of cohorts or loan types between positive and negative subsidy moves the series without the net cost moving in step, so the 81% fall can overstate (or misstate) the fall in net cost. Separately, METHOD.md:34 says "with modifications and reestimates as recorded", but CBO baselines do not project future reestimates, and under FCRA the modification cost of P.L. 119-21 for existing loans is booked in the year of enactment (FY2025), outside the FY2026–FY2035 window.
- **Severity:** major
- **Evidence:** The 2026-02 file lists 091 accounts 0200, 0202, 0206, 0230, 0243, 4257, 4299, 5557 only. No Direct Loan receipt or financing account appears (`grep -i "financing account"` finds only 020-9993 "Net interest paid from credit financing accounts"). 2 U.S.C. 661a quote in sources.md defines the program account as the account from which "cost is disbursed to the financing account". It does not say that every element of cost passes through it.
- **Proposed resolution:** Say "positive subsidy cost paid from the program account (gross of negative subsidies and downward reestimates, which go to a receipt account not in this file)". Drop "with modifications and reestimates as recorded", or say that modifications enacted in FY2025 fall outside the window. Author's wording.
- **Status:** addressed: the README and METHOD now say the outlays are what the account pays out for the loans' cost, and that reestimates and administrative funding sit in the program account (2 U.S.C. 661c(f), (g), fetched and recorded in sources.md). They no longer call it the full subsidy cost: the sources fetched do not establish where a negative subsidy is recorded, so that claim is not made either way. "Modifications and reestimates as recorded" is removed.

### R-20261111-mkt-s61 · skeptic · research/b4_policy_scenarios/README.md:11, 50, 66 (before/after framing invites reading the fall as the law's effect)
- **Objection:** The row and the table pair "last before P.L. 119-21" with "first after", and the fall ($153B, 81%) sits in the "Student-loan reform" row next to the law's provisions. But the drop is already 77% in FY2026 ($16.7B to $3.9B). FY2026 runs from October 2025, and the provisions the row cites take effect from July 1, 2026. So most of the FY2026 drop, at least, is unlikely to come from those provisions on new loans. It points to technical or economic re-estimates (e.g. subsidy-rate or repayment-plan assumptions) or to items outside the cited provisions. The caveat "not the law's effect alone" is present, but the layout still invites the causal reading.
- **Severity:** major
- **Evidence:** cbo_direct_loan_outlays.csv: 2025-01 FY2026 16682 vs 2026-02 FY2026 3875 (-76.8%). The 2024-06 vintage FY2026 value of 16737 shows the pre-law path was stable. README.md:11 states the effective date of July 1, 2026.
- **Proposed resolution:** Label the baselines by date only, or add a line that the fall begins before the cited provisions take effect and cannot be attributed to the law. Cite CBO's own breakdown of baseline changes into legislative, economic and technical components (the February 2026 Budget and Economic Outlook appendix), or CBO's cost estimate for P.L. 119-21, if it can be reached. Author's wording.
- **Status:** addressed: the README drops "last before / first after" and adds the bullet "Too early to be the Grad PLUS change" (most of the fall is already in FY2026, while the provision applies from July 1, 2026). METHOD records it.

### R-20261111-mkt-s62 · skeptic · README.md:50; METHOD.md:35; student_proxy.py docstring ("the last before P.L. 119-21 ... the first after")
- **Objection:** The only vintage evidence is the repository's month labels (`catalog.json` vintages ['2026-02','2025-01','2024-06']). No release date and no statement of which laws each baseline includes is given. "Last before / first after" holds only within the repository's three files. Nothing committed shows that CBO published no account-level projections in between. "Thirteen months" is right by the labels (2025-01 to 2026-02).
- **Severity:** minor
- **Evidence:** cbo-data catalog.json datasets[10]: vintages and temporal only. CHANGE_LOG.md has no spending_detail entry. Commit history for spending_detail is the single "Initial commit." (2026-05-27).
- **Proposed resolution:** Say "the repository's last vintage before / first after". Cite CBO's publication dates for the two baselines from cbo.gov (publication 51142), or record that they were not checked.
- **Status:** addressed: the baselines are named by the repository's file labels, with the law approved between them; "thirteen months" kept (confirmed).

### R-20261111-mkt-s63 · skeptic · claims/tracks/markets.csv b4_student_cbo_* (vintage column)
- **Objection:** All 26 rows carry vintage `cbo:2026-06-12`. That is the repository commit date, not the baseline vintage. Rows from the January 2025 and February 2026 baselines therefore look like one vintage, and a later re-run against a new commit would change the vintage without the data changing.
- **Severity:** minor
- **Evidence:** markets.csv rows 2–27, vintage field. `git log -1` in the clone: 284a956, 2026-06-12, "demographic data 2026-01 correction" (not a spending_detail change).
- **Proposed resolution:** Use the baseline label in vintage (e.g. `cbo-baseline:2025-01` / `2026-02`, both for the change rows), with the commit kept in notes or computation.
- **Status:** addressed in the notes, not the vintage: every row's notes now say the vintage is the repository commit date and that the baseline (file label 2025-01 or 2026-02) is named in the claim. Kept, because the vintage format records a retrieval snapshot and the files carry only month labels.

### R-20261111-mkt-s64 · skeptic · README.md:44-71; METHOD.md 3b (other student-loan accounts not mentioned)
- **Objection:** The section does not say which related accounts are excluded. The FFEL program account (091-0231) appears only in the 2024-06 file (FY2024 $18.2B, zeros after) and is absent from the later two files. The FFEL liquidating account (091-0230), the student loan reserve fund (091-4257, FFEL guaranty agencies), TEACH (091-0206) and Student aid administration (091-0202, which holds Direct Loan servicing and admin costs; mandatory outlays FY2026 $1.5B in the 2026-02 file vs $0.7B in the 2025-01 file) are also left out. Separately, the committed CSV and student_proxy.json path carry the 2024-06 FY2024 Direct Loan value of $149.3B, about 9x any other year. My inference is that it reflects reestimates or modifications booked in FY2024. It is unlabelled and would mislead if charted as "context".
- **Severity:** minor
- **Evidence:** Account scan of the three files (TIN prefix 091, titles matching student/loan/FFEL). cbo_direct_loan_outlays.csv row 2024-06,2024: 149312.0.
- **Proposed resolution:** Add one sentence listing the excluded accounts and why: FFEL lending ended in 2010, and admin costs sit outside credit-reform cost. Flag the FY2024 context value, or drop FY2024 from the context path.
- **Status:** addressed: the README bullet "One account only" names the related accounts left out (Student aid administration, TEACH Grant program account, FFEL liquidating account, Federal student loan reserve fund). METHOD says the June 2024 baseline is context only, not shown, and its FY2024 value is unexplained by the repository.
