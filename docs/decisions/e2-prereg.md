> **Claude draft.** Drafted by Claude; Eleonora's choices are recorded in the Decisions table. Not frozen: E2 must not be run until every choice is made and the frozen commit exists (`preregister` skill).

# Pre-registration: E2, planted-error test for the reviewer subagents
Status: **draft, partly decided** (2026-11-04). Not frozen. No E2 result exists.

## Decisions (Eleonora, 2026-11-04, decision card about 16:35–16:41 UTC; PLAN.md "Decisions taken", `543d96a`: "accept all the recommendations for CHOICE-1 to CHOICE-9")
| Choice | Decided |
|---|---|
| CHOICE-3 size | (a) 12 planted documents × 3 errors + 4 controls (36 errors) |
| CHOICE-5 isolation | (b) separate worktree holding only the variants plus the data |
| CHOICE-6 told about plants | no |
| CHOICE-7 scoring | (b) `score.py` location match, human "same fix" judgement, a second human re-scores a random 20% |
| CHOICE-8 intervals | both; cluster bootstrap over documents (2,000 resamples) is primary |
| CHOICE-9 baseline reviewer | yes, on data documents only |
| **CHOICE-1 recall threshold** | **open**: the draft gave no recommended value. Proposed 70% (tracks/infra.md E2-2) |
| **CHOICE-2 false-alarm ceiling** | **open**: no recommended value. Proposed 25% |
| **CHOICE-4 seed** | **open**: the draft listed two options with no recommendation. Proposed: the fixed integer `20261104`, written here before freezing (the commit-hash option cannot be known before the commit that contains it) |
| **CHOICE-10 category balance** | **open**: outside "CHOICE-1 to 9". Recommended (b), stratified |

The file is frozen (`prereg: E2 (frozen)`) once the four open choices have values. Until then `plant.py` refuses to run.

## Question
How often do the project's reviewer subagents, `skeptic` (data: revisions, definitions, double counting, holder-vs-risk, causal words, arithmetic) and `quant-reviewer` (method: leakage, look-ahead, overfitting, multiple testing, standard errors, benchmarks), catch errors deliberately planted in copies of real project write-ups? Which kinds do they miss, and how often do they raise objections where nothing was planted?

## Hypotheses and what counts as support, null or against
- **H1 (skeptic recall):** `skeptic` catches at least **CHOICE-1** of planted data errors.
  - Support: the lower bound of the 95% interval is at or above the threshold.
  - Against: the upper bound is below it.
  - Otherwise inconclusive.
- **H2 (quant-reviewer recall):** the same test for `quant-reviewer` on planted method errors.
- **H3 (division of labour):** each agent catches more errors of its own kind than of the other's. Reported descriptively (no test), by category.
- **H4 (false alarms):** on unplanted control documents, the share of objections rated blocker or major that are not real problems is at most **CHOICE-2**. A "real problem" is something the scorer confirms is wrong in the original document; such finds are logged as genuine findings, not false alarms.

## Material
- **Documents:** copies of committed write-ups taken at one fixed commit (recorded in the results):
  - data documents: `research/a1_gfc_decomposition/README.md`, `research/a2_net_exposure/README.md`, `analysis/findings.md` and one memo from `.claude/skills/research-memo/examples/`;
  - method documents: `research/c1_nowcast/README.md` and the forecasting and event-study write-ups available at the frozen commit.
- **Error catalogue** (`evals/e2_planted_errors/catalogue.yaml`, fixed with the freeze). Each entry is a category, a transformation and an example:
  - Data (`skeptic`): wrong vintage label; Z.1 figure called NY Fed (or the reverse); "holds" changed to "bears the losses"; a figure double-counted (Fed MBS added to agency pools); a wrong number (a digit changed, beyond rounding); a definition shift (the public share quoted without state and local); an unidentified causal word ("drove", "caused"); a period mismatch (quarter changed).
  - Method (`quant-reviewer`): a full-sample statistic used in an "out-of-sample" claim; a benchmark removed; a p-value from many tests reported as if it were one; HAC dropped or the wrong standard error stated; a holdout used for tuning; a confidence interval presented as a prediction interval.
- **CHOICE-3, the number of documents and errors:**
  - (a) 12 planted documents × 3 errors each + 4 controls: 36 errors, an interval about ±15 pp;
  - (b) 24 × 3 + 8 controls: 72 errors, about ±11 pp;
  - (c) 40 × 2 + 10 controls: 80 errors, the narrowest interval, the most reviewer runs.

  Cost: each reviewer run is one subagent call in a Claude Code session; no API key. (a) is about 40 runs per agent. Recommendation: (a) for a first run; E3 reruns it.

