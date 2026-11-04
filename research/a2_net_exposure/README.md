# A2: Gross vs net public exposure (credit risk transfer and mortgage insurance)

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A2. Status: bounds done; the net series waits on Eleonora's choice of what counts as "transferred"** (options in [`METHOD.md`](METHOD.md) and `tracks/analysis.md`). Sources, with hashes and quotes: [`sources.md`](sources.md).

Data: Fed Z.1, `Z1.csv` dated 2026-09-11; FHFA CRT Progress Reports (Dec 2016 to 4Q 2023) and FHFA Reports to Congress (2024, 2025), transcribed in [`crt_fhfa.csv`](crt_fhfa.csv). Every number below has a register row (`claims/tracks/analysis.csv`).

## Result

**What FHFA publishes is risk transferred at issuance, not risk still transferred.** From 2013 through 2025 Fannie Mae and Freddie Mac sold credit risk transfer (CRT) cover with a combined risk in force (RIF) of about $233B at issuance (FHFA, rounded). Outstanding cover is lower, because notes pay down and deals are called. That gives a bound, not a point:

| End of 2025: principal (UPB), less CRT loss capacity (RIF) for net | Gross | Net of CRT only, lower bound (all issued CRT still in force; mortgage insurance not netted) |
|---|---|---|
| Fannie Mae + Freddie Mac holdings, household share | $6.27T | $6.05T |
| Public share of household mortgages and consumer credit | 56.4% | 55.2% |

- Household-apportioned, the issued CRT RIF is $217B, at most 3.5% of the Enterprises' gross holdings.
- **Measured as loss capacity against principal, CRT alone lowers the public share by at most 1.2 pp.** This is not a floor on the public share once mortgage insurance is netted (below). The bound holds in every year 2013–2025 (`net_exposure.csv`); net ≤ gross is asserted in the script.
- **That is not the same as saying 3.5% of the risk was transferred.** RIF is the most investors can lose on a slice of the losses, not on the principal; the tranches sold sit above a retained first-loss slice (`METHOD.md`). How much of the expected or stress loss that slice carries is not measured here: it needs deal structures and a loss model (`METHOD.md`, measure 3). FHFA's own summary is that through CRT *and mortgage insurance together* "the majority of the underlying mortgage credit risk on mortgages targeted for CRT has been transferred" (4Q 2019 report).
- **Mortgage insurance RIF is bigger in dollars than CRT RIF, but cannot be netted yet, and FHFA says the two RIF figures are "not strictly comparable"** (loan-level vs pool-level cover). FHFA reports $835B of primary mortgage insurance RIF on loans the Enterprises acquired 2013–2023, measured at acquisition. That is 12.5% of 2023 gross holdings after apportioning, but it misses cover written before 2013 and keeps cover since cancelled, so it is neither a bound nor an estimate of outstanding cover. The Enterprises also keep the counterparty risk if an insurer fails.
- **Cumulative reference-pool principal says nothing about coverage.** By 2025 it is 1.1× the Enterprises' whole household book, because loans that paid off or refinanced are still counted at their issuance balance, and refinanced loans are counted again in new pools.

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
