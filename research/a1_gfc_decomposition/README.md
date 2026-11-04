# A1: What made up the 2007–11 jump?

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A1. Status: analysis done; write-up is a Claude draft for Eleonora to replace.** The decomposition is exact, and every policy date below is checked against a primary source ([`sources.md`](sources.md)).

Data: Fed Z.1, `Z1.csv` dated 2026-09-11. Every number in this file has a row in [`claims/register.csv`](../../claims/register.csv), and `claims/check_register.py` scans this file.

## Result

From 2007Q4 to 2011Q4 the public share of household mortgages and consumer credit rose from 36.1% to 49.2%, +13.1 pp. That total matches validation check C5. The parts below add up to it exactly.

**Growth versus retreat.** Public holdings growing explains 7.1 pp. Private holdings shrinking explains 6.0 pp. The split is exact: ΔP = (1 − P₀)·ΔPub / S₁ − P₀·ΔPriv / S₁.

**Which public holders grew:**

| Component | Change in holdings | Contribution |
|---|---|---|
| Ginnie Mae pools (FHA, VA, USDA loans) | +$746B | 3.8 pp |
| Federal student loans | +$379B | 1.9 pp |
| Fannie Mae and Freddie Mac (portfolio + pools) | +$278B | 1.4 pp |

All other public holders combined (FHLBs, other GSEs, federal direct mortgages, state and local) were net zero to one decimal.

**Which private holders shrank.** Private-label securitization and mortgage REITs held $1.71T less, which contributed 4.9 pp. Banks, credit unions and other private holders contributed the rest of the 6.0 pp.

**Own-share view.** Here each public holder's own share of the total changes, so the private retreat is spread across them. Ginnie pools +6.1 pp, Fannie and Freddie +3.9 pp, federal student loans +3.1 pp. Summed into the catalog's buckets, this view reproduces `analysis/results.json` `gfc_window_split_pp` exactly (GSE & agency, federal student loans, state and local).

**What this changes.**
- **The largest public piece is FHA/VA, not the GSEs.** That part is explicitly federal: FHA and VA insure the loans, and Ginnie Mae guarantees the securities.
- **Fannie and Freddie's piece came early and partly reversed.** Quarter by quarter (`path.csv`), Fannie and Freddie had contributed 1.3 pp by 2008Q3, before the September 2008 conservatorship. They peaked at 2.3 pp in 2009Q4 and were back to 1.4 pp by 2011Q4. Their balances barely grew. Their share rose mostly because private holders shrank around them.
- **"The GSE conservatorship ratcheted risk onto the public" doesn't fit these data.** Conservatorship changed the backing behind debt the GSEs already held. Within this window, it didn't change how much they held.

## Dated policy events

The decomposition is an accounting, not a causal estimate (that is A7). The events below line up in time with the components; that does not show they caused them. Each date and citation was checked on 2026-11-04 against the official text (GovInfo for statutes, FHFA, the Fed's Z.1 release); URLs, file hashes and quoted sections are in [`sources.md`](sources.md).

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
- **FAS 166/167 reshuffled private holders in 2010Q1.** Card ABS moved onto bank balance sheets, so the private-label line jumps and the bank line falls in that quarter (`path.csv`). Every private holder has the same weight in the identity, so reclassifications between private holders cancel. The private total is unaffected, but the split between private lines around 2010Q1 is accounting, not behaviour. The same consolidation moved GSE pool MBS from sector 41 to sector 40, which is why Fannie and Freddie are shown as portfolio plus pools.
- **Apportioning.** Mortgage holders are scaled to the household liability, as in the rest of the project, assuming the same holder mix for household and business 1–4 family mortgages.
- **"Other GSEs" is partly a residual.** It is FL403065105 minus the Fannie, Freddie and FHLB lines. It is small (under $20B) and is reported, not hidden.
- **A different counterfactual gives different words.** `analysis/findings.md` says that had private debt stayed at its 2007Q4 level, the share would have risen 6.1 pp. That holds private debt fixed. The identity here instead splits the actual change. Both say about half of the jump came from private retreat.
- **Revisions.** The figures are from the 2026-09-11 vintage. Rerun after each Z.1 release.

## Files and how to rerun

```bash
uv run --project pipeline python validation/run.py        # downloads the Z.1 zip if absent
uv run --project pipeline python research/a1_gfc_decomposition/decompose.py
```

- `decompose.py`: the decomposition. It asserts that the parts sum to the total and that the cells reproduce the scope total.
- `decomposition.csv`: endpoint contributions by loan type × holder (all holders).
- `own_share_change.csv`: the own-share view (public holders).
- `path.csv`: cumulative chained contributions by quarter, grouped.
- `results.json`: headline numbers for the register.
- `sources.md`: the primary sources for the policy dates, with hashes.
- Method decision: [`docs/decisions/a1-decomposition.md`](../../docs/decisions/a1-decomposition.md).
