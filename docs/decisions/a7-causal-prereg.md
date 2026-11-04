# Pre-registration: A7, causal evidence around the 2008 GSE conservatorship and the 2010 student-loan takeover (SAFRA)

> **Claude draft, not the author's text.** Claude drafted the options. Eleonora chose them on 2026-11-04 by accepting every recommended option; each choice carries a **Decided** line. The wording is still Claude's.

Status: decided by Eleonora 2026-11-04; frozen in commit `prereg: A7 (frozen)` (hash recorded in PLAN.md and the build log). One precondition remains open (checklist item 3 at the end): it must be met in a dated addendum before any outcome is inspected. When frozen, no A7 result existed: there is no `research/a7_*` folder, no A7 row in `claims/register.csv` and no A7 entry in the session log. No regression, fit or donor outcome path was computed or looked at to write this.

Depends on: A1 (done), B1 (spreads, in progress on `claude/track-markets`), and A5 (state panel) or A8 (international panel), both in progress on `claude/track-analysis`. Each design below says which of these it needs. Nothing here assumes data that is not yet in the repo.

## Question

Did the two federal actions change who bears US household credit risk, or its price, beyond what would have happened anyway?

- **Event G (GSEs).** FHFA placed Fannie Mae and Freddie Mac in conservatorship on 6 Sep 2008; Treasury's preferred-stock agreements were signed on 7 Sep 2008 (FHFA, `research/a1_gfc_decomposition/sources.md`).
- **Event S (student loans).** SAFRA (P.L. 111-152, Sec. 2201), approved 30 Mar 2010: no new FFEL loans first disbursed after 30 Jun 2010 (GovInfo, same file).

### What A1 implies for the framing

A1 (Shapley split, `research/a1_gfc_decomposition/README.md`) found that the largest public piece of the 2007–11 rise was Ginnie Mae pools (FHA, VA, USDA loans), not Fannie and Freddie. Fannie and Freddie had contributed 1.1 pp by 2008Q2, the last quarter-end before the conservatorship; they peaked at 2.3 pp in 2009Q4 and fell back after that. Their balances grew $278B over the window. A1 counts the GSEs as public at every date, so it cannot say whether the conservatorship changed how much they held; that is a question for this file.

So conservatorship is a weak candidate treatment for the public *holdings share*. It is a stronger candidate for *price* (if investors saw GSE debt as closer to Treasury-backed) and for *private-label volume* (if a backed competitor crowds it out).

CHOICE 1 (what Event G is a treatment for):
- (a) Public holdings share (Z.1, quarterly). Directly the project's headline series. But A1 suggests little to find, and a null would be expected by construction.
- (b) Pricing: mortgage spread over Treasuries from B1 (Claude recommends). The event changed backing, and price is where backing should show. Weekly data allow narrow windows. Needs B1 first.
- (c) Both, with (b) primary and (a) secondary and descriptive. Most complete, but more tests (see Multiple testing).
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

## Hypotheses

Each hypothesis states support, null and against in advance.

- **H1 (G, pricing).** The mortgage spread (B1 proxy, e.g. PMMS 30-year minus a Treasury yield) fell in the window after 6–7 Sep 2008, relative to its pre-event behaviour. Support: abnormal change negative and outside the placebo-in-time distribution at the chosen level. Null: inside it. Against: positive and outside it.
- **H2 (G, private-label crowding out).** Private-label securitization holdings (Z.1 `FL673065105`, and mortgage REITs `FL643065173`) fell more after 2008Q3 than the synthetic or pre-trend counterfactual. Support / null / against as for H1, using the RMSPE-ratio rank.
- **H3 (G, public share).** The public share rose more after 2008Q3 than the counterfactual. Given A1, a null here is the expected result and will be reported as such.
- **H4 (S, student loans).** See the student-loan section; the outcome is itself a choice.

## Data

