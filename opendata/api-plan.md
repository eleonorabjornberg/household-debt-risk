# Public read-only API: plan (F4)

**Status: options for Eleonora. Nothing here is built or exposed.** PLAN.md and the track rules say any
public API exposure needs her approval first.

## What exists today

- **Static downloads** (built in F4): `/downloads/<table>.csv|json`, `/downloads/dictionary.json` on the
  web site, regenerated from the committed snapshots on every build. This is already a stable, cacheable,
  read-only interface with no server code and no database access.
- **Supabase REST (PostgREST)**: the sites read `mart.*` with the public anon key. That key is in the
  browser bundle by design, so the `mart` tables are technically readable by anyone who finds it. It is not
  documented or promised as an API.
- **MCP server** (`mcp/household-credit-mcp`, D5): local stdio, for Claude; not a public endpoint.

## Options

| | A. Static files only (now) | B. Versioned JSON API on the web site | C. Document Supabase REST |
|---|---|---|---|
| What | Keep `/downloads/`; add a stable versioned path `/downloads/v1/` and a changelog | Next.js route handlers `GET /api/v1/tables`, `GET /api/v1/tables/{name}?from=&to=&columns=&format=csv|json`, `GET /api/v1/claims/{id}`, all served from the same committed snapshots and the register | Publish PostgREST URLs and the anon key as the API |
| Database load | None | None (reads files in the deployment) | Every call hits the production database |
| Abuse surface | CDN only | CDN-cached; Vercel firewall/rate limits available | Free-tier database; Supabase rate limits only |
| Schema promise | File columns (dictionary) | `/v1` contract, independent of the warehouse schema | Couples users to `mart` table names |
| Vintages | Current only, unless we keep old files | Can serve `?vintage=` from archived snapshots | Latest only |
| Work | Small | ~1 day: handlers, OpenAPI file, tests, docs page | Docs only, but hard to take back |

## Recommendation (Claude draft, for Eleonora to decide)

A now; B when there is a user for it, and only after she approves exposing it. Not C: it turns the
production database into a public dependency and fixes the warehouse schema as a contract.

If she picks B: an OpenAPI 3.1 file in `opendata/openapi.yaml`, handlers under `web/app/api/v1/`, CSV and
JSON with the same licence fields as the downloads, `Cache-Control: public, s-maxage=86400`, no
authentication, and a preview-deployment test in CI before anything reaches production.

## Questions

- F4-2: Approve option A only, or A then B?
- F4-3: Should old vintages stay downloadable (archive each Z.1 release under `/downloads/<z1 vintage>/`)?
