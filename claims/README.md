# Claims register

`register.csv` has one row per published number (or per distinct spelling-group of one claim). It is the
evidence behind PLAN task 0.5: every number on the sites, in the README and in the findings traces to how
it was computed, its series, its vintage and a validation status.

## Columns (exact names, exact order)

| Column | Meaning |
|---|---|
| `claim_id` | Stable slug (`[a-z0-9_]`), unique. Name it by what and when: `public_share_2026q2`. Never reuse an id for a different claim. |
| `claim` | One plain sentence of what is claimed. |
| `display` | The number exactly as printed (`56.4%`, `$10.77T`, `+13.1 pp`, `3.56×`). If one claim is printed several ways (`+13.1 pp`, `+13.1 pts`, `13 points`), list every spelling separated by ` \| `. Two different claims that happen to print the same (`24.6%`) get two rows. |
| `value` | The number in `unit`, unrounded where known (`0.5638`, `10.77`). Date rows use an ISO date. |
| `unit` | `share`, `pp`, `usd_tn`, `usd_bn`, `ratio`, `count`, `pvalue`, `pct_rank`, `date`. |
| `period` | Quarter or range: `2026Q2`, `2007Q4-2011Q4`; `n/a` for design constants. |
| `locations` | Every `file:line` where it appears, separated by `;`. For atlas `{token}` copy, the line holding the token. |
| `computation` | The validation check id if one recomputes it (`C2`), else the code path (`analysis/notebook.py:q1_ratchet -> analysis/results.json <key>`) or a SQL query against `mart.*`. |
| `series_ids` | Z.1 / FRED / NY Fed ids involved, separated by spaces. |
| `vintage` | Source vintage, e.g. `z1:2026-09-11` (see `web/public/data/meta.json`); several separated by spaces (`z1:2026-09-11 fred:2026-10-27`); `n/a` for constants. |
| `validation` | One of the statuses below. |
| `check_id` | Id from `validation/results.json` (`C2`). Required when `validation` is `PASS` or `FAIL`; empty otherwise. |
| `notes` | Caveats: holdings not guarantees, real vs nominal dollars, how a token renders, why a row is STALE. |

## Validation statuses

| Status | Meaning |
|---|---|
| `PASS` | A check in `validation/results.json` recomputes the number independently and passes. `check_id` names it, and that check must currently be `PASS`. |
| `FAIL` | Such a check exists and fails. `check_id` names it, and that check must currently be `FAIL`. |
| `UNVERIFIED` | Traced to code or a results file, but no independent check yet. Not a defect, a to-do. |
| `ESTIMATE` | Model output, imputation or proxy. Must be labelled as an estimate where it is published. |
| `STALE` | The displayed value disagrees with the current source. The note says by how much; the copy needs fixing. |
| `DEFINITION` | A design setting chosen for the site, not a data claim (for example, one atlas dot = $50B). Nothing to recompute; `check_id` is empty. |

## Adding or changing a row

1. Find the number in the source file; note every `file:line` it appears on.
2. Find where it comes from: a `validation/results.json` check, else `analysis/notebook.py` (and the key in
   `analysis/results.json` or the table in `analysis/tables/`), else a SQL query against `mart.*`.
3. Recompute it from the data, not from the copy. If the copy disagrees at the printed precision, mark `STALE`.
4. Append the row with `claim_id`, `display`, `value`, `unit`, `locations`, and so on. Reuse an existing row if it is the same
   claim printed again: add the location, and add the new spelling to `display` after ` | `.
5. Run `uv run --project pipeline python claims/check_register.py` (or `uv run --project pipeline pytest claims`).
   Line numbers are checked to exist, so after editing a file re-check that its rows' `locations` still point at the number.
6. To promote a row to `PASS`, add the independent check to `validation/run.py` first, then set `validation` and `check_id`.

## The check

`check_register.py` validates the CSV (header, unique ids, statuses, check ids against `validation/results.json`,
that a `PASS`/`FAIL` row agrees with its check, locations that exist). It then scans `README.md`,
`atlas/content/story.ts`, `web/content/story.ts` and `analysis/recommendation.md` for number-like tokens and fails on any with no matching
`display`. The token regex, the normalisation and the allowlist are documented at the top of the script. Tokens that
reach the page only through a template (`{share}`, `{pls}`, `${facts.x}`) are registered by hand, with the resolved
value in `display` and the data field in `notes`.
