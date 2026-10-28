# Who Holds the Debt?

How US household debt has been reshaped by economic crises since the 1950s. The project looks at two things most analyses skip:

1. **Who bears the credit risk.** Household debt is split by *holder*, not just by loan type: the federal government, the GSEs and agency pools, banks, private securitization, and others. Did crises ratchet it onto public balance sheets?
2. **What the debt is backed by.** Debt is split into home-backed (an appreciating asset), vehicle-backed (a depreciating asset), and debt with no collateral at all, such as cards and student loans. For each class we track how well its collateral covers it through each crisis.

**What we found** (full write-up in [`analysis/findings.md`](analysis/findings.md)):

- **Most US household debt now sits on public balance sheets.** The public share of household mortgages and consumer credit rose from 3.2% in 1952 to **56.4% in 2026Q2** ($10.77T of $19.10T). "Public" means the federal government, GSEs and agency pools, and state & local governments.
- **But crises mostly didn't put it there.** We started from the thesis that each crisis ratchets the share up. The data rejects that as a general pattern: shifts after crises are indistinguishable from ordinary periods (placebo p ≈ 0.30). The long climb is a slow structural build-out of the GSEs, +18.8 pp in the 1980s alone.
- **One crisis did.** From 2007Q4 to 2011Q4 the share jumped from 36.1% to 49.2% (+13.1 pp, 98th percentile of all 16-quarter windows), and half of that was private lenders retreating. It never reversed. In 2001, by contrast, the share fell 3.8 pp during the private-label boom.
- **The public book has tilted toward unsecured debt.** The public sector now holds 86% of student loans and 51% of all uncollateralized household debt, up from 7% in 2007. Household debt overall has *not* drifted away from home collateral: home coverage is 3.56×, its highest outside 2022–26 since 1960.

| NBER peak | Public share at peak | 16 quarters later |
|---|---|---|
| 1973Q4 | 7.2% | 11.3% |
| 1981Q3 | 16.3% | 24.6% |
| 1990Q3 | 34.5% | 41.6% |
| 2001Q1 | 40.6% | 36.8% |
| 2007Q4 | 36.1% | 49.2% |
| 2019Q4 | 55.2% | 56.3% |

## Stack
| Layer | Tech | Folder |
|---|---|---|
| Ingest + transform | Python (uv), pandas, psycopg | `pipeline/` |
| Warehouse | Supabase Postgres (`raw` → `core` → `mart`) | `supabase/migrations/` |
| Analysis & viz | Tableau Desktop / Tableau Cloud (live connection as `tableau_reader`) | `tableau/` |
| Story site | Next.js on Vercel, Tableau Embedding API v3 | `web/` |
| Notebooks / findings | Python | `analysis/` |
| Hot Potato (dot-flow site) | Next.js + Canvas on Vercel, reads the same `mart` views | `atlas/` |

## Hot Potato (`atlas/`)
A second, standalone site that tells the same story as an animated dot flow. Each dot is $50B of debt in 2026 dollars, and dots move between six holder piles as you scroll. A Shares lens shows 1,000 dots, 0.1% each. Dots keep their identity from quarter to quarter: each quarter is rounded with the largest-remainder method, and only the difference moves, by the fewest dots possible (`atlas/lib/timeline.ts`, tested in `timeline.test.ts`). It deploys as its own Vercel project with **Root Directory `atlas`** and the same two `NEXT_PUBLIC_SUPABASE_*` variables. Without them it falls back to the `web/public/data` snapshots.

```bash
cd atlas && npm install && npm test && npm run dev
```

## Data
- Fed **Z.1 Financial Accounts** (`FRB_Z1_csv.zip`): holders of 1-4 family mortgages and consumer credit, the consumer credit split by type, and household real estate and durables.
- **FRED**: CPI, disposable income, unemployment, Case-Shiller, and Fed MBS holdings (the QE overlay).
- **NY Fed Household Debt & Credit** (2003+): delinquency transitions by loan type.

`pipeline/series_catalog.yaml` is the single source of truth for every series.

## Quickstart
```bash
cp .env.example .env               # fill DATABASE_URL (and optionally FRED_API_KEY)
cd pipeline && uv sync
uv run hhdebt run --export         # extract -> transform -> load (if DATABASE_URL) -> web/public/data/*.json
uv run pytest
```

Steps can also be run one at a time:

| Command | Does |
|---|---|
| `uv run hhdebt extract` | Downloads Z.1 (`FRB_Z1_csv.zip` into `data/z1/`, streamed and filtered without unzipping), FRED and the latest NY Fed HHDC workbook into `data/staging/<source>.csv`. Dev shortcuts: `--z1-zip PATH`, `--z1-csv PATH` (or `HHDEBT_Z1_CSV`), `--nyfed-xlsx PATH`, `--sources z1 fred`. |
| `uv run hhdebt transform` | Builds `core.*` and `mart.*` into `data/out/*.csv` (method notes are in `pipeline/src/hhdebt/transform.py`). |
| `uv run hhdebt load` | One transaction: upserts `raw.observations` and replaces the contents of `core` and `mart`. |
| `uv run hhdebt export-tableau` | Writes flat, pre-joined CSVs for Tableau Public to `tableau/data/` (one per dashboard). Also run by `run --export`. |
| `uv run hhdebt export-snapshot` | Writes each mart table plus `dim_crisis` and `dim_risk_bucket` to `web/public/data/<table>.json` (from the DB if `DATABASE_URL` is set, else from `data/out`). |

Local database:
```bash
service postgresql start
sudo -u postgres createdb hhdebt
sudo -u postgres psql -d hhdebt -f supabase/local_shim.sql -f supabase/migrations/20261027000000_init.sql
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hhdebt
```
`.github/workflows/refresh.yml` runs the pipeline and tests quarterly (the 20th of Mar/Jun/Sep/Dec, after each Z.1 release) and on demand, and uploads the snapshots as a build artifact. It needs the `DATABASE_URL` secret (and optionally `FRED_API_KEY`).
