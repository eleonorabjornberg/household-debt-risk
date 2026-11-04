# C1: Nowcasting the public share between Z.1 releases (data plumbing)

> **Claude draft, not the author's text.** This describes the plumbing only. The evaluation design is Eleonora's choice: which indicators, the vintage rule, the benchmarks and the metrics. The options, with a recommendation, are in [`tracks/markets.md`](../../tracks/markets.md) under "Questions for Eleonora". No nowcast has been computed or evaluated.

**PLAN task C1. Status: plumbing built; evaluation blocked on Eleonora's design choice.** The acceptance criteria are a point-in-time panel, in which each input is read at the value public at the nowcast instant, and a release-lag table per input. The panel is `pit.panel(t)`. The table is [`release_lags.csv`](release_lags.csv). The Z.1 release calendar is [`z1_calendar.csv`](z1_calendar.csv). Candidate inputs are listed in [`inputs.yaml`](inputs.yaml), and the sources with their hashes in [`sources.md`](sources.md).

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
