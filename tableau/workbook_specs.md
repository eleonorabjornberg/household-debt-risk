# Tableau build specs: "Who Holds the Debt?"

There is one workbook, **`WhoHoldsTheDebt`**, with four embeddable dashboards. The website embeds these exact view paths (case-sensitive):

| Dashboard | View path (embed) | Primary tables |
|---|---|---|
| The Ratchet | `WhoHoldsTheDebt/Ratchet` | `mart.public_share`, `mart.debt_by_risk_holder`, `core.dim_risk_bucket`, `core.dim_crisis` |
| Crisis small multiples | `WhoHoldsTheDebt/CrisisSmallMultiples` | `mart.crisis_event_window`, `core.dim_crisis` |
| Collateral coverage | `WhoHoldsTheDebt/Collateral` | `mart.collateral_coverage`, `core.dim_crisis` |
| Payment priority | `WhoHoldsTheDebt/PaymentPriority` | `mart.nyfed_by_type` |

All of them use the published data source **`hhdebt`** (`tableau/hhdebt.tds`; connection steps in `tableau/README.md`). Reference numbers to QA against are in `analysis/results.json` and `analysis/findings.md`.

---

## 0. Shared conventions

### 0.1 Data source model (`hhdebt`)

Use **logical-layer relationships** (noodles), not physical joins, so each sheet queries only the tables it uses:

```
mart.public_share (date)  ──< mart.debt_by_risk_holder (date)  >── core.dim_risk_bucket (risk_bucket)
        │
        └── crisis_quarters (date)              [custom SQL, see below]

mart.collateral_coverage (date)  ── crisis_quarters (date)
mart.crisis_event_window (crisis_id) >── core.dim_crisis (crisis_id)
mart.nyfed_by_type                               [standalone]
core.dim_crisis                                   [also related 1=1 to public_share for band LODs, see 0.4]
```

* `public_share.date = debt_by_risk_holder.date` (one-to-many)
* `debt_by_risk_holder.risk_bucket = dim_risk_bucket.risk_bucket` (many-to-one)
* `public_share.date = crisis_quarters.date` (one-to-many; a quarter can sit inside two overlapping windows)
* `crisis_event_window.crisis_id = dim_crisis.crisis_id` (many-to-one)

**`crisis_quarters`** is custom SQL giving one row per quarter-end inside each NBER recession (peak quarter through trough quarter):

```sql
select c.crisis_id, c.name, c.kind,
       (q + interval '3 months' - interval '1 day')::date as date
from core.dim_crisis c
cross join lateral generate_series(
        date_trunc('quarter', c.start_q),
        date_trunc('quarter', coalesce(c.end_q, c.start_q)),
        interval '3 months') as q
where c.kind = 'nber_recession'
```

### 0.2 Colour: one bucket palette everywhere

Public buckets are **cool** (blue/teal family) and private buckets are **warm** (red/amber/pink family). The stack order is the palette order, and color stays tied to its bucket: if a filter drops a bucket, the others keep their colors. The order was validated with the dataviz palette validator on the light surface `#fcfcfb`. All gates pass: worst adjacent CVD ΔE 15.3, worst normal-vision ΔE 19.6. Teal, amber and pink are under 3:1 contrast against the surface, so **always show the legend and the tooltip**, and label the two biggest bands directly.

| sort_order | risk_bucket | Label | Light (Tableau) | Dark-mode alternate (site) |
|---|---|---|---|---|
| 1 | federal_direct | Federal government (direct) | `#1C5CAB` | `#256ABF` |
| 2 | gse_agency | GSEs & agency pools | `#1BAF7A` | `#199E70` |
| 3 | state_local | State & local governments | `#3987E5` | `#3987E5` |
| 4 | banks_credit_unions | Banks & credit unions | `#E34948` | `#D03B3B` |
| 5 | private_securitization | Private securitization & mREITs | `#EDA100` | `#C98500` |
| 6 | nonbank_other | Finance cos. & other private | `#E87BA4` | `#D55181` |

**Collateral classes** (Collateral and PaymentPriority dashboards). Validated all-pairs: worst CVD ΔE 15.3, normal-vision 20.8.

| collateral_class | Label | Light |
|---|---|---|
| home_backed | Home-backed | `#6250D6` (violet) |
| vehicle_backed | Vehicle-backed | `#EDA100` (amber) |
| uncollateralized | No collateral | `#E34948` (red) |
| other_nonrevolving | Other non-revolving (mixed) | `#898781` (muted grey, the "Other" fold) |

