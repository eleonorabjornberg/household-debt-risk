# Who Holds the Debt?

How US household debt has been reshaped by economic crises since the 1950s. The project looks at two things most analyses skip:

1. **Who bears the credit risk.** Household debt is split by *holder*, not just by loan type: the federal government, the GSEs and agency pools, banks, private securitization, and others. Does each crisis ratchet more of it onto public balance sheets?
2. **What the debt is backed by.** Debt is split into home-backed (an appreciating asset), vehicle-backed (a depreciating asset), and debt with no collateral at all, such as cards and student loans. For each class we track how well its collateral covers it through each crisis.

**Working thesis (to be tested):** each crisis since 1970 moved a larger share of household credit risk onto public or quasi-public balance sheets, and away from debt backed by appreciating collateral.

A first look at the Z.1 data from 1952 to 2026 shows the public share of household mortgages and consumer credit:

| Crisis | Public share at peak | Public share 16 quarters later |
|---|---|---|
| 1973 | 6.8% | 10.7% |
| 1981 | 14.5% | 22.5% |
| 1990 | 32.8% | 40.2% |
| 2001 | 39.6% | 36.0% |
| 2007 | 35.5% | 48.3% |

By 2026 the share is about 56%. The 2001 recession is the one exception, and it coincides with the private-label securitization boom.

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
cp .env.example .env               # fill DATABASE_URL etc.
cd pipeline && uv sync
uv run python -m pipeline.run      # extract → transform → load
uv run pytest
```
