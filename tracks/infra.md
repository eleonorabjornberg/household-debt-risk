# Track: Infrastructure

Branch: `claude/track-infra` · Tasks, in order: F1, F2, F4 · Rules: PLAN.md "Parallel tracks".

## Handoff (2026-11-04 ~17:30 UTC, from the session that ended at this commit's parent)
**State.** Branch `claude/track-infra`. Last commits: `6c03d52` (Eleonora's CHOICE-1/2/4/10 values; `plant.py --stratified`), `3852ee5` (CHOICE-11/12 drafts), both merged by the coordinator into `claude/sweet-gates-avwrcs`. `make test` passes (163 passed, 3 skipped; MCP 37 passed, 1 skipped). `make evals` reports E2 NEVER RUN and E1 NOT BUILT. Nothing has been run against the API, and the E2 prereg is **not frozen**.

**Open items (all wait for Eleonora's round-5 answers, relayed by the coordinator; do nothing on them before then):**
- E2: CHOICE-11 (design (a)/(b)/(c)), CHOICE-12 (decision rule if (a) or (c)), and CHOICE-8 changed to Wilson primary (too few clusters for the bootstrap). Also fix the exact method-document list at the freeze; the rehearsal used `research/c1_nowcast/README.md` and `research/c2_forecast/SPECS.md`.
- Spend pilot: E1 only, 30 loops, cap $2.98. Do not build the E1 questions or spend anything until she says so.
- `ANTHROPIC_API_KEY`: set as a network secret. In the old session the free check `curl -sS -o /dev/null -w "%{http_code}\n" https://api.anthropic.com/v1/models -H "anthropic-version: 2023-06-01"` returned 401. Run it first in the new session: 200 means the key arrives.

**`plant.py` changes still needed, per CHOICE-11 option** (make them, with tests, before the freeze commit):
- All options: allocate planted documents by a **count per agent** (e.g. `--planted-data N --planted-method M`, or `--planted` per agent). `run()` currently cycles `sources[i % len(sources)]`, so the data/method split follows the source list. Controls likewise: 1 data + 1 method.
- (a) 4 data docs × 2 and 3 method docs × 2: the existing `stratify()` works once allocation is fixed (8/8 and 6/6 divide evenly).
- (b) 6 × 2 per agent: skeptic 12 over 8 categories needs an **"as equal as possible"** mode: quotas of ⌊n/c⌋ plus one extra for n mod c categories chosen by the seeded RNG, recorded in `key.json`. Today `stratify()` refuses uneven splits (a test asserts this; keep that test for the strict mode).
- (c) 6 × 1 per agent: also "as equal as possible" for skeptic (6 of 8 categories); `--errors-per-doc 1`.
- Then write the chosen values into the prereg, set `Status: **frozen**` (the line `plant.py` `is_frozen()` matches), commit as `prereg: E2 (frozen)`, and put that hash in the prereg ("Frozen at") and in this file. Update the test `test_refuses_unless_frozen` (it asserts the prereg is a draft). `make evals` already fingerprints the prereg, `plant.py` and the catalogue.

**Pilot procedure (only after her go-ahead):**
1. Re-check live pricing: fetch the Anthropic pricing page (or the `claude-api` skill, then the page) and compare with the table in "Cost estimates" above (cached 2026-10-06). If any price differs, recompute the $1.99 estimate and the $2.98 cap and send them to the coordinator before spending.
2. Build 10 E1 questions with answers verified independently of any model (from `analysis/results.json`, committed tables or the register), and the scoring script, with no API calls.
3. Run 10 questions × Opus/Sonnet/Haiku 5.5 × 1 repetition = 30 loops. Log the `usage` of every call. Keep a running dollar total; stop at $2.98, or as soon as any model's measured cost per loop is more than 1.5× its assumption (Opus $0.129, Sonnet $0.067, Haiku $0.0033).
4. Report the measured cost per loop and the re-estimated build-out to the coordinator. The pilot does not approve the build-out.

## Status
| Task | Status | Notes |
|---|---|---|
| F1 | ready for review | Every register row on both sites is a hover/focus popover + link to `/sources#<id>`; 46/49 web and 27/29 atlas rows link in the prerendered HTML, the rest are listed with reasons in `claims/site/unlinked.json` (3 are register fixes below) |
| F2 | ready for review | `make all` and `.github/workflows/ci.yml`; evals join once E3 exists. F2-1 done: FRED pinned via ALFRED, so pinned reruns reproduce every committed result byte for byte (`8bf5d88`) |
| F4 | ready for review | Downloads under `/downloads/v1/` (latest plus an archive of every Z.1 release), dictionary, licence notes, chart-text check, API plan. F4-1 to F4-3 done (`abc9894`) |
| F3 | ready for review, 2 questions (F3-1, F3-2) | `.github/workflows/z1-release.yml` + `tools/z1_release.py` (3 tests). Rehearsed locally on the 2026-06-11 → 2026-09-11 release (what moved, stale claims, PR body). Not run on GitHub: scheduled runs only fire from the default branch, so nothing runs before merge |
| D3 | ready for review | `.claude/skills/research-memo` (SKILL, audiences, `facts.py`, `memo_check.py` gate, 5 tests) and three logged example memos (MBS desk, rates strategist, bank treasury), all PASS; review fixes logged in `examples/README.md` |
| E2 | needs-approval (CHOICE-11/12) | All 10 choices have Eleonora's values (2026-11-04) in `docs/decisions/e2-prereg.md`; `plant.py --stratified` built (CHOICE-10). **Freeze held**: the per-agent sample size makes H2 testable only at 12/12 (E2-3). Not frozen, not run |
| E3 | partly built; blocked on E1 (cost approved, key not added) and the E2 freeze | `evals/regression.py` + `make evals`: fingerprints the reviewer prompts, models, catalogue, code and prereg; reports NEVER RUN / UP TO DATE / RERUN NEEDED per eval (E1 reported NOT BUILT); charts E2 recall over time through chart-from-sql (smoke-tested on synthetic data in the scratchpad only); results stay append-only. 3 tests |
| D7 | ready for review | `plugin/fed-data-desk`: 6 skills, 4 commands, 6 agents and the household-credit MCP server; local marketplace at `plugin/`; `plugin/sync.py` (+ `--check` in `make ci-static`). Validates, and installs cleanly in a throwaway config. The MCP server answers. Before/after for 3 routine jobs in `examples/`. Two icon candidates in `assets/icon-candidates/` for Eleonora's pick (D7-1); none active, nothing submitted |

Commits: `684b088` F1 · `d33d4b6` F2 · `f609788` F4 (plus this status file).

### How each acceptance criterion was checked
- **F1, "clicking or hovering a number shows its register row".** `claims/site/check_html.mjs` reads every prerendered page after `next build` and fails unless every register row with a location on that site appears as a `data-claim` link (or is a listed exception). Screenshots taken with Playwright at 1200 px and 390 px: the desktop popover, the atlas step and legend popovers, the phone bottom sheet and `/sources#gfc_jump_pp`. Unit tests (`lib/claims.test.ts`, 8 per site) cover the matcher: digit boundaries (`7%` is never matched inside `17%`), longest spelling first, anchors, and stat literals. The popover works without JavaScript (CSS on hover and focus-within) and is tied to the link with `aria-describedby`.
- **F2, "fresh clone + `make all` reproduces the published numbers; CI green".** I ran `make all` in this sandbox: ingest (live Z.1, FRED and NY Fed), validation (41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN), models (notebook + A1 decomposition), and both sites' tests and builds. It took about 2 minutes once the Z.1 zip was cached. `tools/repro_check.py` then compared every results file with the committed one:
  - Z.1-based outputs reproduce exactly: `validation/results.json`, `research/a1_gfc_decomposition/results.json` and every `web/public/data` table.
  - Three values in `analysis/results.json` moved because FRED published a new weekly WSHOMCB observation (2026-10-28). Two of them are published in `analysis/findings.md:15`: `fed_mbs_weekly_usd` $1.90T → $1.88T, and `fed_mbs_runoff_usd` $845B → $857B. I did not commit the regenerated files.
  - The pipeline's two database tests fail here because the Supabase pooler host does not resolve (known issue). `make test` now drops the database URLs, and `make test-db` runs those tests separately.
  - CI: green on both pushes, run 1 (F2) and run 2 (F4): https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/ci.yml
- **F4, "CSV/JSON downloads with a data dictionary and licence notes; API documented; every chart has a text description".** `/data` page and `/downloads/*` (6 CSV + 6 JSON + `dictionary.json` + `LICENSE-DATA.md`), checked on the built site (CSV served, no horizontal scroll at 390 px). The API is documented as a plan (`opendata/api-plan.md`), not built, because exposure needs approval. `tools/check_chart_text.mjs` passes: 25 web charts each have an SVG with `role="img"`, `<title>` and `<desc>`; 4 of 5 figures also have a data table; the atlas canvas has an `aria-label`.

### Vercel previews (branch builds; production untouched)
| Commit | web (`household-debt-risk-web`) | atlas (`household-debt-risk`) |
|---|---|---|
| F1 `684b088` | READY: household-debt-risk-k4z0ye2r5-eleonorabjornberg.vercel.app | READY: household-debt-risk-fcgvk3jxq-eleonorabjornberg.vercel.app |
| F2 `d33d4b6` | READY: household-debt-risk-exk1rovkw-eleonorabjornberg.vercel.app | READY: household-debt-risk-m8zvwncc2-eleonorabjornberg.vercel.app |
| F4 `f609788` | READY: household-debt-risk-m8ujyyxew-eleonorabjornberg.vercel.app | no deployment (atlas/ unchanged in that commit; likely skipped by the project's ignored-build step) — F2 preview is current for atlas |

## Log notes for the coordinator
- 2026-11-04 ~17:25 UTC, same session. E2-3 answered ("way fewer errors", taken as direction). Drafted CHOICE-11 (three smaller designs with Wilson arithmetic) and CHOICE-12 (decision rule, since 6–8 errors per agent cannot support 70% even when every error is caught). Error caught by Claude before commit: I first wrote that `plant.py --stratified` runs designs (a)/(c) as built, but it allocates documents by cycling over sources, so every option needs a small change. Spend pilot approved (10 items, 1.5× cap); nothing run, because `ANTHROPIC_API_KEY` is unset and E1/D6 are not built.
- 2026-11-04 ~18:00 UTC (new infra session, took over at `df6957c`). Task: freeze the E2 prereg with Eleonora's E2-2 values (70%, 25%, seed 20261104, stratified). Values written into the prereg; `plant.py --stratified` built (seeded backtracking: every category planted equally, no category twice in a document, all fit together) with 2 tests; a rehearsal (seed 20261104, scratchpad, nothing reviewed, no API) gives 3 per data category and 2 per method category. **Not frozen.** Error caught by Claude: the CHOICE-1 recommendation (written by the earlier infra session) quoted 31/36 as the bar, but each agent gets only 24 or 12 errors; with 12, H2 can be supported only by a perfect score (E2-3). A first stratifier (random retries) found no assignment; caught by the rehearsal, replaced by a backtracking search. Main model, no subagents, no API calls.
- 2026-11-04 ~17:00 UTC, after Eleonora's decision cards (`543d96a`, merged). F3-1 and F3-2 applied (`7126688`). Cost estimates written. The E2 prereg records her six decided choices; it is not frozen, because CHOICE-1, -2 and -4 have no recommended value and CHOICE-10 is outside 1–9 (E2-2). D7 icon candidates (`e766d1e`). E3 runner (`make evals`). Errors caught by Claude: I first wrote CHOICE-4 (seed) as decided, but its draft had no recommendation, so I reverted it to open before committing; `regression.py chart` called chart-from-sql without matplotlib, caught by the smoke test, and now uses `--with matplotlib` as the skill says. Main model, no subagents.
- 2026-11-04 ~05:05 UTC, D5 fallback fix (coordinator's request). Merged `0c05fd1` first. `get_backend()` now probes the database once and falls back to the snapshots with a `backend_note` when it cannot connect; `HOUSEHOLD_CREDIT_REQUIRE_DB=1` keeps the hard failure. New `tests/test_fallback.py` (4 tests; the main one uses a real unresolvable `.invalid` host). `tests/test_guard.py::test_get_backend_default_is_snapshot` asserted the old lazy, non-connecting behaviour, so I changed it to inject a reachable fake connection. MCP suite: 37 passed, 1 skipped. Live check with the sandbox's real `DATABASE_URL_READONLY`: `public_share` answers from the snapshots in 0.5 s, with the note. Main model, no subagents.
- 2026-11-04 ~05:40 UTC, E2 tooling and D7. Main model, no subagents (0 subagent tokens). E2: catalogue (14 error types), `plant.py` (refuses until the pre-registration is frozen; hidden key with a SHA-256 commitment), `score.py` (location match, then a human same-fix call, then Wilson and cluster-bootstrap intervals; appends only), 6 tests; a rehearsal on six write-ups planted 36 errors with uneven categories (now CHOICE-10). D7: `claude plugin validate` passes (icon warning only), and the install was tested with `CLAUDE_CONFIG_DIR` pointing at the scratchpad, so the user's config was not touched. Errors caught by Claude: in the before/after work, the MCP server errors instead of falling back to snapshots when `DATABASE_URL_READONLY` is set but the host is unreachable (finding below); an unverified sentence I had written in an example ("took the whole 0.8 session") was removed before commit.
- 2026-11-04 ~05:10 UTC, D3. Three subagents (one per audience, sonnet tier) drafted the memos in parallel (95.8k + 86.9k + 95.9k subagent tokens). The main model built the skill and gate and reviewed each memo. Errors: the gate (memo_check / claim-check) caught UNTRACED spellings, 4 NOT RECOMPUTABLE rows and a MISMATCH on the ESTIMATE row `uncoll_break_2005q4`. The **main session** caught a definition error in 2 of 3 memos (the Fed counted as a public holder; state and local left out) and a wrong mechanism (Fed runoff said to move the public share), both now in SKILL.md hard rules. E2: pre-registration drafted, choices open.
- 2026-11-04 ~04:50 UTC, F3. Main model, no subagents (0 subagent tokens). The workflow reuses the z1-release-update skill's `what_moved.py` and `stale_claims.py`. Detection reads the Z1.csv member date, so it works in a fresh CI checkout (the skill's `detect_release.py` needs `data/manifest.jsonl`, which CI lacks). The comparison vintage is the Fed's archived per-table zip of the previous release (`/releases/z1/<YYYYMMDD>/z1_csv_files.zip`; 20260911 already answers 200). Rehearsal: what_moved 2026-06-10 → 2026-09-11 written, stale_claims ran (2 count rows "cannot compare", as designed), PR body assembled. Not exercised: `gh pr create` and the full workflow on GitHub (they fire only from main).
- 2026-11-04 ~04:35 UTC: merged `51a0b6a` (coordinator branch) into `claude/track-infra` with no conflicts (`a14db9f`). The pre-commit checks pass on the merged tree, as do the offline suites (pipeline 48 passed / 2 skipped, claims+research+validation+skills 65 passed / 2 skipped, MCP 33 passed / 1 skipped). `make ci-static` caught that the sites' `lib/claims.json` was stale after the register fold; I regenerated it (`17e1e1a`). Web now links 47/49 rows (the `5.0 pts` fix landed) and atlas 27/29. Both sites test and build, and the F1 and F4 checks pass. I did not start the rest of the overnight list (see Q-scope).
- 2026-11-04, second pass after the coordinator relayed Eleonora's decisions (verified against PLAN.md on `claude/sweet-gates-avwrcs`, commit `a590475`). Main model, no subagents (0 subagent tokens). Errors caught by Claude: (1) ALFRED's number formatting changed `analysis/tables/fed_mbs.csv` without changing any value; `repro_check` passed but `git status` showed the diff, so I normalised the formatting. (2) Shell heredocs containing a command-substitution string tripped the command safety check, so nothing ran; I redid those edits with the Edit tool.
- 2026-11-04, infra track session. Tasks F1, F2, F4. The main model did all the design, code and review. I used no subagents: each step was a few targeted reads and edits, so delegating would have cost more than it saved. Subagent tokens: 0. Cost not measured.
- Environment: `FRED_API_KEY`, `DATABASE_URL_READONLY` and `DATABASE_URL` set; `ANTHROPIC_API_KEY` unset in this session. The Supabase and Vercel MCP servers failed to connect at start (proxy tunnel). A second Vercel connector worked for reading deployments. No production deployment or database was touched; `make` drops `DATABASE_URL` unless `LOAD=1`.
- Errors, and who caught them (all caught by Claude, this session):
  1. Adding an import shifted three register locations (`web/app/page.tsx:66`, `atlas/components/Experience.tsx:211`). `check_register.py`'s drift check caught it. Fix: I kept the line numbers stable instead of editing the register.
  2. Atlas's `.legend span` rule overrode the hidden popover, so the legend popover showed all the time, cut off at the bottom. Caught in a Playwright screenshot; fixed with doubled-class selectors and an upward-opening variant.
  3. The first `make all` stopped on the database tests (pooler unreachable). Caught by the run; offline and database tests are now separate targets.
  4. The reproduction check showed published FRED-based values drifting (question F2-1).
  5. The root `.gitignore` rule `data/` hid the new `web/app/data` route. Caught by `git add`; I added a narrow `!web/app/data/` exception.
- Register: F1–F4 publish no new numbers. The `/sources` summary counts register rows; `/data` shows source vintages from `meta.json`. So `claims/tracks/infra.csv` is not needed.

## Questions for Eleonora
- **E2-3 (answered 2026-11-04: none of (a)–(c), "Let's do way fewer errors instead"; smaller designs drafted as CHOICE-11/12 in the prereg).** Freeze held: per-agent sample size (found while freezing, 2026-11-04).** Your values are in the prereg. But the CHOICE-1 recommendation assumed 36 errors per agent ("31/36"). H1/H2 are per agent, and 12 planted documents split into 8 data and 4 method documents: 24 skeptic and 12 quant-reviewer errors. At 70%, H1 needs 22/24 (92%) and H2 needs 12/12 (11/12 has Wilson lower bound 0.646), before the wider cluster bootstrap. Options: (a) freeze as decided; (b) 12 planted documents per agent (36 errors each, about twice the runs); (c) keep the size and lower the threshold. Recommendation: (b), because it is the design the 70% was chosen against. The method document list also needs exact files at the freeze (the rehearsal used `research/c1_nowcast/README.md` and `research/c2_forecast/SPECS.md`).
- **E2-2 (answered 2026-11-04: 70%, 25%, seed 20261104, stratified).** Four E2 choices still had no value. "Accept all the recommendations for CHOICE-1 to CHOICE-9" covers six of them. My draft gave no recommended value for CHOICE-1 (the recall threshold for H1/H2), CHOICE-2 (the false-alarm ceiling for H4) or CHOICE-4 (the seed), and CHOICE-10 (category balance) is outside 1–9. Freezing would mean Claude picking the thresholds the test is judged against, so it is **not frozen**. Proposed values, for you to accept or change:
  - **CHOICE-1, recall threshold** (the same for skeptic and quant-reviewer): (a) 50%, (b) **70%**, (c) 80%. Support needs the lower bound of the 95% interval at or above it. With 36 errors the interval is about ±15 pp, so (b) is supported only by an observed recall of 31/36 (86%) or more (Wilson lower bound 0.713); (c) would need 34/36 (94%). Recommendation: (b).
  - **CHOICE-2, false-alarm ceiling** (share of blocker/major objections on controls that are not real problems): (a) 10%, (b) **25%**, (c) 40%. There will be few objections on 4 controls, so the interval is wide; (b) keeps H4 informative. Recommendation: (b).
  - **CHOICE-4, seed:** (a) **the fixed integer 20261104**, written into the file before freezing; (b) the first 8 hex digits of the freeze commit. (b) is circular: the commit cannot contain its own hash. Recommendation: (a).
  - **CHOICE-10, category balance:** (a) random, (b) **stratified** (each category planted a fixed number of times), (c) drop rare categories. Recommendation: (b), as in the draft.

  The other six choices are applied in the file (decided by Eleonora 2026-11-04). It freezes as soon as these three have values.

### Decided by Eleonora 2026-11-04 (decision cards, about 16:35–16:41 UTC; PLAN.md "Decisions taken", coordinator commit `543d96a`)
- **F3-1: (a).** Drop the `refresh.yml` schedule and default `load` to false; load by hand after merging. Done in `7126688` (workflow file only; nothing run).
- **F3-2: (a).** A Claude session runs the z1-release-update skill to draft release notes. Documented in the `z1-release.yml` header and the PR body (`7126688`).
- **E2-1:** accept all the recommendations for CHOICE-1 to CHOICE-9. Applied, except where no recommendation existed (E2-2 above).
- **D7-1:** list the plugin more widely; it needs a 512–2048 px icon. Icon candidates are drafted for her pick; nothing is submitted to any listing.
- **D6, E1, E4:** approved, with a cost estimate first (below). No key added and nothing spent.
- **Copy review:** she approved the 2008 copy revision, the nav links and the /sources and /data intros. `public_share_2001q1` / `_2005q1` and their F1 exceptions stay.
- **Still open:** the `FRED_API_KEY` repository secret (later), and F2-2 (the coordinator is answering her directly).
- Settings she must change for F3: Settings → Actions → General → "Allow GitHub Actions to create and approve pull requests". Also note that a PR opened with the workflow's token does not trigger `ci.yml`; re-run CI from the PR.

### Cost estimates for D6, E1, E4 (for Eleonora's approval; all are estimates)
**Prices:** list prices per million tokens, from the `claude-api` skill's model table (cached 2026-10-06) and its prompt-caching notes. **Re-check the live pricing page before any spend.**

| Model | Input | Output | Cache read | Cache write (5 min) |
|---|---|---|---|---|
| Claude Opus 5.5 | $4.00 | $20.00 | $0.20 | $5.00 |
| Claude Sonnet 5.5 | $2.00 | $10.00 | $0.20 | $2.50 |
| Claude Haiku 5.5 | $0.10 | $0.50 | $0.01 | $0.125 |

- Batch API: 50% off every token, cache included.
- Haiku 5.5 rates are for prompts up to 100K tokens; every call here is far below that.

**Assumptions, the same for all three tasks (to be replaced by measured `usage` after a pilot):**
- Each call is a tool-use loop against the household-credit MCP tools.
- 60% of input tokens are cache reads, from a stable cached prefix of system prompt and tool definitions; cache writes are negligible next to reads.
- Output tokens include thinking.
- No LLM grader in E1: answers are scored by a script against independently verified values.

| Task | Calls | Tokens per call (input / output) | Model(s) | Estimate |
|---|---|---|---|---|
| **E1** question-to-SQL benchmark | 100 questions × 3 models × 3 repetitions = 900 loops | 4 turns, about 37.8k input (6k prefix + 2.3k per turn, summed over turns) / 3.2k output | Opus 5.5, Sonnet 5.5, Haiku 5.5 | Opus $38.70 + Sonnet $20.03 + Haiku $1.00 = **$59.74** |
| **D6** "Ask Hot Potato" | per reader question | 3 turns, about 21k input / 2.1k output | one model (her choice) | Per question: Opus $0.078, Sonnet $0.040, Haiku $0.002 |
| | development and tests, about 400 questions | as above | | Opus $31.25 / Sonnet $16.13 / Haiku $0.81 |
| | running: 1,000 questions/month | as above | | Opus $78 / Sonnet $40 / Haiku $2 per month |
| | running: 10,000 questions/month | as above | | Opus $781 / Sonnet $403 / Haiku $20 per month |
| **E4** red-team of D6 | 60 attacks × 3 repetitions × 2 rounds (before and after guardrails) = 360 transcripts | 1.5× a D6 question | the D6 model, plus a Sonnet 5.5 judge (4k in / 0.5k out per transcript) | Opus target $46.86 / Sonnet target $26.45 / Haiku target $5.77 (judge $4.68 included) |

**Totals.** Build-out spend (E1 + D6 development + E4) is about $138 if D6 runs on Opus, $96 on Sonnet, or $67 on Haiku; E1 is the same in each case. The running cost of D6 then scales with readers, as above.

**Recommended safeguards:**
- A workspace spend limit at 1.5× the estimate.
- A pilot of 10 items per task first; stop and re-estimate if measured cost per item is more than 1.5× the assumption.
- D6 in production only behind a per-IP rate limit and a monthly cap (PLAN D6 acceptance).

E1 could use the Batch API for a further 50% off only if the loop is restructured to one batched turn at a time; I did not assume it.

Answered 2026-11-04: Eleonora accepted the recommendations (PLAN.md "Decisions taken", coordinator commit `a590475`). What was done:
- **F2-1 (a), pin FRED via ALFRED** (`8bf5d88`). `HHDEBT_FRED_ASOF` (pipeline) and `FRED_ASOF` (notebook) read FRED as it stood on one day (ALFRED `realtime_start` = `realtime_end`). The day defaults to the committed `web/public/data/meta.json` `vintages.fred` (2026-10-27), and `make` passes it; a refresh moves it on purpose (`make all FRED_ASOF=2026-12-20`, say). Verified: a pinned ingest plus the notebook reproduce every committed results file and table byte for byte, so `findings.md:15` ($1.90T, $845B) no longer drifts. ALFRED writes some whole numbers as `1721271.0` and missing weeks as `.`; both are normalised so the tables match the fredgraph format exactly.
- **F2-2.** Eleonora will add the optional `DATABASE_URL_READONLY` Actions secret herself. Per the coordinator, raw-TCP Postgres does not pass this environment's proxy. The pipeline's DB tests now skip with the reason when the host is unreachable; `HHDEBT_REQUIRE_DB=1` (`make test-db`) makes that a failure.
- **F4-1 (a)** (`abc9894`). `nyfed_by_type` is now downloadable under the NY Fed Terms of Use, with their attribution line and source identifier ("Source: New York Fed Consumer Credit Panel/Equifax") in the JSON, `LICENSE-DATA.md`, `NOTICE-nyfed.txt` and on `/data`. I did the manual check first: the HHDC workbook has no use restriction beyond the general terms (`opendata/sources.md`).
- **F4-2 (A now, B later, never C).** A is built as the stable `/downloads/v1/` contract (`index.json`, `latest/`, `vintages/`, `opendata/CHANGELOG.md`). B is not built; exposing it later needs her approval.
- **F4-3 (archive).** `opendata/archive.mjs` stores each Z.1 release's snapshots gzipped in `opendata/archive/z1-<date>/` (about 0.2 MB each) and never overwrites one. `make ingest` runs it, and CI checks that the committed vintage is archived. `z1-2026-09-11` is archived and served at `/downloads/v1/vintages/z1-2026-09-11/`.
- **For F3 (coordinator):** the refresh workflow should run `make ingest FRED_ASOF=<run date>` and commit the new `opendata/archive/z1-<date>/` with the snapshots.

## Proposed changes to shared files
- **D5 finding, FIXED on this branch at the coordinator's request (see the log).** Original note: with `DATABASE_URL_READONLY` set and the database unreachable (as in this cloud sandbox), every tool returns `Error executing tool ...: failed to resolve host`, instead of falling back to the snapshot backend with a note. Proposal: on a connection error at start-up, fall back to the snapshot backend and put `backend: snapshot (database unreachable)` in every answer.
- **README index line (for the coordinator):** `plugin/fed-data-desk/`, the Fed Data Desk Claude Code plugin; install with `claude plugin marketplace add ./plugin && claude plugin install fed-data-desk@household-debt-risk`.
- **D3 findings, `claims/register.csv`:**
  - (1) `uncoll_break_2005q4` (ESTIMATE) holds two numbers, 7.6% and 11.5%, under one value (0.0763). claim-check therefore returns MISMATCH on the 11.5% at `web/content/story.ts:312`. Fix: split it, adding a row `uncoll_share_2006q1` with value 0.1146 (`analysis/results.json collateral.uncoll_share_2006Q1`), display `11.5%`, ESTIMATE, location web/content/story.ts:312; remove `11.5%` from the old row's display. The site copy itself is right.
  - (2) There is no row for banks' share of household debt (the bank audience's lead number); a row from `mart.debt_by_risk_holder` (`banks_credit_unions`, 2026Q2) would let memos use it.
  - (3) These rows are NOT RECOMPUTABLE in claim-check, which blocks them from memos: `nyfed_sample_share`, `private_label_2026q2_real`, `a1_ginnie_holdings_2011q4`, `nyfed_mortgage_change`. A parseable `computation` would fix it.
- **F3-1 (a) patch, if approved** (`.github/workflows/refresh.yml`; not a shared file, but it decides what reaches production, so it waits for her): delete the `schedule:` block (lines 7–8), change `default: true` to `default: false` for the `load` input, and replace the header comment with "Manual: load the database after merging a z1-release PR (Actions → refresh-data → Run workflow, load = true). Scheduled release detection is z1-release.yml."
0. **New, after merging `cc74d76`, `claims/register.csv`:** `web/content/story.ts:148` renders the A1 Shapley numbers bare ("accounts for 6.9 of the 13.1 pts and public growth for 6.2 … only 1.2 of it"), because the copy strips " pts". Either add the bare spellings `6.9`, `6.2`, `1.2` to `a1_private_change_pp`, `a1_public_growth_pp`, `a1_ff_pp` (the F1 matcher only links them on that cited line, with digit boundaries), or keep the unit in the copy ("6.9 points"). Recommendation: keep the unit; a bare "6.9" reads as unitless. Then remove the three rows from `claims/site/unlinked.json`, where they are listed as known exceptions for now.
Patches for the coordinator; I have not applied them.

1. **`claims/register.csv`** (found by the F1 link check):
   - `pre_gfc_decline_1999_2007_pp`: add the spelling `5.0 pts` to `display`. `web/content/story.ts:118` renders `5.0 pts` (it strips the sign), and neither listed spelling matches. Then remove the row from `claims/site/unlinked.json`.
   - `public_share_2001q1`, `public_share_2005q1`: their only location is a `facts` definition (`dotcomFrom`, `dotcomTo`, web/content/story.ts:37-38) that is never rendered. Either delete the two unused facts (copy change) or keep the rows and their exceptions.
   - `atlas_dot_unit`: change the location `atlas/app/page.tsx:27` → `atlas/app/page.tsx:28`. Line 27 still passes the drift check only because it holds a template. Also add `atlas/app/page.tsx:26` to `public_share_1952q1` and `atlas/app/page.tsx:27` to `public_share_2026q2`; the atlas hero renders both, now with explicit links.
2. **`README.md`**: badges and the reproduce command:
   ```markdown
   [![ci](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/ci.yml)
   [![refresh-data](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/refresh.yml/badge.svg)](https://github.com/eleonorabjornberg/household-debt-risk/actions/workflows/refresh.yml)
   [![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](opendata/README.md) [![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
   ```
   Under "How to reproduce": `make all` (and `make help` for the steps). Index lines: `opendata/` (downloads, dictionary, licences, API plan), `tools/` (reproduction and chart-text checks), `claims/site/` (F1 source register in the sites). The MIT badge needs a `LICENSE` file at the root; there is none yet. Proposal: add one with the MIT text, copyright Eleonora Björnberg.
3. **`CLAUDE.md` Commands**: add `make all`, `make ci`, `make help`, and `cd web && npm test` (web now has vitest).
4. **Site chrome I added outside `content/` (please review as copy):** web nav links "Data" and "Sources"; the `/sources` and `/data` page intros (`web/app/sources/page.tsx`, `web/app/data/page.tsx`, `atlas/app/sources/page.tsx`); one sentence in the atlas coda ("Every number on this page links to its row in the claims register", `atlas/components/Coda.tsx`). With five links the web masthead nav wraps on a 390 px phone. Proposal: shorten "How it was built" to "Build", or move Data and Sources to the footer.
5. **PLAN.md**: once reviewed, set F1, F2 (validation and tests part) and F4 to done. F4's "API documented" is met by the plan, pending F4-2.
