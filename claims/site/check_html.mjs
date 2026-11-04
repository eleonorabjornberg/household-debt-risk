// After `next build`, checks that every register row located on a site is a link in the prerendered
// HTML (PLAN F1 acceptance: hovering or clicking a number shows its register row).
//   node claims/site/check_html.mjs --site web     (run from the repo root, after the site's build)
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { ROOT } from "../site_export.mjs";

const i = process.argv.indexOf("--site");
const site = i > 0 ? process.argv[i + 1] : null;
if (!site) { console.error("usage: node claims/site/check_html.mjs --site web|atlas"); process.exit(2); }
const appDir = join(ROOT, site, ".next", "server", "app");
if (!existsSync(appDir)) { console.error(`${appDir} not found: run the site's build first`); process.exit(2); }

const claims = JSON.parse(readFileSync(join(ROOT, site, "lib", "claims.json"), "utf8")).claims;
const allowed = JSON.parse(readFileSync(join(ROOT, "claims", "site", "unlinked.json"), "utf8"))[site] ?? {};
const html = readdirSync(appDir, { recursive: true })
  .filter((f) => String(f).endsWith(".html") && !String(f).includes("_not-found") && !String(f).includes("_global-error") && !String(f).startsWith("sources"))
  .map((f) => readFileSync(join(appDir, String(f)), "utf8"))
  .join("\n");
const linked = new Set([...html.matchAll(/data-claim="([^"]+)"/g)].map((m) => m[1]));
const known = new Set(claims.map((c) => c.id));

const errors = [];
for (const id of linked) if (!known.has(id)) errors.push(`linked id ${id} has no row in lib/claims.json`);
for (const c of claims) {
  if (!linked.has(c.id) && !(c.id in allowed)) errors.push(`${c.id} (${c.display.join(" | ")}) is never linked; locations ${c.locations.join(" ")}`);
  if (linked.has(c.id) && c.id in allowed) errors.push(`${c.id} is linked now: remove it from claims/site/unlinked.json`);
}
for (const id of Object.keys(allowed)) if (!known.has(id)) errors.push(`unlinked.json lists ${id}, which has no row for ${site}`);

if (errors.length) {
  console.error(`F1 ${site}: ${errors.length} problem(s)\n  ${errors.join("\n  ")}`);
  process.exit(1);
}
console.log(`F1 ${site}: ${linked.size} of ${claims.length} register rows linked; ${Object.keys(allowed).length} known exceptions (claims/site/unlinked.json)`);
