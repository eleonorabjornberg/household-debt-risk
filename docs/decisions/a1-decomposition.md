# A1: how to decompose the 2007–11 jump

**Date:** 2026-11-04. **Decided by:** Eleonora, 2026-11-04: Shapley. (First draft, same day: Claude chose the endpoint identity at the same time as the results were computed. The quant-reviewer objected, R-20261104-1 and -2 in `claims/review-log.md`, and Eleonora decided.)

**Decision.** Split the change in the public share P = Pub / (Pub + Priv) between two quarters with a Shapley split of the public and private totals:

    C_pub  = ½ [ (f(Pub1, Priv0) − f(Pub0, Priv0)) + (f(Pub1, Priv1) − f(Pub0, Priv1)) ],   f(a, b) = a / (a + b)
    C_priv = (P1 − P0) − C_pub

Within each side, each holder × loan-type cell gets the side's contribution in proportion to its change in holdings. Also report each public holder's own share change, Δ(Pub_i / S), which sums exactly over public holders.

**Why.**
- Exact: the parts sum to P1 − P0 with no residual (asserted in code).
- Symmetric: the split does not depend on whether public or private is counted first. The endpoint identity weights by the start share P0 and so favours the public term while P rises; under it the order of the two sides reverses (public 7.1, private 6.0 against Shapley 6.2 and 6.9).
- The quarter-by-quarter chained Shapley path agrees with the endpoint Shapley split to one decimal, so the headline does not depend on the path.
- Reclassifications between private holders (FAS 166/167 card ABS onto banks) do not change the private total, so they do not change the private side's contribution.
- The own-share view matches the bucket split already published (`analysis/results.json` `gfc_window_split_pp`).
- Fannie Mae and Freddie Mac are each shown as portfolio plus pools, because FAS 166/167 moved their pool MBS between Z.1 sectors 41 and 40 in 2010Q1.

**Kept as sensitivity** (`results.json` `sensitivity`): the endpoint-weighted identity P1 − P0 = (1 − P0)·ΔPub/S1 − P0·ΔPriv/S1, and the chained quarterly Shapley path.

**Rejected.**
- The endpoint identity as the main split: the side order depends on its weighting (R-20261104-1).
- A "private debt held fixed" counterfactual as the main split: it answers a different question and leaves an interaction term. It stays in findings.md as published.

**Not decided here.** Whether any component was caused by its policy event; that is A7.
