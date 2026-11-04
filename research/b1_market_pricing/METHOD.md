# B1 method note (written before any regression was run)

> **Claude draft, not the author's text.** A proposed specification for Eleonora to accept, change or replace. Committed before the regressions were run, so later results can be checked against it. Changes after results exist are listed at the bottom with their reason.

Date: 2026-11-04. PLAN task B1: "Market-implied credit risk: mortgage-rate spread over Treasuries; agency vs private-label. Did the shift compress the price of household credit risk?"

## What can and cannot be measured with free data

| Wanted | Free? | Used here |
|---|---|---|
| Agency MBS option-adjusted spread (OAS) | No (Bloomberg, ICE, Yield Book) | Not used |
| Private-label RMBS spreads | No (Intex, dealer runs) | Not used |
| Primary 30-year fixed mortgage rate | Yes: Freddie Mac PMMS via FRED `MORTGAGE30US`, weekly, 1971+ | Proxy S1 |
| Treasury yields | Yes: FRED `DGS10`, `DGS5`, `T10Y2Y`, daily | Benchmarks and controls |
| Jumbo vs conforming 30-year rate | Yes, 2017+ only: Optimal Blue via FRED `OBMMIJUMBO30YF`, `OBMMIC30YF`, `OBMMIFHA30YF` | Proxy S2 (descriptive) |
| Jumbo vs conforming before 2017 | FHFA MIRS (discontinued 2019) publishes non-jumbo only by month (Table 26); jumbo cannot be separated without assumptions | Not used |
| General corporate credit spread | Yes: FRED `BAA10Y` (Moody's), 1986+ | Control |

## Proxies and their limits

**S1 = PMMS 30-year rate − 10-year Treasury yield** (quarterly means, percentage points). Not a credit spread. It bundles: (a) the GSE guarantee fee, which is set administratively by Fannie, Freddie and FHFA, not by a market; (b) the value of the borrower's prepayment option; (c) servicing and the primary–secondary (originator) spread; (d) the agency MBS spread to Treasuries (liquidity, convexity). PMMS covers conforming, mostly GSE-eligible loans, so for most of the sample the credit risk in S1 is priced by a public guarantor. Freddie Mac changed the PMMS method on 2022-11-17 (from a lender survey to applications data; FRED series notes), a level break risk. The 10-year Treasury is a duration-matching convention, not exact; a 5y/10y average is a robustness check.

**S2 = jumbo − conforming 30-year rate** (Optimal Blue locked rates, 2017+). Jumbo loans exceed the conforming limit and cannot be sold to the GSEs, so lenders keep the credit risk (since 2008 mostly on bank balance sheets; private-label jumbo issuance is small). S2 is therefore "price of credit risk held privately, minus price when the GSEs guarantee it", plus liquidity and borrower-mix differences (jumbo borrowers have higher incomes and FICO scores, which pushes S2 down). Ten years of data with a public share that barely moves: descriptive only, no regression. FHA − conforming is reported alongside as the price spread between the two public channels.

## Regression (association, not causal)

Quarterly, 1986Q1 (first `BAA10Y` quarter) to the latest Z.1 quarter.

    S1_t = a + b · public_share_t + c1 · DGS10_t + c2 · vol10_t + c3 · slope_t + c4 · BAA10Y_t + c5 · refi_t + e_t

- `public_share_t`: public share of household 1–4 family mortgages, quarter end, Z.1 (public = federal direct + GSE and agency pools + state and local, apportioned exactly as `validation/run.py` and A1 do). Mortgage-only, because S1 is a mortgage price. Robustness: the project's headline share (mortgages + consumer credit).
- `DGS10_t`: quarterly mean of the 10-year yield (rate level).
- `vol10_t`: standard deviation of daily changes in `DGS10` within the quarter, in percentage points, times √252 (realized rate volatility; a free stand-in for the paywalled MOVE index and for the value of the prepayment option).
- `slope_t`: quarterly mean of `T10Y2Y`.
- `BAA10Y_t`: quarterly mean (general price of corporate credit risk).
- `refi_t`: `DGS10_t` minus its trailing 20-quarter mean (prepayment-option moneyness proxy; built from Treasuries, not PMMS, so it is not mechanically tied to S1).
- Standard errors: Newey–West HAC, Bartlett kernel, lag L = floor(4·(T/100)^(2/9)).

**Specifications, all reported:**
1. L: levels, as above.
2. D: first differences of every variable (guards against a spurious levels fit; the public share is very persistent).
3. L and D with the headline share in place of the mortgage share.
4. L and D with S1 measured against the mean of `DGS5` and `DGS10`.
5. L and D ending 2022Q3 (before the PMMS method change).

Diagnostics: Engle–Granger-style ADF statistic on the L residuals (no lag selection: ADF with 4 lags, constant), reported, not used to choose a specification.

**Reading rule, fixed now:** "compression" means b < 0 with the 95% HAC interval excluding zero in both L and D. If L and D disagree in sign or significance, the result is reported as "no robust association". No specification is dropped for its result.

## Point-in-time

B1 is descriptive, so it uses the latest vintage of every series (Z.1 of 2026-09-11; FRED as retrieved). Vintages are recorded in `results.json`. Real-time data are a C1 matter.

## Changes after results
2026-11-04, after the first results and the quant-reviewer and skeptic reviews (`claims/review-log.md`, R-20261104-mkt-q1 to q5 and s1 to s8). Nothing above was changed. Three **post-hoc** checks were added. They are reported in `regressions.csv` under variants starting "post-hoc:", and the reading rule is not applied to them:
- the main specification with HAC lag 8 (q1: lag sensitivity);
- the main specification with a Fannie Mae + Freddie Mac share in place of the full mortgage public share, because PMMS prices conforming loans and the full share also counts Ginnie Mae pools of FHA/VA loans (s2);
- the main specification with a dummy for 2022Q4 onward, the quarters after the PMMS method change (q2, s1).
The README now also reports the residual ADF statistics next to Engle–Granger 5% critical values (q1).
