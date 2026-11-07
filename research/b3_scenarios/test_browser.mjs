// PLAN B3: real-browser parity. The /scenarios page of web/ must reproduce the Python core (engine.py).
//   cd web && npm run build && npm run test:b3-browser        (or: node research/b3_scenarios/test_browser.mjs)
// Starts `next start` on a free local port (no deployment), drives the page in Chromium, and checks:
//   1. every fixed case (fixtures/cases.json, written by engine.py) through the ?case= hook, to 1e-9;
//   2. every preset button against results_*.json (written by engine.py), to 1e-9;
//   3. in-page invariants: public + private = total every quarter; transferred <= cap; zero default -> zero loss;
//   4. the form path: inputs typed into the controls give engine.py's result on the Z.1 exposures (1e-9), and the
//      displayed totals equal engine.py's values rounded the way the page rounds them;
//   5. the Claude-draft banner is visible.
// With SCREENSHOT_DIR set, saves light/dark screenshots at phone and desktop width there (not committed).
import { createRequire } from "node:module";
import { execFileSync, spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { createServer } from "node:net";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = dirname(fileURLToPath(import.meta.url));
// --site web (default) or --site atlas: the page lives in both while web/ stays in the repo (site-visible (b), 2026-11-07)
const siteArg = process.argv.indexOf("--site");
const site = siteArg > 0 ? process.argv[siteArg + 1] : "web";
if (!["web", "atlas"].includes(site)) throw new Error(`unknown site ${site}`);
const web = join(here, "..", "..", site);
const cases = JSON.parse(readFileSync(join(here, "fixtures", "cases.json"), "utf8"));
const presets = {
  ...JSON.parse(readFileSync(join(here, "presets", "dfast2026.json"), "utf8")).presets,
  ...JSON.parse(readFileSync(join(here, "presets", "replay_2008_2012.json"), "utf8")).presets,
};
const results = {
  ...JSON.parse(readFileSync(join(here, "results_dfast2026.json"), "utf8")),
  ...JSON.parse(readFileSync(join(here, "results_replay_2008_2012.json"), "utf8")),
};
const PRESET_BUTTON = {
  dfast2026_proxy: "Fed stress test 2026, hypothetical (proxy)",
  dfast2026_proxy_with_student: "Fed stress test 2026 + federal student loans (weak proxy)",
  replay_2008_2012_proxy: "2008–12 replay of bank write-offs (proxy)",
};

let fail = 0, checks = 0;
const close = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
const check = (ok, what) => { checks++; if (!ok) { fail++; console.error(`FAIL ${what}`); } };

// engine.py on given inputs (the independent reference for the form path)
function python(classes, transfer) {
  const code = [
    "import importlib.util, json, sys",
    `spec = importlib.util.spec_from_file_location('engine', ${JSON.stringify(join(here, "engine.py"))})`,
    "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)",
    `ex = json.load(open(${JSON.stringify(join(here, "exposures.json"))}))['exposures']`,
    "a = json.loads(sys.argv[1])",
    "print(json.dumps(m.run(ex, a['classes'], a['transfer'])))",
  ].join("\n");
  return JSON.parse(execFileSync("python3", ["-I", "-c", code, JSON.stringify({ classes, transfer })], { encoding: "utf8" }));
}

// the page's rounding (web/lib/format.ts usdFromMillions and pct), restated to compare displayed text
const usd = (m, d = 1) => { const a = Math.abs(m), s = m < 0 ? "−" : "";
  return a >= 1e6 ? `${s}$${(a / 1e6).toFixed(d)}T` : a >= 1e3 ? `${s}$${(a / 1e3).toFixed(a >= 1e5 ? 0 : d)}B` : `${s}$${a.toFixed(0)}M`; };
const pct0 = (x) => `${(x * 100).toFixed(0)}%`;

function invariants(name, r, transfer) {
  r.total.forEach((t, i) => check(close(t, r.public[i] + r.private[i]), `${name}: public + private = total, quarter ${i + 1}`));
  if (transfer) check(r.sum.transferred <= transfer.cap_musd * (1 + 1e-12), `${name}: transferred <= cap`);
}

const freePort = () => new Promise((res) => { const s = createServer(); s.listen(0, () => { const p = s.address().port; s.close(() => res(p)); }); });

async function main() {
  if (!existsSync(join(web, ".next", "BUILD_ID"))) throw new Error(`${site}/ is not built: run \`npm run build\` in ${site}/ first`);
  const port = await freePort();
  const server = spawn("npx", ["next", "start", "-p", String(port)], { cwd: web, stdio: "ignore", detached: true });
  const base = `http://127.0.0.1:${port}/scenarios`;
  const browser = await chromium.launch();
  try {
    for (let i = 0; i < 60; i++) { try { if ((await fetch(base)).ok) break; } catch { /* not up yet */ } await new Promise((r) => setTimeout(r, 500)); }
    const page = await browser.newPage();
    const read = async () => JSON.parse(await page.locator('[data-testid="b3-result"]').textContent());

    // 5. banner
    await page.goto(base);
    check(await page.getByTestId("b3-draft-banner").isVisible(), "Claude-draft banner visible");

    // 1. fixed cases
    for (const c of cases) {
      await page.goto(`${base}?case=${encodeURIComponent(c.name)}`);
      await page.getByTestId("b3-case").waitFor();
      const got = (await read()).result;
      for (const k of ["public", "private", "total", "transferred"]) {
        check(got[k].length === c.expected[k].length && got[k].every((v, i) => close(v, c.expected[k][i])), `case "${c.name}": ${k}`);
        check(close(got.sum[k], c.expected.sum[k]), `case "${c.name}": sum.${k}`);
      }
      invariants(`case "${c.name}"`, got, c.transfer);
      if (c.name === "zero default") check(got.sum.total === 0, "zero default gives zero loss");
    }

    // 2. presets
    await page.goto(base);
    for (const [key, label] of Object.entries(PRESET_BUTTON)) {
      await page.getByRole("radio", { name: label, exact: true }).click();
      const got = await read();
      // numeric, not textual: the bundler re-serialises imported JSON, and one replay timing weight comes out one
      // unit in the last place away from the source file (found 2026-11-05); 1e-12 relative allows that and nothing more
      const near = (a, b) => Math.abs(a - b) <= 1e-12 * Math.max(1, Math.abs(b));
      const same = (a, b) => JSON.stringify(Object.keys(a)) === JSON.stringify(Object.keys(b)) && Object.keys(b).every((c) =>
        near(a[c].pd, b[c].pd) && near(a[c].lgd, b[c].lgd) && a[c].timing.length === b[c].timing.length
        && a[c].timing.every((w, i) => near(w, b[c].timing[i])));
      check(same(got.classes, presets[key].classes), `preset ${key}: inputs are the preset's (to 1e-12)`);
      check(close(got.result.sum.public, results[key].public_musd), `preset ${key}: public`);
      check(close(got.result.sum.private, results[key].private_musd), `preset ${key}: private`);
      check(close(got.result.sum.total, results[key].total_musd), `preset ${key}: total`);
      invariants(`preset ${key}`, got.result, null);
    }

    // 4. form path: own scenario typed into the controls, with a capped transfer
    await page.getByRole("radio", { name: "Your own", exact: true }).click();
    const want = { mortgage: [4, 35, 4], consumer_other: [8, 80, 2] };
    for (const c of ["mortgage", "student_federal", "consumer_other"]) {
      const box = page.getByTestId(`b3-on-${c}`);
      if ((await box.isChecked()) !== Boolean(want[c])) await box.click();
      if (!want[c]) continue;
      for (const [f, v] of [["pd", want[c][0]], ["lgd", want[c][1]], ["q", want[c][2]]]) await page.getByTestId(`b3-${f}-${c}`).fill(String(v));
    }
    await page.getByTestId("b3-transfer-on").check();
    await page.getByTestId("b3-share").fill("60");
    await page.getByTestId("b3-cap").fill("40");
    const got = await read();
    const classes = Object.fromEntries(Object.entries(want).map(([c, [pd, lgd, q]]) => [c, { pd: pd / 100, lgd: lgd / 100, timing: Array(q).fill(1 / q) }]));
    const transfer = { share: 0.6, cap_musd: 40000 };
    const py = python(classes, transfer);
    for (const k of ["public", "private", "total", "transferred"]) {
      check(got.result[k].length === py[k].length && got.result[k].every((v, i) => close(v, py[k][i])), `form path: ${k} matches engine.py`);
    }
    invariants("form path", got.result, transfer);
    const text = async (id) => (await page.getByTestId(id).textContent()).trim();
    check(await text("b3-total") === usd(py.sum.total), `form path: displayed total ${await text("b3-total")} vs ${usd(py.sum.total)}`);
    check(await text("b3-public") === usd(py.sum.public), "form path: displayed public");
    check(await text("b3-private") === usd(py.sum.private), "form path: displayed private");
    check(await text("b3-transferred") === usd(py.sum.transferred), "form path: displayed transferred");
    check(await text("b3-share-losses") === pct0(py.sum.public / py.sum.total), "form path: displayed public share of losses");

    // invalid input is refused on the page, not computed
    await page.getByTestId("b3-pd-mortgage").fill("120");
    check(await page.getByTestId("b3-error").isVisible(), "default rate above 100% is refused");

    // screenshots for review
    if (process.env.SCREENSHOT_DIR) {
      mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
      for (const scheme of ["light", "dark"]) {
        for (const [w, h, tag] of [[390, 844, "phone"], [1280, 900, "desktop"]]) {
          const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, deviceScaleFactor: 2 });
          const p = await ctx.newPage();
          await p.goto(base);
          await p.getByRole("radio", { name: PRESET_BUTTON.replay_2008_2012_proxy, exact: true }).click();
          await p.screenshot({ path: join(process.env.SCREENSHOT_DIR, `${site}-scenarios-${tag}-${scheme}.png`), fullPage: true });
          const wide = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
          check(!wide, `no horizontal scroll at ${tag} width (${scheme})`);
          await ctx.close();
        }
      }
    }
  } finally {
    await browser.close();
    try { process.kill(-server.pid); } catch { /* already gone */ }
  }
  console.log(fail ? `${fail} of ${checks} checks failed (${site})` : `ok: ${checks} browser checks match the Python core (${site})`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
