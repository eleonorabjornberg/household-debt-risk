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

- **Decided (Eleonora, card b4-student, option (c), 2026-11-04):** use a CBO or ED estimate of the shift in lending, from a reachable, free source; if none is found, it goes back to her.
- **Search result (2026-11-04, `sources.md`).** ED's final rule (91 FR 23768, RIA Table 3.1) estimates the **reduction in federal** non-consolidated disbursements over 2026–2035. Neither it nor the NPRM estimates how much of that lending **moves to private lenders**; ED says only that "there may be a transition". CBO is not reachable (403 from the site). So the estimate that option (c) asks for, the shift to private lending, was not found. The item went back to Eleonora.
- **Decided (Eleonora, card b4-student-2, option (iii), 2026-11-05):** wait for a reachable CBO estimate; the student-loan scenario stays out of B4 until then. **Nothing is built.**

### 3b. Student-loan reform: CBO budget-side proxy (Eleonora, card cbo-repo-55 (b), 2026-11-11; written after a first look at the account's rows, before any total was computed)

> **Claude draft.** Implements her option text: add github.com/US-CBO/cbo-data as a source "for budget-side context only" and "use the Direct Loan account outlays as a labelled proxy in B4's student-loan scenario". This reopens 3 above.

- **Source.** CBO's account-level baseline spending projections ("Spending Projections by Budget Account", CBO publication 51142), as files in the CBO repository at commit 284a956: `data/budget/spending_detail/annual_fy_{2024-06,2025-01,2026-02}.csv`, outlays in $ millions by fiscal year (`sources.md`). Fetched with `git clone`; api.github.com is not used (it answers 403).
- **Account.** "Federal Direct Student Loan Program Account", TIN 091-0243-0-1-502, Mandatory.
- **What its outlays are.** Under the Federal Credit Reform Act (2 U.S.C. 661a, `sources.md`), a credit program account is "the budget account into which an appropriation to cover the cost of a direct loan ... program is made", and "cost" is the "estimated long-term cost to the Government ... calculated on a net present value basis". Reestimates are shown in a subaccount of the program account, and administrative funding within the same account (2 U.S.C. 661c(f), (g)). So these outlays are what the account pays out for the loans' cost, **not the amount lent** and not a loss. Loan disbursements run through the non-budget financing account, which is not in CBO's file. Where a negative subsidy is recorded is not established by the sources fetched, so the outlays are not called a complete net subsidy cost (skeptic mkt-s60).
- **The proxy.** The change in the projected outlays of that account between the January 2025 and February 2026 baselines (the repository's file labels; P.L. 119-21 was approved between them, on July 4, 2025), summed over the fiscal years both cover (FY2026–FY2035), with each baseline's year-by-year path beside it. The June 2024 baseline is extracted for context only and not shown in the README; its FY2024 value is far above every later year, which the repository does not explain (skeptic mkt-s64).
- **Timing (skeptic mkt-s61).** Most of the fall is already in FY2026, but the end of Grad PLUS applies to periods from July 1, 2026, so the README says the drop cannot be read as that provision's effect.
- **Labelled a proxy, and what it is not.** It is not a CBO estimate of the law's effect: a change between baselines also carries every economic and technical revision CBO made in between. It is not an estimate of lending moving to private lenders, which the CBO repository does not contain. It does not enter the B3 loss engine, and it changes no public share in this task.
- **Open choice for Eleonora (proposed card).** Whether and how this proxy should feed the engine. Options: (a) budget-side context only, as built here; (b) pair it with ED's estimate of the reduction in federal disbursements (91 FR 23768, already in `sources.md`) as the volume side; (c) a hypothetical shift of part of the federal stock, labelled as such.

### 3c. Volume side: ED's estimate of federal disbursements (Eleonora, docket 56 b4-student-proxy-map (b), 2026-11-11)

> **Claude draft.** Her option text: "Pair it with ED's disbursement estimate: Add the Education Department's loan-volume estimate in its rule (91 FR 23768) as the volume side, after a source check. Still no loss-engine change until you review it."

- **Source check (2026-11-11, `sources.md`).** Free, reachable on www.govinfo.gov, the official Federal Register text (PDF, hashed). It holds a volume estimate: the RIA's Table 3.1 (FR page 23855), federal student-loan disbursements before and after the Act over 2026–2035, by loan type, in $ millions. The table says only "2026–2035"; the same RIA states its budget estimates by loan cohort ("A cohort reflects all loans originated in a given fiscal year"), so the README calls them probably cohort years (skeptic mkt-s66). ED's columns are "Pre" and "Post": its source line names the PB2026 volume assumption and its cost estimates for the Act, while its text credits "the final regulations"; the README quotes ED's labels rather than calling them before and after the Act (mkt-s67).
- **What is shown.** Table 3.1's disbursement columns as printed, the non-consolidated total before and after, and the fall. `ed_volume.py` reads the table's verbatim text layer (`fixtures/ed_rule_table_3_1.txt`). It checks that the three non-consolidated rows reproduce ED's printed difference, and that the graduate and Parent PLUS falls match the rule's own text ($171 billion, $49 billion). Consolidation loans are shown on their own line and kept out of the total, as ED does.
- **Labels.** An ED projection of the fall in **federal** lending, not an estimate of lending moving to private lenders and not a loss. It is set beside the CBO proxy (3b), but the two are not combined: one is projected program-account outlays (what the account pays for the loans' cost) across two CBO baselines, the other projected loan volume from ED's model. No ratio between them is computed, because that would be a new method choice.
- **No loss-engine change** (her ruling). Neither figure enters B3, and no public share changes.

## Results
The recession range and the GSE-release range are computed (`results.json`, `b4.py`; README by `make_readme_and_rows.py`). Section 3 is left out until a reachable CBO estimate exists (card b4-student-2 (iii)).
