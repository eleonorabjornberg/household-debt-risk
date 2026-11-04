// Open-data downloads (PLAN F4). Writes public/downloads/ from the committed snapshots in public/data
// and the data dictionary:
//   <table>.csv, <table>.json   every table the dictionary marks redistribute: true
//   dictionary.json             columns, units, licences, vintages, row counts
//   LICENSE-DATA.md             licence and attribution text
// Runs before every build. ../opendata/dictionary.json is the source; lib/opendata.json is the
// committed copy (refreshed here when the repo root is available) that the /data page reads.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const web = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(web, "..", "opendata", "dictionary.json");
const copy = join(web, "lib", "opendata.json");
const dataDir = join(web, "public", "data");
const out = join(web, "public", "downloads");
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
const meta = JSON.parse(readFileSync(join(dataDir, "meta.json"), "utf8"));

const cell = (v) => {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
};

mkdirSync(out, { recursive: true });
const summary = [];
for (const t of dict.tables) {
  const entry = { name: t.name, licence: t.licence, redistribute: t.redistribute };
  if (t.redistribute) {
    const rows = JSON.parse(readFileSync(join(dataDir, `${t.name}.json`), "utf8"));
    const cols = t.columns.map((c) => c.name);
    const extra = Object.keys(rows[0] ?? {}).filter((k) => !cols.includes(k));
    if (extra.length) throw new Error(`${t.name}: columns ${extra.join(", ")} are not in opendata/dictionary.json`);
    const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => cell(r[c])).join(","))].join("\n") + "\n";
    writeFileSync(join(out, `${t.name}.csv`), csv);
    const lic = dict.licences[t.licence];
    writeFileSync(
      join(out, `${t.name}.json`),
      JSON.stringify({ table: t.name, title: t.title, licence: lic.name, licence_url: lic.url, attribution: lic.attribution,
        vintages: meta.vintages, cpi_base_quarter: meta.cpi_base_quarter, columns: t.columns, rows }) + "\n",
    );
    entry.rows = rows.length;
  }
  summary.push(entry);
}
writeFileSync(
  join(out, "dictionary.json"),
  JSON.stringify({ ...dict, vintages: meta.vintages, cpi_base_quarter: meta.cpi_base_quarter, mart_start: meta.mart_start, mart_end: meta.mart_end, files: summary }, null, 1) + "\n",
);
const L = dict.licences;
writeFileSync(
  join(out, "LICENSE-DATA.md"),
  `# Licences for these downloads

Source vintages: ${Object.entries(meta.vintages).map(([k, v]) => `${k} ${v}`).join(", ")}.

## Derived tables: ${L["cc-by-4.0"].name}
${L["cc-by-4.0"].url}

${L["cc-by-4.0"].applies_to}

Attribution: ${L["cc-by-4.0"].attribution}

## Code: ${L.mit.name}
${L.mit.applies_to} ${dict.repository}

## Not redistributed here
${dict.tables.filter((t) => !t.redistribute).map((t) => `- ${t.title}: ${t.link} (${L[t.licence].name})`).join("\n")}
${dict.third_party_not_redistributed.map((x) => `- ${x.name} (${x.series}): ${x.link}. ${x.why}`).join("\n")}
`,
);
console.log(`make-downloads: ${summary.filter((s) => s.redistribute).length} tables -> public/downloads`);
