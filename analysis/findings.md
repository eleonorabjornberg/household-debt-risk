# Who Holds the Debt? Findings

**Data:** Fed Z.1 Financial Accounts, latest vintage through 2026Q2, plus FRED context series downloaded 2026-10-27. **Scope:** household and nonprofit 1-4 family mortgages (FL153165105) plus consumer credit (FL153166000). That was $19.10T in 2026Q2, 87.3% of total household liabilities. **Public** means the federal government (direct), GSEs and agency pools, and state and local governments. Mortgage holders are apportioned to the household liability. Every number below comes from `analysis/notebook.py` (see `results.json` and `tables/`). Unless marked "pp" (percentage points), shares are shares of the scope total.

Headline figures were cross-checked against the pipeline's `mart` tables (`data/out/`) and match: the 58.6% peak in 2021Q1, 56.4% and $10.77T in 2026Q2, the +$198.5B quarterly change in scope debt, Fed MBS at 16.4% → 10.3%, and home coverage of 3.56× with a low of 1.85×.

## Headline findings

1. **Most US household debt now sits on public or quasi-public balance sheets.** The public share of household mortgages and consumer credit rose from **3.2% in 1952Q1** to **56.4% in 2026Q2**: **$10.77T of $19.10T**. The all-time high was **58.6% in 2021Q1**. For mortgages alone it is **65.6%**. For consumer credit it is **31.3%**, almost all of it federal student loans.
2. **Crises don't reliably ratchet the share up. One did.** In the 16 quarters after an NBER peak, the public share rose **+3.7 pp on average**. Over all other 16-quarter windows since 1952 it rose **+3.0 pp**. That gap is noise. **30% of random placebo sets of 11 dates do as well or better**, and only **5 of 11** crisis windows beat the median ordinary window. Counting only crises since 1970, the gap is +1.8 pp, still weak (p ≈ 0.15).
3. **The Great Recession is the ratchet.** From 2007Q4 to 2011Q4 the public share jumped **from 36.1% to 49.2% (+13.1 pp)**. That is the largest change of any crisis, in the **98th percentile** of all 16-quarter windows. It also reversed a decline: the share had fallen 5.7 pp in the 16 quarters before the peak. Without 2007, crisis windows do *worse* than ordinary ones (−0.3 pp). Outside the GFC window, crisis windows cover **52% of quarters and 50% of the rise**, which is exactly proportional.
4. **Even the 2007 ratchet is half private retreat.** Public holdings grew **+29% (+$1.40T)** from 2007Q4 to 2011Q4. Privately held debt **shrank 24.6% (−$2.07T)**, led by private-label securitization, whose share fell **12.5 pp**. Had private debt stayed at its 2007Q4 level, the public share would have risen 6.1 pp, not 13.1.
5. **The long climb is mostly structural.** The GSE and agency build-out added **+18.8 pp in the 1980s alone** (1979Q4–1989Q4). The 1990 window's gain (+7.0 pp) matches the 16 quarters before it (+7.0 pp): it is the trend continuing. The 2001 recession is a counter-example: the share **fell 3.8 pp (4th percentile)** as private-label securitization boomed.
6. **The public book has tilted toward unsecured debt but is still 85% home-backed.** Federal student loans grew from **2.4% of the public book in 2007Q4 to 14.9% in 2026Q2** ($1.61T of $10.77T). Since 2007Q4 the public sector has added **$6.0T**: **$4.5T of agency mortgages and $1.5T of student loans**. It now holds **86% of all student loans** and **51% of all uncollateralized household debt** (cards plus student loans), up from **7% in 2007Q4**.
7. **The Fed's QE book sits inside the public share and is rate risk, not credit risk.** Fed-held agency MBS peaked at **16.4% of scope debt in 2022Q1** ($2.72T). They are now **10.3% (2026Q2)**, and **$1.90T on 2026-10-21**, **$845B below the April 2022 peak**. Credit risk on these securities stays with the GSEs and Ginnie Mae/FHA/VA, and ultimately the Treasury. The Fed bears interest-rate and duration risk.

