> **Claude draft, not frozen.** Drafted by Claude (`preregister` skill) for Eleonora. The design choices are hers. Her decisions of 2026-11-05 are recorded below. **Still open: R (card e1-R2), how the h3 (b) change is made to the approved set (card e1-set-h3), and how the clustering enters the tests (CHOICE-E1-17, to be carded).** The file is frozen only after these. Nothing here may be run against the API until it is frozen and she has separately approved the spend.

# Pre-registration: E1, question-to-SQL benchmark (Haiku vs Sonnet vs Opus)
Status: **draft**, updated 2026-11-05 with Eleonora's choices. Not frozen. No full-E1 result exists.

## Decisions (Eleonora, 2026-11-05 05:19–05:22 UTC, docket round 9; PLAN.md "Decisions taken", coordinator commit `77460b4`)
| Choice | Decided |
|---|---|
| CHOICE-E1-1 question mix | (a) stratified by tool family × difficulty, about 15 unanswerable |
| CHOICE-E1-2 second verification path | (b) PASS register rows first, through `validation/`, then checked as in the pilot |
| CHOICE-E1-3 question writer | (a) Claude drafts all; Eleonora approves the set |
| CHOICE-E1-4 turn limit | (a) 4 |
| CHOICE-E1-5 top-level cache | (b) drop it; keep only the system/tools breakpoint |
| CHOICE-E1-6 effort | (a) `medium` for all three models |
| CHOICE-E1-7 repetitions | (b) 3 |
| CHOICE-E1-8 framing | (b) confirmatory |
| CHOICE-E1-9 `lookup_claim` | (a) keep all 10 tools |
| CHOICE-E1-10 seed | (a) `20261104` |
| CHOICE-E1-11 scoring | (a) the pilot rule |
| CHOICE-E1-12 baseline | (b) a no-tools run on one model, up to $4 |
| CHOICE-E1-16 baseline model (e1-base) | **Opus** (a model choice, not a spend OK) |
| CHOICE-E1-13 holdout | (b) hold back 20 questions, unseen until the first E3 rerun |
| CHOICE-E1-14 cost cap | (a) $31. A ceiling only: the full run needs her separate spend OK |
| CHOICE-E1-15 unit (e1-unit) | **(ii)** every repetition counted, clustered by question |
| CHOICE-E1-15 T (e1-T) | **70%** |
| CHOICE-E1-15 H3 (e1-h3) | **(b)** raise the unanswerable questions to about 25 of 100; R not given |
| Question set (rv-e1-set) | approved as is (`questions.yaml` at `3faa99b`), after choosing h3 (b); how the two fit is card e1-set-h3 |

Recorded in PLAN.md "Decisions taken" (coordinator commit `11f0562`), relayed 2026-11-05.

## Still open (Eleonora's)
- **e1-set-h3** (docket round 18): how h3 (b) changes the approved set. (replace) swap about 10 answerable questions for unanswerable ones, keeping 100; (add) add about 10 unanswerable questions, making about 110; (keep) keep the set as approved, with 15. Under replace or add she reviews only the changed questions. The holdout is then redrawn with the same seed and the same per-family rule (3 unanswerable held back as now, or 5 if she prefers; not yet asked).
- **e1-R2** (docket round 18): R = 70%, 80% or 90%.
- **CHOICE-E1-17, how the clustering enters the tests** (unit (ii) is chosen; the method is not). Both are implemented in `analyze_e1.py`, written before any result:
  - (a) **design effect**: Wilson interval with n replaced by n / DEFF, where DEFF = 1 + (m − 1) × ICC (one-way ANOVA ICC, floored at 0; m = 3 repetitions). H2 uses the clustered McNemar test of Durkalski et al. (2003). Closed form, but it relies on the ICC estimate.
  - (b) **question bootstrap**: resample questions with replacement (10,000 draws, seed 20261104). Percentile 95% intervals for the rates; H2 from the bootstrap distribution of the paired difference. Fewer assumptions, but less exact with few clusters (12–20 refusal questions).
  - No recommendation from Claude.
