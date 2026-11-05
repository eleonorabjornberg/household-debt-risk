### R-20261104-ana-39 · skeptic · research/a2_net_exposure/fannie_extract.py:28-29,63-69
- **Objection:** The restatement cross-check ("where a later 10-K restates a year end, both must agree", docstring line 11) never fires for FY2023-FY2025: those 10-Ks print "2023 , compared with" (space before the comma), which `(?:,? compared ...)` does not match, so the prior-year values for 2022, 2023 and 2024 are silently not compared. The values happen to agree (38, 42, 43), so no number moves; the check is weaker than documented and the tests (test_fannie_extract.py) cover only the no-space layouts.
- **Severity:** minor
- **Evidence:** `CRT.search("...$42 billion as of December 31, 2023 , compared with approximately $38 billion as of December 31, 2022 .").groups()` -> `('42', '2023', None, None)`; fannie_ce_outstanding.csv crt_quote for 2023-2025 lacks "compared".
- **Proposed resolution:** allow `\s*,?\s*compared` and add a fixture with the FY2023 spacing; assert the prior group matched whenever "compared with" follows.
- **Status:** open

### R-20261104-ana-40 · skeptic · research/a2_net_exposure/sources.md:55-58; fannie_ce_outstanding.csv 2013-2016
- **Objection:** Fannie's mortgage-insurance risk in force is recorded as "not found" for FY2013-16, but the 10-Ks do state it in a different wording ("We had total mortgage insurance coverage risk in force of $126.2 billion and $117.9 billion ... as of December 31, 2016 and 2015"). Not netted and not in a published claim, so nothing published is wrong, but "not found" is inaccurate.
- **Severity:** minor
- **Evidence:** fnma_10k_fy2016.htm text, offset ~1047466 (regex MI requires "mortgage insurance risk in force was").
- **Proposed resolution:** extend MI pattern to "mortgage insurance coverage risk in force of", or change "not found" to "stated in other wording, not extracted".
- **Status:** open

### R-20261104-ana-41 · skeptic · research/a2_net_exposure/README.md:40; net_exposure.py:143; tenk.py:26
- **Objection:** Stale text after the Fannie addition: README:40 still says Fannie's cover "will narrow the range from above once its filings can be read", and the two code comments say SEC was not fetched; the section at README:69-72 now reports it.
- **Severity:** minor
- **Evidence:** file:lines above.
- **Proposed resolution:** point README:40 to the 56.0% figure (and its year coverage); update the comments.
- **Status:** open


### Responses to R-20261104-ana-39 to -41 (analysis track, 2026-11-04)
- ana-39: accepted. The restatement pattern now allows a space before the comma; the check runs for every year and passes (2022–2024 restated values agree). Test added.
- ana-40: accepted. FY2013–16 wording ("total mortgage insurance coverage risk in force of $X billion ... as of December 31, FY") added, dated by its own sentence; the four cells in sources.md and the CSV now hold the figures and quotes. Not netted, so no published number changes.
- ana-41: accepted. README line 40, net_exposure.py and tenk.py no longer say Fannie's filings cannot be read.

### R-20261104-ana-42 · quant-reviewer · research/a7_causal/README.md:9; claims/tracks/analysis.csv:9 (a7_h1_rank)
- **Objection:** "2.2% of the 90 comparable five-week windows ... fell as much" misreads the rank p. p = (k+1)/(n+1) = 2/91, so k = 1: one of 90 placebo windows (the one starting 2008-03-20, abnormal -0.418 pp) fell as much, i.e. 1.1%. The prereg decision-rule wording is "more than in N of M placebo windows" (prereg:144).
- **Severity:** should fix
- **Evidence:** reproduced offline (functions imported, no outputs written): placebo_n 90, count(placebo <= -0.3936) = 1, p_rank 0.022.
- **Proposed resolution:** "one of 90 placebo windows fell as much (one-sided rank p = 2/91 = 0.022)"; fix the register description. Add that the 90 windows overlap (about 20 non-overlapping), so the p is coarse.
- **Status:** open

