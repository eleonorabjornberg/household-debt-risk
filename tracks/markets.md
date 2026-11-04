# Track: Markets and nowcast

Branch: `claude/track-markets` · Tasks, in order: B1, C1 · Rules: PLAN.md "Parallel tracks".

## Summary at stop (2026-11-04)
**B1** is ready for the coordinator's review. Under the rule fixed in advance, every variant shows no robust association. The honest reading is "inconclusive, low power". Eleonora accepted it as specified (Q-B1 (a)).
**C1** has its development-sample evaluation done, under Eleonora's design, with a spec committed before any score. Results so far:
- The accounting bridge has about a quarter lower RMSE than no-change, but the difference is not significant after Holm, and the bridge is biased downward. Under C2's wording that is "comparable", not "beats".
- The bridge regression does better, on few forecasts.
- The holdout has not been run. It waits on the coordinator's ruling on the C1/C2 holdout conflict.
Nothing touched production or the database.

## Status
| Task | Status | Notes |
|---|---|---|
| B1 | ready for review | `research/b1_market_pricing/`. Spec fixed in `METHOD.md` before results (commit b094579, before results a8fc3de). Verdict under the pre-set rule: no robust association in every variant; levels fits mostly fail Engle–Granger, the positive levels sign coincides with the period from 2022Q4 on (PMMS method change and other conditions), and the test has little power, so the README reads "inconclusive". quant-reviewer and skeptic run; 12 of 13 objections resolved, 1 open (g-fee control: a design extension, below). 46 register rows in `claims/tracks/markets.csv`. |
| B2 | ready for review (pending skeptic) | `research/b2_crt_pricing/` (e63d889). FHFA Dec 2016 deal-level credit costs, 47 deals 2013–16; zero-attach median 32 bps a year, about 6.4× FHFA's own baseline expected loss. 2017+ prices chart-only; GSE/SEC deal data blocked. Method choices for Eleonora: Q-B2. |
| C1 | ready for review (development sample); holdout run waits on Q-C1c | Spec `EVALUATION.md` (7ae4afb) before any score; deviations dated there. Real-time Z.1 from all 41 archived releases (2017-03-09 in folder 20170305). Development result (99d56cd): accounting bridge RMSE about 0.74 of no-change, not significant after Holm, biased downward (mostly 2020–21); bridge regression better on its own 2019Q3–2023Q2 targets, Holm-significant at k = 1 and 2 only. quant-reviewer (q11–q16) and skeptic (s9–s15) run and addressed; one minor stated limitation open (s12). |

