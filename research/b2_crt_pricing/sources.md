# B2 sources

Checked with the `source-provenance` skill on 2026-11-04 by Claude. The PDFs are not committed. The verbatim text-layer lines that B2 parses are committed as `fixtures/fhfa_dec2016_tables.txt` (a US government work), with the PDF's SHA-256 in its header.

| Supports | Source | URL | Retrieved (UTC) | Bytes | SHA-256 | Quote |
|---|---|---|---|---|---|---|
| Deal tables (reference pool UPB, attach/detach, sold portion) and estimated credit costs and guarantee fees, CAS and STACR 2013–2016 | FHFA, *Credit Risk Transfer Progress Report*, December 2016, report pages 6, 9, 13, 14 | https://www.fhfa.gov/sites/default/files/2023-03/CRTProgressReport_Dec2016.pdf | 2026-11-04 04:57 | 545786 | `6cd3036812994ab3f6221cac523fea33decea9a9e75a0cc3b30b6a503fa9f615` | "Estimated credit costs as of the date of bond issuance, based on a hypothetical baseline scenario: Constant Prepayment Rate (CPR) =10%, Constant Default Rate (CDR) = 0.2%, Loss Given Default (LGD) =25%, early redemption at 10-year maturity. The calculations assume that 100% of the STACR/CAS notes are sold (no retention by the Enterprises)." Also: "STACR 2015-DNA1 and 2015-HQ2 are removed from this analysis because of their seasoned collateral which dramatically reduces the implied cost." |
| Issuance spreads after 2016 are charts only | FHFA, *CRT Progress Report*, 4Q 2023, Appendices D and E | https://www.fhfa.gov/sites/default/files/2024-04/CRT-Progress-Report-4Q23.pdf | 2026-11-04 04:57 | 888817 | `93502f0a134c78473a2cd5dd60f4bd06ff124f5cdfa2196e1462da7d373f0c40` | "Credit Spread at Issuance vs BBB Corporate Bond Index (bps)", a chart with deal letters and no values in the text. The 4Q18–4Q22 reports have the same appendices (same URLs as A2's `sources.md`). |
| CRT volumes by year (context) | A2, `research/a2_net_exposure/crt_fhfa.csv` (FHFA progress reports, transcribed by the analysis track) | see A2 `sources.md` | — | — | — | — |

## Checked and not used

| Wanted | Host | Status 2026-11-04 |
|---|---|---|
| Freddie Mac CRT deal data and issuance margins | crt.freddiemac.com | not reachable (proxy, code 000); host to add to Allowed domains |
| Fannie Mae CAS deal data | capitalmarkets.fanniemae.com, www.fanniemae.com | 000 / 403 |
| STACR and CAS offering documents on EDGAR | www.sec.gov, efts.sec.gov | 403 without a declared User-Agent. Eleonora's decision (PLAN.md) is to declare one through `SEC_USER_AGENT`, which is unset in this session |
| Secondary-market CRT spreads | Bloomberg, Intex, dealer runs | paywalled |

## Inconsistencies inside the source, kept as published
- **STACR 2016-DNA1** is dated 01/21/16 in the deal table and 01/01/16 in the credit-cost table. `deals.csv` keeps both and flags the row with `date_tables_disagree`.
- **CAS 2016-6** has no estimated credit cost: the cell is blank in FHFA's table. It is recorded as absent.
- **Two deal-table rows print no deal name** (CAS 2016-3 (1), STACR 2016-HQA4). They are matched by program, date, attach/detach and position; the match is asserted.
