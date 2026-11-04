# Pre-registration: C2 scoring protocol for the public-share forecast

> **Claude draft, not the author's text.** Options for Eleonora to choose; nothing here is decided until she records it.

Status: draft (2026-11-04). Not frozen. No C2 forecast, fit or score exists yet. When the choices are made, freeze it as the `preregister` skill says: commit this file on its own as `prereg: C2 (frozen)`, then record the hash here.

Each design choice is a `CHOICE:` line with options. "(Claude recommends)" marks one option. It is a suggestion, not a decision.

## Question

How well can the public share of US household mortgage and consumer debt be forecast 1, 4 and 8 quarters ahead? And does any model do better than simple benchmarks, in a way that holds up out of sample?

The share is the one `validation/run.py` recomputes. Public mortgage holdings are apportioned to household mortgages (`FL153165105`) by each holder's share of total mortgages (`FL893065105`). Public consumer-credit holders are added. The sum is divided by the scope total `FL154104015`. "Public" is the `public: true` risk buckets in `pipeline/series_catalog.yaml`.

## Hypotheses

- **H1.** At horizon h, the candidate model's loss is lower than the no-change benchmark's.
- **H2.** The candidate model's loss is lower than the AR benchmark's.
- **H3.** The candidate's 80% and 95% intervals cover at their nominal rates.
- **Support:** the decision rules below are met. **Null:** loss differences are inside the noise, or they change sign between the development sample and the holdout. **Against:** the benchmark wins on the primary loss in both samples.
- A null is a result. C3 reports it with the same weight as a win.

## Data and vintages

What exists, stated plainly:

- **Z.1, latest vintage.** `data/validation/FRB_Z1_csv.zip`, `Z1.csv` dated 2026-09-11. Quarterly from 1952Q1 to 2026Q2: 298 quarters. Levels are in $ millions, end of quarter, not seasonally adjusted (catalog header).
- **Z.1, one earlier vintage.** `data/validation/prev_z1_csv_files.zip`. These are the Fed's archived per-table files for the 2026-06-11 release, ending 2026Q1. `validation/zparse.py` reads them. Validation check F2 found public-share revisions between the two vintages of at most 0.021 pp (`validation/REPORT.md`). That is two vintages, not a revision history.
- **No Z.1 vintage archive in the repo.** The Fed keeps per-release folders (`releases/z1/<YYYYMMDD>/`). The June 2026 folder works. How far back these folders have usable CSVs is **not verified**. The public share is not a FRED series, so ALFRED has no vintages of the target. Some Z.1 aggregates are on FRED/ALFRED. Whether every component series is there, and from when, is **not verified**.
- **C1 inputs.** G.19, H.8 and `WSHOMCB` have ALFRED vintages (per PLAN C1). C1 is still to be built. Its release-lag table will set when each input can be used.
- **Known breaks.** The validation suite lists breaks at 1968Q1, 1977Q1, 2006Q1 and 2010Q1. This file does not interpret them. That is A4's job.
- **Timing.** Z.1 for quarter T is released about ten weeks after T ends (2026Q2 came out on 2026-09-11). The next release is expected on 2026-12-10, with 2026Q3.

**Origin.** A forecast origin is a Z.1 release date. T is the latest quarter in that release. Horizon h means quarter T+h. So h=1 is the quarter in progress or just ended, close to a nowcast. Horizons are counted from T whether or not C1 indicators are used. That keeps the protocol the same with or without C1.

**Model families.** Family Z uses Z.1 history only. Family Z+C1 adds C1 indicators, read point-in-time. Family Z+C1 is scored only on origins covered by C1's point-in-time panel. If C1 yields no usable indicator, Family Z+C1 is recorded as absent, not filled with a default.

## Method

**CHOICE: target.**
- (a) The level of the share at T+h. Simple to read. Errors are in pp.
- (b) The cumulative change, share(T+h) − share(T), turned back into a level for scoring. (Claude recommends.) Changes are closer to stationary. Within one vintage the level error and the change error are the same number, so nothing is lost. Across vintages they differ: see the revisions choice.
- (c) As (b), but modelled on the log-odds of the share, so forecasts and intervals stay between 0 and 1. More correct near the edges. Harder to explain. The share is now far from 0 and 1, so the gain is small.

**Horizons.** 1, 4 and 8 quarters. Fixed. Direct forecasts, one model per horizon, unless a model is iterated by construction (the AR benchmark: see below).

**CHOICE: estimation window.**
- (a) Expanding: each origin uses all data back to 1952Q1. Most data. Slow to adapt after a regime change, such as 2008.
- (b) Rolling, 80 quarters (20 years). Adapts. Fewer observations. The window length is a tuning choice in its own right.
- (c) Expanding as the primary design, plus rolling 80 quarters as one declared secondary that counts in the multiple-testing family. (Claude recommends.)

