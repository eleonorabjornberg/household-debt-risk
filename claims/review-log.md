# Review log

Objections raised by the review subagents (`.claude/agents/skeptic.md`, `quant-reviewer.md`, `editor.md`) and by people, with their resolutions. Append only: entries are never deleted or rewritten; a resolution is added under the entry.

Entry format:

```
### R-<YYYYMMDD>-<n> · <reviewer> · <target file or claim_id>
- **Objection:**
- **Severity:** blocker / major / minor
- **Evidence:**
- **Proposed resolution:**
- **Status:** open | resolved (<date>, by <who>): <what was done> | rejected (<date>, by <who>): <why>
```

Resolutions are written by the main session or Eleonora, never by the reviewer that raised the objection.

---

### R-20261104-1 · quant-reviewer · research/a1_gfc_decomposition/README.md (growth vs retreat split)
- **Objection:** The headline "public growth 7.1 pp, private retreat 6.0 pp" depends on the chosen weighting and the ordering reverses under the alternatives. The endpoint identity weights by the start share P0 (36.1%), which favours the public term while P rises. Chaining the same identity by quarter (the script's own path.csv) gives public 6.27 pp, private 6.83 pp; a Shapley split of the two counterfactuals gives public 6.25, private 6.87. The README says the split "is exact" but does not mention that it depends on the path. The docstring says "chained and endpoint totals both equal P1 - P0", which holds only for the grand total, not for groups. The results.json groups and the 2011Q4 row of path.csv disagree with no note: Ginnie 3.81 vs 3.29, PLS/mREITs 4.93 vs 5.71, student loans 1.94 vs 1.62. The decision doc rejected Shapley for "no gain", but here it changes the headline.
- **Severity:** major
- **Evidence:** Reran in the scratchpad by importing decompose.py; no repo files were written. Endpoint public/private 7.127/5.979; chained 6.274/6.832; the Shapley public term is 6.245. path.csv 2011Q4 row: ginnie_pools 3.2879, private_label_and_mreits 5.7088.
- **Proposed resolution:** Report endpoint, chained and Shapley side by side, or call the split "roughly even (6.0-6.9 pp private, by method)". State that group totals depend on the path, and fix the docstring.
- **Status:** open

### R-20261104-2 · quant-reviewer · docs/decisions/a1-decomposition.md
- **Objection:** The design was not set before the results. The decision doc was added in the same commit as decompose.py, results.json and the CSVs (f8b7ddc, 2026-11-04T00:30:57Z). It quotes the result (+13.1 pp) and is "Decided by: Claude", so it is not Eleonora's design (the authorship rule). The README cites it as "Method decision" and declares neither point.
- **Severity:** major
- **Evidence:** `git log --name-status -- docs/decisions research/a1_gfc_decomposition`.
- **Proposed resolution:** Say in the README that the method was chosen at the same time as the results, by Claude, and is awaiting Eleonora's decision. Record her choice in PLAN.md "Decisions taken".
- **Status:** open

### R-20261104-3 · quant-reviewer · research/a1_gfc_decomposition/README.md (counterfactual comparison)
- **Objection:** The comparison with findings.md item 4 is not like for like. The 6.1 pp counterfactual (private held at 2007Q4) measures the public-growth side; it reproduces at 6.11. Under it, private retreat is the remaining 6.99 pp, not 6.0. The README puts 6.1 right after the 6.0 private figure, which invites reading the two as the same quantity. "Both say about half" holds only loosely (46% vs 53%).
- **Severity:** minor
- **Evidence:** pub_t1/(pub_t1+priv_t0) - P0 = 6.115 pp; residual 6.991 pp.
- **Proposed resolution:** State that 6.1 pp is the counterpart of the 7.1 pp public term, and give the counterfactual's private piece (7.0 pp).
- **Status:** open

### R-20261104-4 · quant-reviewer · research/a1_gfc_decomposition/README.md (causal wording)
- **Objection:** An accounting split cannot carry causal or counterfactual statements, but the README makes some. "Conservatorship ... didn't change how much they held" and "doesn't fit these data" need a counterfactual (the GSEs' holdings without conservatorship), which this method cannot supply and the README itself defers to A7. "Their share rose mostly because private holders shrank around them" is the own-share view (3.9 pp vs 1.4 pp growth term) restated as a cause. The README's limit "accounting, not a causal estimate" is contradicted in "What this changes".
- **Severity:** major
- **Evidence:** README "What this changes", bullets 2-3.
- **Proposed resolution:** Rephrase descriptively. For example: "GSE balances rose $278B; most of their own-share gain is arithmetic from a shrinking denominator; whether conservatorship changed holdings is A7."
- **Status:** open

### R-20261104-5 · quant-reviewer · research/a1_gfc_decomposition/test_decompose.py, decompose.py
- **Objection:** The tests would not catch a missing holder. They exercise contrib() only, on synthetic data, and do catch a flipped sign through the exact-sum check. cells(), the PUBLIC_* lists, the group partition and the own-share view are untested. The README says the script "asserts ... that the cells reproduce the scope total", but scope_gap is only recorded, not asserted. A dropped public holder would move the share with no error. The gap is in fact about 0, at most 4e-9 $M across the window.
- **Severity:** minor
- **Evidence:** decompose.py main(): `scope_gap = ...` with no assert; tests cover contrib() only. Both tests pass.
- **Proposed resolution:** Assert scope_gap < tolerance at every quarter in [t0, t1]. Add a test that the groups partition the cell columns, and one that removing a cell trips the scope check.
- **Status:** open
