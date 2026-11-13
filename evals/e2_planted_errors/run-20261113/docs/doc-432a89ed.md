# A1: What made up the 2007–11 jump?

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A1. Status: analysis done; method decided by Eleonora (Shapley, 2026-11-04); the write-up is a Claude draft for her to replace.** The skeptic and quant-reviewer agents reviewed it (`claims/review-log.md`, R-20261104-1 to -12). Data: Fed Z.1, `Z1.csv` dated 2026-09-11. Every number here has a row in [`claims/register.csv`](../../claims/register.csv), and every policy date is checked against a primary source ([`sources.md`](sources.md)).

## Result

From 2007Q4 to 2011Q4 the public share of household mortgages and consumer credit rose from 36.1% to 49.2%, +13.1 pp (validation check C5). A little over half of that came from private holdings shrinking: private retreat explains 6.9 pp and public growth 6.2 pp. The parts add up to the total exactly.
Here the public share leaves out state and local governments, unlike elsewhere in the project.

**Method.** Shapley, per Eleonora's decision of 2026-11-04: the public side's contribution is the average of counting it first and counting it last, and the private side gets the rest. Within each side, each holder's share is proportional to its change in holdings. The endpoint-weighted identity of the first draft gave public 7.1 pp and private 6.0 pp, which reverses the order; the quarter-by-quarter Shapley path matches the Shapley endpoints to one decimal. All three are in `results.json` (`sensitivity`).

**Which public holders grew:**

| Component | Change in holdings | Contribution |
|---|---|---|
| Ginnie Mae pools (FHA, VA, USDA loans) | +$746B | 3.3 pp |
| Federal student loans | +$379B | 1.7 pp |
| Fannie Mae and Freddie Mac (portfolio + pools) | +$278B | 1.2 pp |

All other public holders combined (FHLBs, other GSEs, federal direct mortgages, state and local) were net zero to one decimal.

**Which private holders shrank.** Private-label securitization and mortgage REITs held $1.71T less, which contributed 5.7 pp. Part of that is accounting: FAS 166/167 moved securitized loans, mostly card ABS, onto bank balance sheets in 2010Q1 (`path.csv`), which leaves the private total unchanged. Banks, credit unions and other private holders contributed the rest of the 6.9 pp.

**Own-share view.** Measured by each public holder's own share of the total, which spreads the private retreat across them: Ginnie pools +6.1 pp, Fannie and Freddie +3.9 pp, federal student loans +3.1 pp. Summed into the catalog's buckets, this reproduces `analysis/results.json` `gfc_window_split_pp` exactly. It describes composition and says nothing about cause.

**What this changes.**
- **The largest public increase was in Ginnie Mae pools (FHA/VA/USDA loans).** Fannie and Freddie grew less but still held far more: $4.34T against Ginnie pools' $1.13T in 2011Q4. VA and USDA guarantees are partial, and FHA loans held by banks, or bought out of Ginnie pools, count as private here.
- **Fannie and Freddie's piece came early and partly reversed.** Per `path.csv`, they had contributed 1.1 pp by 2008Q2, the last quarter-end before the September 2008 conservatorship, peaked at 2.3 pp in 2009Q4 and fell back afterwards. Their balances grew $278B over the window.
The 2008 rescues caused this shift directly.
- **These data cannot test whether the conservatorship ratcheted risk onto the public.** The GSEs count as public at every date, so the conservatorship changes nothing in this accounting. Whether it changed how much the GSEs held, or what their debt cost, is a counterfactual question for A7.

## Dated policy events