## Log notes for the coordinator
**Session 2026-11-04 (markets track).**
- Environment: `FRED_API_KEY` set, `DATABASE_URL_READONLY` set, `DATABASE_URL` set, `ANTHROPIC_API_KEY` unset. No database used (B1 and C1 read Z.1 and FRED directly). Not reachable: `alfred.stlouisfed.org` (the API host `api.stlouisfed.org` works and serves vintages), `www.freddiemac.com`, `www.fanniemae.com`, `www.sifma.org`.
- B1: method note first, then `b1.py` (OLS with Newey–West HAC in numpy; matches statsmodels to machine precision in `test_b1.py`). Added `research/common/fred.py` (cached FRED/ALFRED client, SHA-256 manifest, units-by-vintage rescaling), shared by B1 and C1.
- C1: point-in-time plumbing, release-lag table, Z.1 calendar from ALFRED, Fed Z.1 archive probed for older target vintages.
- Subagents: quant-reviewer on B1 (about 37k tokens, 9 tool calls), skeptic on B1 (about 52k tokens, 13 tool calls), quant-reviewer on C1 plumbing (sonnet, about 44k tokens, 7 tool calls): no look-ahead leak found; 5 objections (mkt-q6 to q10), code fixes for q8 and q9, the rest folded into Q-C1 below.
- **Errors and who caught them:**
  1. B1 README called the positive levels coefficient a finding although the levels residuals fail Engle–Granger. *Caught by quant-reviewer* (R-20261104-mkt-q1). Fixed.
  2. B1 README said the coefficient "loses significance" before the PMMS change; it actually flips sign. *Caught by quant-reviewer and skeptic* (mkt-q2, mkt-s1). Fixed.
  3. B1 headline "no association" overstated a low-power test. *Caught by skeptic* (mkt-s4) *and quant-reviewer* (mkt-q3). Now "inconclusive", with the power bound.
  4. B1 register rows dropped minus signs in `display`, mixed vintages, used catalog-level instead of cell-level series ids. *Caught by skeptic* (mkt-s8). Rows regenerated; signs checked by script, because `check_register.py` and `claim-check` ignore signs (proposal below).
  5. B1 public share counted Ginnie Mae (FHA/VA) pools that PMMS does not price. *Caught by skeptic* (mkt-s2). Fannie+Freddie-only share added as a declared post-hoc check.
  6. Both reviewers numbered their entries R-20261104-1…, colliding with each other and potentially with other tracks. *Caught by Claude (main session)*. Renumbered R-20261104-mkt-q*/s*.
  7. C1: ALFRED's units label switches from billions to millions mid-history (G.19 2025-02-07, Z.1 on FRED 2026-01-09), which made every revision look like 99.9%. *Caught by Claude (main session)* from the revision column of the first lag table. Fixed by rescaling each row by the units label in force when it was published (no look-ahead), with a test.
  8. C1: back-filled history (old dates added when a series is extended) showed up as lags of decades. *Caught by Claude (main session)*. Lags now count only observations that were the newest date in their first vintage, with a test.
  9. C1 draft attributed the late 2026-01-09 Z.1 release to the 2025 shutdown without a source. *Caught by Claude (main session)* on reread. Reworded to the observed date only.
  10. B1 (and any use of A1's holder cells before 1987): in 1974Q3–1986Q3 the Z.1 pool sub-series (FL413065110/123/133/143) sum to more than the pool total FL413065105 (by about $14.6B in 1980Q4), so cell-based shares are overstated there and step at 1986Q4. B1's first three sample quarters were affected; its first-differences estimate moved from −0.08 to −0.57 (verdict unchanged). *Caught by Claude (main session)* when C1's vintage test compared the archived share with the A1-cell share over 1952–2026. B1 now uses catalog-level shares as validation does. A1's own 2007–11 results are not affected.

**Session 2026-11-04, continued (after Eleonora's decisions).**
- Verified the coordinator's message against PLAN.md "Decisions taken" at a590475 before acting.
- Reported to the coordinator (send_message), not resolved here: (1) holdout conflict, C1 2024Q3+ vs frozen C2 2023Q3+; handled by cutting at 2023Q2; (2) C2's fact check says pre-2016-09 releases are HTML/PDF only, but `z1r-N.zip` text archives exist 2010–2016 (holder-table coverage unverified); (3) the A1 pool sub-series issue (item 10).
- Fed archive downloads: Python's urllib got 403 from www.federalreserve.gov, while plain curl and `requests` (the client `validation/run.py` already uses) got 200; switched to `requests`, no user-agent change. The 2017-03-09 release has no CSV zip: recorded as absent.
- Precision bug: z1_cells.csv was first written with 6 significant digits, which broke the base-share identity by about 1e-7. *Caught by Claude (main session)* through the assert in `nowcast.run`. Fixed (12 digits).
- Subagents this part: quant-reviewer on C1 (about 72k tokens, 21 tool calls; 6 objections, 2 major), skeptic on C1 (about 113k tokens, 38 tool calls; 7 objections, 2 major). Errors they caught: double-counted targets at k = 3 (quant-reviewer q11); the bridge regression compared on different targets from the bridge (q12, s11); the '2017-03-09 release missing' claim, which was wrong: it is in folder 20170305 (skeptic s9); wrong dates in sources.md (s14).
- Coordinator's quant review of B1 (coord-q1..q4) caught: a false 'every row fails EG' sentence (major), a 95% half-width presented as power, a causal attribution from post-hoc variants, and the correction missing from METHOD.md. All fixed (dc68eb7).
- Merge of the coordinator branch (1c51735): its folded register rows for b1/c1 were stale; c1 rows replaced in place, b1 rows moved back to `claims/tracks/markets.csv` (flagged to the coordinator).

## Questions for Eleonora
(Design choices are hers. List each with the options and a recommendation; do not proceed on that point until she answers.)

### Q-B1. Accept B1 as specified, and whether to extend it
**Answered 2026-11-04 by Eleonora: (a)**, with a g-fee control only if B1 feeds A6 (PLAN.md "Decisions taken", a590475).
The specification in `research/b1_market_pricing/METHOD.md` (proxies, controls, levels and differences, reading rule) was Claude's proposal, fixed before results so that the result could not steer it.
- (a) Accept as is; B1 closes as "inconclusive, low power".
- (b) Add a guarantee-fee control from FHFA's annual g-fee reports (free, 2009+), as a new pre-specified variant (open objection mkt-q4).
- (c) Add a pre-2017 jumbo proxy backed out of FHFA MIRS (assumption-heavy).
- **Recommendation: (a), with (b) as a small follow-up if B1 numbers will feed A6.** (c) adds assumptions faster than evidence.

### Q-C1. Nowcast evaluation design
**Answered 2026-11-04 by Eleonora: the recommendation on items 1–9** (a590475). Item 6 must agree with the frozen C2 protocol; the holdout conflict is with the coordinator. Implemented in `research/c1_nowcast/EVALUATION.md`.
1. **Target vintage** (what the nowcast is scored against).
   (a) the first-release share, as first published in Z.1 for that quarter; (b) the latest vintage (Z.1 of 2026-09-11); (c) both, one primary.
   **Recommendation: (c) with (a) primary.** The nowcast stands in for the first release, and holder series revise. Needs the Fed archive parsed for 2010–2018 releases (ALFRED holder series start 2019).
2. **Indicator set** (fixed before any evaluation).
   (a) minimal: G.19 federal-government and total consumer credit, mortgage side carried forward from the last Z.1; (b) (a) plus G.19 private holders and H.8 bank residential and consumer loans; (c) (b) plus agency monthly summaries (Ginnie Mae now; Freddie and Fannie need `www.freddiemac.com` and `www.fanniemae.com` allowed).
   **Recommendation: (b) now, (c) as a second pre-registered run if the hosts are added.** Keeps the set small and fixed.
3. **Nowcast instants.**
   (a) monthly, on a fixed day (e.g. the 15th); (b) weekly, after each H.8; (c) three fixed points per quarter (1 month, 2 months after quarter end, day before Z.1).
   **Recommendation: (a).** Each quarter's share is then nowcast about twice before Z.1 publishes it, which is enough to see the G.19 information arrive, without weekly instants inflating the sample with near-duplicates.
4. **Model.**
   (a) accounting bridge: move each Z.1 component with its higher-frequency counterpart's growth since the last Z.1 quarter, recompute the share, no estimated parameters; (b) bridge regression of the change in share on indicator growth, estimated on a rolling window; (c) both, (a) primary.
   **Recommendation: (c).** (a) is transparent and cannot overfit; (b) is the challenger.
5. **Benchmarks.** No-change (last published share); random walk with drift (mean of the last four quarterly changes); AR(1) on the quarterly change. **Recommendation: all three, no-change as the headline comparison.**
6. **Metrics, sample and holdout.** RMSE and MAE in percentage points, each relative to no-change; sign accuracy of the change; for the tests, Diebold–Mariano with HAC errors against non-nested benchmarks and Clark–West against nested ones (the AR and bridge regressions nest no-change), all reported as descriptive given the small sample. Benchmarks are built from as-of data too (the last *published* share, not the final vintage). The holdout is the last eight quarters (2024Q3–2026Q2), untouched, and written into the pre-registration before any run.
   **Sample start depends on option 2** (quant-reviewer mkt-q6): ALFRED vintages begin 2008-10 (G.19 government, finance companies, credit unions), 2010-06 (Z.1 household totals), 2012-06 (G.19 depository institutions), 2012-08 (H.8 consumer loans), 2015-02 (H.8 residential real estate), 2019-03 (Z.1 holder series). So: option 2a can start 2010Q2; option 2b only 2015Q1 (about 38 evaluation quarters before the holdout); target option 1a before 2019 needs the Fed archive parsed. The alternative of starting 2b earlier with missing inputs treated as absent (model drops them) is possible but makes the indicator set change over time.
   **Recommendation: 2b from 2015Q1, with 2a from 2010Q2 as a longer-sample comparison; coordinate with the C2 scoring protocol the coordinator is drafting, so C1 and C2 share one protocol.**
9. **Definition of the quarterly change being nowcast** (mkt-q7). (a) first-release share of quarter q minus the share of q−1 *as published in the same Z.1*; (b) minus the q−1 share as previously published. **Recommendation: (a)**, so revisions to q−1 are not scored as nowcast error; the bridge growth rates use the same rule (same-vintage growth).
7. **Share definition.** (a) the headline share (mortgages + consumer credit); (b) mortgage-only. **Recommendation: (a)**, the project's quantity.
8. **Seasonal adjustment.** NSA throughout (Z.1 holder levels are NSA; `HMLBSHNO` and `CCLBSHNO` used rather than the SA `HHMSDODNS`). **Recommendation: NSA.**

### Q-B2 (new). B2 method and scope
1. **Price measure.**
   (a) FHFA's estimated credit cost ÷ the baseline expected loss of the sold slice, under FHFA's own scenario (as built);
   (b) cost ÷ a loss distribution (several scenarios), which needs assumptions FHFA does not publish;
   (c) cost alone, with no multiple.
   **Recommendation: (a)**, plus (c) alongside. The multiple is labelled as relative to FHFA's baseline only.
2. **2017–2023 prices.**
   (a) read issuance spreads off FHFA's Appendix D/E charts, with a stated reading error, labelled estimates;
   (b) leave the gap;
   (c) get deal data from crt.freddiemac.com (needs the host allowed) and EDGAR (needs `SEC_USER_AGENT` set in this environment).
   **Recommendation: (c) if you can add the host and variable; otherwise (b).** Chart reading adds error that the register cannot verify.

### Q-C1c (new). When to run the C1 holdout
C1 and C2 share the holdout 2023Q3–2026Q2, and C2's Family Z+C1 uses C1's indicators. Scoring C1 on the holdout now would show holdout outcomes before C2's candidates are frozen, which could steer C2's design.
- **Options:** (a) run the C1 holdout now; (b) run it in the same single run as C2's holdout, after C2's candidates are frozen; (c) keep it unrun until C3.
- **Recommendation: (b).** Both holdouts are then seen once, by frozen models. Until then C1 reports development results only.

### Q-C1b (new, for later). Indicator set 2c as a second pre-registered run
The development results show the bridge biased downward. A likely cause is that public mortgage holders have no monthly indicator in 2b.
- **Hosts now reachable:** `www.freddiemac.com` (per the coordinator) and ginniemae.gov. Fannie Mae still returns 403.
- **Options:** (a) pre-register a 2c run with the Freddie Mac and Ginnie Mae monthly summaries, Fannie carried flat; (b) wait until Fannie is reachable; (c) no 2c run.
- **Recommendation: (a)**, frozen before it is scored. It must not modify the current run.

## Proposed changes to shared files
(PLAN.md, register, README, site copy: describe or attach a patch; the coordinator applies them.)
1. **PLAN.md B1 row → done** once the coordinator's review agrees: "inconclusive, low power; no robust association under the pre-set rule; `research/b1_market_pricing/`".
2. **PLAN.md C1 row → blocked (Eleonora: evaluation design)**, with the plumbing noted.
3. **PLAN.md Environment prerequisites:** add `www.freddiemac.com` and `www.fanniemae.com` as not reachable on 2026-11-04 (needed for C1 option 2c); note `alfred.stlouisfed.org` blocked but `api.stlouisfed.org` sufficient.
4. **claims/check_register.py:** the scan drops the leading sign when matching, so a README that prints the wrong sign passes. Suggest a sign-aware comparison (or a warning) for rows whose `value` is negative.
5. **Review-log ids:** suggest a track infix (`R-<date>-<track>-<n>`) in the skeptic and quant-reviewer agent definitions, so parallel tracks cannot collide.
6. **claims/tracks/markets.csv:** 46 B1 rows to move into the register on merge.
