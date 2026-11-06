// Loads the Ask Hot Potato tool environment from the site's own files: the snapshot tables in public/data
// (copied by scripts/copy-data.mjs) and lib/ask/{catalog,register}.json (scripts/ask-data.mjs). Server only.
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { parseCsv } from "./csv";
import type { Env, Tables } from "./tools";

const TABLES = ["public_share", "debt_by_risk_holder", "dim_risk_bucket", "collateral_coverage", "crisis_event_window",
                "dim_crisis", "nyfed_by_type", "meta"] as const;
let cached: Promise<Env> | null = null;

export function loadEnv(root: string = process.cwd()): Promise<Env> {
  if (!cached || root !== process.cwd()) {
    const p = (async () => {
      const read = async (f: string) => JSON.parse(await readFile(f, "utf8"));
      // public/data is copied at build time (gitignored); in a fresh checkout read the pipeline's copies directly.
      const own = path.join(root, "public", "data");
      const dir = existsSync(path.join(own, "nyfed_by_type.json")) ? own : path.join(root, "..", "web", "public", "data");
      const tables = Object.fromEntries(await Promise.all(
        TABLES.map(async (t) => [t, await read(path.join(dir, `${t}.json`))]))) as Tables;
      const catalog = await read(path.join(root, "lib", "ask", "catalog.json"));
      // register.json is generated at build time (gitignored); without it, read the register itself.
      const reg = path.join(root, "lib", "ask", "register.json");
      const claims = existsSync(reg) ? await read(reg)
        : parseCsv(await readFile(path.join(root, "..", "claims", "register.csv"), "utf8"));
      return { tables, catalog, claims };
    })();
    if (root !== process.cwd()) return p;
    cached = p;
  }
  return cached;
}
