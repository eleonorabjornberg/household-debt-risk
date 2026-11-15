// Copies each research write-up (research/<task>/README.md) into content/research/<slug>.md for the /research pages
// (Eleonora, 2026-11-09: "Make sure our quantitative work is visible there as well"). Hard cut (Eleonora, 2026-11-11,
// "as long as the mcp/api has it"): the site shows only the short version. CUTS below names, per slug, the whole
// sections or paragraphs left out (matched by the start of their line, so the READMEs stay untouched and the register's
// line references stay valid); a closing line points to the full write-up, which the MCP server and the Ask API
// (get_research_writeup) return in full. The kept text is copied as it stands; only relative links change, so none 404
// on the site: a link to another published README goes to its /research page, every other repository path goes to its
// GitHub page on main (the repo's visibility is hers to set).
// The same run writes lib/ask/research.generated.ts: the full README texts for the Ask API, which deploys from atlas/
// alone (the MCP reads research/ directly; research/writeups.json holds the task ids both use).
// Runs before every build and dev start; if research/ isn't reachable it keeps the committed copies.
// --check: exit 1 if a committed copy is stale (no write).
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const out = join(here, "..", "content", "research");
export const GITHUB = "https://github.com/eleonorabjornberg/household-debt-risk";

// slug -> research folder (one README each). Kept in step with content/research.ts (tested).
export const PAGES = {
  a1: "a1_gfc_decomposition", a2: "a2_net_exposure", a3: "a3_pre1952", a4: "a4_breaks", a5: "a5_distribution",
  a7: "a7_causal", a8: "a8_international", b1: "b1_market_pricing", b2: "b2_crt_pricing", b3: "b3_scenarios",
  b4: "b4_policy_scenarios", c1: "c1_nowcast", c3: "c3_accuracy", "joint-holdout": "joint_holdout",
};
// What the site leaves out, per slug: { from, to? } drops the lines from the first line starting with `from` up to (not
// including) the next line starting with `to`, or to the end of the file. Whole sections or paragraphs only; no sentence
// is rewritten. A rule that matches nothing is an error, so a README edit cannot silently defeat the cut.
export const CUTS = {
  a1: [{ from: "**Own-share view.**", to: "**What this changes.**" }, { from: "## Dated policy events" }],
  a2: [{ from: "- Household-apportioned" }],
  a3: [{ from: "## Splice and checks" }],
  a4: [{ from: 'This is "a break', to: "**H2," }, { from: "No one-quarter step" }],
  a5: [{ from: "### Estimate:" }],
  a7: [{ from: "- *Sensitivity", to: "**H2, private-label" }, { from: "## Files and how to rerun" }],
  a8: [{ from: "- **The two measures diverge" }],
  b1: [{ from: "All coefficients and the first-differences" }],
  b2: [{ from: "## 2017–2023: aggregate annual cost" }],
  b3: [{ from: "## Checks", to: "## DFAST preset" }, { from: "- **Mortgages** take", to: "| Preset" },
       { from: "**Reading.**", to: "## 2008–12 replay" }, { from: "- Each quarter's loss", to: "| Preset" },
       { from: "**Limits.**" }],
  b4: [{ from: "**What stays public.**", to: "**Result.**" }, { from: "## Student-loan reform" }],
  c1: [{ from: "- **The bridge is biased downward.**", to: "**What this does not show.**" },
       { from: '## How "what was public on day t" is answered' }],
  c3: [{ from: "**Terms.**", to: "**The holdout**" }, { from: "## 1. Specification registry" }],
  "joint-holdout": [{ from: "## C1: the accounting bridge", to: "## C2: the share forecasts" },
                    { from: "| design | h | candidate", to: "No candidate beats" }],
};

/** The README text with the slug's CUTS removed (blank-line runs collapsed). */
export function cutWriteup(md, slug) {
  const lines = md.split("\n");
  const drop = new Set();
  for (const { from, to } of CUTS[slug] ?? []) {
    const i = lines.findIndex((l) => l.startsWith(from));
    if (i < 0) throw new Error(`sync-research: cut for ${slug} matches nothing: ${from}`);
    let j = lines.length;
    if (to) {
      j = lines.findIndex((l, k) => k > i && l.startsWith(to));
      if (j < 0) throw new Error(`sync-research: cut end for ${slug} matches nothing: ${to}`);
    }
    for (let k = i; k < j; k++) drop.add(k);
  }
  const kept = [];
  lines.forEach((l, k) => {
    if (drop.has(k)) return;
    // a table that lost the blank line above it (a dropped paragraph took it along) gets one back
    if (l.startsWith("|") && kept.length && kept.at(-1).trim() !== "" && !kept.at(-1).startsWith("|")) kept.push("");
    kept.push(l);
  });
  return kept.join("\n").replace(/\n{3,}/g, "\n\n").trimEnd();
}

