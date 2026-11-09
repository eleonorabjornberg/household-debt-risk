// A small Markdown reader for /findings (docket 48 site-findings (b)): renders analysis/findings.md as it stands.
// Covers what that file uses: #/## headings, paragraphs, **bold**, *italic*, `code`, [text](url) links,
// ordered and unordered lists (nested by indent) and pipe tables. Added for /research (2026-11-09): fenced code
// blocks and "> " blockquotes, which the research write-ups use (the Claude-draft banner is a blockquote). No raw HTML is ever emitted, so the
// text cannot inject markup; anything unrecognised renders as plain text.

export type Inline =
  | { t: "text"; v: string }
  | { t: "strong"; c: Inline[] }
  | { t: "em"; c: Inline[] }
  | { t: "code"; v: string }
  | { t: "link"; href: string; c: Inline[] };

export interface ListItem { body: Inline[]; children: ListBlock[] }
export interface ListBlock { t: "list"; ordered: boolean; start: number; items: ListItem[] }
export type Block =
  | { t: "heading"; level: number; id: string; c: Inline[] }
  | { t: "para"; c: Inline[] }
  | ListBlock
  | { t: "table"; head: Inline[][]; rows: Inline[][][] }
  | { t: "fence"; lang: string; text: string }
  | { t: "quote"; blocks: Block[] };

const LIST_RE = /^(\s*)([-*]|\d+\.)\s+(.*)$/;
const isTableLine = (l: string) => l.trim().startsWith("|");
const isFence = (l: string) => /^\s*```/.test(l);
const isQuote = (l: string) => /^\s*>/.test(l);
const isSep = (l: string) => /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$/.test(l);

export function slug(s: string): string {
  return s.toLowerCase().replace(/[`*]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

export function plain(c: Inline[]): string {
  return c.map((x) => ("v" in x ? x.v : plain(x.c))).join("");
}

export function parseInline(s: string): Inline[] {
  const out: Inline[] = [];
  let buf = "";
  const flush = () => { if (buf) { out.push({ t: "text", v: buf }); buf = ""; } };
  let i = 0;
  while (i < s.length) {
    const rest = s.slice(i);
    let m: RegExpMatchArray | null;
    if (rest[0] === "`" && (m = rest.match(/^`([^`]+)`/))) {
      flush(); out.push({ t: "code", v: m[1] }); i += m[0].length; continue;
    }
    if (rest.startsWith("**") && (m = rest.match(/^\*\*(.+?)\*\*/))) {
      flush(); out.push({ t: "strong", c: parseInline(m[1]) }); i += m[0].length; continue;
    }
    if (rest[0] === "*" && (m = rest.match(/^\*([^*\s][^*]*?)\*(?!\*)/))) {
      flush(); out.push({ t: "em", c: parseInline(m[1]) }); i += m[0].length; continue;
    }
    if (rest[0] === "[" && (m = rest.match(/^\[([^\]]+)\]\(([^)\s]+)\)/))) {
      flush(); out.push({ t: "link", href: m[2], c: parseInline(m[1]) }); i += m[0].length; continue;
    }
    buf += s[i];
    i += 1;
  }
  flush();
  return out;
}

function splitRow(l: string): string[] {
  let t = l.trim();
  if (t.startsWith("|")) t = t.slice(1);
  if (t.endsWith("|")) t = t.slice(0, -1);
  return t.split("|").map((c) => c.trim());
}

function parseList(lines: string[]): ListBlock {
  // lines: consecutive list lines (and their continuation lines), first line at the list's own indent
  const indentOf = (l: string) => (l.match(/^(\s*)/)?.[1].length ?? 0);
  const base = indentOf(lines[0]);
  const first = lines[0].match(LIST_RE)!;
  const ordered = /\d/.test(first[2]);
  const list: ListBlock = { t: "list", ordered, start: ordered ? parseInt(first[2], 10) : 1, items: [] };
  let cur: { text: string; sub: string[] } | null = null;
  const done = () => {
    if (!cur) return;
    const children: ListBlock[] = [];
    let j = 0;
    while (j < cur.sub.length) {
      const k0 = j;
      j += 1;
      while (j < cur.sub.length && !(indentOf(cur.sub[j]) === indentOf(cur.sub[k0]) && LIST_RE.test(cur.sub[j]) &&
             /\d/.test(cur.sub[j].match(LIST_RE)![2]) !== /\d/.test(cur.sub[k0].match(LIST_RE)![2]))) j += 1;
      children.push(parseList(cur.sub.slice(k0, j)));
    }
    list.items.push({ body: parseInline(cur.text), children });
  };
  for (const l of lines) {
    const m = l.match(LIST_RE);
    if (m && indentOf(l) === base) { done(); cur = { text: m[3], sub: [] }; }
    else if (m && cur) cur.sub.push(l);
    else if (cur && cur.sub.length) cur.sub[cur.sub.length - 1] += " " + l.trim();
    else if (cur) cur.text += " " + l.trim();
  }
  done();
  return list;
}

export function parseMarkdown(src: string): Block[] {
  const lines = src.replace(/\r\n?/g, "\n").split("\n");
  const blocks: Block[] = [];
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) { i += 1; continue; }
    if (isFence(l)) {
      const lang = l.trim().slice(3).trim();
      const body: string[] = [];
      i += 1;
      while (i < lines.length && !isFence(lines[i])) { body.push(lines[i]); i += 1; }
      i += 1;                                              // closing fence (or end of file)
      blocks.push({ t: "fence", lang, text: body.join("\n") });
      continue;
    }
    if (isQuote(l)) {
      const inner: string[] = [];
      while (i < lines.length && isQuote(lines[i])) { inner.push(lines[i].replace(/^\s*>\s?/, "")); i += 1; }
      blocks.push({ t: "quote", blocks: parseMarkdown(inner.join("\n")) });
      continue;
    }
    const h = l.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      const c = parseInline(h[2].trim());
      blocks.push({ t: "heading", level: h[1].length, id: slug(plain(c)), c });
      i += 1;
      continue;
    }
    if (isTableLine(l) && i + 1 < lines.length && isSep(lines[i + 1])) {
      const head = splitRow(l).map(parseInline);
      const rows: Inline[][][] = [];
      i += 2;
      while (i < lines.length && isTableLine(lines[i])) { rows.push(splitRow(lines[i]).map(parseInline)); i += 1; }
      blocks.push({ t: "table", head, rows });
      continue;
    }
    if (LIST_RE.test(l)) {
      const start = i;
      i += 1;
      while (i < lines.length && lines[i].trim() && !/^#{1,6}\s/.test(lines[i]) && !isTableLine(lines[i]) &&
             !isFence(lines[i]) && !isQuote(lines[i]) &&
             (LIST_RE.test(lines[i]) || /^\s+\S/.test(lines[i]))) i += 1;
      blocks.push(parseList(lines.slice(start, i)));
      continue;
    }
    const start = i;
    i += 1;
    while (i < lines.length && lines[i].trim() && !/^#{1,6}\s/.test(lines[i]) && !LIST_RE.test(lines[i]) &&
           !isFence(lines[i]) && !isQuote(lines[i]) &&
           !(isTableLine(lines[i]) && i + 1 < lines.length && isSep(lines[i + 1]))) i += 1;
    blocks.push({ t: "para", c: parseInline(lines.slice(start, i).map((x) => x.trim()).join(" ")) });
  }
  return blocks;
}
