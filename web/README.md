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
| Crisis scroll-through (chapter 2) | `components/scrolly/CrisisScrolly.tsx` |
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

**`NEXT_PUBLIC_*` values are inlined at build time.** After adding or changing any of them in Vercel
(or `.env.local`), redeploy (or rebuild); a running deployment won't pick the change up.

### Crisis scroll-through (chapter 2)

`components/scrolly/CrisisScrolly.tsx` puts a sticky Ratchet chart beside one step card per crisis
(NBER recessions plus policy shocks). When a step reaches the middle of the viewport, the chart zooms
to t0 − 2y … t0 + 4y and the crisis is highlighted; leaving the section resets it. A holder legend
next to the chart highlights a holder, and a side card shows that holder's share, from the site's own
data. Figure 2's panel titles jump to the matching step. On phones (≤ 768px) the chart sticks to the
top and the steps scroll underneath.

The chart is the native `RatchetChart`, driven by the active step (zoom and crisis highlight) and the legend.

Chart colors (public cool, private warm): CSS variables
`--b-<risk_bucket>` and `--c-<collateral_class>` in `app/globals.css`, with validated dark-mode steps.

## Deploying on Vercel

1. Import the repository and set **Root Directory** to `web`. Framework preset: Next.js (auto). No
   other build settings are needed.
2. Keep "Include source files outside of the Root Directory in the Build Step" enabled (the default)
   so the build can refresh the catalog from `pipeline/series_catalog.yaml`. If it's disabled the
   committed `content/series_catalog.json` is used.
3. Add the environment variables above for Production (and Preview if wanted), then redeploy.
   `NEXT_PUBLIC_*` values are inlined at build time, so each change needs a new deployment.

## Exposing the `mart` schema in Supabase

The migration already grants `anon` read access to `mart` and adds `public_read` RLS policies. PostgREST
only serves schemas you list, so:

1. Supabase Dashboard → **Project Settings → API** (Data API) → **Exposed schemas**: add `mart`, save.
2. The two dimension tables live in `core` (not exposed). `supabase/migrations/20261027010000_mart_dim_views.sql`
   exposes them as read-only `mart.dim_crisis` / `mart.dim_risk_bucket` views (already applied to the
   hosted project). Until they exist the site reads both dims from `public/data/` (or the fixtures).
3. Copy the project URL and the publishable key (`sb_publishable_...`) into `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