- **What the threshold demands under unit (ii)** depends on the ICC, which is unknown until the run. The two bounds are no clustering (ICC 0, every answer independent) and full clustering (ICC 1, a question's 3 answers always agree). The Wilson lower bound must reach the threshold:
  - **H1** (68 answerable questions, 204 answers), T = 70%: ICC 0 needs 76.3%; ICC 1 needs 80.9%.
  - **H3** at about **20 scored unanswerable questions** (60 answers, after h3 (b)):
    - R = 70%: ICC 0 needs 81.6%; ICC 1 needs 90.1%.
    - R = 80%: ICC 0 needs 90.2%; ICC 1 needs 97.6%.
    - R = 90%: ICC 0 needs 97.6%; ICC 1 cannot be supported.
  - **H3** at 12 (if she keeps the set):
    - R = 70%: ICC 0 needs 85.0%; ICC 1 needs 96.0%.
    - R = 80%: ICC 0 needs 93.1%; ICC 1 cannot be supported.
    - R = 90%: ICC 0 needs 99.9%; ICC 1 cannot be supported.
- **Holm and the intervals** (a detail in `analyze_e1.py`, for her to confirm with CHOICE-E1-17): the H1/H3 verdict comes from the 95% interval, and a "supported" also needs a Holm-adjusted one-sided p < 0.05 within its family. The alternative is Holm-adjusted (wider) intervals.

## What has already been seen (disclosed before any choice was made)
A **cost pilot** ran on 2026-11-04 (approved by Eleonora, cap $2.98; `evals/e1_sql_benchmark/pilot-2026-11-04/`, commit `a4998b7`). It used 10 easy questions (9 single-tool `public_share` lookups), 1 loop per model, effort `medium`, at most 4 turns. What was seen:
- cost per loop: Opus 5.5 $0.0403, Sonnet 5.5 $0.0102, Haiku 5.5 $0.0008;
- pilot accuracy: Opus 10/10, Sonnet 9/10 (the miss ran out of the 4-turn limit), Haiku 10/10.

The design is therefore not blind to the pilot (turn limit, difficulty mix, cap). The 10 pilot questions are not in the set (a test checks this). The write-up must say the pilot was seen.

## Question
On factual questions about who holds US household credit risk, answered only through the project's read-only household-credit MCP tools, how do Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 compare on accuracy, cost per question, cost per correct answer and latency? Do they refuse questions the data cannot answer?

## Hypotheses (confirmatory, CHOICE-E1-8 (b)) and what counts as support
- **H1** (per model, 3 tests): accuracy on scored answerable questions ≥ **T** (open).
- **H2** (2 paired tests): Opus and Sonnet differ in accuracy; Sonnet and Haiku differ in accuracy. Paired by question and repetition, clustered by question (unit (ii)); the test is set by CHOICE-E1-17.
- **H3** (per model, 3 tests): correct-refusal rate on scored unanswerable questions ≥ **R** (open).
- Support: the 95% lower bound (clustered per CHOICE-E1-17) ≥ threshold, with Holm-adjusted one-sided p < 0.05 (H1, H3); or Holm-adjusted clustered p < 0.05 (H2). Null: otherwise. Against (H1, H3): the upper bound is below the threshold. Script: `evals/e1_sql_benchmark/analyze_e1.py`, written and tested on synthetic data before any E1 result. Cost per correct answer and latency are descriptive.

## Data
- **Backend:** the MCP server's snapshot backend (`DATABASE_URL_READONLY` and `DATABASE_URL` unset); production is never queried.
- **Data files and hashes (recorded 2026-11-05; the run checks them).** Z.1 vintage 2026-09-11; NY Fed and FRED vintages 2026-10-27 (`meta.json`). SHA-256:
  - `collateral_coverage.json` `82afd5ab…d8ebb1`
  - `crisis_event_window.json` `05f58dfc…3dde`
  - `debt_by_risk_holder.json` `263ab492…ab15`
  - `dim_crisis.json` `6b169f26…fedd0`
  - `dim_risk_bucket.json` `1b3abc3c…510e`
  - `meta.json` `44d2d0f9…3b23`
  - `nyfed_by_type.json` `4cae3789…79a9`
  - `public_share.json` `c3dce2a4…5e67`
  - raw sources used for path 2: `FRB_Z1_csv.zip` `83b8eded…8c06`; `HHD_C_Report_2026Q2.xlsx` `ddfba16b…9237`

  Full hashes are in `validation/results.json` and at the freeze. If a Z.1 release lands before the run, the run still uses these files.
- **Question set:** `evals/e1_sql_benchmark/questions.yaml`, 100 new questions, drafted by Claude for Eleonora's approval.
  - Families (tool used), with L/C/M counts (one lookup / a computation / needs two tools):
    - public share: 15 (5/5/5)
    - holdings by bucket: 15 (5/5/5)
    - crisis windows: 15 (5/5/5)
    - collateral coverage: 15 (5/5/5)
    - NY Fed by type: 15 (5/5/5)
    - register and coverage tools: 10 (4/3/3)
  - **Unanswerable: 15.** Three holder × loan-type crosses, two forecasts, two borrower-level, two geographic, one sub-quarterly, three out of range, one not in the data, and one that is in the NY Fed workbook but not in any tool.
  - The set's SHA-256 at this draft: `bd70a40d…4aa6`.
- **Holdout:** 20 questions drawn by `verify_set.py` with `random.Random(20261104)`, stratified by family (3 per family, 2 for register/coverage, 3 unanswerable). They are q104, q111, q112, q121, q123, q130, q131, q134, q140, q146, q152, q156, q169, q170, q174, q177, q185, q186, q192, q193. E1 scores the other **80: 68 answerable and 12 unanswerable.**
- **Gold answers, verified with no model (CHOICE-E1-2 (b)).**
  - **Path 1** evaluates each question's check on the snapshot the MCP server serves (`spec.py`).
  - **Path 2** is a validation-PASS register row. For 82 questions, `validation/e1_gold.py` (checks `E1-<id>`) rebuilds the tables from the raw Fed Z.1 zip and the raw NY Fed workbook. It does not import the pipeline and parses the workbook by sheet title. The rebuilt value must agree with the snapshot to a tenth of the scoring tolerance. The 3 remaining questions reuse existing PASS rows (A1, A2, C4).
  - `build_register.py` writes the 82 rows to `claims/tracks/infra.csv`. `verify_set.py` then checks snapshot against register to the register's precision: **100/100**, with all 82 E1 checks PASS and the rest of the validation suite unchanged (123 PASS, 0 FAIL).
  - What the two paths share: the question's check spec and its evaluator (sums, differences, argmax), and the crisis start dates (a project definition). Imputed pre-2006 student-loan rows are not rebuilt, so no question uses them.
  - Unanswerable questions have gold "refuse".

## Method (fixed settings)
- **Models:** `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`. The served `response.model` is logged on every call.
- **Harness:** `evals/e1_sql_benchmark/run_e1.py` (built 2026-11-05, tested offline only), on `pilot.py`'s loop. With `--live` it refuses unless this file is frozen and the snapshot, `questions.yaml` and `gold.json` match `snapshot_hashes.json`. It has a manual tool-use loop, `tool_choice` auto and adaptive thinking (always on for these models). Server-side refusal fallbacks are off. A `stop_reason` of `refusal` counts as a refusal.
- **System prompt and answer format:** as in the pilot (`ANSWER:` and `QUARTER:` lines), frozen with this file and fingerprinted by `evals/regression.py`.
- **Tools:** all 10 household-credit MCP tools, as of the freeze (CHOICE-E1-9 (a)).
- **Effort:** `medium` for all three (CHOICE-E1-6 (a)).
- **Turn limit:** 4 (CHOICE-E1-4 (a)). A loop that ends at the limit without an `ANSWER:` line is scored wrong and also counted as "truncated".
- **Repetitions:** 3 per question per model (CHOICE-E1-7 (b)).
- **Order:** the 80 questions are shuffled with `random.Random(20261104)`. Within a question the three models run back to back, cheapest first, so a stop leaves comparable data.
- **Caching:** one `cache_control` breakpoint on the system prompt (prefix: tools plus system), with no top-level automatic cache (CHOICE-E1-5 (b)).
- **Logged per call:** the four `usage` token kinds, cost at the live prices on the run date, latency, `stop_reason`, text and tool calls. Never the key or any request header.

## Scoring (CHOICE-E1-11 (a), the pilot rule)
- An answer is correct if the number on the `ANSWER:` line, read in the unit the model states and converted to the question's unit, is within the question's tolerance of gold, and the `QUARTER:` matches where one is asked.
- Tolerances are in the question file: share 0.0005 · pp 0.05 (0.01 for NY Fed rate changes) · $tn 0.01 · $bn 1 · NY Fed rates 0.01 · growth % 0.1 · ratios 0.01 · counts exact.
- A refusal, or no number, is wrong on an answerable question.
- On an unanswerable question an answer is correct only if it gives no number and says the data cannot answer.
- The scorer is `score()` in `pilot.py`, now extended to $bn, %, ratio and count and tested. "Says the data cannot answer" is detected by a fixed phrase list (`REFUSAL_RE`: cannot, unable, not available, not covered, outside, no data, and similar). The human 20% re-score checks it. A human re-scores a seeded random 20% of answers (`random.Random(20261104)`).

## Benchmarks and holdout
- **Baseline (CHOICE-E1-12 (b), CHOICE-E1-16 Opus):** a no-tools run on Opus 5.5 (answers from memory) over the 80 scored questions × 3 repetitions, about $2–4, inside the $31 cap (`run_e1.py --baseline claude-opus-5-5`, its cap set to $31 minus the main run's spend). Reported descriptively next to Opus with tools; no hypothesis test.
- **Holdout (CHOICE-E1-13 (b)):** the 20 questions listed above. They are not run in E1; they are run first at the first E3 rerun.

## Multiple testing
8 tests (3 H1, 2 H2, 3 H3), Holm correction at α = 0.05 within each family (H1, H2, H3).

## Cost cap and stops (CHOICE-E1-14 (a): $31 ceiling; figures are estimates)
- **Estimate:** 80 questions × 3 repetitions = 240 loops per model, 720 in all. At the pilot's token profile: Opus $9.66 + Sonnet $2.44 + Haiku $0.20 = **$12.30**. The full set is harder (multi-tool), so the planning figure is 2×, about **$25**, plus the baseline (at most $4). Dropping the top-level cache probably lowers this; that is not measured.
- **Stops, checked after every call:**
  1. The running total reaches **$31**. A pre-call guard stops before any call could cross it.
  2. A model's mean cost per loop exceeds 3× its pilot mean: Opus $0.121, Sonnet $0.030, Haiku $0.0025.
  3. A checkpoint after the first 10% of loops: if the projected total exceeds $31, stop and report.

  On any stop, the triggering call is recorded and the partial results are reported as partial.

## Decision rules
- Each H is reported as supported, null or against, by the rules above. A model "is more accurate" only if its paired McNemar test survives Holm.
- Every published E1 number gets a register row pointing at the results file.

## What is and is not identified
- Identified: accuracy and cost **of this harness** (these tools, this prompt, 4 turns, effort `medium`) on **this question set** and data vintage.
- Not identified: general text-to-SQL ability (no SQL is written; the tools wrap fixed queries); performance on the live database backend, at other efforts or prompts, or on D6 reader questions.
- Question-writer effect: Claude wrote the questions (CHOICE-E1-3 (a)), so their style may favour Claude models.

## Deviations (dated, after freezing)
None (not frozen).
