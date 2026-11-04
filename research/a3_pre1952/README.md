# A3: The public share before 1952

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A3. Status: built; review pending.** The project's series started in 1952Q1. It now runs from 1925: Z.1 annual levels for 1945–1951, and *Historical Statistics of the United States* (1975) for 1925–1944. Sources, hashes and quotes: [`sources.md`](sources.md). Table: [`public_share_1925_1952.csv`](public_share_1925_1952.csv), with a source and reliability label on every year.

## Result

**Before the Second World War the public share was far higher than in 1952.** It was zero until 1932, because no federal body held home mortgages. The Home Owners' Loan Corporation, created in June 1933, refinanced distressed home mortgages, and by 1935 public holders had 14.1% of household mortgages and consumer credit. The share then fell every year except 1942 as HOLC's book ran off, to 5.0% in 1944, 3.51% in 1945 and a low of 1.62% in 1947. It was back to 3.16% by 1952, where the quarterly series begins.

| Year | Public share | Source | Reliability |
|---|---|---|---|
| 1925–1932 | zero (no federal holder) | Historical Statistics | C |
| 1935 | 14.1% | Historical Statistics (HOLC, FNMA) | B |
| 1945 | 3.51% | Z.1 annual | A |
| 1947 | 1.62% | Z.1 annual | A |
| 1952 | 3.16% | Z.1 annual = Z.1 quarterly at 1952Q4 | A |

Reliability: **A** = Fed Z.1. **B** = federal holdings from HOLC and FNMA reports, total debt from Grebler, Blank and Winnick via *Historical Statistics*, which warns that these estimates "must be used with caution". **C** = zero by construction (no federal holder yet); state and local holdings are not measured in the source.

## Splice and checks

- **1945–1952 from Z.1 annual levels**, the same series and cells as A1. For every year both exist (81 years, 1945–2025), each annual level equals the Q4 quarterly level exactly, so the annual and quarterly series join with no adjustment (`z1_1945.py`).
- **1925–1944 from Historical Statistics**: public = HOLC (N 270) + FNMA (N 271); total = 1- to 4-family mortgage debt (N 273) + consumer credit (X 551). HOLC lent only on homes "for not more than four families" (Home Owners' Loan Act, sec. 2(c)), so the 1- to 4-family total is the matching denominator.
- **Overlap at 1945**, the one year both sources exist: Historical Statistics gives 3.54%, Z.1 gives 3.51%, a gap of 0.035 pp (tolerance 0.25 pp, asserted). The series switches source at 1945 with no rescaling; a ratio-adjusted variant is kept as a sensitivity column.

## Policy timeline (each date checked against the statute or an official report; `sources.md`)

| Date | Event | Source |
|---|---|---|
| 13 Jun 1933 | Home Owners' Loan Act: creates HOLC to refinance home mortgages | 48 Stat. 128, ch. 64 |
| 27 Jun 1934 | National Housing Act: creates the FHA (mortgage insurance) | 48 Stat. 1246, ch. 847 |
| 3 Feb 1938 | National Housing Act amendments (Title III, national mortgage associations) | 52 Stat. 8, ch. 13 |
| 10 Feb 1938 | First national mortgage association (later Fannie Mae) established by the RFC | FHLB Review, March 1938; RFC Final Report (1959) |
| 22 Jun 1944 | Servicemen's Readjustment Act: VA home-loan guaranty | 58 Stat. 284, ch. 268 |
| 15 Jul 1949 | Housing Act of 1949 | 63 Stat. 413, ch. 338 |
| 8 Nov 1965 | Higher Education Act: federally insured student loans (Title IV, Part B) | 79 Stat. 1219, P.L. 89-329 |
| 1 Aug 1968 | Housing and Urban Development Act: partitions FNMA into Fannie Mae and Ginnie Mae (Title VIII) | 82 Stat. 476, P.L. 90-448 |
| 24 Jul 1970 | Emergency Home Finance Act: Federal Home Loan Mortgage Corporation Act (Freddie Mac, Title III) | 84 Stat. 450 |

The 2008–2010 steps are in A1's `sources.md`.

## Limits

- **The points before 1945 are estimates by others.** The 1925–1952 totals in *Historical Statistics* come from Grebler, Blank and Winnick (NBER, 1956), which could not be reached (`www.nber.org` does not answer); the 1- to 4-family total is rounded to $0.1 billion.
- **What is missing before 1945.** State and local holdings, federal holdings of consumer credit, and farm mortgages (outside the project's scope throughout). Federal Land Bank farm loans are not household mortgages here, as in Z.1.
- **Holder, not risk.** FHA (from 1934) and VA (from 1944) insured or guaranteed loans held by private lenders are not counted, as in the rest of the project; by 1945 FHA-insured 1- to 4-family loans were $4.1 billion (N 274), so a risk-bearer measure would be much higher from the late 1930s.
- **Values read by hand.** Every Historical Statistics value was read from page images (170–200 dpi) of the FRASER copy; the transcription is in `hist_stats_1925_1945.csv`.
- **Fannie Mae was a federal agency until 1968**; Z.1 records it under the federal government until then, so the GSE share is zero before 1968.

## Files and how to rerun

```bash
uv run --project pipeline python research/a3_pre1952/z1_1945.py
uv run --project pipeline python research/a3_pre1952/pre1945.py
```
