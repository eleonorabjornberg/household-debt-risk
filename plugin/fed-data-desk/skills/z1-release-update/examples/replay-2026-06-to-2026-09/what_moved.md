# What moved: 2026-06-10 to 2026-09-11

Previous vintage: 2026-06-10 (latest quarter 2026Q1). Current vintage: 2026-09-11 (latest quarter 2026Q2). Scope is 1-4 family mortgages plus consumer credit of households and nonprofits; public = federal, GSE and agency pools, state and local holders. Computed from the raw Z.1 files; figures are not edited.

## New quarters

2026Q2

## Headline, 2026Q2

| Measure | Level | q/q | y/y |
|---|---|---|---|
| Public share of scope | 56.4% | -0.2 pp | -0.2 pp |
| Public debt | $10.77T | +$0.07T | +$0.26T |
| Scope total | $19.10T | +$0.20T | +$0.53T |

q/q is against 2026Q1, y/y against 2025Q2, both as published in the current vintage (so they include revisions).

## Risk buckets, share of scope, 2026Q2

| Bucket | Share | q/q | y/y |
|---|---|---|---|
| federal_direct | 8.8% | -0.1 pp | +0.1 pp |
| gse_agency | 47.0% | -0.1 pp | -0.3 pp |
| state_local | 0.6% | 0.0 pp | 0.0 pp |
| banks_credit_unions | 33.6% | +0.2 pp | +0.1 pp |
| private_securitization | 3.6% | +0.1 pp | +0.4 pp |
| nonbank_other | 6.4% | -0.1 pp | -0.2 pp |

## Revisions to history

297 quarters are in both vintages (1952Q1 to 2026Q1). 5 moved by at least 0.05 pp of public share or $1,000M of scope or public debt. The 5 largest, ranked by the biggest move relative to those thresholds:

| Quarter | Share prev | Share now | Change | Scope change ($M) | Public change ($M) |
|---|---|---|---|---|---|
| 2025Q3 | 56.62% | 56.60% | -0.02 pp | +5,272 | -956 |
| 2026Q1 | 56.60% | 56.59% | -0.01 pp | +4,651 | +1,623 |
| 2025Q4 | 56.41% | 56.39% | -0.02 pp | +4,544 | -1,350 |
| 2025Q2 | 56.64% | 56.63% | -0.01 pp | +3,465 | -637 |
| 2024Q4 | 56.72% | 56.73% | +0.01 pp | -1,811 | -6 |

Largest absolute share revision: 0.021 pp in 2025Q3. (Revision table uses two decimals so small moves are visible.)

## Validation flags

Summary: 41 PASS, 0 FAIL, 2 WARN, 1 NOT RUN.

| Check | Status | Observed |
|---|---|---|
| D2 mart.public_share (database) vs recomputation | NOT RUN | DATABASE_URL_READONLY not set |
| E8 Other quarter-on-quarter jumps in component shares (robust z > 6, >= 1.0 pp) | WARN | 93 unexplained (+12 at known breaks) of 32 series |
| F1 Scope total FL154104015 revisions, 1952Q1-2026Q1 (297 qtrs) | WARN | 19 quarters revised > $0.5M; max |rev| $5,272M in 2025Q3 |

Unexplained component-share jumps (E8): 93 in the whole history, 0 in the last five quarters.
