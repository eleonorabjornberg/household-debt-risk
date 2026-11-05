# Pre-registration: C1b, a second C1 nowcast run with agency monthly data

> **Claude draft, not the author's text.** Eleonora decided on 2026-11-04 to pre-register this run (Q-C1b, option (a): Freddie Mac and Ginnie Mae monthly data, Fannie Mae carried flat; PLAN.md "Decisions taken"). The design choices below are hers to make. Claude drafted them as `CHOICE:` lines with a recommendation. Nothing here has been run.

Status: **frozen.** The freeze commit is the commit that adds `research/c1b_nowcast/FREEZE.json` (SHA-256 of this file, the code, the inputs and the development outputs). Before that: Drafted 2026-11-04 by Claude (markets track). Eleonora's choices filled in on 2026-11-04 (evening) from PLAN.md "Decisions taken" (cards c1b-joint, c1b-cells-2, c1b-pubdate-2, c1b-map). This version is committed before `research/c1b_nowcast/nowcast_c1b.py` exists or has scored anything. Lines marked *[implementation]* are Claude's mechanical details and can be overruled before the freeze. The development run was scored after the choices commit (0acbde6) and the code commit (9e0820a); the quant-reviewer's pre-freeze objections (R-20261104-mkt-q25 to q28) were then resolved by the *[implementation]* lines marked "added before the freeze". The holdout has not been run.

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
- **Ginnie Mae.** Monthly reports (`https://www.ginniemae.gov/data_and_reports/reporting/Pages/monthly_summary_reports.aspx`). The page is reachable, but **no downloadable file was found in its static HTML on 2026-11-04**; the provenance check failed (markets track, reported to the coordinator 2026-11-04 ~17:25 UTC). **Ginnie is carried flat and the run is recorded as "Freddie only".**
- **Freddie Mac, as fetched.** `research/c1b_nowcast/freddie_mvs.py` fetched the listing page (`https://www.freddiemac.com/investors/financials/monthly-volume-summaries`, 165 reports) and the 129 reports from January 2016 to September 2026 on 2026-11-04. It parses Table 1 ("Total mortgage portfolio", ending balance, $ millions) for every month each report shows (about 13 months per report). Byte counts and SHA-256 per PDF: `data/c1b/mvs/manifest.jsonl` and `freddie_mvs_reports.csv`. Only publication metadata and Table 1 were read before this commit; no nowcast was computed.
- **Fannie Mae.** Carried flat, as decided: fanniemae.com is still blocked.
- **Everything else as C1.** Z.1 vintages from the release archive (41 releases from 2016-09-16), G.19 and H.8 from ALFRED as of each instant, and the target is the first-release share (`research/c1_nowcast/EVALUATION.md`).

## Method
- **Model.** C1's accounting bridge with indicator set 2b, plus one mapping: the agency cells move with their agency's monthly growth.
  - *Freddie's growth.* From the last month of quarter T to the latest month published by instant t, both read from reports published by t.
- **CHOICE (decided): which Z.1 cells the agency data move. Eleonora: (d)** (card c1b-cells-2, 2026-11-04). Her first pick, (a), split by the finer Z.1 series, could not run: none of the 41 archived releases carries FL403065120, FL413065123, FL413065110 or FL413065133.
  - **(d)** Freddie's share of the combined GSE + pool cell = Freddie's own published total mortgage portfolio ÷ that vintage's combined cell. Real-time; **labelled a proxy**, because Freddie's total includes multifamily and the Z.1 cells are household 1–4 family.
  - *[implementation]* Combined cell C_T = `mort_gse` + `mort_pools` at T in the base release R (household-apportioned, as in C1). Freddie's level F_T = the ending balance for the last month of T in the latest MVS report published before t. Freddie's share s = min(1, F_T / C_T).
  - *[implementation]* Nowcast: C_q = C_T × (1 + s × (g − 1)), with g Freddie's growth (below). `mort_gse` and `mort_pools` are both scaled by C_q / C_T (both are public, so the split between them does not move the share). Fannie, Ginnie, the FHLBs and the rest of the cell are carried flat. Every other cell moves as in C1's set 2b.
