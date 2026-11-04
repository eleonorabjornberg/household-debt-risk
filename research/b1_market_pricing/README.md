# B1: Did the public takeover compress the price of household credit risk?

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task B1. Status: analysis done, ready for review; write-up is a Claude draft.** Specification fixed before any result in [`METHOD.md`](METHOD.md); sources and hashes in [`sources.md`](sources.md); code `b1.py` (tests `test_b1.py`, HAC errors checked against statsmodels).

Data: Fed Z.1 dated 2026-09-11; FRED retrieved 2026-11-04. Sample 1986Q1–2026Q2, quarterly. Every number in this file has a row in `claims/tracks/markets.csv`.

## Result

**No robust association.** With rate level, rate volatility, curve slope, the corporate Baa spread and a refinancing proxy held fixed, the mortgage-rate spread over Treasuries does not move with the public share of household mortgages in a way that survives the pre-registered checks:

| Specification | Coefficient on public share (pp of spread per unit of share) | 95% HAC interval |
|---|---|---|
| Levels, main | 1.22 | 0.17 to 2.26 |
| First differences, main | −0.08 | −3.66 to 3.49 |
| Levels, sample ends 2022Q3 (before the PMMS method change) | −0.31 | −1.10 to 0.47 |

The levels coefficient is positive (a higher public share goes with a *wider* spread, about 1.2 bp per percentage point of share), but it loses significance when the sample stops before Freddie Mac's November 2022 change to the PMMS method, and the first-differences estimate is centred on zero with a wide interval. By the reading rule fixed in `METHOD.md` (compression needs a negative coefficient whose interval excludes zero in both levels and differences), every variant reads "no robust association": main, headline share instead of mortgage share, 5y/10y Treasury blend, and the pre-2022Q4 sample. All coefficients are in `regressions.csv`.

**Descriptive means** (`spreads_summary.csv`):

| Period | Public share of household mortgages (mean) | 30-year mortgage rate − 10-year Treasury (mean) |
|---|---|---|
| 1986Q1–2008Q2 | 48.6% | 1.66 pp |
| 2008Q3–2019Q4 | 59.9% | 1.73 pp |
| 2020Q1–2026Q2 | 66.5% | 2.27 pp |

The share rose by about 18 points across the three periods; the spread did not fall. The 2020s rise in the spread lines up with rate volatility (the volatility control is positive and significant in every specification), not with the public share.

**Agency versus privately held credit risk, 2017–2026 only.** The jumbo − conforming 30-year rate (Optimal Blue) averaged 0.03 pp, ranging from −0.48 to 0.38 pp by quarter. Loans that the GSEs cannot guarantee were not priced materially above loans they can. FHA − conforming averaged −0.05 pp. Ten years with an almost flat public share is too short for a regression, so this stays descriptive.

## What this does and does not show

- **The proxies are not the price of credit risk.** The PMMS spread bundles the guarantee fee (set by Fannie, Freddie and FHFA, not by a market), the prepayment option, servicing and originator margins, and the agency MBS spread. For most of the sample the credit risk in it is priced by a public guarantor, administratively. A flat spread therefore cannot tell "risk compressed" apart from "risk priced by fiat at a stable fee". Agency MBS option-adjusted spreads and private-label spreads would separate these, but they are paywalled (Bloomberg, ICE, Intex).
- **The jumbo comparison is confounded.** Jumbo borrowers have higher incomes and credit scores, and banks compete for them as relationship clients, so a near-zero jumbo − conforming spread is not evidence that private and public prices for the *same* risk are equal.
- **Association, not cause.** The public share moved with the 2008 crisis, which also moved every control. Nothing here identifies a causal effect; A7 is where that would come from.
- **One plausible proxy gap.** FHFA's MIRS (discontinued May 2019) has non-jumbo rates back to the 1980s but no jumbo table; backing a jumbo rate out of the all-loans table would need assumptions about the loan mix. Left as a possible extension.

## Reproduce

```bash
uv run --project pipeline python validation/run.py          # downloads the Z.1 zip to data/validation/
uv run --project pipeline python research/b1_market_pricing/b1.py   # needs FRED_API_KEY
uv run --project pipeline pytest -q research/b1_market_pricing
```
The quarterly panel goes to `data/b1/panel.csv` (outside git: third-party rates are linked, not redistributed).
