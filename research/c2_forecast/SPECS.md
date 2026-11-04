# C2 specification registry (opened before any C2 score)

> **Claude draft, not the author's text.** This file implements the frozen pre-registration `docs/decisions/scoring-protocol.md` (frozen commit `192d60c`, SHA-256 of the file `2191580fe188ad78543171a94d4d52fea9be5b5546b8bdf60902f31ba7bf678a`; Eleonora's choices of 2026-11-04). It adds only what the protocol leaves to implementation, each marked *[implementation]*. Every specification tried is listed here with its development scores, including abandoned and failed ones, as C3 requires. Deviations from the protocol would go in the protocol's own Deviations section, through the coordinator; there are none.

Opened 2026-11-04, before `forecast.py` produced any score.

## Fixed by the protocol (restated, not changed)
- **Target and horizons.**
  - Target: the cumulative change share(T+h) − share(T), turned back into a level. Errors are in pp of share.
  - h = 1, 4, 8. Direct forecasts, one model per horizon. The AR benchmark is iterated.
- **Estimation window.**
  - Primary: expanding from 1952Q1.
  - Secondary: rolling 80 quarters, which counts in the multiple-testing family.
- **Origins.** The first development origin is T = 1990Q1. Development targets end at 2023Q2. The holdout is 2023Q3–2026Q2 and is untouched: the loader refuses holdout targets unless it is given `--holdout --prereg 192d60c`.
- **Purge and embargo.** A training pair (features at s, target at s+h) is kept only if s+h ≤ T − 4 (e = 4).
- **Data.**
  - Primary: latest vintage (Z.1 of 2026-09-11), labelled *pseudo out-of-sample*.
  - Real-time check: origins at each archived Z.1 release from 2016-09-16, scored against the first release and the latest vintage. Vintages from `research/c1_nowcast/z1_share_vintages.csv`.
- **Benchmarks.**
  - No-change (primary).
  - Drift: h × the mean quarterly change over the estimation window.
  - AR(p) on quarterly changes, p chosen by BIC from 0 to 4 at each origin on training data only, iterated to h.
  - Seasonal naive: descriptive only, unless the development-sample seasonality check passes. The check runs before any scoring.
- **Losses and intervals.**
  - Losses: RMSE (primary) and MAE.
  - Interval scores at 80% and 95%. CRPS where a full predictive distribution exists.
  - Intervals: empirical quantiles of the model's own past out-of-sample errors at the same horizon. Only errors realised by the origin count, purged the same way (target ≤ T − 4). Burn-in: 40 past errors.
- **Coverage.** Clopper–Pearson intervals. At h = 1 also Kupiec and Christoffersen; at h > 1 coverage is descriptive.
- **Tests (development only).**
  - Non-nested pairs: DM with the HLN correction, HAC lag h − 1, t(n − 1).
  - Nested pairs: Clark–West.
  - Holm over {3 horizons} × {candidates} × {no-change, AR}.
  - Holdout results are descriptive.
- **Leakage tests 1–5.** A guard check, plus outcome checks on tests 1 and 5.
- **Decision rule (a).** Lower development RMSE, significant after Holm, and lower holdout RMSE.

## Candidates (at most 3 enter the holdout)

| ID | Family | Specification |
|---|---|---|
| `Z-DIR` | Z | Direct OLS of the h-quarter change on an intercept and the last 4 quarterly changes at s. Fitted on all pairs allowed by purge and embargo. |
| `Z-DAMP` | Z | Damped mean: forecast = m × Σ_{j=1..h} φ^j, where m is the mean of the last 4 quarterly changes at T. φ is chosen from {0, 0.25, 0.5, 0.75, 0.9, 1} by the in-sample h-step squared error on training pairs only. φ = 0 is no-change. |
| `ZC1-DIR` | Z+C1 | `Z-DIR` plus one regressor: C1's accounting-bridge nowcast of the next quarter's change, computed point-in-time at the origin date (the Z.1 release date) with C1's code. Scored only on the origins C1's panel covers: real-time origins from 2016-09-16, plus the pseudo-real-time P2b span (origins from 2015Q1 releases) for the latest-vintage design. If too few training pairs exist (< 12), it is recorded as absent at that origin. |

