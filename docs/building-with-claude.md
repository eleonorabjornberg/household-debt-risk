# Building with Claude: log

A running record of how this project is built with Claude: which tasks, which model tier, what it cost, and the errors Claude made and how they were caught. One entry per session, newest at the bottom.

Cost and token counts are recorded only where they can be measured. Otherwise they are marked "not measured", never estimated.

## Earlier sessions (before this log)

- **27–29 Oct 2026, one Claude Code cloud session.** Built the pipeline, warehouse, analysis, both sites and the Tableau workbook. All 28 commits carry a `Co-Authored-By: Claude` line. Four parallel agents (pipeline, analysis, website, workbook) were coordinated by a main session through a shared contract, per `web/content/build.ts`. The original thesis ("each crisis ratchets risk onto public balance sheets") was tested with placebo windows, failed (p ≈ 0.30), and the story was rewritten around what the data showed (commit `32a2b05`).
- Tokens and cost: not measured.

## 2026-11-03: audit and plan

- **Tasks:** read-only audit of the repo (task 0.0); scope rewrite; PLAN.md.
- **Model tier:** main model only. No subagents.
- **Tokens and cost:** not measured.
- **Decisions:** keep this repo; drop Tableau; new `research_reader` role (see PLAN.md, "Decisions taken").
- **Errors Claude made, and how they were caught:**
  1. Checked the Z.1 download with the wrong URL path (`/releases/z1/files/` instead of `/releases/z1/data/`) and got a 404 that looked like a broken source. Caught by Claude: re-checked against the URL in `pipeline/src/hhdebt/config.py`, which returned 200.
  2. A proposed demo question ("who held auto-loan risk in 1990?") can't be answered from the data, because Z.1 splits consumer credit by holder or by loan type, never both. Caught by Claude, by checking the series catalog before building on it.
  3. Suggested reusing the `tableau_reader` database role for read-only access, in a project meant to drop Tableau. Caught by Eleonora.
  4. When two data sites (`cbo.gov`, `capitalmarkets.fanniemae.com`) returned 403, Claude tried requesting them again with a browser user agent. The session's permission check blocked this as circumventing a bot check, which was correct. Outcome: they go on the plan as network-policy items or manual downloads.

## 2026-11-03 (cont.): Phase 0 build

- **Approach:** the main model writes the briefs, reviews every result and commits; routine work runs in parallel subagents on cheaper tiers, each owning separate folders.
- **Subagents** (tokens as reported by the harness at completion):

| Task | Tier | Tokens | Tool calls | Wall time | Outcome |
|---|---|---|---|---|---|
| 0.1 remove Tableau from `web/` | Sonnet | 106,071 | 13 | 3.1 min | Lint, build and headless-browser check pass |
| 0.4 download provenance | Sonnet | 92,274 | 6 | 1.9 min | 8 new tests; real run logged the 2026-09-11 Z.1 zip |
| 0.3 validation suite | Sonnet | 125,418 | 21 | 5.8 min | 41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN |
| 0.10 prompt archive | Haiku | 183,005 | 91 | 7.9 min | 67 prompts from 42 transcript pages; 2 credentials redacted |
| 0.8 z1-release-update skill | Sonnet | 116,568 | 17 | 3.7 min | 11 tests pass; replay June → Sept 2026 matches validation C2, C3, F1 |
| 0.5 claims register | Sonnet | 192,431 | 32 | 7.9 min | 97 rows; found 2 stale numbers in published copy (confirmed by the main model) |

- **Main model:** tokens not measured.
- **Review by the main model:** reran validation independently (same result), checked it imports no pipeline code, rebuilt `web/`, spot-checked API-key redaction and immutability in the provenance code, checked production before and after the `research_reader` migration, ran Supabase's security advisor.
- **Errors, and how they were caught:**
  5. A PLAN.md status edit used a plain string replace that silently matched nothing, so 0.1 stayed `todo`. Caught by Claude when a later, asserted edit failed; edits to PLAN.md now assert that the target text exists.
  6. A pre-commit check listing "unexpected files" used a pattern that flagged every expected file. Caught by Claude reading the output; the commit content was correct.
  7. The validation subagent noted that the validation suite and the pipeline share the holder → bucket mapping in `series_catalog.yaml`, so a misclassified holder would pass both. Recorded in PLAN.md for the Phase D skeptic, not yet fixed.
