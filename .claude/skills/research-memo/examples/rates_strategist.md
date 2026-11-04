> **Claude draft.** Written by Claude from the project's claims register for Eleonora to review and rewrite; not her text. Numbers: Fed Z.1 vintage 2026-09-11; FRED download 2026-10-27; NY Fed household debt data download 2026-10-27.

# The Fed's mortgage book is shrinking inside a household sector that is far less levered than in 2007
**Audience:** `rates_strategist`, rates or macro strategist at an asset manager · **Date:** 2026-11-04 · **Data:** Fed Z.1 Financial Accounts 2026-09-11; FRED 2026-10-27; NY Fed household debt data 2026-10-27

## Bottom line
Fed-held agency MBS peaked in 2022Q1 and have run off steadily since. Over the same period the public sector as a whole kept holding most household mortgage and consumer debt, and the Fed's retreat does not change that share at all: Fed MBS sit inside the agency pools, which count as public whoever holds them. Household leverage against income is far below its 2007 level. The balance-sheet story for duration is therefore mostly about who absorbs the MBS the Fed no longer holds, not about household credit stress.

## What the data show
- **Fed MBS runoff (Z.1 plus FRED).** Fed-held agency MBS peaked at $2.72T in 2022Q1, or 16.4% of the household mortgage and consumer-credit debt the project tracks. In 2026Q2 they are 10.3% of that debt. On the weekly series they were $1.90T on 2026-10-21, which is $845B below the April 2022 peak.
- **Public holders overall (Z.1).** The public sector (federal government, GSEs and agency pools, state and local governments) held $10.77T of household mortgages and consumer credit in 2026Q2, a 56.4% share. The share peaked at 58.6% in 2021Q1, so the runoff has coincided with only a modest drift down in the public share, not a collapse.
- **Mortgages versus consumer credit (Z.1).** The public share of household mortgages alone was 65.6% in 2026Q2. For consumer credit it was 31.3%, almost all federal student loans.
- **Leverage against income (Z.1 and FRED).** Mortgage and consumer debt is about 80% of disposable income in 2026Q2, against about 124% at the end of 2007.
- **How fast public holdings respond to a shock (Z.1).** From 2007Q4 to 2011Q4 the public share rose +13.1 pp, from 36.1% to 49.2%. That is the one episode in the project's history where a crisis clearly pushed the share up. About half of it was private lenders retreating rather than public expansion; the share had fallen in the years before the peak.

## What it means for you
For a duration or curve view, the household sector is not currently the transmission channel to worry about: debt is a much smaller multiple of income than in 2007, and the Fed MBS decline is a supply-and-demand question for the agency market rather than a signal about household credit. The 2007 to 2011 episode is the useful reference for how the public share behaves in a shock. It moved up quickly, and much of that move came from private holders stepping back, so a similar episode would push more mortgage risk onto agency and GSE balance sheets at the same time as the Fed is a smaller holder than it was at its peak. The data do not say how that supply would be priced.

## Caveats
- **Holdings are not guarantees.** "Public sector holds" describes who owns the claim, not who bears a loss. Agency MBS carry guarantees; other public holdings, such as student loans, do not work the same way. Nothing here implies taxpayers bear losses.
- **Z.1 versus NY Fed.** The Fed MBS share, the public shares and the debt-to-income ratio are Z.1-based (the debt-to-income ratio also uses FRED income data). The NY Fed credit-report data show total household debt of $18.77T in 2026Q2. That is a NY Fed figure, not a Z.1 figure, built from credit-report data rather than the Z.1 accounts; the two sources use different scopes and are not interchangeable.
- **Weekly versus quarterly.** The $1.90T figure is a weekly FRED series; the 16.4% and 10.3% shares are quarter-end Z.1 ratios. Do not read them as one series.
- **Verification status.** Most rows used here are marked UNVERIFIED in the register (see Sources); they trace to code but have not had an independent review. Z.1 is revised each quarter, so these figures can move.
- **Scope.** The project covers household and nonprofit 1-4 family mortgages plus consumer credit. It excludes other household liabilities and says nothing about commercial or multifamily mortgages.

## What to watch
- The next Z.1 release (mid-December): whether the Fed MBS share keeps falling and whether the public share stays near its current level.
- The weekly Fed MBS series: whether runoff continues at the same pace.
- Debt to income: a rise toward its 2007 level would change the reading above.
- Any episode in which private holders pull back from mortgages, since that was the mechanism behind the 2007 to 2011 jump.

## Sources
| Register row | Claim | Period | Status | Vintage |
|---|---|---|---|---|
| `fed_mbs_peak_usd` | Fed-held agency MBS at their peak | 2022Q1 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_peak_share` | Fed MBS peak share of scope debt | 2022Q1 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_now_share` | Fed MBS share of scope debt now | 2026Q2 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `fed_mbs_weekly_usd` | Fed MBS on the weekly series | 2026-10-21 | UNVERIFIED | fred:2026-10-27 |
| `fed_mbs_runoff_usd` | Fed MBS below the April 2022 peak | 2022-04-13 to 2026-10-21 | UNVERIFIED | fred:2026-10-27 |
| `public_usd_2026q2` | Public holdings of household debt | 2026Q2 | PASS | z1:2026-09-11 |
| `public_share_2026q2` | Public share | 2026Q2 | PASS | z1:2026-09-11 |
| `public_share_peak` | Public share peak | 2021Q1 | PASS | z1:2026-09-11 |
| `public_share_mortgage_2026q2` | Public share of mortgages | 2026Q2 | PASS | z1:2026-09-11 |
| `public_share_cc_2026q2` | Public share of consumer credit | 2026Q2 | PASS | z1:2026-09-11 |
| `debt_to_income_2026q2` | Debt to disposable income now | 2026Q2 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `debt_to_income_2007q4` | Debt to disposable income, 2007 | 2007Q4 | UNVERIFIED | z1:2026-09-11 fred:2026-10-27 |
| `gfc_jump_pp` | Public share rise in the Great Recession | 2007Q4-2011Q4 | PASS | z1:2026-09-11 |
| `public_share_2007q4` | Public share at the 2007 peak | 2007Q4 | PASS | z1:2026-09-11 |
| `public_share_2011q4` | Public share four years later | 2011Q4 | PASS | z1:2026-09-11 |
| `gfc_half_private_retreat` | About half the rise was private retreat | 2007Q4-2011Q4 | UNVERIFIED | z1:2026-09-11 |
| `nyfed_total_2026q2` | NY Fed total household debt | 2026Q2 | UNVERIFIED | nyfed:2026-10-27 |
