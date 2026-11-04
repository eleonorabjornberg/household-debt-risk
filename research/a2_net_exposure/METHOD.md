# A2 method note: what "transferred" can mean

> **Claude draft, not the author's text.** Options and the reasoning behind the bounds computed so far. Which definition of "transferred" the project uses is Eleonora's decision (see `tracks/analysis.md`, "Questions for Eleonora").

## The gross side

Gross public exposure is what A1 and the rest of the project already call public: Z.1 holdings of the federal government, the GSEs and agency pools, and state and local governments, household-apportioned. For A2 the part that can be netted is **Fannie Mae and Freddie Mac (portfolio + pools)**. The other public holders have no comparable transfer programme in this window:

- **Ginnie Mae pools (FHA, VA, USDA loans).** FHA insures the loan in full. VA guarantees only part of each loan; the rest of the loss falls on the Ginnie issuer (a private servicer). Netting that out needs VA guaranty data (not yet sourced), so Ginnie stays at gross.
- **Federal student loans.** No risk transfer.

## Three things that get called "transferred"

1. **Reference-pool UPB.** The unpaid principal of the loans a CRT deal references. FHFA reports it at issuance. It is not a measure of risk moved, since a deal covers only a slice of the losses on that pool. Cumulated since 2013 it keeps loans that have paid off at their issuance balance and counts refinanced loans again in new pools (FHFA also notes that one Freddie reference pool can back both a STACR and an ACIS deal). By 2025 the cumulative reference UPB exceeds the whole Fannie/Freddie book (`net_exposure.csv`, `cum_crt_ref_upb_over_gross`), which shows it cannot be read as "share of the book covered".
2. **Risk in force (RIF).** The most the private side can lose: the note size of the sold tranches (STACR, CAS) or the insurer's limit (CIRT, ACIS, mortgage insurance). FHFA: "The total RIF for all PMI represents the maximum level of coverage". RIF is in dollars of loss capacity, so subtracting it from unpaid principal gives the most principal that can still lose money for the public sector. RIF is small next to UPB (about 3% of reference UPB at issuance; FHFA, `sources.md`) because mortgage losses are small next to principal.
3. **Expected or stress loss transferred.** The share of the losses the Enterprise would expect (or would suffer in a stress) that now falls on private investors. A CRT tranche that covers, for example, losses from 1.5% to 4.9% of the pool (CAS 2023-R01, attach/detach 150/490 bp, FHFA 4Q23 report p.4) absorbs a small share of principal but much of the stress loss. On this measure the transfer is large for the loans covered. FHFA writes that through CRT and mortgage insurance "the majority of the underlying mortgage credit risk on mortgages targeted for CRT has been transferred" (4Q 2019 report). It needs a loss model and the outstanding deal structures, which overlaps with A6 (fair-value subsidy).

**First-loss vs mezzanine.** In every 2023 CAS and CIRT deal in the FHFA 4Q23 report the attach point is above zero (60 to 165 bp), so Fannie keeps the first loss below it and the senior risk above the detach point, and sells the slice in between. The 4Q 2019 report notes that Fannie changed its CAS REMIC structure in 2019 to transfer more of the first-loss position. So the same RIF can carry very different expected loss depending on where it attaches. Measure 2 ignores this; measure 3 is built on it.

## What is computed now (independent of the choice)

FHFA publishes RIF at issuance only. Outstanding RIF is lower, because notes pay down with the reference pool and deals are called. So for every year end 2013–2025:

    G − cumulative issued CRT RIF  ≤  net Fannie/Freddie exposure  ≤  G

`net_exposure.py` computes both sides, and the public share of household credit on each side (the denominator, total household mortgages and consumer credit, is unchanged by a transfer). It asserts net ≤ gross and that the lower bound stays positive. These are bounds on measure 2, not an estimate of it.

**Mortgage insurance** is reported next to the bounds, not inside them. FHFA's PMI figures are RIF at acquisition for loans acquired from 2013 on. They omit cover on loans acquired earlier and keep cover that has since been cancelled or paid off, so they bound nothing. The Enterprise keeps the counterparty risk on PMI (FHFA 4Q23 report p.12), and PMI pays before CRT investors, so adding PMI and CRT RIF overstates the joint cover on loans that have both.

## What would turn the bounds into a series

- **Outstanding CRT and MI cover from the Enterprises' 10-K/10-Q** (free, primary). They are expected to report credit-enhanced UPB and outstanding coverage; not yet checked, because the filings could not be reached. `www.sec.gov` is blocked by the network policy here; allowing it (or Eleonora downloading the filings) would give an observed net series rather than a bound.
- **A runoff estimate**: decay each issuance year's RIF with an assumed paydown rate (for example, the Z.1 GSE book's own runoff). This is an estimate, labelled as one, and sensitive to the 2020–21 refinancing wave. Not done until Eleonora picks the definition.
- **Measure 3** needs deal-level attach/detach points and a loss model (A6).

## Limits

- 2013–2016 cumulative CRT RIF is the sum of FHFA's annual totals (rounded to $0.1 billion), and 2017 is derived from the 4Q 2018 report. 2024 and 2025 are rounded to $1 billion. Year-on-year consistency is asserted in `load_crt` (within $1 billion or 1%).
- CRT and PMI amounts are scaled to households with the same ratio as the Z.1 GSE holdings, which assumes the CRT-covered book has the household/business mix of all 1–4 family mortgages.
- FHFA's CRT figures cover single-family loans only; multifamily CRT is excluded, as are multifamily loans from the household scope.
- Z.1 vintage 2026-09-11. FHFA figures can be revised between reports (2021: the 4Q21 cumulative is $23 million below the 4Q20 cumulative plus 2021 flow).
