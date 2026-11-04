# B4: Policy-regime scenarios

> **Claude draft, not the author's text.** The status of each policy debate was looked up from primary sources on 2026-11-04 ([`sources.md`](sources.md)), not assumed. How each scenario maps onto the B3 engine is Eleonora's choice: the recession range follows her Q-B3 decision, the GSE range her card b4-gse (a); the student-loan scenario waits for a sourced estimate (card b4-student (c)). Method: [`METHOD.md`](METHOD.md).

**PLAN task B4. Status: recession range and GSE-release range done; the student-loan scenario waits for a sourced estimate.**

| Scenario | Status of the debate (as looked up, 2026-11-04) | Result |
|---|---|---|
| Recession | — | Losses from $595B to $1,886B on 2026Q2 balances. The public share of losses is 23% to 42%. The range runs from B3's DFAST proxy to its 2008–12 replay; both are proxies. |
| GSEs released from conservatorship | FHFA's conservatorship page, retrieved 2026-11-04, says "Fannie Mae and Freddie Mac continue to operate under conservatorship, as they have since 2008". The page carries no date of its own and cites the 2025 Scorecard, so it may lag. Only the first page of FHFA news releases (10 items) was checked, and none concerned an exit. So the status is **unconfirmed beyond those two pages**. | Public share of losses from 7% to 42% across both recession proxies and 0–100% of the Fannie and Freddie book turning private (below). |
| Student-loan reform | P.L. 119-21, approved July 4, 2025: no Federal Direct PLUS loans for graduate and professional students for periods from July 1, 2026, subject to the statute's transition exception ("Subject to paragraph (8)"); new limits; a Repayment Assistance Plan. | Waits for a sourced estimate of the lending shift (card b4-student (c)) |

- **No transfer.** Neither range applies a CRT or mortgage-insurance transfer. With A2's cover as an input, the public figures would be lower.
- **Two kinds of bound.** The two recession ends differ in horizon as well as severity: nine quarters of stressed bank loss rates against five years of realised bank charge-offs. The upper end is probably an upper bound for the public book (`research/b3_scenarios/README.md`).

## GSE release: who bears the losses (card b4-gse (a))

**What moves.** On release, a share of the losses on Fannie Mae's and Freddie Mac's books (portfolio and pools) turns private: 0% (the implicit guarantee holds), then 25%, 50%, 75% and 100% (fully private, no backstop). These are scenario points, not forecasts of release terms. Balances and loss rates stay as in B3; only the side of the losses changes.

**What stays public.** Ginnie Mae and FmHA pools (an explicit federal guarantee), the FHLBs and the other GSEs. The split of B3's "GSEs & agency pools" mortgage book ($8,977B, household-apportioned, 2026Q2, from the 2026-09-11 Z.1 release):
- Fannie Mae and Freddie Mac, the book that is released: $6,277B (Fannie $3,329B, Freddie $2,948B).
- Ginnie Mae and FmHA pools: $2,611B.
- FHLBs and other GSEs: $90B.

**Result.** Public losses and the public share of all household-credit losses, by share of the Fannie/Freddie book's losses that turns private:

| Share turning private | DFAST 2026 proxy: public losses | Public share of losses | 2008–12 replay proxy: public losses | Public share of losses |
|---|---|---|---|---|
| 0% | $137B | 23% | $801B | 42% |
| 25% | $114B | 19% | $663B | 35% |
| 50% | $90B | 15% | $526B | 28% |
| 75% | $67B | 11% | $389B | 21% |
| 100% | $43B | 7% | $252B | 13% |

Total losses do not change with the share: $595B under the DFAST proxy and $1,886B under the replay. At 0% the figures equal the recession range above.

**Caveats.**
- **One loss rate per class.** B3 applies one mortgage loss rate to every holder, so Fannie and Freddie lose at the same rate as Ginnie's FHA and VA pools. If Ginnie's pools lose more per dollar than the GSE book, the public share at each point is understated, and overstated if they lose less. Relative loss rates are not estimated here.
- **Proxies.** Both loss paths are bank-portfolio proxies (B3).
- **Release is not the same as loss-bearing.** A released GSE would hold capital and buy CRT. The share turning private stands in for those terms, which are not known (option (c) of the card, a specific proposal, was not chosen).

## Reproduce

```bash
uv run --project pipeline python research/b3_scenarios/engine.py        # exposures (Z.1 2026-09-11)
uv run --project pipeline python research/b4_policy_scenarios/b4.py
uv run --project pipeline python research/b4_policy_scenarios/make_readme_and_rows.py
```