The site deliberately reuses amber and red across dashboards. They never appear in the same view with a different meaning.

**Ink and chrome:** primary text `#0B0B0B`, secondary text `#52514E`, axis labels `#898781`, gridlines `#E1E0D9` (horizontal only, 1px), baseline `#C3C2B7`, background `#FCFCFB`, crisis band fill `#52514E` at 18% (see 0.4). Lines are 2px. Font is Tableau Book / system sans; numbers use tabular figures in tooltips and tables.

Set up the palette once in `Preferences.tps` (`My Tableau Repository/Preferences.tps`):

```xml
<workbook><preferences>
  <color-palette name="HHDebt Buckets" type="regular">
    <color>#1C5CAB</color><color>#1BAF7A</color><color>#3987E5</color>
    <color>#E34948</color><color>#EDA100</color><color>#E87BA4</color>
  </color-palette>
  <color-palette name="HHDebt Collateral" type="regular">
    <color>#6250D6</color><color>#EDA100</color><color>#E34948</color><color>#898781</color>
  </color-palette>
</preferences></workbook>
```

Then on each Color card, choose *Edit Colors → HHDebt Buckets* and **assign by member explicitly**. Never use "Assign Palette": it assigns by sort order and breaks if a member is missing.

### 0.3 Shared calculated fields (create in the data source so every sheet sees them)

| Name | Formula | Notes |
|---|---|---|
| `Quarter` | `DATETRUNC('quarter', [date])` | x-axis; format `"Q"q yyyy` |
| `Quarter label` | `STR(YEAR([date])) + "Q" + STR(DATEPART('quarter',[date]))` | tooltips |
| `Bucket label` | `[label]` (from dim_risk_bucket) | |
| `Public / private` | `IF [is_public] THEN "Public" ELSE "Private" END` | |
| `Bucket share` | `SUM([share_of_total])` | summed over debt_type → share of scope |
| `Bucket $T` | `SUM([nominal_musd]) / 1e6` | |
| `Public share` | `AVG([public_share])` | one row per date, so AVG = value |
| `Fed MBS share` | `AVG([fed_mbs_share_of_scope])` | null before 2009 |
| `Scope $T` | `AVG([scope_total_musd]) / 1e6` | |
| `Public $T` | `AVG([public_musd]) / 1e6` | |
| `Is latest quarter` | `[date] = {FIXED : MAX([date])}` | for end labels |
| `Latest quarter label` | `{FIXED : MAX([date])}` → format `"Q"q yyyy` | dashboard subtitle |

### 0.4 Crisis bands (Ratchet and Collateral)

Tableau can't put a third mark layer on a dual-axis chart. So the NBER bands are **reference bands driven by `core.dim_crisis` through LOD calcs**, one band per recession. Relate `core.dim_crisis` to `mart.public_share` with a relationship calculation `1 = 1`, which makes it a constant cross-relationship (11 rows).

For each recession *Y* in {1953, 1957, 1960, 1969, 1973, 1980, 1981, 1990, 2001, 2007, 2020}:

```
// Band Y start
{FIXED : MIN(IF [kind] = 'nber_recession' AND YEAR([start_q]) = Y   // 2019Q4 peak: use YEAR = 2019
             THEN DATEADD('quarter', -1, [start_q]) END)}
// Band Y end
{FIXED : MIN(IF [kind] = 'nber_recession' AND YEAR([start_q]) = Y THEN [end_q] END)}
```

On the date axis, add Analytics → Reference Band. Scope **Entire table**; Band from = `MIN([Band Y start])`, Band to = `MIN([Band Y end])`; Fill `#52514E`, opacity 18%; no line; label None; tooltip off. Reference bands draw *behind* marks, so **set area opacity to 82%** on the Ratchet so the bands show through. Policy shocks (`kind = 'policy_shock'`) are **reference lines**, not bands: dashed 1px `#898781`, labelled with `[name]` at the top. (A new recession means adding two calcs and one band, roughly once a decade.)

### 0.5 Sizing and layout

