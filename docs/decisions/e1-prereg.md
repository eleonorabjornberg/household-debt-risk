> **Claude draft, not frozen.** Drafted by Claude (`preregister` skill) for Eleonora. The design choices are hers; all of them are now recorded below (2026-11-05). **Still open: her review of the 10 changed questions (rv-e1-redraft).** The file is frozen only after that. Nothing here may be run against the API until it is frozen and she has separately approved the spend.

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
| CHOICE-E1-15 H3 (e1-h3) | **(b)** raise the unanswerable questions to about 25 of 100 |
| e1-set-h3 | **replace** about 10 answerable questions with unanswerable ones, keeping 100; she reviews only the changed questions |
| CHOICE-E1-15 R (e1-R2) | **70%** |
| e1-holdback | hold back **about 5** unanswerable questions, in proportion |
| CHOICE-E1-17 clustering (e1-cluster) | **(b)** question bootstrap: 10,000 draws, seed 20261104, percentile 95% intervals; H2 from the paired-difference bootstrap |
| Support rule (e1-support) | **(i)** the 95% interval at or above the threshold AND a Holm-adjusted one-sided p < 0.05 |
| Question set (rv-e1-set) | approved as is (`questions.yaml` at `3faa99b`), after choosing h3 (b); then 10 questions replaced (e1-set-h3), which she reviews |

Recorded in PLAN.md "Decisions taken" (coordinator commits `11f0562`, `c55701b` and `ccc1fc6`; e1-cluster and e1-support chosen 14:25 UTC), relayed 2026-11-05.

