# B4 method note: policy-regime scenarios

> **Claude draft, not the author's text.** The status of each debate is looked up from primary sources (`sources.md`, 2026-11-04). How each scenario maps onto the B3 engine is a design choice for Eleonora (Q-B4 in `tracks/markets.md`). Only the recession range, which follows directly from her Q-B3 decision, is computed.

PLAN task B4: "Policy-regime scenarios: GSEs released from conservatorship, student-loan reform, recession." Acceptance: "Each scenario's assumptions dated and sourced; results as ranges, not points."

## 1. Recession (computed)
- **Range.** From B3's DFAST 2026 proxy (the lower end) to its 2008–12 bank charge-off replay (the upper end). Both are applied to 2026Q2 balances, and both are labelled proxies.
- **Outputs.** Losses public and private, and the public share of losses. No CRT or mortgage-insurance transfer is applied (cap 0), because A2's bounds are not yet an input. That is a further assumption.

## 2. GSEs released from conservatorship (status: in conservatorship, FHFA page retrieved 2026-11-04)
- **What changes in the engine.** Who bears losses on the GSE and agency-pool mortgages, through the side of those exposures, not their balances.
- **CHOICE: which share of GSE-book losses becomes private on release.**
  - (a) A range from 0% (the implicit guarantee remains) to 100% (the GSEs fully private, with no backstop), with 25/50/75 points. *Recommended:* it is a range, as acceptance asks, and it needs no forecast of terms.
  - (b) Private up to the GSEs' capital, public beyond it. Needs their capital, from 10-Ks (Freddie reachable, Fannie blocked).
  - (c) Release terms from a specific proposal. None is found on FHFA's site; Treasury is unreachable.
- **Ginnie Mae (FHA, VA) pools stay public in every case.** They carry an explicit federal guarantee.

## 3. Student-loan reform (status: P.L. 119-21, approved July 4, 2025: no Grad PLUS for periods from July 1, 2026; new limits; Repayment Assistance Plan)
- **What changes in the engine.** The law changes new lending, not the existing stock. Over a horizon of a few years, part of graduate borrowing may move to private lenders.
- **CHOICE: how to represent it.**
  - (a) Stock unchanged: report that the reform does not move today's public share, plus a flow note. *Recommended,* because no sourced estimate of how much lending moves is available (ED unreachable).
  - (b) Move a range of the federal student-loan stock to private, as an illustrative sensitivity (for example 0–10%), labelled hypothetical.
  - (c) Use an estimate from CBO or ED of the volume shift. Needs a source; cbo.gov's data pages are untested and ED is blocked.

## Results
Only the recession range is computed (`results.json`, `b4.py`). Sections 2 and 3 wait for Q-B4.
