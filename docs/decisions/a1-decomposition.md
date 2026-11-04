# A1: how to decompose the 2007–11 jump

**Date:** 2026-11-04. **Decided by:** Claude (main model); for Eleonora's review with A1.

**Decision.** Split the change in the public share P = Pub / S between two quarters with the exact identity

    P1 − P0 = (1 − P0) · ΔPub / S1  −  P0 · ΔPriv / S1

summed over holder × loan-type cells. Also report each public holder's own share change, Δ(Pub_i / S), which sums exactly over public holders.

**Why.**
- Both are exact: no interaction term and no residual, so "sums exactly to +13.1 pp" (the PLAN criterion) holds by construction and is asserted in code.
- The first view separates public growth from private retreat, which is the question in findings.md item 4. The second matches the bucket split already published (`analysis/results.json` `gfc_window_split_pp`), so nothing previously published changes.
- Every private cell has the same weight (−P0), so accounting moves between private holders (FAS 166/167 card ABS onto banks) cancel in the private total.
- Fannie Mae and Freddie Mac are each shown as portfolio plus pools, because FAS 166/167 moved their pool MBS between Z.1 sectors 41 and 40 in 2010Q1.

**Rejected.**
- Shapley or log-mean Divisia splits: also exact, but harder to explain, with no gain for a two-period accounting.
- A "private debt held fixed" counterfactual as the main split: it answers a different question (what if private holders had not shrunk) and leaves an interaction term. It stays in findings.md as published.

**Not decided here.** Whether any component was caused by its policy event; that is A7.
