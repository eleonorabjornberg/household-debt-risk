# Validation suite (PLAN task 0.3)

Independent re-computation of the project's headline numbers from the Fed's raw Z.1 file. It does **not**
import `hhdebt`; it re-parses `Z1.csv` itself and reads only `pipeline/series_catalog.yaml` for series IDs
and risk-bucket membership. It reports; it never changes a number.

```
uv run --project pipeline python validation/run.py [--z1-zip PATH] [--prev-z1-zip PATH]
uv run --project pipeline python -m pytest validation/test_run.py
```

Without `--z1-zip` the zip is taken from `data/validation/FRB_Z1_csv.zip` (gitignored), downloaded from
`https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip` if absent. Exit code 1 if any check FAILs.
Outputs: terminal table, `REPORT.md` (table, vintage = `Z1.csv` timestamp, zip SHA-256, run time), `results.json`.

| Check | What it does |
|---|---|
| A1-A4 | Every quarter 1952Q1 to latest, tolerance $0.5M: 17 mortgage holders = FL893065105; 9 consumer-credit holders = FL153166000; 4 types = FL153166000; FL153165105 + FL153166000 = FL154104015 |
| B | At 1990Q3, 2007Q4, 2011Q4, 2026Q2: re-sum apportioned mortgage holders, consumer-credit holders, scope total and public + private against the published totals |
| C | Headlines recomputed and compared after rounding to published precision (3.2%, 56.4%, $10.77T of $19.10T, 36.1% to 49.2%, +13.1 pp, 58.6% in 2021Q1, 65.6%, 31.3%). C9 tests "never reversed" two ways: (i) min share from 2012Q1 on vs 2011Q4, (ii) vs 2007Q4. PASS only if (i); if only (ii), FAIL with a rewording note |
| D | `web/public/data/public_share.json` vs recomputation, every quarter (1e-6 shares, $1M levels). If `DATABASE_URL_READONLY` is set the same against `mart.public_share` (read-only session); otherwise NOT RUN |
| E | Known breaks 1968Q1, 1977Q1, 2006Q1, 2010Q1 (two checks) visible in the data; public share continuous through 2010 with sectors 40+41 summed; gaps; other jumps |
| F | Revisions between this vintage and a previous one. `--prev-z1-zip` accepts a long-format `FRB_Z1_csv.zip` or the Fed's per-table `z1_csv_files.zip`. Without it the Fed's 20260611 archive folder is probed and every URL tried is logged; else NOT RUN. `--no-network-prev` skips probing |

Status values: PASS, FAIL, WARN (needs a human look, does not fail the run), NOT RUN (never counted as PASS).

## Jump rule (E8)

For each component series take its share of its own total (mortgage holders / FL893065105; consumer-credit holders
and types / FL153166000; mortgages and consumer credit / FL154104015), the quarter-on-quarter change, and a robust
z = (x - median) / max(1.4826 x MAD, 0.1 pp) over 1952Q1 to latest. Flag |z| > 6 **and** |change| >= 1.0 pp. The
pp floor keeps tiny series from flagging on trivia. Flags at the four known break quarters are listed as explained;
all others are WARN, never FAIL. The threshold is a judgement call; change `JUMP_Z` / `JUMP_MIN_PP` in `run.py`.

## Files

`run.py` entry point; `zparse.py` streaming Z.1 parser (reads the 3 GB `Z1.csv` inside the zip without
unzipping); `test_run.py` pytest (parser, identity check, never-reversed rule, on synthetic data).
