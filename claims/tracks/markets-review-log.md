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