| Outcome | Series | Frequency, start | Status |
|---|---|---|---|
| Public share, holder lines | Z.1 holder series in `pipeline/series_catalog.yaml` | Quarterly | In repo (vintage 2026-09-11) |
| Private-label holdings | `FL673065105`, `FL643065173` | Quarterly | In repo. FAS 166/167 moved card ABS in 2010Q1 (A1 limits), so mortgage lines only |
| Mortgage spread | B1 proxies (PMMS, Treasury yields) | Weekly | Not in repo yet; from B1 |
| Student loans by holder | `FL313066220` (federal), bank, ABS, finance-company, nonprofit lines | Quarterly, **only from 2006Q1** (`analysis/findings.md`) | In repo |
| Fed MBS holdings (control, not outcome) | FRED `WSHOMCB` | Weekly | In catalog |
| Donor panels | A5 (states) or A8 (countries) | To be stated in their availability notes | Not in repo yet |

Vintages: Z.1 2026-09-11 for all Z.1 series; ALFRED vintages are not needed because nothing is forecast, but the vintage is recorded in every result. Exclusions: any quarter or donor named in the decision rules below.

## Overlapping events

The verified dates (A1 `sources.md`): Economic Stimulus Act 13 Feb 2008 (loan limits); ECASLA 7 May 2008 (Treasury authority to buy FFEL loans); HERA 30 Jul 2008; conservatorship 6–7 Sep 2008; ARRA 17 Feb 2009 (loan limits); FAS 166/167 effective in Z.1 almost all in 2010Q1; SAFRA approved 30 Mar 2010, effective for loans first disbursed after 30 Jun 2010.

**Verified 2026-11-04** (`prereg-fact-checks.md` §1, federalreserve.gov): the Fed's agency-MBS purchase programme was announced 25 Nov 2008 (2008Q4); purchases began 5 Jan 2009 (H.4.1 of 15 Jan 2009); it was expanded to up to $1.25 trillion on 18 Mar 2009. `WSHOMCB` first shows holdings on 14 Jan 2009, a settlement date, so it dates settlement, not the first purchase. These rows go into the A7 `sources.md` when the folder is created.

Consequences:
- **HERA and conservatorship fall in the same quarter (2008Q3).** Quarterly Z.1 data cannot separate them. Only weekly spreads can.
- **SAFRA's enactment (2010Q1) falls in the same quarter as FAS 166/167.** Its effective date (1 Jul 2010) is 2010Q3.
- **ECASLA (2008Q2) already moved FFEL loans to the federal book**, two years before SAFRA. The student-loan pre-period is short and partly treated.

CHOICE 2 (how to handle overlapping 2008–09 events):
- (a) One bundled "federal backstop" episode, HERA to ARRA (30 Jul 2008 – 17 Feb 2009). Honest about what quarterly data can see. But the answer is about the bundle, not conservatorship.
- (b) Separate narrow windows per event, weekly spreads only, with a dummy for each other event in the window (Claude recommends for H1). Isolates conservatorship as far as free data allow. Still cannot remove news that leaked before the weekend of 6–7 Sep.
- (c) Both: (b) for pricing, (a) for quarterly holdings (H2, H3). Matches each outcome to what its frequency can resolve; more tests.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

## Method

### Event study (H1; also usable for H2–H4 as an interrupted time series)

CHOICE 3 (event window, weekly spreads):
- (a) [−1, +1] weeks. Least contamination from other news. One PMMS observation each side is noisy.
- (b) [−1, +4] weeks (Claude recommends). Allows for slow pass-through to quoted mortgage rates and still ends before the Fed MBS announcement (25 Nov 2008, verified; the window ends in early October). Some other September–October 2008 news falls inside.
- (c) [−4, +12] weeks. Captures the full adjustment. Overlaps the Fed programme and the wider crisis, so it is hard to attribute.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

CHOICE 4 (estimation window for "normal" spread behaviour):
- (a) 52 weeks ending the week before the Economic Stimulus Act (13 Feb 2008). Clean of 2008 housing laws. Includes the 2007 credit turmoil, so "normal" is already stressed.
- (b) 104 weeks ending the week before HERA (30 Jul 2008) (Claude recommends). Longer, so the variance estimate is steadier; contains ESA and ECASLA, which are dummied out.
- (c) Several pre-crisis years (e.g. ending 2006). Calm baseline, but that makes 2008 look abnormal for reasons unrelated to the event.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

