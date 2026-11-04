> **Claude draft, not frozen.** Drafted by Claude (`preregister` skill) for Eleonora. The design choices are hers. Every `CHOICE-E1-n` below is **open** until she decides it, and her decisions go in the Decisions table with dates. Nothing in this file may be run against the API until she has frozen it and separately approved the full-run spend.

# Pre-registration: E1, question-to-SQL benchmark (Haiku vs Sonnet vs Opus)
Status: **draft**, 2026-11-04. Not frozen. No full-E1 result exists.

## What has already been seen (disclosed before any choice is made)
A **cost pilot** ran on 2026-11-04 (approved by Eleonora, cap $2.98; `evals/e1_sql_benchmark/pilot-2026-11-04/`, commit `a4998b7`). It used 10 easy questions (9 of them single-tool `public_share` lookups), 1 loop per model, effort `medium`, at most 4 turns. What was seen:
- cost per loop: Opus 5.5 $0.0403, Sonnet 5.5 $0.0102, Haiku 5.5 $0.0008;
- pilot accuracy: Opus 10/10, Sonnet 9/10 (the miss ran out of the 4-turn limit), Haiku 10/10;
- the tools the models chose, and the answer format working as parsed.

So this design is **not blind** to the pilot. That bears on CHOICE-E1-4 (turn limit), CHOICE-E1-1 (difficulty mix) and the cost cap. The 10 pilot questions are excluded from the scored set (see Data), and the write-up must say the pilot was seen.

## Question
On factual questions about who holds US household credit risk, answered only through the project's read-only household-credit MCP tools, how do Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 compare on accuracy, cost per question, cost per correct answer, and latency? Do they refuse questions the data cannot answer?

## Hypotheses and what counts as support
The framing is open (**CHOICE-E1-8**). Under a confirmatory framing the candidates are:
- **H1** (per model): accuracy on answerable questions is at least a threshold *T* (Wilson 95% lower bound ≥ *T*).
- **H2** (between models): Opus and Sonnet differ in accuracy, and Sonnet and Haiku differ in accuracy (paired, exact McNemar).
- **H3** (refusals): on unanswerable questions, each model's correct-refusal rate is at least *R*.
- Cost per correct answer and latency are always descriptive.

Support: lower bound ≥ threshold, or McNemar p below the corrected α. Null: the interval contains the threshold, or no significant paired difference. Against: the upper bound is below the threshold.

## Data
- **Backend:** the MCP server's snapshot backend (`DATABASE_URL_READONLY` and `DATABASE_URL` unset), so production is never queried.
- **Data files:** `web/public/data/*.json`, Z.1 vintage **2026-09-11**, NY Fed and FRED vintages 2026-10-27 (`meta.json`). The SHA-256 of every snapshot file is recorded at the freeze. If a Z.1 release lands between freeze and run, the run still uses the frozen files, checked by hash.
- **Coverage** (from the `data_coverage` tool): public/private share and six risk buckets, 1951Q4–2026Q2; collateral coverage by class; 14 crisis windows (-8..+16 quarters); NY Fed CCP by loan type, 2003Q1–2026Q2; the claims register. It cannot answer: holder × loan-type crosses, out-of-range or future quarters, loan- or borrower-level questions, geography, sub-quarterly frequency.
- **Question set:** about 100 new questions, not the 10 pilot questions. The composition is **CHOICE-E1-1**, who writes them is **CHOICE-E1-3**, and how answers are verified is **CHOICE-E1-2**. The set is committed, with gold answers, before the freeze. No model sees it before the run.
- **Gold answers, verified with no model.** Every answer is computed two independent ways and both must agree to the stated tolerance. Path 1 recomputes from the snapshot the MCP server serves (as `verify.py` does now). Path 2 is either a validation-PASS row in `claims/register.csv` or a second computation from the raw source files. Known gap: the NY Fed and collateral tools have **no PASS register rows**, so their questions need path 2 from raw files (CHOICE-E1-2). Unanswerable questions have no number. Their gold is "refuses", and each is checked against the `cannot_answer` list and `check_answerable`.

