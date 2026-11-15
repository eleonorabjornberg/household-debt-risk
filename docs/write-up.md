> **Claude draft.** Written by Claude in Eleonora's register for her to replace with her own text. The design, the decisions and the validation are hers (`PLAN.md`, "Decisions taken"). Every number below has a row in `claims/register.csv` (eval numbers in `claims/tracks/infra.csv`); numbers marked UNVERIFIED there are traced but not independently recomputed.

# Hot Potato: who holds America's household credit risk

Eleonora Björnberg. "Be a Master in Claude" challenge, ieNYC × DataCamp, submitted 2026-11-15.
Repository: github.com/eleonorabjornberg/household-debt-risk. Live site: https://hot-potato-credit.vercel.app

## 1. Problem

The public sector now holds most of America's household credit. In 2026Q2 federal agencies, the GSEs and their pools held 56.4% of household mortgage and consumer credit ($10.77T of $19.10T, Fed Z.1, vintage 2026-09-11), up from 3.2% in 1952. The shift came in two steps. The 1980s added +18.8 pp as securitization moved mortgages into agency pools. The financial crisis added 13.1 points between 2007Q4 and 2011Q4 (36.1% to 49.2%), in the 98th percentile of all 16-quarter windows since 1952, and half of that was private lenders retreating. It never reversed. The public sector also holds 86% of student loans and 51% of all uncollateralized household debt, up from 7% in 2007.

This matters to anyone who prices or holds the other side of that risk. An agency MBS desk, a bank treasury and an insurer's ALM team each face a market where the marginal holder of household credit is a policy actor, which does not sell into losses the way a private balance sheet does. The project asks three questions: who holds the risk, how it is priced, and where it is going. It answers them from free public data only (Fed Z.1 Financial Accounts, NY Fed Consumer Credit Panel, FRED, SEC filings), so anyone can rebuild every number.

## 2. Approach

