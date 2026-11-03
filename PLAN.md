# PLAN

**Question every component serves:** who holds America's household credit risk, how is it priced, and where is it going?

**Aim:** a research platform at working-paper standard, plus an AI research system that keeps it current and audits itself. Framed for quantitative research and AI systems for financial markets.

**Owner:** Eleonora Björnberg. She sets the design and approves each phase; Claude builds, checks and drafts.

---

## How to resume (read this first in a fresh session)

1. Read this file, then `docs/building-with-claude.md` (latest entries at the bottom).
2. Find the first task whose status is `next`. Check its dependencies are `done`.
3. Work only on that task. When its acceptance criteria are met, set it to `done`, add a log entry, commit, push.
4. **Stop at the end of every phase** and ask for approval before starting the next one.

**Status values:** `done` · `in progress` · `next` · `todo` · `blocked (reason)` · `needs-approval` · `dropped (reason)`

**Current position:** Phase 0. 0.1, 0.3, 0.4 and 0.10 in progress (parallel subagents); 0.2 built and tested locally, waiting for approval to apply to the production database.

---

## Rules

- Stop for approval after PLAN.md and after each phase.
- Never present an unverified number as fact. Label estimates, imputations and proxies wherever they appear.
- Never fabricate data. Check availability before any task that needs a new source. If a series is paywalled (Bloomberg, ICE, Intex, CoreLogic…), say so and propose a free proxy.
- Don't touch the production Vercel deployment without asking. Preview deployments only.
- Commit after each task, with a clear message. Push to the working branch.
- Token discipline: excerpts over whole files, no data dumps in chat, cheaper models or subagents for routine work, the main model for analysis and review. Suggest `/clear` or a new session at phase boundaries.
- Any step Eleonora must run herself comes with exact, copy-pasteable commands.
- Secrets never pass through the chat. They live in the cloud environment's settings (Network secrets / environment variables).

## Standard of evidence (borrowed from `repo-market-model`)

- A number is publishable only if it traces to a query, a series ID, a source vintage and a validation status (`claims/register.csv`, task 0.5).
- Raw downloads are kept immutable, with retrieval time, URL, byte count and SHA-256 recorded. Raw and processed data stay out of git; code and metadata go in.
- Point-in-time ("as-of") inputs for every forecast: only information public at the forecast instant, using ALFRED vintages where they exist.
- Rolling-origin evaluation, purged and embargoed, with an untouched holdout. Every model is compared to naive and AR benchmarks. Failed specifications are published too.
- A quantity that could not be computed is recorded as absent, never as a default.
- Method decisions are recorded in `docs/decisions/<topic>.md`, with date and reasoning.

## Repository layout (target)

Each kind of artifact has one obvious home, so the repo link alone shows the code, skills, prompts, notebooks and dashboards, and a reader can reproduce any of them.

| Path | Holds | Evidence it must carry |
|---|---|---|
| `README.md` | Index of everything below, with one line per artifact and a link | "How to reproduce" section (0.9) |
| `pipeline/`, `supabase/` | Ingest, transform, warehouse schema | Tests |
| `validation/` | One-command validation suite | `REPORT.md` from the latest run |
| `claims/` | `register.csv`, `review-log.md` | Every published number has a row |
| `analysis/`, `research/` | Notebooks and code for Phases A–C | Each notebook runs top to bottom from a fresh clone |
| `atlas/` | Hot Potato, the live dashboard (incl. "Ask Hot Potato", D6) | Every number links to its register row (F1) |
| `web/` | The long-form story site | Same |
| `.claude/skills/<name>/` | `SKILL.md`, scripts, `examples/` | `examples/triggers.md`: prompts that should and should not trigger it, with recorded outputs |
| `.claude/agents/` | Subagent definitions | Sample outputs in `claims/review-log.md` |
| `mcp/household-credit-mcp/` | MCP server | Tests, `README` with install instructions, example transcripts |
| `plugin/fed-data-desk/` | Cowork plugin | `examples/before/` and `examples/after/` for each routine job |
| `evals/` | E1–E4 benchmarks and results over time | Results files appended, never overwritten |
| `prompts/` | The prompts that built and run the system (0.10) | Dated, one file per session or agent |
| `docs/` | `building-with-claude.md`, `decisions/` | Updated every session |
| `paper/` | Working paper and op-ed (F6) | Every number passes `claim-check` |

## Decisions taken

