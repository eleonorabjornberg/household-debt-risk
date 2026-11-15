// Builds public/downloads/fed-data-desk-plugin.zip from the repository's plugin/ folder (R1, 2026-11-15: Eleonora asked
// for the plugin to be downloadable). The zip holds a local marketplace (fed-data-desk-plugin/.claude-plugin/
// marketplace.json) and the plugin itself, so it installs with `claude plugin marketplace add ./fed-data-desk-plugin`.
// Deterministic: fixed timestamps and sorted entries, so the same plugin/ gives the same bytes.
import { mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { crc32, deflateRawSync } from "node:zlib";

const here = dirname(fileURLToPath(import.meta.url));
const SRC = join(here, "..", "..", "plugin");
const OUT = join(here, "..", "public", "downloads", "fed-data-desk-plugin.zip");
const ROOT = "fed-data-desk-plugin";
const SKIP = new Set(["sync.py", "icon-candidates", "__pycache__", ".DS_Store"]);

function walk(dir) {
  return readdirSync(dir).sort().flatMap((name) => {
    if (SKIP.has(name)) return [];
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

// DOS date/time for 2026-11-15 00:00:00.
const DOS_TIME = 0;
const DOS_DATE = ((2026 - 1980) << 9) | (11 << 5) | 15;

export function buildZip(srcDir = SRC) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const file of walk(srcDir)) {
    const name = Buffer.from(`${ROOT}/${relative(srcDir, file).split("\\").join("/")}`, "utf8");
    const data = readFileSync(file);
    const comp = deflateRawSync(data, { level: 9 });
    const useDeflate = comp.length < data.length;
    const body = useDeflate ? comp : data;
    const crc = crc32(data) >>> 0;
    const method = useDeflate ? 8 : 0;
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x0800, 6);
    local.writeUInt16LE(method, 8); local.writeUInt16LE(DOS_TIME, 10); local.writeUInt16LE(DOS_DATE, 12);
    local.writeUInt32LE(crc, 14); local.writeUInt32LE(body.length, 18); local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(name.length, 26); local.writeUInt16LE(0, 28);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0); central.writeUInt16LE(0x031e, 4); central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8); central.writeUInt16LE(method, 10); central.writeUInt16LE(DOS_TIME, 12);
    central.writeUInt16LE(DOS_DATE, 14); central.writeUInt32LE(crc, 16); central.writeUInt32LE(body.length, 20);
    central.writeUInt32LE(data.length, 24); central.writeUInt16LE(name.length, 28);
    central.writeUInt32LE((0o100644 << 16) >>> 0, 38); central.writeUInt32LE(offset, 42);
    locals.push(local, name, body);
    centrals.push(central, name);
    offset += local.length + name.length + body.length;
  }
  const cd = Buffer.concat(centrals);
  const end = Buffer.alloc(22);
  const n = centrals.length / 2;
  end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(n, 8); end.writeUInt16LE(n, 10);
  end.writeUInt32LE(cd.length, 12); end.writeUInt32LE(offset, 16);
  return { zip: Buffer.concat([...locals, cd, end]), files: n };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const { zip, files } = buildZip();
  mkdirSync(dirname(OUT), { recursive: true });
  writeFileSync(OUT, zip);
  console.log(`plugin-zip: ${files} files, ${(zip.length / 1024).toFixed(0)} KB -> public/downloads/fed-data-desk-plugin.zip`);
}
