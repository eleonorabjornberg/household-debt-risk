# So what? Recommendation v1

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN.md Phase 0 recommendation. Status: Claude draft; Eleonora writes the final text.** Data: Fed Z.1 vintage 2026-09-11 (latest quarter 2026Q2) plus the NY Fed Household Debt and Credit Report for 2026Q2. Every number below has a row in [`claims/register.csv`](../claims/register.csv); the id is in brackets. Rows with status `PASS` are reproduced independently by `validation/run.py`. Rows marked `UNVERIFIED` are traced to `analysis/notebook.py` and its results files but not yet checked independently; most numbers here are in that state, which is itself a limit on how hard to lean on them.

This note says what the findings mean for three audiences and, just as important, what they do not mean. It adds no new numbers to [`findings.md`](findings.md). Where the data cannot answer a question, it says so instead of guessing.

## In one paragraph

Public holders (the federal government, the GSEs and agency pools, and state and local governments) hold most US household mortgage and consumer debt: 56.4%, $10.77T of $19.10T, in 2026Q2. They did not get there through crises. Seventy years of slow GSE build-out did most of it, and 2007–11 is the one crisis that moved the share and kept it moved. Holding debt is not the same as bearing its losses, though. Most of the public book is mortgages with thick equity behind them in aggregate, and other parties stand in front of the taxpayer on some of it. The part of the public book where losses depend on collection rather than collateral is federal student loans, and it has grown from 2.4% to 14.9% of the book since 2007. So the honest summary for each audience is: taxpayers are the backstop for most household debt, but their nearest credit exposure is student loans, not mortgages. Policy should treat the public share as a structural fact, not a crisis legacy waiting to unwind. And aggregate mortgage default risk looks low next to 2007, but these data cannot see the tail where defaults happen.

## 1. Taxpayers

**What the data show**
- Public holders have 56.4% of in-scope household debt, $10.77T of $19.10T [public_share_2026q2, public_usd_2026q2, scope_usd_2026q2]. The share is 65.6% for mortgages and 31.3% for consumer credit [public_share_mortgage_2026q2, public_share_cc_2026q2].
- The public book is $9.16T of mortgages and $1.61T of consumer credit, almost all of it federal student loans [public_mortgage_usd_2026q2, student_usd_2026q2]. Student loans went from 2.4% of it at the end of 2007 to 14.9% now [student_in_public_book_2007q4, student_in_public_book_2026q2].
- The public sector holds 86% of student loans and 51% of all household debt with no collateral, against 7% of uncollateralized debt in 2007Q4 [public_share_of_student_loans, public_share_of_uncoll_2026q2, public_share_of_uncoll_2007q4].

**Recommendation.** Say "taxpayers are the ultimate backstop for most household debt", not "most of the losses land on public balance sheets". Point to student loans as the place where public credit exposure is closest to the surface.

**Limits**
- *Holding is not guaranteeing.* Z.1 records who holds a loan, not who loses if it defaults. Federally insured FHA/VA loans sit in bank portfolios (risk is public, holder private). Most FFEL student loans held by banks and ABS before 2010 carried a 97–98% federal guarantee [ffel_guarantee], so the 2010 student-loan shift overstates the shift in risk. Going the other way, private mortgage insurance and GSE credit-risk-transfer deals since 2013 move part of the GSE risk to private investors. None of these is measured in this project yet.
- *Equity is the first loss.* For mortgages, borrowers' equity absorbs losses before any holder. Coverage is 3.56× in aggregate [home_coverage_2026q2], but that figure includes unmortgaged homes.
- *Student-loan losses depend on collection.* The debt is hard to discharge in bankruptcy and can be collected through wage garnishment and tax-refund offsets, so a high default rate does not translate one-for-one into losses. This project does not estimate loss rates.
- *Revisions.* Z.1 revises history every quarter; between the June and September 2026 vintages the public share for shared quarters moved by at most 0.021 pp [revision_max_share_pp_2026_06_to_09].

## 2. Policy

**What the data show**
- Recession windows look like any other 16-quarter window: placebo p ≈ 0.30, and only 5 of 11 crisis windows beat the median ordinary window [ratchet_placebo_p, ratchet_crises_above_median].
- 2007Q4–2011Q4 is the exception: 36.1% to 49.2%, +13.1 points, the 98th percentile of all four-year windows [public_share_2007q4, public_share_2011q4, gfc_jump_pp, gfc_percentile]. About half was private retreat: privately held debt shrank 24.6% ($2.07T) while public holdings grew 29% ($1.40T) [gfc_private_shrink_pct, gfc_private_shrink_usd, gfc_public_growth_pct, gfc_public_growth_usd]. The share has not fallen below its 2011Q4 level since: the lowest quarter after it was 49.9% in 2012Q1 [public_share_min_after_2011q4].
- The GSE and agency pools added 18.8 points in the 1980s alone, outside any single crisis [gse_1980s_pp].
- Since 2019 the share has stayed between 55% and 59%, and none of the 2020Q1, 2023Q4 or 2025Q2 shocks moved it by more than one point [public_share_min_since_2019, public_share_max_since_2019, shocks_max_pp].