* **Desktop layout:** Size = *Range*, min 800×560, max 1200×720. Design at **1000×620**. Tiled layout only (no floating objects), with outer padding 16px and inner padding 8px.
* **Phone layout:** Device layouts → Phone → *Fit width*, height *Automatic*, 375px design width with 16px side gutters. Stack the components vertically in the order *title → main chart (height 340) → legend → secondary chart (if any, height 220) → parameter controls → source line*. Hide the secondary legend; keep the parameter control.
* **Title** (worksheet title off; a text object is the dashboard title): 18px bold `#0B0B0B`. The subtitle is 12px `#52514E` and includes `<Latest quarter label>`.
* **Source line** (12px `#898781`, bottom): "Source: Federal Reserve Z.1 Financial Accounts; FRED; NY Fed CCP/Equifax. Households include nonprofits. Mortgage holders apportioned to household liability."
* **Toolbar:** hidden in embed (set by the site). Turn off "Show sheets as tabs".
* Every chart also gets a **hidden "Data" worksheet** (crosstab of the same fields), reachable from the viz's Download → Crosstab. This is the accessibility table view.

---

## 1. The Ratchet: `WhoHoldsTheDebt/Ratchet`

**Question it answers:** Who holds US household mortgages and consumer credit, 1952–now, and did crises push it onto public balance sheets?

### Data
* `mart.debt_by_risk_holder` (rows: date × risk_bucket × debt_type) → `core.dim_risk_bucket`
* `mart.public_share` (one row per date; public share line and Fed MBS overlay)
* `core.dim_crisis` (bands; see 0.4)

### Sheet `Ratchet – main` (dual axis, synchronized: **one 0–100% scale**, not two scales)
| Shelf | Content |
|---|---|
| Columns | `Quarter` (continuous, exact date) |
| Rows | `Bucket share` (axis 1) and `Public share line` (axis 2) → Dual Axis → **Synchronize Axis** → hide the right axis |
| Axis 1 marks | **Area**; Color = `risk_bucket` (palette 0.2, assigned per member); sort `risk_bucket` by `MIN([sort_order])` ascending so federal_direct is at the bottom; opacity 82%; Detail = `Bucket label`; Analysis → Stack Marks **On** |
| Axis 2 marks | **Line**, 2px; Measure Names on Color: `Public share` = `#0B0B0B` solid, `Fed MBS share` = `#0B0B0B` at 70% with **Path → Line pattern = dashed** (Tableau 2023.2+; on older versions use `#52514E` solid 1px) |
| Axis 2 measures | Measure Values = `Public share`, `Fed MBS share` (Measure Names filter keeps only these two) |
| Axis | 0 to 1 fixed, format percent 0 decimals, ticks every 20%; no axis title; date axis ticks every 10 years |
| Filters | `Quarter` range (context), default 1952Q1 → latest |
| Parameters | `p_Measure` (string): **Share of debt** (default) / **$ trillions**. With `$ trillions`, axis 1 uses `IF [p_Measure]='$ trillions' THEN [Bucket $T] ELSE [Bucket share] END` and axis 2 is hidden (`Public share line` returns NULL; see calc). |

Calculated fields:
```
// Bucket value
IF [p_Measure] = '$ trillions' THEN SUM([nominal_musd]) / 1e6 ELSE SUM([share_of_total]) END

// Public share line   (hidden in $ mode)
IF [p_Measure] = '$ trillions' THEN NULL ELSE AVG([public_share]) END

// Fed MBS line
IF [p_Measure] = '$ trillions' THEN NULL ELSE AVG([fed_mbs_share_of_scope]) END

// Public share change vs 16q earlier (tooltip)
AVG([public_share]) - LOOKUP(AVG([public_share]), -16)        // compute using Quarter

// Crisis in progress (tooltip)
{FIXED [date] : MAX(IF NOT ISNULL([crisis_quarters].[crisis_id]) THEN [crisis_quarters].[name] END)}
```

**Direct labels:** label the line at the latest quarter only (`Is latest quarter` = TRUE on Label, "Public 56.4%"). Label the `gse_agency` and `banks_credit_unions` areas once, mid-band at 1995. The legend shows all six buckets plus the two lines.

**Bands:** the 11 NBER reference bands from 0.4, plus 3 policy-shock reference lines (2020Q1, 2023Q4, 2025Q2).