**CHOICE: first evaluation origin.** Development origins run from this date up to the holdout.
- (a) 1985Q1. About 130 training quarters at the first origin. Most origins. Spans the 1980s rise of agency MBS.
- (b) 1990Q1. (Claude recommends.) A round post-1980s start. Still about 130 origins at h=1 before the holdout. Close to where ALFRED coverage of many C1-type inputs plausibly begins (not verified).
- (c) 2000Q1. Closest to today's market structure. Only about 90 origins, and the 2008 shift weighs heavily on them.
Family Z+C1 starts where C1's panel starts. Every model comparison uses the common set of origins of the models compared.

**CHOICE: purge and embargo.** At origin T, a training pair for horizon h is (features at s, target at s+h).
- *Purge* (fixed, not a choice): keep a pair only if s+h ≤ T. That means only targets already published at the origin. Without it, targets at multi-step horizons overlap the period being forecast, and the model learns from the future. The purge removes the last h quarters of feature rows.
- *Embargo*: drop e more quarters, s+h ≤ T−e. Recent Z.1 quarters are the ones most revised, and in a latest-vintage backtest they carry revisions that were not known at the time.
  - (a) e = 0. Purge only. Most data. Assumes recent revisions do not matter.
  - (b) e = 1, one release cycle. A small guard.
  - (c) e = 4. (Claude recommends.) A year of guard costs under 3% of training data at a 1990 origin. That Z.1 revisions are concentrated within about a year is a working assumption, **not verified**.

**CHOICE: real-time vs latest-vintage data.**
- (a) Latest vintage everywhere. A pseudo out-of-sample test. Labelled as such. Overstates real-time accuracy by an unknown amount.
- (b) Build a real-time Z.1 archive from the Fed's release folders, score against the first release, and use it as far back as the folders allow. Most honest. The depth of the archive is unknown, and building it is extra work (a source-provenance task).
- (c) Both. (Claude recommends.) Latest vintage is the primary design over the full sample. A real-time check runs over whatever window archived vintages cover, even if short. Every forecast filed from now on is kept and scored against the first release and the latest. C3 reports the gap between the two as a measured revision effect.
C1 features are always read point-in-time from ALFRED, whatever the target vintage. A feature with no vintages is flagged "latest vintage", and its model is labelled "not real-time".

## Benchmarks and the holdout

**Benchmarks (all of them are scored, at every horizon):**
- No-change (random walk): share(T+h) = share(T). The primary benchmark.
- Drift: share(T) + h × the mean quarterly change over the estimation window.
- AR(p) on quarterly changes, iterated to h.
- Seasonal naive, because Z.1 levels are not seasonally adjusted: share(T) + the change over the same h quarters a year earlier (h ≤ 4; for h=8, two years earlier). Descriptive only. It is not used in the decision rules unless the training sample shows seasonality (checked on development data only, before any scoring).

**CHOICE: AR order.**
- (a) Fixed p = 1. No search, nothing to overfit. May be too simple.
- (b) p chosen by BIC from 0 to 4, again at each origin using training data only. (Claude recommends.) Standard. BIC leans toward small p.
- (c) p chosen by AIC from 0 to 8. Fits better in sample. Overfits more.

**CHOICE: holdout.** It is scored once.
- (a) The last 8 quarters, 2024Q3–2026Q2. At h=8 there is only one holdout forecast.
- (b) The last 12 quarters, 2023Q3–2026Q2. (Claude recommends.) Origins 2023Q2 onward give 12, 9 and 5 holdout forecasts at h = 1, 4, 8. Development stops at targets up to 2023Q2.
- (c) As (b), plus a prospective holdout: forecasts made at each Z.1 release from 2026-12-10 onward, committed before the release.
Honest caveat for every option: the history to 2026Q2 has already been seen in A1 and on the sites. A historical holdout is untouched by the models, not by the researchers. Only (c)'s prospective part is truly unseen. Claude suggests adding (c) once C3 is out, as a running record that does not hold up C3.

**Holdout rules (proposed as fixed):**
- The data loader cuts the series at 2023Q2 unless it is given the frozen pre-registration hash and an explicit holdout flag.
- At most N frozen candidates enter the holdout (see multiple testing). Each is listed by name and commit before the run.
- There is one scoring run, as one commit. Its `results.json` is written by script (hand edits are blocked by the hooks).
- If a bug turns up after the run, the fix is a dated deviation. The original and the corrected results are both published. No candidate is added after the run.

## Losses, intervals and coverage

**CHOICE: primary point loss.**
- (a) RMSE, in pp of share. (Claude recommends.) Standard. Punishes large misses, such as 2008–11. Pairs with DM tests.
- (b) MAE. Robust to one bad quarter. Hides the large misses that matter most here.
- (c) CRPS as the primary loss, for point and interval together. Most complete. Needs a full predictive distribution from every model, benchmarks included.
Whichever is primary, RMSE and MAE are both reported. So are the interval score at 80% and 95% (Gneiting-Raftery / Winkler) and CRPS where a full predictive distribution exists.

**CHOICE: interval method.** It applies to every model and benchmark, so interval scores can be compared.
- (a) Model-based, Gaussian. Simple. Wrong if errors have fat tails or change size over time.
- (b) Empirical quantiles of the model's own past out-of-sample errors at the same horizon, using only errors already realised at the origin (purged the same way). (Claude recommends.) Needs no distributional assumption. Needs a burn-in of past errors, about 40 origins, before intervals start.
- (c) Adaptive conformal intervals. Like (b), but updated online for coverage. Better under drift. One more tuning rate to fix in advance.

