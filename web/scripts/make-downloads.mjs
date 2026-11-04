// Open-data downloads (PLAN F4; decisions F4-1 to F4-3). Writes public/downloads/v1/:
//   latest/<table>.csv|json              every table the dictionary marks redistribute: true, from
//                                         the committed snapshots in public/data (what the charts show)
//   latest/dictionary.json, LICENSE-DATA.md, NOTICE-nyfed.txt
//   vintages/z1-<date>/...               the same for every archived vintage in ../opendata/archive
//   index.json                           every vintage and file
// `v1` is the contract: file names and columns under it change only with a new version (see
// opendata/CHANGELOG.md). Runs before every build. ../opendata/dictionary.json is the source; lib/opendata.json
// is the committed copy the /data page reads, refreshed here when the repo root is available.
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { gunzipSync } from "node:zlib";

const web = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(web, "..", "opendata", "dictionary.json");
const archiveDir = join(web, "..", "opendata", "archive");
const copy = join(web, "lib", "opendata.json");
const dataDir = join(web, "public", "data");
const out = join(web, "public", "downloads", "v1");
const check = process.argv.includes("--check");

const dictText = existsSync(src) ? readFileSync(src, "utf8") : readFileSync(copy, "utf8");
if (existsSync(src) && (!existsSync(copy) || readFileSync(copy, "utf8") !== dictText)) {
  if (check) {
    console.error("web/lib/opendata.json is stale: run node web/scripts/make-downloads.mjs");
    process.exit(1);
  }
  writeFileSync(copy, dictText);
}
if (check) {
  console.log("web/lib/opendata.json up to date");
  process.exit(0);
}
const dict = JSON.parse(dictText);
const L = dict.licences;

const cell = (v) => {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
};

/** Writes one vintage's files into `dir`. `read(name)` returns a snapshot's parsed JSON or null. */
function writeVintage(dir, read, label) {
  mkdirSync(dir, { recursive: true });
  const meta = read("meta") ?? {};
  const files = [];
  for (const t of dict.tables.filter((t) => t.redistribute)) {
    const rows = read(t.name);
    if (!rows) continue; // a table that did not exist in an older vintage
    const cols = t.columns.map((c) => c.name);
    const extra = Object.keys(rows[0] ?? {}).filter((k) => !cols.includes(k));
    if (extra.length) throw new Error(`${label} ${t.name}: columns ${extra.join(", ")} are not in opendata/dictionary.json`);
    writeFileSync(join(dir, `${t.name}.csv`), [cols.join(","), ...rows.map((r) => cols.map((c) => cell(r[c])).join(","))].join("\n") + "\n");
    const lic = L[t.licence];
    writeFileSync(
      join(dir, `${t.name}.json`),
      JSON.stringify({
        table: t.name, title: t.title, licence: lic.name, licence_url: lic.url, attribution: lic.attribution,
        ...(lic.source_identifier ? { source_identifier: lic.source_identifier } : {}),
        vintages: meta.vintages, cpi_base_quarter: meta.cpi_base_quarter, columns: t.columns, rows,
      }) + "\n",
    );
    files.push({ table: t.name, licence: t.licence, rows: rows.length, csv: `${t.name}.csv`, json: `${t.name}.json` });
  }
  writeFileSync(join(dir, "dictionary.json"), JSON.stringify({ ...dict, vintages: meta.vintages, cpi_base_quarter: meta.cpi_base_quarter,
    mart_start: meta.mart_start, mart_end: meta.mart_end, files }, null, 1) + "\n");
  const used = [...new Set(files.map((f) => f.licence))];
  writeFileSync(join(dir, "LICENSE-DATA.md"), `# Licences for these downloads

Source vintages: ${Object.entries(meta.vintages ?? {}).map(([k, v]) => `${k} ${v}`).join(", ")}.

${used.map((k) => `## ${L[k].name}
${L[k].url}

Applies to: ${files.filter((f) => f.licence === k).map((f) => f.table).join(", ")}. ${L[k].applies_to}

Attribution: ${L[k].attribution}${L[k].source_identifier ? `\n\nSource identifier (keep it with the data): ${L[k].source_identifier}` : ""}
`).join("\n")}
## Code: ${L.mit.name}
${L.mit.applies_to} ${dict.repository}

## Not redistributed here
${dict.third_party_not_redistributed.map((x) => `- ${x.name} (${x.series}): ${x.link}. ${x.why}`).join("\n")}
`);
  if (used.includes("nyfed-terms")) {
    const n = L["nyfed-terms"];
    writeFileSync(join(dir, "NOTICE-nyfed.txt"), `${n.attribution}\n${n.source_identifier}\n\nApplies to: ${files.filter((f) => f.licence === "nyfed-terms").map((f) => `${f.csv}, ${f.json}`).join("; ")}.\n${n.applies_to}\nTerms: ${n.url}\n`);
  }
  return { vintages: meta.vintages ?? {}, files };
}

rmSync(out, { recursive: true, force: true });
const fromDisk = (name) => {
  const p = join(dataDir, `${name}.json`);
  return existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : null;
};
const index = { version: "v1", latest: { path: "latest/", ...writeVintage(join(out, "latest"), fromDisk, "latest") }, vintages: [] };

if (existsSync(archiveDir)) {
  for (const v of readdirSync(archiveDir).filter((d) => d.startsWith("z1-")).sort().reverse()) {
    const fromArchive = (name) => {
      const p = join(archiveDir, v, `${name}.json.gz`);
      return existsSync(p) ? JSON.parse(gunzipSync(readFileSync(p)).toString("utf8")) : null;
    };
    index.vintages.push({ id: v, path: `vintages/${v}/`, ...writeVintage(join(out, "vintages", v), fromArchive, v) });
  }
} else {
  console.log(`make-downloads: ${archiveDir} not found; publishing latest only`);
}
writeFileSync(join(out, "index.json"), JSON.stringify(index, null, 1) + "\n");
console.log(`make-downloads: latest (${index.latest.files.length} tables) + ${index.vintages.length} archived vintage(s) -> public/downloads/v1`);