*[implementation]* `Z-DAMP`'s φ grid, `Z-DIR`'s 4 lags, and `ZC1-DIR`'s minimum of 12 training pairs. All are fixed here, before scoring.

## Nesting (for the choice of test)
- **Against no-change.** Every candidate, the drift and the AR benchmark nest no-change (zero forecast), so Clark–West is used.
- **Against AR.** Candidates are not nested, so DM-HLN is used.

## Specification registry
| ID | Status | Commit | Development scores |
|---|---|---|---|
| `Z-DIR` | candidate | first scored in the commit after 92fed89 | Relative RMSE vs no-change, latest-vintage expanding: h=1: 0.75, h=4: 0.70, h=8: 0.79. `scores_dev.csv`, `tests_dev.csv` |
| `Z-DAMP` | candidate | same | h=1: 0.73, h=4: 0.70, h=8: 0.81 |
| `ZC1-DIR` | candidate (few origins) | same | On its common origins: h=1: 0.80 (n=18), h=4: 1.40 (n=12), h=8: 0.96 (n=4) |

## Process notes and issues for the coordinator (dated)
- **2026-11-04, ordering.** The first development scoring run happened before the leakage tests were written. The protocol says those tests run "before any scoring". The tests were written straight after; all 14 pass and needed no code change, so the scores are unchanged. Recorded here, and reported to the coordinator as a candidate dated deviation, since they own the protocol.
- **2026-11-04, seasonality.** The pre-scoring check (`seasonality.json`, F-test of quarter dummies on quarterly changes, 1952Q2–2023Q2) gives p ≈ 7e-5. Under the protocol, seasonal naive therefore enters the decision rules. The protocol's family definition lists only (no-change, AR). Candidate-versus-seasonal-naive comparisons (DM-HLN) were added to the Holm family, the stricter reading, and this is flagged to the coordinator.
- **2026-11-04, placebo (leakage test 5).** Z-DIR trained on a time-shuffled target "beats" no-change by Clark–West at h = 1 (p = 0.0002) and h = 4 (p = 0.04), with relative RMSE about 0.96. Shuffling keeps the target's mean, so the placebo is close to a drift forecast, and drift is slightly better than no-change. That is not a leak, but the protocol says C2 is not done until the placebo shows no skill. The fix would be to redefine the placebo (demeaned target, or skill measured against drift). That is a protocol question for the coordinator and Eleonora, not changed here.

## Proposed deviations (for Eleonora; the C2 protocol is frozen, so they are hers to decide)
Status of each: **PROPOSED**, not in force. The coordinator queued all three for her review (2026-11-04).

- **PROPOSED, dated 2026-11-04: order of leakage tests and first scoring.** "The protocol requires the leakage tests to run before any scoring. On 2026-11-04 the first development scoring run of `forecast.py` came before `test_forecast.py` existed. The tests were written immediately afterwards. All 14 passed with no change to `forecast.py`, so the development scores were not affected. The holdout was not opened. Future runs execute the tests first (the pre-commit hook runs them)."
- **PROPOSED, dated 2026-11-04: seasonal naive in the Holm family.** "The pre-scoring seasonality check (`seasonality.json`: F-test of quarter dummies on quarterly changes, 1952Q2–2023Q2, p ≈ 7e-5) triggers the protocol's rule that seasonal naive enters the decision rules. Its comparisons with each candidate (DM-HLN, non-nested) are added to the Holm family, which grows from 36 to 42 tests: the stricter reading." Kept in force for now, as the coordinator asked, pending her decision.
- **Placebo (leakage test 5): nothing changed.** The result is in `placebo_dev.json`: "skill" over no-change at h = 1 and 4. The options listed for her are (a) demean the shuffled target, (b) measure placebo skill against drift, and (c) keep the definition and record a failure. **They were stated after the placebo result was seen**, so she can weigh that. Until she rules, C2 stays open and the holdout stays sealed.
