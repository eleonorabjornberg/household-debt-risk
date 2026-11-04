# B2 sources

Checked with the `source-provenance` skill on 2026-11-04 by Claude. The PDFs are not committed. The verbatim text-layer lines that B2 parses are committed as `fixtures/fhfa_dec2016_tables.txt` (a US government work), with the PDF's SHA-256 in its header.

| Supports | Source | URL | Retrieved (UTC) | Bytes | SHA-256 | Quote |
|---|---|---|---|---|---|---|
| Deal tables (reference pool UPB, attach/detach, sold portion) and estimated credit costs and guarantee fees, CAS and STACR 2013–2016 | FHFA, *Credit Risk Transfer Progress Report*, December 2016, report pages 6, 9, 13, 14 | https://www.fhfa.gov/sites/default/files/2023-03/CRTProgressReport_Dec2016.pdf | 2026-11-04 04:57 | 545786 | `6cd3036812994ab3f6221cac523fea33decea9a9e75a0cc3b30b6a503fa9f615` | "Estimated credit costs as of the date of bond issuance, based on a hypothetical baseline scenario: Constant Prepayment Rate (CPR) =10%, Constant Default Rate (CDR) = 0.2%, Loss Given Default (LGD) =25%, early redemption at 10-year maturity. The calculations assume that 100% of the STACR/CAS notes are sold (no retention by the Enterprises)." Also: "STACR 2015-DNA1 and 2015-HQ2 are removed from this analysis because of their seasoned collateral which dramatically reduces the implied cost." |
| Issuance spreads after 2016 are charts only | FHFA, *CRT Progress Report*, 4Q 2023, Appendices D and E | https://www.fhfa.gov/sites/default/files/2024-04/CRT-Progress-Report-4Q23.pdf | 2026-11-04 04:57 | 888817 | `93502f0a134c78473a2cd5dd60f4bd06ff124f5cdfa2196e1462da7d373f0c40` | "Credit Spread at Issuance vs BBB Corporate Bond Index (bps)", a chart with deal letters and no values in the text. The 4Q18–4Q22 reports have the same appendices (same URLs as A2's `sources.md`). |
| CRT volumes by year (context) | A2, `research/a2_net_exposure/crt_fhfa.csv` (FHFA progress reports, transcribed by the analysis track) | see A2 `sources.md` | — | — | — | — |

## GSE 10-K aggregates for 2017–2023 (`gse_10k.py`, `freddie_crt_cost.csv`)
Freddie Mac 10-K PDFs from https://www.freddiemac.com/investors/financials/pdf/ (the files A2 fetched with `freddie_10k.py`; retrieved again 2026-11-04 ~21:20 UTC; SHA-256 equal to A2's record). Fannie Mae: EDGAR, not yet run.

| Filing | What is read | SHA-256 |
|---|---|---|
| 10k_021320.pdf | FY2019, Table 22 "Details of Single-Family Credit Enhancement Expense" (2017–2019) | `399cfcea93509f5834bbc0896e10ccaa3704109fd6bc7fb4589e78bc8aedb683` |
| 10k_021121.pdf | FY2020, Table 24 "Details of Single-Family Credit Enhancement Expenses and Recoveries" (2018–2020) | `d4392ce83e416dc7584bb464dbe495c5469903622f65211fa0c2890e26fe4e1b` |
| 10k_021022.pdf | FY2021, Table 12 "Single-Family Segment Financial Results", credit enhancement expense (2019–2021) | `6dc7ab061105f6fa8781c17f355357da6d9f983ca277b12e6ba1ee3988439f97` |
| 10k_022223.pdf | FY2022, consolidated non-interest expense, credit enhancement expense (2020–2022) | `0799b32511a8780fb63bee75b618021fa9ba406ac2c4de934755da3bd6999e88` |
| 10k_021424.pdf | FY2023, consolidated non-interest expense, credit enhancement expense (2021–2023) | `bf99cfd4c6f19e1a8871a118018737e0065cfe5240b83e16a8e6e7883f0c891f` |