export const readmeUrl = (dir) => `${GITHUB}/blob/main/research/${dir}/README.md`;
/** What the site page ends with, in place of the cut part. */
export const notice = (dir) =>
  `Full write-up, with every table and check: via the MCP and Ask API (\`get_research_writeup\`) or on GitHub ([README](${readmeUrl(dir)})).\n`;

const BY_PATH = Object.fromEntries(Object.entries(PAGES).map(([s, d]) => [`research/${d}/README.md`, s]));

/** Rewrites one Markdown link target found in research/<dir>/README.md. */
export function rewrite(href, dir) {
  if (/^(https?:|mailto:|#)/.test(href)) return href;
  const [path, frag] = href.split("#");
  const target = normalize(join("research", dir, path)).replace(/\\/g, "/");
  if (target.startsWith("..")) return null;                       // outside the repo: drop the link
  if (BY_PATH[target]) return `/research/${BY_PATH[target]}${frag ? `#${frag}` : ""}`;
  const isDir = path.endsWith("/") || (existsSync(join(root, target)) && !/\.[A-Za-z0-9]+$/.test(target));
  return `${GITHUB}/${isDir ? "tree" : "blob"}/main/${target.replace(/\/$/, "")}${frag ? `#${frag}` : ""}`;
}

/** All [text](href) links outside fenced blocks; a dropped link keeps its text. */
export function rewriteLinks(md, dir) {
  let fenced = false;
  return md.split("\n").map((line) => {
    if (/^\s*```/.test(line)) { fenced = !fenced; return line; }
    if (fenced) return line;
    // link text may itself hold code spans: [`sources.md`](sources.md)
    return line.replace(/\[((?:[^\]`]|`[^`]*`)*)\]\(([^)\s]+)\)/g, (m, text, href) => {
      const h = rewrite(href, dir);
      return h === null ? text : `[${text}](${h})`;
    });
  }).join("\n");
}

/** lib/ask/research.generated.ts: every full README, for the Ask API's get_research_writeup (atlas/ deploys alone). */
export function generatedModule(ids) {
  const items = Object.entries(PAGES).map(([slug, dir]) => {
    const markdown = readFileSync(join(root, "research", dir, "README.md"), "utf8");
    const lines = markdown.split("\n");
    const title = (lines.find((l) => l.startsWith("# ")) ?? `# ${slug}`).slice(2).trim();
    const entry = ids.find((w) => w.slug === slug);
    if (!entry || entry.dir !== dir) throw new Error(`sync-research: ${slug} is not in research/writeups.json`);
    return { slug, ids: entry.ids, title, source_path: `research/${dir}/README.md`,
             line_count: lines.length - (markdown.endsWith("\n") ? 1 : 0), markdown };
  });
  return (
    "// GENERATED by scripts/sync-research.mjs from research/<task>/README.md and research/writeups.json. Do not edit;\n" +
    "// the Ask API's get_research_writeup serves these full texts (the site pages show only the short version).\n" +
    "export type ResearchWriteup = { slug: string; ids: string[]; title: string; source_path: string; line_count: number; markdown: string };\n" +
    `export const RESEARCH_WRITEUPS: ResearchWriteup[] = ${JSON.stringify(items, null, 1)};\n`
  );
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const check = process.argv.includes("--check");
  if (!existsSync(join(root, "research"))) {
    console.log("sync-research: research/ not found, keeping content/research/");
    process.exit(0);
  }
  mkdirSync(out, { recursive: true });
  const stale = [];
  for (const [slug, dir] of Object.entries(PAGES)) {
    const text = rewriteLinks(cutWriteup(readFileSync(join(root, "research", dir, "README.md"), "utf8"), slug), dir) +
      "\n\n" + notice(dir);
    const dst = join(out, `${slug}.md`);
    if (existsSync(dst) && readFileSync(dst, "utf8") === text) continue;
    if (check) stale.push(`content/research/${slug}.md`);
    else writeFileSync(dst, text);
  }
  const gen = join(here, "..", "lib", "ask", "research.generated.ts");
  const body = generatedModule(JSON.parse(readFileSync(join(root, "research", "writeups.json"), "utf8")));
  if (!existsSync(gen) || readFileSync(gen, "utf8") !== body) {
    if (check) stale.push("lib/ask/research.generated.ts");
    else writeFileSync(gen, body);
  }
  if (check) {
    console.log(stale.length ? `sync-research: stale ${stale.join(", ")}` : "sync-research: content/research up to date");
    process.exit(stale.length ? 1 : 0);
  }
  console.log(`sync-research: ${Object.keys(PAGES).length} write-ups in content/research/`);
}
