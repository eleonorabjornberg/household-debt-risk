# C1 sources

Checked with the `source-provenance` skill on 2026-11-04 by Claude. Raw downloads are not committed: they are cached in `data/fred/`, and `data/fred/manifest.jsonl` records each one. Bytes and SHA-256 identify the exact copy read. All requests go to `https://api.stlouisfed.org/fred/` and need a free API key (not recorded). The real-time window is `realtime_start=1776-07-04&realtime_end=9999-12-31`, so every vintage comes back.

## ALFRED real-time vintages

| Series | ALFRED request | Retrieved (UTC) | Bytes | SHA-256 |
|---|---|---|---|---|
| `HMLBSHNO` (values, all vintages) | series/observations?series_id=HMLBSHNO&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:07:08+00:00 | 361976 | `4d323c606fea1172c82fc72602ddc57b8bc6b8fddc15407f737c41abc3d3e65f` |
| `HMLBSHNO` (units by vintage) | series?series_id=HMLBSHNO&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:07:08+00:00 | 7821 | `e31eea2b0e2f5625becdbfb98204e296972471fcaa73a77fe0d4a54703288da7` |
| `CCLBSHNO` (values, all vintages) | series/observations?series_id=CCLBSHNO&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:07:09+00:00 | 160386 | `56b4bb20fbad57fb6f6a75fd24f543504566af66f54a522357fd52bfc4f8fe53` |
| `CCLBSHNO` (units by vintage) | series?series_id=CCLBSHNO&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:07:09+00:00 | 7733 | `9ceeb23fb1ae8324e2552deb13a9bc2e97b732f6db83167514d83091dc0becda` |
| `BOGZ1FL154104015Q` (values, all vintages) | series/observations?series_id=BOGZ1FL154104015Q&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:07:10+00:00 | 169116 | `94207f511a2e08d739abc6c518ba9289020c5053463125ce607d94853131fa52` |
| `BOGZ1FL154104015Q` (units by vintage) | series?series_id=BOGZ1FL154104015Q&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:07:11+00:00 | 7041 | `85da61f24289b1f5f59b88f3dbcd8d18ba88b581154fbe146d712b2a43944fbe` |
| `BOGZ1FL413065105Q` (values, all vintages) | series/observations?series_id=BOGZ1FL413065105Q&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:02+00:00 | 33851 | `620b03c1ff32e5cf64ed0cd6056d8846978d41e9b80ce74c8a3984e1b53ef04b` |
| `BOGZ1FL413065105Q` (units by vintage) | series?series_id=BOGZ1FL413065105Q&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:33+00:00 | 5749 | `e8912b97884c96fe06fd88b1ffc8073ba760e97ae4afec398e449d81c586ecdf` |
| `BOGZ1FL403065105Q` (values, all vintages) | series/observations?series_id=BOGZ1FL403065105Q&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:02+00:00 | 41988 | `bc137a17847a3bb25b48e0ad9b1ab0e6317c525a5538328ea9302a6d53166167` |
| `BOGZ1FL403065105Q` (units by vintage) | series?series_id=BOGZ1FL403065105Q&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:34+00:00 | 6861 | `66b6b6175cf3010047ff89f70d00060a91e0f7c61b4e3f3cb90fc3346e277c66` |
| `FGCCSAQ027S` (values, all vintages) | series/observations?series_id=FGCCSAQ027S&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:03+00:00 | 41742 | `f58498ab25d53e921818abb255153e443457266b06fca1fc7f6a9c5505091e20` |
| `FGCCSAQ027S` (units by vintage) | series?series_id=FGCCSAQ027S&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:34+00:00 | 7496 | `4da3731787780f3fbd59ce6308e5977027e4572dd49cd2e7478145ab86d3ac82` |
| `TOTALNS` (values, all vintages) | series/observations?series_id=TOTALNS&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:04+00:00 | 1124008 | `2b52dcb26df76b06b164fb4abe671d6d6085b8d8b872e7da0c3c47596f00eabe` |
| `TOTALNS` (units by vintage) | series?series_id=TOTALNS&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:35+00:00 | 2008 | `723011fcbad8ef585cdf2374da00d640b923f3ef08fe3b4159fb1104122370b6` |
| `TOTALGOV` (values, all vintages) | series/observations?series_id=TOTALGOV&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:04+00:00 | 259629 | `400abb0aea9583f61a651539f215e2afbf8e39ac18c9fc6e6a8545a053359a6c` |
| `TOTALGOV` (units by vintage) | series?series_id=TOTALGOV&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:36+00:00 | 3108 | `216ff3bb4f7402d4febfd1fd7212517404830715a9b3e0b570fdf7525a52a916` |
| `TOTALDI` (values, all vintages) | series/observations?series_id=TOTALDI&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:05+00:00 | 537253 | `ee95fbf5a3c74a98daf665ee359c69b8ef4b74a997d5e3e3bf839a5b72c716b0` |
| `TOTALDI` (units by vintage) | series?series_id=TOTALDI&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:37+00:00 | 2322 | `36ab0fb342e4a1beec4f0c323d7d92512419bf6e97afcf53f8e4cee2df4f30d7` |
| `TOTALFC` (values, all vintages) | series/observations?series_id=TOTALFC&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:06+00:00 | 392418 | `8d8435872aee2b0c2c54b176136d8bf10456b4c6c0cf096a7f57ca3efb6ea8df` |
| `TOTALFC` (units by vintage) | series?series_id=TOTALFC&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:37+00:00 | 2020 | `79444fa586eb89541719084dbcab31f19f060d773db3cea5f19d84d662fdbece` |
| `TOTALTCU` (values, all vintages) | series/observations?series_id=TOTALTCU&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:06+00:00 | 375457 | `fc22ff69ae2965384e2b602edfd96f766aace133e3da85702dea18bc4961180f` |
| `TOTALTCU` (units by vintage) | series?series_id=TOTALTCU&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:38+00:00 | 2011 | `512e18acd05308e1d36b443dbef10e43108388583adc42192d94099e731b280b` |
| `RREACBW027NBOG` (values, all vintages) | series/observations?series_id=RREACBW027NBOG&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:07+00:00 | 1643079 | `9afa9cb59ee75ea0e1d533075ccc7ce18d8a9e9a9df430c62a111f21497c2475` |
| `RREACBW027NBOG` (units by vintage) | series?series_id=RREACBW027NBOG&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:38+00:00 | 1421 | `74e7852651e126d6e0ce26441e423088f0e454e92d59d81e28cdeed61e36bb5f` |
| `CLSACBW027NBOG` (values, all vintages) | series/observations?series_id=CLSACBW027NBOG&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:09+00:00 | 2593530 | `061bc86aa39e7f119e489164ba9e4d2270f60be73d4bbe4e7e795aa708585f87` |
| `CLSACBW027NBOG` (units by vintage) | series?series_id=CLSACBW027NBOG&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:38+00:00 | 1389 | `29a16e3a9a812b45ddf8932df958ed7e9f981480d187a6c3d8022cc10e36255b` |
| `WSHOMCB` (values, all vintages) | series/observations?series_id=WSHOMCB&realtime_start=1776-07-04&realtime_end=9999-12-31&output_type=1&limit=100000&file_type=json | 2026-11-04T01:02:09+00:00 | 121071 | `85ccc47f17e74a363c327d8c7c09aaf8580297fd71106929defec51a9d83bda4` |
| `WSHOMCB` (units by vintage) | series?series_id=WSHOMCB&realtime_start=1776-07-04&realtime_end=9999-12-31&file_type=json | 2026-11-04T01:05:39+00:00 | 2125 | `5507d46e8f4df8962f1195c5bcbe1a26134da8cee493216ddabd17b5ce469112` |