Abnormal change = actual minus a constant-mean (or AR(1), fixed now) prediction from the estimation window. Inference: rank of the event-window change among all same-length windows inside the estimation window (placebo in time), plus HAC standard errors as a secondary check.

### Synthetic control (H2, H3, and H4 if a donor outcome exists)

The US is treated as one unit. A synthetic US is a weighted mix of donors, fitted on the pre-period.

CHOICE 5 (donor pool, conditional on what A5 / A8 deliver):
- (a) Countries from A8 (Canada, Denmark, UK, Germany, plus any BIS/ECB series A8 makes comparable). Right unit: the event was national. But four or five donors means the smallest possible permutation p-value is about 1/(J+1), e.g. 0.2 with four donors, so a "significant" result is impossible at 5%. Donors had their own 2008–09 interventions, which A8 must list with sources; any donor with a housing-finance intervention in the window is dropped or flagged.
- (b) US states from A5 (Claude recommends, *if* A5 finds a state-level outcome). Many units. But every state was treated at once, so this is not a US synthetic control. It only works as an intensity design: states with more GSE-eligible (or FFEL) exposure before the event against states with less. It is valid only if A5 finds a state series for the outcome. Note: as far as the repo shows, NY Fed state tables give balances by loan type, not by holder, so a state *public share* may not exist; A5's availability note decides.
- (c) No donor panel: event study and pre-trend extrapolation only. Always available. Weakest counterfactual; stated as such.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

Rule: whichever of (a)/(b) A5 or A8 makes available first is not a reason to choose it. The choice is recorded before either panel's outcome paths are inspected.

CHOICE 6 (predictors and pre-period):
- (a) Outcome lags only (e.g. 2000Q1, 2003Q1, 2005Q1, 2007Q4) over pre-period 2000Q1–2007Q4. Simple and transparent; risk of overfitting a short panel.
- (b) Outcome lags plus house-price growth, unemployment and household debt to income, pre-period 2000Q1–2007Q4 (Claude recommends). Standard practice; the pre-period ends before ESA (13 Feb 2008), so no 2008 law is inside it. Needs these covariates for each donor.
- (c) Longer pre-period from the 1990s. More fit data, but structural differences between housing-finance systems grow with distance.
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

Holdout inside the pre-period: weights are fitted on 2000Q1–2005Q4 and checked on 2006Q1–2007Q4 before any post-period value is looked at.

CHOICE 7 (pre-period fit criterion):
- (a) Drop donors (in placebo runs) whose pre-period RMSPE is more than 5× the US's, and report the post/pre RMSPE ratio rank (Claude recommends). The 5× cutoff is this project's own choice: the claim that it follows Abadie, Diamond and Hainmueller (2010) could not be checked from here (`prereg-fact-checks.md` §3) and is not made. The ratio rank, the primary inference, does not need a cutoff.
- (b) Cutoff 2×. Stricter; with few donors it may leave almost none.
- (c) No cutoff, ratio rank only. Keeps every donor; poorly fitted placebos then dilute the test.
- In all three: if the US's own pre-period RMSPE in the holdout is worse than a stated level no synthetic estimate is reported, only "fit failed". Level: the US pre-period RMSPE in the holdout is larger than the standard deviation of the outcome over 2006–07 (the example level in the draft, adopted with the recommendations; Eleonora may revise it by a dated deviation before any fit is run).
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

Inference: placebo in space (refit with each donor as if treated; p = rank of the US post/pre RMSPE ratio) and placebo in time (move the treatment date to each quarter of 2004Q1–2006Q4 and refit). Leave-one-donor-out is reported as a robustness check.

## The student-loan case (Event S)

FFEL loans were already federally guaranteed. SAFRA mostly changed who *holds and funds* new federal loans, not who *bears the default risk*. ECASLA purchases had started that move in 2008. So the federal holdings share rising after 2010 is largely relabelling and would "pass" any test by construction.