What differs by year, kept as printed: 2017–2020 single-family, with interest on CRT debt (STACR debt notes) and the reinvestment offset; 2021 single-family credit enhancement expense only (CRT-debt interest not printed); 2022–2023 consolidated credit enhancement expense only (includes a small multifamily part: $48M of $1,518M in 2021). Restated values (2018: 402 → 394; 2019: 693 → 734) are kept in `latest_*` columns.

**Fannie Mae** 10-Ks from SEC EDGAR (CIK 0000310522), fetched 2026-11-04 ~21:22 UTC by `research/a2_net_exposure/fannie_10k.py`. The declared User-Agent was given per command only; per-request URL, status, bytes and SHA-256 are in `data/a2/fannie/fetch_log.json` (outside git, no User-Agent recorded). Every year printed by two filings agrees (checked by `gse_10k.py`). The FY2024 10-K does not print the table.

| Filing | What is read | Bytes | SHA-256 |
|---|---|---|---|
| fnma_10k_fy2017.htm | sentence (2017, 2016) | 10188398 | `4d55f8935dc73ee57af98cfb5bf69c00f36411d912a74508290756c0c5fa18f6` |
| fnma_10k_fy2018.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2018, 2017) | 12069724 | `0fe4fa81a0bae14ba1f6d5a5af9e8bd0c25d58a10331e12c06ba75624f39aac5` |
| fnma_10k_fy2019.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2019, 2018) | 12044201 | `78f253668b397bac705937f7b639d15a8a10bd096392eeb34f03ec69632d81e7` |
| fnma_10k_fy2020.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2020, 2019) | 9820122 | `b52b354ccefa04ca69b6c6d16914c6809adf2f6cca6bac258a69e94abd9206ab` |
| fnma_10k_fy2021.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2021, 2020) | 9613994 | `7212a7974035135c25107ce10ae826917ab72be2b73cf65798358037a9f45152` |
| fnma_10k_fy2022.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2022, 2021) | 9113995 | `45b10453011311d439777905ca84571c772b9769774f07d5fa1306c7dff18084` |
| fnma_10k_fy2023.htm | table "Credit Risk Transfer Transactions", cash paid or transferred (2023, 2022) | 17363248 | `85d2732f262e60f02690c0195edce69edd58fdf1efde742f5e03f0dae5e5ca90` |

Not like for like across the GSEs: Fannie's CAS cash is interest **net of LIBOR/SOFR** plus CAS REMIC and CLN payments; Freddie's 2017–2020 "interest expense related to CRT debt" is gross interest, with Freddie's own estimate of reinvestment income on the proceeds printed beside it.

## Checked and not used

| Wanted | Host | Status 2026-11-04 |
|---|---|---|
| Freddie Mac CRT deal data and issuance margins | crt.freddiemac.com, capitalmarkets.freddiemac.com | crt.freddiemac.com added to Allowed domains on 2026-11-04 (evening) but the proxy gateway answers 502 to CONNECT (20:39 and 21:17 UTC); capitalmarkets.freddiemac.com (where Freddie's investor page links CRT) gets no response (000). Whether deal data are free is unverified |
| Fannie Mae CAS deal data | capitalmarkets.fanniemae.com, www.fanniemae.com | 000 / 403 |
| STACR and CAS offering documents on EDGAR | www.sec.gov, efts.sec.gov | 403 without a declared User-Agent. Eleonora's decision (PLAN.md) is to declare one through `SEC_USER_AGENT`, which is unset in this session |
| Secondary-market CRT spreads | Bloomberg, Intex, dealer runs | paywalled |

## Inconsistencies inside the source, kept as published
- **STACR 2016-DNA1** is dated 01/21/16 in the deal table and 01/01/16 in the credit-cost table. `deals.csv` keeps both and flags the row with `date_tables_disagree`.
- **CAS 2016-6** has no estimated credit cost: the cell is blank in FHFA's table. It is recorded as absent.
- **Two deal-table rows print no deal name** (CAS 2016-3 (1), STACR 2016-HQA4). They are matched by program, date, attach/detach and position; the match is asserted.