- **CHOICE-10, category balance.** A rehearsal on six write-ups (2026-11-04, nothing reviewed) planted all 36 errors, but random placement left `period_shift` at 0 and `number_change` at 1. Options:
  - (a) random placement, as rehearsed;
  - (b) stratified: each category planted a fixed number of times, with documents chosen among those where it fits;
  - (c) drop categories that rarely fit.

  Recommendation: (b), so every category has enough cases for the per-category table.

## Planting and the hidden key
- Tooling (built 2026-11-04, tested on synthetic documents only): `evals/e2_planted_errors/` (`catalogue.yaml`, `plant.py`, `score.py`). `plant.py` refuses to run until this file's Status line says frozen.
- `plant.py` takes the frozen seed (**CHOICE-4**: a fixed integer chosen before running, or the first 8 hex digits of the freeze commit).
  - For each planted document, it applies the given number of catalogue transformations at random eligible lines.
  - It writes the variants to `evals/e2_planted_errors/run-<id>/docs/` and the key (document, line, category, original text, planted text) to `run-<id>/key.json`.
- The key is hidden from the reviewers:
  - it is never in the reviewed folder;
  - reviewers are told which folder to review and that they may read nothing else under `evals/`;
  - its SHA-256 is printed and committed (`key.sha256`) **before** any reviewer runs, so the key cannot change afterwards.
- **CHOICE-5, how reviewers are isolated:**
  - (a) reviewers run in this repo, told to read only the variant folder and the committed data (they need the data to check numbers), and to write objections to `run-<id>/review-log.md`, not `claims/review-log.md`;
  - (b) a separate worktree containing only the variants plus the data, so the originals cannot be compared directly.

  Recommendation: (b). Under (a), a reviewer could `diff` against the original and score perfectly without reasoning. (b) still lets them recompute numbers from the data, which is what the real job requires.
- Reviewers get their standard prompt (the agent definition) plus one line naming the folder. They are not told that errors were planted. **CHOICE-6:** tell them or not.
  - Recommendation: not. Real reviews have no quota, and a known plant inflates objection counts.

## Scoring (fixed in advance)
- **Catch rule:** a planted error is caught if an objection
  - (i) points to its document and to a line within ±2 lines, or quotes its text; and
  - (ii) names a problem of the same category or one that would lead to the same fix.
- **CHOICE-7, who scores:**
  - (a) Eleonora alone, blind to the category until after scoring;
  - (b) `score.py` matches location automatically and a human judges (ii) only for location matches;
  - (c) automatic only (location plus category keywords).

  Recommendation: (b), with Eleonora (or a second human) re-scoring a random 20% to report agreement.
- **Recall:** caught / planted, by agent and by category, with Wilson 95% intervals. Documents are the clusters (errors in one document are not independent), so **CHOICE-8:**
  - (a) Wilson intervals on errors, with the cluster issue stated;
  - (b) a cluster bootstrap over documents (2,000 resamples, seed fixed).

  Recommendation: report both; (b) is primary.
- **False alarms:** blocker or major objections on control documents that the scorer confirms are not real problems, divided by objections on control documents. Wilson 95% interval.
- **Every miss is analysed:** for each uncaught error, a line in `run-<id>/misses.md`: category, document, why it was plausibly missed, and whether a prompt change would target it. Prompt changes are proposals for a later run (E3), never applied to this one.

## Benchmarks
- A baseline reviewer: the same model with no agent definition, only "review this document for errors", on the same variants. It shows whether the agent prompts add anything. **CHOICE-9:** include it (doubles the runs) or not.
  - Recommendation: include it for the data documents only.
- No holdout: nothing is tuned on these results. Prompt changes they suggest are tested on a fresh seed in E3.

## Multiple testing
H1 and H2 are the two confirmatory tests; no correction, and both are reported whatever the outcome. Everything by category and H3 is descriptive.

## Decision rules
- Write-up statement per hypothesis: "catches at least X of planted data errors" only if H1 is supported; "inconclusive" if the interval straddles the threshold; "misses more than 1 − X" if H1 is rejected. The same for H2.
- The results go in `evals/e2_planted_errors/results/` and are appended, never overwritten (PLAN E3).
- Claude does not change the agent prompts in response. It proposes changes in the write-up for Eleonora.

## What is and is not identified
- Identified: recall on these error kinds, in these documents, at this commit, with these models.
- Not identified: recall on natural (unplanted) errors, which may be subtler or more varied; performance on other projects; stability across model versions. That is E3's job: rerun when prompts or models change.

## Deviations (dated, after freezing)
None (not frozen).
