> **Claude draft.** Independent review of the whole repository from the judges' point of view, by a Fable 5.2 subagent (high effort, read-only, offline), run on 2026-11-15 at Eleonora's request. The scores are model opinions, not the judges'. Spot-checked by the coordinator: README line 57, the missing live URL in the README and `atlas/content/build.ts` "More than 40 automated tests" were confirmed.

# Judge-lens review, 2026-11-15

Offline tests run by the reviewer all pass: atlas 190, pipeline 25 (25 skipped, no data), claims and validation 29, MCP 39. `claims/check_register.py` passes. Not checked (no network): the live site, the CI badge and repo visibility.

## Scores

| Criterion | Score | Strongest evidence | Biggest weakness |
|---|---|---|---|
| Business relevance and clarity | 7/10 | Sharp question with a surprising answer, and the original thesis tested and rejected (`README.md` 16–19); `analysis/recommendation.md`; `research-memo` skill for named desks | No one-line "who uses this and for what decision"; the README opens as economic history; the "so what" is only a Claude draft |
| Depth of Claude usage | 9/10 | 7 skills, 6 subagents, blocking hooks; own MCP server with structured refusals; Ask API app with a fail-closed gate and cost cap; E1 benchmark (720 loops, 3 models); `plugin/fed-data-desk/` | Ask is off in production; the project MCP server is not in `.mcp.json` |
| Rigor | 8.5/10 | `validation/REPORT.md` (136 PASS, 0 FAIL); frozen pre-registrations with dated deviations; E2 isolation breach disclosed and rerun; unflattering E1 results reported | 2,285 of 2,530 register rows UNVERIFIED; E2 at the ceiling (14/14) with the plain baseline also 8/8; model second rater; Claude wrote the E1 questions |
| Documentation and demo (repo only) | 6/10 | `docs/building-with-claude.md` logs tier, tokens and who caught each error; `make all` / `make ci` | README stale and undersells; `PLAN.md` is 80 KB of internal shorthand; no evals index |

## Top five fixes (impact per minute)

1. **Eleonora, 5 min.** Confirm the repo is public, the production site loads and the CI badge is green.
2. **Claude, 15 min, `README.md`.** Add the live URL; fix line 57 ("plugin/ and evals/ planned", both exist), line 48 (6 research tasks listed, 15 exist), line 45 (1 of 7 skills named); add a "How Claude was used" table. The register pins lines 16–19, 23–28 and 99, so edit without shifting them or repoint the rows.
3. **Claude, 20 min.** `evals/README.md` index for E1–E4 (Claude draft); fix the stale `evals/e2_planted_errors/README.md` title ("not run", prereg "draft"); E4 has no readable summary.
4. **Eleonora, 20–30 min.** Set the Ask variables in Vercel and redeploy, or record the Ask segment locally.
5. **Claude, 5–15 min.** Stale status: `PLAN.md` line 20 ("not yet merged"), `docs/challenge-readiness.md` (12 Nov deadline, Ask off by her choice). `claim-check` gives a false MISMATCH on README "p ≈ 0.30" (picks "99" from "MC 99% interval" in check H6).

Eleonora, in the write-up: state the UNVERIFIED share and the E2 ceiling before a judge finds them.

## Confusing or overclaimed on first contact

- About 90% of register statuses are UNVERIFIED, while the `analysis/recommendation.md` banner says "The numbers are checked and registered".
- README describes two sites; the 2026-11-07 decision made it one. The status of `web/` is unclear.
- README's local database block applies one migration; `CLAUDE.md` applies three.
- `make evals` prints "E1: RERUN NEEDED" without explanation.
- Internal shorthand (docket and card numbers, round numbers) throughout `PLAN.md`, the log and results notes.
- `atlas/content/build.ts`: "More than 40 automated tests"; there are about 280.
- PLAN F5 (the build log) shows "todo (ongoing)".
- Stale `docs/status-2026-11-04-morning.md`; `mcp/household-credit-mcp/examples/transcripts.md` predates a field rename.
- The duplicate Vercel project `household-debt-risk-web` is still mentioned in `prompts/`.

## Suggested demo opening

The audit loop, live: the dots moving through 2007–11 on Hot Potato, a click on 56.4% to its register row on `/sources`, then `claim-check` returning MATCH recomputed from the Fed's raw file, then a one-digit change refused by the pre-commit hook, and one sentence on E2's disclosed isolation breach and rerun.
