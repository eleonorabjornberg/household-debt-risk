// Copies the pipeline's JSON snapshots from ../web/public/data into public/data, so the site
// still renders when Supabase is not configured or unreachable. On Vercel the repo is cloned in
// full, so the sibling folder exists even with Root Directory = atlas.
import { cp, mkdir, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(here, "..", "..", "web", "public", "data");
const dst = path.join(here, "..", "public", "data");
const WANT = ["debt_by_risk_holder", "public_share", "dim_crisis", "dim_risk_bucket", "meta"];

await mkdir(dst, { recursive: true });
let files;
try {
  files = await readdir(src);
} catch {
  console.warn(`[copy-data] ${src} not found; keeping existing public/data`);
  process.exit(0);
}
for (const f of files.filter((f) => WANT.includes(path.parse(f).name))) {
  await cp(path.join(src, f), path.join(dst, f));
}
console.log(`[copy-data] copied ${WANT.length} snapshot files`);