| Date | Decision | By |
|---|---|---|
| 2026-11-03 | Keep this repo (`household-debt-risk`) rather than start a new one; rename later if wanted. | Eleonora |
| 2026-11-03 | Drop Tableau from the project entirely (task 0.1). Charts come from the `chart-from-sql` skill and the sites' own SVG/Canvas. | Eleonora |
| 2026-11-03 | Read-only database access goes through a new `research_reader` role, not `tableau_reader`. | Eleonora / Claude |
| 2026-11-03 | The two earlier scope updates are replaced by this plan. | Eleonora |
| 2026-11-03 | This plan covers the product only. | Eleonora |
| 2026-11-03 | Plan approved. | Eleonora |
| 2026-11-03 | Eleonora registers any Freddie Mac / Fannie Mae data accounts herself (A2, B2). | Eleonora |
| 2026-11-03 | Research memos (D3) target financial institutions: banks, asset managers, insurers, MBS and CRT investors. | Eleonora |
| 2026-11-03 | Licences (default, open to change): MIT for code; CC BY 4.0 for derived data and text. Third-party series (e.g. S&P Case-Shiller via FRED) are not redistributed, only linked. | Eleonora / Claude |

## Environment prerequisites

Set in the cloud environment's settings (session title bar → environment menu → **Edit**). A new session picks them up.

| Need | For | Status |
|---|---|---|
| `FRED_API_KEY` (free, fred.stlouisfed.org → My Account → API Keys) | ALFRED vintages for 0.3, C1, C2 | not set |
| `DATABASE_URL_READONLY` (`research_reader`, Supabase → Connect → Session pooler) | 0.3, D (MCP, evals, Ask Hot Potato) | not set; needs task 0.2 first |
| `DATABASE_URL` (write; ideally a Supabase dev branch) | schema changes from Phase A on | not set |
| `ANTHROPIC_API_KEY` (console.anthropic.com → API Keys; paid) | D (Ask Hot Potato), E1–E4 | not set |
| Network: `www.cbo.gov` | A6, B4 | returned 403 on 2026-11-03; add to Allowed domains, else manual download |
| Network: `capitalmarkets.fanniemae.com` | A2, B2 | returned 403 on 2026-11-03; same |
| Network: `www.fhfa.gov`, `www.census.gov`, `www.nber.org`, `studentaid.gov` | A2, A3, A5, B4, C1 | untested |

Reachable on 2026-11-03: federalreserve.gov (Z.1, DFA), FRED, newyorkfed.org, freddiemac.com, ginniemae.gov, FRASER, CMHC, Bank of England, Bundesbank, Statbank DK, BIS, ECB, PyPI, CRAN, Supabase, the Anthropic API.

---

## Phase 0 — Foundation (original steps 1–5)

