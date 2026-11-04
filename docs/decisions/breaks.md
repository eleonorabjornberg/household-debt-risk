> **Claude draft, not the author's text.** Claude drafted the options. Eleonora chose them on 2026-11-04 by accepting every recommended option; each choice carries a **Decided** line. The wording is still Claude's.

# Pre-registration: A4, structural breaks in the public share of household debt
Status: decided by Eleonora 2026-11-04; frozen in commit `prereg: A4 (frozen)` (hash recorded in PLAN.md and the build log). No break test, fitted model or break-date search had been run on the target series when it was frozen.

How to read this file: each `CHOICE:` line lists the options considered, one marked "(Claude recommends)"; the **Decided** line under it is Eleonora's pick. Any change after freezing goes under "Deviations" at the end, dated, with a reason. Fact checks behind the edits made just before freezing: [`prereg-fact-checks.md`](prereg-fact-checks.md).

## Question
Did the public share of US household mortgage and consumer debt change course at known policy dates? Does the data, left to itself, put breaks anywhere else?

Context: `analysis/findings.md` (ratchet test) found that crisis windows as a group do not beat ordinary 16-quarter windows (11 NBER-peak windows; random placebo sets of 11 dates do as well about 30% of the time). Only 2007–11 stands out. That test used fixed windows around recession peaks. A4 asks a different question: are there breaks in the series itself, and do they line up with legislation?

## Hypotheses
- **H1 (any break).** The series has at least one structural break over the sample. Support: Bai-Perron UDmax/WDmax rejects "no break" at 5%. Null: it does not.
- **H2 (known dates).** There is a break at each pre-named date D (list below). Support: the decision rule for "confirmed" is met. Null: "not confirmed at D". Against: a break is found, but its confidence interval excludes D.
- **H3 (dates are special).** Known dates show breaks more often than random dates would. Support: the known-date statistics rank high against a placebo of all admissible dates. Null: they do not. This mirrors the findings placebo.

## Data
- Source: Federal Reserve Z.1 Financial Accounts, release of 2026-09-11. Quarterly, end-of-quarter stocks, 1952Q1–2026Q2 (298 quarters; 297 first differences, 1952Q2–2026Q2).
- Series as computed in `validation/run.py` `compute()`, independently of the pipeline:
  - Total share = (public mortgages + public consumer credit) / FL154104015.
  - Mortgage share = public mortgages / FL153165105. Public mortgages are an **apportionment** (an estimate): each public holder's share of FL893065105, times FL153165105.
  - Consumer-credit share = public consumer-credit holders / FL153166000.
  - "Public" = risk buckets `federal_direct`, `gse_agency`, `state_local` (`pipeline/series_catalog.yaml`).
- A ratio of two nominal stocks has no price level in it. No deflation is needed.
- Known **measurement** breaks (`validation/REPORT.md` E1–E3, `research/a1_gfc_decomposition/sources.md`): 1968Q1 revolving credit starts; 1977Q1 revolving reclassification; 2006Q1 student loans split out; 2010Q1 FAS 166/167 consolidation ("almost all … occurred in the first quarter of 2010", Z.1 of 10 June 2010). The validation suite sums sectors 40+41 so the public share is meant to be continuous through 2010. These four quarters are definitional, not policy. A break there must not be read as a policy effect.

