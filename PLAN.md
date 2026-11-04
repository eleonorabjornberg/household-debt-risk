# PLAN

**Question every component serves:** who holds America's household credit risk, how is it priced, and where is it going?

**Aim:** a research platform at working-paper standard, plus an AI research system that keeps it current and audits itself. Framed for quantitative research and AI systems for financial markets.

**Owner:** Eleonora Björnberg. She sets the design and approves each phase; Claude builds, checks and drafts.

---

## How to resume (read this first in a fresh session)

1. Read this file, then `docs/building-with-claude.md` (latest entries at the bottom).
2. Find your task. A **track session** (see "Parallel tracks" below) works only on its own track's tasks, in order, on its own branch. The **coordinator session** works on the first task marked `next` that belongs to no track, plus reviews and merges. Check dependencies are `done`.
3. When a task's acceptance criteria are met, set it to `done` (track sessions: in their track's status file, not here), add a log entry, commit, push.
4. **Stop at the end of every phase** and ask for approval before starting the next one.

**Status values:** `done` · `in progress` · `next` · `todo` · `blocked (reason)` · `needs-approval` · `dropped (reason)`

**Current position:** Phase A, run as three parallel tracks (below) since 2026-11-04. A1 done. D1, D2, D4, D5 done early. Coordinator next: pre-registration options for A4, A7 and C2 (for Eleonora to choose), D3, skeptic review of A1. Open from Phase 0: D2 and the `research_reader` test need the Supabase pooler host reachable from the sandbox. Proposed for Eleonora: revise recommendation and site copy that frame the 2008 ratchet as GSE-driven, in light of A1.

## Parallel tracks (from 2026-11-04)

Eleonora approved running Phase A onward as parallel cloud sessions, one per track, each on its own branch cut from `claude/sweet-gates-avwrcs`. Phase-end approvals are unchanged: no track starts a new phase's work without her approval.

| Track | Branch | Tasks, in order | Status file |
|---|---|---|---|
| Data analysis | `claude/track-analysis` | A2, A5, A8 | `tracks/analysis.md` |
| Markets and nowcast | `claude/track-markets` | B1, C1 | `tracks/markets.md` |
| Infrastructure | `claude/track-infra` | F1, F2 (validation and tests only until E3 exists), F4 | `tracks/infra.md` |
| Coordinator | `claude/sweet-gates-avwrcs` | shared files, reviews, merges; A4/A7/C2 pre-registration options; D3; anything not in a track | this file |

**Shared files are the coordinator's.** Tracks do not edit `PLAN.md`, `claims/register.csv`, `docs/building-with-claude.md`, `README.md`, `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/` or the site copy (`atlas/content/`, `web/content/`). Instead a track:
- keeps its status, log notes (tasks, models, subagent tokens, errors and who caught them) and questions for Eleonora in its status file;
- adds register rows to `claims/tracks/<track>.csv` (same header; `check_register.py` reads it), which the coordinator moves into the register on merge;
- writes each analysis under `research/<task>_<name>/` with a "Claude draft" banner on the write-up, as A1 does;
- proposes changes to shared files as a patch or a list in its status file.

**Every track** follows CLAUDE.md and the Rules above, runs its own subagents (cheaper models for routine work), commits through the pre-commit hook, pushes only to its own branch, never touches production, and stops to ask Eleonora (through its status file and its session) for any design choice. Before a task is marked done, the coordinator runs `skeptic` (and `quant-reviewer` for any test or forecast) on it and logs the review in `claims/review-log.md`.