The decomposition is an accounting; the causal estimate is A7. Events are matched to components by topic: federal student loans, for example, had moved only 0.03 pp by 2008Q2 and grew most after mid-2010. Each date and citation was checked on 2026-11-04 against the official text (GovInfo for statutes, FHFA, the Fed's Z.1 release); URLs, file hashes and quoted sections are in [`sources.md`](sources.md).

| Date | Event | Component it lines up with |
|---|---|---|
| 13 Feb 2008 | Economic Stimulus Act of 2008 (P.L. 110-185), Secs. 201–202: temporary rise in GSE and FHA loan limits | Ginnie pools; Fannie and Freddie |
| 7 May 2008 | Ensuring Continued Access to Student Loans Act (P.L. 110-227), Sec. 7: temporary authority to buy FFEL loans | Federal student loans |
| 30 Jul 2008 | Housing and Economic Recovery Act (P.L. 110-289), Secs. 1101 and 1117: creates FHFA; temporary Treasury authority to buy GSE obligations | Fannie and Freddie |
| 6–7 Sep 2008 | FHFA places Fannie Mae and Freddie Mac in conservatorship (6 Sep); Treasury preferred-stock agreements signed (7 Sep) | Fannie and Freddie |
| 17 Feb 2009 | American Recovery and Reinvestment Act (P.L. 111-5), Secs. 1202–1203: FHA and GSE loan limits for 2009 | Ginnie pools; Fannie and Freddie |
| 2010Q1 | FAS 166 and 167: Z.1 moves consolidated securitizations from the pool and ABS sectors onto GSE, bank and finance-company balance sheets, "almost all" in 2010Q1 (Fed Z.1 release, 10 Jun 2010) | Accounting only (see limits) |
| 30 Mar 2010 | Health Care and Education Reconciliation Act (P.L. 111-152), Sec. 2201 (SAFRA): no new FFEL loans first disbursed after 30 Jun 2010 | Federal student loans |

## Limits

- **Holding is not guaranteeing.** Most FFEL loans held by banks before 2010 already carried a federal guarantee, so the student-loan component overstates the shift in credit risk. FHA and VA loans held directly by banks are federally insured but count as private here. Net exposure is task A2.
- **FAS 166/167 reshuffled private holders in 2010Q1.** Card ABS moved onto bank balance sheets, so the private-label line jumps and the bank line falls in that quarter. The private side's contribution depends only on the private total, so these reclassifications cancel. The same consolidation moved GSE pool MBS from sector 41 to sector 40, which is why Fannie and Freddie are shown as portfolio plus pools.
- **Ginnie label.** The Ginnie line includes the small FmHA pool line (FL413065133), which is zero at both endpoints.
- **Apportioning.** Mortgage holders are scaled to the household liability, as in the rest of the project, assuming the same holder mix for household and business 1–4 family mortgages.
- **"Other GSEs" is partly a residual:** FL403065105 minus the Fannie, Freddie and FHLB lines. It is under $20B.
- **A different counterfactual gives different words.** `analysis/findings.md` says that had private debt stayed at its 2007Q4 level, the share would have risen 6.1 pp. That is the public-growth side of a split that holds private debt fixed; the Shapley split averages over both orders. Both say about half of the jump came from private retreat.
- **Pool sub-series before 1987.** In the 2026-09-11 vintage the four pool lines (FL413065110, FL413065123, FL413065133, FL413065143) exceed the pool total FL413065105 from 1974Q3 to 1986Q3, by up to $21.4B ($14.6B in 1980Q4). Inside A1's window they match exactly, and `decompose.py` asserts this every run. A1 should stay inside 1987 onwards with these cells until the gap is explained. The markets track found the gap on 2026-11-04.
- **Revisions.** The figures are from the 2026-09-11 vintage. Rerun after each Z.1 release.

## Files and how to rerun

```bash
uv run --project pipeline python validation/run.py        # downloads the Z.1 zip if absent
uv run --project pipeline python research/a1_gfc_decomposition/decompose.py
```

- `decompose.py`: the decomposition (Shapley; the endpoint identity as a sensitivity). It asserts that the parts sum to the total and that the cells reproduce the scope total.
- `test_decompose.py`: synthetic tests of both methods.
- `decomposition.csv`: endpoint contributions by loan type × holder (all holders).
- `own_share_change.csv`: the own-share view (public holders).
- `path.csv`: cumulative chained contributions by quarter, grouped.
- `results.json`: headline numbers for the register.
- `sources.md`: the primary sources for the policy dates, with hashes.
- Method decision: [`docs/decisions/a1-decomposition.md`](../../docs/decisions/a1-decomposition.md).
