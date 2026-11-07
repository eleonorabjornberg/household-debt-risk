// GENERATED COPY: edit claims/site/claims-core.ts in the repo root, not the copy in a site.
// Matches registered numbers in rendered copy (PLAN F1). See claims/site/README.md.

export type Validation = "PASS" | "FAIL" | "UNVERIFIED" | "ESTIMATE" | "STALE" | "DEFINITION";

export interface Claim {
  id: string;
  claim: string;
  display: string[];
  value: string;
  unit: string;
  period: string;
  locations: string[];
  computation: string;
  series: string[];
  vintage: string;
  validation: Validation | string;
  checkId: string;
  notes: string;
  register: string;
  anchors: string[];
  exact: string[];
}

export interface ClaimsFile {
  site: string;
  generatedFrom: string[];
  claims: Claim[];
}

export type Segment = string | { id: string; text: string };

export const STATUS_TEXT: Record<string, string> = {
  PASS: "Independently recomputed by a validation check, which passes",
  FAIL: "A validation check recomputes it and currently fails",
  UNVERIFIED: "Traced to code or a results file; no independent check yet",
  ESTIMATE: "Estimate, imputation or proxy",
  STALE: "Disagrees with the current source; the copy needs fixing",
  DEFINITION: "Design setting, not a data claim",
};

const norm = (s: string) => s.replace(/\s+/g, " ").trim();
const isDigit = (c: string | undefined) => !!c && /[0-9]/.test(c);
const isWord = (c: string | undefined) => !!c && /[0-9A-Za-z]/.test(c);

/** True if `text.slice(i, i + len)` is a whole number token, not part of a longer one. */
function bounded(text: string, i: number, len: number): boolean {
  const first = text[i];
  const last = text[i + len - 1];
  const before = text[i - 1];
  const after = text[i + len];
  if (isDigit(first) && (isDigit(before) || before === "." || (before === "," && isDigit(text[i - 2])))) return false;
  if (isWord(first) && isWord(before)) return false;
  if (isDigit(last) && (isDigit(after) || ((after === "." || after === ",") && isDigit(text[i + len + 1])))) return false;
  if (isWord(last) && isWord(after)) return false;
  return true;
}

export function makeMatcher(claims: Claim[]) {
  const byId = new Map(claims.map((c) => [c.id, c]));
  const anchors = claims.map((c) => ({ c, a: c.anchors.map(norm), e: c.exact.map(norm) }));

  /** Claims whose cited lines this rendered string comes from. */
  function eligible(text: string, context = ""): Claim[] {
    const hay = norm(`${text} \n ${context}`);
    const whole = norm(text);
    return anchors.filter(({ a, e }) => e.includes(whole) || a.some((x) => hay.includes(x))).map(({ c }) => c);
  }

  /** Splits `text` into plain strings and linked claim segments. */
  function segment(text: string, context = ""): Segment[] {
    const cands = eligible(text, context)
      .flatMap((c) => c.display.map((d) => ({ id: c.id, d })))
      .sort((x, y) => y.d.length - x.d.length);
    if (!cands.length) return [text];
    const taken: { start: number; end: number; id: string }[] = [];
    for (const { id, d } of cands) {
      let from = 0;
      for (;;) {
        const i = text.indexOf(d, from);
        if (i < 0) break;
        from = i + 1;
        const end = i + d.length;
        if (!bounded(text, i, d.length)) continue;
        if (taken.some((t) => i < t.end && end > t.start)) continue;
        taken.push({ start: i, end, id });
      }
    }
    if (!taken.length) return [text];
    taken.sort((x, y) => x.start - y.start);
    const out: Segment[] = [];
    let pos = 0;
    for (const t of taken) {
      if (t.start > pos) out.push(text.slice(pos, t.start));
      out.push({ id: t.id, text: text.slice(t.start, t.end) });
      pos = t.end;
    }
    if (pos < text.length) out.push(text.slice(pos));
    return out;
  }

  return { byId, eligible, segment };
}
