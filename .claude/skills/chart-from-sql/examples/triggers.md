# Trigger examples for `chart-from-sql`

## Should trigger

| Prompt | Why |
|---|---|
| "Chart the public share since 1952 with recessions shaded for the paper." | Static time series, recession shading. |
| "Make a figure of the A1 contributions by holder group." | Signed horizontal bar from `decomposition.csv`. |
| "Plot the forecast path with its 80% and 95% bands as a fan chart." | Fan chart kind. |
| "Turn this query result into a stacked area of holder shares." | Query/DataFrame to chart, stacked area. |
| "I need small multiples of the six holder buckets, with alt text." | Small multiples plus generated alt text. |
| "Render the benchmark comparison as a PNG and SVG in the project style, dark version too." | Light and dark variants. |

## Should NOT trigger

| Prompt | Why |
|---|---|
| "Add a hover tooltip to the hero chart on the story site." | Interactive site chart: hand-built SVG in `web/`. |
| "Make the Hot Potato dots flow faster." | `atlas/` Canvas code. |
| "Build a Tableau dashboard." | No Tableau; and a dashboard is not a static figure. |
| "Which holders drove the 2008 jump?" | Analysis question; answer from the data (A1), chart only if asked. |
| "Write the SQL for public share by quarter." | Query writing, not charting. |
| "Run the Z.1 update." | `z1-release-update`. |

## Recorded outputs

Real runs from the repo root (`uv run --project pipeline --with matplotlib python .claude/skills/chart-from-sql/scripts/chart.py ...`).

File input, percent, recession shading (`--file web/public/data/public_share.json --kind line --x date --y public_share --as-percent --recessions --title "Public share" --source "Fed Z.1" --vintage 2026-09-11`):
```
wrote: ps.png, ps.svg, ps.alt.txt, ps.json
alt: Line chart titled "Public share": Public share (Percent (%)) by date, 1951Q4 to 2026Q2, 299 observations. Public share rose from 2.9% in 1951Q4 to 56.4% in 2026Q2 (high 58.6% in 2021Q1; low 2.5% in 1965Q3). Shaded bands mark 11 NBER recessions (1953Q2 to 2020Q2).
```

`--sql "SELECT date, public_share FROM mart.public_share"` with `DATABASE_URL_READONLY` unset (exit 2):
```
error: DATABASE_URL_READONLY is not set. Use --file with a CSV/JSON export instead, or set it in the environment (never paste it into chat).
```

`--sql "DELETE FROM mart.public_share"` (refused before any connection, exit 2):
```
error: only SELECT (or WITH ... SELECT) statements are allowed
```

No units given (`--file ... --kind line --x date --y public_share`, exit 2):
```
error: units required: pass ylabel (e.g. 'USD trillion') or as_percent=True
```

Gallery alt texts (from `examples/*.alt.txt`):
- `a1_contributions`: "Horizontal bar chart titled "What moved the public share, 2007Q4 to 2011Q4: contribution by holder group": 7 bars of Contribution to change in public share (percentage points). Largest positive: Private-label securitization and mortgage REITs, +4.93 pp. Largest negative: Other public holders, -0.04 pp. The bars sum to +13.11 pp (6 positive totalling +13.14 pp, 1 negative totalling -0.04 pp)."
- `a1_cumulative_path` ends: "Private label and mREITs rose from 0.18 pp in 2008Q1 to 5.71 pp in 2011Q4. ... Total rose from 0.89 pp in 2008Q1 to 13.11 pp in 2011Q4." (13.11 matches `results.json` total_pp 13.1056.)
