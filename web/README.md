# Who Holds the Debt? (story site)

Next.js 16 (App Router, TypeScript) scrollytelling essay on why most US household debt now sits on
public balance sheets, and why crises (with one exception, 2007) didn't put it there. Pages are statically generated and revalidated about
once a day; the site works with no environment variables at all.

## Local development

```bash
cd web
npm install
npm run dev            # http://localhost:3000
npm run build && npm start   # production build (runs scripts/sync-catalog.mjs first)
npm run lint
```

## Where things live

| What | File |
|---|---|
| All reader-facing copy and the analysis numbers it quotes (`facts`) | `content/story.ts` (numbers from `analysis/results.json` / `findings.md`) |
| Series catalog shown on `/methods` | `content/series_catalog.json`, regenerated from `../pipeline/series_catalog.yaml` on every build |
| Data access (Supabase → snapshots → fixtures) | `lib/data.ts` |
| Row types (mirror the `mart` tables) | `lib/types.ts` |
| Rows → chart-ready arrays, headline numbers | `lib/shape.ts` |
| Native SVG charts | `components/charts/*` (one shared `TimeSeriesChart`) |
| Tableau embed (Public or Cloud) + Cloud token route | `components/TableauViz.tsx`, `lib/tableau.ts`, `app/api/tableau-token/route.ts` |
| Synthetic dev data | `fixtures/*.json` (fake; `npm run fixtures` regenerates) |

## Data sources, in order

1. **Supabase**, when `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (or the legacy `NEXT_PUBLIC_SUPABASE_ANON_KEY`) are set. Reads the
   `mart` schema with `@supabase/supabase-js` (`db: { schema: 'mart' }`), paging 1,000 rows at a time.
2. **Pipeline snapshots** in `public/data/<table>.json` (one per mart table plus `dim_crisis`,
   `dim_risk_bucket`, and optional `meta.json`). The pipeline writes these; don't edit them by hand.
3. **Fixtures** in `fixtures/<table>.json`. Clearly fake; the home page shows a "Fixture data" banner.

A failed Supabase read for a table falls back to the files for that table (logged at build time).
Results are cached with `"use cache"` + `cacheLife("days")`.

## Environment variables

See `.env.example`. All are optional.

| Variable | Used for |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Live reads of the `mart` schema. The key starts `sb_publishable_`; `NEXT_PUBLIC_SUPABASE_ANON_KEY` is accepted as a fallback |
| `NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE` | Your Tableau Public profile name. Turns on **Public mode** (takes precedence over Cloud) |
| `NEXT_PUBLIC_TABLEAU_VIEWS` | Public mode: comma-separated sheet names that are published, e.g. `Ratchet` |
| `NEXT_PUBLIC_TABLEAU_SCROLLY` | `1` lets the chapter 2 scroll-through drive the Ratchet view (needs automatic dashboard sizing). Anything else: native chart |
| `TABLEAU_SERVER_URL` | Cloud: e.g. `https://10ax.online.tableau.com`; also where the Embedding API script loads from |
| `TABLEAU_SITE` | Cloud: site content URL (the `/t/<site>/` part); blank for the default site |
| `TABLEAU_CONNECTED_APP_CLIENT_ID`, `..._SECRET_ID`, `..._SECRET_VALUE` | Cloud: Connected App (direct trust) credentials, server-only |
| `TABLEAU_EMBED_USER` | Cloud: Tableau username the embed token acts as (JWT `sub`) |

**`NEXT_PUBLIC_*` values are inlined at build time.** After adding or changing any of them in Vercel
(or `.env.local`), redeploy (or rebuild); a running deployment won't pick the change up.

Views embedded: `WhoHoldsTheDebt/Ratchet`, `/CrisisSmallMultiples`, `/Collateral`, `/PaymentPriority`
(`TABLEAU_VIEWS` in `lib/tableau.ts`). `/methods` shows which mode the build is using.

### Tableau Public (start here)

1. Publish the workbook to Tableau Public as `WhoHoldsTheDebt` (so the views URL is
   `https://public.tableau.com/views/WhoHoldsTheDebt/Ratchet`). Check the URL on Tableau Public; if the
   workbook or sheet name differs, update `TABLEAU_VIEWS` in `lib/tableau.ts`.
2. Set `NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE` to your profile name and `NEXT_PUBLIC_TABLEAU_VIEWS` to the
   sheets that exist (start with `Ratchet`), then redeploy. Add more sheet names as you publish them.

