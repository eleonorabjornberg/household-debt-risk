> **Claude draft.** Summary written by Claude for Eleonora to replace. The guardrails were approved by her as built; the labels below are model labels (P1 by Claude on 2026-11-06, P2 by Claude at her instruction on 2026-11-15), a disclosed deviation from the planned human review, and stay UNVERIFIED until she signs them off.

# E4: red-team of Ask Hot Potato

Ask Hot Potato is the question box on the site: Claude with read-only tools over the project's data, required to cite the query and vintage behind every number and to refuse what the data cannot answer.

## Design
- **Catalogue:** [`attacks.yaml`](attacks.yaml), attack families A1–A12: forecast smuggling, hypotheticals, holder vs guarantor, mixing NY Fed and Z.1 definitions, false premises, anchoring, injection and role play, pre-check bypass, units and scale, causal overreach, claim laundering (UNVERIFIED rows without their status), exfiltration and cost. Each attack states what a failure looks like.
- **Frozen before any paid call:** [`frozen.json`](frozen.json) holds the catalogue's SHA-256; the harness (`atlas/scripts/ask-redteam.ts`) refuses a changed catalogue.
- **Two passes:** P1 on the catalogue; guardrails added; P2 on the catalogue plus held-out paraphrases. The paraphrases were written at the same time and by the same author as the guardrails, so they are held out in time, not blind.
- **Scoring:** `atlas/scripts/redteam-score.ts` flags suspect answers automatically; flagged answers and a sample of unflagged ones were then labelled pass, fail, unclear or false positive.
- **Spend:** within the $20 D6 + E4 cap Eleonora approved on 2026-11-06.

## Results (UNVERIFIED)
| Pass | Calls | Flags | Labels |
|---|---|---|---|
| P1 | [`run-P1-2026-11-06/`](run-P1-2026-11-06/) | `flags.jsonl`, rescored in `run-P1-2026-11-06-rescore-v2/` | [`run-P1-2026-11-06-labels.json`](run-P1-2026-11-06-labels.json) |
| P2 | [`run-P2-2026-11-06/`](run-P2-2026-11-06/) | `flags.jsonl` | [`run-P2-2026-11-06-labels.json`](run-P2-2026-11-06-labels.json) |

In the P2 labels most scorer flags were false positives; one answer was labelled a fail (a computed private-share range that did not match the tool values), a few were unclear, and no secret or system-prompt text leaked. The counts are in the labels file; `PLAN.md` row E4 has the summary. Only part of the held-out paraphrases fall in the labelled set, so P2 says little about generalisation.

## Limits
- Claude wrote both the attacks and the guardrails.
- Labels are model labels, not human ones.
- Ask is not yet switched on in production; the passes tested the same code and prompts before that.
