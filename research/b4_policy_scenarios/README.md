# B4: Policy-regime scenarios

> **Claude draft, not the author's text.** The status of each policy debate was looked up from primary sources on 2026-11-04 ([`sources.md`](sources.md)), not assumed. How each scenario maps onto the B3 engine is Eleonora's choice: the recession range follows her Q-B3 decision, the GSE range her card b4-gse (a). The student-loan scenario is left out for now (card b4-student-2 (iii)). Method: [`METHOD.md`](METHOD.md).

**PLAN task B4. Status: recession range and GSE-release range done; the student-loan scenario has a CBO budget-side proxy (card cbo-repo-55 (b), 2026-11-11); whether it feeds the loss engine waits on Eleonora.**

| Scenario | Status of the debate (as looked up, 2026-11-04) | Result |
|---|---|---|
| Recession | — | Losses from $595B to $1,886B on 2026Q2 balances. The public share of losses is 23% to 42% (federal student loans excluded: no loss rate in either preset). The range runs from B3's DFAST proxy to its 2008–12 replay; both are proxies. |
| GSEs released from conservatorship | FHFA's conservatorship page, retrieved 2026-11-04, says "Fannie Mae and Freddie Mac continue to operate under conservatorship, as they have since 2008". The page carries no date of its own and cites the 2025 Scorecard, so it may lag. Only the first page of FHFA news releases (10 items) was checked, and none concerned an exit. So the status is **unconfirmed beyond those two pages**. | Public share of mortgage and other consumer-credit losses (federal student loans excluded) from 7% to 42% across both recession proxies and 0–100% of the Fannie and Freddie book turning private (below). |
| Student-loan reform | P.L. 119-21, approved July 4, 2025: no Federal Direct PLUS loans for graduate and professional students for periods from July 1, 2026, subject to the statute's transition exception ("Subject to paragraph (8)"); new limits; a Repayment Assistance Plan. | Budget-side proxy only (Eleonora, card cbo-repo-55 (b), 2026-11-11; section below). CBO's projected outlays of the Direct Loan program account over FY2026–FY2035 fell from $189B in its January 2025 baseline to $35B in its February 2026 baseline. These outlays are what the account pays out for the cost of federal direct loans, not the amount lent, and the change is not a CBO estimate of the law's effect or of lending moving to private lenders. No public share changes. |

- **No transfer.** Neither range applies a CRT or mortgage-insurance transfer. With A2's cover as an input, the public figures would be lower.
- **Two kinds of bound.** The two recession ends differ in horizon as well as severity: nine quarters of stressed bank loss rates against five years of realised bank charge-offs. The upper end is probably an upper bound for the public book (`research/b3_scenarios/README.md`).

## GSE release: who bears the losses (card b4-gse (a))

**What moves.** On release, a share of the losses on Fannie Mae's and Freddie Mac's books (portfolio and pools) turns private: 0% (losses stay on the GSEs' and Treasury's side, as under conservatorship), then 25%, 50%, 75% and 100% (fully private, no backstop). These are scenario points, not forecasts of release terms. Balances and loss rates stay as in B3; only the side of the losses changes.

