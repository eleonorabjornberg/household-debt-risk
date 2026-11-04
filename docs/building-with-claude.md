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

## 2026-11-04: finishing Phase 0 (session_01GDxCQ4PEo3YCh72CZhKaU4)

- **Tasks:** 0.8 stale-claims step and unit reconciliation; 0.7 recommendation v1 and Hot Potato copy; 0.9 README index and reproduce steps; 0.10 prompts from the 3–4 Nov session. 0.5 (the register) was finished by the previous session, which was still running in parallel and pushed it at 00:05.
- **Environment:** `FRED_API_KEY` set; `DATABASE_URL_READONLY`, `DATABASE_URL`, `ANTHROPIC_API_KEY` unset. The network policy now denies www.federalreserve.gov, FRED and newyorkfed.org (proxy 403; all reachable on 3 Nov), so validation could not be rerun and check D2 and the `research_reader` permission test were not run.
- **Model tier:** main model for the recommendation, the copy, the review and the register edits; subagents below.
- **Subagents** (tokens as reported by the harness at completion):

| Task | Tier | Tokens | Tool calls | Wall time | Outcome |
|---|---|---|---|---|---|
| 0.10 prompts of session_01GDxCQ42apfBERQ1Fw4qyjV | Haiku | 129,310 | 38 | 3.1 min | 18 prompts, commit-linked, 0 redactions needed; reviewed and committed. The main model added a 19th, typed after the subagent ran |
| 0.5 claims register | Sonnet | not reported (stopped) | not reported | ~6 min | Stopped unused: the other session had already pushed a register. Partial files discarded, nothing committed |

- **Previous session cost** (harness figure for session_01GDxCQ42apfBERQ1Fw4qyjV, main model, 3–4 Nov): $12.61, 292,112 output tokens. This session's main-model tokens: not measured.
- **Errors, and how they were caught:**
  8. Two sessions worked on the same branch at once. This session briefed a subagent to build `claims/register.csv` because the branch did not have one at session start; the previous session pushed its own six minutes later. Caught when the push was rejected as non-fast-forward. The subagent was stopped, its partial work set aside, and this session's commits rebased on the pushed register. Lesson: before delegating, check that the previous session is idle (`get_session`), not only that the branch lacks the file.
  9. The recommendation draft quoted Z.1's 2026Q2 scope change as $198B, which Eleonora had just corrected to +$199B (data $198.53B). Caught by the register check once `analysis/recommendation.md` was added to the files it scans.
  10. The README index insertion shifted the line numbers that register rows point at, and two rows pointed at copy that had been replaced (the "1 of 11" stat). `check_register.py` only checks that a line exists, not that the number is on it, so it passed anyway. Caught by a one-off script that checks each location's line for the display text; rows fixed. Proposed for Phase D: make the check verify the text on the line.
  11. The old Hot Potato copy said a GSE release from conservatorship "would move the biggest pile back across the line". Under the site's own definition, GSEs count as public in or out of conservatorship. Caught by the main model while writing 0.7; corrected.
- **Later the same session:** Eleonora approved the four 0.7 copy fixes and allowed the four data hosts. Fresh-clone check: cloned the branch into the scratchpad, followed README steps 1–3, and validation reproduced the committed report exactly (44 checks, same status and observed text; only the run time differs). The four copy fixes changed line numbers in three files, so register locations were remapped with a line diff rather than by hand, then every location was checked for its display text.
  12. The register's own check passed while three rows' display spellings didn't match the wording on the line ("18.8 points", "more than one point"). Caught by the same line-content script; spellings added. This is the same gap as error 10.
  13. Describing the old COVID step, the main model wrote "+2.3 points" by subtracting the rounded shares (57.5 − 55.2); the unrounded change is +2.24, so +2.2. Caught by the register scan of the recommendation, which flagged the number as unregistered; reworded without a new figure.
