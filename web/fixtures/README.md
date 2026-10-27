# Fixtures (synthetic, not real data)

These JSON files are **fake**. They have the exact shape of the `mart` tables and the two `core` dims
(`supabase/migrations/20261027000000_init.sql`), with hand-shaped curves so the charts have something
to draw during development. Never quote numbers from them.

`lib/data.ts` uses a fixture only when neither Supabase nor `public/data/<table>.json` provides that
table, and the home page then shows a "Fixture data" banner.

Regenerate with `npm run fixtures` (`scripts/make-fixtures.mjs`, deterministic).
