> **Claude draft.** Written by Claude (coordinator) for Eleonora to replace with her own text. Numbers are UNVERIFIED until the second-person rescore is done and she approves this note. Not published.

# E2 planted-error test, run 2026-11-13: results

Pre-registration: `docs/decisions/e2-prereg.md` (frozen at 5986353). Scores: `results/results.jsonl` (last line, `run-20261113`). Everything here is descriptive; no confirmatory test (CHOICE-12 (i)).

## R1, R2: recall
| Agent | Caught | Wilson 95% | Reference |
|---|---|---|---|
| `skeptic` (data) | 8 of 8 | 0.68–1.00 | 70% |
| `quant-reviewer` (method) | 6 of 6 | 0.61–1.00 | 70% |

The errors in one document are not independent. The cluster bootstrap over documents gives 1.00–1.00, which says nothing with 3–4 clusters and every error caught (labelled unreliable, as pre-registered).

## R3: by category
Each of the 14 categories was caught once, by the agent it was planted for. Table: `by_category` in the results line.

## R4: false alarms
0 of 7 blocker/major objections on the 2 control documents were false alarms (Wilson 95% 0.00–0.35), beside the 25% reference. All 7 were scored real problems in the original documents. Severity mapping: the quant-reviewer's high and medium count as blocker/major (Eleonora, e2-sevmap-55). The upper end of the interval is above 25%: 7 objections are too few to place the rate below the reference.

## Baseline (CHOICE-9)
The same model with no agent definition caught 8 of 8 data errors (Wilson 95% 0.68–1.00), the same as `skeptic`. On this run the `skeptic` prompt shows no measured advantage in recall. The baseline's 4 high/medium objections on the data control were not scored for R4 (the prereg defines R4 for the two agents only).

## Misses
None (`misses.md`).

## Not identified
A recall rate precise enough to compare with 70%; recall on natural errors; other models or prompt versions. Those are for E3 and a larger pre-registered run.

## Still open
- Second-person rescore of `doc-5bca86fe.md#0`, `#1` and `doc-4af129f3.md#1`; agreement to be reported here.
