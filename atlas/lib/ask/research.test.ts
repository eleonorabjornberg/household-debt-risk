// get_research_writeup / list_research (Eleonora, 2026-11-11: the research pages may be cut hard "as long as the
// mcp/api has it"). The Ask API serves the full README texts from lib/ask/research.generated.ts; the site pages show
// only the short version (scripts/sync-research.mjs CUTS). Parity with the Python tools is in parity.test.ts.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { loadEnv } from "./env";
import { RESEARCH_WRITEUPS } from "./research.generated";
import { TOOLS } from "./tools";
import { TOOL_DEFS } from "./agent";
import { CUTS, PAGES, cutWriteup, generatedModule } from "../../scripts/sync-research.mjs";

const root = path.join(__dirname, "..", "..", "..");
const haveRepo = existsSync(path.join(root, "research", "writeups.json"));
const env = () => loadEnv(path.join(__dirname, "..", ".."));

describe("get_research_writeup", () => {
  it("returns the full README by task id, slug or folder, in the usual envelope", async () => {
    const e = await env();
    for (const [key, slug] of [["A1", "a1"], ["a1", "a1"], ["c2", "joint-holdout"], ["Joint holdout", "joint-holdout"],
                               ["b4_policy_scenarios", "b4"], ["C3", "c3"]]) {
      const r = TOOLS.get_research_writeup(e, { task: key });
      expect(r.ok, key).toBe(true);
      expect(r.data.slug, key).toBe(slug);
      expect(r.data.markdown, key).toBe(RESEARCH_WRITEUPS.find((w) => w.slug === slug)!.markdown);
      expect(r.data.markdown).toMatch(/^# .*\n\n> \*\*Claude draft/);
      expect(r.data.site_url).toBe(`/research/${slug}`);
      expect(r.data.github_url).toMatch(new RegExp(`/blob/main/${r.data.source_path}$`));
      for (const k of ["units", "series_ids", "vintage", "limits", "limits_url", "data"]) expect(r, k).toHaveProperty(k);
      expect(r.limits.some((l: string) => /Claude draft/.test(l))).toBe(true);
    }
  });
  it("refuses unknown tasks (A6 has no write-up) and points to list_research", async () => {
    const e = await env();
    for (const t of ["", "A6", "zz9", undefined]) {
      const r = TOOLS.get_research_writeup(e, { task: t });
      expect(r.refused).toBe(true);
      expect(r.reason_code).toBe("unknown_writeup");
      expect(r.nearest_answerable[0].tool).toBe("list_research");
      expect(JSON.stringify(r)).not.toContain("markdown");
    }
  });
  it("list_research lists the 14 write-ups with their task ids and no text", async () => {
    const r = TOOLS.list_research(await env(), {});
    expect(r.ok).toBe(true);
    expect(r.data).toHaveLength(14);
    expect(r.data.flatMap((w: any) => w.ids)).toEqual(expect.arrayContaining(["A1", "C1b", "C2", "Joint holdout", "C3"]));
    expect(r.data.every((w: any) => !("markdown" in w) && w.line_count > 20)).toBe(true);
  });
  it("is offered to the model as a tool", () => {
    const names = TOOL_DEFS.map((t) => t.name);
    expect(names).toEqual(expect.arrayContaining(["list_research", "get_research_writeup"]));
    for (const n of names) expect(TOOLS[n], n).toBeTypeOf("function");
  });
});

describe.skipIf(!haveRepo)("generated texts and the site cut", () => {
  it("research.generated.ts is current and holds each README unchanged", () => {
    const ids = JSON.parse(readFileSync(path.join(root, "research", "writeups.json"), "utf8"));
    expect(readFileSync(path.join(__dirname, "research.generated.ts"), "utf8")).toBe(generatedModule(ids));
    for (const [slug, dir] of Object.entries(PAGES))
      expect(RESEARCH_WRITEUPS.find((w) => w.slug === slug)!.markdown, slug)
        .toBe(readFileSync(path.join(root, "research", dir as string, "README.md"), "utf8"));
  });
  it("cuts every page to a short version that keeps the draft banner and points to the full write-up", () => {
    for (const [slug, dir] of Object.entries(PAGES)) {
      const full = readFileSync(path.join(root, "research", dir as string, "README.md"), "utf8");
      const site = readFileSync(path.join(__dirname, "..", "..", "content", "research", `${slug}.md`), "utf8");
      expect(CUTS[slug as keyof typeof CUTS], slug).toBeTruthy();
      expect(site.split("\n").length, slug).toBeLessThan(full.split("\n").length);
      expect(site, slug).toMatch(/Claude draft/);
      expect(site, slug).toContain("get_research_writeup");
      expect(site, slug).toContain(`/blob/main/research/${dir}/README.md`);
      // only whole lines are cut: every kept line (the closing notice aside) is a line of the README
      const fullLines = new Set(full.split("\n").map((l) => l.replace(/\]\([^)]*\)/g, "](")));
      const kept = site.split("\n").slice(0, -2).filter((l) => l.trim());
      for (const l of kept) expect(fullLines.has(l.replace(/\]\([^)]*\)/g, "](")), `${slug}: ${l.slice(0, 60)}`).toBe(true);
    }
  });
  it("fails loudly when a cut no longer matches", () => {
    expect(() => cutWriteup("# T\n\ntext\n", "a1")).toThrow(/matches nothing/);
  });
});
