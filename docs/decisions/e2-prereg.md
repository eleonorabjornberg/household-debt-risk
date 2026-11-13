> **Claude draft, frozen.** Text drafted by Claude. Every design choice is Eleonora's, as recorded in the Decisions table with dates. Frozen 2026-11-04 (`preregister` skill). Changes after the freeze go only in "Deviations", dated.

# Pre-registration: E2, planted-error test for the reviewer subagents
Status: **frozen** on 2026-11-04, choices by Eleonora (PLAN.md "Decisions taken", coordinator commits `543d96a` and `b7f1158`). Freeze commit: `5986353`. No E2 result exists at the freeze.

## Frozen at
Commit `5986353` ("prereg: E2 (frozen)", 2026-11-04). SHA-256 of this file as frozen there: `1f474cfd0f115823122eb4098cf7eb451932b88b1db05b4170ca6d3480779646`. This section and the Status line's hash were added in the follow-up commit (a commit cannot contain its own hash); nothing else changed.

## Decisions (all by Eleonora, 2026-11-04, decision cards; PLAN.md "Decisions taken" on `claude/sweet-gates-avwrcs`)
| Choice | Decided | When |
|---|---|---|
| CHOICE-11 size (replaces CHOICE-3) | **(a) one of each category**: `skeptic` 4 planted data documents × 2 errors = 8 errors (every data category once); `quant-reviewer` 3 planted method documents × 2 errors = 6 errors (every method category once); 2 controls (1 data, 1 method). 9 documents, +5 baseline runs | round 5, `b7f1158` |
| CHOICE-12 decision rule | **(i) descriptive pilot**: recall with its interval and a per-category table, no supported/against verdict; the confirmatory 70% test waits for a larger run | round 5, `b7f1158` |
| CHOICE-8 intervals | **Wilson 95% intervals primary**, with the within-document clustering stated; the cluster bootstrap is reported as secondary (too few clusters to rely on) | round 5, `b7f1158` (changes the earlier "bootstrap primary") |
| CHOICE-1 recall threshold | 70%, the reference value for the descriptive report (CHOICE-12 (i): no verdict is drawn from it in this run) | 16:35–16:41 UTC, values relayed later the same day |
| CHOICE-2 false-alarm ceiling | 25%, reference value only (as CHOICE-1) | as above |
| CHOICE-4 seed | the fixed integer **`20261104`** | as above |
| CHOICE-10 category balance | (b) stratified: each category planted a fixed number of times; under CHOICE-11 (a), once each | as above |
| CHOICE-5 isolation | (b) separate worktree holding only the variants plus the data | `543d96a` |
| CHOICE-6 told about plants | no | `543d96a` |
| CHOICE-7 scoring | (b) `score.py` location match, human "same fix" judgement, a second human re-scores a random 20% | `543d96a` |
| CHOICE-9 baseline reviewer | yes, on data documents only | `543d96a` |

How the design got here: the first design (CHOICE-3 (a), 36 errors) was found before freezing to give only 24 `skeptic` and 12 `quant-reviewer` errors, so a 70% test would need 22/24 and 12/12 (question E2-3). Eleonora asked for "way fewer errors instead". With 8 and 6 errors no result can support 70% (8/8 has a Wilson lower bound of 0.676, 6/6 of 0.610), hence the descriptive rule.

## Question
How often do the project's reviewer subagents, `skeptic` (data: revisions, definitions, double counting, holder-vs-risk, causal words, arithmetic) and `quant-reviewer` (method: leakage, look-ahead, overfitting, multiple testing, standard errors, benchmarks), catch errors deliberately planted in copies of real project write-ups? Which kinds do they miss, and how often do they raise objections where nothing was planted?

## What is reported (descriptive pilot, CHOICE-12 (i))
No hypothesis is confirmed or rejected by this run. Reported:
- **R1 (`skeptic` recall):** caught / 8 planted data errors, with a Wilson 95% interval, set beside the 70% reference. Every statement is of the form "caught k of 8 (interval a–b)"; never "catches at least 70%".
- **R2 (`quant-reviewer` recall):** the same, out of 6 method errors.
- **R3 (division of labour):** which errors of each kind each agent caught, by category. Descriptive.
- **R4 (false alarms):** on the 2 control documents, blocker or major objections that the scorer confirms are not real problems, as a share of objections on controls, with a Wilson interval, beside the 25% reference. A "real problem" is something the scorer confirms is wrong in the original document; it is logged as a genuine finding, not a false alarm.
- **Per-category table:** for each of the 14 categories, caught or missed, by which agent (and the baseline, for data categories).

