// Copies each research write-up (research/<task>/README.md) into content/research/<slug>.md for the /research pages
// (Eleonora, 2026-11-09: "Make sure our quantitative work is visible there as well"). The text is copied as it
// stands; only relative links change, so none 404 on the site: a link to another published README goes to its
// /research page, every other repository path goes to its GitHub page on main (the repo's visibility is hers to set).
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

if (import.meta.url === `file://${process.argv[1]}`) {
  const check = process.argv.includes("--check");
  if (!existsSync(join(root, "research"))) {
    console.log("sync-research: research/ not found, keeping content/research/");
    process.exit(0);
  }
  mkdirSync(out, { recursive: true });
  const stale = [];
  for (const [slug, dir] of Object.entries(PAGES)) {
    const text = rewriteLinks(readFileSync(join(root, "research", dir, "README.md"), "utf8"), dir);
    const dst = join(out, `${slug}.md`);
    if (existsSync(dst) && readFileSync(dst, "utf8") === text) continue;
    if (check) stale.push(`content/research/${slug}.md`);
    else writeFileSync(dst, text);
  }
  if (check) {
    console.log(stale.length ? `sync-research: stale ${stale.join(", ")}` : "sync-research: content/research up to date");
    process.exit(stale.length ? 1 : 0);
  }
  console.log(`sync-research: ${Object.keys(PAGES).length} write-ups in content/research/`);
}