**Tooltip (area):**
```
<Quarter label>
<Bucket label>                       (bold, in the bucket colour)
<Bucket share>  of household mortgages + consumer credit    → format 0.0%
<Bucket $T> trillion  (nominal)                             → $0.00
Public share this quarter: <Public share>  (<Public share change vs 16q earlier> pp vs 4 years earlier)
<Crisis in progress>
```
**Tooltip (lines):**
```
<Quarter label>
Public share: <Public share>   ·   $<Public $T>T of $<Scope $T>T
Fed-held agency MBS: <Fed MBS share> of scope debt
The Fed's MBS are inside the public share. The Fed bears interest-rate risk; credit risk stays with the GSEs/Ginnie Mae.
```

### Sheet `Ratchet – KPI` (text tile row above the chart)
Three BANs (big numbers), each a separate sheet with Text marks: **Public share now** (`Public share` at max date, 0.0%), **Change since 2007Q4** (`ZN(latest) - value at 2007Q4`, +0.0 "pp"; computed with `{FIXED : MAX(IF [date] = #2007-12-31# THEN [public_share] END)}`), **Fed MBS share now**. Numbers are 28px `#0B0B0B`, labels 12px `#52514E`. No color fills.

### Dashboard
1000×620: title + subtitle (60), KPI row (80), main chart (420), legend at the right (180 wide) or below on phone, source line. Phone: KPI row becomes three stacked lines; chart 340 high; legend below the chart.

---

## 2. Crisis small multiples: `WhoHoldsTheDebt/CrisisSmallMultiples`

**Question:** Around each crisis (−8 to +16 quarters), how did the chosen metric move compared with the peak quarter?

### Data
`mart.crisis_event_window` → `core.dim_crisis` (crisis_id). This is long format: one row per crisis × metric × q_offset.

The metric codes the pipeline must emit (the parameter list below must match exactly):

| Parameter display | `metric` code | Unit of `value` |
|---|---|---|
| Public share | `public_share` | share 0–1 |
| Public share, mortgages | `public_share_mortgage` | share 0–1 |
| Public share, consumer credit | `public_share_cc` | share 0–1 |
| Federal direct share | `share:federal_direct` | share 0–1 |
| GSE & agency share | `share:gse_agency` | share 0–1 |
| Banks & credit unions share | `share:banks_credit_unions` | share 0–1 |
| Private securitization share | `share:private_securitization` | share 0–1 |
| Uncollateralized share | `share:uncollateralized` | share 0–1 |
| Home-backed coverage | `coverage:home_backed` | ratio (×) |
| Vehicle proxy coverage | `coverage:vehicle_backed` | ratio (×) |

### Parameters
* `p_Metric` (string, list): the codes above with their display aliases. Default `public_share`.
* `p_View` (string, list): **Change from peak** (default) / **Level**.
* `p_IncludeShocks` (boolean, default False): adds the 2020Q1/2023Q4/2025Q2 policy-shock panels.

### Calculated fields
```
// Is share metric
[metric] = 'public_share' OR STARTSWITH([metric], 'share:') OR STARTSWITH([metric], 'public_share_')

// Y value
IF [p_View] = 'Level' THEN
    IF [Is share metric] THEN SUM([value]) * 100 ELSE SUM([value]) END
ELSE
    IF [Is share metric] THEN SUM([delta_from_t0]) * 100 ELSE SUM([delta_from_t0]) END
END
// Shares display in % or pp (×100); coverage in × or Δ×.
// If the pipeline already stores delta_from_t0 in pp, drop the ×100 on the delta branch. Check that the 2007Q4 public_share
// row at q_offset 16 reads 13.1 (pp), not 1311.

// Panel # (0-based, chronological; keyed on the peak year from dim_crisis.start_q)
CASE YEAR([start_q])
  WHEN 1953 THEN 0 WHEN 1957 THEN 1 WHEN 1960 THEN 2 WHEN 1969 THEN 3
  WHEN 1973 THEN 4 WHEN 1980 THEN 5 WHEN 1981 THEN 6 WHEN 1990 THEN 7
  WHEN 2001 THEN 8 WHEN 2007 THEN 9 WHEN 2019 THEN 10
  WHEN 2020 THEN 11 WHEN 2023 THEN 12 WHEN 2025 THEN 13 END
// Grid row / column (4 columns on desktop)
INT([Panel #] / 4)          → Grid row (discrete dimension)
[Panel #] % 4               → Grid col (discrete dimension)

// Kind filter
[kind] = 'nber_recession' OR [p_IncludeShocks]

// Panel title (shown via Label on a hidden mark or in tooltip)
[name] + " (" + STR(YEAR([start_q])) + "Q" + STR(DATEPART('quarter',[start_q])) + ")"

// Value at +16 (end label)
IF [q_offset] = 16 THEN [Y value] END
```