`CHOICE: target series.`
(a) Total share only. One series, fewest tests, matches the headline. Hides offsetting moves in mortgages and consumer credit.
(b) Total share as primary; mortgage and consumer-credit shares as secondary, reported descriptively. (Claude recommends) One confirmatory family keeps the test count small; the split shows which book moved.
(c) All three as co-primary. Most informative, but triples the tests and the multiple-testing burden.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: trend and unit root.` The share is bounded, persistent and trending. Bai-Perron assumes stable regimes with stationary errors; a level series with a near unit root gives spurious "breaks".
(a) First differences (quarterly change, pp) with a mean-shift model. A break = a change in the speed of growth. Fits Bai-Perron's assumptions. A one-off step in the level shows up as a single-quarter pulse, which this model will not flag as a break. (Claude recommends) It is the version whose test theory holds; level steps are covered by the next choice.
(b) Levels with a linear trend, breaks allowed in intercept and slope (Perron-style). Sees steps directly. Inference is fragile if errors are close to I(1).
(c) Both, (a) primary and (b) sensitivity, plus ADF/KPSS/Zivot-Andrews reported as diagnostics only. They do not pick the specification, so the choice stays fixed in advance.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: what counts as a break at a known date.`
(a) Slope only (mean shift in the change).
(b) Slope, plus a level step judged descriptively: the size of the one-quarter change at D against the validation suite's robust-z rule (|z| > 6 and at least 1 pp). (Claude recommends) Policy can act as a jump or a new pace; this covers both without a weak one-observation test.
(c) Slope and step, both tested formally (step as a pulse dummy). Formal, but a one-observation test leans on normality the data may not have.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: bounded share.` (a) Raw share in pp. (Claude recommends) Readable; the share stays well inside 0–1 over most of the sample. (b) Logit of the share, as a sensitivity. Respects the bounds; harder to read.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

## Candidate known dates
Only dates verified against a primary source in `research/a1_gfc_decomposition/sources.md` may be used now. All other statutes are listed by name only and are **to verify in A3 with a primary source**; none enters the test until it has a sources.md row.

Verified (A1):
| Event | Verified date | Quarter (quarter that contains the date) |
|---|---|---|
| Economic Stimulus Act of 2008 (GSE and FHA loan limits) | approved 13 Feb 2008 | 2008Q1 |
| ECASLA (Education Dept. may buy student loans) | approved 7 May 2008 | 2008Q2 |
| HERA (FHFA created; Treasury purchase authority) | approved 30 Jul 2008 | 2008Q3 |
| Fannie Mae and Freddie Mac conservatorship | 6 Sep 2008 (PSPAs 7 Sep) | 2008Q3 |
| ARRA (2009 FHA and GSE loan limits) | approved 17 Feb 2009 | 2009Q1 |
| SAFRA (end of new FFEL loans) | approved 30 Mar 2010; no new FFEL first disbursed after 30 Jun 2010 | 2010Q1 approved; 2010Q3 effective |
| FAS 166/167 (measurement, not policy) | consolidations mostly in 2010Q1 | 2010Q1 |

To verify in A3 (inside the 1952–2026 sample, named only, no dates assumed): Housing and Urban Development Act of 1968 (Fannie Mae split, Ginnie Mae); Emergency Home Finance Act of 1970 (Freddie Mac); Higher Education Act of 1965 (guaranteed student loans); FIRREA (1989); the 1992 GSE act (FHEFSSA); the Student Loan Reform Act of 1993 (Direct Loans). Pre-1952 dates (HOLC, FHA, Fannie Mae's founding) fall outside this sample.

Enactment dates for these six have since been checked against the Statutes at Large on GovInfo (`prereg-fact-checks.md` §2): HEA 8 Nov 1965; HUD Act 1 Aug 1968; EHFA 24 Jul 1970; FIRREA 9 Aug 1989; FHEFSSA (Title XIII of Pub. L. 102-550) 28 Oct 1992; Student Loan Reform Act (Title IV-A of Pub. L. 103-66) 10 Aug 1993. Effective dates were not checked. Under the decision below they still do not enter the test: they can be added only through a dated A3 addendum that gives each a sources.md row and maps it with the date rule below.

Two confounds are visible before any test. HERA and the conservatorship fall in the same quarter (2008Q3). SAFRA's approval falls in the same quarter as the FAS 166/167 consolidation (2010Q1). Neither pair can be separated with quarterly data.

`CHOICE: which dates enter the Chow tests.`
(a) Two: 2008Q3 (HERA + conservatorship) and 2010Q3 (SAFRA effective). Fewest tests; the two largest verified steps; avoids the 2010Q1 measurement confound.
(b) All verified policy quarters: 2008Q1, 2008Q2, 2008Q3, 2009Q1, 2010Q3 (five). (Claude recommends) Uses everything verified, still a small family, and keeps 2010Q1 out as a measurement quarter. Five dates inside nine quarters cannot all be told apart; the write-up must say so.
(c) Option (b) plus the A3 statutes once verified. Covers the whole history; must wait for A3 and needs a heavier correction.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: date-to-quarter mapping.` Z.1 stocks are end-of-quarter, so an event is first visible in the stock of the quarter that contains it.
(a) Quarter containing the signing/action date, for all events. Simple and mechanical.
(b) Quarter containing the effective date, where the statute sets one (SAFRA: 2010Q3); otherwise the signing quarter. (Claude recommends) Stocks move when lending rules change, not when a bill is signed; one rule, applied the same way to every date.
(c) Both, reported side by side. Doubles the tests at dates where they differ.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