## Method (fixed settings)
- **Models:** `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`. The served `response.model` is logged on every call.
- **Harness:** `evals/e1_sql_benchmark/pilot.py`, generalised. It has a manual tool-use loop, `tool_choice` auto and adaptive thinking (always on for these models). Server-side refusal fallbacks are off, so a refusal is never answered by another model. A `stop_reason` of `refusal` counts as a refusal.
- **System prompt and answer format:** as in the pilot, ending in `ANSWER:` and `QUARTER:` lines. The text is frozen with this file and fingerprinted by `evals/regression.py`.
- **Tools:** the 10 household-credit MCP tools with their docstrings as of the freeze (**CHOICE-E1-9** on `lookup_claim`).
- **Effort:** **CHOICE-E1-6**.
- **Turn limit:** **CHOICE-E1-4**. A loop that ends at the limit without an `ANSWER:` line is scored wrong, and is also counted separately as "truncated".
- **Repetitions:** **CHOICE-E1-7**.
- **Order:** questions shuffled with a fixed seed (**CHOICE-E1-10**); within each question the three models run back to back, cheapest first, so a cost stop leaves comparable data for all three.
- **Caching:** a `cache_control` breakpoint on the system prompt (prefix of tools plus system). Whether to keep the pilot's top-level automatic cache is **CHOICE-E1-5**. Caching does not change model outputs, only cost.
- **Logged per call:** the four `usage` token kinds, cost at the live prices on the run date, latency, `stop_reason`, text and tool calls. Never the key or any request header.

## Scoring (fixed before the run)
**CHOICE-E1-11** sets the rule. Options:
- (a) The pilot rule unchanged: correct if the `ANSWER:` number, read in the unit the model states and converted to the question's unit, is within tolerance of gold, and the quarter matches where one is asked. A refusal or no number is wrong.
- (b) As (a), and the answer must also name the source (Z.1 or NY Fed). This catches a right number from the wrong source, at the cost of a second, partly textual check.
- (c) As (a), with partial credit for the right number in the wrong quarter, or the reverse. Finer-grained, but harder to compare with the pilot.

For every rule, on unanswerable questions a response is correct only if it gives no number and says the data cannot answer. Tolerance is half a unit in the last place of the register value, or the per-unit tolerance stated in the question file. The scorer is `score()` in `pilot.py`. A human re-scores a seeded random 20% of answers (seed per CHOICE-E1-10), as in E2.

## Benchmarks and holdout
- **Baseline, CHOICE-E1-12:** (a) none; (b) a no-tools run on one model (answers from memory), which shows what the tools add, for about 1/3 of one model's cost; (c) a "check_answerable only" baseline for the refusal questions.
- **Holdout for E3:** **CHOICE-E1-13**: (a) none, since E3 reruns the full set; (b) hold back 20 questions, unseen until the first E3 rerun, to check that later prompt changes do not overfit the 80.

## Multiple testing
Under a confirmatory framing there are 3 per-model H1 tests, 2 H2 comparisons and 3 H3 tests, so 8 tests: Holm correction at α = 0.05 within each family. Under a descriptive framing: intervals only, no verdicts (as E2 CHOICE-12 (i)).

## Cost cap and stops (figures are estimates; the cap is Eleonora's, CHOICE-E1-14)
- **Re-estimate from the pilot.** At the pilot's token profile, 300 loops per model (100 questions × 3 repetitions) cost Opus $12.08 + Sonnet $3.05 + Haiku $0.25 = **$15.37**. The full set is harder (multi-tool, more turns), so a planning figure of **2× is about $31**. A baseline (CHOICE-E1-12 (b)) adds up to $4 on Opus. Dropping the top-level cache (CHOICE-E1-5 (b)) probably lowers all of these; that is not measured.
- **Cap options:** (a) **$31**, the 2× planning figure with no margin; (b) **$46**, 3× pilot profile, i.e. 1.5× the planning figure; (c) **$62**, 4× pilot profile. Under (a), an ordinary difficulty overrun stops the run part-way. Under (c), the spend is about the original pre-pilot estimate ($59.74).
- **Stops, checked after every call, as in the pilot:**
  1. The running total reaches the cap. A pre-call guard stops before any call could cross it.
  2. Any model's mean cost per loop exceeds 1.5× its planning figure, that is 3× its pilot mean: Opus $0.121, Sonnet $0.030, Haiku $0.0025.
  3. **Checkpoint** after the first 10% of loops: project the total; if the projection exceeds the cap, stop and report before going on.

  On any stop, the triggering call is recorded, the run ends, and partial results are reported as partial.

