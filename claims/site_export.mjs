// Exports the claims register for one site (PLAN F1).
//
//   node claims/site_export.mjs --site web --out web/lib/claims.json
//
// Reads claims/register.csv and every claims/tracks/*.csv, keeps the rows with at least one location
// under `<site>/`, and writes them as JSON for the site's source popovers and /sources page.
//
// Each claim carries `anchors`: literal text fragments taken from the source lines its `locations`
// point at (string literals, with `${...}` and `{token}` placeholders removed). The site links a
// number only when its display spelling appears in a rendered string that also contains one of these
// fragments, so "30%" is linked where the register says it is printed and nowhere else. A location
// A short literal that is exactly a display spelling (a stat tile's value) is kept in `exact`: a
// rendered string equal to it is linked. A location
// whose line has no usable literal (a number computed in a component) gets no anchor; components
// wrap those numbers explicitly with the claim id.
//
// No dependencies, so each site's prebuild can import it from the repo checkout.
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
export const MIN_ANCHOR = 12; // shorter fragments ("3.2%", "pts") are too generic to anchor on

/** RFC 4180 CSV parser: quoted fields, doubled quotes, newlines inside quotes. */
export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') q = false;
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.length > 1 || row[0] !== "") rows.push(row);
      row = [];
    } else field += c;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const [header, ...body] = rows;
  return body.map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])));
}

export function registerFiles(root = ROOT) {
  const files = [join(root, "claims", "register.csv")];
  const tracks = join(root, "claims", "tracks");
  if (existsSync(tracks)) {
    for (const f of readdirSync(tracks).sort()) if (f.endsWith(".csv")) files.push(join(tracks, f));
  }
  return files.filter(existsSync);
}

/** Literal fragments of one source line that a rendered string will contain verbatim. */
export function anchorsFromLine(line) {
  const lits = [];
  const re = /"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`|'((?:[^'\\]|\\.)*)'/g;
  let m;
  while ((m = re.exec(line))) lits.push(m[1] ?? m[2] ?? m[3]);
  // A line inside a multi-line template literal or JSX text has no quotes of its own.
  if (!lits.length) {
    const t = line.trim();
    if (!/^(\/\/|\/\*|\*)/.test(t)) lits.push(t.replace(/<[^>]+>/g, " "));
  }
  const out = [];
  for (const lit of lits) {
    const s = lit.replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16))).replace(/\\(.)/g, "$1");
    for (const piece of s.split(/\$\{[^}]*\}|\{[A-Za-z][A-Za-z0-9_]*\}|\{[^}]*\}/)) {
      const p = piece.trim();
      if (p.length >= MIN_ANCHOR) out.push(p);
    }
  }
  return out;
}

export function exportSite(site, root = ROOT) {
  const prefix = `${site}/`;
  const lineCache = new Map();
  const lineOf = (file, n) => {
    if (!lineCache.has(file)) {
      const p = join(root, file);
      lineCache.set(file, existsSync(p) ? readFileSync(p, "utf8").split("\n") : []);
    }
    return lineCache.get(file)[n - 1] ?? "";
  };
  const claims = [];
  for (const file of registerFiles(root)) {
    for (const r of parseCsv(readFileSync(file, "utf8"))) {
      const locations = r.locations.split(";").map((s) => s.trim()).filter(Boolean);
      const mine = locations.filter((l) => l.startsWith(prefix));
      if (!mine.length) continue;
      const display = r.display.split(" | ").map((s) => s.trim()).filter(Boolean);
      const anchors = new Set();
      const exact = new Set();
      for (const loc of mine) {
        const [f, n] = loc.split(":");
        const line = lineOf(f, Number(n));
        for (const a of anchorsFromLine(line)) anchors.add(a);
        // A short literal that is exactly a display spelling (`stat: "p ≈ 0.30"`) is rendered on its own.
        for (const d of display) if (line.includes(`"${d}"`)) exact.add(d);
      }
      claims.push({
        id: r.claim_id,
        claim: r.claim,
        display,
        value: r.value,
        unit: r.unit,
        period: r.period,
        locations: mine,
        computation: r.computation,
        series: r.series_ids.split(/\s+/).filter(Boolean),
        vintage: r.vintage,
        validation: r.validation,
        checkId: r.check_id,
        notes: r.notes,
        register: relative(root, file),
        anchors: [...anchors],
        exact: [...exact],
      });
    }
  }
  claims.sort((a, b) => a.id.localeCompare(b.id));
  return { site, generatedFrom: registerFiles(root).map((f) => relative(root, f)), claims };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : undefined; };
  const site = arg("--site");
  const out = arg("--out");
  if (!site || !out) { console.error("usage: node claims/site_export.mjs --site web|atlas --out <file> [--check]"); process.exit(2); }
  const json = JSON.stringify(exportSite(site), null, 1) + "\n";
  if (process.argv.includes("--check")) {
    const cur = existsSync(out) ? readFileSync(out, "utf8") : "";
    if (cur !== json) { console.error(`${out} is out of date with the register; run: node claims/site_export.mjs --site ${site} --out ${out}`); process.exit(1); }
    console.log(`${out} up to date`);
  } else {
    writeFileSync(out, json);
    console.log(`site_export: ${JSON.parse(json).claims.length} claims for ${site} -> ${out}`);
  }
}
