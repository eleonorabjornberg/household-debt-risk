# A5 availability note (written before any analysis)

Checked 2026-11-04, about 01:00 UTC, from this environment. Hashes and quotes: [`sources.md`](sources.md).

| Need | Source | Free? | Reachable? | Granularity | Use in A5 |
|---|---|---|---|---|---|
| Who borrows, by wealth, income, age, race, education, generation | Fed **Distributional Financial Accounts** (`dfa.zip`, files dated 2026-09-15) | yes | yes | national; quarterly 1989Q3–2026Q2; liabilities split into home mortgages, consumer credit, other | main source for the borrower side |
| Who borrows, by state | NY Fed **State Level Household Debt Statistics 2003–2025** (`area_report_by_year.xlsx`, Feb 2026; CCP/Equifax) | yes | yes | 50 states + DC; Q4 each year 2003–2025; balance per capita by type (mortgage excl. HELOC, auto, card, student, total) and 90+ day delinquency | state tables and tile maps |
| Student loans by state | NY Fed `student-loan-by-state.xlsx` (CCP/Equifax) | yes | yes | states; borrowers, average balance, delinquency; includes private student loans | state view of a mostly federal loan type |
| County level | NY Fed databank lists "County level" under the 2018 state statistics, but with no download link (2026-11-04) | — | no file found | — | **not used**: every geographic claim stays at state level (PLAN A5) |
| CCP microdata | NY Fed Consumer Credit Panel | no (not public) | — | — | not used |
| Income by state | Census ACS | yes | `www.census.gov` answers 200; `api.census.gov` and `www2.census.gov` are refused by the network policy | — | not used yet; state per-capita debt is shown without an income denominator |
| Who holds (and so carries) the risk by loan type | Fed Z.1 (have, vintage 2026-09-11) | yes | yes | national, by holder and loan type | public share by loan type |

**What is not available anywhere free:** a table that crosses borrower group (wealth, income, state) with the holder of the loan. The DFA splits liabilities by borrower but not by holder; Z.1 splits by holder but not by borrower; the NY Fed state data split by loan type but not by holder. Any "public exposure by borrower group" is therefore an **imputation** across sources, and the assumption it rests on is a design choice for Eleonora (`tracks/analysis.md`, Q4).

**Sampling.** The NY Fed state figures come from a 5% sample (1% for student loans); the NY Fed notes that "national and state totals here may not match those reported in the Quarterly Report on Household Debt and Credit."
