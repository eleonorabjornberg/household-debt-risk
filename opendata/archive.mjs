// Archives the current snapshots as one published vintage (PLAN F4, decision F4-3).
//   node opendata/archive.mjs            # after an export; no-op if this vintage is already archived
//   node opendata/archive.mjs --check    # CI: fail if the committed vintage is missing or changed
//
// Copies web/public/data/*.json to opendata/archive/z1-<Z.1 vintage>/<file>.json.gz (gzip, fixed
// header, so the same data give the same bytes). An archive is never overwritten: if the directory
// exists with different data the script fails, because a Z.1 vintage, once published, is fixed.
// web/scripts/make-downloads.mjs serves every archive at /downloads/v1/vintages/z1-<date>/.
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { gunzipSync, gzipSync } from "node:zlib";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = join(root, "web", "public", "data");
// Volatile fields that would make an identical vintage look different.
const strip = (name, text) => {
  if (name !== "meta.json") return text;
  const m = JSON.parse(text);
  delete m.generated_at;
  delete m.snapshot_source;
  return JSON.stringify(m, null, 1) + "\n";
};

const meta = JSON.parse(readFileSync(join(dataDir, "meta.json"), "utf8"));
const z1 = meta.vintages?.z1;
if (!z1) throw new Error("meta.json has no vintages.z1");
const dir = join(root, "opendata", "archive", `z1-${z1}`);
const files = readdirSync(dataDir).filter((f) => f.endsWith(".json")).sort();

if (existsSync(dir)) {
  const changed = files.filter((f) => {
    const p = join(dir, `${f}.gz`);
    if (!existsSync(p)) return true;
    const old = gunzipSync(readFileSync(p)).toString("utf8");
    // nyfed retrieval date moves on every download; compare the rest
    const norm = (name, t) => (name === "meta.json" ? JSON.stringify({ ...JSON.parse(t), vintages: { ...JSON.parse(t).vintages, nyfed: null } }) : t);
    return norm(f, old) !== norm(f, strip(f, readFileSync(join(dataDir, f), "utf8")));
  });
  if (changed.length) {
    console.error(`archive z1-${z1} exists and differs in ${changed.join(", ")}. A published vintage is fixed;`
      + " if the data were revised within the same Z.1 release, archive under a new name by hand.");
    process.exit(1);
  }
  console.log(`archive: z1-${z1} already archived, unchanged`);
} else if (process.argv.includes("--check")) {
  console.error(`archive: z1-${z1} (the committed snapshots' vintage) is not archived: run node opendata/archive.mjs`);
  process.exit(1);
} else {
  mkdirSync(dir, { recursive: true });
  for (const f of files) {
    writeFileSync(join(dir, `${f}.gz`), gzipSync(Buffer.from(strip(f, readFileSync(join(dataDir, f), "utf8"))), { level: 9 }));
  }
  console.log(`archive: wrote ${files.length} files to opendata/archive/z1-${z1}/`);
}
