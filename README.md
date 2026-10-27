# Who Holds the Debt?

How US household debt has been reshaped by economic crises since the 1950s. The project looks at two things most analyses skip:

1. **Who bears the credit risk.** Household debt is split by *holder*, not just by loan type: the federal government, the GSEs and agency pools, banks, private securitization, and others. Does each crisis ratchet more of it onto public balance sheets?
2. **What the debt is backed by.** Debt is split into home-backed (an appreciating asset), vehicle-backed (a depreciating asset), and debt with no collateral at all, such as cards and student loans. For each class we track how well its collateral covers it through each crisis.

**Working thesis (to be tested):** each crisis since 1970 moved a larger share of household credit risk onto public or quasi-public balance sheets, and away from debt backed by appreciating collateral.

A first look at the Z.1 data from 1952 to 2026 shows the public share of household mortgages and consumer credit:

| Crisis | Public share at peak | Public share 16 quarters later |
|---|---|---|
| 1973 | 7.2% | 11.3% |
| 1981 | 16.3% | 24.6% |
| 1990 | 34.5% | 41.6% |
| 2001 | 40.6% | 36.8% |
| 2007 | 36.1% | 49.2% |

By 2026Q2 the share is 56.4%. "Public" means the federal government, GSEs and agency pools, and state & local governments. The 2001 recession is the one exception, and it coincides with the private-label securitization boom.

## Stack
| Layer | Tech | Folder |
|---|---|---|
| Ingest + transform | Python (uv), pandas, psycopg | `pipeline/` |
| Warehouse | Supabase Postgres (`raw` → `core` → `mart`) | `supabase/migrations/` |
| Analysis & viz | Tableau Desktop / Tableau Cloud (live connection as `tableau_reader`) | `tableau/` |
| Story site | Next.js on Vercel, Tableau Embedding API v3 | `web/` |
| Notebooks / findings | Python | `analysis/` |

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
| `uv run hhdebt export-snapshot` | Writes each mart table plus `dim_crisis` and `dim_risk_bucket` to `web/public/data/<table>.json` (from the DB if `DATABASE_URL` is set, else from `data/out`). |

Local database:
```bash
service postgresql start
sudo -u postgres createdb hhdebt
sudo -u postgres psql -d hhdebt -f supabase/local_shim.sql -f supabase/migrations/20261027000000_init.sql
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hhdebt
```
`.github/workflows/refresh.yml` runs the pipeline and tests quarterly (the 20th of Mar/Jun/Sep/Dec, after each Z.1 release) and on demand, and uploads the snapshots as a build artifact. It needs the `DATABASE_URL` secret (and optionally `FRED_API_KEY`).