- **CHOICE (decided): publication date of each agency report. Eleonora: (a2)** (card c1b-pubdate-2, 2026-11-04). Her first pick, (a), the PDF creation date checked against the listing page, could not run as written: the listing shows no dates, and 21 of the 129 reports carry a creation date of 2024-01-18 (re-issued in a batch).
  - **(a2)** The PDF creation date where it is plausible (after month end and within 45 days of it), otherwise month end + a fixed lag. Re-issued months are labelled **"content possibly revised"**.
  - *[implementation]* Fixed lag = the largest lag among the plausible reports: 33 days (108 plausible reports, lags 17–33 days). The 21 re-issued reports: 2016-08, 2019-05, -06, -07, -09, -11, -12, 2020-01 to -06, 2021-11, 2022-02, 2023-03, -05 to -09 (`freddie_mvs_reports.csv`).
  - *[implementation]* A report is usable at instant t if its publication date is strictly before t (the 15th).
- **CHOICE (decided): what Freddie's report quantity maps to. Eleonora: (a)**, growth rates only, so definition differences cancel (card c1b-map, 2026-11-04). Under (d) the level enters only as the weight s.
  - *[implementation]* g = F(m*) / F(last month of T), both read from the **same** report: the latest one published before t. m* is the latest month in that report on or before the end of q. Using one report for both months keeps definition breaks between reports out of g (one was found: the March 2021 report restates February 2021 by +$44.0 billion). If no month after T is published yet, g = 1.
- **Instants, k, metrics.** As C1: the 15th of each month, k = 1, 2, 3, RMSE and MAE in pp, mean error.

## Benchmarks and holdout
- **Benchmarks.** No-change (the C1 headline) and C1's bridge (2b), the comparison that matters for H1 and H2.
- **Development and holdout.** Development targets 2016Q3–2023Q2, as C1. Holdout 2023Q3–2026Q2, the same sealed holdout as C1 and C2.
- **CHOICE (decided): does C1b enter the joint holdout run? Eleonora: (a)**, yes: build and freeze C1b, then one joint C1 + C1b + C2 holdout run (card c1b-joint, 2026-11-04).
- *[implementation]* Sample: real time only (C1's RT sample: Z.1 vintages from 2016-09-16, first-release target). C1's pseudo-real-time samples P2a and P2b are not rerun.

## Multiple testing
Two hypotheses × 3 instant indices. C1b's bridge against C1's bridge is non-nested: DM with the HLN correction, lag 0, plus the post-hoc lag-1 sensitivity, as C1. Holm over the 6 tests. All p-values descriptive given about 25 targets per k.
- *[implementation]* H1 test: DM-HLN on squared errors, C1's bridge vs C1b's bridge, two-sided, per k.
- *[implementation]* H2 test: paired t-test (HLN small-sample factor, lag 0, two-sided) of the mean of e(C1b) − e(C1), per k. H2 is supported at k when the test is significant after Holm and |mean e(C1b)| < |mean e(C1)|. H1 is supported at k when its test is significant after Holm and C1b's RMSE is lower (column `supported` in `tests_dev.csv`).
- *[implementation]* Bias: mean error of each model per k, with a Newey–West standard error (lag 1, Bartlett weights) (`bias_dev.csv`). Added before the freeze after quant-reviewer R-20261104-mkt-q26.

## Decision rules
- **"Improves on C1":** lower RMSE at every k on development, significant after Holm at one or more k, and lower in the holdout (if (a) above).
  - *[implementation]* "Lower in the holdout" = lower RMSE pooled over k = 1–3 on the holdout targets 2023Q3–2026Q2 (per-k values reported descriptively).
- **"Comparable":** not significant, or the sign differs across k.
- **"Does not improve":** C1's bridge has lower RMSE at one or more k.
- **Bias:** reported as mean error with its HAC standard error, descriptively.
- *[implementation, added before the freeze after quant-reviewer R-20261104-mkt-q27]* The rules are applied in this order: "does not improve" first (C1's RMSE lower at one or more k); then "comparable" if C1b's RMSE is not strictly lower at every k (an exact tie counts as not lower) or no H1 test is significant after Holm; then, in the joint run, "comparable (holdout RMSE not lower)" if C1b's pooled holdout RMSE is not lower; otherwise "improves on C1". "Sign differs across k" in "comparable" is therefore read as covered by "does not improve".
- *Descriptive robustness (not a decision rule; quant-reviewer R-20261104-mkt-q28):* RMSE on instants that used a re-issued Freddie report vs the rest.

## Joint holdout run
*[implementation, added before the freeze after quant-reviewer R-20261104-mkt-q25]* One run, one commit, opened once:
1. Eleonora adds a row to PLAN.md "Decisions taken" that says "unseal", "holdout" and "C1b"; that commit is the approval commit. It must come after C1b's freeze commit (`research/c1b_nowcast/FREEZE.json`).
2. On a clean tree, `research/c2_forecast/holdout_run.py --prereg 192d60c --approval <commit>` runs C2 and C1 on the holdout (its own gates, unchanged).
3. Immediately after, `research/c1b_nowcast/nowcast_c1b.py --holdout --approval <same commit>`. It refuses unless the tree differs from HEAD only by C2's fresh `holdout_results.json` made with the same approval commit, both FREEZE.json files match, and the approval commit lies between C1b's freeze and HEAD.
4. The three result files (C2's `holdout_results.json`, C1b's `holdout_results.json` and `nowcasts_holdout.csv`) are committed together as one commit. Neither script is rerun.
C1's holdout numbers appear in both outputs (C1b's as the comparison column `bridge_c1`); both come from the same frozen C1 code in the same run.

## What is and is not identified
- It measures whether Freddie's (and possibly Ginnie's) monthly data improve a mechanical nowcast. It says nothing about why the share moves.
- With Fannie and Ginnie carried flat, any gain is a lower bound on what full agency data could give.
- s is a proxy (multifamily inside Freddie's total; Freddie's total also includes Freddie-guaranteed securities held outside the pools cell). It matters only as the weight on Freddie's growth.

