// Number grounding for Ask Hot Potato: is each number in an answer one the tools returned (at the precision shown)?
// Used by the app's post-answer check (lib/ask/guardrails.ts) and by the E4 scorer (scripts/redteam-score.ts).
// v2 (after E4 P1 labels): reads T/B suffixes, NY Fed billions, signed changes, numbers stored as strings,
// ranges like "56–58%", and Spanish/German decimal commas and scale words.
import type { Row } from "./tools";

const YEARISH = /\b(?:19|20)\d\d[-–]\d\d(?:[-–]\d\d)?\b|\b(1[89]\d\d|20\d\d)(\s*Q[1-4])?\b|\bQ[1-4]\b/gi;
type Cand = { value: number; step: number };
export type AnswerNumber = { raw: string; candidates: Cand[] };

const PCT = /^(%|percent|per cent|percentage points?|pp|pts?|points?|por ciento|prozent)$/i;
const TRN = /^(trillion|tn|t|billones|billionen)$/; // es "billones" and de "Billionen" are 10^12
const BIL = /^(billion|bn|b|mil millones|milliarden|mrd)$/;
const MIL = /^(million|mn|m|millones|millionen)$/;

function normalize(text: string): string {
  return text
    .replace(YEARISH, " ")
    .replace(/(\d)\.(\d{3})\.(\d{3})\b/g, "$1$2$3")             // 2.789.536 (es/de thousands)
    .replace(/(\d),(?=\d{3}(?!\d))/g, "$1")                      // 12,345 and $13,117B -> 12345, 13117B
    .replace(/(\d),(\d{1,2})\b/g, "$1.$2")                       // 2,79 -> 2.79 (decimal comma)
    .replace(/(-?\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)\s*%/g, "$1% – $2%"); // 56–58% -> 56% – 58%
}

/** Numbers in prose with their scale and display precision. Small bare integers (counts, list markers) are skipped. */
export function answerNumbers(text: string): AnswerNumber[] {
  const out: AnswerNumber[] = [];
  const re = /(?<![A-Za-z\d.])(-?\d+(?:\.\d+)?)\s*(%|percentage points?|percent|per cent|por ciento|prozent|pp|pts?|points?|trillion|billion(?:en)?|billones|mil millones|milliarden|million(?:en)?|millones|mrd|tn|bn|mn|T|B|M)?(?![A-Za-z])/gi;
  for (const m of normalize(text).matchAll(re)) {
    const n = Number(m[1]), unit = (m[2] ?? ""), u = unit.toLowerCase(), q = Math.pow(10, -(m[1].split(".")[1] ?? "").length);
    // single letters only count as scale when upper-case right after a number ("$10.77T", "$13,117B")
    const single = unit.length === 1 && unit !== unit.toUpperCase() ? "" : u;
    if (!unit && Number.isInteger(n) && Math.abs(n) <= 20) continue;
    let c: Cand[];
    if (PCT.test(single)) c = [{ value: n / 100, step: q / 100 }, { value: n, step: q }];
    else if (TRN.test(single)) c = [{ value: n * 1e6, step: q * 1e6 }, { value: n * 1e3, step: q * 1e3 }]; // USD mn (Z.1) or bn (NY Fed)
    else if (BIL.test(single)) c = [{ value: n * 1e3, step: q * 1e3 }, { value: n, step: q }];
    else c = [{ value: n, step: q }];
    out.push({ raw: m[0].trim(), candidates: c });
  }
  return out;
}

/** Every finite number in tool outputs, including numeric strings (register values come from CSV as text). */
export function toolNumbers(o: unknown, acc: number[] = []): number[] {
  if (typeof o === "number" && Number.isFinite(o)) acc.push(o);
  else if (typeof o === "string" && /^-?\d+(\.\d+)?(e[-+]?\d+)?$/i.test(o.trim())) acc.push(Number(o));
  else if (Array.isArray(o)) o.forEach((x) => toolNumbers(x, acc));
  else if (o && typeof o === "object") Object.values(o as Row).forEach((x) => toolNumbers(x, acc));
  return acc;
}

/** Grounded if a tool number (sign ignored) rounds to the shown number, or is within 0.5% of it ("about $13.9tn"). */
export function grounded(num: AnswerNumber, pool: number[]): boolean {
  return num.candidates.some((c) => pool.some((v0) => {
    const v = Math.abs(v0), x = Math.abs(c.value);
    return Math.abs(v - x) <= c.step / 2 + 1e-9 || Math.abs(v - x) <= v * 0.005;
  }));
}

/** Numbers in `text` that are neither in the tool outputs nor repeated from the question. */
export function ungrounded(text: string, outputs: unknown, question = ""): string[] {
  const pool = toolNumbers(outputs);
  const asked = toolNumbers(answerNumbers(question).flatMap((n) => n.candidates.map((c) => c.value)));
  return answerNumbers(text).filter((n) => !grounded(n, pool) && !grounded(n, asked)).map((n) => n.raw);
}