**Merging.** The coordinator fetches a track branch, reviews it, merges it into `claude/sweet-gates-avwrcs`, folds the track's register rows and log notes into the shared files, and tells the track to rebase.

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
| 2026-11-04 | Phase 0 approved; start Phase A. D2 and the `research_reader` test stay open until `DATABASE_URL_READONLY` is set. | Eleonora |
| 2026-11-04 | Four 0.7 copy fixes approved (2026-dollar label, COVID step at 2023Q4, named decline windows, unused facts removed). | Eleonora |
| 2026-11-04 | Add hooks: register check and tests before every commit; no hand edits to `results.json`. | Eleonora |
| 2026-11-04 | Authorship: design, validation and write-up are Eleonora's; Claude's analysis texts are labelled drafts until she rewrites them. | Eleonora |
| 2026-11-04 | Run the plan as parallel tracks (data analysis A2/A5/A8; markets and nowcast B1/C1; infrastructure F1/F2/F4), one cloud session and branch each; this session coordinates, owns the shared files and merges. Higher cost accepted. | Eleonora |
| 2026-11-04 | Rule change: tracks may run in parallel instead of only the first `next` task; phase-end approvals stay. | Eleonora |
| 2026-11-04 | Claude drafts the design options for A4, A7 and C2 with the `preregister` skill; Eleonora chooses. | Eleonora |
| 2026-11-04 | Build the Claude tooling (skills, subagents, MCP) with the whole plan in mind: D1, D2, D4, D5 pulled forward. | Eleonora |
| 2026-11-04 | `ANTHROPIC_API_KEY` added to the environment settings (D6, E1–E4); `fraser.stlouisfed.org`, `www.census.gov`, `www.cbo.gov` allowed (A3, A6). | Eleonora |
| 2026-11-04 | A1 method: Shapley split of public vs private totals, pro rata within each side; the endpoint identity and the chained path are kept as sensitivity (`docs/decisions/a1-decomposition.md`). | Eleonora |
| 2026-11-04 | Accept Claude's recommended option on every CHOICE in the A4, A7 and C2 pre-registrations; freeze them. Frozen commits: A4 `02cc47f`, A7 `206e126`, C2 `192d60c`. | Eleonora |
| 2026-11-04 | A4's R `strucchange` cross-check runs on Eleonora's Mac, once the Python implementation exists. | Eleonora |
| 2026-11-04 | A7: credit Abadie, Diamond and Hainmueller (2010) for the 5× placebo cutoff if the paper confirms it; checked against the paper, then added as a dated deviation. | Eleonora |
| 2026-11-04 | Track questions: accept Claude's recommendation on every item in `docs/decisions/open-questions-2026-11-04.md` (A2 Q1–Q3, A5 Q4, A8 Q5, B1, C1 items 1–9, F2-1, F2-2, F4-1–F4-3). C1 item 6 must agree with the frozen C2 protocol; any conflict goes in as a dated deviation there. | Eleonora |
| 2026-11-04 | A8 national-statistics hosts, `www.sec.gov`/`efts.sec.gov` and `www.freddiemac.com`/`www.fanniemae.com` added to Allowed domains. | Eleonora |
| 2026-11-04 | Live database checks go through the Supabase connector (HTTPS), since raw-TCP Postgres is not supported through this environment's proxy. | Eleonora |
| 2026-11-04 | A7 CHOICE 7: placebo cutoffs become the paper's 20×, 5× and 2× pre-period MSPE (5× quoted in the text), credited to Abadie, Diamond and Hainmueller (2010); the primary ratio-rank inference is unchanged. Dated deviation in `a7-causal-prereg.md`. | Eleonora |
| 2026-11-04 | SEC EDGAR requests declare a User-Agent naming the project and Eleonora's contact email, per the SEC's fair-access policy. The address is read from the `SEC_USER_AGENT` environment variable and kept out of the repo. | Eleonora |
| 2026-11-04 | C1's holdout follows the frozen C2 protocol (2023Q3–2026Q2), not 2024Q3. This applies her rule that C1 agrees with C2; the markets track found the conflict. | Eleonora (rule) / Claude (application) |

## Environment prerequisites

Set in the cloud environment's settings (session title bar → environment menu → **Edit**). A new session picks them up.

