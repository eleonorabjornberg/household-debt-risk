# Site ↔ Tableau integration contract

The website (`web/`) drives and listens to the published Tableau Public workbook through the
Embedding API v3. Both sides depend on these exact names. Change them only together.

## Published workbook
- Workbook: `WhoHoldsTheDebt-extracts` (file `tableau/WhoHoldsTheDebt-extracts.twbx`), on profile `eleonora.bj.rnberg`. Figure 1 still points at the older `WhoHoldsTheDebt` workbook until v3.3 is published.
- Dashboard (view): `Ratchet` → `https://public.tableau.com/views/WhoHoldsTheDebt-extracts/Ratchet`.
- Worksheets inside the dashboard: `Ratchet – main` (stacked area) and `Public share` (line).
  The dash is an en dash (U+2013).

## Fields (data source `ratchet`, file `tableau/data/ratchet.csv`)
| Field caption | CSV column | Notes |
|---|---|---|
| `Date` | `date` | Quarter-end date. The site range-filters on this. |
| `Bucket label` | `bucket_label` | The site selects or highlights marks by these values. |
| `Recession` | `recession` | 1 when the quarter is inside an NBER recession (start_q..end_q inclusive), else 0. |
| `Crisis id` | `crisis_id` | The `crisis_id` of that NBER recession; empty outside recessions. |

## Parameter (removed in v3.1: the dual-axis bands crashed Tableau Public; the site tolerates its absence)
- Name: `Active crisis`. String, default `none`. Allowed values: `none` + every `crisis_id` in
  `tableau/data/crises.csv`.
- Effect: the band for that recession is drawn darker. All other bands stay light grey.

## What the site does
| Trigger | API call |
|---|---|
| A crisis step scrolls into view | `changeParameterValueAsync('Active crisis', id)` on the workbook; `applyRangeFilterAsync('Date', {min: t0−2y, max: t0+4y})` on both worksheets |
| The reader leaves the crisis chapter, or clicks Reset | parameter → `none`; `clearFilterAsync('Date')` |
| Click on a holder in the site's legend | `selectMarksByValueAsync([{fieldName: 'Bucket label', value: [label]}], 'select-replace')` on `Ratchet – main` |
| Click on a crisis panel in Figure 2 | same as scrolling to that crisis step |
| Reader clicks a band in Tableau (`markselectionchanged`) | the site reads `Bucket label` + `Date` from the selected marks and shows a side card |

Every call is wrapped so that a failure (e.g. the parameter doesn't exist in an older published
version) is logged and ignored. The page never breaks.
