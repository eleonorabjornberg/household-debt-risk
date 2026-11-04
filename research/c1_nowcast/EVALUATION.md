# C1 evaluation specification (committed before any nowcast was scored)

> **Claude draft, not the author's text.** The design choices are Eleonora's, taken 2026-11-04: she accepted the recommendations in `tracks/markets.md` Q-C1, items 1–9 (PLAN.md "Decisions taken", coordinator commit a590475). Claude filled in the mechanical details needed to run them. Those are marked *[implementation]*, and any of them can be overruled. This file was committed before `nowcast.py` produced any score. Changes after that go under "Deviations", with a date.

The design must agree with the frozen C2 protocol (`docs/decisions/scoring-protocol.md`, 192d60c, on the coordinator's branch). Conflicts are reported to the coordinator, not resolved here (see "Open conflicts").

## Target and vintages (items 1, 7, 9)
- **Quantity.** The headline public share of household mortgages and consumer credit, computed as `validation/run.py` computes it (public holders at catalog level; mortgages apportioned with FL153165105 / FL893065105).
- **What is nowcast.** The change in the share from the last published quarter T to the next quarter q = T+1.
- **Primary target: first release.** share(q) in the first Z.1 that contains q, minus share(T) in that same release (item 9a, same-vintage). Source: `first_release.csv` and `z1_share_vintages.csv` (Fed release archive, 2016-09-16 onward).
- **Secondary target: latest vintage.** The same change, both quarters from the 2026-09-11 release.
- **Missing release.** A release with no archived CSV would leave its quarter without a first-release target, and its nowcasts recorded as absent. None is missing after the 2017-03-09 fix (see Deviations).

## Instants and information sets (items 2, 3)
- **Instants.** The 15th of every month *[implementation: the fixed day]*. A nowcast "at t" uses everything published by the end of day t (`pit.as_of`).
- **Base and target.** At t, R is the latest Z.1 release on or before t, T is R's last quarter, and the target is q = T+1. The instant index k = 1, 2, 3 counts instants since R. A fourth instant, when one occurs before the next release, was pooled with k = 3 *[implementation]*; replaced, see Deviations.
- **Indicator set 2b (primary).**
  - G.19: `TOTALGOV` (federal government), `TOTALDI` (depository institutions), `TOTALFC` (finance companies), `TOTALTCU` (credit unions), `TOTALNS` (total).
  - H.8: `RREACBW027NBOG` (bank residential real-estate loans).
  - All NSA (item 8), read as of t from ALFRED and rescaled to millions by the units label of the day.
- **Indicator set 2a (comparison).** `TOTALGOV` and `TOTALNS` only.

## Models (item 4)
- **Accounting bridge (primary; no estimated parameters).** Start from R's household-apportioned cells at T (`z1_vintages.CELLS`). Each mapped cell is moved by its indicator's growth, and the share is recomputed.
  - *Growth.* g = I(latest period ≤ end of q available at t) / I(last period ≤ end of T). Both values come from the same as-of(t) vintage, per item 9 and quant-reviewer mkt-q8. Monthly series use the month; H.8 uses the latest Wednesday.
  - *No newer data.* If no indicator period after T is available yet, g = 1.
  - *Mapping under 2b:*
    - `cc_federal` ← `TOTALGOV`
    - `cc_depository` ← `TOTALDI`
    - `cc_finance` ← `TOTALFC`
    - `cc_credit_unions` ← `TOTALTCU`
    - total consumer credit ← `TOTALNS`, with `cc_other_private` as the residual
    - `mort_banks` ← `RREACBW027NBOG`
    - every other cell carried at its T level
  - *Mapping under 2a:* `cc_federal` ← `TOTALGOV`, total consumer credit ← `TOTALNS`, other consumer-credit cells scaled with the residual, all mortgage cells carried.
  - *[implementation: the cell–indicator mapping above.]*
- **Bridge regression (challenger).** Δ_actual = a + b·Δ_bridge, fitted separately for each k by OLS. It uses only past pairs whose target was already published at t; there is no other purge, since real-time vintages make an embargo unnecessary. It needs at least 12 past pairs, otherwise it is recorded as absent *[implementation: the minimum]*.

## Benchmarks (item 5)
All benchmarks are computed from R only, so they use as-of data:
- **No-change:** Δ = 0. This is the headline comparison.
- **Drift:** the mean of R's last four quarterly changes.
- **AR(1) on quarterly changes:** fitted by OLS on R's full history, 1952Q2 to T (expanding window, as in C2's primary design; the order is fixed at 1, see Deviations).

