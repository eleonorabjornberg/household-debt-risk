> **Claude draft.** Written by Claude from the project's claims register for Eleonora to review and rewrite; not her text. Numbers: Fed Z.1 2026-09-11; FRED 2026-10-27; NY Fed 2026-10-27.

# Agency mortgage holders are shifting from the Fed's book back to the market, and private-label has not returned
**Audience:** `mbs_desk`, agency MBS trader or portfolio manager · **Date:** 2026-11-04 · **Data:** Fed Z.1 Financial Accounts 2026-09-11; FRED weekly Fed holdings 2026-10-27; NY Fed household credit report 2026-10-27

## Bottom line
Public holders (the federal government, Fannie Mae and Freddie Mac and the agency pools, Ginnie Mae's included, and state and local governments) hold 65.6% of household mortgages in 2026Q2 (Z.1). The Fed is not a separate holder in that count: its MBS sit inside the agency pools. Its own MBS book has been shrinking since its 2022Q1 peak, so the buyer base for agency paper is changing even though the public share is high. Private-label securitization is a small remnant of its pre-crisis size. Holdings here describe who owns the loans, not who bears the loss.

## What the data show
- **Public share of mortgages.** From the Z.1, the public share of household mortgages alone was 65.6% in 2026Q2, worth $9.16T in nominal dollars. These are holdings, not guarantees.
- **Fed runoff.** Fed-held agency MBS peaked at 16.4% of in-scope household debt in 2022Q1, equal to $2.72T at that quarter-end. By 2026Q2 the share was 10.3%. On the FRED weekly series, which is later than the Z.1 vintage, the Fed held $1.90T on 2026-10-21, which is $845B below the April 2022 peak. This is rate (duration) risk rather than credit risk, and it sits inside the public share.
- **Private-label.** The private-label pile was $4.5T at the end of 2007 and $1.7T at the end of 2011, both in 2026 dollars. The private-label pile is not an exposure measure, because it leaves out private-label risk held in banks or other holders.
- **Where the 2007-11 shift landed.** Mortgages in Ginnie Mae pools (household-apportioned) rose $746B over 2007Q4-2011Q4. The largest public increase in that window was in Ginnie Mae pools, not the GSEs. Private-label securitization and mortgage REITs held $1.71T less over the same window; part of that is an accounting move of securitized loans onto bank balance sheets in 2010Q1, not retreat.
- **The whole public share.** For mortgages and consumer credit together, the public share was 36.1% at 2007Q4 and 49.2% at 2011Q4, a rise of 13.1 pp. It stands at 56.4% in 2026Q2.

## What it means for you
For supply and positioning work, the holder mix matters more than the headline public share. The Fed's retreat from its peak does not change the public share (Fed MBS sit inside the agency pools, which count as public whoever holds them), but it changes who holds agency paper, on a schedule the Fed sets, so the net amount the market must absorb depends on how much of the runoff is replaced by other holders. The Z.1 does not tell us who that marginal buyer is by pool coupon or vintage, so it cannot replace your own flow data.

The 2007-11 episode is a reminder of which parts of the public book grew fastest in stress. Ginnie Mae pools grew most, and private-label shrank. Today's much smaller private-label share means that stress in the mortgage market would meet a thin private bid for non-agency risk, while the agency channel is the one with an existing, large holder base. This is a description of the holder structure, not a view on spreads or coupons.

## Caveats
- **Holdings are not guarantees.** Public holders owning a loan or a pool does not mean taxpayers bear its credit loss. VA and USDA guarantees are partial, and FHA loans held by banks count as private here.
- **Z.1 versus NY Fed.** The two sources measure different things and should not be set against each other. In 2026Q2 the Z.1 shows household mortgages rising by $150B (not seasonally adjusted). That is a Z.1 figure; the NY Fed credit-report data are a sample of credit reports and are read separately.
- **Vintage and status.** Most rows used here are UNVERIFIED in the claims register (no independent validation check yet); the status is shown in the Sources table. The weekly Fed figure is later than the Z.1 vintage, so it is not a same-date comparison with the quarterly shares.
- **Nominal versus real.** The private-label figures are in 2026 dollars; the Ginnie Mae and public-holder dollar amounts are nominal.
- **Accounting.** The decomposition behind the 2007-11 comparison is an accounting identity, not a causal estimate.

## What to watch
- The next Z.1 release (the Fed publishes around the second week of December) for whether the Fed's share keeps falling from 10.3%.
- The next weekly FRED update of Fed-held agency MBS, against the $1.90T level on 2026-10-21.
- Whether the public share of mortgages moves away from 65.6% in the 2026Q3 data, and which holders account for it.
- The next NY Fed household debt report, read separately from the Z.1 figures.

## Sources
| Register row | Claim | Period | Status | Vintage |
|---|---|---|---|---|
| `public_share_mortgage_2026q2` | Public share of household mortgages | 2026Q2 | PASS | z1:2026-09-11 |
| `public_mortgage_usd_2026q2` | Public holders' household mortgages, nominal | 2026Q2 | UNVERIFIED | z1:2026-09-11 |
| `fed_mbs_peak_share` | Fed MBS peak share of scope debt | 2022Q1 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_peak_usd` | Fed MBS peak level | 2022Q1 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_now_share` | Fed MBS share of scope debt | 2026Q2 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_weekly_usd` | Fed MBS weekly level | 2026-10-21 | UNVERIFIED | fred:2026-10-27 |
| `fed_mbs_runoff_usd` | Fed MBS below April 2022 peak | 2022-04-13 to 2026-10-21 | UNVERIFIED | fred:2026-10-27 |
| `private_label_2007q4_real` | Private-label pile, 2026 dollars | 2007Q4 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `private_label_2011q4_real` | Private-label pile, 2026 dollars | 2011Q4 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `a1_ginnie_change_usd` | Ginnie Mae pool mortgages, change | 2007Q4-2011Q4 | UNVERIFIED | z1:2026-09-11 |
| `a1_pls_change_usd` | Private-label and REIT holdings, change | 2007Q4-2011Q4 | UNVERIFIED | z1:2026-09-11 |
| `public_share_2007q4` | Public share, mortgages and consumer credit | 2007Q4 | PASS | z1:2026-09-11 |
| `public_share_2011q4` | Public share, mortgages and consumer credit | 2011Q4 | PASS | z1:2026-09-11 |
| `gfc_jump_pp` | Public share rise | 2007Q4-2011Q4 | PASS | z1:2026-09-11 |
| `public_share_2026q2` | Public share, mortgages and consumer credit | 2026Q2 | PASS | z1:2026-09-11 |
| `z1_mortgage_change` | Z.1 household mortgage change | 2026Q2 | UNVERIFIED | z1:2026-09-11 |