- **Pipeline.** A Python package (`pipeline/`, `hhdebt`) extracts every Z.1 vintage, transforms it into holder buckets and loads a Postgres warehouse in three layers: `raw` keeps every vintage, `core` the latest, `mart` the analysis views. `make all` rebuilds everything from a fresh clone.
- **Claims register.** Every published number has a row in `claims/register.csv` with the code path, series IDs, vintage and a validation status. A pre-commit hook runs the register check and the offline tests and blocks the commit if either fails.
- **Independent validation.** `validation/run.py` recomputes headline numbers from the raw Fed files without importing the pipeline, so a bug in the pipeline cannot also pass its own check. A number is `PASS` only when that recomputation agrees.
- **Pre-registration.** Statistical tests (the structural-break and placebo tests, the forecasts, the evals) were written down in `docs/decisions/` before any result existed. Deviations are dated in the same files.
- **One public site.** Hot Potato (`atlas/`) shows holdings as moving dots, quarter by quarter, with the dashboard, research pages, scenarios and methods; each number opens its register row on `/sources`. The first story site (`web/`) stays in the repository; its pages moved into Hot Potato on 2026-11-07 (Eleonora's decision).

## 3. How Claude was used

Claude built, checked and drafted; Eleonora designed, decided and validated. Her decisions are logged with dates in `PLAN.md`, and the build log (`docs/building-with-claude.md`) records every session's tasks, model tier, cost and each error with who caught it.

| Feature | What it does here |
|---|---|
| 7 skills | `claim-check` traces a number to its register row and recomputes it; `z1-release-update` runs a new Fed release end to end and stops for approval; `preregister`, `source-provenance`, `research-memo`, `chart-from-sql`, `decision-cards` |
| 6 subagents | `skeptic` (data definitions, revisions, double counting) and `quant-reviewer` (leakage, multiple testing) log objections to `claims/review-log.md`; `register-keeper`, `editor`, `analyst`, `prompt-archivist` |
| MCP server | `household-credit`: read-only tools over the warehouse that refuse questions the data cannot answer and name the nearest answerable one |
| API app | Ask Hot Potato (`atlas/app/api/ask/`): a question box on the live site that answers through tool use against the database, cites its sources and declines forecasts and out-of-scope questions; rate limits fail closed |
| Hooks | pre-commit register check and tests; hand edits to any `results.json` blocked |
| Multi-session orchestration | a coordinator session and infra, markets and analysis track sessions working in parallel; decisions reached Eleonora as tap-to-answer cards (decision docket, review queue) |
| Prompt archive | the prompts she typed, verbatim and redacted, linked to the commits they produced (`prompts/`) |

**Evals of the tooling.** The tools themselves were tested, each against a pre-registration.
- **E1, question to SQL.** 80 questions, Haiku, Sonnet and Opus 5.5, three repetitions each (720 loops, no API errors). Accuracy on answerable questions: Opus 91.7%, Sonnet 96.1%, Haiku 92.8%. Correct refusal of unanswerable questions separated the models: Opus 91.7%, Sonnet 68.3%, Haiku 40.0%. Cost: Opus $12.11, Sonnet $5.47, Haiku $0.32. A no-tools Opus baseline answered 0.0% of the answerable questions, so the MCP tools carry the accuracy. Total E1 spend was $20.05 of a $31 cap.
- **E2, planted errors.** A script planted errors under a hidden key; the `skeptic` subagent caught 8 of 8 planted data errors and `quant-reviewer` 6 of 6 planted method errors, with 0 of 3 counted objections on clean control documents being false alarms. The first run had an isolation breach, found by a second-rater model and disclosed; Eleonora chose a rerun with each reviewer in its own folder.
- **E4, red team.** Attacks on the Ask box (forecast smuggling, false premises, injection, exfiltration) before and after guardrails. No secret or system-prompt text leaked.

## 4. Results

- The public share of household credit rose from 3.2% (1952) to 56.4% (2026Q2), in two steps: the 1980s (+18.8 pp) and the financial crisis (+13.1 pp, 2007Q4 to 2011Q4). The 2001 recession moved it the other way (−3.8 pp).
- A placebo test of the crisis step against 282 windows (1952Q1 to 2022Q2) gives p ≈ 0.30. The test has low power, so it neither confirms nor rejects that the crisis step was unusual.
- Real estate value was 3.56× mortgage debt in 2026Q2, so mortgages remain well secured in aggregate. The growth in the public book is in student loans and other uncollateralized debt.
- Ask Hot Potato runs in production. On 2026-11-15 a test question was answered from the warehouse with Z.1 vintage 2026-09-11, and a question the data cannot answer (a banks-only mortgage share) was declined.

## 5. Limits

- **Verification.** Of 2,530 register rows, 2,285 were UNVERIFIED at the start of submission day: traced to code and series, not recomputed independently. 64 of them appeared on public pages (README and the site). On 2026-11-15, 62 independent checks were added that recompute those numbers from the raw Fed Z.1, FRED and NY Fed files without the pipeline's code; all 62 pass. The other two cannot be recomputed (a description of the NY Fed panel and a count of the project's tests) and stay UNVERIFIED with a note. 2,223 rows remain UNVERIFIED: research and eval intermediates that no public page shows. Three of the new checks read FRED's latest files rather than the pinned vintage, so a revision to disposable income could move two of them.
- **E2 cannot separate the prompts from the model.** Both reviewer agents hit the ceiling, and the plain baseline also located every planted data error (8 of 8). The E2 second rater (Fable 5.2) is a model, not the second human the pre-registration named.
- **Who wrote the tests.** Claude wrote the E1 questions and the E4 attacks. E1's gold answers were recomputed by script from the data, without a model, but the question set may still suit the tools Claude built. The E1 results describe the tooling as of 2026-11-05; prompts changed afterward, so the regression check flags E1 for a rerun, which needs Eleonora's approval to spend.
- **E4 labels are model labels**, and the held-out paraphrases were written by the same author as the guardrails, so they are held out in time only; the author saw them while building the guardrails.
- **Blocked sources.** Two tasks that needed CBO documents (A6, B4) are blocked: cbo.gov refuses requests from the build environment, and the project does not work around bot checks.
- **Holder is not risk-bearer.** Z.1 records who holds a loan, not who loses when it defaults. Agency guarantees and private credit-risk transfer move losses away from the holder; the site says so where it matters.
