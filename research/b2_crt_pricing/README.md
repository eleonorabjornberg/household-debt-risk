# B2: What the market charges for the credit risk the GSEs pass back

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write. The method is Claude's proposal ([`METHOD.md`](METHOD.md), committed before any number), listed for her decision under Q-B2 in `tracks/markets.md`.

**PLAN task B2. Status: ready for review; the write-up is a Claude draft.** Sources and hashes are in [`sources.md`](sources.md). The code is `b2.py`; its tests in `test_b2.py` check transcription against the rendered PDF, include a planted typo, and test the loss engine. Every number in this file has a row in `claims/tracks/markets.csv`.

## What could be priced

Only one free source gives numbers for the price of CRT: FHFA's *CRT Progress Report* of December 2016. For each CAS (Fannie Mae) and STACR (Freddie Mac) deal from 2013 to 2016, it gives an "estimated credit cost", an estimated guarantee fee, and the deal's structure. FHFA estimated the cost from issuance pricing under one baseline loss scenario: 10% prepayment, 0.2% annual defaults, 25% loss given default, and redemption at 10 years. 47 deals have a published cost.

Later FHFA reports show issuance spreads only as charts. Deal-level data from the GSEs and SEC filings are blocked from this environment, and secondary-market spreads are paywalled (`sources.md`). So B2 covers 2013–2016 deals only.

## Result

**Investors were paid several times FHFA's own baseline expected loss.** Under the baseline scenario a pool loses about 31 bps of its original balance over ten years, about 5.0 bps a year. In the 21 deals where the GSE sold the first loss (attachment point 0), the investors' slice absorbs all of that.
- Their median credit cost was 32 bps a year of the reference pool.
- That is 6.4 times the slice's baseline expected loss (range 5.0 to 8.6).
- It is also about 57% of FHFA's estimated guarantee fee on the same pools (median 55 bps).

**Deals that kept the first loss** (attachment at 30–100 bps) were cheaper, with a median cost of 13 bps. Their slice starts at or above the baseline's cumulative loss, so a multiple of expected loss is unstable or undefined for them. 17 of them have no baseline loss at all, and their multiple is recorded as absent.

**By issue year** (`by_year.csv`):

| Year | Deals priced | Credit cost, weighted by reference UPB (bps a year) | Cost per dollar of bonds sold (a year) | Priced deals' share of the year's CRT reference UPB |
|---|---|---|---|---|
| 2013 | 3 of 3 | 12.5 | 5.9% | 94% |
| 2014 | 14 of 14 | 11.7 | 4.0% | 98% |
| 2015 | 14 of 14 | 23.0 | 6.9% | 80% |
| 2016 | 16 of 17 | 30.9 | 10.1% | 71% |

The weighted cost rose from 2014 to 2016 as the GSEs began selling the first loss, which costs more throughout (above). FHFA itself attributes the 2016 rise for CAS to this: "The estimated credit cost of CAS issuances increased in 2016 because Fannie Mae sold the first loss position to investors". Per dollar of bonds sold, investors earned about 4.0–10.1% a year above the reference rate.

## What this does and does not show

- **This is FHFA's estimate, not a market spread series.** The cost is derived from issuance pricing under one scenario. It assumes 100% of the notes were sold, so dividing by the bonds actually sold overstates the rate where the GSE kept part of a tranche. The table does not state the unit; it is read as bps a year of the reference pool, because FHFA sets it beside guarantee fees (an assumption).
- **A multiple above 1 is the premium over FHFA's baseline, not over expected losses in general.** It mixes investors' risk aversion with any belief that losses will exceed the baseline, and the two cannot be separated here.
- **Tie to A2.** The priced deals cover most of each year's CRT reference UPB (last column). The rest is insurance (CIRT, ACIS) and unpriced deals. A2's net-exposure bounds (`research/a2_net_exposure/`) are the quantity this price applies to. B2 does not recompute them, and dividing by A2's risk in force would mix coverage.
- **2017 onward is a gap.** Reading issuance spreads off FHFA's charts would be an estimate with a stated reading error. It is listed as a choice for Eleonora, not done.

## Reproduce

```bash
uv run --project pipeline python research/b2_crt_pricing/b2.py
uv run --project pipeline pytest -q research/b2_crt_pricing
```
