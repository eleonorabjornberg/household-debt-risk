import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { type Block, type ListBlock, isNumericCell, parseInline, parseMarkdown, plain } from "./markdown";

const COPY = path.join(__dirname, "..", "content", "findings.md");
const SOURCE = path.join(__dirname, "..", "..", "analysis", "findings.md");

function words(blocks: Block[]): string[] {
  const out: string[] = [];
  const list = (b: ListBlock) => b.items.forEach((it) => { out.push(plain(it.body)); it.children.forEach(list); });
  const walk = (bs: Block[]): void => bs.forEach((b) => {
    if (b.t === "quote") walk(b.blocks);
    else if (b.t === "heading" || b.t === "para") out.push(plain(b.c));
    else if (b.t === "list") list(b);
    else if (b.t === "table") { b.head.forEach((c) => out.push(plain(c))); b.rows.forEach((r) => r.forEach((c) => out.push(plain(c)))); }
  });
  walk(blocks);
  return out.join(" ").split(/\s+/).filter(Boolean);
}

/** The source's words with Markdown syntax removed: what a reader should see, in order. */
function sourceWords(src: string): string[] {
  return src.split("\n")
    .filter((l) => !/^\s*\|?\s*:?-{3,}/.test(l))
    .map((l) => l.replace(/^\s*>\s?/, "").replace(/^\s*(#{1,6}|[-*]|\d+\.)\s+/, "").replace(/\|/g, " ").replace(/\*\*|`/g, "").replace(/\*([^*\s][^*]*?)\*/g, "$1"))
    .join(" ").split(/\s+/).filter(Boolean);
}

describe("parseInline", () => {
  it("reads bold, italic, code and links, and leaves the rest as text", () => {
    const c = parseInline("a **b** *c* `d` [e](https://x.org) 3 × 4");
    expect(c.map((x) => x.t)).toEqual(["text", "strong", "text", "em", "text", "code", "text", "link", "text"]);
    expect(plain(c)).toBe("a b c d e 3 × 4");
  });
  it("does not treat a lone asterisk as emphasis", () => {
    expect(plain(parseInline("2 * 3 and * x"))).toBe("2 * 3 and * x");
  });
});

describe("parseMarkdown", () => {
  it("nests indented list items and keeps the ordered list's start", () => {
    const b = parseMarkdown("5. **Collateral proxies.**\n   - Home\n   - Vehicle\n6. Next");
    expect(b).toHaveLength(1);
    const l = b[0] as ListBlock;
    expect(l.ordered && l.start).toBe(5);
    expect(l.items).toHaveLength(2);
    expect(l.items[0].children[0].items.map((i) => plain(i.body))).toEqual(["Home", "Vehicle"]);
  });
  it("reads a pipe table", () => {
    const b = parseMarkdown("| A | B |\n|---|---|\n| 1 | **2** |\n");
    expect(b[0].t).toBe("table");
    if (b[0].t === "table") expect(b[0].rows[0].map(plain)).toEqual(["1", "2"]);
  });
});

describe("analysis/findings.md on /dashboard", () => {
  const src = readFileSync(COPY, "utf8");
  const blocks = parseMarkdown(src);
  it("is an exact copy of analysis/findings.md (run scripts/sync-findings.mjs)", () => {
    if (existsSync(SOURCE)) expect(src).toBe(readFileSync(SOURCE, "utf8"));
  });
  it("renders every word and number of the source, in order, with no Markdown left over", () => {
    expect(words(blocks)).toEqual(sourceWords(src));
    expect(words(blocks).join(" ")).not.toMatch(/\*\*|`/);
  });
  it("keeps every heading and table", () => {
    expect(blocks.filter((b) => b.t === "heading")).toHaveLength(src.split("\n").filter((l) => /^#{1,6}\s/.test(l)).length);
    expect(blocks.filter((b) => b.t === "table")).toHaveLength(src.split("\n").filter((l) => /^\|\s*-{3,}/.test(l)).length);
  });
});


describe("fences and blockquotes (/research, 2026-11-09)", () => {
  it("keeps a fenced block verbatim, markup and all", () => {
    const b = parseMarkdown("text\n```bash\nuv run x.py   # **not bold** [not](link)\n\nsecond\n```\nafter");
    expect(b.map((x) => x.t)).toEqual(["para", "fence", "para"]);
    expect(b[1]).toEqual({ t: "fence", lang: "bash", text: "uv run x.py   # **not bold** [not](link)\n\nsecond" });
  });
  it("parses a blockquote's inside as blocks", () => {
    const b = parseMarkdown("> **Claude draft, not the author's text.** Line one\n> line two\n\nnext");
    expect(b[0].t).toBe("quote");
    const q = b[0] as Extract<Block, { t: "quote" }>;
    expect(q.blocks).toHaveLength(1);
    expect(plain((q.blocks[0] as Extract<Block, { t: "para" }>).c)).toBe("Claude draft, not the author's text. Line one line two");
    expect(b[1].t).toBe("para");
  });
  it("ends a paragraph or list at a fence or quote", () => {
    expect(parseMarkdown("para\n> quote").map((x) => x.t)).toEqual(["para", "quote"]);
    expect(parseMarkdown("- item\n```\ncode\n```").map((x) => x.t)).toEqual(["list", "fence"]);
  });
  it("right-aligns numeric table columns and honours explicit alignment", () => {
    const b = parseMarkdown("| Peak | Share | Change | Note |\n|---|---|:---:|---|\n| 1980Q1 | 14.3% | +9.3 pp | x |\n| 2019Q4 | **55.2%** | — | 32.8% → 40.2% |");
    if (b[0].t !== "table") throw new Error("not a table");
    expect(b[0].align).toEqual(["left", "right", "center", "left"]);
    expect(isNumericCell("32.8% → 40.2%")).toBe(true);
    expect(isNumericCell("-0.3")).toBe(true);
    expect(isNumericCell("Private-label boom")).toBe(false);
    expect(isNumericCell("1999Q4–2007Q4")).toBe(false);
  });
});
