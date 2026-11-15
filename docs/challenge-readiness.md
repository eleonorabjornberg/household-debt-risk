> **Claude draft.** This is a checklist built by Claude (coordinator session, 2026-11-06) for Eleonora to review. It is not the write-up and not the demo script: the design, validation, write-up and demo are hers (challenge integrity rule and CLAUDE.md authorship rule). It makes no claim about how the project will be judged. It contains no data numbers; every count below is a file count you can check with `ls`.

# Challenge readiness check: "Be a Master in Claude" (ieNYC × DataCamp)

**Deadline:** per Eleonora on 2026-11-15, submission is due that day. (The 12 Nov date first written here is out of date.)
**To submit:** (1) a 2–3 page write-up (problem, approach, how Claude was used, results and limits); (2) the artifacts (GitHub link or ZIP); (3) a 3–5 minute demo video. Items 1 and 3 are yours and are not started in the repo.

## Criterion 1: business relevance and clarity of the problem

| Evidence | Where |
|---|---|
| Problem statement and scope | `README.md`, `PLAN.md` (top), `CLAUDE.md` first line |
| Original analysis: who holds household credit risk | `analysis/findings.md`, `analysis/recommendation.md` (Claude draft), `research/` |
| Market-audience memo workflow | `.claude/skills/research-memo/` |
| Live public site | Hot Potato, production from `main`: https://hot-potato-credit.vercel.app (also household-debt-risk.vercel.app) |
| Long-form story with scenarios | `web/app/scenarios/` (B3) |

**Gaps.** The one-paragraph "why a desk/bank/insurer should care" framing exists only in Claude-draft form (`analysis/recommendation.md`); the write-up needs it in your words. You have not yet confirmed that hot-potato-credit.vercel.app loads (this session cannot reach *.vercel.app).

## Criterion 2: depth of Claude usage (skills, agents, MCP, API)

| Kind | What exists | Where |
|---|---|---|
| Skills (7) | chart-from-sql, claim-check, decision-cards, preregister, research-memo, source-provenance, z1-release-update | `.claude/skills/` |
| Subagents (6) | analyst, editor, prompt-archivist, quant-reviewer, register-keeper, skeptic | `.claude/agents/` |
| MCP server | household-credit MCP (read-only DB tools) | `mcp/household-credit-mcp/` |
| API app | "Ask Hot Potato" (D6): tool use against the database, cited queries | `atlas/app/api/ask/route.ts`, `atlas/lib/ask/`; production allowed since 2026-11-15, **off until its Vercel variables are set** |
| API benchmark | E1 question-to-SQL, Haiku vs Sonnet vs Opus | `evals/e1_sql_benchmark/` |
| Hooks | pre-commit register check + offline tests; block hand edits to `results.json` | `.claude/settings.json`, `.claude/hooks/` |
| Multi-session orchestration | coordinator + infra/markets/analysis track sessions, decision docket and review queue artifacts | `tracks/`, `docs/decision-cards.html`, `docs/review-queue.html` |
| Prompt archive | three session archives | `prompts/` |

**Gaps (updated 2026-11-15).** Ask runs in production only once Eleonora sets its Vercel variables and redeploys; until then a live Ask demo needs a local run. E4 P1 and P2 are run and labelled by models (UNVERIFIED); see `evals/e4_redteam/README.md`.

## Criterion 3: rigor (validation, verification, honest limits)

| Evidence | Where |
|---|---|
| Claims register: every published number traced to code, series, vintage, status | `claims/register.csv`, `claims/check_register.py` (run by the pre-commit hook) |
| Adversarial review log (skeptic, quant-reviewer) | `claims/review-log.md` |
| Pre-registrations written before results | `docs/decisions/` (e1, e2, c1b, a7 and others) |
| Scoring protocol, its erratum and deviations, kept in public | `docs/decisions/scoring-protocol*.md` |
| Holdout forecasts run once | PLAN C1/C2 |
| Red team of the Ask app | `evals/e4_redteam/` |
| CI | `.github/workflows/ci.yml` |

**Gaps.** E1 results note is a Claude draft with rows still UNVERIFIED until you check them. E2 (planted errors) and E3 (regression suite) are in progress. A6 and B4 are blocked by cbo.gov returning 403 (a limit to state, not hide). Update 2026-11-07: Eleonora has added this limit to her write-up.

## Criterion 4: quality of documentation and demo

| Evidence | Where |
|---|---|
| Build log: tasks, models, costs, errors and who caught them | `docs/building-with-claude.md` |
| Decisions credited to you | `PLAN.md` "Decisions taken" |
| One-command rebuild | `make all`, `make ci` |
| Open data, source pages | F4 downloads; F1 `/sources` on the site |

**Gaps.** Demo video and write-up not started (yours). The duplicate Vercel project `household-debt-risk-web` (your call: useless duplicate) is still listed under your Vercel account; reviewers following a stale link could land on it.

## Possible demo click-path (a list of places, not a script)

1. The live site at hot-potato-credit.vercel.app: the dot-flow view.
2. Click a number → source popover → `/sources` (claims register in the app).
3. `web/` `/scenarios`.
4. In Claude Code: a skill (e.g. `claim-check` on a sentence) and a subagent (`skeptic`) logging to `claims/review-log.md`.
5. The MCP server answering a data question with series IDs and vintage.
6. E1 benchmark results and the E4 red-team catalogue.
7. The pre-commit hook blocking a commit with an untraced number.
8. The decision docket / review queue as the human-in-the-loop.

## Open items before submission (owner; updated 2026-11-15)

- Write-up, 2–3 pages (Eleonora).
- Demo video, 3–5 min (Eleonora).
- Confirm the production site loads (Eleonora).
- Ask live: production OK given 2026-11-15; set the Vercel variables and redeploy (Eleonora).
- E4 P2: run and model-labelled (P2 labels by Claude at her instruction, 2026-11-15); her review of the labels is open.
- Check the E1 UNVERIFIED rows (Eleonora).
- Artifacts: Eleonora chose a GitHub link (2026-11-07). The repository is **private** as of 2026-11-07, so the judges cannot open the link until she makes it public or gives them access (Eleonora).