| Need | For | Status |
|---|---|---|
| `FRED_API_KEY` (free, fred.stlouisfed.org → My Account → API Keys) | ALFRED vintages for 0.3, C1, C2 | set (2026-11-04) |
| `DATABASE_URL_READONLY` (`research_reader`, Supabase → Connect → Session pooler) | 0.3, D (MCP, evals, Ask Hot Potato) | set; the pooler host does not resolve from the sandbox and the proxy carries HTTPS only, so live checks go through the Supabase connector instead (2026-11-04) |
| `DATABASE_URL` (write; ideally a Supabase dev branch) | schema changes from Phase A on | set (2026-11-04) |
| `ANTHROPIC_API_KEY` (console.anthropic.com → API Keys; paid) | D (Ask Hot Potato), E1–E4 | added to environment settings 2026-11-04 (new sessions pick it up; unset in the coordinator session) |
| Network: `www.federalreserve.gov`, `fred.stlouisfed.org`, `api.stlouisfed.org`, `www.newyorkfed.org` | 0.3, 0.9, 0.8 live run, every Z.1/FRED/NY Fed extract | reachable on 2026-11-03; proxy 403 early on 2026-11-04; allowed again later that day |
| Network: `www.govinfo.gov`, `www.fhfa.gov`, `www.ginniemae.gov` | A1 primary sources, A2 | reachable 2026-11-04 |
| Network: `studentaid.gov`, `www.hud.gov`, `www.federalregister.gov`, `fraser.stlouisfed.org`, `www.fasb.org` | A2, A3, A5 | still blocked 2026-11-04; `www.congress.gov` answers 403 itself (use GovInfo instead) |
| Network: `www.cbo.gov` | A6, B4 | allowed 2026-11-04; the root page still answers 403 (likely the site's own bot check, not the proxy): try the data pages, else manual download |
| Network: `capitalmarkets.fanniemae.com` | A2, B2 | returned 403 on 2026-11-03; same |
| Network: `www.fhfa.gov`, `www.census.gov`, `www.nber.org`, `studentaid.gov` | A2, A3, A5, B4, C1 | untested |

Reachable on 2026-11-03: federalreserve.gov (Z.1, DFA), FRED, newyorkfed.org, freddiemac.com, ginniemae.gov, FRASER, CMHC, Bank of England, Bundesbank, Statbank DK, BIS, ECB, PyPI, Supabase, the Anthropic API. CRAN was listed here, but on 2026-11-04 cran.r-project.org was refused and R is not installed (`docs/decisions/prereg-fact-checks.md` §4).

---

## Phase 0 — Foundation (original steps 1–5)

Goal: a validated, Tableau-free base that any later phase can trust.

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| 0.0 | **Audit** of repo, data, schema, frontends and evidence of Claude use | — | Summary delivered in session; key points in `docs/building-with-claude.md` | done |
| 0.1 | **Remove Tableau** and add a repo `CLAUDE.md` (how to work here, pointers to this file, the rules above) | — | `git grep -i tableau` finds nothing in code, config, sites or current docs; the only mentions left are historical records (applied migrations, which are never edited; the build log; this plan's decisions); pipeline tests pass; `web/` builds with native charts only; `CLAUDE.md` committed | done |
| 0.2 | **`research_reader` role**: migration with SELECT on `mart` + `core` dimensions, no password; drop `tableau_reader` | 0.1 | Migration applies cleanly on a local Postgres; Eleonora sets the password herself (exact SQL provided); the role cannot read `raw` or write anywhere (test) | done (applied to production 2026-11-03; password and `DATABASE_URL_READONLY` still to be set by Eleonora) |
| 0.3 | **Validation suite** `validation/run.py`, one entry point, independent of `hhdebt` code | 0.1 | Recomputes from the Fed zip: (a) the 4 Z.1 identities every quarter; (b) sector totals vs published Z.1 series for 1990Q3, 2007Q4, 2011Q4, 2026Q2; (c) headlines: 3.2% (1952Q1), 56.4% / $10.77T of $19.10T (2026Q2), 36.1% → 49.2% (2007Q4–2011Q4), "never reversed" as a testable rule; (d) committed snapshots and the database (if reachable) match; (e) known breaks (1968Q1, 1977Q1, 2006Q1, 2010Q1) flagged, new jumps and gaps detected; (f) revisions between two vintages. Writes `validation/REPORT.md` plus a terminal pass/fail table. **Any failure is reported to Eleonora; no number is changed silently.** | done (41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN on the 2026-09-11 vintage; see `validation/REPORT.md`. Known limit: holder → bucket mapping comes from `series_catalog.yaml` in both implementations, so a misclassified holder would pass both; for the Phase D skeptic) |
| 0.4 | **Raw-download provenance**: every extract records URL, retrieval time, bytes and SHA-256 in a manifest | 0.3 | `data/manifest.jsonl` written by every extractor; validation checks the manifest | done |
| 0.5 | **Claims register v0** `claims/register.csv` (pulled forward from F1): every headline number in README, `findings.md` and both sites | 0.3 | Each row has claim, value, unit, query or code path, series IDs, vintage and validation status; a test fails if a site number has no register row | done (97 rows: 12 PASS, 82 UNVERIFIED, 1 ESTIMATE, 2 STALE; `claims/check_register.py` passes) |
| 0.6 | **Building-with-Claude log** (F5 started now) | — | `docs/building-with-claude.md` exists with an entry per session: tasks, model tier used, tokens/cost where measurable (otherwise "not measured"), errors Claude made and how they were caught | done |
| 0.7 | **Recommendation v1 ("So what")** for taxpayers, policy and mortgage default risk | 0.3, 0.5 | Every claim has a register row and an attached limit (holding ≠ guarantee, correlation ≠ cause, revisions). Hot Potato's "What does this mean?" revised; the "losses land on public balance sheets" overstatement fixed. Also resolve, **with Eleonora's OK before any number changes** (the 2 STALE rows were fixed with her OK on 2026-11-04): atlas shows 2026-dollar totals ($10.8T of $19.2T) where README uses nominal ($10.77T of $19.10T); atlas COVID step says "barely moves" while showing +2.2 pp; two different pre-GFC decline windows (−5.0 pts vs 5.7 pp); unused web facts (`public1980s`, `covidDelta`, `uncollShare`). Preview deployment only | done (draft `analysis/recommendation.md` read and approved in substance by Eleonora on 2026-11-04; she will replace it with her own text; Claude draft banner stays until then; every number in the register and scanned by `claims/check_register.py`; Hot Potato copy revised; the four listed copy items fixed with her OK on 2026-11-04; branch preview deployments only) |
| 0.8 | **Skill `z1-release-update`**: detect a new release → extract → transform → validation gate → "what moved" note → flag stale copy → draft commit | 0.3, 0.5 | `.claude/skills/z1-release-update/SKILL.md` plus scripts; trigger examples (should fire / should not) recorded; tested by replaying the June → September 2026 releases (June vintage found at `https://www.federalreserve.gov/releases/z1/20260611/z1_csv_files.zip`, wide per-table CSVs; `validation/zparse.py` reads both formats) before the next live release (10 Dec 2026) | done (stale-claims step run against the 104-row register: 0 changed, 12 unchanged, 2 cannot compare, 90 without a check; `stale_claims.py` reads register units, with shares stored as fractions; first live run 10 Dec 2026) |
| 0.9 | **README index and reproduce steps**: one line and link per artifact (per the layout above); how a reader rebuilds every number from a fresh clone | 0.3–0.8 | Every folder in the layout is listed; a fresh clone following the README reproduces the validation report | done (fresh clone of the branch, README steps 1–3 run on 2026-11-04: validation 41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN, all 44 checks identical to the committed report except the run time; tests pass) |
| 0.10 | **Prompt archive** `prompts/`: the prompts that set the scope and built each part, from this session on; earlier prompts recovered from the 27–29 Oct session transcript where feasible (token-heavy, done by a subagent) | 0.6 | One dated file per session; each prompt linked to the commits it produced; agent and skill prompts referenced, not duplicated | done (67 prompts from the 27–29 Oct session; this session's prompts to add at session end) |

**Phase 0 exit:** validation passes or every failure is explained and approved; register covers all published numbers; skill tested on the replay; Eleonora approves.

---

## Phase A — Core analysis: who holds the risk

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| A1 | **Decompose the 2007–11 jump** by loan type × holder: GSE conservatorship (Sept 2008), FHA/Ginnie Mae expansion, the 2010 student-loan takeover (SAFRA ended new FFEL loans) | 0.3 | Z.1 (have); Ginnie Mae / FHA portfolio data (ginniemae.gov reachable); FSA portfolio data (studentaid.gov untested) | Additive decomposition that sums exactly to +13.1 pp; each component tied to a dated policy event with a primary source; register rows || done (exact decomposition in `research/a1_gfc_decomposition/`: Shapley split (Eleonora, 2026-11-04): public growth 6.2 pp, private retreat 6.9 pp; largest public increase Ginnie Mae pools (FHA/VA/USDA), not Fannie/Freddie; reproduces C5 and the published bucket split; 21 register rows; skeptic and quant-reviewer objections R-20261104-1 to -11 resolved; every policy date checked against GovInfo, FHFA or the Fed, see `sources.md`) |
| A2 | **Net vs gross public exposure**: subtract risk sold back through CRT (STACR, CAS) and mortgage insurance | A1 | FHFA CRT reports (fhfa.gov untested); Freddie deal data (reachable, may need registration); Fannie deal data (host 403); no CRT before 2013 | Gross and net series 2013+; method note on what "transferred" means (first-loss vs mezzanine, reference-pool notional vs expected loss); net ≤ gross check; estimates labelled | next |
| A3 | **Full history before 1952**: Z.1 annual 1945–51; earlier from historical sources. Document HOLC (1933), FHA (1934), Fannie Mae (1938) and every later policy step | 0.3 | Z.1 annual (have); Grebler, Blank & Winnick (NBER 1956) and Fed *Banking and Monetary Statistics* (FRASER, reachable); *Historical Statistics of the US*: Millennial ed. is paywalled, the 1975 Bicentennial ed. is free (census.gov untested) | Splice method documented with overlap checks; each pre-1945 point labelled by source and reliability; a policy timeline in which every date is checked against a primary source (statute, agency report) | todo |
| A4 | **Structural breaks**: legislation dates as candidate breaks; Bai-Perron (unknown breaks) and Chow (known dates) | A3 | Derived series (have) | Python implementation cross-checked against R `strucchange` on the same series (R and CRAN not available in the cloud environment; the cross-check runs on Eleonora's Mac, see `docs/decisions/breaks.md`); HAC errors; result table: candidate date → confirmed / not confirmed / confidence interval; pre-registered in `docs/decisions/breaks.md` before running | todo |
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
| D1 | **Skill `claim-check`**: trace any number to its query, series and vintage; flag mismatches | 0.5 | Given a sentence with a number, returns the register row and a recompute, or flags it as untraced or mismatched; trigger examples logged | done (2026-11-04, `.claude/skills/claim-check`, 14 tests) |
| D2 | **Skill `chart-from-sql`**: query → publication-quality chart in the project style | 0.3 | Fixed style module (palette validated for contrast in light and dark); source and vintage line on every chart; alt text generated; examples logged | done (2026-11-04, `.claude/skills/chart-from-sql`, 60 tests; live SQL untested until the DB host is reachable) |
| D3 | **Skill `research-memo`**: findings → 2-page memo for a named market audience (e.g. MBS desk, rates strategist, policy shop) | D1 | Every number passes `claim-check`; three audience examples logged | todo |
| D4 | **Subagents** in `.claude/agents/`: `analyst` (runs queries), `skeptic` (revisions, definition changes, double counting, vintages), `quant-reviewer` (leakage, overfitting, bad tests), `editor` (style and sourcing) | D1 | Each has a role, tool limits and a logged output format; every objection and its resolution recorded in `claims/review-log.md` | done (2026-11-04, six agents in `.claude/agents/`; E2 planted-error test still to run) |
| D5 | **MCP server `household-credit-mcp`**: Z.1, FRED, NY Fed, CBO | 0.2, 0.5 | Read-only; tools return values with series ID, vintage and caveats; refuses questions the data can't answer (e.g. auto loans by holder, which Z.1 doesn't split); tests, docs and install instructions; publishing to PyPI or an MCP registry only with approval | done (2026-11-04, `mcp/household-credit-mcp`, snapshot backend tested, 33 tests; Postgres backend untested live) |
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