### Sheet `Crisis SM`
| Shelf | Content |
|---|---|
| Filters | `metric` = `[p_Metric]` (calc filter `[metric] = [p_Metric]`), `Kind filter` = True |
| Columns | `Grid col` (discrete, header hidden), `q_offset` (continuous, fixed −8 to 16, ticks every 4) |
| Rows | `Grid row` (discrete, header hidden), `Y value` (continuous; **Independent axis ranges off**: every panel shares one scale) |
| Marks | Line, 2px, `#1C5CAB`; Detail = `crisis_id`; Label = `Value at +16` (end only, format `+0.0;-0.0`) |
| Reference line | x = 0, dotted 1px `#898781` (the peak); y = 0 (Change view only), 1px `#C3C2B7` |
| Panel titles | Put `Panel title` on Text in a separate header sheet with the same Grid row/col, *or* (simpler) Label the first point (`q_offset = -8`) with `Panel title` in 10px bold `#0B0B0B`, positioned top-left |
| Shading | Reference band per pane from q_offset 0 to 16, `#ECEBE6` (the post-peak window) |

**Highlight the 2007 panel** with `IF YEAR([start_q])=2007 THEN 'GFC' ELSE 'Other' END` on Color: GFC `#1C5CAB`, Other `#1C5CAB` too (same color). Use **size** instead: GFC 3px, others 2px. Color does not encode rank.

**Tooltip:**
```
<Panel title>
Quarter <q_offset> from the peak (<date as "Q"q yyyy>)
<p_Metric display>: <value formatted>
Change since peak: <delta formatted>  (pp for shares, × for coverage)
```

### Dashboard
1000×640: title, then a parameter row at the top (Metric dropdown, View toggle, Include shocks checkbox; one row, left-aligned), then the grid (3 rows × 4 columns = 11 NBER panels, or 4 rows with shocks), then a source line. Subtitle: "Each line starts 8 quarters before an NBER peak and ends 16 after. Shaded: the 16 quarters after the peak."
**Phone:** make a duplicate sheet `Crisis SM – phone` with `Grid col = [Panel #] % 2` and `Grid row = INT([Panel #]/2)` (2 columns) and use it in the phone layout. Parameters stack above.

---

## 3. Collateral coverage: `WhoHoldsTheDebt/Collateral`

**Question:** What is the debt backed by, and how well does the collateral cover it through each crisis?

### Data
`mart.collateral_coverage` (date × collateral_class) related to `crisis_quarters` on date. NBER bands via 0.4 (relate `core.dim_crisis` 1=1 here as well).

### Calculated fields
```
// Coverage
AVG([coverage_ratio])                                    // NULL for uncollateralized / other

// Equity cushion (home only)
IF ATTR([collateral_class]) = 'home_backed' THEN 1 - 1 / AVG([coverage_ratio]) END

// Share of debt
SUM([share_of_debt])

// Estimated flag label
IF MAX([is_estimated]) THEN "Estimated: student loans not split out before 2006" ELSE "" END

// Share solid / share estimated  (two measures so estimated years can be drawn differently)
IF NOT [is_estimated] THEN [share_of_debt] END            → Share (reported)
IF [is_estimated] THEN [share_of_debt] END                → Share (estimated)

// Class label
CASE [collateral_class]
  WHEN 'home_backed' THEN 'Home-backed (appreciating)'
  WHEN 'vehicle_backed' THEN 'Vehicle-backed (depreciating)'
  WHEN 'uncollateralized' THEN 'No collateral (cards, student)'
  WHEN 'other_nonrevolving' THEN 'Other non-revolving (mixed)' END
```

### Sheet `Coverage – home` (main)
* Columns `Quarter`; Rows `Coverage`; filter `collateral_class = home_backed`.
* Line 2px `#6250D6`. Axis format `0.0"×"`, fixed from 1× to auto max. Reference line at **1.0×** labelled "Debt = value of homes", `#C3C2B7`.
* NBER bands (0.4). Label the latest point and the 2012Q1 low (1.85×) with annotations.
* Tooltip: `<Quarter label>` / `Owner-occupied homes are worth <Coverage>× household mortgages` / `Aggregate equity cushion: <Equity cushion>` (0%) / `Aggregate ratio: includes homes with no mortgage, so it hides underwater borrowers.`

