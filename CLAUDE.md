# CLAUDE.md

Research platform on who holds America's household credit risk, how it is priced, and where it is going.

## Start here
1. `PLAN.md`: phases, tasks, dependencies, acceptance criteria and status. Work on the first task marked `next`, and only that task.
2. `docs/building-with-claude.md`: session log. Add an entry every session (tasks, model tier, cost if measured, errors and how they were caught).
3. Stop for Eleonora's approval at the end of every phase.

## Rules
- Authorship (course rule): the design, validation and write-up are Eleonora's. Claude builds, checks and drafts. Any analysis text Claude writes (recommendation, research write-ups, memos, paper) starts with a "Claude draft" banner and stays a draft until Eleonora replaces it with her own text. Per her voice-53 (a) (2026-11-10), site and research pages may be drafted in her register with the `eleonora-writing` skill, but each keeps its "Claude draft" banner until she approves that page; Claude never presents its text as hers. Her decisions go in PLAN.md "Decisions taken" and the log as she makes them; the log names who caught each error.
- Never present an unverified number as fact. Label estimates, imputations and proxies.
- Never fabricate data. Check a source is available (and free) before building on it; propose a free proxy for paywalled series.
- Every published number needs a row in `claims/register.csv` (query or code path, series IDs, vintage, validation status).
- Don't touch the production Vercel deployment or the production database without asking. Branch pushes and preview deployments are fine.
- Anything waiting on Eleonora (a decision, an approval, or finished work to review) goes onto a card page with the `decision-cards` skill, not only into chat or a status file: decisions on the decision docket, finished work on the review queue (`docs/review-queue.html`). Tracks send such items to the coordinator, who adds the cards.
- Secrets never go through the chat; they live in the cloud environment settings.
- Commit after each task with a clear message.
- Token discipline: read excerpts, not whole files; no data dumps in chat; cheaper models or subagents for routine work.
- No Tableau. Charts are Python (the `chart-from-sql` skill, when built) or the sites' own SVG/Canvas.

## Layout
| Path | What |
|---|---|
| `pipeline/` | Python package `hhdebt` (uv): `extract → transform → load → export-snapshot`. Series catalog: `pipeline/series_catalog.yaml`. Methods: top of `pipeline/src/hhdebt/transform.py` |
| `supabase/migrations/` | Warehouse schema: `raw` (every vintage) → `core` (latest) → `mart` (analysis). Applied migrations are history: never edit them, add a new one |
| `analysis/` | Notebook, findings, tables and figures for the original analysis |
| `atlas/` | Hot Potato, the live dot-flow site (Next.js + Canvas) |
| `web/` | Long-form story site (Next.js, hand-drawn SVG charts) |
| `PLAN.md` | Target layout for the folders still to come (`validation/`, `claims/`, `research/`, `.claude/skills/`, `.claude/agents/`, `mcp/`, `plugin/`, `evals/`, `prompts/`, `paper/`) |

## Hooks
`.claude/settings.json` runs two checks. Before any `git commit`, `.claude/hooks/checks.sh` (register check and offline tests) must pass, or the commit is blocked. Hand edits to any `results.json` are blocked; regenerate them with their script. For your own commits: `git config core.hooksPath .githooks`.

## Commands
```bash
cd pipeline && uv sync && uv run pytest          # tests; data tests skip unless data/ exists
uv run hhdebt run --export                       # full pipeline (needs network; DATABASE_URL to load)
cd atlas && npm install && npm test && npm run dev
cd web && npm install && npm test && npm run build
make all                                         # everything from a fresh clone (make help lists steps)
make ci                                          # what CI runs
```

Local Postgres for schema tests:
```bash
service postgresql start
sudo -u postgres createdb hhdebt
sudo -u postgres psql -d hhdebt -f supabase/local_shim.sql -f supabase/migrations/20261027000000_init.sql -f supabase/migrations/20261027010000_mart_dim_views.sql -f supabase/migrations/20261103000000_research_reader.sql -f supabase/migrations/20261115000000_ask_limits.sql
```

## Database roles
- `research_reader`: the one read-only login (`DATABASE_URL_READONLY`). SELECT on `mart` and the `core` dimensions; read-only sessions, 15 s statement timeout.
- `anon` / `authenticated`: the sites, through Supabase's API, `mart` only.
- Writes: the pipeline's `DATABASE_URL` only.

## Next.js note
`web/AGENTS.md`: this Next.js version has breaking changes. Read `node_modules/next/dist/docs/` before writing Next.js code.
