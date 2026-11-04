# A8: Who bears household credit risk, US vs Canada, Denmark, UK, Germany

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A8. Status: partial.** Eleonora chose (2026-11-04) to show both measures, with the risk bearer as the headline. Only the US has a computable headline (b) share, and only Germany a computable holder (a) share; every other cell lacks one national figure and is recorded as missing ([`AVAILABILITY.md`](AVAILABILITY.md)). Definitions by country, checked against the sources where they could be reached: [`CROSSWALK.md`](CROSSWALK.md). Sources, hashes and quotes: [`sources.md`](sources.md), [`national_figures.csv`](national_figures.csv).

## Result

| | (b) Risk bearer: a public body takes the credit loss (headline) | (a) Holder: held by publicly owned lenders |
|---|---|---|
| **US**, end 2025 | 55.2% to 56.2% (public holders and guaranteed GSE/agency pools, net of CRT; A2) | not computable from Z.1 (see Limits); the project's public bucket, which counts guaranteed pools, is 56.4% |
| **Canada** | not computable; CMHC states it insures 19.8% of Canadian *residential* mortgages (31 Dec 2025) | not sourced |
| **Denmark** | not computable: state student loans not sourced; no public loss on mortgage-bank loans (Nationalbank, 2013) | not computable (student loans) |
| **UK** | not computable: student loans, Help to Buy equity loans and the Mortgage Guarantee Scheme not sourced | same |
| **Germany**, Q4 2025 | public share not computable: BAföG not sourced. Publicly owned banks are a separate third category, not part of this column (see below) | 30.3% (savings banks, Landesbanken and promotional banks) |

- **No ranking yet.** Only the US has a headline share, and every gap elsewhere (student loans in all four countries; private insurers' federally backed cover in Canada; UK schemes) can only raise the other countries' shares. The evidence so far is qualitative: in Denmark "the credit risk is initially borne by the mortgage bank" (Danmarks Nationalbank, 2013), on mortgage-bank loans that make up 80.4% of Danish bank and mortgage-bank loans to households; in KfW's home-ownership programme 124/134 the on-lending bank takes the liability ("die Haftung", KfW programme sheet, 2023); Canada's public exposure runs through mortgage insurance (CMHC's 19.8% is a share of residential mortgages, which include multi-unit rental, not of household credit).
- **The two measures diverge most in Germany.** Publicly owned banks hold 30.3% of bank lending to individuals. On the risk-bearer measure Eleonora classed this lending as a third category, *publicly owned, not guaranteed* (Q7, 2026-11-04). It has no US counterpart and is neither added to nor subtracted from a public share, so it is not comparable with the US 55.2% to 56.2% and Germany still has no headline number. The evidence ([`Q7_EVIDENCE.md`](Q7_EVIDENCE.md), Bundesbank): state guarantees for public-law banks ended in July 2005; BayernLB and HSH Nordbank were recapitalised by their Länder in 2008–09 and WestLB by the federal fund SoFFin; HSH losses were later settled under a state guarantee (Annual Report 2016). Those cases are Landesbanken; savings banks hold most of the category, and no public support for them was found. **Scope open:** the 2005 sources cover public-law banks (savings banks and Landesbanken, 29.1%); no source on guarantees for promotional banks (1.1%) was read, so their place in the category awaits Eleonora's confirmation. Public ownership of savings banks and Landesbanken is not sourced here either (only KfW's).

## Limits

- **US holder measure.** The GSEs' guaranteed MBS are mostly held by private investors, but since FAS 166/167 (2010Q1) Z.1 carries the Enterprises' consolidated trusts inside their own lines (A1), so retained holdings cannot be separated with the series used here. The US therefore has a risk-bearer share and no holder share.
- **Denominators differ.** Each country's total is its own national figure: StatCan national balance sheet (mortgages + consumer credit); Statbank DNMUDL bank and mortgage-bank loans to households; Bank of England lending to individuals excluding student loans; Bundesbank bank lending to employees and other individuals (excludes the self-employed and non-profits). None is harmonised with the US Z.1 scope.
- **Germany's holder share** leaves out public building-savings banks (Landesbausparkassen), which the Bundesbank table does not separate from private ones.
- **Dates.** Figures are end 2025 (Canada StatCan Q4 2025; CMHC 31 Dec 2025; Bundesbank Q4 2025). The qualitative statements are older: Danmarks Nationalbank 2013, KfW programme sheet 2023.
- **Re-checking.** Raw files are not committed; the hashes identify the copies read. The Bank of England query ends "Dateto=now" and the Statbank query is a POST, so a later download will differ; the exact Statbank query is in `sources.md`.

## Files and how to rerun

```bash
uv run --project pipeline python research/a8_international/compare.py
```

- `national_figures.csv`: every non-US figure, transcribed from its national source with URL, SHA-256 and the exact table cell or quote.
- `compare.py`: computes only shares with a national numerator and denominator; asserts URL and hash for every number, shares in [0, 1], and the US ordering.
- `comparison.csv`, `results.json`: outputs.
