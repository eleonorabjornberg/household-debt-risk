> **Claude draft.** Written by Claude (coordinator) for Eleonora to replace with her own text. No results yet: they wait on three same_fix judgments (round 45). Not published.

# E2 planted-error test, rerun 2026-11-13 (`run-20261113r`)

Pre-registration: `docs/decisions/e2-prereg.md`, with the 2026-11-13 rerun deviation (seed 20261114, isolation procedure). Rerun chosen by Eleonora (e2-rerun-56) after the Fable 5.2 judge found the isolation breach in `run-20261113`.

## Setup
- Seed 20261114, source commit 63c1f2e, 9 documents (7 planted with 2 errors each, 2 controls: doc-4a4226fd, doc-29e024ea). Key SHA-256 in `key.sha256`, checked before scoring.
- 14 subagent runs: 5 `skeptic`, 4 `quant-reviewer`, 5 baseline (data documents only, CHOICE-9). No API spend.
- Each run worked in its own folder holding only its variant and the data it may read.

## Isolation audit
Every tool call of all 14 runs was checked: none read a path outside its own folder. The `../..` paths in two runs (quant on doc-c386f705, baseline on doc-2c30f9c7) resolve inside their own folder. One channel remains: the allowed copy of `claims/register.csv` carries the original values and line locations, so a reviewer could notice a changed number by comparing with it. Reviewers did cite register rows.

## Assembly
The 14 reports were assembled into `review-log.md` (48 entries) and `baseline/review-log.md` (27 entries) by a script, with no change to wording. Two mechanical edits: "Severity:" was set in bold so the scorer reads it, and closing "what I checked" prose (not objections) was cut. The quant run on doc-ed560835 used the severity words "critical" and "moderate"; they are kept as written. That document is not a control, so the false-alarm count (R4) is unaffected. Baseline reports give no severity, so under the prereg rule no baseline control objection counts toward R4; its 5 control objections go to Eleonora as descriptive only.

## Match (before human judgment)
| | Located | Of |
|---|---|---|
| Reviewers | 14 | 14 |
| Baseline (data documents) | 8 | 8 |

"Located" means an objection points at the planted line. Whether it proposes the same fix is Eleonora's call (`same_fix`); recall is computed only after that.

## Judgments so far (Eleonora, review queue 44)
- `same_fix`: **yes** on 11 of 14 reviewer matches and 8 of 8 baseline matches. Three reviewer cards (doc-67be578b #0, #1; doc-7326b106 #0) had no saved answer and are re-asked in round 45.
- `real_problem`: **yes** on the 3 reviewer control objections that count for R4 (R-20261113r-1, -16, -17) and on all 5 baseline control objections (descriptive only: the baseline gives no severity, so none counts for R4).

## Second rater (Fable 5.2 model, per Eleonora's rescore-pack-57 note)
Blind to her scores: it saw `rescore-pack.md` and the four documents only. Its answers are in `second-rater.json`.
- Drawn errors (doc-ed3e7abc #0, #1; doc-7326b106 #1): located and same fix on all 3. Agreement with Eleonora: **3 of 3**.
- Reviewer control objections (R-1, -16, -17): real problem on all 3. Agreement: **3 of 3**.
- Baseline control objections (descriptive): real problem on B1 and B4, not on B2, B3, B5. Agreement: **2 of 5**.
- The second rater is a model, not a second human as the prereg says (Deviations, rescore-pack-57). It says its R-16, R-17, B1 and B3 answers rest partly on files outside the pack that it could not check.

## Still open
- Eleonora: `same_fix` for the three round-45 cards.
- Then `score.py summarise` on the reviewer folder (the baseline is read from `baseline/scoring.csv`, as in run-20261113). Results stay UNVERIFIED until she replaces this draft.
