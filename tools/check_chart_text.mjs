// After `next build`: every chart on a site has a text description (PLAN F4).
//   node tools/check_chart_text.mjs --site web|atlas
// Rules, on every prerendered page:
//   - an <svg> is either decorative (aria-hidden="true") or role="img" with a non-empty <title> and <desc>
//   - a <canvas> has a non-empty aria-label
//   - a figure (class "figure") with a chart has a caption or a "Show the data as a table" alternative
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const i = process.argv.indexOf("--site");
const site = i > 0 ? process.argv[i + 1] : null;
if (!site) { console.error("usage: node tools/check_chart_text.mjs --site web|atlas"); process.exit(2); }
const dir = join(process.cwd(), site, ".next", "server", "app");
const pages = readdirSync(dir, { recursive: true }).map(String).filter((f) => f.endsWith(".html") && !f.startsWith("_"));

const errors = [];
let charts = 0;
for (const p of pages) {
  const html = readFileSync(join(dir, p), "utf8").replace(/<script[\s\S]*?<\/script>/g, "");
  for (const m of html.matchAll(/<svg\b([^>]*)>([\s\S]*?)<\/svg>/g)) {
    if (/aria-hidden="true"/.test(m[1])) continue;
    charts++;
    const title = /<title[^>]*>\s*[^<\s][^<]*<\/title>/.test(m[2]);
    const desc = /<desc[^>]*>\s*[^<\s][^<]*<\/desc>/.test(m[2]);
    if (!/role="img"/.test(m[1]) || !title || !desc) errors.push(`${p}: <svg${m[1].slice(0, 60)}...> needs role="img", <title> and <desc>`);
  }
  for (const m of html.matchAll(/<canvas\b([^>]*)>/g)) {
    charts++;
    if (!/aria-label="[^"]+"/.test(m[1])) errors.push(`${p}: <canvas> without aria-label`);
  }
  for (const m of html.matchAll(/<(figure|section)\b[^>]*class="figure[^"]*"[^>]*>([\s\S]*?)<\/\1>/g)) {
    if (!/<svg|<canvas/.test(m[2])) continue;
    if (!/figure__caption[^>]*>\s*[^<\s]/.test(m[2]) && !/Show the data as a table/.test(m[2]))
      errors.push(`${p}: a figure with a chart has neither a caption nor a data table`);
  }
}
if (errors.length) {
  console.error(`F4 ${site}: ${errors.length} chart(s) without a text description\n  ${errors.join("\n  ")}`);
  process.exit(1);
}
console.log(`F4 ${site}: ${charts} chart(s) on ${pages.length} page(s), each with a text description`);
