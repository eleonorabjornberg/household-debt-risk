# Track: Markets and nowcast

Branch: `claude/track-markets` · Tasks, in order: B1, C1 · Rules: PLAN.md "Parallel tracks".

## Status
| Task | Status | Notes |
|---|---|---|
| B1 | ready for review | `research/b1_market_pricing/`. Spec fixed in `METHOD.md` before results (commit b094579, before results a8fc3de). Verdict under the pre-set rule: no robust association in every variant; levels fits fail Engle–Granger, the positive levels sign comes from the 2022-11 PMMS method change, and the test has little power, so the README reads "inconclusive". quant-reviewer and skeptic run; 12 of 13 objections resolved, 1 open (g-fee control: a design extension, below). 46 register rows in `claims/tracks/markets.csv`. |
| C1 | blocked (Eleonora: evaluation design, Q-C1 below) | Plumbing done: `research/c1_nowcast/` point-in-time panel `pit.panel(t)`, `release_lags.csv`, `z1_calendar.csv`, candidate inputs, sources with hashes, offline no-look-ahead tests. No nowcast computed or evaluated. |

## Log notes for the coordinator
**Session 2026-11-04 (markets track).**
- Environment: `FRED_API_KEY` set, `DATABASE_URL_READONLY` set, `DATABASE_URL` set, `ANTHROPIC_API_KEY` unset. No database used (B1 and C1 read Z.1 and FRED directly). Not reachable: `alfred.stlouisfed.org` (the API host `api.stlouisfed.org` works and serves vintages), `www.freddiemac.com`, `www.fanniemae.com`, `www.sifma.org`.
- B1: method note first, then `b1.py` (OLS with Newey–West HAC in numpy; matches statsmodels to machine precision in `test_b1.py`). Added `research/common/fred.py` (cached FRED/ALFRED client, SHA-256 manifest, units-by-vintage rescaling), shared by B1 and C1.
- C1: point-in-time plumbing, release-lag table, Z.1 calendar from ALFRED, Fed Z.1 archive probed for older target vintages.
- Subagents: quant-reviewer on B1 (about 37k tokens, 9 tool calls), skeptic on B1 (about 52k tokens, 13 tool calls), quant-reviewer on C1 plumbing (see below once run).
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

## Questions for Eleonora
(Design choices are hers. List each with the options and a recommendation; do not proceed on that point until she answers.)

### Q-B1. Accept B1 as specified, and whether to extend it
The specification in `research/b1_market_pricing/METHOD.md` (proxies, controls, levels and differences, reading rule) was Claude's proposal, fixed before results so that the result could not steer it.
- (a) Accept as is; B1 closes as "inconclusive, low power".
- (b) Add a guarantee-fee control from FHFA's annual g-fee reports (free, 2009+), as a new pre-specified variant (open objection mkt-q4).
- (c) Add a pre-2017 jumbo proxy backed out of FHFA MIRS (assumption-heavy).
- **Recommendation: (a), with (b) as a small follow-up if B1 numbers will feed A6.** (c) adds assumptions faster than evidence.

### Q-C1. Nowcast evaluation design (nothing is computed until you choose)
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
6. **Metrics, sample and holdout.** RMSE and MAE in percentage points, each relative to no-change; Diebold–Mariano with HAC errors (reported as descriptive, given about 60 quarters); sign accuracy of the change. Rolling origin from 2010Q2 (ALFRED's first household-total vintages) with the last eight quarters (2024Q3–2026Q2) untouched as holdout. **Recommendation: as listed; coordinate with the C2 scoring protocol the coordinator is drafting, so C1 and C2 share one protocol.**
7. **Share definition.** (a) the headline share (mortgages + consumer credit); (b) mortgage-only. **Recommendation: (a)**, the project's quantity.
8. **Seasonal adjustment.** NSA throughout (Z.1 holder levels are NSA; `HMLBSHNO` and `CCLBSHNO` used rather than the SA `HHMSDODNS`). **Recommendation: NSA.**

## Proposed changes to shared files
(PLAN.md, register, README, site copy: describe or attach a patch; the coordinator applies them.)
1. **PLAN.md B1 row → done** once the coordinator's review agrees: "inconclusive, low power; no robust association under the pre-set rule; `research/b1_market_pricing/`".
2. **PLAN.md C1 row → blocked (Eleonora: evaluation design)**, with the plumbing noted.
3. **PLAN.md Environment prerequisites:** add `www.freddiemac.com` and `www.fanniemae.com` as not reachable on 2026-11-04 (needed for C1 option 2c); note `alfred.stlouisfed.org` blocked but `api.stlouisfed.org` sufficient.
4. **claims/check_register.py:** the scan drops the leading sign when matching, so a README that prints the wrong sign passes. Suggest a sign-aware comparison (or a warning) for rows whose `value` is negative.
5. **Review-log ids:** suggest a track infix (`R-<date>-<track>-<n>`) in the skeptic and quant-reviewer agent definitions, so parallel tracks cannot collide.
6. **claims/tracks/markets.csv:** 46 B1 rows to move into the register on merge.
