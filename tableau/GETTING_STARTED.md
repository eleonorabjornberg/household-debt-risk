# Getting started with Tableau Public

This guide covers how the Tableau charts for the website (https://household-debt-risk-web.vercel.app) are built, published and refreshed. It assumes no prior Tableau experience. Tableau Public is free, and the data is public, so publishing it publicly is fine.

| File | What it is |
|---|---|
| `WhoHoldsTheDebt-extracts.twbx` | **Open this one.** The packaged workbook: four dashboards plus the data, including a built-in `.hyper` extract per data source (Tableau Public only accepts extract-backed data). |
| `WhoHoldsTheDebt-extracts.twb` | The same workbook without the data. The build script writes it; you can ignore it. |
| `data/*.csv` | The data as plain spreadsheets, written by the pipeline (`hhdebt export-tableau`). |
| `build_workbook.py` | Regenerates both workbook files and the extracts from the CSVs. |

The workbook is published on Tableau Public as **`WhoHoldsTheDebt-extracts`**. The site embeds four of its views:

| Dashboard (URL path `views/WhoHoldsTheDebt-extracts/<name>`) | Worksheets inside | Data |
|---|---|---|
| `Ratchet` | `Ratchet – main` (stacked area by holder), `Public share` (line) | `ratchet.csv` |
| `CrisisSmallMultiples` | `Crisis SM – main` (one panel per crisis, change in public share since t0, in percentage points) | `crisis_windows.csv` |
| `Collateral` | `Collateral – share` (debt mix by collateral), `Collateral – coverage` (home coverage ratio) | `collateral.csv` |
| `PaymentPriority` | `Payment priority – main` (serious-delinquency rate, one row per loan type) | `payment_priority.csv` |

Keep the dashboard names exactly as they are, because the website uses them. All dashboards size automatically to the width the site gives them. The file opens on the `Public share` worksheet; click the dashboard tabs at the bottom to see the rest.

---

## 1. One-time setup

1. Create a free account at https://public.tableau.com. Your **profile name** is the last part of `https://public.tableau.com/app/profile/<profile-name>`.
2. Install the **Tableau Public** app from https://www.tableau.com/products/public/download and sign in.

## 2. Open, check, save

1. In the Tableau Public app choose **File → Open…** and pick `tableau/WhoHoldsTheDebt-extracts.twbx`. If it offers to upgrade the file, click **OK**.
2. Quick checks:
   - **Ratchet:** the coloured bands fill 0–100%, with the public holders (blues/teal) at the bottom. This stack order is now built into the file. If it's ever wrong, click the `Bucket label` pill on Color → **Sort… → Field `Sort order`, Minimum, Descending**.
   - **CrisisSmallMultiples:** one panel per crisis, labelled and ordered by year ("1953 Recession" … "2025 Collections").
   - **Collateral** and **PaymentPriority:** lines and areas in purple (home-backed), amber (vehicle), red (no collateral) and grey (other), with the same names in the legend.
3. **File → Save to Tableau Public As…**, keep the name **`WhoHoldsTheDebt-extracts`** and confirm the overwrite. Saving under the same name replaces the published version at the same URLs, so the website needs no change and no redeploy.

If something fails, copy the **exact error text** (many dialogs have "Show details"/"Copy"), take a screenshot, and send both to Claude.

## 3. What the Ratchet fields mean

Each row of `ratchet.csv` is one quarter × one holder of the debt × one debt type, from 1951Q4 to 2026Q2.

| Field | Meaning |
|---|---|
| `Date` | The quarter, stored as its last day (2026-06-30 = 2026Q2). |
| `Bucket label` | Who bears the credit risk. The public buckets are Federal government (direct), GSEs & agency pools, and State & local. The private buckets are Banks & credit unions, Private securitization & mortgage REITs, and Finance companies & other. |
| `Sort order` | 1–6, the stacking order. |
| `Share of total` | This bucket's slice of all household mortgages + consumer credit that quarter. Summed over buckets it is 100%. |
| `Public share` | The three public buckets combined: **3.2% in 1952 → 56.4% in 2026Q2**. It repeats on every row of a quarter, so the sheet averages it. |
| `Recession`, `Crisis id` | 1 and the NBER recession's id inside a recession; 0 and empty otherwise. These are in the data but not drawn. |

## 4. Connecting the website (already done; for reference)

In Vercel (**Project → Settings → Environment Variables**):

- `NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE` = your profile name;
- `NEXT_PUBLIC_TABLEAU_VIEWS` = `Ratchet,CrisisSmallMultiples,Collateral,PaymentPriority`.

After changing either variable, **Redeploy**, because `NEXT_PUBLIC_*` values are baked in at build time. You don't need to redeploy after re-saving the workbook.

## 5. The quarterly refresh

1. The GitHub Action (`.github/workflows/refresh.yml`) re-runs the pipeline after each Fed Z.1 release. Download the **`data-snapshots-<run id>`** artifact from the latest successful **refresh** run and copy its `tableau/data/` files over this repo's `tableau/data/`. Alternatively, run `cd pipeline && uv run hhdebt export-tableau` locally.
2. Rebuild the workbook and its extracts from the repo root:
   `uv run --with tableauhyperapi python tableau/build_workbook.py`
   Add `--check` to also re-read the files with `tableaudocumentapi` (`--with tableaudocumentapi --with setuptools`).
3. Open `tableau/WhoHoldsTheDebt-extracts.twbx`, check that the Ratchet's latest public share looks right (2026Q2 = **56.4%**), and **Save to Tableau Public As… `WhoHoldsTheDebt-extracts`** (overwrite).
4. Commit the updated CSVs and workbook files.

> Rebuilding with the script replaces any edits made by hand in Tableau. Make lasting changes in `build_workbook.py` instead.

## 6. Plan B: build the Ratchet by hand (about 10 minutes)

Use this only if the generated file won't open at all.

1. **Connect → Text file** → `tableau/data/ratchet.csv`. Check that `date` is a Date and the shares are numbers, then click **Sheet 1** and rename it `Ratchet – main`.
2. Right-click-drag `date` to **Columns** → green `QUARTER(date)`. Drag `share_of_total` to **Rows**, set Marks to **Area**, and drag `bucket_label` to **Color**.
3. Number format: right-click `share_of_total` → **Default Properties → Number Format → Percentage**, 0 decimals.
4. Order and colours: on the `bucket_label` pill choose **Sort → Field `sort_order`, Minimum, Descending**. Then **Color → Edit Colors**: Federal `#1C5CAB`, GSEs `#1BAF7A`, State & local `#3987E5`, Banks `#E34948`, Private securitization `#EDA100`, Finance cos. `#E87BA4`.
5. New worksheet `Public share`: green `QUARTER(date)` on Columns, `public_share` on Rows, pill → **Measure → Average**, Marks **Line**.
6. New dashboard `Ratchet`: **Size → Automatic**. Drag in `Ratchet – main`, then `Public share` below it, and add a Text title `Who holds US household debt? 1952–2026`.
7. **Data → ratchet → Extract Data… → Extract**, then **Save to Tableau Public As… `WhoHoldsTheDebt-extracts`**.

## 7. Later

Richer versions of the dashboards (parameters, reference lines, KPI tiles, phone layouts) are described in `workbook_specs.md`. Moving to Tableau Desktop/Cloud with a live database connection is covered in `README.md` (*Upgrade later*).
