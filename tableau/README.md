# Tableau: connecting to Supabase and publishing

Tableau reads **only** the `mart` schema plus three `core` dimension tables (`core.dim_crisis`, `core.dim_risk_bucket`, `core.dim_series`). It connects as the read-only role `tableau_reader`, which is created in `supabase/migrations/20261027000000_init.sql`. The website embeds the published views; see `workbook_specs.md`.

## 1. One-time database setup (project owner)

```sql
-- in the Supabase SQL editor, as postgres
alter role tableau_reader password '<long-random-password>';
-- optional hardening
alter role tableau_reader set statement_timeout = '60s';
alter role tableau_reader set default_transaction_read_only = on;
```

Store the password in the team password manager, never in the repo. RLS is enabled on every mart table, and the `public_read` policies already include `tableau_reader`.

## 2. Tableau Desktop → Supabase Postgres

Use the **Supavisor pooler in session mode**. The direct `db.<ref>.supabase.co` host is IPv6-only on most plans and Tableau Cloud cannot reach it.

| Field | Value |
|---|---|
| Connector | **PostgreSQL** (Connect → To a Server → PostgreSQL) |
| Server | `aws-0-<region>.pooler.supabase.com` (Supabase → Project Settings → Database → Connection string → *Session pooler*) |
| Port | **5432** (session mode; 6543 is transaction mode, which does not support the prepared statements Tableau uses) |
| Database | `postgres` |
| Authentication | Username and Password |
| Username | **`tableau_reader.<project-ref>`** (Supavisor needs the project ref suffix) |
| Password | the password from step 1 |
| Require SSL | **checked** |

Steps:
1. Install the PostgreSQL JDBC driver if Tableau asks for it (Help → Download drivers → PostgreSQL; put the `.jar` in `~/Library/Tableau/Drivers` on macOS or `C:\Program Files\Tableau\Drivers` on Windows).
2. Fill in the fields above and click **Sign In**. If you get an SSL error, download the Supabase CA certificate (Project Settings → Database → SSL Configuration) and, under *Advanced → Initial SQL / SSL*, set `sslmode=verify-full` with that root cert. Otherwise leave the default `require`.
3. Pick schema **mart** and drag the tables as described in `workbook_specs.md`. The shortcut is to open `hhdebt.tds` (double-click it, or Data → New Data Source → *Tableau Data Source* file). It already holds the connection and the logical model. You only need to replace `<region>` and `<project-ref>` and type the password.
4. Use **Extract**, not Live, for anything published (see §4). Live is fine while authoring.

## 3. Publishing to Tableau Cloud

1. Server → Sign In → `https://<pod>.online.tableau.com` (same value as `TABLEAU_SERVER_URL` in `.env`), site = `TABLEAU_SITE`.
2. Publish the data source first: **Server → Publish Data Source → hhdebt**.
   * Project: `WhoHoldsTheDebt`
   * Authentication: **Embedded password**. The refresh has to run unattended, so do not use "Prompt user".
   * Check "Update workbook to use the published data source".
3. Publish each workbook to the same project with **Server → Publish Workbook**:
   * Workbook name **`WhoHoldsTheDebt`**, a single workbook whose dashboards are named exactly `Ratchet`, `CrisisSmallMultiples`, `Collateral`, `PaymentPriority`. The embed paths are then `views/WhoHoldsTheDebt/Ratchet` and so on.
   * **Show sheets as tabs: off.** Under *Sheets*, publish only the four dashboards; hide the worksheets.
   * Permissions: give the embed user (`TABLEAU_EMBED_USER`, a Viewer) *View* only.
4. Embedding (web team): use a Connected App (direct trust). Create it in Tableau Cloud under Settings → Connected Apps, set the domain allowlist to the Vercel production and preview domains, then copy the client ID, secret ID and secret value into `TABLEAU_CONNECTED_APP_*` in Vercel env vars. The site signs a short-lived JWT (scope `tableau:views:embed`) per page view. Use `<tableau-viz src="https://<pod>.online.tableau.com/t/<site>/views/WhoHoldsTheDebt/Ratchet" token="..." device="default" toolbar="hidden" hide-tabs>`.

## 4. Extract refresh schedule

The data change at most a few times a quarter. The Z.1 is released about 10 weeks after quarter-end (early/mid March, June, September, December), and the NY Fed report comes out about 5–6 weeks after quarter-end. The pipeline reloads `mart.*` after each release (see `.github/workflows`).

* **Extract refresh: weekly, Tuesday 06:15 UTC (full refresh).** The extract is tiny (well under 100k rows), so a full refresh takes seconds.
* Add a **daily** schedule in the two weeks after a Z.1 release if you want the site to pick up the new quarter faster. A simpler option: have the pipeline trigger a refresh through the REST API after a successful load: `POST /api/<ver>/sites/<site-id>/datasources/<ds-id>/refresh`, using a personal access token stored as a GitHub secret.
* Turn on "Send email when refresh fails" for the data source owner.
* Tableau Cloud suspends refreshes for content nobody has viewed in a long time. The embedded views keep the content active, but check the schedule after quiet periods.

## 5. Checks after each refresh

* `Ratchet`: the latest quarter in the header should match `analysis/results.json → latest_quarter`. The public share tooltip for 2026Q2 should read **56.4%**.
* `CrisisSmallMultiples` with *Public share*: the 2007Q4 panel at +16 should read **+13.1 pp**.
* If these don't match, the mart and the analysis disagree on a definition (state and local holders included in public, mortgage apportioning). Reconcile with `analysis/tables/public_share_quarterly.csv`.