**Recommendation.** Treat the public share as the structural result of how the US finances housing, not a temporary crisis position that will unwind by itself. The policy lever that matters is the GSEs' status: a release from conservatorship would change who stands behind the largest pile (implicit versus explicit backing, capital, pricing), but not which pile it is in, because the GSEs count as public here either way. Debates about "getting the taxpayer off the hook" should be framed as who bears the GSEs' credit risk and how it is capitalised, not as reducing the public share.

**Limits**
- *Correlation is not cause.* The windows are descriptive. Eleven episodes, overlapping windows (1980Q1 and 1981Q3) and a trending, autocorrelated series mean the p-values are descriptive, not a formal test. The 1980Q1 and 1981Q3 windows were also large, +9.3 points and +8.3 points [window_1980q1_fwd16_pp, window_1981q3_fwd16_pp], but similar gains happened outside recessions in the 1980s, which is why they are read as trend.
- *Definitions drive the share.* "Public" is a project choice (federal, GSEs and agency pools, state and local). Counting only explicit federal backing would give a much smaller number; that version is not computed yet.
- *2025 collections.* Student-loan collections on defaulted federal loans restarted in 2025 (US Department of Education). The effect on losses is not in these data yet.

## 3. Mortgage default risk

**What the data show**
- Aggregate home coverage is 3.56× (a 72% equity cushion), higher than at any point outside 2022–26 since 1960; the low was 1.85× in 2012Q1 [home_coverage_2026q2, home_cushion, home_coverage_low].
- Mortgage and consumer debt is about 80% of disposable income, against 124% at the end of 2007 [debt_to_income_2026q2, debt_to_income_2007q4].
- Mortgages are 73% of in-scope debt [mortgage_share_of_scope_2026q2]; household debt has not drifted away from home collateral.
- The Fed holds agency MBS equal to 10.3% of in-scope debt (peak 16.4% in 2022Q1) [fed_mbs_now_share, fed_mbs_peak_share]. That is interest-rate risk for the Fed; the credit risk stays with the GSEs and Ginnie Mae.

**Recommendation.** At the aggregate level, mortgage default risk is low compared with 2007, and nothing here suggests the public mortgage book is the fragile part of household credit. Do not infer default risk from who holds the debt: a high public share says who is exposed, not how likely losses are. Any statement about default risk should wait for loan-level data (Phase A2 and B, Freddie Mac and Fannie Mae performance files).

**Limits**
- *Aggregates hide the tail.* Coverage and debt-to-income are national totals. Defaults happen among borrowers with little equity or falling income, which these numbers cannot see. No LTV, credit-score or regional distribution is used here.
- *Coverage includes homes without mortgages*, so it overstates the equity behind the average mortgaged home.
- *Two sources disagree on the latest quarter.* The NY Fed reports household debt falling to $18.77T in 2026Q2, with mortgages down $74B [nyfed_total_2026q2, nyfed_mortgage_change]; Z.1 shows mortgages up $150B and in-scope debt up $199B, not seasonally adjusted [z1_mortgage_change, z1_scope_change]. Coverage and sampling differ. Neither should be quoted next to the other without saying which it is.
- *Revisions* apply as in section 1.

## What would change this recommendation

- Loan-level data showing a thick tail of low-equity public mortgages (Phase A2, B).
- A measure of how much GSE risk has been transferred to private parties (CRT and mortgage insurance), which would lower the public share of *losses* below the public share of *holdings*.
- A conservatorship exit with an explicit guarantee, or its removal.
- A Z.1 revision that moves any registered number at display precision; the `z1-release-update` skill flags those.

## Changes made to the sites

Hot Potato's "What does this mean?" (`atlas/content/story.ts`, `meaning`) is revised to match this note:
1. "Most of the losses land on public balance sheets, not on banks" is replaced by "Taxpayers are the backstop, not the first loss", which names equity, mortgage insurance and risk transfer as standing in front, and says the site does not measure them.
2. The one-in-eleven stat, an interpretive count rather than a measured number, is replaced by the placebo p ≈ 0.30. "Never reversed" is stated as the tested rule: the share has not fallen below its end-2011 level.
3. The student-loan point now says part of the shift is relabelling (pre-2010 guarantees) and that losses depend on collection.
4. "Would move the biggest pile back across the line" was wrong under this site's own definition (GSEs count as public in or out of conservatorship). It now says a release changes who stands behind the pile, not which pile it is in.

Four further copy fixes, approved by Eleonora on 2026-11-04:
5. Hot Potato's "Today" step now says its totals are in 2026 dollars; the README and findings use nominal dollars ($10.77T of $19.10T), the site real ($10.8T of $19.2T).
6. The COVID step showed 2021Q4, a rise of more than two points in two years, under the title "COVID barely moves the dots". It now shows 2023Q4, the same 16-quarter window as every other crisis: 55.2% to 56.2%, about one point.
7. The two pre-crisis declines now name their windows: −5.0 points from the end of 1999 to the end of 2007 (story site) and 5.7 pp over 2003Q4–2007Q4 (findings).
8. Three values defined in the story site's code but never shown (`public1980s`, `covidDelta`, `uncollShare`) are deleted; their register rows keep the places the numbers are still published.

Deployed as a preview only.