In Public mode the Embedding API v3 loads from
`https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js` and each listed figure
renders `<tableau-viz src="https://public.tableau.com/views/WhoHoldsTheDebt/<Sheet>" toolbar="bottom" hide-tabs>`
with **no token** (`/api/tableau-token` is never called). Its source line gets an "Open on Tableau
Public" link to `https://public.tableau.com/app/profile/<profile>/viz/WhoHoldsTheDebt/<Sheet>`. Figures
whose sheet isn't listed keep the native chart and the "interactive version coming" note; with
`NEXT_PUBLIC_TABLEAU_VIEWS` unset, no figure embeds.

### Tableau Cloud (upgrade later)

Used only when `NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE` is blank and all five required Cloud variables are
set; then every figure embeds. If any is missing, `GET /api/tableau-token` returns **503** with the list
of missing variables. With them set, the route returns `{ token, expiresIn }`: an HS256 JWT with
`iss` = client id, header `kid` = secret id, `aud` = `tableau`, `sub` = embed user,
`scp` = `["tableau:views:embed"]`, a random `jti`, and a 5-minute expiry. The token route is public by
design (anyone viewing the story needs a token), so give `TABLEAU_EMBED_USER` a Viewer-role account
that can see only this workbook.

### Crisis scroll-through (chapter 2) and two-way linking

`components/scrolly/CrisisScrolly.tsx` puts a sticky Ratchet chart beside one step card per crisis
(NBER recessions plus policy shocks). When a step reaches the middle of the viewport, the chart zooms
to t0 − 2y … t0 + 4y and the crisis is highlighted; leaving the section resets it. A holder legend
next to the chart highlights a holder, and a side card shows that holder's share, from the site's own
data. Figure 2's panel titles jump to the matching step. On phones (≤ 768px) the chart sticks to the
top and the steps scroll underneath.

By default the scroll-through uses the native `RatchetChart`. With `NEXT_PUBLIC_TABLEAU_SCROLLY=1`
(and the Ratchet view configured) on wide screens it lazy-loads its own Ratchet embed and drives it
through `lib/tableauControl.ts`, following `tableau/INTEGRATION_CONTRACT.md`: Date range filter on
both worksheets, the `Active crisis` parameter (skipped if the published workbook lacks it), and
`selectMarksByValueAsync` on `Ratchet – main`. It also listens for `markselectionchanged` to update the
side card. Turn the flag on only once the published dashboard uses automatic sizing; a fixed
1000×700 dashboard is clipped in the column. Figure 1's embed does not depend on this flag. Every
API failure is logged once and ignored.

### Fallbacks

With no Tableau configuration every figure shows its native chart with a short "interactive version
coming" note. In either mode the native chart is shown while the embed loads, and stays (with a short
note) if the Embedding API script fails to load, the token request fails, the viz fires a
`vizloaderror` event, or it doesn't fire `firstinteractive` within 30 seconds (a missing Tableau Public
view shows a "Where's the viz?" page without a load error, so this catches sheets listed before they're published).

Chart colors match the Tableau workbook (`tableau/workbook_specs.md` §0.2): CSS variables
`--b-<risk_bucket>` and `--c-<collateral_class>` in `app/globals.css`, with validated dark-mode steps.

## Deploying on Vercel

1. Import the repository and set **Root Directory** to `web`. Framework preset: Next.js (auto). No
   other build settings are needed.
2. Keep "Include source files outside of the Root Directory in the Build Step" enabled (the default)
   so the build can refresh the catalog from `pipeline/series_catalog.yaml`. If it's disabled the
   committed `content/series_catalog.json` is used.
3. Add the environment variables above for Production (and Preview if wanted), then redeploy.
   For Tableau Public that's just `NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE` and `NEXT_PUBLIC_TABLEAU_VIEWS`;
   because they're inlined at build time, each change needs a new deployment.

## Exposing the `mart` schema in Supabase

The migration already grants `anon` read access to `mart` and adds `public_read` RLS policies. PostgREST
only serves schemas you list, so:

1. Supabase Dashboard → **Project Settings → API** (Data API) → **Exposed schemas**: add `mart`, save.
2. The two dimension tables live in `core` (not exposed). `supabase/migrations/20261027010000_mart_dim_views.sql`
   exposes them as read-only `mart.dim_crisis` / `mart.dim_risk_bucket` views (already applied to the
   hosted project). Until they exist the site reads both dims from `public/data/` (or the fixtures).
3. Copy the project URL and the publishable key (`sb_publishable_...`) into `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