Goal: a validated, Tableau-free base that any later phase can trust.

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| 0.0 | **Audit** of repo, data, schema, frontends and evidence of Claude use | — | Summary delivered in session; key points in `docs/building-with-claude.md` | done |
| 0.1 | **Remove Tableau** and add a repo `CLAUDE.md` (how to work here, pointers to this file, the rules above) | — | `git grep -i tableau` finds nothing in code, config, sites or current docs; the only mentions left are historical records (applied migrations, which are never edited; the build log; this plan's decisions); pipeline tests pass; `web/` builds with native charts only; `CLAUDE.md` committed | in progress |
| 0.2 | **`research_reader` role**: migration with SELECT on `mart` + `core` dimensions, no password; drop `tableau_reader` | 0.1 | Migration applies cleanly on a local Postgres; Eleonora sets the password herself (exact SQL provided); the role cannot read `raw` or write anywhere (test) | needs-approval (built and tested on local Postgres; applying it to production drops `tableau_reader`) |
| 0.3 | **Validation suite** `validation/run.py`, one entry point, independent of `hhdebt` code | 0.1 | Recomputes from the Fed zip: (a) the 4 Z.1 identities every quarter; (b) sector totals vs published Z.1 series for 1990Q3, 2007Q4, 2011Q4, 2026Q2; (c) headlines: 3.2% (1952Q1), 56.4% / $10.77T of $19.10T (2026Q2), 36.1% → 49.2% (2007Q4–2011Q4), "never reversed" as a testable rule; (d) committed snapshots and the database (if reachable) match; (e) known breaks (1968Q1, 1977Q1, 2006Q1, 2010Q1) flagged, new jumps and gaps detected; (f) revisions between two vintages. Writes `validation/REPORT.md` plus a terminal pass/fail table. **Any failure is reported to Eleonora; no number is changed silently.** | in progress |
| 0.4 | **Raw-download provenance**: every extract records URL, retrieval time, bytes and SHA-256 in a manifest | 0.3 | `data/manifest.jsonl` written by every extractor; validation checks the manifest | in progress |
| 0.5 | **Claims register v0** `claims/register.csv` (pulled forward from F1): every headline number in README, `findings.md` and both sites | 0.3 | Each row has claim, value, unit, query or code path, series IDs, vintage and validation status; a test fails if a site number has no register row | todo |
| 0.6 | **Building-with-Claude log** (F5 started now) | — | `docs/building-with-claude.md` exists with an entry per session: tasks, model tier used, tokens/cost where measurable (otherwise "not measured"), errors Claude made and how they were caught | done |
| 0.7 | **Recommendation v1 ("So what")** for taxpayers, policy and mortgage default risk | 0.3, 0.5 | Every claim has a register row and an attached limit (holding ≠ guarantee, correlation ≠ cause, revisions). Hot Potato's "What does this mean?" revised; the "losses land on public balance sheets" overstatement fixed. Preview deployment only | todo |
| 0.8 | **Skill `z1-release-update`**: detect a new release → extract → transform → validation gate → "what moved" note → flag stale copy → draft commit | 0.3, 0.5 | `.claude/skills/z1-release-update/SKILL.md` plus scripts; trigger examples (should fire / should not) recorded; tested by replaying the June → September 2026 releases (archive URLs to verify) before the next live release (10 Dec 2026) | todo |
| 0.9 | **README index and reproduce steps**: one line and link per artifact (per the layout above); how a reader rebuilds every number from a fresh clone | 0.3–0.8 | Every folder in the layout is listed; a fresh clone following the README reproduces the validation report | todo |
| 0.10 | **Prompt archive** `prompts/`: the prompts that set the scope and built each part, from this session on; earlier prompts recovered from the 27–29 Oct session transcript where feasible (token-heavy, done by a subagent) | 0.6 | One dated file per session; each prompt linked to the commits it produced; agent and skill prompts referenced, not duplicated | in progress |

**Phase 0 exit:** validation passes or every failure is explained and approved; register covers all published numbers; skill tested on the replay; Eleonora approves.

---

## Phase A — Core analysis: who holds the risk

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| A1 | **Decompose the 2007–11 jump** by loan type × holder: GSE conservatorship (Sept 2008), FHA/Ginnie Mae expansion, the 2010 student-loan takeover (SAFRA ended new FFEL loans) | 0.3 | Z.1 (have); Ginnie Mae / FHA portfolio data (ginniemae.gov reachable); FSA portfolio data (studentaid.gov untested) | Additive decomposition that sums exactly to +13.1 pp; each component tied to a dated policy event with a primary source; register rows | todo |
| A2 | **Net vs gross public exposure**: subtract risk sold back through CRT (STACR, CAS) and mortgage insurance | A1 | FHFA CRT reports (fhfa.gov untested); Freddie deal data (reachable, may need registration); Fannie deal data (host 403); no CRT before 2013 | Gross and net series 2013+; method note on what "transferred" means (first-loss vs mezzanine, reference-pool notional vs expected loss); net ≤ gross check; estimates labelled | todo |
| A3 | **Full history before 1952**: Z.1 annual 1945–51; earlier from historical sources. Document HOLC (1933), FHA (1934), Fannie Mae (1938) and every later policy step | 0.3 | Z.1 annual (have); Grebler, Blank & Winnick (NBER 1956) and Fed *Banking and Monetary Statistics* (FRASER, reachable); *Historical Statistics of the US*: Millennial ed. is paywalled, the 1975 Bicentennial ed. is free (census.gov untested) | Splice method documented with overlap checks; each pre-1945 point labelled by source and reliability; a policy timeline in which every date is checked against a primary source (statute, agency report) | todo |
| A4 | **Structural breaks**: legislation dates as candidate breaks; Bai-Perron (unknown breaks) and Chow (known dates) | A3 | Derived series (have) | Python implementation cross-checked against R `strucchange` (CRAN reachable) on the same series; HAC errors; result table: candidate date → confirmed / not confirmed / confidence interval; pre-registered in `docs/decisions/breaks.md` before running | todo |
| A5 | **Distribution**: geographic and by income/wealth; who borrows vs who carries the risk | 0.3 | Fed Distributional Financial Accounts (free, reachable); NY Fed CCP: microdata not public; state-level HHDC free; county-level availability to verify; ACS income (census.gov) | Availability note first; maps and tables with source labels; any county-level claim tied to a published NY Fed product, otherwise state level | todo |
| A6 | **Hidden subsidy**: CBO-style fair-value estimate of the subsidy in government-held household credit risk | A2, B1 | CBO fair-value reports (host 403); market risk premia from B1 proxies | Replicates a published CBO figure within a stated tolerance before extending it; sensitivity to the discount-rate assumption; labelled as an estimate | todo |
| A7 | **Causal evidence**: event studies and synthetic control around the 2008 conservatorship and the 2010 student-loan takeover | A1, A5 or A8 | US-level treatment needs donors: other countries (A8) or a state panel (A5) | Pre-registered design; pre-trend and placebo-in-time/space tests; results reported even if null; explicit statement of what is and isn't identified | todo |
| A8 | **International comparison**: US vs Canada (CMHC), Denmark (covered bonds), UK, Germany | 0.3 | CMHC, Statbank DK / Danmarks Nationalbank, Bank of England, Bundesbank, BIS, ECB (all reachable) | Definition crosswalk (what counts as "public" or "guaranteed" in each system); comparable public-share series with stated gaps; no figure without its national source | todo |

**Phase A exit:** every new number in the register; skeptic review (Phase D agents, or a manual pass if D isn't built yet) logged; Eleonora approves.

---

## Phase B — Markets and pricing: how the risk is priced

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| B1 | **Market-implied credit risk**: mortgage-rate spread over Treasuries; agency vs private-label. Did the shift compress the price of household credit risk? | 0.3 | Freddie PMMS (FRED `MORTGAGE30US`) and Treasuries (`DGS10`) free; jumbo vs conforming rates (Optimal Blue on FRED, 2017+, to verify); agency MBS OAS and private-label pricing are **paywalled** (Bloomberg, ICE, Intex) → proxies: PMMS − Treasury blend, jumbo−conforming spread, published spreads from papers (cited, not reused as data) | Each proxy's limits documented; regression of spread on public share with controls (rate level, volatility, prepayment option proxy); stated as association unless A7 supports more | todo |
| B2 | **CRT spreads** as the market's price for the risk the GSEs hand back; link to A2 | A2 | Issuance margins by tranche (Freddie/Fannie deal data, to verify); secondary-market spreads likely paywalled → issuance-only | Spread-per-unit-of-expected-loss series by deal; tie to A2's net exposure; paywall gaps stated | todo |
| B3 | **Scenario engine**: default rate, loss severity, recovery path → losses split public vs private; interactive in the app | A2, B1 | Holdings (have); loss parameters from published GSE/FHA/FSA data and the 2008–12 experience | Python core with unit tests (losses sum to total; public + private = total; zero default → zero loss); a browser version that matches the Python core on fixed cases; preview deployment only | todo |
| B4 | **Policy-regime scenarios**: GSEs released from conservatorship, student-loan reform, recession | B3 | Current status of each debate **looked up at run time** from primary sources (FHFA, Treasury, ED, Congress), not assumed | Each scenario's assumptions dated and sourced; results as ranges, not points | todo |

**Phase B exit:** as Phase A.

---

## Phase C — Forecasting: where the risk is going

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| C1 | **Nowcast** the public share between Z.1 releases from higher-frequency data | 0.4, `FRED_API_KEY` | Monthly G.19 consumer credit (free); weekly H.8 bank loans (free); weekly Fed MBS `WSHOMCB` (have); Fannie/Freddie/Ginnie monthly summaries (to verify); release dates and vintages from ALFRED | Point-in-time panel: each input read at its value public at the nowcast instant; release-lag table per input | todo |
| C2 | **Forecast model** with purged rolling-origin validation, leakage tests, prediction intervals, naive/AR benchmarks, mirroring `repo-market-model` | C1 | — | Pre-registered scoring protocol (`docs/decisions/scoring-protocol.md`); untouched holdout; leakage tests that fail on a deliberately leaked feature; interval coverage reported | todo |
| C3 | **Honest accuracy report**, including where the model fails | C2 | — | Accuracy vs benchmarks with confidence bands; failure cases and regimes listed; failed specifications published | todo |

**Phase C exit:** as Phase A, plus the quant-reviewer agent's sign-off logged.

---

## Phase D — AI research system

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| D1 | **Skill `claim-check`**: trace any number to its query, series and vintage; flag mismatches | 0.5 | Given a sentence with a number, returns the register row and a recompute, or flags it as untraced or mismatched; trigger examples logged | todo |
| D2 | **Skill `chart-from-sql`**: query → publication-quality chart in the project style | 0.3 | Fixed style module (palette validated for contrast in light and dark); source and vintage line on every chart; alt text generated; examples logged | todo |
| D3 | **Skill `research-memo`**: findings → 2-page memo for a named market audience (e.g. MBS desk, rates strategist, policy shop) | D1 | Every number passes `claim-check`; three audience examples logged | todo |
| D4 | **Subagents** in `.claude/agents/`: `analyst` (runs queries), `skeptic` (revisions, definition changes, double counting, vintages), `quant-reviewer` (leakage, overfitting, bad tests), `editor` (style and sourcing) | D1 | Each has a role, tool limits and a logged output format; every objection and its resolution recorded in `claims/review-log.md` | todo |
| D5 | **MCP server `household-credit-mcp`**: Z.1, FRED, NY Fed, CBO | 0.2, 0.5 | Read-only; tools return values with series ID, vintage and caveats; refuses questions the data can't answer (e.g. auto loans by holder, which Z.1 doesn't split); tests, docs and install instructions; publishing to PyPI or an MCP registry only with approval | todo |
| D6 | **"Ask Hot Potato"** (Anthropic API app on the site): tool use against the database; every answer cites its query; refuses unsupported forecasts | D5, `ANTHROPIC_API_KEY` | Answers carry the query and vintage; refusal cases tested; rate limit and cost cap; preview deployment first, production only with approval | todo |
| D7 | **Cowork plugin "Fed Data Desk"**: packages the skills, subagents and MCP for a research team | D1–D5 | Installs cleanly; before/after outputs for three routine jobs | todo |

**Phase D exit:** as Phase A.

---

## Phase E — Evaluation of the AI system

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| E1 | **Question-to-SQL benchmark**: about 100 questions with verified answers; Haiku vs Sonnet vs Opus on accuracy, cost and latency | D5, `ANTHROPIC_API_KEY` | Answers verified independently of any model; scoring rules fixed before the run; cost estimated and approved before running | todo |
| E2 | **Planted-error test**: deliberate errors; catch rate and misses for `skeptic` and `quant-reviewer` | D4 | Errors planted by a script with a hidden key; catch rate with confidence intervals; every miss analysed | todo |
| E3 | **Regression suite**: rerun E1–E2 when prompts or models change; chart results over time | E1, E2 | One command; results appended, never overwritten; chart via `chart-from-sql` | todo |
| E4 | **Red-team "Ask Hot Potato"**: try to get misleading answers or unsupported forecasts | D6 | Attack catalogue, results, guardrails added and remaining failures documented | todo |

**Phase E exit:** as Phase A.

---

## Phase F — Reproducibility, living site, publication

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| F1 | **Source register in the app**: every published number links to query, series, vintage and validation status | 0.5 | Clicking or hovering a number on the site shows its register row | todo |
| F2 | **`make all`** (ingest → validation → models → build) and a GitHub Action running validation and evals on every push; README badges | 0.3, E3 | Fresh clone + `make all` reproduces the published numbers; CI green; evals that cost money run on schedule or by hand, not on every push, unless approved | todo |
| F3 | **Scheduled updates** after each Z.1 release; Claude drafts release notes, Eleonora approves before publishing | 0.8, F2 | The workflow opens a PR with the "what moved" note; nothing publishes without her merge | todo |
| F4 | **Open data**: downloads, a public read-only API, accessible chart descriptions | 0.5, D2 | CSV/JSON downloads with a data dictionary and licence notes; API documented; every chart has a text description | todo |
| F5 | **Building-with-Claude log**: models per task, token cost, errors and how they were caught | 0.6 | Kept up to date every session (started in 0.6) | todo (ongoing) |
| F6 | **Outputs**: working-paper draft (SSRN format); short op-ed | all | Every number passes `claim-check`; `skeptic` and `editor` reviews logged | todo |

---

## Dependency summary

```
0.1 → 0.2 → D5 → D6, E1
0.1 → 0.3 → 0.4 → C1 → C2 → C3
        0.3 → 0.5 → 0.7, 0.8, D1 → D3, D4 → E2
        0.3 → A1 → A2 → B2, B3 → B4
              A3 → A4        A2 + B1 → A6
              A1 + (A5 or A8) → A7
0.3–0.8 → 0.9;   everything → F6
```

## Open questions for Eleonora

None at present.