## Decision rules
- Confirmatory framing: each H is reported as supported, null or against, by the rules above. A model "is more accurate" only if its paired McNemar test survives Holm.
- Descriptive framing: accuracy with Wilson 95% intervals, the paired disagreement table, cost per correct answer, and latency median and p90, with no ranking language beyond what the intervals show.
- Every published E1 number gets a `claims/register.csv` row pointing at the results file.

## What is and is not identified
- Identified: accuracy and cost **of this harness** (these tools, this prompt, this turn limit and effort) on **this question set** and data vintage.
- Not identified: general text-to-SQL ability (no SQL is written; the tools wrap fixed queries); performance on the live database backend; performance at other effort levels or prompts; D6 reader-question costs (prose answers, different length).
- Question-writer effect: if Claude writes the questions (CHOICE-E1-3 (a)), the question style may favour Claude models in ways a human-written set would not.

## Open choices (all Eleonora's; no recommendation unless stated with a reason)
| ID | Choice | Options and trade-offs |
|---|---|---|
| CHOICE-E1-1 | Question mix (about 100) | (a) stratified by tool family (public share, buckets, crisis windows, collateral, NY Fed, register/coverage) × difficulty (single lookup / computation such as diff or argmax / multi-tool), with about 15 unanswerable; (b) the same, weighted to the tools D6 readers will use most; (c) unstratified, written freely. Strata make per-cell results readable but cells are small (about 5 questions each) |
| CHOICE-E1-2 | Second verification path where no PASS register row exists (NY Fed, collateral) | (a) recompute from raw source files with a separate script (no shared code with the export); (b) first add PASS register rows through `validation/`, then verify as the pilot did; (c) drop questions without a PASS row (leaves NY Fed and collateral out of E1) |
| CHOICE-E1-3 | Who writes the questions | (a) Claude drafts all, Eleonora approves the set; (b) Eleonora writes about 30, Claude the rest, reported separately; (c) Eleonora writes all. (a) is cheapest but carries the question-writer effect above |
| CHOICE-E1-4 | Turn limit | (a) 4, as in the pilot; (b) 6; (c) 8. Pilot evidence: 1 of 30 loops (Sonnet, q03) was cut off at 4 while retrying out-of-range quarters, and the full set is harder. A higher limit measures the model more than the harness, but raises the worst-case cost per loop |
| CHOICE-E1-5 | Top-level automatic cache | (a) keep, as in the pilot (cost comparable with the pilot); (b) drop it and keep only the system/tools breakpoint (probably cheaper for 2-turn loops, not measured). Either way accuracy is unaffected |
| CHOICE-E1-6 | Effort | (a) `medium` for all three, as in the pilot; (b) each model's default (Opus and Haiku `medium`, Sonnet `high`); (c) two levels per model, which doubles the cost |
| CHOICE-E1-7 | Repetitions | (a) 1; (b) 3 (the basis of the estimate); (c) 5. Repetitions measure run-to-run variation; with 1, the intervals rest on question sampling alone |
| CHOICE-E1-8 | Framing | (a) descriptive (intervals, no verdicts); (b) confirmatory, with thresholds *T* and *R* set here; (c) descriptive for H1/H3, confirmatory for H2 only |
| CHOICE-E1-9 | `lookup_claim` tool | (a) keep all 10 tools (as D6 will have them); (b) remove it for E1, since it can return a registered value directly, which makes register-backed questions retrieval rather than computation; (c) keep it and report register-backed and other questions separately |
| CHOICE-E1-10 | Seed | (a) a fixed integer written here before the freeze (E2 used `20261104`); (b) another fixed integer |
| CHOICE-E1-11 | Scoring rule | (a), (b) or (c) under Scoring |
| CHOICE-E1-12 | Baseline | (a), (b) or (c) under Benchmarks |
| CHOICE-E1-13 | Holdout | (a) or (b) under Benchmarks |
| CHOICE-E1-14 | Cost cap | (a) $31, (b) $46 or (c) $62, under Cost cap. The full run also needs her separate spend approval |

## Decisions
None yet.

## Deviations (dated, after freezing)
None (not frozen).
