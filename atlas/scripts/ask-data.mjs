// Exports what the Ask Hot Potato tools (lib/ask, PLAN D6) read besides the snapshots: the series catalog
// (pipeline/series_catalog.yaml) and the claims register (claims/register.csv).
// Runs before every build and dev server. If the repo root is not available, the committed copies are kept.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..", "..");
const out = path.join(here, "..", "lib", "ask");

/** Minimal RFC 4180 parser (quoted fields, doubled quotes, newlines inside quotes). */
export function parseCsv(text) {
  const rows = [];
  let row = [], field = "", inQ = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQ) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') inQ = false;
      else field += c;
    } else if (c === '"') inQ = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.length > 1 || row[0] !== "") rows.push(row);
      row = [];
    } else field += c;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows;
  return body.map((r) => Object.fromEntries(head.map((h, j) => [h, r[j] ?? ""])));
}

const catalogPath = path.join(root, "pipeline", "series_catalog.yaml");
if (!existsSync(catalogPath)) {
  console.log("ask-data: repo root not found, keeping committed lib/ask/*.json");
} else {
  const cat = YAML.parse(readFileSync(catalogPath, "utf8"));
  const catalog = { series: cat.series, risk_buckets: cat.risk_buckets, collateral_classes: cat.collateral_classes };
  writeFileSync(path.join(out, "catalog.json"), JSON.stringify(catalog) + "\n");
  // The main register only, as the MCP server's lookup_claim reads it (track rows are folded in on merge).
  const files = [path.join(root, "claims", "register.csv")];
  const keep = ["claim_id", "claim", "display", "value", "unit", "period", "check_id", "series_ids", "vintage",
                "validation", "computation", "notes"];
  const claims = files.flatMap((f) => parseCsv(readFileSync(f, "utf8")))
    .map((r) => Object.fromEntries(keep.map((k) => [k, r[k] ?? ""])));
  writeFileSync(path.join(out, "register.json"), JSON.stringify(claims) + "\n");
  console.log(`ask-data: catalog (${catalog.series.length} series) and register (${claims.length} claims) exported`);
}
