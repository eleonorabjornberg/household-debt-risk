// Copies ../analysis/findings.md into content/findings.md for the findings on /dashboard (docket 48 site-findings (b)),
// so the page shows the findings as they stand and a later edit reaches it on the next build.
// Runs before every build and dev start; if the source isn't reachable it keeps the committed copy.
// --check: exit 1 if the committed copy is stale (no write).
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "analysis", "findings.md");
const out = join(here, "..", "content", "findings.md");
const check = process.argv.includes("--check");

if (!existsSync(src)) {
  console.log(`sync-findings: ${src} not found, keeping ${out}`);
  process.exit(0);
}
const text = readFileSync(src, "utf8");
const same = existsSync(out) && readFileSync(out, "utf8") === text;
if (check) {
  console.log(same ? "sync-findings: content/findings.md up to date" : "sync-findings: content/findings.md is stale");
  process.exit(same ? 0 : 1);
}
if (!same) writeFileSync(out, text);
console.log(`sync-findings: ${same ? "unchanged" : "wrote"} content/findings.md`);
