// Refreshes lib/claims.json and the shared source-register files from claims/ (PLAN F1).
// Runs before every build and dev server. If the repo root is not available (the site built from its
// own folder alone), the committed copies are kept.
import { existsSync } from "node:fs";
import { dirname, join, basename } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const siteDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const shared = join(siteDir, "..", "claims", "site", "sync.mjs");
if (!existsSync(shared)) {
  console.log(`sync-claims: ${shared} not found, keeping committed lib/claims.json`);
} else {
  const { sync } = await import(pathToFileURL(shared).href);
  sync([basename(siteDir)]);
  console.log("sync-claims: lib/claims.json and shared F1 files refreshed");
}
