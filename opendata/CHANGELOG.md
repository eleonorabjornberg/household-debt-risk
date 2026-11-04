# Open-data changelog

The download contract lives under `/downloads/v1/`. File names and columns change only with a new
version (`v2`), recorded here. Adding a table or a released vintage is not a breaking change.

## Releases archived (`/downloads/v1/vintages/`)

| Release | Z.1 | FRED as-of | NY Fed retrieved | Archived |
|---|---|---|---|---|
| `z1-2026-09-11` | 2026-09-11 (2026Q2) | 2026-10-27 | 2026-10-27 | 2026-11-04 |

## v1 (2026-11-04)

- Tables: `public_share`, `debt_by_risk_holder`, `collateral_coverage`, `crisis_event_window`,
  `dim_crisis`, `dim_risk_bucket` (CC BY 4.0), `nyfed_by_type` (NY Fed Terms of Use).
- Files per release: `<table>.csv`, `<table>.json`, `dictionary.json`, `LICENSE-DATA.md`,
  `NOTICE-nyfed.txt`; `index.json` at the root.
