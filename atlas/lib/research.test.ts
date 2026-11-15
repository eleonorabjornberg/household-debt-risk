// /research index (2026-11-09): questions and status fragments are verbatim from PLAN.md; slugs match the sync script;
// every write-up copy exists; method lines (Claude draft) carry no figures; the README authorship notes stay out of the copy.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { research } from "../content/research";
import { parseMarkdown } from "./markdown";
import { PAGES, rewrite } from "../scripts/sync-research.mjs";

const plan = path.join(__dirname, "..", "..", "PLAN.md");
const row = (id: string) => {
  const line = readFileSync(plan, "utf8").split("\n").find((l) => l.startsWith(`| ${id} |`));
  if (!line) throw new Error(`no PLAN row ${id}`);
  return line.split("|").map((c) => c.trim());
};

describe("index entries", () => {
  it("covers every task once, A6 blocked with its reason", () => {
    expect(research.map((r) => r.id)).toEqual(["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "B1", "B2", "B3", "B4",
      "C1", "C1b", "C2", "C3", "Joint holdout"]);
    const a6 = research.find((r) => r.id === "A6")!;
    expect(a6.slug).toBeNull();
    expect(a6.blocked).toBeTruthy();
  });
  it.skipIf(!existsSync(plan))("quotes PLAN.md verbatim", () => {
    for (const r of research) {
      if (/^[ABC]\d$/.test(r.id)) expect(row(r.id)[2], r.id).toBe(r.question);
      const cell = row(r.statusRow ?? r.id).at(-2)!;
      for (const s of r.status) expect(cell, `${r.id}: ${s}`).toContain(s);
      if (r.blocked) expect(cell).toContain(r.blocked);
    }
  });
  it("has no figures in the Claude-written method lines", () => {
    for (const r of research) expect(r.method, r.id).not.toMatch(/\d[\d,.]*\s?(%|pp|bps?)|\$\d|\d\.\d/);
  });
  it("uses the sync script's slugs, and each has its copy", () => {
    const slugs = new Set(research.map((r) => r.slug).filter(Boolean));
    expect([...slugs].sort()).toEqual(Object.keys(PAGES).sort());
    for (const s of slugs) expect(existsSync(path.join(__dirname, "..", "content", "research", `${s}.md`)), s!).toBe(true);
  });
});

describe("write-up copies", () => {
  // The README authorship notes came off on 2026-11-15 (Eleonora, review round 47 r1-research-notes: "remove them
  // everywhere"); the copies must not bring one back.
  it("carry no Claude-draft authorship note", () => {
    for (const s of Object.keys(PAGES)) {
      const md = readFileSync(path.join(__dirname, "..", "content", "research", `${s}.md`), "utf8");
      expect(md, s).not.toMatch(/Claude draft, not the author's text|^> \*\*Claude draft/m);
      const blocks = parseMarkdown(md);
      expect(blocks.some((b) => b.t === "quote" || (b.t === "para")), s).toBe(true);
    }
  });
  it("have no relative links left", () => {
    for (const s of Object.keys(PAGES)) {
      const md = readFileSync(path.join(__dirname, "..", "content", "research", `${s}.md`), "utf8");
      const bad = [...md.matchAll(/\]\(([^)\s]+)\)/g)].map((m) => m[1]).filter((h) => !/^(https?:|\/|#)/.test(h));
      expect(bad, s).toEqual([]);
    }
  });
  it("rewrites links: other READMEs to /research, files to GitHub, outside the repo dropped", () => {
    expect(rewrite("../c1_nowcast/README.md#x", "c3_accuracy")).toBe("/research/c1#x");
    expect(rewrite("METHOD.md", "b2_crt_pricing")).toBe(
      "https://github.com/eleonorabjornberg/household-debt-risk/blob/main/research/b2_crt_pricing/METHOD.md");
    expect(rewrite("../../docs/decisions/breaks.md", "a4_breaks")).toBe(
      "https://github.com/eleonorabjornberg/household-debt-risk/blob/main/docs/decisions/breaks.md");
    expect(rewrite("../../../etc/passwd", "a1_gfc_decomposition")).toBeNull();
    expect(rewrite("https://www.fhfa.gov/x", "b2_crt_pricing")).toBe("https://www.fhfa.gov/x");
  });
});