**Verdict on the thesis.** The claim that *"each crisis since 1970 moved a larger share of household credit risk onto public balance sheets"* is **not supported as stated.** The direction is right: public holding has risen strongly over seven decades. But crisis step-ups are statistically indistinguishable from the trend, except in 2007–11. In 2001 the share fell, and 2019Q4/2020 added only about 1 pp. A defensible version: *"The public share has climbed for 70 years, mostly through the slow build-out of the GSEs. One crisis, 2008, produced a genuine ratchet, partly because private lenders retreated, and it was never reversed."* The second half of the thesis, *"away from debt backed by appreciating collateral"*, is **partly true for the public book** because of the student loan takeover. It is **not true for household debt overall**. Mortgages are 73.2% of scope debt today, against 65.6% in 1953. Aggregate home coverage of 3.56× is higher than at any point from 1960Q2 to 2021.

## 0. Verifying the first pass
The first-pass numbers in the original README did not include **state and local governments (FL213065103)** in "public". State and local holdings are mostly housing-finance-agency mortgages: **up to 2.1% of scope debt (1986Q1)** and 0.6% now. The README now uses the figures below, which include state and local, as the catalog and pipeline define "public":

| NBER peak | Public share at peak | +16 quarters | Change | First pass (ex-S&L) |
|---|---|---|---|---|
| 1953Q2 | 3.3% | 3.2% | −0.1 pp | — |
| 1957Q3 | 3.4% | 4.0% | +0.7 pp | 2.9% → 3.3% |
| 1960Q2 | 4.1% | 2.8% | −1.3 pp | 3.5% → 2.2% |
| 1969Q4 | 5.0% | 7.2% | +2.2 pp | 4.6% → 6.8% |
| 1973Q4 | 7.2% | 11.3% | +4.1 pp | 6.8% → 10.7% |
| 1980Q1 | 14.3% | 23.6% | +9.3 pp | 13.2% → 21.5% |
| 1981Q3 | 16.3% | 24.6% | +8.3 pp | 14.5% → 22.5% |
| 1990Q3 | 34.5% | 41.6% | +7.0 pp | 32.8% → 40.2% |
| 2001Q1 | 40.6% | 36.8% | −3.8 pp | 39.6% → 36.0% |
| 2007Q4 | 36.1% | 49.2% | +13.1 pp | 35.5% → 48.3% |
| 2019Q4 | 55.2% | 56.2% | +1.0 pp | 55.2% → 55.9% (2020Q1 start) |
| **2026Q2 (latest)** | **56.4%** | | | 55.8% |

Identity checks, all exact from 1952 to 2026:
- The 17 mortgage holders sum to FL893065105.
- The 9 consumer-credit holders sum to FL153166000.
- The 4 consumer-credit types sum to FL153166000.
- FL153165105 + FL153166000 = FL154104015.

## 1. Ratchet test
**Design.** For every start quarter *t* from 1952Q1 to 2022Q2 (282 windows), Δ₁₆(*t*) = share(*t*+16) − share(*t*). The crisis windows start at the 11 NBER peaks. The statistic is the mean Δ₁₆ over crisis windows minus the mean over all other windows. Two placebo tests check it:
- (a) 20,000 random sets of 11 start quarters;
- (b) every circular shift of the real crisis calendar, which keeps its spacing.

Windows overlap and the series is autocorrelated, so there are effectively about 11 observations.

| Test | Crisis mean | Other | Excess | p (random) | p (shift) | Crises > median |
|---|---|---|---|---|---|---|
| All 11 NBER peaks | +3.68 pp | +3.01 | +0.67 | 0.30 | 0.31 | 5/11 |
| Peaks since 1970 (7) | +5.58 | +3.75 | +1.83 | 0.15 | 0.16 | 5/7 |
| Excluding 2007 | +2.74 | +3.05 | −0.31 | 0.58 | 0.58 | 4/10 |
| Excluding 1980, 1981, 2007 | +1.22 | +3.09 | −1.87 | 0.89 | 0.89 | 2/8 |
| Acceleration (forward − prior 16q), all | +2.24 | −0.10 | +2.34 | 0.10 | 0.12 | 6/10 |
| Acceleration, since 1970 | +3.56 | −0.33 | +3.89 | 0.07 | 0.10 | 5/7 |
| Mortgages only | +4.46 | +3.47 | +1.00 | 0.27 | 0.25 | 6/11 |
| Mortgages only, since 1970 | +6.72 | +4.23 | +2.49 | 0.13 | 0.10 | 5/7 |
| Public excluding federal student loans | +3.50 | +2.53 | +0.97 | 0.22 | 0.20 | 7/11 |
| Windows starting at the trough | +2.61 | +3.05 | −0.44 | 0.63 | 0.66 | 6/11 |

