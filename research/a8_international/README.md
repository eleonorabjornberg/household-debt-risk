# A8: Who bears household credit risk, US vs Canada, Denmark, UK, Germany

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A8. Status: partial.** Eleonora chose (2026-11-04) to show both measures, with the risk bearer as the headline. National sources give a computable share for two of the five countries; for the other three, one figure is missing and is recorded as missing ([`AVAILABILITY.md`](AVAILABILITY.md)). Definitions by country: [`CROSSWALK.md`](CROSSWALK.md). Sources, hashes and quotes: [`sources.md`](sources.md) and [`national_figures.csv`](national_figures.csv).

## Result, end of 2025

| | (b) Risk bearer: public body takes the credit loss (headline) | (a) Holder: held by publicly owned lenders |
|---|---|---|
| **US** | 55.2% to 56.2% (public holders, net of CRT; A2) | 56.4% (Z.1) |
| **Canada** | not computable; CMHC insures 19.8% of residential mortgages | not sourced |
| **Denmark** | mortgage-bank loans (80.4% of household loans): none; student loans not sourced | none found except student loans (not sourced) |
| **UK** | not computable: government student loans not sourced | same |
| **Germany** | none found for bank loans (KfW loans carry the on-lending bank's liability); student loans not sourced | 29.1% (savings banks and Landesbanken) |

- **The US is the outlier on the headline measure even before the gaps are filled.** In Denmark the mortgage bank, not the state, bears the loss on the loans that make up most household credit: "the credit risk is initially borne by the mortgage bank" (Danmarks Nationalbank). In Germany KfW's housing loans are passed through banks that take "die Haftung" (liability). Canada's public exposure runs through mortgage insurance: CMHC alone covers 19.8% of residential mortgages, before the federally backed cover of private insurers.
- **The holder measure misleads across systems.** Germany's publicly owned savings banks and Landesbanken hold 29.1% of bank lending to individuals, but public ownership does not guarantee the borrower's loan; on the risk-bearer measure that 29.1% is private risk.
- **Canada needs care.** CMHC's insurance-in-force includes multi-unit rental mortgages, which are not household debt, and the private insurers' federally backed cover is not sourced, so no Canadian share of household credit is computed.

## Limits

- **Student loans are the common gap.** The US share includes federal student loans; for Canada, Denmark, the UK and Germany the state's student-loan book is not sourced (official hosts blocked or no free stock figure), so their public shares are understated where shown.
- **Different denominators.** Each country's total comes from its own national source (StatCan national balance sheet; Statbank DNMUDL bank and mortgage-bank loans; BoE lending to individuals excluding student loans; Bundesbank bank lending to employees and other individuals). They are not harmonised; the BIS household-credit ratios on FRED are harmonised but give no public share.
- **US "risk bearer" is still a holder measure net of CRT.** FHA/VA-insured loans held by private lenders are not added back, and mortgage insurance is a separate line (A2).
- **Dates.** Year-end 2025 throughout (Canada StatCan Q4 2025, CMHC 31 Dec 2025).

## Files and how to rerun

```bash
uv run --project pipeline python research/a8_international/compare.py
```

- `national_figures.csv`: every non-US figure, transcribed from its national source with URL, SHA-256 and the exact table cell or quote.
- `compare.py`: computes only shares with a national numerator and denominator; asserts URL and hash for every number, shares in [0, 1], and the US ordering low ≤ high ≤ holder.
- `comparison.csv`, `results.json`: outputs.