For reference, the 70% point and its Wilson interval: 6/8 (75%), 0.41–0.93; 5/6 (83%), 0.44–0.97.

## Material
- **Documents** (copies taken at the commit recorded in `key.json` as `source_commit`):
  - data (`skeptic`), 4 planted, one copy each: `research/a1_gfc_decomposition/README.md`, `research/a2_net_exposure/README.md`, `analysis/findings.md`, `.claude/skills/research-memo/examples/bank_treasury.md` *[implementation: "one memo" resolved to the first example memo alphabetically]*;
  - method (`quant-reviewer`), 3 planted, one copy each: `research/c1_nowcast/README.md`, `research/c1_nowcast/EVALUATION.md`, `research/c2_forecast/SPECS.md` *[implementation: "c1 README and the forecasting and event-study write-ups available at the frozen commit"; these are the forecasting write-ups that exist; no event-study write-up exists yet]*;
  - controls: 1 unplanted copy of a data document and 1 of a method document (the first in each list, by `plant.py`'s per-agent cycling).
- **Error catalogue** (`evals/e2_planted_errors/catalogue.yaml`, fixed with the freeze):
  - Data (`skeptic`), 8 categories: wrong vintage label; Z.1 figure called NY Fed (or the reverse); "holds" changed to "bears the losses"; a figure double-counted (Fed MBS added to agency pools); a wrong number (a digit changed, beyond rounding); a definition shift (the public share quoted without state and local); an unidentified causal word ("drove", "caused"); a period mismatch (quarter changed).
  - Method (`quant-reviewer`), 6 categories: a full-sample statistic used in an "out-of-sample" claim; a benchmark removed; a p-value from many tests reported as if it were one; HAC dropped or the wrong standard error stated; a holdout used for tuning; a confidence interval presented as a prediction interval.
- Cost: each reviewer run is one subagent call in a Claude Code session, with no API key. 9 agent runs plus 5 baseline runs.

## Planting and the hidden key
- Tooling: `evals/e2_planted_errors/` (`catalogue.yaml`, `plant.py`, `score.py`). `plant.py` refuses to run unless this file's Status line says frozen. The frozen command:

  ```
  uv run --project pipeline python evals/e2_planted_errors/plant.py \
      --data research/a1_gfc_decomposition/README.md research/a2_net_exposure/README.md \
             analysis/findings.md .claude/skills/research-memo/examples/bank_treasury.md \
      --method research/c1_nowcast/README.md research/c1_nowcast/EVALUATION.md research/c2_forecast/SPECS.md \
      --planted-data 4 --planted-method 3 --controls-data 1 --controls-method 1 \
      --errors-per-doc 2 --seed 20261104 --stratified --out evals/e2_planted_errors/run-<id>
  ```

  A rehearsal of this command before the freeze (scratchpad, nothing reviewed) gave 9 variants and 14 errors, every category exactly once.
- `--stratified` (CHOICE-10) assigns categories to documents by a seeded search, so that each category is planted the set number of times, no document gets one twice, and the errors fit their document together.
- Outputs: the variants in `run-<id>/docs/` and the key (document, line, category, original text, planted text) in `run-<id>/key.json`.
- The key is hidden from the reviewers:
  - it is never in a reviewed folder;
  - its SHA-256 (`key.sha256`) is committed **before** any reviewer runs, so the key cannot change afterwards.
- **Isolation (CHOICE-5 (b))**, *[implementation]*: **one reviewer run per document**. Each run's worktree holds only that one variant plus the committed data. The two controls are copies of documents that are also planted (a1 README, c1 README). Two variants of one source in the same folder would let a reviewer find the plants with `diff`, so variants are never reviewed together.
- Reviewers get their standard prompt (the agent definition) plus one line naming the document. They are not told that errors were planted (CHOICE-6).

## Scoring (fixed in advance)
- **Catch rule:** a planted error is caught if an objection
  - (i) points to its document and to a line within ±2 lines, or quotes its text; and
  - (ii) names a problem of the same category or one that would lead to the same fix.
- **Who scores (CHOICE-7 (b)):** `score.py` matches location automatically; a human judges (ii) only for location matches; Eleonora or a second human re-scores a random 20% and agreement is reported. *[implementation]* With 14 errors, 20% is 3 errors, drawn with `random.Random(20261104)` from the scored rows; `score.py` does not draw this sample yet, so it is drawn by hand with that seed and the draw is recorded in the run folder.
- **Recall:** caught / planted, by agent and by category. **Wilson 95% intervals are primary** (CHOICE-8), with the clustering stated: the errors in one document are not independent. The cluster bootstrap over documents (2,000 resamples, seed 20261104) is reported as secondary, labelled unreliable with 3–4 clusters.
- **False alarms:** as R4, with a Wilson 95% interval.
- **Every miss is analysed:** for each uncaught error, a line in `run-<id>/misses.md`: category, document, why it was plausibly missed, and whether a prompt change would target it. Prompt changes are proposals for a later run (E3), never applied to this one.

## Benchmarks
- Baseline reviewer (CHOICE-9): the same model with no agent definition, only "review this document for errors", on the same variants. Data documents only: 4 planted + 1 control = 5 runs. It shows whether the `skeptic` prompt adds anything.
- No holdout: nothing is tuned on these results. Prompt changes they suggest are tested on a fresh seed in E3.

## Multiple testing
None: no confirmatory test in this run (CHOICE-12 (i)). Everything is descriptive.

## Decision rules
- Write-up statements are counts with intervals ("caught k of n, Wilson 95% a–b"), set beside the 70% / 25% references. The words "supported", "rejected" and "at least 70%" are not used about this run.
- The confirmatory test of 70% recall needs a larger run with its own pre-registration (or a dated deviation here before any result), through E3.
- The results go in `evals/e2_planted_errors/results/` and are appended, never overwritten (PLAN E3).
- Claude does not change the agent prompts in response. It proposes changes in the write-up for Eleonora.

## What is and is not identified
- Identified: which of these 14 planted errors these agents caught, in these documents, at this commit, with these models, with the uncertainty of 8 and 6 cases.
- Not identified: a recall rate precise enough to compare with 70%; recall on natural (unplanted) errors, which may be subtler or more varied; performance on other projects; stability across model versions. That is E3's job: rerun when prompts or models change.

## Deviations (dated, after freezing)
- **2026-11-13, isolation not enforced (CHOICE-5 (b)).** The reviewer runs of run-20261113 ran in worktrees that held the whole repository, not only the variant plus data. Some reviewers used that: in `run-20261113/review-log.md` the skeptic diffs variants against the originals (both errors in doc-01bab658 and doc-4af129f3, 4 of 8 data catches), and quant-reviewer runs cite repository files and git history. Caught by the Fable 5.2 judge pass Eleonora asked for, after scoring; missed by Claude (coordinator), who set up the runs. The run's recall is therefore not a test of the prompts under the pre-registered conditions. Whether to rerun on a fresh seed in isolated worktrees is Eleonora's decision.
- **2026-11-13, severity mapping decided after results.** The quant-reviewer grades high/medium/low, not blocker/major. Eleonora's e2-sevmap-55 (high and medium count as blocker/major for R4) was chosen after the objections were visible. Under the unmapped rule (skeptic blocker/major only) R4 is 0 of 3. Both figures are reported.
- **2026-11-13, freeze commit after the history rewrite.** The freeze commit 5986353 cited above is `d65afd3` on the submitted branch (the 2026-11-09 rewrite changed SHAs). The frozen file's SHA-256 is unchanged.
- **2026-11-13, rerun on a fresh seed (Eleonora, e2-rerun-56).** Written before planting. run-20261113 stays as disclosed above; the rerun is `run-20261113r` with the frozen command and a fresh seed. Seed `20261113` planted only 13 of 14 errors (one did not fit the A2 README), so, before any reviewer ran, the rule "take the next integer that plants all 14" was applied: the seed is **`20261114`**. Seeds were tried only for whether the planting completes; no reviewer saw any of them. Isolation is enforced this time: each reviewer run gets its own folder outside the repository, holding only its one variant (as `document.md`) plus copies of the committed data (`validation/results.json`, `web/public/data/`, `analysis/tables/`, the non-Markdown files under `research/`, `pipeline/series_catalog.yaml`, `claims/register.csv`), no Markdown sources and no git history. Reviewers are told to read only inside that folder; afterwards the coordinator checks each run's transcript for any path outside it and reports what it finds. Reports come back as hand-back messages and are assembled into the run folder as before. The 20% rescore is drawn with `random.Random(20261104)` as before, and per Eleonora's e2-rescore-ctrl-56 the second person also rescores the control objections.
