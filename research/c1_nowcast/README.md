# C1: Nowcasting the public share between Z.1 releases

> **Claude draft, not the author's text.** The evaluation design is Eleonora's (her Q-C1 decisions of 2026-11-04, recorded in PLAN.md). The implementation details Claude added are marked in `EVALUATION.md`.

**PLAN task C1. Status: development-sample evaluation done; holdout pending the coordinator.** The acceptance criteria are a point-in-time panel, in which each input is read at the value public at the nowcast instant, and a release-lag table per input. The panel is `pit.panel(t)`. The table is [`release_lags.csv`](release_lags.csv). The Z.1 release calendar is [`z1_calendar.csv`](z1_calendar.csv). Candidate inputs are listed in [`inputs.yaml`](inputs.yaml), and the sources with their hashes in [`sources.md`](sources.md).

## Results: development sample only (targets to 2023Q2; holdout not run)

> **Claude draft, not the author's text.** The scores below follow [`EVALUATION.md`](EVALUATION.md), which was committed before any score existed (7ae4afb). The holdout is untouched: the C1 and C2 holdout starts are still being reconciled by the coordinator. So under C2's wording rule, nothing here can yet be called "beats".

**Real time (RT)** means: the Z.1 base is read from the Fed's release archive, the indicators from ALFRED as of each instant, and the target is the first release. There are monthly instants from October 2016, and targets run 2016Q3–2023Q2. The three instants whose base release (2017-03-09) has no archived CSV are absent. RMSE relative to no-change (below 1 is better), by instant index k (k = 1 is the first monthly instant after a Z.1 release):

| k | n | Accounting bridge | DM-HLN p / Holm p | n (regression) | Bridge regression | Clark–West p / Holm p | AR(1) | Drift |
|---|---|---|---|---|---|---|---|---|
| 1 | 26 | 0.74 | 0.02 / 0.16 | 14 | 0.43 | <0.01 / 0.01 | 0.97 | 0.87 |
| 2 | 26 | 0.74 | 0.06 / 0.46 | 14 | 0.45 | <0.01 / 0.02 | 0.97 | 0.87 |
| 3 | 25 | 0.80 | 0.15 / 0.47 | 13 | 0.52 | <0.01 / 0.03 | 1.09 | 0.91 |

- **The accounting bridge** has an RMSE of 0.29 pp, against 0.38 pp for no-change, pooled over k: about a quarter lower. After the Holm correction the difference is not significant at any k. Under C2's wording it is so far "comparable to the benchmark".
- **The bridge is biased downward.** Its mean error is −0.22 pp, and the bias does not shrink as more monthly data arrive (−0.18 at k = 1, −0.26 at k = 3). One likely reason, not tested: the public mortgage holders (agency pools, GSEs) have no monthly indicator in set 2b and are carried flat. Banks' mortgages and consumer credit, by contrast, move with H.8 and G.19.
- **The bridge regression** fits its intercept to past errors, which removes most of that bias. Its RMSE is about half of no-change's, and it is significant after Holm at every k. It has only 13–14 forecasts per k, because it needs 12 past first-release pairs before it starts.
- **AR(1)** does no better than no-change (0.97–1.09). **Drift** is slightly better (0.87–0.91), but worse than the bridge.
- **Against the latest vintage instead of the first release** (RT-latest), the bridge's relative RMSE is 0.77.

**Pseudo-real-time comparisons** use latest-vintage Z.1, cut at each release's last quarter, so they are *not real-time* for Z.1. The indicators are still point-in-time. With indicator set 2b, targets 2015Q1–2023Q2, the bridge's relative RMSE is 0.77. With set 2a (G.19 federal and total only), targets 2010Q2–2023Q2, it is 0.76. All scores are in `scores_dev.csv`, all tests in `tests_dev.csv`, and every nowcast in `nowcasts_dev.csv`.

**What this does not show.**
- It does not show accuracy on unseen data: the holdout has not been run.
- The samples are small (25–26 targets per k in RT). All p-values are descriptive.
- The bias finding suggests adding the agency monthly summaries (indicator set 2c), but that would be a new, separately pre-registered run. It must not be a change to this one.

## How "what was public on day t" is answered

- **Source.** Each input is read from ALFRED (`research/common/fred.py`, which caches the raw JSON in `data/fred/` with a SHA-256 manifest). ALFRED returns every value an observation has ever had, with the interval `[realtime_start, realtime_end]` during which it was current.
- **The as-of rule.** `pit.as_of(v, t)` keeps the rows with `realtime_start ≤ t ≤ realtime_end`. An observation first published after day t is absent from the panel. It is never filled in or carried back.
- **Units are taken as of publication.** ALFRED's units label changes across vintages: G.19 moved from billions to millions with the 2025-02-07 vintage, and Z.1 series on FRED with the 2026-01-09 vintage. Every value is rescaled to millions using the label in force on the day the value was published, so the rescaling adds no look-ahead.
- **Release lags.** A lag is measured from the end of the reference period to an observation's first publication. Two kinds of observation are excluded. The first is any observation carried by ALFRED's first vintage, because it has no earlier vintage to date it against. The second is history back-filled when a series is extended, because those dates were not the newest in the vintage that first carried them.
- **Tests (`test_pit.py`, offline).** They check that the as-of read never returns a later vintage, that a deliberately leaked future row stays invisible before its publication date, that the lag and back-fill rules work, and that units are rescaled by the label in force when each value was published.

## What the release-lag table shows (`release_lags.csv`)

- **G.19 consumer credit** comes out about five weeks after month end.
- **H.8 bank loans** come out about nine days after the week ends.
- **The Fed's agency MBS holdings (H.4.1)** come out the next day.
- **Z.1 itself** comes out about ten weeks after quarter end. The 2025Q3 release, published 2026-01-09, came out more than three months after quarter end. That release's cause is not checked here.

So, partway between two Z.1 releases, roughly one to two months of G.19 data and most of a quarter of H.8 data are public for the unpublished quarter.

## Gaps that limit the design

- **Target vintages.** ALFRED has real-time vintages of the household liability totals from 2010 (`HMLBSHNO`, `CCLBSHNO`). It has the holder-side Z.1 series (agency pools, GSEs, scope total) only from 2019. Older vintages of the full public share would have to come from the Fed's own release archive: CSV from 2017, fixed-width .prn tables before that, back to 2010 (see `sources.md`). That archive is not parsed yet.
- **The mortgage side is thin.** No free, monthly, real-time series covers the public mortgage holders (agency pools, GSE portfolios). Ginnie Mae's monthly reports are reachable but not parsed, and they carry no vintages. Freddie Mac's and Fannie Mae's monthly summaries are blocked by the network policy (their hosts would need adding). H.8 covers only banks' residential loans, a private holder.
- **The Fed's MBS holdings are not a holder of household mortgages in Z.1's sense.** The pools are the holder, so `WSHOMCB` can only be an auxiliary signal.

## Reproduce

```bash
uv run --project pipeline python research/c1_nowcast/pit.py                     # needs FRED_API_KEY
uv run --project pipeline python research/c1_nowcast/pit.py --asof 2024-05-01   # one as-of panel
uv run --project pipeline pytest -q research/c1_nowcast
```
