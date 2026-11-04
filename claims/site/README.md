# Source register in the sites (PLAN F1)

Every registered number on `atlas/` and `web/` links to its row in `claims/register.csv` (and
`claims/tracks/*.csv`). Hover or focus a number to see the claim, period, computation (validation
check, code path or query), series, vintage and validation status; click it to open the full row on the
site's `/sources` page.

| File | Copied to | What |
|---|---|---|
| `../site_export.mjs` | `<site>/lib/claims.json` | Register rows with a location in that site, plus text anchors from the cited lines |
| `claims-core.ts` | `<site>/lib/claims-core.ts` | Matcher: splits a rendered string into text and claim segments |
| `SourceRef.tsx` | `<site>/components/claims/SourceRef.tsx` | `<Sourced text>` (auto-link) and `<ClaimRef id>` (explicit) |
| `SourcesList.tsx` | `<site>/components/claims/SourcesList.tsx` | The `/sources` table |
| `claims.css` | `<site>/app/claims.css` | Popover and table styles (uses the site's `--paper`, `--ink`, `--muted`, `--rule`, `--accent`) |

Edit the files here, never the copies: each site's `prebuild` (`scripts/sync-claims.mjs`) refreshes
them, and `node claims/site/sync.mjs --check` (run in CI) fails if a committed copy is stale. The copies
are committed so a site still builds when only its own folder is available.

## How a number gets linked

1. A claim is **eligible** in a rendered string when the string (or the context passed with it, such as
   a stat tile's label) contains one of the claim's anchors: a literal fragment of 12+ characters from a
   line its `locations` point at. Placeholders (`${facts.x}`, `{share}`) are cut out of the anchors, so
   copy filled at render time still matches. A string that is exactly a short literal on a cited line
   (`stat: "p ≈ 0.30"`) also matches.
2. Within that string, every display spelling of an eligible claim is linked, longest spelling first,
   with digit boundaries (`7%` never matches inside `17%`).
3. Numbers computed in components (no literal on the cited line) are wrapped explicitly:
   `<ClaimRef id="public_share_2026q2">{pct(x, 1)}</ClaimRef>`.

A wrong or missing `locations` entry therefore shows up as an unlinked number. Each site's
`lib/claims.test.ts` renders every copy string through the matcher and fails if a claim located in a
copy file is never linked.