### R-20261104-ana-43 · quant-reviewer · research/a7_causal/README.md:11; causal.py:201-202
- **Objection:** The addendum (prereg:202) fixes Holm across H1-H4 with rank p for H2/H3. It does not say failed fits enter as p = 1; that convention is in the code only. It makes no difference: with the computed rank p (0.769, 0.462) Holm gives the same rejections (H4 only; H1 0.022 > 0.0167). The README does not say this, and it presents the two-hypothesis family ("H1 would pass") as an open question without saying that changing the family now would be a deviation made after the results.
- **Severity:** should fix
- **Evidence:** a4.holm({H1:.022,H2:.7692,H3:.4615,H4:2e-6}) -> only H4 rejected.
- **Proposed resolution:** state that p = 1 is a code convention and that the verdict holds under either treatment. Label the H1+H4 family as a post-results sensitivity that cannot replace the pre-registered verdict.
- **Status:** open

### R-20261104-ana-44 · quant-reviewer · research/a7_causal/causal.py:200 (with :156)
- **Objection:** The series is cut to 1999Q1 before its(), so the placebo trend windows P-32..P-1 for 2004Q1-2006Q4 get only 20-31 quarters, not the 32 in the addendum (prereg:198). Z.1 starts in 1945Q4 for both series.
- **Severity:** should fix (verdict unaffected: both fits failed)
- **Evidence:** window lengths 20,21,...,31. With the full series, H2 p stays 0.769 and H3 p moves from 0.462 to 0.538.
- **Proposed resolution:** pass the untrimmed series (or start at 1996Q1) and regenerate results.json.
- **Status:** open

### R-20261104-ana-45 · quant-reviewer · research/a7_causal/results.json (H2, H3); README.md:14
- **Objection:** The fit-failed rule (prereg:146) says "show the fit, no effect estimate". results.json still reports mean_post_deviation (-870 $bn, +8.2 pp), post_deviations, ratios and p_rank for H2/H3. README:14 also comments that the series "move sharply after 2008Q3", but does not show the fit numbers.
- **Severity:** should fix
- **Evidence:** holdout RMSPE vs 2006-07 SD: H2 657 vs 170 ($bn), H3 2.23 vs 0.81 (pp).
- **Proposed resolution:** in the README, give the holdout RMSPE and SD for each series. In results.json, drop the post-period fields when fit_ok is false, or label them clearly as not estimates.
- **Status:** open

### R-20261104-ana-46 · quant-reviewer · research/a7_causal/causal.py:112-113, 206
- **Objection:** (a) sqrt(5*LRV) is the asymptotic variance of a five-week sum. The finite-window variance from the sample autocovariances (5g0 + 2*sum (5-k)gk) gives t = -2.37. Adding the error in estimating mu gives -2.43. The iid t is -2.31. The variance also comes from the estimation window, but September-October 2008 was more volatile, so every version overstates t. (b) The "against" branch uses 1 - p_rank as its upper-tail p and skips Holm, unlike the "supported" branch. It was not triggered.
- **Severity:** note (the HAC t is secondary and outside Holm)
- **Evidence:** reproduced: LRV 0.00498, g0 0.00581.
- **Proposed resolution:** state that the t is descriptive and give the finite-window version. Use (count(placebo >= ab)+1)/(n+1) for the "against" test.
- **Status:** open

### R-20261104-ana-47 · quant-reviewer · research/a7_causal/README.md:12,20; docs/decisions/a7-causal-prereg.md:193
- **Objection:** (a) Lehman is disclosed. The README could also say that -0.366 of the -0.35 pp fall comes in week 0 (into 11 Sep, before Lehman); this is descriptive, not a new test. Other news in the window, such as AIG and TARP, should also be named. (b) The addendum header says "16:55 UTC", but it was committed at 16:47:49. The order of events checks out: addendum 16:47, code 16:50:09, data fetched 16:50:40, results 16:55. Only the label is wrong. (c) H4: the pre-period 2008Q2-2010Q2 is partly treated by ECASLA (prereg:59). The README does not mention this.
- **Severity:** note
- **Evidence:** git log and stat mtimes; weekly changes [-0.366, 0.018, -0.055, 0.127, -0.072].
- **Proposed resolution:** small wording additions.
- **Status:** open

