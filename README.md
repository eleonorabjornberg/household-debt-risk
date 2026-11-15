# Who Holds the Debt?

[![ci](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/ci.yml)
[![refresh-data](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/refresh.yml/badge.svg)](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/refresh.yml)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](opendata/README.md) [![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)

**Live site: [Hot Potato](https://hot-potato-credit.vercel.app)** (also at household-debt-risk.vercel.app). The repository holds the pipeline, the checks, the evals and the Claude tooling behind it.

How US household debt has been reshaped by economic crises since the 1950s. The project looks at two things most analyses skip:

1. **Who bears the credit risk.** Household debt is split by *holder*, not just by loan type: the federal government, the GSEs and agency pools, banks, private securitization, and others. Did crises ratchet it onto public balance sheets?
2. **What the debt is backed by.** Debt is split into home-backed (an appreciating asset), vehicle-backed (a depreciating asset), and debt with no collateral at all, such as cards and student loans. For each class we track how well its collateral covers it through each crisis.

**What we found** (full write-up in [`analysis/findings.md`](analysis/findings.md)):

> **Claude draft.** The findings summary below was written by Claude for Eleonora to review and rewrite. It is not her text yet.

- **Most US household debt now sits on public balance sheets.** The public share of household mortgages and consumer credit rose from 3.2% in 1952 to **56.4% in 2026Q2** ($10.77T of $19.10T). "Public" means the federal government, GSEs and agency pools, and state & local governments.
- **But crises mostly didn't put it there.** We started from the thesis that each crisis ratchets the share up. The data does not support that as a general pattern: a placebo test finds no detectable excess in shifts after crises over ordinary periods (p ≈ 0.30, low power), drawing from the 282 overlapping 16-quarter windows, 1952Q1–2022Q2. The long climb is a slow structural build-out of the GSEs, +18.8 pp in the 1980s alone.
- **One crisis did.** From 2007Q4 to 2011Q4 the share jumped from 36.1% to 49.2% (+13.1 pp, 98th percentile of all 16-quarter windows), and half of that was private lenders retreating. It never reversed. In 2001, by contrast, the share fell 3.8 pp during the private-label boom.
- **The public book has tilted toward unsecured debt.** The public sector now holds 86% of student loans and 51% of all uncollateralized household debt, up from 7% in 2007. Household debt overall has *not* drifted away from home collateral: home coverage is 3.56×, its highest outside 2022–26 since 1960.

| NBER peak | Public share at peak | 16 quarters later |
|---|---|---|
| 1973Q4 | 7.2% | 11.3% |
| 1981Q3 | 16.3% | 24.6% |
| 1990Q3 | 34.5% | 41.6% |
| 2001Q1 | 40.6% | 36.8% |
| 2007Q4 | 36.1% | 49.2% |
| 2019Q4 | 55.2% | 56.2% |

## Repository index

Status of each part is in [`PLAN.md`](PLAN.md); how it was built, with which models and what went wrong, is in [`docs/building-with-claude.md`](docs/building-with-claude.md).

| Path | What it is |
|---|---|
| [`PLAN.md`](PLAN.md) | Phases, tasks, acceptance criteria and status: the source of truth for what is done and what is next |
| [`CLAUDE.md`](CLAUDE.md) | How to work in this repo (rules for people and for Claude) |
| [`pipeline/`](pipeline/) | Python package `hhdebt`: extract → transform → load → export snapshots. Series catalog: [`pipeline/series_catalog.yaml`](pipeline/series_catalog.yaml) |
| [`supabase/migrations/`](supabase/migrations/) | Warehouse schema (`raw` → `core` → `mart`) and the read-only `research_reader` role |
| [`validation/`](validation/) | One-command validation suite, independent of the pipeline code. Latest run: [`validation/REPORT.md`](validation/REPORT.md) |
| [`claims/`](claims/) | [`register.csv`](claims/register.csv): every published number with its source, series, vintage and validation status; a test fails if a site number has no row |
| [`analysis/`](analysis/) | Notebook, [`findings.md`](analysis/findings.md), [`recommendation.md`](analysis/recommendation.md) (the "so what", with limits), tables and figures |
| [`atlas/`](atlas/) | Hot Potato, the public site (Next.js + Canvas): the potato flow, dashboard, research pages, scenarios, methods, sources and "Ask Hot Potato". Live at [hot-potato-credit.vercel.app](https://hot-potato-credit.vercel.app) |
| [`web/`](web/) | The first long-form story site (Next.js, hand-drawn SVG charts). Its scenarios, methods and build pages moved into Hot Potato (decision of 2026-11-07, one site) |
| [`.claude/skills/`](.claude/skills/) | Seven project skills, each with scripts and tests: `z1-release-update` (runs a new Z.1 release end to end and stops for approval), `claim-check` (recomputes any published number from its register row), `chart-from-sql`, `research-memo`, `preregister`, `source-provenance`, `decision-cards` |
| [`prompts/`](prompts/) | The prompts that built the project, one dated file per session |
| [`docs/`](docs/) | [`building-with-claude.md`](docs/building-with-claude.md), the session log |
| [`research/`](research/) | Phase A–C analyses, one folder per task, each with a README and method notes: decompositions (A1, A2), pre-1952 history (A3), structural breaks (A4), distribution (A5), causal tests (A7), international comparison (A8), market and CRT pricing (B1, B2), scenarios (B3, B4), nowcasts, forecasts and their accuracy (C1, C1b, C2, C3) |
| [`docs/decisions/`](docs/decisions/) | Method decisions and frozen pre-registrations (A4, A7, C2) |
| [`.claude/agents/`](.claude/agents/) | Review and helper subagents (skeptic, quant-reviewer, editor, register-keeper, analyst, prompt-archivist) |
| [`mcp/household-credit-mcp/`](mcp/household-credit-mcp/) | Read-only MCP server over the project's data |
| [`plugin/fed-data-desk/`](plugin/fed-data-desk/) | The skills, agents and MCP server packaged as one Claude Code plugin |
| [`evals/`](evals/) | Evaluations of the Claude tooling: E1 question-to-SQL benchmark, E2 planted-error test, E3 regression suite, E4 red-team of Ask Hot Potato. Index: [`evals/README.md`](evals/README.md) |
| [`opendata/`](opendata/) | Downloads, data dictionary, licences and the API plan |
| [`tools/`](tools/) | Reproduction check and chart-text checks |
| [`claims/site/`](claims/site/) | Source references shared by both sites (F1) and the link check |
| [`.github/workflows/`](.github/workflows/) | CI and the quarterly pipeline refresh |

Not built yet (see PLAN.md): `paper/`, the working paper (F6).

## How Claude was used

| What | Where | What it does |
|---|---|---|
| Multi-session build | [`docs/building-with-claude.md`](docs/building-with-claude.md), [`prompts/`](prompts/) | A coordinator session and parallel track sessions (infra, markets, analysis); every session logged with model tier, cost and each error with who caught it |
| Skills | [`.claude/skills/`](.claude/skills/) | Seven repeatable workflows, from a quarterly data release to recomputing a single published number |
| Subagents | [`.claude/agents/`](.claude/agents/) | Adversarial reviewers (`skeptic` for data, `quant-reviewer` for statistics, `editor` for prose) that log objections to [`claims/review-log.md`](claims/review-log.md), plus helpers |
| Hooks | [`.claude/settings.json`](.claude/settings.json), [`.claude/hooks/`](.claude/hooks/) | Every commit must pass the claims-register check and the offline tests; hand edits to results files are blocked |
| MCP server | [`mcp/household-credit-mcp/`](mcp/household-credit-mcp/) | Read-only tools over the warehouse that refuse questions the data cannot answer (forecasts, holder-by-type splits) |
| API app | [`atlas/app/api/ask/`](atlas/app/api/ask/), [`atlas/lib/ask/`](atlas/lib/ask/) | "Ask Hot Potato": Claude with tool use over the data, every answer citing its query and vintage, with rate limits and a daily cost stop |
| Evals | [`evals/README.md`](evals/README.md) | Benchmarks of the tooling itself, with pre-registrations frozen before any result ([`docs/decisions/`](docs/decisions/)) |

Analysis text Claude wrote carries a "Claude draft" banner. The design, the decisions (listed in `PLAN.md`, "Decisions taken") and the final write-up are Eleonora's.

## How to reproduce the numbers

Everything at once: `make all` (`make help` lists the steps; `make ci` runs what CI runs). Step by step:

From a fresh clone, with Python and [uv](https://docs.astral.sh/uv/). It needs network access to `www.federalreserve.gov`, and no database or API keys.

1. Install the Python environment:
   ```bash
   cd pipeline && uv sync && cd ..
   ```
2. Rebuild every headline number from the Fed's raw Z.1 file and check it. This downloads `FRB_Z1_csv.zip` (about 64 MB) into `data/validation/`, recomputes the identities, sector totals and headlines, compares them with the committed snapshots, and compares with the previous (June 2026) vintage:
   ```bash
   uv run --project pipeline python validation/run.py
   ```
   It writes `validation/REPORT.md` and `validation/results.json`. Compare them with the committed versions (`git diff validation/`): on the same Z.1 vintage (`Z1.csv` dated 2026-09-11) only the run time should change. A later vintage will move some numbers; step 4 lists which published ones.
3. Check the claims register and the tests:
   ```bash
   uv run --project pipeline pytest -q claims validation/test_run.py .claude/skills/z1-release-update/tests
   ```
   ```bash
   cd pipeline && uv run pytest -q && cd ..
   ```
4. See which published numbers a new vintage would change (it never edits copy):
   ```bash
   uv run --project pipeline python .claude/skills/z1-release-update/scripts/stale_claims.py
   ```
5. Optional: rerun the pipeline and the analysis (`cd pipeline && uv run hhdebt run --export --no-load`, then `cd analysis && uv run --with pandas --with matplotlib --with numpy python -I notebook.py`, as the notebook's header says), and build the sites (`cd atlas && npm install && npm test && npm run build`; `cd web && npm install && npm run build`).

Check D2 (database vs recomputation) runs only when `DATABASE_URL_READONLY` is set; otherwise it reports NOT RUN, which is never counted as a pass.

## Stack
| Layer | Tech | Folder |
|---|---|---|
| Ingest + transform | Python (uv), pandas, psycopg | `pipeline/` |
| Warehouse | Supabase Postgres (`raw` → `core` → `mart`) | `supabase/migrations/` |
| First story site (pages since moved into Hot Potato) | Next.js, hand-drawn SVG charts | `web/` |
| Notebooks / findings | Python | `analysis/` |
| Hot Potato (potato-flow site) | Next.js + Canvas on Vercel, reads the same `mart` views | `atlas/` |

## Hot Potato (`atlas/`)
The public site tells the story as an animated potato flow. Each potato is $50B of debt in 2026 dollars, drawn in the ink of the holder that has it, and potatoes move between six holder piles as the story plays (Play, five chapter buttons, or the timeline). A Shares lens shows 1,000 potatoes, 0.1% each. Potatoes keep their identity from quarter to quarter: each quarter is rounded with the largest-remainder method, and only the difference moves, by the fewest potatoes possible (`atlas/lib/timeline.ts`, tested in `timeline.test.ts`). It deploys as its own Vercel project with **Root Directory `atlas`** and the same two `NEXT_PUBLIC_SUPABASE_*` variables. Without them it falls back to the `web/public/data` snapshots.

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
| `uv run hhdebt export-snapshot` | Writes each mart table plus `dim_crisis` and `dim_risk_bucket` to `web/public/data/<table>.json` (from the DB if `DATABASE_URL` is set, else from `data/out`). |

Local database:
```bash
service postgresql start
sudo -u postgres createdb hhdebt
sudo -u postgres psql -d hhdebt -f supabase/local_shim.sql -f supabase/migrations/20261027000000_init.sql -f supabase/migrations/20261027010000_mart_dim_views.sql -f supabase/migrations/20261103000000_research_reader.sql -f supabase/migrations/20261115000000_ask_limits.sql
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hhdebt
```
`.github/workflows/refresh.yml` runs the pipeline and tests quarterly (the 20th of Mar/Jun/Sep/Dec, after each Z.1 release) and on demand, and uploads the snapshots as a build artifact. It needs the `DATABASE_URL` secret (and optionally `FRED_API_KEY`).
