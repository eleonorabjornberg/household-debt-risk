> **Claude draft.** Written by Claude (coordinator) for Eleonora to replace with her own text. No results yet: they wait on her same_fix and real_problem judgments and the second-person rescore. Not published.

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

## Still open
- Eleonora: `same_fix` for 14 reviewer and 8 baseline matches; `real_problem` for 3 reviewer control objections (R-20261113r-1, -16, -17) and, descriptively, 5 baseline ones.
- Second person: rescore of `rescore-sample.json` (doc-ed3e7abc #0, #1; doc-7326b106 #1) and the reviewer control objections (e2-rescore-ctrl-56).
- Then `score.py summarise` on both folders.