### Responses to R-20261104-ana-42 to -47 (analysis track, 2026-11-04)
- ana-42: accepted. README and register now say one of 90 overlapping placebo windows fell as much (rank p 0.022).
- ana-43: accepted. Holm now uses the computed rank p for H2/H3 as the addendum says (0.77, 0.54); same verdicts. The H1+H4 family is labelled a sensitivity examined after the results.
- ana-44: accepted. Full series used, so every placebo pre-window has 32 quarters; H3 p 0.46 → 0.54; verdicts unchanged.
- ana-45: accepted. Failed fits keep their statistics only under "diagnostics_not_an_effect_estimate"; README shows the fit numbers.
- ana-46: noted; the exact five-week-variance t (−2.37) is reported next to −2.49. The "against" branch is unused here (the change is negative).
- ana-47: accepted. README says 0.37 pp of the fall came in week 0, before Lehman; notes ECASLA in the H4 pre-period; records the addendum's 16:55 header against its 16:47 commit time.

## 2026-11-05: a8-promo (b) applied (commit 2549090), skeptic and editor round

Changed text: `research/a8_international/README.md:15,18`, `compare.py` docstring and DE note, register row `a8_de_promotional_banks_unclassified`. Reviewers read the diff and `sources.md`/`Q7_EVIDENCE.md`; both found no changed number (0.0115, 0.2913, 0.3028 unchanged; tests pass).

### R-20261105-ana-48 · skeptic · major · README.md:15 (col. 3), :18; register `a8_de_public_owned_share`; CROSSWALK.md:11
- **Objection:** the holder (a) share, 30.3%, includes the whole 17,817 category, which now is labelled as holding DZ Bank; the holder measure therefore counts DZ Bank as publicly owned, whose ownership is not sourced (Q7_EVIDENCE.md:82). These places still say "promotional banks".
- **Status:** open, sent to the coordinator as a proposed card. Outside a8-promo (which relabels the 1.1% only); not edited.

### R-20261105-ana-49 · skeptic · minor · CROSSWALK.md:11
- **Objection:** still says Länder promotional banks are not sourced; follow-ups 2–3 source NRW.BANK, Rentenbank and L-Bank.
- **Status:** open, in the same proposed card (copy outside her a8-promo choice).

### R-20261105-ana-50 · skeptic · minor · README.md:18, register notes
- **Objection:** "the category also holds DZ Bank" dropped the caveat that this comes from the P&L and bank-office statistics and that the I.7 footnotes were not re-read.
- **Status:** accepted; caveat added to README:18.

### R-20261105-ana-51 · skeptic · minor · README.md:18
- **Objection:** "backs the banks' creditors, not their borrowers" simplifies the statutes, which also cover credits to third parties the bank expressly guarantees.
- **Status:** accepted; now "cover the banks' own borrowing and any credits a bank expressly guarantees; none of the texts on file guarantees the households the banks lend to".

### R-20261105-ana-52 · skeptic · note · option (b) as applied
- **Objection:** Q7_EVIDENCE's own wording of (b) added "DZ Bank does not appear to"; the docket card and PLAN don't, and nothing on file shows DZ Bank's guarantee status. Q7_EVIDENCE:48 still names the old column.
- **Status:** no DZ Bank guarantee sentence added (nothing on file supports it). Decision line added to Q7_EVIDENCE.md recording the column rename.

### Editor (ana-e1 to ana-e11)
- ana-e1 (README:18, "none of these texts" too strong given L-Bank statute not read): accepted, now "none of the texts on file", L-Bank cited to the annual report.
- ana-e2 (§ 1a vs Art. 1a): the changed text uses § 1a throughout; older "Art. 1a" uses elsewhere left as they were.
- ana-e3 (the four could be read as the members of the 1.1%): accepted; "whether each is in the 1.1% is not confirmed" added to README and register notes.
- ana-e4 (English category name): the English name is the one transcribed for table I.7 in sources.md row 18; the label now says "The Bundesbank category" first. No other change.
- ana-e5 (README:15 col. 3 still "promotional banks"): same as ana-48, open, in the proposed card.
- ana-e6 (length): accepted in part; split into four sentences.
- ana-e7 (card id for 2026-11-04 decision): accepted, "cards q7-promo-2, 2026-11-04, and a8-promo, 2026-11-05".
- ana-e8 (input id `promotional_banks_lending_individuals`): kept on purpose (transcription id in national_figures.csv and sources.md); compare.py comment and the Q7_EVIDENCE decision line say so.
- ana-e9 (register id): kept on purpose; register notes now say so.
- ana-e10 (DZ Bank wording in notes): accepted, "The Bundesbank lists DZ Bank in this category … its ownership and guarantee status are not sourced". The 17,817 / 1,551,414 values come from the rerun of compare.py and the test asserts them.
- ana-e11 (voice): no change needed.
