# A8 availability note (written before any analysis)

Checked 2026-11-04, 00:52 and 01:10 UTC, from this environment. A 403 on CONNECT from the proxy means the network policy refuses the host (`/root/.ccr/README.md`); hosts were not retried with other user agents.

## What A8 needs

A comparable **public (or publicly guaranteed) share of household credit** for the US, Canada, Denmark, the UK and Germany: a numerator (household debt held or guaranteed by the state, by each country's own definition) and a denominator (total household credit).

## Denominator: available

| Series | Source | Reachable | Coverage |
|---|---|---|---|
| Total credit to households and NPISHs, adjusted for breaks (BIS, via FRED): `QCAHAM770A`, `QDKHAM770A`, `QGBHAM770A`, `QDEHAM770A`, `QUSHAM770A` | BIS total credit statistics, republished by FRED (`api.stlouisfed.org`) | yes | quarterly to 2025Q4; from 1969 (CA), 1994 (DK), 1966 (UK), 1970 (DE), 1947 (US) |

These are comparable across countries by construction (the BIS harmonises them). They include NPISHs, unlike the project's US scope, which is households only (Z.1); the US gap between the two is to be measured, not assumed.

## Numerator: blocked

| Country | Primary source for the public/guaranteed part | Host | Status 2026-11-04 |
|---|---|---|---|
| Canada | CMHC mortgage insurance in force; NHA MBS and Canada Mortgage Bonds outstanding; OSFI and Bank of Canada data on insured mortgages | `www.cmhc-schl.gc.ca`, `www.osfi-bsif.gc.ca`, `www.bankofcanada.ca`, `www150.statcan.gc.ca`, `www.canada.ca` | refused (403) |
| Denmark | Mortgage-bank (realkredit) lending and covered bonds outstanding; any state guarantee | `www.nationalbanken.dk`, `www.statbank.dk`, `api.statbank.dk`, `www.dst.dk`, `www.finanstilsynet.dk` | refused (403) |
| UK | Bank of England mortgage lending statistics; government schemes (Help to Buy equity loans, Mortgage Guarantee Scheme) | `www.bankofengland.co.uk`, `www.gov.uk`, `www.ons.gov.uk`, `www.fca.org.uk`, `www.ukfinance.org.uk` | refused (403) |
| Germany | Bundesbank household lending; KfW promotional loans; Bausparkassen | `www.bundesbank.de`, `www.kfw.de`, `www.destatis.de` | refused (403) |
| Cross-country | BIS, ECB, Eurostat, OECD, IMF, World Bank, European Mortgage Federation (HYPOSTAT), European Covered Bond Council | `www.bis.org`, `data.bis.org`, `stats.bis.org`, `www.ecb.europa.eu`, `data.ecb.europa.eu`, `data-api.ecb.europa.eu`, `ec.europa.eu`, `sdmx.oecd.org`, `www.imf.org`, `data.imf.org`, `api.worldbank.org`, `hypo.org`, `www.ecbc.eu` | refused (403) |

PLAN.md "Environment prerequisites" lists CMHC, Bank of England, Bundesbank, Statbank DK, BIS and ECB as reachable on 2026-11-03. They are not reachable from this session on 2026-11-04.

**Free proxy?** None found for the numerator. FRED carries the BIS credit totals but no series on who holds or guarantees household credit in these countries. A numerator built from anything else would be an imputation without a national source, which PLAN A8 rules out ("no figure without its national source").

## What would unblock A8

Add to Allowed domains (environment settings → Network), at minimum: `www.cmhc-schl.gc.ca`, `www150.statcan.gc.ca`, `www.bankofcanada.ca`, `www.nationalbanken.dk`, `api.statbank.dk`, `www.bankofengland.co.uk`, `www.bundesbank.de`, `www.kfw.de`, `data.bis.org`, `data-api.ecb.europa.eu`. Or download the national tables by hand and drop them in `data/a8/` (the script would record hashes).
