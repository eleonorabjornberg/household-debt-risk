# Track: Infrastructure

Branch: `claude/track-infra` · Tasks, in order: F1, F2, F4 · Rules: PLAN.md "Parallel tracks".

## Status
| Task | Status | Notes |
|---|---|---|
| F1 | ready for review | Every register row on both sites is a hover/focus popover + link to `/sources#<id>`; 46/49 web and 27/29 atlas rows link in the prerendered HTML, the rest are listed with reasons in `claims/site/unlinked.json` (3 are register fixes below) |
| F2 | ready for review | `make all` and `.github/workflows/ci.yml`; evals join once E3 exists. Reproduction gap: FRED inputs are not pinned (question F2-1) |
| F4 | ready for review, 3 questions open | Downloads, dictionary, licence notes, chart-text check, API plan (nothing exposed). NY Fed data link-only until F4-1 is answered |

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
- **F2-1. FRED inputs are not pinned, so `make all` drifts.** `analysis/notebook.py` downloads the latest FRED observations. A rerun moves the published Fed-MBS figures in `findings.md:15` ($1.90T, $845B) whenever WSHOMCB updates. Options: (a) pin FRED to the committed vintage with ALFRED `realtime_end` (in `meta.json` / the register vintage) so reruns are exact, and let a refresh move the vintage on purpose; (b) accept the drift and mark those two rows as moving weekly; (c) drop the weekly figure from the findings. **Recommendation: (a).** It is a notebook change in the analysis track's area, so I have not made it.
- **F4-1. NY Fed data.** The NY Fed's terms allow sharing, but anyone who redistributes must keep their terms and attribution ("© 2026 Federal Reserve Bank of New York. Content from the New York Fed subject to the Terms of Use at newyorkfed.org."). So `nyfed_by_type` cannot go out under CC BY 4.0. Options: (a) redistribute it under the NY Fed terms with their attribution line, as a separately licensed file; (b) link only. **Recommendation: (a), after a manual check that the HHDC data carry no extra use restriction (the HHDC page loads with JavaScript, so I could not see one).** It stays link-only until you answer.
- **F4-2. Public API.** Option A (static versioned downloads, done), B (read-only JSON API from the committed snapshots, on the web site) or C (document Supabase REST). **Recommendation: A now, B when there is a user, never C.** Details in `opendata/api-plan.md`. Nothing is exposed.
- **F4-3.** Keep old vintages downloadable (an archive per Z.1 release)? Recommendation: yes, from F3 on, since it costs only storage.
- **F2-2. Optional repository secret `DATABASE_URL_READONLY`** (Settings → Secrets and variables → Actions). It lets CI's validation run check D2 against `mart.public_share`. CI is green without it. `research_reader` is read-only with a 15 s timeout, so it is safe to add.

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
