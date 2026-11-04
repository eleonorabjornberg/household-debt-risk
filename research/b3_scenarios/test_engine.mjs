// Node test: the browser engine matches the Python core on every fixed case (fixtures/cases.json).
//   node research/b3_scenarios/test_engine.mjs
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { run } from "./engine.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const cases = JSON.parse(readFileSync(join(here, "fixtures", "cases.json"), "utf8"));
let fail = 0;
const close = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
for (const c of cases) {
  const got = run(c.exposures, c.classes, c.transfer);
  for (const k of ["public", "private", "total", "transferred"]) {
    const g = got[k], e = c.expected[k];
    if (g.length !== e.length || g.some((x, i) => !close(x, e[i]))) { console.error(`FAIL ${c.name} ${k}`, g, e); fail++; }
    if (!close(got.sum[k], c.expected.sum[k])) { console.error(`FAIL ${c.name} sum.${k}`); fail++; }
  }
}
let refused = 0;
for (const bad of [{ mortgage: { pd: 1.2, lgd: 0.3 } }, { mortgage: { pd: 0.1, lgd: 0.3, timing: [0.5, 0.4] } }]) {
  try { run(cases[0].exposures, bad); } catch { refused++; }
}
if (refused !== 2) { console.error("FAIL invalid input accepted"); fail++; }
console.log(fail ? `${fail} failures` : `ok: ${cases.length} cases match the Python core`);
process.exit(fail ? 1 : 0);
