// Copies ../pipeline/series_catalog.yaml into content/series_catalog.json so /methods can render
// the catalog even when Vercel builds from the web/ root without the rest of the repo.
// Runs before every build (npm "prebuild"); if the YAML isn't reachable it keeps the committed JSON.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parse } from "yaml";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "pipeline", "series_catalog.yaml");
const out = join(here, "..", "content", "series_catalog.json");

if (!existsSync(src)) {
  console.log(`sync-catalog: ${src} not found, keeping ${out}`);
  process.exit(0);
}
const doc = parse(readFileSync(src, "utf8"));
writeFileSync(out, JSON.stringify(doc, null, 2) + "\n");
console.log(`sync-catalog: wrote ${doc.series.length} series to content/series_catalog.json`);