## Deviations (dated, after freezing)
### 2026-11-05: c1b-dev-1 (a), instants with no published target (Eleonora's decision; markets track wrote it)
*Before any holdout value was seen.* The first joint holdout run, approved at 77460b4, stopped with `KeyError: '2026Q3'` in `research/c1_nowcast/nowcast.py` `run()`. By the code order, C2's holdout step had already run in memory; nothing from it or from C1 was written or printed, and no file was left. The instant grid runs to 2026-10-01. The 2026-09-15 and 2026-10-01 instants follow the 2026-09-11 release, whose last quarter is 2026Q2, so their target is 2026Q3, and no Z.1 has published 2026Q3 yet. The frozen code looked that target up in the latest vintage without checking that it was there.

Eleonora chose option (a) on card c1b-dev-1 (PLAN.md "Decisions taken", 2026-11-05):
- Such rows are kept in the nowcast table and labelled "no target" (`target` column, `nowcast.NO_TARGET`). Their `actual` is empty, so they are never scored or tested. They do not count as holdout targets (`holdout_run.py` reports `n_targets` on scored rows only, plus `n_no_target_instants` and `no_target_quarters`).
- Code change: `nowcast.target_latest()` checks only whether q is in the latest vintage before the lookup. Nothing else in the models, instants, benchmarks, inputs, tests or holdout window changes. Development outputs are unchanged, since every development target is published.
- 2026Q3 lies outside the pre-registered holdout window (2023Q3–2026Q2), so these rows could never have been scored. The holdout filter (`q > DEV_END`) has no upper bound; they drop out only because they have no actual.
- In C1b's holdout table (`nowcast_c1b.py`, unchanged) these rows carry an empty `actual` but not the `target` label.
- Frozen files changed: `research/c1_nowcast/nowcast.py`, `research/c2_forecast/holdout_run.py` (the count above, and the order check below) and `docs/decisions/c1b-prereg.md` (this entry). `research/c1b_nowcast/FREEZE.json` and `research/c2_forecast/FREEZE.json` are re-hashed in the fix commit. C2's FREEZE still names the protocol as `scoring-protocol.md @ 192d60c` (the `--prereg` value the run requires). This entry is appended after that commit and changes no scoring rule.
- Order check (quant-reviewer mkt-q29): `holdout_run.py` now refuses an approval commit that is not strictly after the last commit that changed C2's FREEZE.json, as C1b already did. An approval from before this fix, such as 77460b4, cannot open the rerun.
- The holdout is run once more, with a NEW approval commit from Eleonora that comes after the fix commit. The crashed run does not count as an opening: no holdout result exists from it.
