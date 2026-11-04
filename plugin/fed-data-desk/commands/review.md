---
description: Adversarial review of a write-up by the skeptic (data) and quant-reviewer (method) subagents
argument-hint: <file>
---
Run the `skeptic` subagent on $ARGUMENTS. If the file contains any test, interval, p-value, forecast or model evaluation, also run the `quant-reviewer` subagent on it. Each appends its objections to `claims/review-log.md`. Summarise the entry ids with severity. Do not resolve the objections yourself; resolutions are written by the main session or Eleonora.
