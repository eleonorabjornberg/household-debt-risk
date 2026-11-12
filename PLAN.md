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

Eleonora approved running Phase A onward as parallel cloud sessions, one per track, each on its own branch cut from `claude/sweet-gates-avwrcs`. Phase-end approvals are unchanged: no track starts a new phase's work without her approval. On 2026-11-04 (night) she gave that approval for Phases B–F (see Decisions taken). Her review of each phase's results still comes when its tasks are done.

| Track | Branch | Tasks, in order | Status file |
|---|---|---|---|
| Data analysis | `claude/track-analysis` | A2, A5, A8; then A3, A4 (code, frozen prereg), A7 addendum then A7, A6 | `tracks/analysis.md` |
| Markets and nowcast | `claude/track-markets` | B1, C1; then B2, B3, B4, C2 (frozen protocol), C3 | `tracks/markets.md` |
| Infrastructure | `claude/track-infra` | F1, F2 (validation and tests only until E3 exists), F4; then F3, D3, E2 (pre-registered first), E3, D7 | `tracks/infra.md` |
| Coordinator | `claude/sweet-gates-avwrcs` | shared files, reviews, merges; A4/A7/C2 pre-registration options; anything not in a track. D6, E1, E4 wait for Eleonora (cost or API key) | this file |

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
| 2026-11-04 | Eleonora writes her own `analysis/recommendation.md` at the end of the project, not at the end of Phase A; the Claude draft stays bannered until then. | Eleonora |
| 2026-11-04 | Revise the recommendation and site copy that frame the 2008 ratchet as GSE-driven, in light of A1 (preview deployments only). | Eleonora |
| 2026-11-04 | Merge the three track branches overnight; Phase A still stops for her approval when its tasks are done. | Eleonora |
| 2026-11-04 | Continue into the later phases in parallel, overnight: "I want you to continue on with Phase B once you've merged everything", "You can continue with the other phases as well", "we're already across phases since we're working with separate tracks. Just keep them running overnight … leave human decisions for my review." The tracks take the queues in the table above. Design choices, paid sources, new hosts and cost approvals (D6, E1, E4) are queued for her and not decided. | Eleonora |
| 2026-11-04 | Q6: declare the SEC User-Agent in-shell in one track (analysis), SEC requests only, never written to a file; unblock now (decision card 16:33 UTC, then in chat). | Eleonora |
| 2026-11-04 | GitHub setting "Allow GitHub Actions to create and approve pull requests": done (decision card 16:33 UTC). | Eleonora |
| 2026-11-04 | Q8(a), A7 donors: use the pre-registered fallback, event study for H2/H3 and mechanical check for H4 (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q8(b): confirm weekly S1 = PMMS minus the mean of daily DGS10 over the same week up to the PMMS date (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q8(c): confirm constant-mean prediction as the primary A7 model, AR(1) as sensitivity (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | A4: accept all the structural-break deviations in docs/decisions/breaks.md (she asked why R is not available) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q7: not decided. "We need to research this first, we can't leave it up to judgement." Research the status of German public banks before choosing (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | C2: accept the test-ordering deviation (leakage tests written after the first development scoring) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | C2: accept adding seasonal naive to the Holm family (36 → 42 tests) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | C2 placebo: option (a), demean the shuffled target. The options were written after the result was seen, and the card said so (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q-B2.1: price measure (a) FHFA credit cost ÷ baseline expected loss, with (c) cost alone alongside (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q-B2.2: 2017–2023 prices from deal data (crt.freddiemac.com and EDGAR) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q-B3: scenario presets from both DFAST loss rates (labelled a proxy) and the 2008–12 replay, starting with DFAST (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q-C1c: run the C1 holdout in the same run as C2's holdout, after C2 is frozen (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Q-C1b: pre-register a second C1 run with Freddie Mac and Ginnie Mae, Fannie flat (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | F3-1: drop the refresh.yml schedule and default load to false; load by hand after merging (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | F3-2: a Claude session runs the z1-release-update skill to draft release notes (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | E2-1: accept all the recommendations for CHOICE-1 to CHOICE-9 (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | D7-1: list the plugin more widely (needs a 512–2048 px icon) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | D6, E1, E4 API spend: approve all three, with a cost estimate sent to her first (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Copy review: approve the 2008 copy revision (A1 Shapley split) on the story site, Hot Potato, findings and recommendation draft (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | Copy review: approve the Data/Sources nav links and the /sources and /data intros (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | public_share_2001q1 / _2005q1: keep the facts and their register exceptions (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | FRED_API_KEY secret: later (still open) (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | F2-2 DATABASE_URL_READONLY: not decided; she asked how to add it (decision card, 16:35–16:41 UTC). | Eleonora |
| 2026-11-04 | SEC EDGAR access for the markets track too (B2 deal data, C3), same rules as Q6: User-Agent as a per-command prefix only, never written to a file ("Markets gets access", chat ~16:50 UTC). | Eleonora |
| 2026-11-04 | Unseal the C1+C2 holdout (2023Q3–2026Q2): one joint run after the C2 spec is frozen with her accepted deviations ("Go ahead", chat ~16:55 UTC). | Eleonora |
| 2026-11-04 | E2 CHOICE-1: recall threshold 70% (decision card, 16:53 UTC). | Eleonora |
| 2026-11-04 | E2 CHOICE-2: false-alarm ceiling 25% (decision card, 16:53 UTC). | Eleonora |
| 2026-11-04 | E2 CHOICE-4: fixed seed 20261104, written in before freezing (decision card, 16:53 UTC). | Eleonora |
| 2026-11-04 | E2 CHOICE-10: stratified, each category planted a fixed number of times (decision card, 16:54 UTC). | Eleonora |
| 2026-11-04 | D6 model: decide after E1 shows accuracy per model (decision card, 16:54 UTC). | Eleonora |
| 2026-11-04 | D7-1 plugin icon: B, dot grid (decision card, 16:57 UTC). | Eleonora |
| 2026-11-04 | API spend (E1, D6, E4): not decided; she asked for the explanation again first (decision card, 16:54 UTC). `FRED_API_KEY` check and `DATABASE_URL_READONLY`: later. | Eleonora |
| 2026-11-04 | Efficiency: rotate each track to a fresh session at its next stopping point (short handoff note), and keep PLAN.md's status column in step with the tracks (chat). | Eleonora |
| 2026-11-04 | Everything waiting for her review goes onto a card page like the decision cards (review queue), not into chat (chat). | Eleonora |
| 2026-11-04 | Review queue round 1 (17:00 UTC): accepted as is, all 16 cards: A2 Freddie part, A3, A4, A5, A8, B1, B2 (FHFA 2016), B3 core, C1 and C2 development results, F1, F2, F3, F4, D3, D7. | Eleonora |
| 2026-11-04 | Docket round 3 (17:08–17:12 UTC), C1b pre-registration: **c1b-joint (a)** yes, wait, build and freeze C1b, then one joint C1+C1b+C2 holdout run; **c1b-cells (a)** split the GSE and pool cells by the finer Z.1 series per vintage (nearest earlier vintage where missing); **c1b-pubdate (a)** date each agency report by its PDF creation date, checked against the listing page; **c1b-map (a)** use Freddie's growth rates only, so definition differences cancel (cards). | Eleonora |
| 2026-11-04 | Q7 (card q7-2, after the research she asked for): German public banks are a **third category, 'publicly owned, not guaranteed'**, on the risk-bearer measure (card). | Eleonora |
| 2026-11-04 | A7 multiple testing (card a7-family): **keep the pre-registered family of four** and report the sensitivity as is (card). | Eleonora |
| 2026-11-04 | API spend (card spend-pilot): **yes, run the 10-item pilot with the 1.5× cap** (infra's safeguard: stop and re-estimate if measured cost per item exceeds 1.5× the assumption). Only the pilot is approved; the full E1/D6/E4 build-out is not (card). | Eleonora |
| 2026-11-04 | E2 sample size (card e2-3): no option chosen; her note: "Let's do way fewer errors instead." Treated as direction, not a decision: infra drafts concrete smaller designs with their recall-bar arithmetic for a new card; the E2 freeze stays held (card). | Eleonora |
| 2026-11-04 | Review queue round 2 (17:08 UTC): accepted as is: A7, A2 Fannie part, B3 DFAST preset. FRED_API_KEY repo secret and DATABASE_URL_READONLY Actions secret: Later (cards). | Eleonora |
| 2026-11-04 | C1b cell split, second round (card c1b-cells-2): **(d)**, Freddie's share = its own published portfolio level ÷ that vintage's combined GSE cell (real-time; labelled a proxy; includes multifamily). | Eleonora |
| 2026-11-04 | C1b publication dates, second round (card c1b-pubdate-2): **(a2)**, the PDF creation date where plausible (within 45 days of month end), otherwise the fixed lag; re-issued months labelled "content possibly revised". | Eleonora |
| 2026-11-04 | B4 GSE release (card b4-gse): **(a)**, a range of 0–100% of GSE-book losses turning private, with 25/50/75 points; Ginnie pools stay public. | Eleonora |
| 2026-11-04 | B4 student-loan reform (card b4-student): **(c)**, use a CBO or ED estimate of the shift in lending. Needs a reachable, free source (cbo.gov returned 403 and ED was blocked); if none is found, it comes back to her. | Eleonora |
| 2026-11-04 | Review queue round 3 (17:24 UTC): B3 2008–12 replay and B4 recession range accepted as is. FRED_API_KEY and DATABASE_URL_READONLY secrets: Later (cards). | Eleonora |
| 2026-11-04 | E2 design (card e2-11, CHOICE-11): **(a)**, one of each category: skeptic 8 planted errors in 4 documents, quant-reviewer 6 in 3, plus 2 controls (9 documents, +5 baseline). | Eleonora |
| 2026-11-04 | E2 decision rule (card e2-12, CHOICE-12): **(i)**, E2 is a descriptive pilot: recall with its interval and a per-category table, no supported/against verdict; the confirmatory 70% test waits for a larger run. | Eleonora |
| 2026-11-04 | E2 intervals (card e2-8, changes CHOICE-8): **Wilson 95% intervals primary**, with the within-document clustering stated. | Eleonora |
| 2026-11-04 | API pilot plan (card pilot-plan): **go**. E1 only: build and verify 10 questions (no API cost), then 10 questions × 3 models × 1 run = 30 runs, estimate $1.99, hard cap $2.98; stop if any model's cost per run exceeds 1.5× its estimate; re-check live prices first. | Eleonora |
| 2026-11-04 | Q7 scope (card q7-promo): **(iii)**, look for a primary source on whether promotional banks (1.1%, e.g. KfW) carry a state guarantee before deciding whether they belong in "publicly owned, not guaranteed"; the question then comes back to her. | Eleonora |
| 2026-11-04 | Q7 promotional banks (card q7-promo-2): **(c)**, leave the 1.1% (Bundesbank category of banks with special, development and other central support tasks) unclassified until the Länder promotional-bank statutes can be reached. KfW's funding-side guarantee (KfW law Art. 1a) is on file. Reaching the statute hosts (EUR-Lex, gesetze-im-internet.de, Länder law sites) needs her separate OK; none is added. | Eleonora |
| 2026-11-04 | Review round 5: E2 pre-registration as frozen at 5986353 (with infra's [implementation] choices) and the 10 E1 pilot questions, both accepted. | Eleonora |
| 2026-11-04 | Review queue round 4 (17:31 UTC): A8 Q7 (c) application (Germany's third category, 30.3%) accepted as is. | Eleonora |
| 2026-11-05 | C1b joint holdout (card c1b-unseal, 05:18 UTC): **go**, "unseal and run the joint holdout once". This row is her approval to unseal the sealed holdout and run the joint C2 forecast + C1b nowcast holdout one time, against the C2 prereg `192d60c` and C1b frozen at `8c46906`. | Eleonora |
| 2026-11-05 | B4 student loans (card b4-student-2): **(iii)**, wait for a reachable CBO estimate; the student-loan scenario stays out of B4 for now. | Eleonora |
| 2026-11-05 | B2 2017–2023 (card b2-1723): **(i)**, add a "2017–2023 aggregate cost" section to the B2 README, with register rows and a skeptic pass. | Eleonora |
| 2026-11-05 | Freddie STACR data (card crt-host): **add**, she adds capitalmarkets.freddiemac.com and re-checks crt.freddiemac.com; markets retries afterwards. | Eleonora |
| 2026-11-05 | Q7 promotional banks (card q7-promo-3): **(c)**, keep the 1.1% unclassified and ask for more access first (l-bank.info, a Bundesbank member list). | Eleonora |
| 2026-11-05 | E1 prereg choices (docket round 9): mix (a) stratified by tool × difficulty with about 15 unanswerable; verify (b) PASS register rows first through validation/; writer (a) Claude drafts, she approves the set; turns (a) 4; cache (b) drop the top-level cache; effort (a) medium for all three; reps (b) 3; framing (b) confirmatory (T and R in the note); lookup_claim (a) keep all 10 tools; seed (a) 20261104; scoring (a) pilot rule; baseline (b) no-tools run on one model (up to $4); holdout (b) hold back 20 questions for E3; cost cap (a) $31. The cap card sets the ceiling only; the full run still needs her separate spend OK. | Eleonora |
| 2026-11-05 | C1b holdout bug (card c1b-dev-1): **(a)**, rows whose target quarter no Z.1 has published are recorded as "no target"; dated deviation in the frozen docs; rerun once. Her approval row for the rerun is added after markets' fix commit. | Eleonora |
| 2026-11-05 | E1 unit of analysis (e1-unit): **(ii)** every repetition counted, standard errors clustered by question. | Eleonora |
| 2026-11-05 | E1 threshold T (e1-T): **70%**. | Eleonora |
| 2026-11-05 | E1 H3 (e1-h3): **(b)** raise unanswerable questions to about 25 of 100 (part of the set redrafted). R not yet given. | Eleonora |
| 2026-11-05 | E1 no-tools baseline model (e1-base): **Opus**. Not a spend OK. | Eleonora |
| 2026-11-05 | Access (acc-lbank, acc-eu, acc-bbk): **add** www.l-bank.info, **add** publications.europa.eu (both added by her), **go** search bundesbank.de. She also added capitalmarkets.freddiemac.com (crt-host). | Eleonora |
| 2026-11-05 | Reviews: rv-c1b-frozen **ok**, rv-b4-gse **ok**, rv-e1-pilot **ok**, rv-b2-1723 **ok**, rv-e1-set **ok** (approved as is, after choosing h3 (b); see card e1-set-h3). | Eleonora |
| 2026-11-05 | E1 set vs H3 (e1-set-h3): **replace** about 10 answerable questions with unanswerable ones (still 100); she reviews only the changed questions before the freeze. | Eleonora |
| 2026-11-05 | E1 H3 threshold (e1-R2): **R = 70%**. | Eleonora |
| 2026-11-05 | E1 holdout share of unanswerable questions (e1-holdback): hold back **about 5**, in proportion. | Eleonora |
| 2026-11-05 | C1b holdout rerun approval (c1b-dev-1 (a), chosen 14:10 UTC): unseal the joint C2 + C1b holdout and run it once, with the dated "no target" deviation in cddd3ca and the re-hashed FREEZE.json. | Eleonora |
| 2026-11-05 | E1 clustering (e1-cluster, chosen 14:25 UTC): **(b)** question bootstrap, 10,000 draws, seed 20261104, percentile intervals, paired-difference bootstrap for H2. | Eleonora |
| 2026-11-05 | E1 "supported" rule (e1-support, chosen 14:25 UTC): **(i)** 95% interval at or above the threshold AND Holm-adjusted one-sided p < 0.05. | Eleonora |
| 2026-11-05 | A8 German promotional-bank label (a8-promo, chosen 14:44 UTC): **(b)** relabel as in (a), plus a context note on the four liability guarantees. | Eleonora |
| 2026-11-05 | B2 STACR 2017+ (chosen 15:55 UTC): measure **(ii)** spread plus an FHFA-style multiple (spread ÷ baseline expected loss under FHFA's 2016 baseline, a labelled assumption; reference-pool UPB from another source); tranches **(b)** each seniority class (M-1, M-2, B) separately; "(Indicative)" retained tranches **(b)** kept, flagged; LIBOR→SOFR **(b)** add a published LIBOR–SOFR spread adjustment to pre-SOFR deals, source checked first. | Eleonora |
| 2026-11-05 | C3 per-forecast errors (c3-errors, chosen 15:55 UTC): **(b)** a second, separately gated run of the frozen C2 holdout step that writes only the per-forecast table (same frozen code and hashes, no new scores or verdicts); dated deviation, recorded as a second opening of the holdout. | Eleonora |
| 2026-11-05 | C3 "beats" rule (c3-rule, chosen 15:55 UTC): **(b)**, the option she chose at the freeze: correct the record with a dated erratum (the freeze recorded (a) by a coordinator transcription error) and recompute the verdicts from committed results. | Eleonora |
| 2026-11-05 | C3 holdout count (c3-hcount, chosen 15:55 UTC): **(b)** dated deviation (holdout defined by target quarter), and also report the origin-based subset (uses the c3-errors (b) table). | Eleonora |
| 2026-11-05 | C3 rule (b) level (c3-b-level, chosen 18:54 UTC): **(iv)** 5%, the coverage test (Kupiec) only: 3 "beats". The coordinator's recommended option; rolling Z-DAMP's independence result (p = 0.027) is reported beside it. | Eleonora |
| 2026-11-05 | C3 rule (b) for models without intervals (c3-b-nointv, chosen 18:54 UTC): **(c)** report as undetermined. The coordinator's recommended option. | Eleonora |
| 2026-11-05 | A8 holder share (a8-holder, chosen 18:54 UTC): **(b)** relabel the four places to the category label with the DZ Bank caveat, and show savings banks + Landesbanken (29.1%) as the publicly owned figure with the 1.1% beside it as unclassified. The coordinator's recommended option. | Eleonora |
| 2026-11-05 | B2 LIBOR→SOFR source (b2-sofr-src, chosen 18:54 UTC): **(a)** the Regulation ZZ figure, 11.448 bps. The coordinator's recommended option. | Eleonora |
| 2026-11-05 | B2 reference-pool UPB (b2-upb, chosen 18:54 UTC): **(a)** no UPB, per-tranche measure only. The coordinator's recommended option. | Eleonora |
| 2026-11-05 | B2 tranches without a multiple (b2-empty, chosen 18:54 UTC): **(a)** report as is: spreads for all classes, multiples for B-2 only, with the attach-point caveat. The coordinator's recommended option. | Eleonora |
| 2026-11-05 | Review queue (18:55 UTC): approved the E1 redraft of the 10 replaced questions (rv-e1-redraft), accepted the joint holdout write-up as a draft to rewrite (rv-holdout), approved the A8 relabel copy with the guarantees note (rv-a8-promo). | Eleonora |
| 2026-11-05 | E1 spend (e1-spend, chosen 20:59 UTC): **OK** (a): run the main run and the Opus baseline, $31 total cap. No recommendation was given on this card. | Eleonora |
| 2026-11-05 | Review queue (20:59 UTC): approved the A8 holder-share relabel copy as is (rv-a8-holder; editor points ana-e17, e19, e20 not taken up), the C3 final accuracy report (rv-c3-final) and the B2 STACR 2017+ section (rv-b2-stacr17), each as a Claude draft she will rewrite. | Eleonora |
| 2026-11-05 | E1 stop rule (e1-stoprule, chosen 21:15 UTC): (a) the per-model overrun stop (3× pilot mean cost per loop) applies only after 24 loops per model (10%); the $31 cap, the pre-call guard and the 10% checkpoint stay. Dated deviation from the frozen prereg. No recommendation was given on this card. | Eleonora |
| 2026-11-05 | E1 cost (e1-cost, chosen 21:15 UTC): (b) restore the top-level prompt cache, reversing CHOICE-E1-5 (b); cap stays $31. Dated deviation from the frozen prereg. No recommendation was given on this card. | Eleonora |
| 2026-11-05 | E1 stop recalibration (e1-stop2, chosen 21:40 UTC): **recal**: reset each model's per-model overrun stop to 1.5× its measured mean cost per loop from the 27 loops run (Sonnet $0.047, Opus $0.098, Haiku $0.0020); keep the $31 cap, the pre-call guard and the 10% checkpoint. Dated deviation from the frozen prereg. No recommendation was given on this card. | Eleonora |
| 2026-11-05 | E1 resume (e1-resume, chosen 21:40 UTC): **resume** run-2026-11-05b from loop 80, with the resume feature tested offline first. The write-up must say the first 79 loops ran before this deviation. No recommendation was given on this card. | Eleonora |
| 2026-11-05 | Review queue (21:41 UTC): approved the B3 /scenarios page and copy as Claude drafts (rv-b3-page); add the Scenarios nav link on the branch (rv-b3-nav). | Eleonora |
| 2026-11-06 | E1 baseline (e1-baseline, chosen 04:50 UTC): **(a)** resume the Opus baseline from loop 25 with the fixed checkpoint (about $2.04 more, $31 cap unchanged); record the false stop as deviation D6 (code fix, no design change). No recommendation was given on this card. | Eleonora |
| 2026-11-06 | D6 model (d6-model, chosen 04:55 UTC): **Sonnet** answers questions in Ask Hot Potato. No recommendation was given on this card. No note. | Eleonora |
| 2026-11-06 | D6 spend (d6-spend, chosen 04:57 UTC): **cap $20** for building D6 and the E4 red-team (developer testing only; not visitor use). Same safeguards as E1: pre-call guard, 10% checkpoint, stop and report on any overrun. Separate from the $31 E1 cap. No recommendation was given on this card. No note. | Eleonora |
| 2026-11-06 | D6 preview (d6-preview, chosen 04:57 UTC): **tight**: 5 questions per visitor per day and a $2/day hard stop for the whole app, enforced in the app, on the preview deployment only. Production needs her separate OK. No recommendation was given on this card. No note. | Eleonora |
| 2026-11-06 | D6 limit store (d6-store, chosen 14:38 UTC): **(a) Vercel KV / Upstash Redis on its free tier, added by her to the atlas Vercel project.** Claude codes the adapter; she adds the store herself. No recommendation was given on this card. No note. | Eleonora |
| 2026-11-06 | D6 data source (d6-data, chosen 14:39 UTC): **(b) read-only queries to the production mart through Supabase's API** with the publishable key, as atlas does at build time. This authorizes read-only mart queries at question time and nothing else on production. No recommendation was given on this card. No note. | Eleonora |
| 2026-11-06 | D6 preview variables (d6-key, 14:39 UTC): **later**; the preview variables are not added yet, so D6 stays local. No note. | Eleonora |
| 2026-11-06 | E1 results note (rv-e1-results, 14:39 UTC): **approved as a Claude draft**. It stays UNVERIFIED and off the sites until her own text replaces it. No recommendation was given. No note. | Eleonora |
| 2026-11-06 | D6 unplanned build test (rv-d6-buildtest, 14:39 UTC): **seen; keep it in the D6 ledger** ($0.509085 of the $20 cap). No note. | Eleonora |
| 2026-11-06 | D6 production read (d6-martcheck, 19:53 UTC): **(a) yes: one run of the seven read-only mart SELECTs from the infra session, with the publishable key and no model call; results compared with the snapshot and reported.** This authorizes nothing else: no writes, no repeat runs, no deployment change. No note. | Eleonora |
| 2026-11-06 | E4 P2 and the held-out set (e4-p2-heldout, 19:53 UTC): **(a) run P2 now as built, at most $4.00 from the $20 D6+E4 cap.** The write-up reports the 4 held-out A1/A2 prompts as seen before the run and keeps them out of the clean held-out score. No note. | Eleonora |
| 2026-11-06 | E4 P1 hand labels (rv-e4-p1-labels, 19:54 UTC): **approved as a Claude draft**; they stay UNVERIFIED in any write-up until she checks them. No note. | Eleonora |
| 2026-11-06 | E4 Ask guardrails and grounding v2 (rv-e4-guardrails, 19:54 UTC): **approved as built** (code on the branch, not deployed). No note. | Eleonora |
| 2026-11-06 | Vercel team access (in chat, ~20:40 UTC): **"make it"**, lifting her earlier rule against a team-access request. | Eleonora |
| 2026-11-06 | Vercel production (in chat, ~20:50 UTC): **promote `ad3611f` to production**. Atlas promoted (`dpl_4rMG3uKEa4T4RoCJQyJcq6QwWqHL`). | Eleonora |
| 2026-11-06 | Vercel project `household-debt-risk-web` (in chat, ~21:00 UTC): **"a useless duplicate"**. It is not promoted or maintained as a deploy target; household-debt-risk.vercel.app (atlas) is the production site. No deletion requested. | Eleonora |
| 2026-11-06 | Merge into `main` (in chat, ~21:05 UTC): **"merge into main"**; merged as eleonorabjornberg/household-debt-risk#1 (`02515b2`). Site address (in chat, ~21:12 UTC): **free `.vercel.app` name**; hot-potato.vercel.app was taken, so hot-potato-credit.vercel.app was added. | Eleonora |
| 2026-11-07 | Challenge readiness replies (on the review-queue artifact): she **added the cbo.gov limit (A6, B4) to her write-up**; **delete the duplicate Vercel project** `household-debt-risk-web` (not found in her Vercel team from this session, so not deleted by Claude; see log); she will **submit a GitHub link**, not a ZIP. Asked what E4 P2 needs. Live site (her report): **loads, but looks the same as when she started**. | Eleonora |
| 2026-11-07 | Decision docket round 43. **`site-visible` (b): one site.** Move the `web/` pages (scenarios, how it was built, methods) into Hot Potato at the same address, with a visible top bar. Work goes on the branch first, then a preview; production only after her OK on the preview. **`sources-verify` (a):** write independent checks in `validation/run.py` for all 22 data numbers on Hot Potato. Each recomputes from the raw series, not from the analysis code's output. The 2 design constants get a new DEFINITION status, and `/sources` is rebuilt on a preview. No spend. Failing checks are reported, not adjusted. | Eleonora |
| 2026-11-07 | Review queue round 27, `rv-one-site-preview`: **promote**. The one-site build (2289a2d) went to production. | Eleonora |
| 2026-11-07 | Decision docket round 45, wording raised by the analysis reviewers. **`copy-privlabel` (c):** rename the pile to "private securitization and REITs, incl. card ABS". **`copy-2026-dollars` (a):** label the base as 2026Q3 dollars, or footnote it. **`copy-all-uncoll` (a):** drop "all" from "all household debt with no collateral". **`copy-placebo` (a):** reword to "no detectable excess (p ≈ 0.30, low power)" and state the placebo pool. **`placebo-stored` (b):** keep the stored value 0.3025. | Eleonora |
| 2026-11-07 | Review queue round 28, `rv-h-checks`: **promote**. The H1–H22 checks, DEFINITION status and new `/sources` go to production. | Eleonora |
| 2026-11-07 | Review queue round 29, `rv-copy45-live`: **ok**. The live round-45 wording and the short canvas label "Private sec. & REITs" are approved. | Eleonora |
| 2026-11-07 | Decision docket round 46, `copy-placebo-elsewhere` **(b)**: use the Hot Potato placebo wording ("no detectable excess (p ≈ 0.30, low power)") in README.md, analysis/findings.md and web/content/story.ts. | Eleonora |
| 2026-11-08 | Decision docket round 47: `copy-rejects-readme` **(a)**, README.md:15 "The data rejects that as a general pattern" becomes "The data does not support that as a general pattern"; `copy-gap-noise` **(a)**, analysis/findings.md:10 "That gap is noise." becomes "That gap is not statistically detectable."; `copy-they-dont` **(b)**, delete "They don't." in web/content/story.ts:147 and let the placebo sentence carry it. | Eleonora |
| 2026-11-08 | "All edits should reach the live site": production redeployed from daf6522. | Eleonora |
| 2026-11-08 | Docket 48 site-findings (b): add a /findings page to Hot Potato that renders analysis/findings.md. A track builds it; preview first, production only after a separate OK. | Eleonora |
| 2026-11-09 | Docket 49 findings-register (a): add a claims/register.csv row for every unregistered number in analysis/findings.md (~380), add findings.md to the hook scan, then a preview of /findings. | Eleonora |
| 2026-11-09 | Docket 49 findings-all (a): drop "all" in analysis/findings.md:14 ("51% of uncollateralized household debt"), to match Hot Potato. | Eleonora |
| 2026-11-09 | Docket 51 repo-public (b): rewrite history to remove both of her email addresses (all branches force-pushed; she authorized that force push with this choice), then she flips the repo to public herself. | Eleonora |
| 2026-11-09 | Docket 51 findings-prod (a): promote /findings to production once the hook passes on the merged branch, tests pass and the preview is READY; she checks the live page after. | Eleonora |
| 2026-11-09 | Docket 51 findings-rounding (a): change the eight double-rounded numbers in analysis/findings.md to the singly rounded value (55%, 102%, +8.4, +8.3, +0.2, 69%, 69%, 8.2%), update their register rows, re-sync the /findings copy. | Eleonora |
| 2026-11-09 | Docket 51 findings-scan (a): trace the 251 display-match numbers in findings.md, add rows where needed, then make the scan require a row citing the file and line. | Eleonora |
| 2026-11-09 | Review 30 rv-findings-preview: ok (the /findings preview looks right). | Eleonora |
| 2026-11-09 | Docket 52 rewrite-main (b): force-push the rewritten history to every branch except `main`; `main` is rewritten at its next reviewed merge, so production is not rebuilt from older content now. | Eleonora |
| 2026-11-09 | Review round 31 rv-findings-live: **ok**, the live /findings page (production 5879127) looks right. No note. | Eleonora |
| 2026-11-09 | In chat: "Make sure our quantitative work is visible there as well", meaning the live site. The research write-ups (A–C) go onto Hot Potato as labelled Claude drafts: built on a branch, then a preview, with production only after her OK on the preview. E1 stays off the sites, per her 2026-11-06 rv-e1-results decision, unless she changes that. | Eleonora |
| 2026-11-09 | Review round 32 rv-research-preview: **ok-prod**, the /research preview (7efabcc) looks right; promote to production. No note. | Eleonora |
| 2026-11-09 | Review round 32 rv-research-status: **sync**, update the stale status lines in the A3, A4, B1, B2 and B3 READMEs to match PLAN. No note. | Eleonora |
| 2026-11-10 | Review round 33 rv-research-live: **ok**, the live /research pages (production 853747e) look right. No note. | Eleonora |
| 2026-11-10 | In chat: the /research and /findings tables are badly aligned ("Why is the text aligned to the left only?"); she loves the vivid orange and pink and wants the site "more fun, colorful and aesthetic"; /scenarios gives her no overview; /how-it-was-built is factually incorrect. | Eleonora |
| 2026-11-10 | Docket 53 voice-53: **(a)** rewrite the site and research pages with the eleonora-writing skill; keep the "Claude draft" banner on them until she approves each page; amend the CLAUDE.md rule to say so. | Eleonora |
| 2026-11-10 | Docket 53 e1-site-53: **(a)** add E1 to /research as a Claude draft, marked UNVERIFIED (branch first; production only after her review-queue OK). Replaces her 2026-11-06 rule keeping E1 off the sites. | Eleonora |
| 2026-11-10 | Docket 53 d6-key-53: **(a)** she adds the preview API key and the KV store herself, then D6 is deployed to a preview only. Note: "just tell me which api key and how". | Eleonora |
| 2026-11-10 | Docket 53 visibility-53: **(a)** she makes the repository public herself. purge-53: **(b)** no history purge needed. | Eleonora |
| 2026-11-10 | In chat: add "a proper analytical dashboard"; the home page stays, but the data should be actionable. | Eleonora |
| 2026-11-10 | Docket 54 dash-reader-54: **(a)** the dashboard is for a market reader. dash-scope-54: **(a)** Core: headline tiles with change on the quarter and the year (total debt, public share, home coverage, serious-delinquency transitions), holder-mix and loan-type panels, filters for date range and loan type. dash-place-54 (note, no option): "A new dashboard tab, merge it with findings. Don't duplicate effort, just display the findings in a better way. Make sure findings don't get lost." | Eleonora |
| 2026-11-11 | Review queue round 34 (rv-dashboard-34): **ok-prod**, release the /dashboard tab and the site fixes since 853747e to production. | Eleonora |
| 2026-11-11 | Docket 55 cbo-repo-55: **(b)**, add github.com/US-CBO/cbo-data as a source (catalog entry and provenance record) for budget-side context only, and use the Direct Loan account outlays as a labelled proxy in B4's student-loan scenario. This reopens B4 (iii). | Eleonora |
| 2026-11-11 | Docket 55 gradients-55: **(a)**, make every gradient a flat colour. Her note: "dots, stripes and other patterns and solid colors are fine, gradients are not". | Eleonora |
| 2026-11-11 | Home header (rv-header-36): of the live header she said "i don't like this"; after the clipped halftone discs were removed on the branch, she said "release it to production". Released 034e16d (with the gradient-free build, the workflow schema and the B4 CBO proxy README already on the branch). | Eleonora |
| 2026-11-11 | Review queue 35/36: rv-gradients-35 **ok-prod**, rv-schema-35 **ok-prod**, rv-header-36 **ok-prod** (all three live in the 034e16d release); rv-b4-cbo-35 **ok**, keep the CBO proxy on the branch as a labelled Claude draft. | Eleonora |
| 2026-11-11 | Docket 56 b4-student-proxy-map: **(b)**, pair the CBO proxy with the Education Department's loan-volume estimate in its rule (91 FR 23768) as the volume side, after a source check. Still no loss-engine change until she reviews it. | Eleonora |
| 2026-11-11 | Review queue 37: rv-b4-ed-37 **ok**, keep the ED loan-volume side of the B4 student-loan scenario on the branch as a labelled UNVERIFIED Claude draft. Not released to production; no loss-engine change. | Eleonora |
| 2026-11-11 | In chat: "caveats belong in one place only: limits". The /methods Caveats section is now **Limits** (`/methods#limits`) and is the only place caveats appear. The scenarios caveat list, the dashboard student-loan note and the scenario tool's holder-vs-bearer line were folded into it, and each spot now links to `/methods#limits`. |
| 2026-11-11 | AskUserQuestion on the Ask API and MCP: **"Rename to limits"**. The `caveats` field is now `limits` in both, built from one shared file, `claims/limits.json`, which /methods#limits also reads (13 items: the 11 site items plus 2 API-only items). |
| 2026-11-11 | In chat, on the write-ups getting only a light pass: **"sure, as long as the mcp/api has it"**. A hard cut of the research pages on the site is OK, provided the full write-ups stay available through the MCP and the Ask API. |
| 2026-11-12 | Review queue 39/40: rv-potato-38, rv-review-39, rv-limits-40, rv-voice-40, rv-api-40, rv-cut-40 all **ok-prod** ("OK: release this to production"). Held before deploy: the branch head also carries the B4 ED loan-volume draft, which rv-b4-ed-37 kept off production and which no card offered for release; review card rv-release-41 asks her. | Eleonora |

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
| Source: github.com/US-CBO/cbo-data (git clone works; api.github.com 403) | B4 | budget-side context only, per cbo-repo-55 (b) 2026-11-11; no fair-value estimates (A6) |
| Network: `www.cbo.gov` | A6, B4 | allowed 2026-11-04; the root page still answers 403 (likely the site's own bot check, not the proxy): try the data pages, else manual download |
| Network: `capitalmarkets.fanniemae.com` | A2, B2 | returned 403 on 2026-11-03; same |
| Network: `www.fhfa.gov`, `www.census.gov`, `www.nber.org`, `studentaid.gov` | A2, A3, A5, B4, C1 | untested |
| Network, as seen from the track sessions: `www.sec.gov`, `efts.sec.gov`, `www.freddiemac.com`, `www.fanniemae.com` (and other freddiemac/fanniemae hosts), `api.census.gov`, `www2.census.gov`, `www.usmi.org`, `alfred.stlouisfed.org`, CMHC, Bank of England, Bundesbank, Statbank DK, BIS, ECB | A2 Q1(b), A8, C1 2c | proxy 403 on 2026-11-04 (reported by the analysis and markets tracks), although the SEC hosts were meant to be allowlisted; `api.stlouisfed.org` is enough for vintages. Check the track environment's network policy |

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
| A2 | **Net vs gross public exposure**: subtract risk sold back through CRT (STACR, CAS) and mortgage insurance | A1 | FHFA CRT reports (fhfa.gov untested); Freddie deal data (reachable, may need registration); Fannie deal data (host 403); no CRT before 2013 | Gross and net series 2013+; method note on what "transferred" means (first-loss vs mezzanine, reference-pool notional vs expected loss); net ≤ gross check; estimates labelled | done: Freddie Mac part and Fannie Mae part (`f32dc21`, `4487f10`) accepted by Eleonora 2026-11-04 |
| A3 | **Full history before 1952**: Z.1 annual 1945–51; earlier from historical sources. Document HOLC (1933), FHA (1934), Fannie Mae (1938) and every later policy step | 0.3 | Z.1 annual (have); Grebler, Blank & Winnick (NBER 1956) and Fed *Banking and Monetary Statistics* (FRASER, reachable); *Historical Statistics of the US*: Millennial ed. is paywalled, the 1975 Bicentennial ed. is free (census.gov untested) | Splice method documented with overlap checks; each pre-1945 point labelled by source and reliability; a policy timeline in which every date is checked against a primary source (statute, agency report) | done (accepted by Eleonora 2026-11-04; `research/a3_pre1952/`) |
| A4 | **Structural breaks**: legislation dates as candidate breaks; Bai-Perron (unknown breaks) and Chow (known dates) | A3 | Derived series (have) | Python implementation cross-checked against R `strucchange` on the same series (R and CRAN not available in the cloud environment; the cross-check runs on Eleonora's Mac, see `docs/decisions/breaks.md`); HAC errors; result table: candidate date → confirmed / not confirmed / confidence interval; pre-registered in `docs/decisions/breaks.md` before running | done (accepted by Eleonora 2026-11-04; `research/a4_breaks/`; R cross-check added after, `9f10f80`, agrees within the pre-registered tolerance) |
| A5 | **Distribution**: geographic and by income/wealth; who borrows vs who carries the risk | 0.3 | Fed Distributional Financial Accounts (free, reachable); NY Fed CCP: microdata not public; state-level HHDC free; county-level availability to verify; ACS income (census.gov) | Availability note first; maps and tables with source labels; any county-level claim tied to a published NY Fed product, otherwise state level | done (accepted by Eleonora 2026-11-04; `research/a5_distribution/`) |
| A6 | **Hidden subsidy**: CBO-style fair-value estimate of the subsidy in government-held household credit risk | A2, B1 | CBO fair-value reports (host 403); market risk premia from B1 proxies | Replicates a published CBO figure within a stated tolerance before extending it; sensitivity to the discount-rate assumption; labelled as an estimate | blocked (CBO replication: `cbo.gov` returns 403) |
| A7 | **Causal evidence**: event studies and synthetic control around the 2008 conservatorship and the 2010 student-loan takeover | A1, A5 or A8 | US-level treatment needs donors: other countries (A8) or a state panel (A5) | Pre-registered design; pre-trend and placebo-in-time/space tests; results reported even if null; explicit statement of what is and isn't identified | done: accepted by Eleonora 2026-11-04 (`a993b8e`, `3fc159f`); family of four kept |
| A8 | **International comparison**: US vs Canada (CMHC), Denmark (covered bonds), UK, Germany | 0.3 | CMHC, Statbank DK / Danmarks Nationalbank, Bank of England, Bundesbank, BIS, ECB (all reachable) | Definition crosswalk (what counts as "public" or "guaranteed" in each system); comparable public-share series with stated gaps; no figure without its national source | done, partial by design (accepted by Eleonora 2026-11-04; `research/a8_international/`); Q7 settled: publicly owned, not guaranteed 29.1%, promotional banks 1.1% unclassified (q7-promo-2 (c), `39e0578`); q7-promo-3 (c) 2026-11-05: stays unclassified, more access asked for; 2026-11-05 she added www.l-bank.info and publications.europa.eu and said go on a bundesbank.de search; analysis tries them; a8-promo (b) chosen 2026-11-05: relabel plus guarantees note, copy approved 18:55 UTC (rv-a8-promo); a8-holder (b) chosen 18:54 UTC: analysis relabels and shows 29.1% publicly owned with 1.1% unclassified; copy approved 20:59 UTC (rv-a8-holder) |

**Phase A exit:** every new number in the register; skeptic review (Phase D agents, or a manual pass if D isn't built yet) logged; Eleonora approves.

---

## Phase B — Markets and pricing: how the risk is priced

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| B1 | **Market-implied credit risk**: mortgage-rate spread over Treasuries; agency vs private-label. Did the shift compress the price of household credit risk? | 0.3 | Freddie PMMS (FRED `MORTGAGE30US`) and Treasuries (`DGS10`) free; jumbo vs conforming rates (Optimal Blue on FRED, 2017+, to verify); agency MBS OAS and private-label pricing are **paywalled** (Bloomberg, ICE, Intex) → proxies: PMMS − Treasury blend, jumbo−conforming spread, published spreads from papers (cited, not reused as data) | Each proxy's limits documented; regression of spread on public share with controls (rate level, volatility, prepayment option proxy); stated as association unless A7 supports more | done, inconclusive (accepted by Eleonora 2026-11-04; `research/b1_market_pricing/`) |
| B2 | **CRT spreads** as the market's price for the risk the GSEs hand back; link to A2 | A2 | Issuance margins by tranche (Freddie/Fannie deal data, to verify); secondary-market spreads likely paywalled → issuance-only | Spread-per-unit-of-expected-loss series by deal; tie to A2's net exposure; paywall gaps stated | done (all parts approved as Claude drafts): FHFA 2016 tables accepted by Eleonora 2026-11-04; 2017–2023 aggregate-cost section written per b2-1723 (i) (3a30362, skeptic s38–s43 answered 9f1bbd6; register rows folded), accepted by Eleonora 2026-11-05; capitalmarkets.freddiemac.com added 2026-11-05, markets retries the STACR download; 2017+ choices 2026-11-05: measure (ii), tranches (b), indicative (b), SOFR (b); per-tranche 2017+ table built (`5da961f`, `4702af3`; 274 tranches in her classes, intermediate); she chose b2-sofr-src (a), b2-upb (a), b2-empty (a) 18:54 UTC; STACR 2017+ section written (`392a1bf`, `7b64703`; skeptic mkt-s49–s54; 274 = 50 with a multiple + 218 + 3 + 3); approved by Eleonora 20:59 UTC as a Claude draft to rewrite (rv-b2-stacr17) |
| B3 | **Scenario engine**: default rate, loss severity, recovery path → losses split public vs private; interactive in the app | A2, B1 | Holdings (have); loss parameters from published GSE/FHA/FSA data and the 2008–12 experience | Python core with unit tests (losses sum to total; public + private = total; zero default → zero loss); a browser version that matches the Python core on fixed cases; preview deployment only | in progress: core engine accepted by Eleonora 2026-11-04; DFAST preset (`e58b420`) accepted 2026-11-04; 2008–12 replay (`d5f2953`, skeptic `8ab6986`) accepted; app version (web /scenarios, URL only, browser parity tests) built by markets and merged 2026-11-05 (bb3a731); page and copy approved as Claude drafts 2026-11-05 (rv-b3-page); nav link added on the branch (rv-b3-nav); preview deployment not checked (Vercel team scope 403) |
| B4 | **Policy-regime scenarios**: GSEs released from conservatorship, student-loan reform, recession | B3 | Current status of each debate **looked up at run time** from primary sources (FHFA, Treasury, ED, Congress), not assumed | Each scenario's assumptions dated and sourced; results as ranges, not points | recession range accepted; GSE range built (290fcb8, skeptic answered 9f59e00), accepted by Eleonora 2026-11-05; student-loan scenario reopened 2026-11-11 (cbo-repo-55 (b)): Direct Loan account outlays from US-CBO/cbo-data as a labelled proxy, sent to the markets track; proxy built on claude/track-markets (8bec074, skeptic answered 9cd576b), merged 2026-11-11, reviewed OK as a draft (rv-b4-cbo-35); docket 56 (b): add ED's loan-volume estimate (91 FR 23768) as the volume side after a source check, sent to the markets track 2026-11-11; built and merged 2026-11-11 (ED RIA Table 3.1 via GovInfo PDF, 15 UNVERIFIED register rows, skeptic mkt-s65 to s68 addressed), reviewed OK as a draft on the branch (rv-b4-ed-37, 2026-11-11); not in production; no loss-engine change (her OK covers the draft only) |

**Phase B exit:** as Phase A.

---

## Phase C — Forecasting: where the risk is going

| ID | Task | Depends | Data and availability | Acceptance criteria | Status |
|---|---|---|---|---|---|
| C1 | **Nowcast** the public share between Z.1 releases from higher-frequency data | 0.4, `FRED_API_KEY` | Monthly G.19 consumer credit (free); weekly H.8 bank loans (free); weekly Fed MBS `WSHOMCB` (have); Fannie/Freddie/Ginnie monthly summaries (to verify); release dates and vintages from ALFRED | Point-in-time panel: each input read at its value public at the nowcast instant; release-lag table per input | holdout run once 2026-11-05 (`a0d9151`, approval `432fed0`, after fix `cddd3ca`); write-up `research/joint_holdout/README.md` (Claude draft) accepted by Eleonora 18:55 UTC as a draft to rewrite (rv-holdout) |
| C2 | **Forecast model** with purged rolling-origin validation, leakage tests, prediction intervals, naive/AR benchmarks, mirroring `repo-market-model` | C1 | — | Pre-registered scoring protocol (`docs/decisions/scoring-protocol.md`); untouched holdout; leakage tests that fail on a deliberately leaked feature; interval coverage reported | holdout run once 2026-11-05 with C1/C1b (`a0d9151`); results feed C3; write-up accepted by Eleonora 18:55 UTC as a draft to rewrite (rv-holdout) |
| C3 | **Honest accuracy report**, including where the model fails | C2 | — | Accuracy vs benchmarks with confidence bands; failure cases and regimes listed; failed specifications published | built 2026-11-05 (`3c0247c`, Claude draft); reviewed (mkt-s44–s48, mkt-e1–e25, `f462172`); 2026-11-05 she chose c3-rule (b), c3-errors (b), c3-hcount (b): erratum and second gated holdout opening (`c783a5a`, `8d60d86`); recomputed under (b) (`6e86429`, quant-reviewer mkt-q40–q44): 1 to 3 C2 "beats" depending on the reading; she chose c3-b-level (iv) and c3-b-nointv (c) 18:54 UTC; final verdicts under (iv) and (c): 3 C2 "beats" (all h = 1 vs seasonal naive), C1 bridge_reg vs no_change k = 2 "undetermined" (`392a1bf`, `5c8bb4f`; quant-reviewer mkt-q45–q48); approved by Eleonora 20:59 UTC as a Claude draft to rewrite (rv-c3-final) |

**Phase C exit:** as Phase A, plus the quant-reviewer agent's sign-off logged.

---

## Phase D — AI research system

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| D1 | **Skill `claim-check`**: trace any number to its query, series and vintage; flag mismatches | 0.5 | Given a sentence with a number, returns the register row and a recompute, or flags it as untraced or mismatched; trigger examples logged | done (2026-11-04, `.claude/skills/claim-check`, 14 tests) |
| D2 | **Skill `chart-from-sql`**: query → publication-quality chart in the project style | 0.3 | Fixed style module (palette validated for contrast in light and dark); source and vintage line on every chart; alt text generated; examples logged | done (2026-11-04, `.claude/skills/chart-from-sql`, 60 tests; live SQL untested until the DB host is reachable) |
| D3 | **Skill `research-memo`**: findings → 2-page memo for a named market audience (e.g. MBS desk, rates strategist, policy shop) | D1 | Every number passes `claim-check`; three audience examples logged | done (accepted by Eleonora 2026-11-04; `.claude/skills/research-memo`) |
| D4 | **Subagents** in `.claude/agents/`: `analyst` (runs queries), `skeptic` (revisions, definition changes, double counting, vintages), `quant-reviewer` (leakage, overfitting, bad tests), `editor` (style and sourcing) | D1 | Each has a role, tool limits and a logged output format; every objection and its resolution recorded in `claims/review-log.md` | done (2026-11-04, six agents in `.claude/agents/`; E2 planted-error test still to run) |
| D5 | **MCP server `household-credit-mcp`**: Z.1, FRED, NY Fed, CBO | 0.2, 0.5 | Read-only; tools return values with series ID, vintage and caveats; refuses questions the data can't answer (e.g. auto loans by holder, which Z.1 doesn't split); tests, docs and install instructions; publishing to PyPI or an MCP registry only with approval | done (2026-11-04, `mcp/household-credit-mcp`, snapshot backend tested, 33 tests; Postgres backend untested live) |
| D6 | **"Ask Hot Potato"** (Anthropic API app on the site): tool use against the database; every answer cites its query; refuses unsupported forecasts | D5, `ANTHROPIC_API_KEY` | Answers carry the query and vintage; refusal cases tested; rate limit and cost cap; preview deployment first, production only with approval | todo: she chose Sonnet, a $20 build+E4 cap and tight preview limits (5/visitor/day, $2/day app stop) 04:55–04:57 UTC 2026-11-06; production not approved; infra plan `11d5d2c` (tracks/infra-d6-plan.md), offline build done (`8a5e17c`, `02c4ecb`, merged `2bb4d28`; 86 atlas tests pass); unplanned 30-question paid build test $0.509085 of the $20 cap (`328fd9a`, merged `a5c36fe`, 93 atlas tests), which she saw and kept in the ledger 14:39 UTC; no further paid call without a coordinator-checked plan; she chose Vercel KV/Upstash (free tier, she adds it) and read-only mart queries 14:38–14:39 UTC; preview variables later, so D6 stays local; KV store and read-only mart path built offline (`c73a19b`, merged `b244160`, 101 atlas tests); a live test read of the mart waits on her (card d6-martcheck) |
| D7 | **Cowork plugin "Fed Data Desk"**: packages the skills, subagents and MCP for a research team | D1–D5 | Installs cleanly; before/after outputs for three routine jobs | done (accepted by Eleonora 2026-11-04; `plugin/fed-data-desk`, icon B) |

**Phase D exit:** as Phase A.

---

## Phase E — Evaluation of the AI system

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| E1 | **Question-to-SQL benchmark**: about 100 questions with verified answers; Haiku vs Sonnet vs Opus on accuracy, cost and latency | D5, `ANTHROPIC_API_KEY` | Answers verified independently of any model; scoring rules fixed before the run; cost estimated and approved before running | in progress: pilot run (a4998b7): $0.51 of the $2.98 cap; pilot accuracy Opus 10/10, Sonnet 9/10, Haiku 10/10 (pilot, not an E1 result); waits on her review; her 14 prereg choices given 2026-11-05 (cap $31); pilot accepted; question set (100, 3faa99b) approved 2026-11-05; she chose unit (ii), T 70%, h3 (b), baseline Opus; R 70% (e1-R2) and replace (e1-set-h3) chosen 2026-11-05; not frozen; full run needs a separate spend OK; e1-cluster (b) and e1-support (i) chosen 2026-11-05; redraft of the 10 replaced questions approved 18:55 UTC (rv-e1-redraft); 10 retired e1_q1xx register rows deleted (`c7dc50a`); prereg frozen `e0ae2d6` (hash in `26aeb12`); spend OK for the main run and the Opus baseline, $31 total cap, 20:59 UTC (e1-spend (a)); main run stopped after one loop by the per-model overrun stop ($0.0036 spent, `a2b4a9e`); she chose e1-stoprule (a) and e1-cost (b) 21:15 UTC (prereg deviations); infra applied them (`4017e4e`, deviations D1–D3); rerun run-2026-11-05b passed the 10% checkpoint, then stopped after 79 of 720 loops by the Sonnet overrun stop ($2.59 spent, `77afb37`; partial, not an E1 result); baseline not started; she chose recal (e1-stop2) and resume from loop 80 (e1-resume) 21:40 UTC; infra added D4/D5 and the resume feature (`4247938`); main run complete 720/720, no stop, $17.90 (`36d2c67`); pre-registered analysis run (`43ab03e`; not yet written up or registered); Opus baseline stopped at its 10% checkpoint after 24/240 loops on a false projection (infra bug: carried spend scaled by 10; fixed with a test, `5814ec3`); E1 spend $18.13 of $31; Claude-draft results note (`6f53682`, 33 UNVERIFIED rows, baseline section open); she chose resume the baseline (e1-baseline (a), 04:50 UTC 2026-11-06); deviation D6 recorded (`bbd72a3`); baseline complete 240/240, no stop, $2.14 (`ed4a3de`); E1 spend $20.05 of $31 (coordinator recount matches); results note complete (Claude draft, 39 UNVERIFIED rows), approved by her as a Claude draft 14:39 UTC 2026-11-06 (rv-e1-results); stays UNVERIFIED and off the sites until her text replaces it |
| E2 | **Planted-error test**: deliberate errors; catch rate and misses for `skeptic` and `quant-reviewer` | D4 | Errors planted by a script with a hidden key; catch rate with confidence intervals; every miss analysed | in progress: prereg frozen at 5986353 with her round-5 design (CHOICE-11 (a), CHOICE-12 (i), Wilson primary), accepted; not yet run |
| E3 | **Regression suite**: rerun E1–E2 when prompts or models change; chart results over time | E1, E2 | One command; results appended, never overwritten; chart via `chart-from-sql` | in progress (`make evals` status and fingerprints built; waits on E1, E2) |
| E4 | **Red-team "Ask Hot Potato"**: try to get misleading answers or unsupported forecasts | D6 | Attack catalogue, results, guardrails added and remaining failures documented | in progress: infra plan `b1cc8b0` (tracks/infra-e4-plan.md; 60 prompts, then 60 + 20 held out; snapshot data; at most $7.00, so D6 at most $7.51 of the $20 cap), checked by the coordinator 2026-11-06; catalogue frozen and harness built offline (`6c7e8a6`, merged `24e56f7`, 112 atlas tests); P1 run `999f44e` (merged `1530eb5`): $0.642734, 38 of 60 answers auto-flagged, no leak flags, hand labels and guardrails `67108c6` (4 fail, 1 unclear, 34 FP, 4 pass; Claude draft, UNVERIFIED; on the review queue); grounding v2 re-score 20/60 flagged; held-out peek disclosed (A1/A2 pre-check); D6 spent $1.151818 of $20; labels approved as a Claude draft and guardrails approved as built (Eleonora, 19:54 UTC); P2 approved (e4-p2-heldout a, ≤ $4.00, the 4 seen A1/A2 held-out prompts reported apart), running in infra |

**Phase E exit:** as Phase A.

---

## Phase F — Reproducibility, living site, publication

| ID | Task | Depends | Acceptance criteria | Status |
|---|---|---|---|---|
| F1 | **Source register in the app**: every published number links to query, series, vintage and validation status | 0.5 | Clicking or hovering a number on the site shows its register row | done (2026-11-04, popovers + `/sources` on both sites; exceptions in `claims/site/unlinked.json`) |
| F2 | **`make all`** (ingest → validation → models → build) and a GitHub Action running validation and evals on every push; README badges | 0.3, E3 | Fresh clone + `make all` reproduces the published numbers; CI green; evals that cost money run on schedule or by hand, not on every push, unless approved | done (2026-11-04, `make all`, `.github/workflows/ci.yml`, ALFRED-pinned FRED pulls; evals join with E3) |
| F3 | **Scheduled updates** after each Z.1 release; Claude drafts release notes, Eleonora approves before publishing | 0.8, F2 | The workflow opens a PR with the "what moved" note; nothing publishes without her merge | done (accepted by Eleonora 2026-11-04; `tools/z1_release.py`) |
| F4 | **Open data**: downloads, a public read-only API, accessible chart descriptions | 0.5, D2 | CSV/JSON downloads with a data dictionary and licence notes; API documented; every chart has a text description | done (2026-11-04, downloads, dictionary, licence notes, chart-text check; API documented in `opendata/api-plan.md`, exposure per F4-2) |
| F5 | **Building-with-Claude log**: models per task, token cost, errors and how they were caught | 0.6 | Kept up to date every session (started in 0.6) | todo (ongoing) |
| F6 | **Outputs**: working-paper draft (SSRN format); short op-ed | all | Every number passes `claim-check`; `skeptic` and `editor` reviews logged | todo |
| F7 | **Dashboard tab** (docket 54): one /dashboard tab that replaces /findings, for a market reader, with Core tiles and panels on top and the full findings below | F1, F4 | Tiles for total debt, public share, home coverage and serious-delinquency transitions with change on the quarter and the year; holder-mix and loan-type panels with date-range and loan-type filters; every number has a register row; analysis/findings.md shown whole, with a contents list; /findings redirects to /dashboard | built on the branch (2026-11-10); ok-prod from Eleonora 2026-11-11 (rv-dashboard-34); released to production 2026-11-11 (6ec789d, redeploy dpl_HmveLFPi7yeVaENkfYp8TXq1UFJY); live check by Claude passed (tiles, filters, /findings redirect, no console errors, no sideways scroll); the gradient-free build (1397d94) is in review queue round 35 |

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
