# Track: Infrastructure

Branch: `claude/track-infra` · Tasks, in order: F1, F2, F4 · Rules: PLAN.md "Parallel tracks".

## Status
| Task | Status | Notes |
|---|---|---|
| F1 | ready for review | Every register row on both sites is a hover/focus popover + link to `/sources#<id>`; 46/49 web and 27/29 atlas rows link in the prerendered HTML, the rest are listed with reasons in `claims/site/unlinked.json` (3 are register fixes below) |
| F2 | ready for review | `make all` and `.github/workflows/ci.yml`; evals join once E3 exists. F2-1 done: FRED pinned via ALFRED, so pinned reruns reproduce every committed result byte for byte (`8bf5d88`) |
| F4 | ready for review | Downloads under `/downloads/v1/` (latest plus an archive of every Z.1 release), dictionary, licence notes, chart-text check, API plan. F4-1 to F4-3 done (`abc9894`) |

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
- **Q-scope (2026-11-04, overnight).** The coordinator asked this track to take on, overnight and in order: F3 (scheduled Z.1 refresh), D3 (research-memo skill), E2 (planted-error test, pre-registered first), E3, then D7 (plugin). PLAN.md does not assign these to infra. D3 is listed as the coordinator's. PLAN.md also says "no track starts a new phase's work without her approval" and records only "merge the three track branches overnight". So I have **not started them**; I only did the merge (step 1). Please choose one:
  - (a) Approve the list as proposed: F3 → D3 → E2 → E3 → D7 on this track. E2 and E3 are Phase E, and D7 starts new Phase D work.
  - (b) Approve F3 only on this track, since it is Phase F like F1, F2 and F4 and its dependencies (0.8, F2) are in place; the rest stays with the coordinator or waits for the phase decision.
  - (c) Keep this track at F1, F2 and F4; the coordinator schedules the rest.

  **Recommendation: (b).** F3 builds on the archive and FRED pin I just made. The workflow can live on the branch with no schedule firing against production until you merge it. E2, E3 and D7 belong with your Phase D/E decision. D6, E1 and E4 also need cost approval or an API key (`ANTHROPIC_API_KEY` is unset in this session).

Answered 2026-11-04: Eleonora accepted the recommendations (PLAN.md "Decisions taken", coordinator commit `a590475`). What was done:
- **F2-1 (a), pin FRED via ALFRED** (`8bf5d88`). `HHDEBT_FRED_ASOF` (pipeline) and `FRED_ASOF` (notebook) read FRED as it stood on one day (ALFRED `realtime_start` = `realtime_end`). The day defaults to the committed `web/public/data/meta.json` `vintages.fred` (2026-10-27), and `make` passes it; a refresh moves it on purpose (`make all FRED_ASOF=2026-12-20`, say). Verified: a pinned ingest plus the notebook reproduce every committed results file and table byte for byte, so `findings.md:15` ($1.90T, $845B) no longer drifts. ALFRED writes some whole numbers as `1721271.0` and missing weeks as `.`; both are normalised so the tables match the fredgraph format exactly.
- **F2-2.** Eleonora will add the optional `DATABASE_URL_READONLY` Actions secret herself. Per the coordinator, raw-TCP Postgres does not pass this environment's proxy. The pipeline's DB tests now skip with the reason when the host is unreachable; `HHDEBT_REQUIRE_DB=1` (`make test-db`) makes that a failure.
- **F4-1 (a)** (`abc9894`). `nyfed_by_type` is now downloadable under the NY Fed Terms of Use, with their attribution line and source identifier ("Source: New York Fed Consumer Credit Panel/Equifax") in the JSON, `LICENSE-DATA.md`, `NOTICE-nyfed.txt` and on `/data`. I did the manual check first: the HHDC workbook has no use restriction beyond the general terms (`opendata/sources.md`).
- **F4-2 (A now, B later, never C).** A is built as the stable `/downloads/v1/` contract (`index.json`, `latest/`, `vintages/`, `opendata/CHANGELOG.md`). B is not built; exposing it later needs her approval.
- **F4-3 (archive).** `opendata/archive.mjs` stores each Z.1 release's snapshots gzipped in `opendata/archive/z1-<date>/` (about 0.2 MB each) and never overwrites one. `make ingest` runs it, and CI checks that the committed vintage is archived. `z1-2026-09-11` is archived and served at `/downloads/v1/vintages/z1-2026-09-11/`.
- **For F3 (coordinator):** the refresh workflow should run `make ingest FRED_ASOF=<run date>` and commit the new `opendata/archive/z1-<date>/` with the snapshots.

## Proposed changes to shared files
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
