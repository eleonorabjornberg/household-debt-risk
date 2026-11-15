> **Claude draft.** Index written by Claude for Eleonora to replace. The eval designs and the decisions to run them are hers (`PLAN.md`, "Decisions taken"). Results are model runs scored by scripts and, where noted, labelled by models; they stay UNVERIFIED until she reviews them. Numbers are not repeated here: each results file carries its own, and only numbers with a row in `claims/register.csv` are published.

# Evals of the Claude tooling

These test the tools that build and check the research, not the research itself. Each eval was pre-registered (`docs/decisions/`) before any result existed, and each deviation is dated in its pre-registration.

| Eval | Tests | Status | Results |
|---|---|---|---|
| **E1** question-to-SQL benchmark | Haiku, Sonnet and Opus answering data questions through the project's MCP tools: accuracy on answerable questions, refusal of unanswerable ones, cost and latency | Run 2026-11-05 complete; results are a Claude draft, UNVERIFIED | [`e1_sql_benchmark/RESULTS.md`](e1_sql_benchmark/RESULTS.md) |
| **E2** planted-error test | Whether the `skeptic` and `quant-reviewer` subagents catch errors planted by a script with a hidden key, against a no-prompt baseline | First run had a disclosed isolation breach; rerun `run-20261113r` scored 2026-11-14 | [`e2_planted_errors/README.md`](e2_planted_errors/README.md), [`run-20261113r/results-note.md`](e2_planted_errors/run-20261113r/results-note.md) (register rows `e2_r13r_*`) |
| **E3** regression suite | One command that says whether E1 or E2 must be rerun because a prompt, agent or scorer changed | Built | [`regression.py`](regression.py) (`python evals/regression.py status`, or `make evals`) |
| **E4** red-team of Ask Hot Potato | Attacks on the site's question box: forecast smuggling, false premises, injection, exfiltration and more | Passes P1 and P2 run 2026-11-06; labels are model labels, UNVERIFIED | [`e4_redteam/README.md`](e4_redteam/README.md) |
| **D6** Ask Hot Potato smoke run | The Ask app's answers and refusals on a fixed question set during the build | Run 2026-11-06 | [`d6_ask/run-2026-11-06/`](d6_ask/run-2026-11-06/) |

## Why `make evals` says "E1: RERUN NEEDED"

E3 fingerprints every input an eval depends on (agent prompts, the pre-registration, the runner). After the E1 run, `.claude/agents/analyst.md`, `docs/decisions/e1-prereg.md` and `run_e1.py` changed (documentation of deviations and later fixes), so the fingerprint no longer matches and E3 flags E1 as stale. It means "the published E1 results describe an earlier version of the tooling", not that the run failed. A rerun costs API money and is not started without Eleonora's approval.

## Known limits

- Claude wrote the E1 questions and the E4 attacks; E1's gold answers were recomputed by script from the data, without any model (`e1_sql_benchmark/verify.py`).
- E2 reached the ceiling for both agents, and the plain baseline also caught every planted data error, so E2 cannot separate the prompts from a capable base model.
- The E2 second rater (Fable 5.2) and the E4 labels (Claude, at Eleonora's instruction of 2026-11-15) are model judgments, disclosed in the results files.
