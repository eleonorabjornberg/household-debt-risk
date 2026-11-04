# B3 sources

Checked with the `source-provenance` skill on 2026-11-04 by Claude. The PDF is not committed.

| Supports | Source | URL | Retrieved (UTC) | Bytes | SHA-256 | Quote |
|---|---|---|---|---|---|---|
| DFAST preset loss rates | Board of Governors of the Federal Reserve System, *2026 Supervisory Stress Test Results*, June 2026, Table 9, report page 21 (PDF page 27); checked against the rendered page | https://www.federalreserve.gov/publications/files/2026-dfast-results-20260624.pdf | 2026-11-04 16:55 | 2099540 | `aeecec4fa0f8872601d5d8f02f515520fdc302b61f934e24131147dfd7d6fbef` | "Table 9. Projected aggregate loan losses, by type of loan, under the severely adverse scenario, 2026:Q1–2028:Q1". Portfolio loss rates (percent): first-lien mortgages, domestic 1.5; junior liens and HELOCs, domestic 3.2; credit cards 17.1; other consumer 7.3. Footnotes: "Other consumer loans include student loans and automobile loans." "The loss rate is calculated as total projected loan losses over the nine quarters of the projection horizon divided by average loan balances over the horizon." |
| Exposures and consumer-credit mix | Fed Z.1, `FRB_Z1_csv.zip` dated 2026-09-11 (as validation) | https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip | 2026-11-04 | 64219006 | `83b8eded0bc7f9b74c0269ef503a863cee88312460fd7eef076284b98fc28c06` | Series FL153166100, FL153166400, FL153166220, FL153166205, FL313066220 |

## Limits of the proxy
- DFAST covers the largest banks' own portfolios. GSE, FHA/VA, federal and state books have different borrowers and terms, so applying bank loss rates to them is a proxy.
- Z.1's 1–4 family mortgages include junior liens and HELOCs (3.2% in DFAST). The preset uses the first-lien rate (1.5%) for all mortgages, which understates.
- DFAST publishes nine-quarter totals, not a path. The preset spreads losses evenly over nine quarters (an assumption).
- Federal student loans are not in DFAST. They are absent from the main preset; a variant applies the "other consumer" rate (a weak proxy, since bank "other consumer" is mostly auto loans).