**What stays public.** Ginnie Mae and FmHA pools, the FHLBs and the other GSEs. The Ginnie pools are federally insured or guaranteed loans (FHA, VA, USDA); VA and USDA guaranties are partial and issuers bear part of the loss, so counting the whole pool as public is a holder-based simplification (see A1's caveat). The split of B3's "GSEs & agency pools" mortgage book ($8,977B, household-apportioned, 2026Q2, from the 2026-09-11 Z.1 release):
- Fannie Mae and Freddie Mac, the book that is released: $6,277B (Fannie $3,329B, Freddie $2,948B).
- Ginnie Mae and FmHA pools: $2,611B.
- FHLBs and other GSEs: $90B.

**Result.** Public losses and the public share of losses on mortgages and other consumer credit, by share of the Fannie/Freddie book's losses that turns private. Federal student loans are excluded: neither B3 preset gives them a loss rate, so they add no loss.

| Share turning private | DFAST 2026 proxy: public losses | Public share of losses | 2008–12 replay proxy: public losses | Public share of losses |
|---|---|---|---|---|
| 0% | $137B | 23% | $801B | 42% |
| 25% | $114B | 19% | $663B | 35% |
| 50% | $90B | 15% | $526B | 28% |
| 75% | $67B | 11% | $389B | 21% |
| 100% | $43B | 7% | $252B | 13% |

Total losses do not change with the share: $595B under the DFAST proxy and $1,886B under the replay. At 0% the figures equal the recession range above.

**Caveats.**
- **What "public" means here.** Losses on the books of the GSEs, the federal government and other public holders. Under conservatorship the GSEs' own capital takes losses first and Treasury's Senior Preferred Stock Purchase Agreements stand behind them, so "public" is not the same as taxpayer outlay.
- **Gross of existing risk transfer.** The shares are measured before CRT and mortgage insurance. Fannie and Freddie already pass part of their losses to private investors and insurers today (A2, `research/a2_net_exposure/`), so on a net basis today's arrangement already sits above 0%.
- **One loss rate per class.** B3 applies one mortgage loss rate to every holder, so Fannie and Freddie lose at the same rate as Ginnie's FHA and VA pools. If Ginnie's pools lose more per dollar than the GSE book, the public share at each point is understated, and overstated if they lose less. Relative loss rates are not estimated here.
- **Proxies.** Both loss paths are bank-portfolio proxies (B3).
- **Release is not the same as loss-bearing.** A released GSE would hold more capital and could buy more CRT. The share turning private stands in for those terms, which are not known (option (c) of the card, a specific proposal, was not chosen).

## Student-loan reform: a CBO budget-side proxy (card cbo-repo-55 (b))

> **Claude draft.** Eleonora chose (2026-11-11) to add CBO's data repository as a source for budget-side context only, and to use the Direct Loan account's outlays as a labelled proxy here. Method: `METHOD.md` section 3b. Sources, commit and hashes: [`sources.md`](sources.md).

**What the number is.** CBO's baseline projections of spending by budget account, for the "Federal Direct Student Loan Program Account" (TIN 091-0243-0-1-502). Under the Federal Credit Reform Act, a credit program account receives "an appropriation to cover the cost" of the loans, where cost is their net present value to the government (2 U.S.C. 661a). Reestimates of that cost are shown in a subaccount of the same account, and administrative funding may be too (2 U.S.C. 661c). So these outlays are what this account pays out for the **cost** of federal direct loans. They are not the amount lent: loans are paid out through a financing account, which is not in CBO's file. They are not a complete net subsidy cost either: the sources fetched here do not establish where a negative subsidy is recorded.

**PROXY.** Projected outlays in the January 2025 baseline against the February 2026 baseline (the repository's file labels; P.L. 119-21 was approved between them, on July 4, 2025), FY2026–FY2035:

| Fiscal year | January 2025 baseline | February 2026 baseline |
|---|---|---|
| FY2026 | $16.7B | $3.9B |
| FY2027 | $17.6B | $3.7B |
| FY2028 | $18.1B | $3.1B |
| FY2029 | $18.4B | $2.8B |
| FY2030 | $18.8B | $3.0B |
| FY2031 | $19.1B | $3.3B |
| FY2032 | $19.5B | $3.5B |
| FY2033 | $19.9B | $3.8B |
| FY2034 | $20.2B | $4.0B |
| FY2035 | $20.3B | $4.2B |
| Total | $189B | $35B |

The total fell by $153B, or 81%.

**What this does not show.**
- **Not the law's effect alone.** A change between two baselines also carries every economic and technical revision CBO made in the thirteen months between them. The repository does not separate them.
- **Too early to be the Grad PLUS change.** The FY2026 figure already shows most of the fall (table), but the end of Grad PLUS applies to periods from July 1, 2026, late in FY2026. So the drop cannot be read as that provision's effect.
- **Not a shift to private lending.** Neither the CBO repository nor this proxy says how much graduate borrowing moves to private lenders. ED's final rule estimates the fall in federal disbursements (`sources.md`), not where the borrowing goes.
- **Not a loss.** The B3 loss engine is not run for this scenario, so no public share of losses changes. Whether and how this proxy should feed the engine is open (proposed card to Eleonora, `METHOD.md` 3b).
- **Projections, not outturns.** Both baselines are forecasts.
- **One account only.** Related accounts in the same files are left out: Student aid administration, the TEACH Grant program account, the Federal family education loan liquidating account and the Federal student loan reserve fund.

## Reproduce

```bash
uv run --project pipeline python research/b3_scenarios/engine.py        # exposures (Z.1 2026-09-11)
uv run --project pipeline python research/b4_policy_scenarios/b4.py
uv run --project pipeline python research/b4_policy_scenarios/cbo_extract.py      # CBO repo at commit 284a956 (github.com)
uv run --project pipeline python research/b4_policy_scenarios/student_proxy.py
uv run --project pipeline python research/b4_policy_scenarios/make_readme_and_rows.py
```