### Sheet `Coverage – mix` (share of debt by collateral class)
* Columns `Quarter`; Rows `Share (reported)` and `Share (estimated)` on a *shared* axis (Measure Values), Marks = **Area**, stacked; Color = `collateral_class` (HHDebt Collateral palette, by member). Order from the bottom: home, vehicle, other, uncollateralized.
* `Share (estimated)` years get **opacity 45%** and the tooltip line `<Estimated flag label>`. Before 2006 the uncollateralized slice holds revolving credit only; the mart sets `is_estimated = true` for those rows.
* Annotation at 2006Q1: "Student loans split out (+3.9 pp jump is a data break)". Annotation at 1977Q1: "Revolving reclassified".

### Sheet `Coverage – vehicle proxy` (small, secondary)
* `collateral_class = vehicle_backed`, line `#EDA100`, axis `0"×"`. Subtitle on the sheet: "All consumer durables ÷ auto loans: a proxy that overstates vehicle collateral."

### Parameters / filters
* `p_From` (date, default 1952-03-31) and `p_To` (latest) drive a `Quarter` range filter on all three sheets (Apply to all using this data source).
* `p_Crisis` (string list from `core.dim_crisis.name`, plus "None"). When set, a calc `In selected crisis window = [date] >= DATEADD('quarter',-8,[start_q]) AND [date] <= DATEADD('quarter',16,[start_q])` filters (or highlights) all three sheets. Hook it to a dashboard **Highlight** action rather than a filter, so the long view stays visible.

### Dashboard
1000×680: title; the main home-coverage chart (left 620 × 330) and the mix area (right 360 × 330) in one row; then the vehicle proxy (1000 × 180); then a controls row; then the source line. **Phone:** home coverage (300 high), mix (260), vehicle proxy (180), controls.

---

## 4. Payment priority: `WhoHoldsTheDebt/PaymentPriority`

**Question:** When households are stressed, which debts do they keep paying? (NY Fed CCP, 2003+)

### Data
`mart.nyfed_by_type` (date × loan_type): `balance_busd`, `transition_serious_pct` (percent of balance moving into 90+ days delinquent, annualized, as published).

### Calculated fields
```
// Loan type label
CASE [loan_type] WHEN 'mortgage' THEN 'Mortgage' WHEN 'heloc' THEN 'HELOC' WHEN 'auto' THEN 'Auto'
  WHEN 'credit_card' THEN 'Credit card' WHEN 'student' THEN 'Student loan' WHEN 'other' THEN 'Other' END

// Collateral class (drives colour)
CASE [loan_type] WHEN 'mortgage' THEN 'home_backed' WHEN 'heloc' THEN 'home_backed'
  WHEN 'auto' THEN 'vehicle_backed' WHEN 'credit_card' THEN 'uncollateralized'
  WHEN 'student' THEN 'uncollateralized' ELSE 'other_nonrevolving' END

// Serious delinquency transition
AVG([transition_serious_pct]) / 100                        // format 0.0%

// Baseline: each type's own 2003-2006 average transition rate (pre-crisis norm)
{FIXED [loan_type] : AVG(IF YEAR([date]) <= 2006 THEN [transition_serious_pct] END)}

// Stress index (1.0 = the type's pre-crisis norm)
AVG([transition_serious_pct]) / AVG([Baseline])

// Payment priority rank (1 = most protected = smallest rise vs its own norm), per quarter
RANK_DENSE([Stress index], 'asc')                          // Compute using: loan_type (partition by date)
// Raw transition rates are NOT comparable across types for priority: card rates sit above mortgage rates
// even in good years. Rank on the stress index.

// Student loan data caveat
IF [loan_type] = 'student' AND [date] >= #2020-06-30# AND [date] <= #2025-03-31#
THEN "Payment pause and reporting grace period: student loan delinquencies were not reported (Q2 2020–Q1 2025)."
ELSEIF [loan_type] = 'student' AND [date] >= #2025-06-30#
THEN "Re-reporting after the pause inflates transitions; not comparable with pre-2020."
END

// Mortgage vs card gap (pp), the payment-hierarchy-inversion signal
WINDOW_AVG(IF ATTR([loan_type]) = 'mortgage' THEN AVG([transition_serious_pct]) END)
- WINDOW_AVG(IF ATTR([loan_type]) = 'credit_card' THEN AVG([transition_serious_pct]) END)   // Compute using loan_type
```