**Unit changes inside ALFRED.** These come from the series metadata by vintage, in the "units by vintage" rows above. G.19 series moved from "Billions of Dollars" to "Millions of Dollars" with the 2025-02-07 vintage (`TOTALNS`: billions to 2025-02-06). Z.1 series on FRED moved with the 2026-01-09 vintage (`HHMSDODNS`, the SA mortgage series, checked: billions to 2026-01-08; the NSA `HMLBSHNO` used here is rescaled the same way). H.8 series are still labelled billions. `fred.to_millions` rescales each vintage row by the label in force on the day it was published. Without that rescaling, a naive comparison of vintages reads as a 99.9% revision.

## Target vintages before 2019

ALFRED holds vintages for the Z.1 holder series (`BOGZ1…`) only from 2019-03-07. The Fed keeps every past Z.1 release under `https://www.federalreserve.gov/releases/z1/<YYYYMMDD>/`. A HEAD request on 2026-11-04 to one release in six from the ALFRED calendar found:

| Release | `z1_csv_files.zip` | `z1r-1.zip` (fixed-width .prn tables) |
|---|---|---|
| 2010-06-10, 2013-03-07, 2014-09-18, 2016-03-10 | 404 | 200 |
| 2011-09-28 | 404 | 404. This date came from the first calendar, built from `HHMSDODNS` ALFRED vintages; it is an ALFRED vintage, not a Z.1 release. The release is 2011-09-16 (current calendar, from `HMLBSHNO`), not rechecked. |
| 2017-09-21, 2019-03-07, 2020-09-21, 2022-03-10, 2023-09-08, 2025-03-13, 2026-09-11 | 200 | 404 |

So real-time target vintages look possible back to 2010: CSV from 2016-09-16, `z1r-N` text archives before. None of these files has been parsed yet. Which target vintage to use is one of the design questions in `tracks/markets.md`.

## Release archive actually used (`z1_vintages.py`)

All 41 Z.1 releases from 2016-09-16 to 2026-09-11 were downloaded as `z1_csv_files.zip`. Each one's URL, byte count, SHA-256 and retrieval time are in `data/z1_archive/manifest.jsonl`; the per-release cell codes are in `z1_vintage_notes.csv`. One folder is not named after its release date: the 2017-03-09 release (2016Q4) is in `releases/z1/20170305/` (6249231 bytes, SHA-256 `1b730b3a987f1401a72708e0a1566d3382bc8c1cec184afe6c6f4df89bf2bf74`), confirmed by its last quarter. The skeptic found it (R-20261104-mkt-s9).

## Agency monthly summaries

| Source | URL | Status 2026-11-04 |
|---|---|---|
| Ginnie Mae monthly summary reports | https://www.ginniemae.gov/data_and_reports/reporting/Pages/monthly_summary_reports.aspx | 200; not parsed; no real-time vintages (point in time only from the report date) |
| Ginnie Mae Global Markets Analysis | https://www.ginniemae.gov/data_and_reports/reporting/Pages/global_market_analysis.aspx | 200; not parsed |
| Freddie Mac monthly volume summaries | https://www.freddiemac.com/investors/financials/monthly-volume-summaries | not reachable (proxy, code 000); host to add to Allowed domains |
| Fannie Mae monthly summary | https://www.fanniemae.com/about-us/investor-relations/monthly-summary | not reachable (code 000); host to add |
