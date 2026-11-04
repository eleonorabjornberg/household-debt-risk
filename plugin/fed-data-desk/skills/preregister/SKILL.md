---
name: preregister
description: Writes and commits a pre-registration (hypotheses, data and vintages, sample, tests, metrics, decision rules, what would count as a null) in docs/decisions/ BEFORE any result is computed, so later results can be checked against it. Use before structural-break tests (A4), event studies or synthetic control (A7), forecast evaluation (C2), benchmarks (E1) and planted-error tests (E2). Not for descriptive accounting such as decompositions (use a method note), and never after results exist.
---

# Pre-registration

Authorship (CLAUDE.md): research design is Eleonora's. Claude may draft the template and list the choices that must be made, with options and trade-offs, but the choices and the final text are hers. The file carries the "Claude draft" banner until she has written or approved each choice.

## Steps
1. **Check that no results exist yet** for this design (no outputs in the task folder, no numbers in the log). If any exist, stop: a pre-registration written after the fact is not one. Say so and propose a method note instead.
2. **Draft** `docs/decisions/<task>-prereg.md` from the template below, filling in facts (data, vintages, sample bounds available) and leaving each design choice as an explicit `CHOICE:` line with 2–3 options and their trade-offs.
3. **Hand to Eleonora** to make the choices. Record each decision with her name and the date in the file and in PLAN.md "Decisions taken".
4. **Freeze**: commit the final file alone, with message `prereg: <task> (frozen)`. Record the commit hash at the top of the file in a follow-up commit; analysis code reads the frozen file's hash into its results.
5. **Deviations** after freezing are allowed only as a dated "Deviations" section explaining why; the write-up must mention them. `quant-reviewer` checks results against this file.

## Template
```
# Pre-registration: <task id and title>
Status: draft | frozen at <commit> on <date> by Eleonora
## Question
## Hypotheses (H1..Hn) and what would count as support, as a null, as against
## Data: series IDs, sources, vintages (ALFRED for point-in-time), sample period, exclusions
## Method: tests or models; settings fixed in advance (windows, lags, trimming, max breaks, HAC bandwidth, donor pool, loss function)
## Benchmarks (naive, AR, placebo in time/space) and the holdout that stays untouched
## Multiple testing: how many tests, correction or descriptive framing
## Decision rules: what result leads to what statement in the write-up
## What is and is not identified
## Deviations (dated, after freezing)
```

## When NOT to use
- Accounting identities and decompositions (A1): write a method note in `docs/decisions/` instead.
- After any result has been seen.
