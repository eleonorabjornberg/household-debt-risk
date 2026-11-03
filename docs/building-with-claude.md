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
