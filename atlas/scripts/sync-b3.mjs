// PLAN B3: copies the scenario engine and its committed inputs from research/b3_scenarios/ into lib/b3/,
// so the /scenarios page runs exactly the engine that is checked against the Python core. Runs before every
// build and dev server. If the repo root is not available (the site built from its own folder alone), the
// committed copies are kept. lib/b3/manifest.json records each file's SHA-256; lib/b3/sync.test.ts checks
// that the copies still match their sources.
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(siteDir, "..", "research", "b3_scenarios");
const out = join(siteDir, "lib", "b3");
export const FILES = {
  "engine.mjs": "engine.mjs",
  "cases.json": "fixtures/cases.json",
  "exposures.json": "exposures.json",
  "preset_dfast2026.json": "presets/dfast2026.json",
  "preset_replay_2008_2012.json": "presets/replay_2008_2012.json",
  "results_dfast2026.json": "results_dfast2026.json",
  "results_replay_2008_2012.json": "results_replay_2008_2012.json",
};

if (!existsSync(join(src, "engine.mjs"))) {
  console.log(`sync-b3: ${src} not found, keeping committed lib/b3/`);
} else {
  const manifest = {};
  for (const [to, from] of Object.entries(FILES)) {
    copyFileSync(join(src, from), join(out, to));
    manifest[to] = { source: `research/b3_scenarios/${from}`,
                     sha256: createHash("sha256").update(readFileSync(join(out, to))).digest("hex") };
  }
  writeFileSync(join(out, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  console.log(`sync-b3: ${Object.keys(FILES).length} files refreshed in lib/b3/`);
}