## Metrics and tests (item 6, aligned with C2)
- **Losses.** RMSE (primary) and MAE, in pp of share. Each is also reported relative to no-change. Sign accuracy of the change is reported too.
- **Breakdown.** Every loss is reported by instant index k, and pooled.
- **Tests.** Run on the development sample, separately for each k, one target per quarter, HAC lag 0 (h = 1 within each k).
  - Non-nested pairs (the accounting bridge against each benchmark): DM with the Harvey–Leybourne–Newbold correction, t(n−1).
  - Nested pairs (bridge regression, drift and AR(1) against no-change): Clark–West.
  - Holm correction over the primary family: {bridge, bridge regression} × {no-change, AR(1)} × k ∈ {1, 2, 3}.
  - All p-values are descriptive given the sample size.
- **Wording.** "Beats" follows C2's decided rule (a): lower RMSE on development, significant after Holm, and lower in the holdout. "Comparable" and "does not beat" also follow C2.

## Samples and holdout
- **RT, real time (primary).**
  - Z.1 base from the release archive, indicators from ALFRED, target first release.
  - Development targets run 2016Q3–2023Q2.
- **P2b, pseudo-real-time.**
  - Z.1 from the latest vintage, cut at T. This is *not real-time* for Z.1, and is labelled so as C2 requires.
  - Indicators are point-in-time; the target is the latest vintage.
  - Development targets run 2015Q1–2023Q2.
- **P2a, pseudo-real-time.** As P2b, with indicator set 2a. Development targets run 2010Q2–2023Q2.
- **Holdout: 2023Q3–2026Q2** (see Deviations). Untouched by every script run until the holdout run. Targets after 2023Q2 are neither scored nor printed: the loader drops them unless `--holdout` is passed.

## Leakage guards (from C2's tests 1–4, applied to C1)
- **Availability check.** Every datum carries `available_at` (ALFRED `realtime_start`, or the Z.1 release date). `nowcast.guard` raises if any datum used at t has `available_at > t`.
- **Leakage tests (pytest).** They show the guard raises in three cases:
  - (1) the target's first release is fed in as an indicator;
  - (2) a latest-vintage series is used in place of the as-of read;
  - (3) a value is published one day after t.

## Open conflicts (reported to the coordinator 2026-11-04)
- **Holdout start:** resolved 2026-11-04 in C2's favour (2023Q3); see Deviations.
- **Archive depth:** C2's fact check says releases before 2016-09 are HTML/PDF only. In fact `z1r-N.zip` text archives exist for 2010–2016; whether they carry the holder tables is unverified. RT therefore starts at 2016-09.

## Deviations
- **2026-11-04, holdout ruling** (coordinator commit 66adeff; PLAN.md "Decisions taken": "C1's holdout follows the frozen C2 protocol (2023Q3–2026Q2), not 2024Q3", Eleonora's rule, Claude's application). The C1 holdout is now 2023Q3–2026Q2. No score changes: development already stopped at 2023Q2. The holdout run happens once, after review.
- **2026-11-04, tests:** aligned exactly with C2 (DM with HLN, Clark–West for nested pairs, holdout descriptive only), as specified above. No change.
- **2026-11-04, after the first development scores, in response to quant-reviewer (q11–q16) and skeptic (s9–s15).** Each changes the development scores. The original scores are in commit 58a93d8.
  - *One row per target and k* (q11, s13). The spec said a fourth instant "is pooled with k = 3", which counted some targets twice and broke "one target per quarter". A fourth instant is now k = 4. It is kept in `nowcasts_dev.csv` but neither scored nor tested.
  - *Missing release was not missing* (s9). The 2017-03-09 release is archived in folder `20170305`. `z1_vintages.FOLDER_OVERRIDE` maps it, and an assert checks that its last quarter is 2016Q4. 2016Q4 now has a first-release target, and the six instants based on that release are scored.
  - *Like-for-like comparison* (q12, s11). The bridge is also scored on exactly the bridge regression's targets (`bridge_on_reg_targets`). Reported, not tested.
  - *Post-hoc test sensitivity* (q14). DM with a Newey–West lag-1 variance (`posthoc_dm_hac1_p`), because errors at consecutive quarters are autocorrelated within each k. Reported beside the pre-specified lag-0 test. It is not used for wording.
  - *Declared differences from C2* (q15).
    - (i) The AR benchmark is a fixed AR(1), as Eleonora decided for C1 (Q-C1 item 5). C2 chooses the order by BIC, so "as in C2" above refers only to the expanding window.
    - (ii) In the pseudo-real-time samples the bridge regression trains on latest-vintage (revised) targets, with no embargo. That is a further reason they are labelled *not real-time*.
    - (iii) C2's leakage test 4 (fit window) is covered only by the assert that each benchmark's history ends at T. Test 5 (placebo on a shuffled target) and the outcome checks are not implemented for C1. C2 will implement them.
  - *Deterministic column order* in `nowcasts_dev.csv` (q16).
- **2026-11-04, archive depth:** the coordinator confirmed that `z1r-N.zip` archives exist before 2016-09 and recorded a factual correction in C2. The real-time window still starts 2016-09-16. Extending it would need a new deviation before any score.
