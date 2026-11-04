# Pre-registration: C1b, a second C1 nowcast run with agency monthly data

> **Claude draft, not the author's text.** Eleonora decided on 2026-11-04 to pre-register this run (Q-C1b, option (a): Freddie Mac and Ginnie Mae monthly data, Fannie Mae carried flat; PLAN.md "Decisions taken"). The design choices below are hers to make. Claude drafted them as `CHOICE:` lines with a recommendation. Nothing here has been run.

Status: **draft** (not frozen). Drafted 2026-11-04 by Claude (markets track).

**Before any result.** No C1b output exists. C1's own development results are known, and they are what motivated this run: they showed a downward bias, possibly from carrying the public mortgage holders flat (`research/c1_nowcast/README.md`). This design is therefore not blind to C1's development results; it is blind to C1b's. C1's and C2's holdout (2023Q3–2026Q2) is still sealed (Q-C1c).

## Question
Does adding agency monthly data for the public mortgage holders reduce the error, and the downward bias, of C1's accounting-bridge nowcast of the public share?

## Hypotheses
- **H1.** C1b's bridge has lower RMSE than C1's bridge (indicator set 2b) on the same targets and instants.
- **H2.** C1b's bridge has a smaller mean error (bias) than C1's.
- **Support:** lower RMSE at every instant index k, by the decision rule below. **Null:** differences inside the noise. **Against:** C1's bridge has lower RMSE.

## Data (checked 2026-11-04)
- **Freddie Mac.** *Monthly Volume Summary*, one PDF per month, `https://www.freddiemac.com/investors/financials/pdf/<MMYY>mvs.pdf`.
  - Reachable (HTTP 200). The listing page links 165 reports, from January 2013 to September 2026.
  - What it gives: Freddie's mortgage portfolio and its single-family credit-guarantee (pool) UPB at month end.
  - No real-time vintages: each report is the value as first published, and the PDF is the vintage.
- **Ginnie Mae.** Monthly reports (`https://www.ginniemae.gov/data_and_reports/reporting/Pages/monthly_summary_reports.aspx`). The page is reachable, but **no downloadable file was found in its static HTML on 2026-11-04**. Availability is to verify with the `source-provenance` skill before freezing; if it can't be verified, Ginnie is carried flat and the run is recorded as "Freddie only".
- **Fannie Mae.** Carried flat, as decided: fanniemae.com is still blocked.
- **Everything else as C1.** Z.1 vintages from the release archive (41 releases from 2016-09-16), G.19 and H.8 from ALFRED as of each instant, and the target is the first-release share (`research/c1_nowcast/EVALUATION.md`).

## Method
- **Model.** C1's accounting bridge with indicator set 2b, plus one mapping: the agency cells move with their agency's monthly growth.
  - *Freddie's growth.* From the last month of quarter T to the latest month published by instant t, both read from reports published by t.
- **CHOICE: which Z.1 cells the agency data move.** The archive's catalog-level cells (`mort_gse`, FL403065105; `mort_pools`, FL413065105) combine Fannie, Freddie, Ginnie, the FHLBs and others.
  - (a) Split the two cells into Freddie, Ginnie and the rest using the finer Z.1 series (FL403065120 + FL413065123 for Freddie; FL413065110 + FL413065133 for Ginnie) where a vintage has them; otherwise use the shares from the nearest earlier vintage that does. *Recommended.* It uses each agency's own growth. The finer series are absent from the 2016 table layout, so their availability by vintage must be checked first.
  - (b) Apply Freddie's growth to Freddie's share of the combined cell taken from the latest vintage. Simpler, but it puts a latest-vintage quantity into a real-time run.
  - (c) Apply an agency-weighted growth to the whole combined cell. Crude: it also moves Fannie, which is meant to be carried flat.
- **CHOICE: publication date of each agency report** (for the as-of rule).
  - (a) The PDF's own creation date from its metadata, checked against the listing page. *Recommended.*
  - (b) A fixed lag after month end (for example the 25th of the next month), checked against a sample of reports. Simpler, but it can put a report into an instant before it was out.
  - (c) The listing page's dates only (the page may not show them).
- **CHOICE: what Freddie's report quantity maps to.** The Z.1 cell is household 1–4 family mortgages held by Freddie in portfolio and pools; the report gives total single-family portfolio and guarantee UPB.
  - (a) Use growth rates only, so level differences in definition cancel. *Recommended.*
  - (b) Use levels with a calibration ratio from the last Z.1 quarter (in effect the same as (a) for a nowcast).
- **Instants, k, metrics.** As C1: the 15th of each month, k = 1, 2, 3, RMSE and MAE in pp, mean error.

## Benchmarks and holdout
- **Benchmarks.** No-change (the C1 headline) and C1's bridge (2b), the comparison that matters for H1 and H2.
- **Development and holdout.** Development targets 2016Q3–2023Q2, as C1. Holdout 2023Q3–2026Q2, the same sealed holdout as C1 and C2.
- **CHOICE: does C1b enter the joint holdout run?**
  - (a) Yes, if C1b is frozen before that run. *Recommended:* the holdout is then still seen only once.
  - (b) No: C1b is scored on development only, and on a prospective holdout (releases from 2026-12-10).

## Multiple testing
Two hypotheses × 3 instant indices. C1b's bridge against C1's bridge is non-nested: DM with the HLN correction, lag 0, plus the post-hoc lag-1 sensitivity, as C1. Holm over the 6 tests. All p-values descriptive given about 25 targets per k.

## Decision rules
- **"Improves on C1":** lower RMSE at every k on development, significant after Holm at one or more k, and lower in the holdout (if (a) above).
- **"Comparable":** not significant, or the sign differs across k.
- **"Does not improve":** C1's bridge has lower RMSE at one or more k.
- **Bias:** reported as mean error with its HAC standard error, descriptively.

## What is and is not identified
- It measures whether Freddie's (and possibly Ginnie's) monthly data improve a mechanical nowcast. It says nothing about why the share moves.
- With Fannie carried flat, any gain is a lower bound on what full agency data could give.

## Deviations (dated, after freezing)
None (not frozen).