**Leave-one-out excess:**
- Dropping 2007Q4 gives **−0.27**.
- Dropping 1980Q1 gives +0.11.
- Dropping 1981Q3 gives +0.21.
- Dropping 1990Q3 gives +0.34.
- Dropping 2001Q1 gives +1.42.
- Dropping any other crisis leaves +0.6 to +1.2.

**Strength:** weak. Even the best case, acceleration since 1970, has p ≈ 0.07–0.10 with 7 episodes, and 2007 dominates it (+18.8 pp acceleration). The result depends on 2007, with a smaller push from 1980–81.

**Per-crisis windows** (pp change in each bucket's share, t0 → +16):

| Peak | Δ public | Prior 16q | Pctile | Federal | GSE/agency | S&L | Banks/CUs | Private sec. | Other private | Public $ growth | Private $ growth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1953Q2 | −0.06 | — | 20% | −0.93 | +0.83 | +0.04 | +3.66 | 0.00 | −3.60 | +56% | +58% |
| 1957Q3 | +0.66 | +0.11 | 30% | +0.13 | +0.29 | +0.24 | +4.26 | 0.00 | −4.92 | +65% | +37% |
| 1960Q2 | −1.33 | +1.45 | 9% | −0.66 | −0.61 | −0.06 | +3.91 | 0.00 | −2.58 | −4% | +44% |
| 1969Q4 | +2.19 | +2.44 | 45% | −0.86 | +3.05 | 0.00 | +3.86 | +0.25 | −6.30 | +103% | +38% |
| 1973Q4 | +4.09 | +2.19 | 69% | +0.56 | +3.40 | +0.13 | +1.33 | −0.26 | −5.15 | +137% | +44% |
| 1980Q1 | +9.30 | +3.85 | 93% | +0.03 | +8.29 | +0.99 | −10.06 | −0.01 | +0.78 | +118% | +18% |
| 1981Q3 | +8.34 | +5.14 | 86% | −0.29 | +8.30 | +0.32 | −8.62 | +1.02 | −0.74 | +122% | +32% |
| 1990Q3 | +7.03 | +6.97 | 78% | −0.33 | +7.76 | −0.40 | −7.64 | +4.35 | −3.73 | +51% | +12% |
| 2001Q1 | −3.81 | −0.11 | 4% | −0.21 | −3.35 | −0.26 | −1.29 | +3.60 | +1.51 | +40% | +65% |
| 2007Q4 | **+13.11** | −5.66 | **98%** | +3.16 | +9.69 | +0.25 | +0.45 | −12.48 | −1.08 | +29% | **−25%** |
| 2019Q4 | +1.03 | +1.78 | 33% | −0.78 | +1.97 | −0.17 | −1.46 | −0.61 | +1.04 | +26% | +21% |

2007 is the only window in which privately held debt shrank in dollars.

**Structural periods** (Δ public, with the federal / GSE / S&L parts):

| Period | Δ public | Federal | GSE | S&L | What happened |
|---|---|---|---|---|---|
| 1952Q1–1969Q4 | +1.8 | −1.3 | +3.0 | +0.1 | |
| 1969Q4–1979Q4 | +8.7 | −0.3 | +8.5 | +0.5 | Ginnie Mae and Freddie Mac pools |
| 1979Q4–1989Q4 | **+19.0** | −0.6 | **+18.8** | +0.8 | |
| 1989Q4–1999Q4 | +8.4 | +0.4 | +8.6 | −0.7 | |
| 1999Q4–2007Q4 | **−5.0** | −0.1 | −4.4 | −0.5 | Private-label boom |
| 2007Q4–2012Q4 | **+14.3** | +4.2 | +9.8 | +0.3 | |
| 2012Q4–2019Q4 | +4.8 | +4.0 | +0.9 | −0.1 | Student loans on the federal book |
| 2019Q4–2026Q2 | +1.2 | −0.5 | +1.8 | −0.2 | |

- The largest *non-crisis* windows (more than 8 quarters from any peak) start in 1988Q2 (+8.7 pp), 2005Q3 (+8.5 pp, which runs into the GFC) and 1983Q4 (+8.2 pp).
- In 1980, 1981 and 1990 the share was already rising at the same slope for 8 quarters before the peak (`figures/q1_event_windows.png`).
- **The federal student-loan takeover is structural, not a crisis response.** In the 2007 window, federal direct holdings added +3.1 pp in student loans and only +0.08 pp in mortgages. The ECASLA (2008) purchases and SAFRA (2010) moved FFEL lending onto the federal book, and the federal share kept rising afterwards: +4.0 pp in 2012–19.
- Over the whole sample, 63% of the 53.2 pp rise happened inside crisis windows, which cover 54% of quarters: +0.21 pp per quarter inside vs +0.15 pp outside. Without the GFC window, the split is 50% of the rise in 52% of quarters.

Charts: `figures/ratchet.png`, `q1_forward_windows.png`, `q1_event_windows.png`, `q1_permutation.png`.

## 2. Decomposition
The public share can be written two ways:
- S = PM/T + PC/T: the public share of mortgages (PM) plus the public share of consumer credit (PC), both over the scope total T.
- S = w·p_m + (1−w)·p_c, where w is the mortgage weight and p_m, p_c are the public shares within each type.

The exact midpoint decomposition of the change is:
- **composition:** Δw·(p̄_m − p̄_c);
- **within mortgages:** w̄·Δp_m;
- **within consumer credit:** (1−w̄)·Δp_c.

| Window | ΔS | Mortgage part | Consumer-credit part | Composition | Within mortgages | Within CC |
|---|---|---|---|---|---|---|
| 1953Q2 | −0.06 | −0.06 | 0.00 | +0.15 | −0.21 | 0.00 |
| 1957Q3 | +0.66 | +0.66 | 0.00 | +0.12 | +0.54 | 0.00 |
| 1960Q2 | −1.33 | −1.33 | 0.00 | +0.02 | −1.35 | 0.00 |
| 1969Q4 | +2.19 | +2.19 | 0.00 | −0.17 | +2.36 | 0.00 |
| 1973Q4 | +4.09 | +4.03 | +0.06 | +0.41 | +3.62 | +0.06 |
| 1980Q1 | +9.30 | +9.17 | +0.13 | +0.17 | +8.99 | +0.13 |
| 1981Q3 | +8.34 | +8.33 | 0.00 | −0.54 | +8.90 | −0.02 |
| 1990Q3 | +7.03 | +6.84 | +0.19 | +0.65 | +6.15 | +0.22 |
| 2001Q1 | −3.81 | −3.15 | −0.67 | **+2.17** | −5.56 | −0.42 |
| 2007Q4 | +13.11 | +10.03 | **+3.08** | −0.89 | +11.17 | **+2.83** |
| 2019Q4 | +1.03 | +1.96 | −0.93 | +0.37 | +1.26 | −0.61 |
| 2020Q1 shock → 2024Q1 | +0.53 | +1.56 | −1.03 | +0.27 | +1.05 | −0.78 |
| 2023Q4 shock → 2026Q2 (10 quarters) | +0.13 | −0.16 | +0.29 | +0.31 | −0.73 | +0.55 |
| 2025Q2 shock → 2026Q2 (4 quarters) | −0.24 | −0.32 | +0.08 | +0.03 | −0.39 | +0.11 |

- Shifts among holders within mortgages dominate almost every window. Composition never exceeds 1 pp except in 2001, when the mortgage weight rose from 73.6% to 78.5%, and even then the private-label shift (−5.6 pp) overwhelmed it.
- Consumer credit matters only in 2007, when its public share went from 4.4% to 18.0%.
- In the 2019 and 2020 windows the consumer-credit part was negative, because student balances stalled during the payment pause.
- The policy shocks have moved the share by less than 0.6 pp so far.

## 3. FAS 166/167 (2010Q1)
- Sector 40 (FL403065105) rose **+$4,350.5B** in one quarter; its share of all 1-4 family mortgages went from 4.0% to 44.3%.
- Sector 41 (FL413065105) fell **−$4,339.6B**; its share went from 48.2% to 8.6%.
- **Combined, 40+41 changed by only +0.74 pp.** That is an ordinary quarter: from 2005 to 2015 the mean absolute quarterly change was 0.62 pp and the maximum 1.48 pp.

The `gse_agency` bucket sums sectors 40 and 41, so the public share is continuous through 2010. Never chart sector 40 or 41 alone across 2010.

The same standard pulled card-trust ABS back onto bank balance sheets:
- ABS issuers' consumer credit went from $572.5B to $59.0B.
- US-chartered depositories went from $906.3B to $1,227.2B.
- About 4 pp of scope debt moved from private securitization to banks. There is no public-share effect, but the step is visible in the bucket chart.

Chart: `figures/q3_fas167.png`.

## 4. Fed QE overlay
Fed MBS (WSHOMCB, last week of each quarter) as a share of scope debt:
- 2009Q1: 1.8%
- 2009Q4: 7.0%
- 2014Q4: 13.7%
- 2019Q4: 9.7%
- **2022Q1: 16.4%** ($2.72T)
- 2022Q2: 16.0%
- **2026Q2: 10.3%** ($1.96T)

The weekly maximum was $2,740B on 2022-04-13. On 2026-10-21 holdings were $1,895B (−$845B). At the peak the Fed held about 34% of the apportioned GSE/agency bucket; in 2026Q2 it held 22%.

**Phrasing:** the Fed's MBS are inside the public share, not on top of it. Agency MBS carry a guarantee from a GSE or Ginnie Mae, so default losses fall on Fannie Mae and Freddie Mac (in conservatorship, backstopped by the Treasury) or on FHA/VA, whoever holds the security. QE moved interest-rate and duration risk onto the central bank, not credit risk. Suggested copy: *"At its peak the Fed owned about one dollar in six of all household mortgage and consumer debt, as a bondholder exposed to interest rates, not as a lender exposed to defaults."*

## 5. Collateral lens
**Home coverage** = FL155035015 / FL153165105. The equity cushion is 1 − 1/coverage.

| Crisis | Peak | Trough | +16q | Window low | Cushion, peak → +16 |
|---|---|---|---|---|---|
| 1953Q2 | 4.93× | 4.61× | 3.96× | 3.96× | 80% → 75% |
| 1957Q3 | 3.93× | 3.78× | 3.35× | 3.35× | 75% → 70% |
| 1960Q2 | 3.54× | 3.37× | 2.92× | 2.92× | 72% → 66% |
| 1969Q4 | 2.99× | 3.06× | 3.27× | 2.99× | 67% → 70% |
| 1973Q4 | 3.27× | 3.11× | 3.13× | 2.99× | 70% → 68% |
| 1980Q1 | 3.16× | 3.22× | 3.34× | 3.16× | 68% → 70% |
| 1981Q3 | 3.30× | 3.34× | 3.34× | 3.26× | 70% → 70% |
| 1990Q3 | 2.92× | 2.82× | 2.66× | 2.66× | 66% → 62% |
| 2001Q1 | 2.77× | 2.76× | 2.62× | 2.57× | 64% → 62% |
| 2007Q4 | **2.20×** | **1.90× (2009Q2)** | **1.86×** | 1.86× (2011Q4) | **55% → 46%** |
| 2019Q4 | 2.75× | 2.86× | 3.43× | 2.75× | 64% → 71% |
| **2026Q2** | **3.56×** | | | | **72%** |

- The all-time low is **1.85× in 2012Q1**; the high is 5.17× in 1952Q2.
- The current 3.56× was last reached in 1960Q1. Between 1965 and 2021 the maximum was 3.41× (1983Q1), and this cycle peaked at 3.61× (2024Q2).
- Coverage had already slid from 2.54× in 2006Q1 to 2.20× at the 2007Q4 peak.
- This is an aggregate ratio and includes free-and-clear homes, so it hides underwater borrowers. In 2009–11 the aggregate cushion was still 46% while millions of borrowers had negative equity.

**Uncollateralized debt** (revolving FL153166100 + student FL153166220):
- **When the split starts:** revolving is populated from 1968Q1. Student loans only from 2006Q1; before that they sit inside "other non-revolving" (FL153166205). In 2006Q1 that series fell from $640.8B to $233.1B as $481.0B of student loans was carved out. **In the raw series the uncollateralized share jumps from 7.6% to 11.5% in 2006Q1 because of the data break.** The pipeline's `mart.collateral_coverage` removes the break by imputing student loans before 2006Q1 (a linear ramp from 1965Q4, never below known federal, Sallie Mae and nonprofit holdings), flagged `is_estimated`. It shows 11.45% → 11.46%. The figures in this section use the raw series.
- **A second break in 1977Q1:** revolving went from $17.2B to $31.4B while other non-revolving went from $145.0B to $128.9B, a reclassification. The revolving share moved from 2.3% to 4.1% in one quarter.
- **Reliability:** revolving is consistent from 1977Q1, student loans from 2006Q1. Before 2006 the uncollateralized share is a lower bound; federal student loans alone were $66.7B in 2001Q2 and $111.9B in 2007Q2. Before 1968 it is zero by construction.
- **Level:** 16.6% of scope debt now (6.9% cards, 9.7% student). The peak was 18.7% in 2019Q4. Revolving alone peaked at 10.9% in 1997Q4.

| Crisis | Uncollateralized share, peak → trough → +16 | Basis |
|---|---|---|
| 1969Q4 | 0.9% → 1.2% → 2.0% | revolving only |
| 1973Q4 | 2.0% → 2.1% → 4.5% | revolving only; includes the 1977Q1 break |
| 1980Q1 | 4.5% → 4.3% → 5.1% | revolving only |
| 1981Q3 | 4.4% → 4.9% → 5.9% | revolving only |
| 1990Q3 | 7.2% → 7.3% → 8.5% | revolving only |
| 2001Q1 | 10.5% → 10.2% → 7.7% | revolving only |
| 2007Q4 | 12.1% → 12.6% → **14.4%** | revolving + student (revolving alone 7.6% → 6.7%) |
| 2019Q4 | **18.7%** → 17.9% → 16.8% | revolving + student |

Card balances shrank relative to total debt in every crisis since 2001. The 2007 rise in uncollateralized debt is entirely student loans. 2020 is unusual: unsecured debt fell during a recession, because of stimulus payments and the student-loan payment pause.

**Vehicle proxy:** consumer durables at current cost (FL155111005) divided by auto loans (FL153166400). This overstates vehicle collateral because durables include furniture and electronics.
- Coverage fell from 14.5× (1953Q2) to 6.9× (1990Q3) and 5.6× (2007Q4), with a low of **4.77× in 2017Q3**. It is **5.79× now**.
- It rises in crises, when auto lending contracts.
- Its long decline means auto debt has outgrown the goods that could secure it.
- Auto loans are 8.3% of scope debt.

Charts: `figures/q5_collateral.png`, `figures/q5_vehicle_proxy.png`.

## 6. Linking the lenses: what did the public sector absorb?

| Window | Δ public holdings | Mortgages | Consumer credit | Student loans' share of public book, t0 → +16 |
|---|---|---|---|---|
| 1973Q4 | +$56.6B | +$56.0B | +$0.5B | 0.0% → 0.5% |
| 1980Q1 | +$204.3B | +$201.7B | +$2.6B | 1.0% → 1.2% |
| 1981Q3 | +$268.9B | +$266.8B | +$2.1B | 2.0% → 1.3% |
| 1990Q3 | +$570.6B | +$558.5B | +$12.1B | 1.6% → 1.8% |
| 2001Q1 | +$1,082.3B | +$1,094.9B | −$12.5B | 3.8% → 2.4% |
| 2007Q4 | +$1,395.7B | +$1,016.6B | **+$379.1B (27%)** | **2.4% → 8.0%** |
| 2019Q4 | +$2,081.2B | +$1,938.2B | +$142.9B (7%) | 16.4% → 14.4% |

- Until 2007, about 98% or more of each window's public increase was home-backed agency debt.
- In 2007–11, 27% of the increase was unsecured student debt. The student share of the public book went from 2.4% (2007Q4) to 8.0% (2011Q4), peaked at 16.6% (2020Q1), and is 14.9% now.
- Today the public book is $9.16T of mortgages plus $1.61T of student loans.
- The public sector holds 65.6% of household mortgages, 86.4% of student loans (19.6% in 2007Q4), and 50.7% of all uncollateralized household debt (7.3% in 2007Q4).
- The ratchet that did happen moved two kinds of risk onto the public sector:
  - mostly well-collateralized mortgage risk, now covered 3.6× in aggregate;
  - a growing slice of uncollateralized student debt. That debt is hard to discharge in bankruptcy and can be collected through wage and benefit offsets: its credit risk is high, but its recovery tools are strong.

Chart: `figures/q6_public_book.png`.

## 7. Now (2026Q2)
**Z.1:**
- Scope debt is **$19.10T**: $13.98T mortgages plus $5.12T consumer credit. That is **+$198.5B on the quarter** (not seasonally adjusted) and +2.9% year on year.
- Public share is **56.4%**: 56.6% last quarter, −0.2 pp year on year, and 2.2 pp below the 2021Q1 peak. Mortgages are 65.6% public and consumer credit 31.3%.
- Home coverage is **3.56×** (72% equity), against 3.52× last quarter and 3.58× a year ago. The Case-Shiller index is up 1.6% year on year.
- The uncollateralized share is **16.6%** (16.5% a year ago).
- Scope debt is **0.80× disposable income**, against **1.24× at the 2007Q4 peak**. In real terms it is **8.5% below 2007Q4**. Unemployment averaged 4.27%.
- Fed MBS are 10.3% of scope debt, or $1.90T on 2026-10-21.

**NY Fed Household Debt and Credit, 2026Q2** (loaded into `mart.nyfed_by_type`). Total debt was **$18.77T**, the **first quarterly decline since 2020**, with **mortgages −$74B**. Student-loan delinquency is **distorted by re-reporting** of defaulted loans.

**Discrepancy:** Z.1 does **not** show a decline. Household mortgages *rose* $150.4B and scope debt rose $198.5B (not seasonally adjusted). The two sources differ:
- **Coverage:** Z.1 includes nonprofits and is built from lender balance sheets. The NY Fed CCP is a 5% sample of credit reports and separates out HELOCs.
- **Timing and revisions** also differ.

**Do not put "first decline since 2020" next to Z.1 numbers.** Attribute it to the NY Fed explicitly.

**What the two lenses say about today:**
- **Who holds the debt has plateaued.** The public share has stayed between 55% and 59% since 2019. None of the 2020Q1, 2023Q4 or 2025Q2 shocks moved it by more than 1 pp.
- **Mortgage collateral is strong.** Coverage has not been this high outside 2022–26 since 1960.
- **The fragile part is uncollateralized student debt, and the federal government already holds 86% of it.** The next losses there land on the Treasury.
- **Private-sector stress shows in cards and autos.** Auto coverage on the durables proxy (5.8×) is far below its 1990 level of 6.9×.

## Caveats and limitations
1. **Holder ≠ credit-risk bearer.** FFEL student loans held by banks and ABS before 2010 carried a 97–98% federal guarantee, and FHA/VA loans in bank portfolios are federally insured. So the 2010 student "takeover" overstates the shift in credit risk. In the other direction, GSE credit-risk-transfer deals since 2013 and private mortgage insurance shift part of the GSE risk to private parties.
2. **Households include nonprofits** (Z.1 sector 15). FL163066223 (nonprofit student loans) is a holder.
3. **Scope excludes other liabilities**, about 13% of household liabilities: 1 − 87.3% of $21.88T in 2026Q2. Excluded are commercial mortgages, security credit, trade payables, other loans and deferred premiums.
4. **Apportioning** applies holder shares measured over *all* 1-4 family mortgages (FL893065105, which includes business borrowers) to household mortgages. That assumes both have the same holder mix.
5. **Collateral proxies.**
   - Home coverage is aggregate and includes unmortgaged homes.
   - Vehicle coverage uses all consumer durables, which overstates vehicle collateral severalfold.
   - "Other non-revolving" (2.0% of scope debt) is mixed or unknown.
6. **Type-split breaks:** revolving starts in 1968Q1 and is reclassified in 1977Q1; student loans are split out only from 2006Q1. Uncollateralized shares before 2006 are lower bounds in the raw series and imputed in the mart.
7. **Accounting breaks:** FAS 166/167 (2010Q1) moved GSE MBS from sector 41 to sector 40, which nets out within the bucket. It also moved card ABS onto banks (about 4 pp).
8. **BNPL "phantom debt" is invisible.** Buy-now-pay-later balances are not reported to credit bureaus and have no separate Z.1 line, so unsecured debt is understated by an unknown amount.
9. **Revisions.** Z.1 revises history every quarter. These figures are from the 2026Q2-release vintage. Re-run `notebook.py` after each release; figures may move in the third decimal.
10. **Statistics.** The windows overlap (1980Q1 and 1981Q3), the series is trending and autocorrelated, and there are only 11 episodes (7 since 1970). Treat the p-values as descriptive.
11. **Crisis dating.** Windows start at the NBER peak. Starting at the trough instead removes any crisis effect (−0.4 pp vs other windows).
