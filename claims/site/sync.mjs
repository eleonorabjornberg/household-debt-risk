// Writes <site>/lib/claims.json from the register and copies the shared F1 files into each site.
//   node claims/site/sync.mjs                 # both sites
//   node claims/site/sync.mjs --site web      # one site (each site's prebuild runs this)
//   node claims/site/sync.mjs --check         # exit 1 if any committed copy is stale (CI)
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { exportSite, ROOT } from "../site_export.mjs";

export const SITES = ["web", "atlas"];
const HERE = join(ROOT, "claims", "site");
const COPIES = [
  ["claims-core.ts", "lib/claims-core.ts"],
  ["SourceRef.tsx", "components/claims/SourceRef.tsx"],
  ["SourcesList.tsx", "components/claims/SourcesList.tsx"],
  ["claims.css", "app/claims.css"],
  ["claims.test.ts", "lib/claims.test.ts"],
];

export function outputs(site) {
  const files = COPIES.map(([src, dst]) => [join(ROOT, site, dst), readFileSync(join(HERE, src), "utf8")]);
  files.push([join(ROOT, site, "lib", "claims.json"), JSON.stringify(exportSite(site), null, 1) + "\n"]);
  return files;
}

export function sync(sites = SITES, check = false) {
  const stale = [];
  for (const site of sites) {
    for (const [path, body] of outputs(site)) {
      const cur = existsSync(path) ? readFileSync(path, "utf8") : null;
      if (cur === body) continue;
      if (check) stale.push(path.slice(ROOT.length + 1));
      else {
        mkdirSync(dirname(path), { recursive: true });
        writeFileSync(path, body);
      }
    }
  }
  return stale;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const i = process.argv.indexOf("--site");
  const sites = i > 0 ? [process.argv[i + 1]] : SITES;
  const check = process.argv.includes("--check");
  const stale = sync(sites, check);
  if (check && stale.length) {
    console.error(`stale F1 copies (run: node claims/site/sync.mjs):\n  ${stale.join("\n  ")}`);
    process.exit(1);
  }
  console.log(check ? "F1 site copies up to date" : `claims/site/sync: ${sites.join(", ")} updated`);
}