CHOICE 8 (outcome for Event S):
- (a) Federal holdings share of student loans (Z.1), framed as a mechanical check: does the post-2010 rise match the end of new FFEL lending, with no extra effect? Answerable from data in the repo. It tests accounting, not behaviour; say so.
- (b) Non-federal, non-guaranteed student lending (private student loans): the margin where SAFRA could change behaviour (Claude recommends, *if a free source exists*). Not separately visible in Z.1 holder lines, which mix FFEL and private loans. A free source must be found with `source-provenance` first; if none, fall back to (a).
- (c) Drop Event S from causal testing; report it descriptively in A1/A2. Most honest given a 2006Q1 start, ECASLA contamination and no untreated donor (no other country has FFEL, and all states were treated at once).
**Decided: (b).** Eleonora, 2026-11-04 (accepted the recommended option).

Whatever is chosen, there is no valid synthetic control for Event S unless an intensity design (state FFEL exposure) is found by A5.

## Benchmarks and holdout

- Event study: constant-mean and AR(1) normal-spread models; placebo-in-time windows from the estimation period.
- Synthetic control: pre-trend extrapolation of the US series (linear, fitted on 2000Q1–2007Q4) as the naive benchmark; placebo in space and time as above.
- Untouched holdout: 2006Q1–2007Q4 for synthetic-control fit checking. The post-period is not looked at until the fit check is recorded.

## Multiple testing

The count depends on choices 1, 2, 5 and 8. With (b)/(b)/(b)/(b): H1 (one window), H2, H3 and H4, about four primary tests, plus robustness runs.

CHOICE 9:
- (a) Holm correction across the primary family only; robustness runs descriptive (Claude recommends). Controls the family-wise error without needing independence; keeps robustness separate.
- (b) One primary test per event (H1 for G, H4 for S), everything else descriptive. Simplest; loses H2/H3 as tests.
- (c) No correction; all results descriptive with exact ranks. Honest when permutation p-values are coarse anyway (see CHOICE 5a).
**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option).

## Decision rules

- H1 supported → write "the spread fell by X in the [window] after conservatorship, more than in N of M placebo windows". Never "caused" without the overlapping-event caveat.
- Synthetic-control result with the US ranked first of J+1 → "the US moved more than every donor"; with J+1 < 20 the write-up states that this is not significant at 5% by construction.
- Fit failed (CHOICE 7) → report "no credible synthetic control", show the fit, no effect estimate.
- Any null → reported with the same prominence as a positive result, in the write-up and the register.
- If the results contradict A1's reading, both are reported and the conflict is stated; A1 is not revised to fit.
- B1's spread-on-share regression stays "association" unless H1 is supported and robust.

## What is and is not identified

- **Identified, at best:** the change in the mortgage spread in a few weeks around 6–7 Sep 2008, net of a stated normal model and of the other dated events in the window. That is the effect of the conservatorship *announcement bundle* (FHFA action plus Treasury agreements), not of either part alone.
- **Not identified:** HERA versus conservatorship in any quarterly series (same quarter); conservatorship versus the wider crisis in quarterly holdings; any effect on the public share separate from private retreat (A1 shows the share rose mostly as private holders shrank).
- **US-level national treatment with few donors gives weak inference.** With four or five country donors, permutation p-values cannot go below about 0.2. State donors fix the count but not the problem, because every state was treated at the same time; they identify only intensity differences.
- **Holding is not bearing risk.** Z.1 holder lines measure who holds, not who guarantees (A1 limits; net exposure is A2). A shift in holdings is not automatically a shift in credit risk.
- **Student loans:** the federal-share rise after SAFRA is mostly mechanical. Without a private-student-loan series or a state intensity design, Event S is descriptive only.
- Results are reported even if null.

## Deviations (dated, after freezing)

None yet.

## Before freezing (checklist)

1. Done 2026-11-04: Eleonora's choices 1–9 are recorded here and in PLAN.md "Decisions taken".
2. Done 2026-11-04: Fed MBS dates verified; the ADH attribution could not be verified and was removed (`prereg-fact-checks.md` §1, §3).
3. **Open.** Before any outcome is inspected, a dated addendum under "Deviations" must state the donor series, frequency and start date from the A5 or A8 availability note, and the spread proxy B1 uses. The addendum is written from those notes alone; neither panel's outcome paths are looked at first.
4. Done 2026-11-04: committed alone as `prereg: A7 (frozen)`.
