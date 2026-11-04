> **Claude draft.** Drafted by Claude; Eleonora's choices are recorded in the Decisions table. Not frozen: E2 must not be run until the frozen commit exists (`preregister` skill). Every choice now has her value; the freeze is held for one question (below).

# Pre-registration: E2, planted-error test for the reviewer subagents
Status: **draft, freeze held: smaller design to choose (CHOICE-11, -12)** (2026-11-04). Not frozen. No E2 result exists.

## Decisions (Eleonora, 2026-11-04, decision cards about 16:35–16:41 UTC; PLAN.md "Decisions taken" on `claude/sweet-gates-avwrcs`, `543d96a`: "accept all the recommendations for CHOICE-1 to CHOICE-9"; values for CHOICE-1, -2, -4 and -10 relayed by the coordinator session the same day)
| Choice | Decided |
|---|---|
| CHOICE-3 size | (a) 12 planted documents × 3 errors + 4 controls (36 errors) |
| CHOICE-5 isolation | (b) separate worktree holding only the variants plus the data |
| CHOICE-6 told about plants | no |
| CHOICE-7 scoring | (b) `score.py` location match, human "same fix" judgement, a second human re-scores a random 20% |
| CHOICE-8 intervals | both; cluster bootstrap over documents (2,000 resamples) is primary |
| CHOICE-9 baseline reviewer | yes, on data documents only |
| CHOICE-1 recall threshold | **70%** (same for skeptic and quant-reviewer) |
| CHOICE-2 false-alarm ceiling | **25%** |
| CHOICE-4 seed | **the fixed integer `20261104`** |
| CHOICE-10 category balance | **(b) stratified**: each category planted a fixed number of times. With the document list below this is 3 per data category (8 × 3 = 24 skeptic errors) and 2 per method category (6 × 2 = 12 quant-reviewer errors): `plant.py --stratified` |

### Before freezing: the per-agent sample size (found by Claude, 2026-11-04, while freezing)
CHOICE-1 was recommended on the arithmetic "36 errors, about ±15 pp: 70% is supported only by 31/36 (86%) or more". But H1 and H2 are tested **per agent**, and the 36 errors of CHOICE-3 (a) split between the agents. With the documents listed below, 12 planted documents give 8 data and 4 method documents (a rehearsal with seed 20261104, nothing reviewed, confirms it):

| Test | Errors | Smallest result that supports 70% (Wilson lower bound ≥ 0.70) |
|---|---|---|
| H1 skeptic | 24 | **22/24 (92%)**: lower bound 0.742; 21/24 gives 0.690 |
| H2 quant-reviewer | 12 | **12/12 (100%)**; 11/12 gives 0.646 |

These are Wilson bounds; the primary interval (CHOICE-8) is the cluster bootstrap over documents, which is usually wider, so the bar is if anything higher. The rehearsal used `research/c2_forecast/SPECS.md` as the second method document; the method list should name exact files at the freeze. So H2 can be supported only by a perfect score, and H1 needs 92%, not the 86% the recommendation quoted. E2-3 answer (Eleonora, 2026-11-04, PLAN.md "Decisions taken"): none of (a)–(c); her note: "Let's do way fewer errors instead." Taken as direction, not a decision. Claude drafted the smaller designs below for her to choose from.

**CHOICE-11, a smaller design (replaces CHOICE-3 (a)).** Per reviewer agent. "70% point" is the fewest catches whose observed recall is at least 70%; intervals are Wilson 95% at that point. All three use seed 20261104 and need no API key (reviewer runs are subagent calls).

| Option | `skeptic` (data) | `quant-reviewer` (method) | Controls | Documents reviewed (+ baseline) | Can H1/H2 be *supported* at 70% under the current rule? | 70% point and its interval |
|---|---|---|---|---|---|---|
| (a) one of each category | 4 docs × 2 = **8 errors**, every data category once | 3 docs × 2 = **6 errors**, every method category once | 2 (1 data, 1 method) | 9 (+5 baseline) | **No.** Even 8/8 gives a lower bound of 0.676; 6/6 gives 0.610 | 6/8 (75%): 0.41–0.93 · 5/6 (83%): 0.44–0.97 |
| (b) twelve each | 6 docs × 2 = **12**: 4 categories twice, 4 once (picked by the seed) | 6 docs × 2 = **12**, every category twice | 2 | 14 (+7 baseline) | Only with **12/12** (0.757); 11/12 gives 0.646 | 9/12 (75%): 0.47–0.91 |
| (c) one error per document | 6 docs × 1 = **6**, 6 of 8 categories | 6 docs × 1 = **6**, every category once | 2 | 14 (+7 baseline) | **No.** 6/6 gives 0.610 | 5/6 (83%): 0.44–0.97 |

What each option buys:
- (a) is the fewest runs that still give one case of every category (a per-category hit/miss table, nothing more).
- (b) keeps a confirmatory test, but only a perfect score supports it.
- (c) has no within-document clustering, so the Wilson interval is honest without the bootstrap; it is no cheaper than (b) in runs.

With 3–6 documents per agent the cluster bootstrap (CHOICE-8 (b)) has too few clusters to be reliable; under any of these Claude would report Wilson as primary, with the clustering stated (a change to CHOICE-8 for her to confirm).

**CHOICE-12, the decision rule if (a) or (c) is chosen.** H1/H2 cannot be supported at 70% under either, so the rule has to change:
- (i) E2 becomes a **descriptive pilot**: recall with its interval and the per-category table, no "supported/against" statement. The confirmatory 70% test waits for a larger run (E3).
- (ii) a **screening rule**: "meets the bar" if the point estimate is at least 70% (6/8 or 5/6), always written with its interval and labelled as not a statistical test.
- (iii) lower the threshold to one the lower bound can reach (at most 67% for 8/8, 61% for 6/6).

Claude's suggestion, for her to accept or change: (a) with (i). It fits "way fewer errors", covers every category, and does not present a 6–8 error result as a test. Its cost is that the 70% question stays unanswered until a larger run. Tooling: each option needs a small `plant.py` change before the freeze. Today it allocates planted documents by cycling over the sources, not by a count per agent. (b) and (c) also need an "as equal as possible" stratified mode, because 12 and 6 do not divide by 8 data categories.

Once she answers, the file is frozen (`prereg: E2 (frozen)`); until then `plant.py` refuses to run.

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
- `plant.py` takes the frozen seed (**CHOICE-4**: `20261104`) and `--stratified` (**CHOICE-10**).
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
