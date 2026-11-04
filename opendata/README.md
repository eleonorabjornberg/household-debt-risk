# Open data (PLAN F4)

The derived quarterly tables behind the charts, for anyone to download, with a data dictionary and
licence notes. Served by the story site at `/data` (page) and `/downloads/v1/` (files).

| File | What |
|---|---|
| `dictionary.json` | Source of truth: tables, columns, types, units, sources, validation status, licences, and what is not redistributed |
| `archive/z1-<date>/` | Every published Z.1 vintage's snapshots, gzipped (F4-3). Written by `archive.mjs`; never overwritten |
| `archive.mjs` | Archives the current snapshots (`make ingest` runs it); fails if an archived vintage would change |
| `CHANGELOG.md` | Changes to the `v1` download contract and each archived release |
| `sources.md` | Provenance of the licence terms relied on (URL, retrieval time, bytes, SHA-256, quoted passage) |
| `api-plan.md` | Public read-only API: option A (static versioned downloads) chosen 2026-11-04; B later; never C |

## How the files are built

`web/scripts/make-downloads.mjs` runs before every web build (`npm run build`). It copies
`dictionary.json` to `web/lib/opendata.json` (committed, so the `/data` page builds from the `web/` folder
alone) and writes `web/public/downloads/v1/` (gitignored):

```
v1/index.json                         every release and file
v1/latest/<table>.csv|json            from the committed snapshots in web/public/data (what the charts show)
v1/latest/dictionary.json, LICENSE-DATA.md, NOTICE-nyfed.txt
v1/vintages/z1-<date>/...             the same files for each release in archive/
```

- `<table>.csv` and `<table>.json` for every table; the JSON carries the licence, attribution, source
  identifier, source vintages and column dictionary with the rows;
- `dictionary.json` (with vintages, CPI base quarter and row counts), `LICENSE-DATA.md`, and for the NY Fed
  table `NOTICE-nyfed.txt` with the attribution and source identifier their terms require.

`v1` is a contract: file names and columns under it change only with a new version, recorded in
`CHANGELOG.md`. The site built from `web/` alone (no repo root) publishes `latest/` only.

The build fails if a snapshot has a column the dictionary does not describe. `node web/scripts/make-downloads.mjs --check`
(in `make ci-static` and CI) fails if `web/lib/opendata.json` is stale.

## Licences

- **Code: MIT.**
- **Derived tables: CC BY 4.0.** The Fed Board's Z.1 data are in the public domain ("may be copied and
  distributed without permission. Please cite to the Board as the source"); CPI (BLS) and DSPI (BEA) via
  FRED are public domain with citation requested. Our apportionment, classification and imputation are
  licensed CC BY 4.0 with an attribution line that cites the Board and FRED.
- **NY Fed Household Debt and Credit: redistributed under the NY Fed's own terms, not relicensed**
  (decision F4-1, 2026-11-04). Their Terms of Use require anyone who redistributes their content to keep
  the same permissions and restrictions, their attribution line and the source identifier, so
  `nyfed_by_type` cannot go out under CC BY 4.0. It ships with "© 2026 Federal Reserve Bank of New York.
  Content from the New York Fed subject to the Terms of Use at newyorkfed.org." and "Source: New York Fed
  Consumer Credit Panel/Equifax" (in the JSON, `LICENSE-DATA.md`, `NOTICE-nyfed.txt` and on `/data`). Checked
  on 2026-11-04: `HHD_C_Report_2026Q2.xlsx` (962,992 bytes, SHA-256 ddfba16b…d99237) has no use restriction
  beyond the general terms; its only notice is that source line (see `sources.md`).
- **Case-Shiller (CSUSHPINSA): not redistributed.** S&P's copyright; FRED says copyrighted series need the
  owner's permission beyond personal use. It is in no download.

## Accessible chart descriptions

Every chart on both sites has a text description: each web chart is an SVG with `role="img"`, `<title>`
and a `<desc>` built from the data, and four of the five figures also offer "Show the data as a table".
The atlas canvas has a data-driven `aria-label`, a live text summary of the current quarter and a
by-decade table. `tools/check_chart_text.mjs` enforces this after every build (`make f1-links`, CI).
Static figures for the paper get alt text from the `chart-from-sql` skill.
