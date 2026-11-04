# A2: Gross vs net public exposure (credit risk transfer and mortgage insurance)

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A2. Status: bounds done; the net series waits on Eleonora's choice of what counts as "transferred"** (options in [`METHOD.md`](METHOD.md) and `tracks/analysis.md`). Sources, with hashes and quotes: [`sources.md`](sources.md).

Data: Fed Z.1, `Z1.csv` dated 2026-09-11; FHFA CRT Progress Reports (Dec 2016 to 4Q 2023) and FHFA Reports to Congress (2024, 2025), transcribed in [`crt_fhfa.csv`](crt_fhfa.csv). Every number below has a register row (`claims/tracks/analysis.csv`).

## Result

**What FHFA publishes is risk transferred at issuance, not risk still transferred.** From 2013 through 2025 Fannie Mae and Freddie Mac sold credit risk transfer (CRT) cover with a combined risk in force (RIF) of about $233B at issuance (FHFA, rounded). Outstanding cover is lower, because notes pay down and deals are called. That gives a bound, not a point:

| End of 2025 | Gross | Net, lower bound (all issued CRT still in force) |
|---|---|---|
| Fannie Mae + Freddie Mac holdings, household share | $6.27T | $6.05T |
| Public share of household mortgages and consumer credit | 56.4% | 55.2% |

- Household-apportioned, the issued CRT RIF is $217B, at most 3.5% of the Enterprises' gross holdings.
- **Measured as loss capacity against principal, CRT lowers the public share by at most 1.2 pp.** The bound holds in every year 2013–2025 (`net_exposure.csv`); net ≤ gross is asserted in the script.
- **That is not the same as saying 3.5% of the risk was transferred.** RIF is the most investors can lose, set against the slice of losses where most stress losses fall. On expected or stress losses, the share transferred on covered loans is much larger (FHFA calls it "the majority" for the loans targeted for CRT). Measuring that needs a loss model; see `METHOD.md`, measure 3.
- **Mortgage insurance is larger than CRT in RIF terms, but cannot be netted yet.** FHFA reports $835B of primary mortgage insurance RIF on loans the Enterprises acquired 2013–2023, measured at acquisition. That is 12.5% of 2023 gross holdings after apportioning, but it misses cover written before 2013 and keeps cover since cancelled, so it is neither a bound nor an estimate of outstanding cover. The Enterprises also keep the counterparty risk if an insurer fails.
- **Cumulative reference-pool principal says nothing about coverage.** By 2025 it is 1.1× the Enterprises' whole household book, because refinanced loans are counted again in new pools.

## Limits

- **Bounds, not a series.** The observed net series needs outstanding CRT and mortgage-insurance cover from the Enterprises' 10-K/10-Q filings. `www.sec.gov` and the Fannie/Freddie sites are blocked by the network policy here (`sources.md`).
- **Ginnie Mae pools and federal student loans stay at gross.** FHA insures in full; the VA guaranty is partial, but VA data are not yet sourced.
- **Apportioning.** CRT and mortgage-insurance amounts are scaled to households with the Z.1 ratio used for the holdings.
- **FHFA data.** 2013–2016 cumulative RIF is the sum of FHFA's annual totals, 2017 is derived from the 4Q 2018 report, and 2024–2025 are rounded to $1 billion. Year-to-year consistency is asserted.
- **Revisions.** Z.1 vintage 2026-09-11; rerun after each Z.1 release.

## Files and how to rerun

```bash
uv run --project pipeline python validation/run.py        # downloads the Z.1 zip if absent
uv run --project pipeline python research/a2_net_exposure/net_exposure.py
```

- `net_exposure.py`: the bounds. Reuses A1's household-apportioned cells; asserts net ≤ gross, a positive lower bound and a consistent FHFA transcription.
- `crt_fhfa.csv`: FHFA CRT and PMI figures by year, with the report and page for each.
- `net_exposure.csv`: one row per year end, 2013–2025.
- `results.json`: headline numbers for the register.
- `METHOD.md`: what "transferred" can mean, and what each option needs.
- `sources.md`: the FHFA reports, with hashes and quotes.
