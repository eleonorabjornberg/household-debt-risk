# Open data (PLAN F4)

The derived quarterly tables behind the charts, for anyone to download, with a data dictionary and
licence notes. Served by the story site at `/data` (page) and `/downloads/` (files).

| File | What |
|---|---|
| `dictionary.json` | Source of truth: tables, columns, types, units, sources, validation status, licences, and what is not redistributed |
| `sources.md` | Provenance of the licence terms relied on (URL, retrieval time, bytes, SHA-256, quoted passage) |
| `api-plan.md` | Options for a public read-only API, for Eleonora to choose. Nothing is exposed until she approves |

## How the files are built

`web/scripts/make-downloads.mjs` runs before every web build (`npm run build`). It copies
`dictionary.json` to `web/lib/opendata.json` (committed, so the `/data` page builds from the `web/` folder
alone) and writes `web/public/downloads/` (gitignored) from the committed snapshots in
`web/public/data/`, the same files the charts read:

- `<table>.csv` and `<table>.json` for every table with `redistribute: true`; the JSON carries the licence,
  attribution, source vintages and column dictionary with the rows;
- `dictionary.json` (with vintages, CPI base quarter and row counts) and `LICENSE-DATA.md`.

The build fails if a snapshot has a column the dictionary does not describe. `node web/scripts/make-downloads.mjs --check`
(in `make ci-static` and CI) fails if `web/lib/opendata.json` is stale.

## Licences

- **Code: MIT.**
- **Derived tables: CC BY 4.0.** The Fed Board's Z.1 data are in the public domain ("may be copied and
  distributed without permission. Please cite to the Board as the source"); CPI (BLS) and DSPI (BEA) via
  FRED are public domain with citation requested. Our apportionment, classification and imputation are
  licensed CC BY 4.0 with an attribution line that cites the Board and FRED.
- **NY Fed Household Debt and Credit: not relicensed.** The NY Fed's Terms of Use require anyone who
  redistributes its content to keep the same permissions and restrictions and its attribution line, so
  it cannot go out under CC BY 4.0. `nyfed_by_type` is link-only until Eleonora decides (question F4-1 in
  `tracks/infra.md`).
- **Case-Shiller (CSUSHPINSA): not redistributed.** S&P's copyright; FRED says copyrighted series need the
  owner's permission beyond personal use. It is in no download.

## Accessible chart descriptions

Every chart on both sites has a text description: each web chart is an SVG with `role="img"`, `<title>`
and a `<desc>` built from the data, and four of the five figures also offer "Show the data as a table".
The atlas canvas has a data-driven `aria-label`, a live text summary of the current quarter and a
by-decade table. `tools/check_chart_text.mjs` enforces this after every build (`make f1-links`, CI).
Static figures for the paper get alt text from the `chart-from-sql` skill.