**Coverage targets.** 80% and 95%, both two-sided. Coverage is reported per horizon. Each figure comes with a Clopper-Pearson binomial interval. At h=1 it also gets the Kupiec unconditional test and the Christoffersen independence test. At h>1 errors overlap, so independence tests are invalid there and coverage stays descriptive. Plain fact: 12 holdout forecasts at 95% coverage should miss about 0.6 times. The holdout cannot test 95% coverage. Coverage is judged on the development sample. The holdout only reports it.

## Leakage tests

The harness has an as-of guard. Every datum carries `available_at`. Any datum with `available_at` > origin raises an error. Tests (in `pytest`, run before any scoring) must show:

1. **Future target as a feature** (share at T+h): the guard raises. With the guard switched off in the test, the in-sample error at that horizon falls to about zero. This proves the feature reaches the model.
2. **Revised series in place of point-in-time** (a C1 input read from latest vintage instead of ALFRED): the guard raises on the vintage mismatch.
3. **A value published after the origin** (a G.19 value released one day after the origin date): the guard raises.
4. **Full-sample preprocessing** (scaler, seasonal factor or AR order fitted on all data): the fit-window check raises.
5. **Placebo**: a model trained on a time-shuffled target shows no skill over no-change on development data.

**CHOICE: what counts as passing.**
- (a) The guard trips on tests 1–4. Mechanism only.
- (b) Tests 1 and 5 by outcome only. They catch leaks the guard cannot see, but only large ones.
- (c) Both: guard tests 1–4 and outcome checks 1 and 5. (Claude recommends.) A harness that fails to flag a deliberately leaked feature is a bug, and C2 is not done until it is fixed.

## Significance and multiple testing

**CHOICE: tests of accuracy differences.**
- (a) Diebold-Mariano with the Harvey-Leybourne-Newbold small-sample correction for every pair. HAC lag h−1, Student-t critical values with n−1 degrees of freedom. Simple. Invalid for nested pairs (an AR model against no-change), where it is too conservative.
- (b) Clark-West for nested pairs, DM-HLN for non-nested pairs. Tests run on the development sample. Holdout results are descriptive only: relative loss and sign, no p-values. (Claude recommends.) Correct for nesting. Few holdout forecasts cannot carry a test.
- (c) Descriptive only, everywhere. Most honest about the small number of independent origins (overlap at h=8 leaves few). Gives no basis for saying "beats".

**CHOICE: multiple-testing control.** The family is 3 horizons × candidates × (no-change, AR).
- (a) One pre-declared primary comparison (the main candidate vs no-change at h=4, on the primary loss). Everything else is labelled exploratory. Cleanest. Puts weight on one number.
- (b) Holm correction across the whole family, with at most 3 frozen candidates. (Claude recommends.) Controls the family-wise error. Keeps all horizons in play.
- (c) Hansen's Model Confidence Set per horizon. Built for comparing many models. Its bootstrap is fragile with this few effective observations.

## Decision rules

**CHOICE: when the write-up may say a model "beats" a benchmark at horizon h.**
- (a) Lower primary loss on the development sample, significant after correction, and lower loss in the holdout.
- (b) As (a), plus relative loss ≤ 0.95 (at least 5% better) in both samples, and 80% coverage not rejected on development data. (Claude recommends.) It guards against wins too small to matter.
- (c) Holdout only: lower loss there. Easy. With 5–12 forecasts it is close to a coin flip.

Other wording, fixed in advance:
- "Comparable to the benchmark": the loss difference is not significant, or its sign flips between samples.
- "Does not beat": the benchmark's loss is lower in either sample.
- "Intervals are reliable": coverage is not rejected at either level on development data.
- Nothing is said about real-time accuracy unless the real-time check exists. If it does not, the write-up says the results are pseudo out-of-sample on latest-vintage data.

## What C3 must publish

- A specification registry: every specification tried, with ID, commit, date and development-sample scores. Abandoned and failed ones are included.
- Holdout results for every frozen candidate, not only the best.
- All benchmarks, all horizons, all losses, coverage tables with binomial intervals, and the test results with raw and adjusted p-values.
- Failure cases: the ten largest errors per horizon, plus results split by regime (at least 2007Q4–2011Q4 and 2020). The split dates are fixed now, not chosen after seeing errors.
- The revision effect, where measured: first-release vs latest-vintage scores.
- Whether C1 indicators were used. If not, why.
- Every deviation from this file, dated.
- A row in `claims/register.csv` for every number, and a "Claude draft" banner on any Claude-written text.

## What is and is not identified

- The design identifies out-of-sample forecast accuracy relative to the benchmarks over the stated origins.
- It does not identify why the share moves (that is Phase A), and it does not show that any indicator causes anything.
- Without a full vintage archive, the main results do not measure real-time accuracy.
- The policy regime changed in 2008, and there are few such shifts in the sample. Accuracy across the next one is untested.

## Deviations (dated, after freezing)

None. The file is not frozen.
