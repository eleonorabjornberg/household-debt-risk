# B4 method note: policy-regime scenarios

> **Claude draft, not the author's text.** The status of each debate is looked up from primary sources (`sources.md`, 2026-11-04). How each scenario maps onto the B3 engine is a design choice for Eleonora (Q-B4 in `tracks/markets.md`). Only the recession range, which follows directly from her Q-B3 decision, is computed.

PLAN task B4: "Policy-regime scenarios: GSEs released from conservatorship, student-loan reform, recession." Acceptance: "Each scenario's assumptions dated and sourced; results as ranges, not points."

## 1. Recession (computed)
- **Range.** From B3's DFAST 2026 proxy (the lower end) to its 2008–12 bank charge-off replay (the upper end). Both are applied to 2026Q2 balances, and both are labelled proxies.
- **Outputs.** Losses public and private, and the public share of losses. No CRT or mortgage-insurance transfer is applied (cap 0), because A2's bounds are not yet an input. That is a further assumption.

## 2. GSEs released from conservatorship (computed; status: in conservatorship, FHFA page retrieved 2026-11-04)
- **What changes in the engine.** Who bears losses on the GSE and agency-pool mortgages, through the side of those exposures, not their balances.
- **Decided (Eleonora, card b4-gse, option (a), 2026-11-04):** a range of 0% (the implicit guarantee holds) to 100% (fully private, no backstop) of the losses on Fannie Mae's and Freddie Mac's books, with points at 25, 50 and 75%. Options (b) (private up to capital) and (c) (a specific proposal's terms) were not chosen.
- **Implementation (`b4.py`).** B3's "GSEs & agency pools" mortgage exposure is split with the finer Z.1 series of the same release (2026-09-11), household-apportioned as B3: Fannie (FL403065110 + FL413065143) and Freddie (FL403065120 + FL413065123) are the released book; Ginnie and FmHA pools (FL413065110 + FL413065133) and the FHLBs and other GSEs (the GSE sector total FL403065105 less Fannie and Freddie) stay public. The released book is split into a public and a private exposure in proportion to the share; the engine is rerun under each B3 preset. Total losses are unchanged by construction (checked).
- **Ginnie Mae (FHA, VA) pools stay public in every case.** They carry an explicit federal guarantee.

## 3. Student-loan reform (status: P.L. 119-21, approved July 4, 2025: no Grad PLUS for periods from July 1, 2026; new limits; Repayment Assistance Plan)
- **What changes in the engine.** The law changes new lending, not the existing stock. Over a horizon of a few years, part of graduate borrowing may move to private lenders.
- **CHOICE: how to represent it.**
  - (a) Stock unchanged: report that the reform does not move today's public share, plus a flow note. *Recommended,* because no sourced estimate of how much lending moves is available (ED unreachable).
  - (b) Move a range of the federal student-loan stock to private, as an illustrative sensitivity (for example 0–10%), labelled hypothetical.
  - (c) Use an estimate from CBO or ED of the volume shift. Needs a source; cbo.gov's data pages are untested and ED is blocked.

## Results
The recession range and the GSE-release range are computed (`results.json`, `b4.py`; README by `make_readme_and_rows.py`). Section 3 waits for a sourced estimate (card b4-student (c)).
