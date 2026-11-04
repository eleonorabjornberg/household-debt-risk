# B1 sources

Checked with the `source-provenance` skill on 2026-11-04 by Claude. Raw downloads are not committed (raw data stay out of git; the FRED series below belong to third-party publishers and are linked, not redistributed). Bytes and SHA-256 identify the exact copy read; `research/common/fred.py` writes the same fields to `data/fred/manifest.jsonl` on every download.

## Data series

All FRED requests: `https://api.stlouisfed.org/fred/series/observations?series_id=<ID>&file_type=json` (free API key; key not recorded). Retrieved 2026-11-04 00:56 UTC.

| Series | Publisher (via FRED) | Used as | Bytes | SHA-256 | Limit noted |
|---|---|---|---|---|---|
| `MORTGAGE30US` | Freddie Mac, Primary Mortgage Market Survey, weekly, 1971+ | S1 numerator | 276390 | `a1bfd1cd58cdb98beca492b1537a91d5da38353c89c9982aca9860070493cee6` | FRED notes: "On November 17, 2022, Freddie Mac changed the methodology of the Primary Mortgage Market Survey® (PMMS®). The weekly mortgage rate is now based on applications submitted to Freddie Mac from lenders across the country." |
| `DGS10` | Board of Governors (H.15), daily | S1 benchmark; controls | 1606453 | `7922b6e31f48d54967cd6308272124d942ac2ac44bb725a8154e08ab7f704018` | Constant-maturity yield |
| `DGS5` | Board of Governors (H.15), daily | 5y/10y blend benchmark | 1606299 | `85f30bcbcd9d321f08474eb0d4b369fef0f372d6713db4236112e6555f88a8f2` | |
| `T10Y2Y` | FRED-computed from H.15, daily | Slope control | 1250294 | `4ee8030dcac266d17577523df5af67a43a9a49fb01d67bedfef4ab6f017d338d` | |
| `BAA10Y` | Moody's, via FRED, daily, 1986+ | Corporate credit control | 1010783 | `b3312e57a5b0135aee0c785aa31a9552eed130c71efdd821c89f88857a703743` | © Moody's; sets the sample start (1986Q1) |
| `OBMMIJUMBO30YF` | Optimal Blue Mortgage Market Indices, daily, 2017+ | S2 (jumbo) | 245811 | `a88f545009d57cc873c4890caa8dea4bf43a56c4b946640904a98eb950d3ae43` | Locked rates, "over one-third of all mortgage transactions" (FRED notes); © Optimal Blue |
| `OBMMIC30YF` | Optimal Blue, conforming | S2 (base) | 245797 | `4cc0f901456c8e068e4f69cc0d2eed1a3185b3139ff1da1c5f637b60214e7281` | |
| `OBMMIFHA30YF` | Optimal Blue, FHA | FHA − conforming | 245781 | `74c44ad150adb363740c05ae5312fcc776a45b6a4a1f9ec43fe1acfd6441eea5` | |
| Z.1 `FRB_Z1_csv.zip` | Federal Reserve, Financial Accounts, release dated 2026-09-11 | Public share of 1–4 family household mortgages | 64219006 | `83b8eded0bc7f9b74c0269ef503a863cee88312460fd7eef076284b98fc28c06` | Same file and holder mapping as A1 and validation |

## Checked and not used

| Wanted | Source | URL | Bytes | SHA-256 | Finding |
|---|---|---|---|---|---|
| Jumbo vs conforming before 2017 | FHFA, "Update on the Discontinuation of FHFA's Monthly Interest Rate Survey (MIRS)" | https://www.fhfa.gov/DataTools/Downloads/Pages/Monthly-Interest-Rate-Data.aspx | 90541 | `09a05b6057ab3c4cf104bc879244dbd6dcb676998265c240ceca990825dec7f2` | "On May 29, 2019, FHFA published its final Monthly Interest Rate Survey (MIRS), due to dwindling participation by financial institutions." |
| Same | FHFA MIRS Table 26, "Terms on conventional single family mortgages, fixed-rate 30-year and 15-year nonjumbo loans" | https://www.fhfa.gov/sites/default/files/Table26-2019-by-Month.xls | 125440 | `77082efdaf91503fd7c25417c1648a36fa7c44d90f01f9121f21275973ab8bb0` | Monthly tables give non-jumbo loans only (Table 26) or all loans (Tables 17–25); a jumbo rate could be backed out only with assumptions about the mix, so it is not used. Possible extension for Eleonora to decide. |
| Agency MBS OAS, private-label RMBS spreads, MOVE index | Bloomberg, ICE, Yield Book, Intex | — | — | — | Paywalled. Proxies: S1, S2, realized 10-year volatility from `DGS10` |
| Freddie Mac PMMS page | https://www.freddiemac.com/pmms | — | — | — | Not reachable from the sandbox on 2026-11-04 (proxy, code 000); FRED's copy and notes used |
| ALFRED web pages | https://alfred.stlouisfed.org | — | — | — | Not reachable (code 000); the API host `api.stlouisfed.org` serves vintages and is used for C1 |