### Sheet `Priority – small multiples` (main)
* One panel per loan type (2 rows × 3 columns): Columns `Grid col = CASE [loan_type] WHEN 'mortgage' THEN 0 WHEN 'heloc' THEN 1 WHEN 'auto' THEN 2 WHEN 'credit_card' THEN 0 WHEN 'student' THEN 1 ELSE 2 END`; Rows `Grid row = IF [loan_type] IN ('mortgage','heloc','auto') THEN 0 ELSE 1 END`, then `Quarter`.
* Each panel draws **all six types in `#E1E0D9` (1px)** for context, plus **its own type in its collateral color (2px)**. Implement this with a self-join-free trick: put `loan_type` on Detail and use `Color = IF [loan_type] = [Panel type] THEN [Collateral class] ELSE 'context' END`, where `Panel type` is the panel's own type. Simpler alternative: Rows = `Loan type label` (6 rows, one series each), shared y-axis.
* Colors: home-backed `#6250D6`, vehicle `#EDA100`, uncollateralized `#E34948`, other `#898781`.
* Y axis: `Serious delinquency transition`, shared across panels, 0–max, format 0%.
* Shaded 2007Q4–2009Q2 and 2019Q4–2020Q2 NBER bands (reference bands; same LODs as 0.4, using only 2007 and 2020).
* Student panel: dashed segment or 40% opacity for 2020Q2–2025Q1 (use `Student loan data caveat` non-null → opacity via a second measure as in §3). Annotation: "Not comparable: pause and re-reporting".

### Sheet `Priority – rank` (secondary bump chart)
* Columns `Quarter`; Rows `Payment priority rank` (axis reversed: 1 at top); Marks Line + circle 8px; Color = `Collateral class`; Detail = `loan_type`; label at the end with `Loan type label`. A toggle `p_PriorityView` (Rank / Stress index) swaps the rank for the stress index itself (log axis, reference line at 1.0×).
* Exclude `student` by default (filter toggle `p_ShowStudent`, default False) because of the 2020–25 reporting gap.
* What to look for: in 2008–10, mortgage (and HELOC) transitions rose far more relative to their own pre-crisis norm than card or auto transitions did. That is consistent with the "payment hierarchy" shift documented by TransUnion and NY Fed researchers, where borrowers kept paying the car and the card ahead of the house. **Verify the multiples against the loaded data before writing site copy;** the analysis has not yet checked them against `mart.nyfed_by_type`.

### Tooltip
```
<Loan type label> · <Quarter label>
<Serious delinquency transition> of balances moved into 90+ days delinquent (annualized)
Balance: $<balance_busd>B
Stress index: <Stress index>× its 2003–06 average  ·  priority rank <Payment priority rank> of <WINDOW_COUNT(COUNTD([loan_type]))>
<Student loan data caveat>
```

### Dashboard
1000×640: title, small multiples (1000 × 380), then the rank chart (1000 × 160), then the source line ("NY Fed Consumer Credit Panel / Equifax. Transition = share of balances becoming 90+ days delinquent, annualized."). **Phone:** small multiples as 6 stacked rows (Rows = `Loan type label`) at 90px each; rank chart hidden on phone.

---

## 5. QA checklist before publishing

* Ratchet 2026Q2 tooltip shows **Public share 56.4%**, $10.77T of $19.10T. The 2007Q4 line value is 36.1% and 2011Q4 is 49.2%.
* Fed MBS overlay starts in 2009Q1 at 1.8%, peaks at 16.4% (2022Q1), and is 10.3% in 2026Q2.
* `CrisisSmallMultiples` with *Public share* and *Change from peak*: the 2007Q4 panel at +16 reads **+13.1**, and 2001Q1 reads **−3.8**.
* `Collateral` home coverage: 2012Q1 **1.85×**, 2026Q2 **3.56×**.
* No sheet shows sector 40 or sector 41 on its own across 2010 (FAS 166/167).
* Bucket colors match the table in 0.2 on every sheet. Test by excluding one bucket with a filter (for example `private_securitization`): the other colors must not shift.
