# A5: Who borrows, and who holds the loans

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A5. Status: borrower side and state view done; linking borrowers to holders waits on Eleonora's choice** (`tracks/analysis.md`, Q4). What exists and what does not: [`AVAILABILITY.md`](AVAILABILITY.md). Sources and hashes: [`sources.md`](sources.md).

Data: Fed Distributional Financial Accounts (DFA, files dated 2026-09-15, through 2026Q2); NY Fed State Level Household Debt Statistics (CCP/Equifax, Feb 2026, Q4 2025); Fed Z.1 (2026-09-11) for the holder side. Every number below has a register row (`claims/tracks/analysis.csv`).

## Who borrows (DFA, 2026Q2)

| Wealth group | Home mortgages | Consumer credit | Net worth |
|---|---|---|---|
| Bottom 50% | 22.6% | 51.6% | 2.3% |
| Next 40% | 48.9% | 34.9% | |
| Top 10% | 28.4% | | 68.9% |

- **The bottom half by wealth owes half the consumer credit but a fifth of the mortgages.** In 1989Q3 the split was 27.5% of mortgages and 43.8% of consumer credit (`figures/dfa_bottom50_shares.png`).
- **By income, mortgages sit at the top.** The top 20% by income owe 53.2% of home mortgages; the bottom 20% owe 3.3% of mortgages and 7.1% of consumer credit.
- **Leverage is concentrated at the bottom, but lower than in 2007.** The bottom 50% by wealth owe 58.4% of their assets in debt, down from 81.5% in 2007Q4. For the top 0.1% the ratio is 1.1%. (`dfa_leverage.csv`; the DFA values real estate at market prices, so these ratios move with house prices.)

## Who holds the loans (Z.1, 2026Q2)

Public holders (federal government, GSEs and agency pools, state and local) hold 65.6% of household mortgages and 31.3% of consumer credit, which is mostly federal student loans (`loan_type_public_share.csv`). These are national shares by loan type. **No free source says which borrowers' loans the public sector holds** (`AVAILABILITY.md`). Joining the two tables needs an assumption about holder mix within each loan type, which is a design choice (Q4), so the tables are shown side by side and not multiplied.

## Where (NY Fed state data, Q4 2025)

- **Mortgage debt per person with a credit file** ranges from $20.8k in West Virginia to $78.1k in DC, a 3.8× spread (`figures/state_mortgage_pc_2025.png`).
- **Student loan debt per person**, a mostly federal loan type (the NY Fed series includes private student loans), ranges from $3.2k in Wyoming to $12.7k in DC (`figures/state_studentloan_pc_2025.png`).
- Mortgage delinquency by state: `figures/state_mortgage_delinq_2025.png`; all states: `state_2025.csv`.

## Limits

- **State level only.** The NY Fed lists a county-level product but no county file could be found (AVAILABILITY.md), so no claim here is below state level.
- **Sampling.** NY Fed state figures come from a 5% sample (1% for student loans) and may not match the national report. Puerto Rico is in the file but excluded here.
- **Per person, not per household or per borrower.** The denominator is people aged 18+ with a credit file, so states with fewer homeowners show lower mortgage debt per person without any difference in loan size.
- **No income denominator by state yet.** Census ACS needs `api.census.gov`, which the network policy refuses.
- **DFA is model-based.** It allocates Z.1 aggregates across groups using survey data (the Fed's DFA methodology; not yet quoted in `sources.md`), so quarter-to-quarter movements within a group are estimated, not observed.
- **Revisions.** DFA, Z.1 and the NY Fed state data are all revised; rerun after each release.

## Files and how to rerun

```bash
uv run --project pipeline python validation/run.py                                    # Z.1 zip, if absent
uv run --project pipeline python research/a5_distribution/distribution.py             # downloads DFA and NY Fed files into data/a5/
uv run --project pipeline --with matplotlib python research/a5_distribution/figures.py
```

- `distribution.py`: tables and `results.json`; asserts that DFA shares add to 100, that the state file has the 50 states and DC with no gaps, and that the loan-type shares weight back to the overall public share.
- `figures.py`: two DFA charts (chart-from-sql skill) and three state tile maps, each with alt text and a JSON sidecar.
- `dfa_shares.csv`, `dfa_leverage.csv`, `state_2025.csv`, `loan_type_public_share.csv`: the tables.