## Method
Python implementation (new code under `research/`), cross-checked in R `strucchange`. R is not installed here and CRAN is not reachable from this environment (`prereg-fact-checks.md` §4), so the cross-check has to run in another environment. Until it has run, no break can be "confirmed" (decision rule, leg 3).

**Chow (known dates).** Wald test of a mean shift in the first difference at D, using a HAC covariance. One test per pre-named date.

**Bai-Perron (unknown dates).** Global minimisation of the sum of squared residuals by dynamic programming. Report UDmax/WDmax, sequential sup-F(l+1|l), BIC, break dates, and Bai (1997) 95% confidence intervals for each date.

`CHOICE: maximum number of breaks.` (a) 3. (b) 5. (Claude recommends) Bai-Perron's usual default; enough for the 1980s build-out and 2008 without fishing. (c) 8. Lets the data speak; more spurious breaks and wider intervals.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: trimming ε (minimum regime length).` With 297 quarters:
(a) ε = 0.15 (45 quarters, about 11 years). Bai-Perron's recommended value when errors are serially correlated. Cannot find two breaks within 2008–10.
(b) ε = 0.10 (30 quarters). (Claude recommends) A middle ground; still guards size under HAC, and regimes of 7.5 years are plausible for policy.
(c) ε = 0.05 (15 quarters). Can separate close breaks; known size distortions with HAC.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: how the number of breaks is chosen.`
(a) Sequential sup-F(l+1|l) at 5%, after UDmax/WDmax rejects zero breaks. (Claude recommends) Bai and Perron's own advice; robust to serial correlation.
(b) BIC, the rule `strucchange::breakpoints()` uses to pick the number of breaks. Matches R out of the box; its own man page cites Perron (2003): BIC has problems in dynamic regressions.
(c) LWZ. More conservative than BIC; less familiar to readers.
Whichever is chosen, the other two are reported alongside.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

`CHOICE: HAC covariance and error assumptions.`
(a) Quadratic Spectral kernel, Andrews (1991) AR(1) automatic bandwidth, AR(1) prewhitening; error variance allowed to differ across regimes. (Claude recommends) The Bai-Perron (2003) setup; quarterly changes are clearly not independent.
(b) Bartlett (Newey-West) kernel, fixed bandwidth floor(4(T/100)^(2/9)). Common and easy to match in R; less efficient.
(c) As (a), but errors homogeneous across regimes. Fewer parameters; wrong if volatility rose after 2008.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).
In R this is `sandwich::kernHAC` with its defaults (Quadratic Spectral kernel, Andrews bandwidth, VAR(1) prewhitening).

`CHOICE: agreement with R strucchange.`
(a) Strict: same break dates, same SSR (relative difference < 1e-6), test statistics within 1%, CIs equal to the quarter.
(b) Dates and SSR exact; test statistics within 5%; CI bounds within one quarter. (Claude recommends) The dynamic programme is deterministic and must match exactly; HAC and CI code differ in small details between packages.
(c) Dates within one quarter. Too loose to catch a real bug.
Any disagreement beyond tolerance stops the task until explained. Where `strucchange` cannot apply the same HAC setting, compare the parts it can and say which parts were not cross-checked.
What R can check (from the package man pages, `prereg-fact-checks.md` §4): break dates and SSR/BIC from `breakpoints()`, which has no HAC option; HAC Chow and sup-F through `Fstats(..., vcov. = kernHAC)`; break-date CIs through `confint(..., vcov. = kernHAC)`. Sequential sup-F(l+1|l) and UDmax/WDmax are not in `breakpoints()`, so the chosen selection rule is not cross-checked in R, and the report says so.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

## Benchmarks and placebo
No holdout: break tests are in-sample. The placebo is the benchmark. Run the same Chow test at every admissible quarter (inside the trimming bounds), excluding the four measurement quarters. For each known date, report the share of placebo dates with a larger statistic. This answers H3: is the date special, or does a persistent series reject almost everywhere?

## Multiple testing
`CHOICE: correction.`
(a) Holm-Bonferroni across the Chow tests on the primary series at 5% family-wise. (Claude recommends) Few dates, so the cost in power is small, and it is the honest standard for "confirmed".
(b) Bonferroni. Simpler; more conservative than Holm for the same guarantee.
(c) No correction; all tests framed as descriptive. Fine only if no sentence says "confirmed".
Bai-Perron's sup tests already allow for the search over dates. Secondary series are descriptive in every option.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

## Vintages
- Primary: Z.1 release of 2026-09-11, fixed. Every result records the vintage and the frozen file's commit hash.
- Revision sensitivity: rerun everything on the June 2026 vintage (released 2026-06-11; ends 2026Q1). The validation suite already loads it. Any change in a confirmed / not-confirmed verdict, or a break date that moves, is reported as "vintage-sensitive".

`CHOICE: sample end for the June comparison.` (a) Each vintage on its own full sample. (b) Both cut to 2026Q1, so only revisions differ. (Claude recommends) Isolates revisions from one extra quarter.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

## Decision rules
`CHOICE: what "confirmed break at a known date" requires.`
(a) All four: Chow rejects after correction; a Bai-Perron break's 95% CI contains D's quarter; Python and R agree within tolerance; the verdict holds on the June vintage. (Claude recommends) Each leg guards against a different failure: a persistent series, a wrong date, a code bug, a revision.
(b) Chow after correction, plus the Bai-Perron CI condition. Lighter; robustness legs reported but not required.
(c) Chow after correction only. Easiest to meet; says nothing about whether the data would pick the date unaided.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

Sentences tied to outcomes:
- All required legs met: "The data confirm a break at D (quarter, 95% CI)."
- Chow rejects but no Bai-Perron CI covers D, or the reverse: "Consistent with a break near D, not confirmed."
- Neither: "No evidence of a break at D." Never "the policy had no effect".
- Bai-Perron break at an unlisted quarter: reported with its CI as "a break the pre-named dates do not explain". It is not attributed after the fact. Any later attribution needs a verified source and is labelled exploratory.
- Break at a measurement quarter (1968Q1, 1977Q1, 2006Q1, 2010Q1): "coincides with a definitional change", not policy.

## What is and is not identified
- A break is timing, not cause. A confirmed break at D says the series changed course near D. It does not say the statute caused it. Causal attribution is A7 (event study, synthetic control).
- The share is a ratio. A1 found that half of the 2007–11 rise was private debt shrinking. A break can come from the denominator.
- Events in the same quarter (2008Q3; 2010Q1) cannot be separated.
- The mortgage public share uses an apportionment estimate; breaks in it inherit that.

## Dependence on A3
A4 depends on A3 (pre-1952 history), which is not done.

`CHOICE: timing relative to A3.`
(a) Run A4 now on 1952Q1–2026Q2 quarterly with the A1-verified dates; add A3 as a separate pre-registered addendum later. (Claude recommends) Unblocks Phase A; the post-war quarterly series is the one the project publishes.
(b) Wait for A3, then run once on the full history. One analysis, but delayed, and it mixes annual and quarterly data.
(c) Run now, and treat A3 as a robustness extension only, not a new hypothesis.
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

What A3 would add: annual Z.1 for 1945–51 and earlier historical sources, so the New Deal dates (HOLC 1933, FHA 1934, Fannie Mae 1938) become testable; verified dates for the post-1952 statutes listed above; a longer pre-sample. Limits: annual frequency needs its own break test (fewer observations, different trimming); spliced pre-1945 points carry source and reliability labels and may not support formal inference.

## Deviations (dated, after freezing)

### 2026-11-04: simulated critical values (analysis track, before the first run)
The Bai-Perron (2003) tables are not reachable from this environment, so the 5% critical values of sup-F(k), UDmax, WDmax and sup-F(l+1|l) are simulated under the null (i.i.d. normal, T = 600, 2,000 replications, fixed seed; sup-F(l+1|l) as the 0.95^(1/(l+1)) quantile of sup-F(1)). Declared in `research/a4_breaks/breaks.py` before the first run (commit eed0ce7). No decision in the results is close to a critical value.

### 2026-11-04: break-date interval corrected (analysis track, after the first run)
The first run computed the Bai (1997) interval with the simulated quantiles added instead of subtracted, which is wrong whenever the regimes' long-run variances differ. Found by the quant-reviewer (`claims/review-log.md`, R-20261104-ana-35). Bug fix only: no choice above changed, and no H2 verdict changed. The 1966Q1 interval moved from 1965Q1–1997Q4 to 1952Q2–1967Q1.
