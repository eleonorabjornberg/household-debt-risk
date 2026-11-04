---
name: chart-from-sql
description: Turns a query result (read-only SQL, a CSV/JSON file or a pandas DataFrame) into a publication-quality static chart in the project style (PNG at 200 dpi and SVG, light and dark), with title, units, a "Source ... (vintage ...)" line, generated alt text and a JSON sidecar recording data source, vintage and row count. Chart kinds - line (optional NBER recession shading), stacked area, stacked bar, signed horizontal bar, fan chart with interval bands, small multiples. Use for figures in the paper, notes, findings and write-ups (decompositions, time series, forecast fans, benchmark comparisons). Not for the interactive charts on web/ or atlas/ (hand-built SVG/Canvas), dashboards, or any Tableau-style tool; not for analysing data or writing the SQL itself.
---

# chart-from-sql

Goal: one command from a query result to a static figure that already carries its units, source, vintage and alt text, in the same palette as the sites. Charts are Python only (CLAUDE.md: no Tableau).

Run from the repo root. `matplotlib` is **not** in the `pipeline` env, and `pipeline/pyproject.toml` must not be edited here, so every command adds it per run: `uv run --project pipeline --with matplotlib python ...` (pandas and psycopg are already there).

## Hard rules
- Plot only what the query/file returns. Never fill, smooth, extrapolate or invent a point; imputations and proxies are labelled in the title/subtitle by the caller.
- Alt text and axis numbers come from the data (the script computes them); never hand-edit `.alt.txt` or the sidecar.
- Source line, vintage, title and units are mandatory; the script refuses without them. The vintage must be real (`web/public/data/meta.json` `vintages`, or the `vintage_*` field of the research results). If unknown, say "unknown" in `--vintage` and flag it, do not guess.
- SQL: one SELECT (or WITH ... SELECT), run read-only through `DATABASE_URL_READONLY` (read-only session and transaction, 15 s statement timeout). The script rejects anything else before connecting. Never write, never use another connection string, never paste the DSN in chat. If the variable is unset (usual), export the result to CSV/JSON and use `--file`; do not ask for the secret.
- Every published chart's numbers still need rows in `claims/register.csv`; the sidecar gives the file/query and vintage to cite.
- Do not recolour by hand. Colours come from `scripts/style.py`; changing one means re-running `tests/test_style.py`.

## Steps
1. Get the data: `--file PATH` (CSV, or JSON as a list of records, e.g. `web/public/data/public_share.json`) or `--sql "SELECT ..."`. In Python: `make_chart(df, ...)`.
2. Pick the kind (below) and the units. Fractions: `--as-percent` multiplies by 100 and labels `%`. Other conversions: `--scale 1e-6` with `--ylabel "USD trillion"`, `--unit "USD trillion"` (short unit used in alt text).
3. Run, with a title that states the finding or subject, a `--source` naming the series/table, and `--vintage`.
4. Read the PNG (look at it: overlaps, truncation), read `<name>.alt.txt`, check the sidecar. Fix arguments, not pixels.
5. Output goes where the user asked (`--out DIR/name`); the examples in this folder are only the gallery.

```bash
uv run --project pipeline --with matplotlib python .claude/skills/chart-from-sql/scripts/chart.py \
  --file web/public/data/public_share.json --kind line --x date --y public_share --as-percent \
  --recessions --title "Public share of U.S. household mortgage and consumer debt" \
  --source "Fed Z.1 Financial Accounts" --vintage 2026-09-11 --out research/x/figures/public_share
```
Python: `sys.path.insert(0, ".claude/skills/chart-from-sql/scripts"); from chart import make_chart, load_file, run_sql`.

## Kinds
| `--kind` | Use | Data shape |
|---|---|---|
| `line` | time series; several series get direct end labels; `--recessions` shades NBER recessions from `web/public/data/dim_crisis.json` (`kind == nber_recession`, `start_q`..`end_q`; policy shocks are not shaded); `--ink-series total` draws a column in ink | x = date / `YYYY-MM-DD` / `2008Q1`; y = one or more columns (wide) or `--group COL` (long) |
| `area`, `bar` | stacked holder composition (non-negative only; signed data raises) | same |
| `hbar` | signed contributions; `--group side` colours public (blue) / private (orange); `--sort` | x = label column, y = value |
| `fan` | point path + intervals: `--y point --band lo90:hi90:"90% interval" --band lo50:hi50:"50% interval"` (outermost first), `--origin DATE` marks the forecast origin | columns for point and each band end |
| `multiples` | one panel per y column, shared y (`--free-y` to release), `--ncols` | same as line |

`--mode light|dark|both` (dark files get a `-dark` suffix). `--labels col=Label,...` renames series. More than six series: the extra ones are grey and dashed (the palette is capped at six; prefer grouping or `multiples`).

## Outputs
`<name>.png` (200 dpi), `<name>.svg`, optional `-dark` variants, `<name>.alt.txt` (what is plotted, range, start and end value of each series, highs and lows, stacked total, interval at the last point, recession count: all computed), `<name>.json` (title, `source_line`, vintage, `data_source` with file path and SHA-256 or the SQL text, row count, units, scale applied, files, alt text).

## Palette (scripts/style.py)
The sites' own colours (`web/app/globals.css`). Categorical, fixed per holder bucket in `pipeline/series_catalog.yaml` `risk_buckets` order: `#2a78d6` federal direct, `#d95926` GSE and agency, `#199e70` state and local, `#b07800` banks, `#d55181` private securitization, `#008300` finance companies and other. Amber is darkened from the site's light value so every colour works on both papers. Sequential: one blue ramp; diverging: blue / grey / orange. `tests/test_style.py` asserts WCAG contrast >= 3:1 for each series colour on light (`#f7f8f9`) and dark (`#101215`) paper and >= 4.5:1 for text tokens; the palette also passes the `dataviz` validator (CVD separation, lightness band) in both modes. No dual axes; text never takes a series colour.

## Tests
```bash
uv run --project pipeline --with matplotlib python -m pytest .claude/skills/chart-from-sql/tests -q
```
Covers contrast, alt text derived from data, sidecar contents, each kind rendering, and SQL refusal (DML/DDL, multiple statements, SELECT INTO, FOR UPDATE, comments hiding statements). A live-database test needs `DATABASE_URL_READONLY` and is not included.

## Files
`scripts/style.py`, `scripts/chart.py`, `tests/`, `examples/triggers.md`, `examples/build_gallery.py` (rebuilds the gallery from committed data), gallery images `examples/public_share_1952_2026.png`, `examples/a1_contributions.png`, `examples/a1_cumulative_path.png`.

## Known limits
Fonts fall back to DejaVu Sans unless Public Sans is installed. Recession shading uses the dates in `dim_crisis.json` as given (quarter-end to quarter-end). The SQL guard is a keyword filter on top of a read-only session; a column literally named like a SQL keyword (e.g. `update`) must be quoted or aliased.
