# B2 method note (written before any B2 number was computed)

> **Claude draft, not the author's text.** A proposed method for Eleonora to accept, change or replace. Written during the overnight run she approved (PLAN.md "Decisions taken", 2026-11-04). The method choices are listed under "Questions for Eleonora" in `tracks/markets.md`. Changes after results go at the bottom, with a date.

Date: 2026-11-04. PLAN task B2: "CRT spreads as the market's price for the risk the GSEs hand back; link to A2." Acceptance: "Spread-per-unit-of-expected-loss series by deal; tie to A2's net exposure; paywall gaps stated."

## What free data allow (checked 2026-11-04, see `sources.md`)

| Wanted | Free source | Coverage |
|---|---|---|
| Price of transferred risk, by deal | FHFA *Credit Risk Transfer Progress Report*, December 2016: "Estimated Credit Cost" per CAS and STACR deal, with attach/detach points and an estimated guarantee fee | CAS 2013-1 to 2016-7, STACR 2013-DN1 to 2016-HQA4 |
| Issuance spreads 2017–2023 | FHFA progress reports, Appendices D and E | Charts only, with no numbers in the text. Not used; reading values off the charts would be an estimate (Question for Eleonora) |
| Deal structure 2017–2023 (reference UPB, attach/detach, risk in force) | FHFA progress reports, deal tables | No prices |
| Secondary-market CRT spreads | Bloomberg, Intex, dealer runs | Paywalled |
| Deal-level issuance margins from the GSEs | crt.freddiemac.com (not reachable from the sandbox, code 000), capitalmarkets.fanniemae.com (000/403), SEC EDGAR (403 without the `SEC_USER_AGENT` declared by Eleonora's decision, unset in this session) | Blocked; listed, not worked around |

## Quantities

1. **Credit cost c** (bps). FHFA's "Estimated Credit Cost", transcribed as published. FHFA's footnote: estimated "as of the date of bond issuance, based on a hypothetical baseline scenario: Constant Prepayment Rate (CPR) = 10%, Constant Default Rate (CDR) = 0.2%, Loss Given Default (LGD) = 25%, early redemption at 10-year maturity", assuming "100% of the STACR/CAS notes are sold".
   - *Unit, an assumption to state.* c is read as bps per year of reference-pool UPB. FHFA sets it beside guarantee fees, which are quoted in bps per year, but the table header gives no unit. Labelled as an assumption wherever c is used.
2. **Baseline expected loss of the transferred slice, EL** (bps per year of reference UPB), under FHFA's own baseline scenario. *[Claude's choice]*
   - *Pool.* Monthly steps. The balance runs off at CPR 10% and CDR 0.2% (annual rates converted to monthly). Losses each month are defaults × LGD 25%.
   - *Tranche loss.* Cumulative pool loss C_t, as a share of original UPB, is allocated to the slice [attach, detach] as min(max(C_t − a, 0), d − a).
   - *Horizon.* The slice's loss is cumulated to month 120 (FHFA's early redemption).
   - *Annualising.* EL is the slice's cumulative loss divided by the average outstanding pool balance over the 120 months, as a share of original UPB. That puts it on the same per-year, per-UPB footing as c.
3. **Price multiple m = c / EL.** Market price per unit of baseline expected loss. A multiple above 1 is the risk premium investors charge over FHFA's baseline. EL is 0 for deals whose attachment point lies above baseline cumulative losses, and there m is undefined: it is reported as absent, never as infinity or a default.
4. **Annual cost by year, $.** Σ over deals of c × reference UPB, by issue year and enterprise. Reference UPB comes from the same FHFA deal tables (report of December 2016).
5. **Tie to A2.** The annual cost divided by the year's CRT risk in force (A2's `crt_fhfa.csv`, `annual_rif_musd`) gives the price paid per dollar of risk transferred, % per year. A2's net-exposure bounds (`net_exposure.csv`) are cited for context; B2 does not recompute them.

## Checks (asserts in the script)
- Every transcribed row matches the published deal count per table (CAS 25 rows, STACR 23 rows), dates are in order, attach < detach, and 0 < c < 100 bps.
- *Transcription test.* The parser reads FHFA's text layer. Five hand-checked rows (first, last and three middle rows of each table) are compared in pytest, and a planted typo must fail.
- *EL engine tests.* A slice with attach 0 and detach 10000 takes all pool losses. Losses are additive across adjacent slices. A slice attaching above the baseline cumulative loss gets EL = 0.

## What this is not
- Not a market spread series. c is FHFA's model-based estimate from issuance pricing, under one scenario.
- Not 2017 onward. No numeric prices are free after the December 2016 report.
- m measures price relative to FHFA's baseline loss, not to a loss distribution. A high m can mean risk aversion or a belief that losses will exceed the baseline; the two cannot be separated here.

## Changes after results
2026-11-04, after the first run, before any write-up:
- **Premium rate.** Added the annual cost divided by the bonds actually sold (deal tables, "sold portion"), in % per year, as the price per dollar of protection.
- **A2 tie.** Dividing by A2's `annual_rif_musd` is kept only as context (`priced_share_of_crt_upb`). A2's risk in force includes insurance deals (CIRT, ACIS) and deals FHFA did not price, so the ratio would mix coverage.
- **Overstatement.** FHFA's cost assumes 100% of notes are sold, so cost ÷ sold overstates the rate where the Enterprise retained part of a tranche.
- **Transcription check as done.** Three rows per program (six in all: first, middle and last) were hand-checked against the rendered PDF pages (report pages 6, 9, 13 and 14), not only against the text layer. This replaces the "five rows" planned above. The rendered pages also showed two facts:
  - The column after "sold" in Freddie Mac's table is "Insured via ACIS", not "retained". It is now labelled that way; B2 does not use it.
  - The two rows without a deal name are blank in FHFA's printed table itself.
- **Positive-attach multiples.** For deals attaching at 30–100 bps the baseline cumulative loss (about 31 bps) barely reaches the slice, so the multiple is unstable or absent. Summary multiples are reported for zero-attach deals only.

2026-11-04, after the skeptic's review (R-20261104-mkt-s16 to s22, `claims/tracks/markets-review-log.md`):
- **Unit settled** (s18). In every row with both figures, FHFA's estimated guarantee fee equals the credit cost plus 21 or 30 bps. That is TCCA 10 + G&A 7 + residual risk 4 (low LTV) or 13 (high LTV), per FHFA's footnote. So the credit cost is in bps a year, on the guarantee-fee footing. The identity is asserted. The "cost as a share of the guarantee fee" figure is dropped, because it is an identity, not a finding.
- **EL basis shown both ways** (s16). The main basis stays the average outstanding balance, because guarantee fees accrue on the outstanding balance. The original-UPB basis is reported beside it. The multiple's median is about 6.4 on the outstanding basis and about 10.4 on the original basis. Every zero-attach slice absorbs the whole baseline loss, so their EL is one number, and the multiple's range is just the cost's range scaled.
- **Price per dollar of tranche, not per dollar sold** (s17). FHFA's cost assumes the whole [attach, detach] slice is sold. Annual cost is now divided by the tranche size, (detach − attach) × reference UPB. The sold share of the tranche (the Enterprises kept the rest) is reported for context.
- **Nameless rows** (s21). The match now also asserts that the deal-table and cost-table dates agree.