## Still open (Eleonora's)
- **Review of the 10 changed questions** (rv-e1-redraft). The list is under Data. Until she approves, the 10 retired questions and their register rows stay.
- **What the thresholds demand** (context, not a choice) under unit (ii), for the scored set of 60 answerable and 20 unanswerable questions (3 answers each). This depends on the ICC, which is unknown until the run. The two bounds are no clustering (ICC 0, every answer independent) and full clustering (ICC 1, a question's 3 answers always agree). The Wilson lower bound must reach the threshold:
  - **H1**, T = 70%: needs 76.7% (ICC 0) to 81.6% (ICC 1).
  - **H3**, R = 70%: needs 81.6% (ICC 0) to 90.1% (ICC 1).

## What has already been seen (disclosed before any choice was made)
A **cost pilot** ran on 2026-11-04 (approved by Eleonora, cap $2.98; `evals/e1_sql_benchmark/pilot-2026-11-04/`, commit `a4998b7`). It used 10 easy questions (9 single-tool `public_share` lookups), 1 loop per model, effort `medium`, at most 4 turns. What was seen:
- cost per loop: Opus 5.5 $0.0403, Sonnet 5.5 $0.0102, Haiku 5.5 $0.0008;
- pilot accuracy: Opus 10/10, Sonnet 9/10 (the miss ran out of the 4-turn limit), Haiku 10/10.

The design is therefore not blind to the pilot (turn limit, difficulty mix, cap). The 10 pilot questions are not in the set (a test checks this). The write-up must say the pilot was seen.

## Question
On factual questions about who holds US household credit risk, answered only through the project's read-only household-credit MCP tools, how do Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 compare on accuracy, cost per question, cost per correct answer and latency? Do they refuse questions the data cannot answer?

## Hypotheses (confirmatory, CHOICE-E1-8 (b)) and what counts as support
- **H1** (per model, 3 tests): accuracy on scored answerable questions ≥ **T = 70%**.
- **H2** (2 paired tests): Opus and Sonnet differ in accuracy; Sonnet and Haiku differ in accuracy. Paired by question and repetition, clustered by question (unit (ii)); tested by the paired-difference question bootstrap (e1-cluster (b)).
- **H3** (per model, 3 tests): correct-refusal rate on scored unanswerable questions ≥ **R = 70%**.
- **Method (e1-cluster (b), e1-support (i)).** All intervals and p-values come from a **question bootstrap**: resample the scored questions with replacement, carrying each question's 3 answers along (10,000 draws, `random.Random(20261104)`).
  - **H1 and H3:** percentile 95% interval for each model's rate. One-sided p = the share of draws at or below the threshold.
  - **H2:** the paired difference in accuracy (A − B, over the same questions and repetitions). Two-sided p = 2 × the smaller tail share at zero, capped at 1.
  - **Supported** (H1, H3): the lower bound ≥ threshold AND the Holm-adjusted one-sided p < 0.05 within its family. **Against:** the upper bound < threshold. **Null:** otherwise.
  - **H2 supported** (the models differ): Holm-adjusted p < 0.05.
  - Script: `evals/e1_sql_benchmark/analyze_e1.py`, written and tested on synthetic data before any E1 result, run with `--method bootstrap`. Its design-effect method is not pre-registered and is not reported.
  - Cost per correct answer and latency are descriptive.

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
    - public share: 13 (4/4/5)
    - holdings by bucket: 13 (4/4/5)
    - crisis windows: 13 (4/4/5)
    - collateral coverage: 13 (4/4/5)
    - NY Fed by type: 13 (4/4/5)
    - register and coverage tools: 10 (4/3/3)
  - **Unanswerable: 25.**
    - q186–q200, the 15 in the set she approved: three holder × loan-type crosses, two forecasts, two borrower-level, two geographic, one sub-quarterly, three out of range, one not in the data, and one in the NY Fed workbook but in no tool.
    - **q201–q210, added 2026-11-05 under e1-set-h3 "replace"**: two holder × loan-type crosses, one forecast, two borrower-level (one by age), one geographic, one sub-quarterly, two out of range (one just before the series starts), and one in the workbook but in no tool.
  - **Changed questions (for her review).** Ten answerable questions were retired, one lookup and one computation from each tool family, so every family keeps its 5 two-tool questions. They stay in `questions.yaml` under `retired:` with their checks, so their verified register rows stay valid until the coordinator removes them.
    - q102 (PS lookup, mortgage public share 1990Q4) → q201
    - q110 (PS computation, mean public share 2020) → q202
    - q118 (HB lookup, state and local share 2026Q2) → q203
    - q125 (HB computation, banks / private-label ratio 2026Q2) → q204
    - q135 (CW lookup, vehicle coverage at COVID +4) → q205
    - q137 (CW computation, highest home coverage at a crisis t0) → q206
    - q147 (CC lookup, vehicle coverage 2026Q2) → q207
    - q153 (CC computation, change in vehicle coverage 2019Q4–2026Q2) → q208
    - q165 (NY lookup, auto transition rate 2019Q4) → q209
    - q168 (NY computation, credit card balance growth 2019Q4–2026Q2) → q210

    The other 90 questions are unchanged from the set she approved.
  - The set's SHA-256 at this draft: `c3d585bd…edc7` (was `bd70a40d…4aa6` when she approved it, before the replace).
- **Holdout:** 20 questions, drawn by `verify_set.py` with `random.Random(20261104)`. Each family gets 20% of its size, rounded by largest remainder, with ties broken by the seeded generator (e1-holdback: about 5 unanswerable, in proportion). That gives PS 2, HB 3, CW 3, CC 2, NY 3, RG 2, unanswerable 5. The held-out questions are q112, q115, q117, q124, q129, q131, q139, q140, q149, q158, q164, q170, q171, q177, q180, q189, q192, q195, q208, q210. E1 scores the other **80: 60 answerable and 20 unanswerable.**
- **Gold answers, verified with no model (CHOICE-E1-2 (b)).**
  - **Path 1** evaluates each question's check on the snapshot the MCP server serves (`spec.py`).
  - **Path 2** is a validation-PASS register row. For 72 questions in the set (plus the 10 retired ones), `validation/e1_gold.py` (checks `E1-<id>`) rebuilds the tables from the raw Fed Z.1 zip and the raw NY Fed workbook. It does not import the pipeline and parses the workbook by sheet title. The rebuilt value must agree with the snapshot to a tenth of the scoring tolerance. The 3 remaining questions reuse existing PASS rows (A1, A2, C4).
  - `build_register.py` writes the 82 rows to `claims/tracks/infra.csv`. `verify_set.py` then checks snapshot against register to the register's precision: **100/100**, with all 82 E1 checks PASS (including the retired ones) and the rest of the validation suite unchanged (123 PASS, 0 FAIL).
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
