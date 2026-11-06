// The TypeScript tool port must return what the Python MCP tools return (fixtures from
// scripts/ask_parity_fixtures.py, run on the same snapshot, catalog and register).
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { loadEnv } from "./env";
import { TOOLS } from "./tools";

const fixtures = JSON.parse(readFileSync(path.join(__dirname, "parity.fixtures.json"), "utf8")) as
  { tool: string; args: Record<string, unknown>; output: unknown }[];

function same(a: unknown, b: unknown, at = "$"): string | null {
  if (typeof a === "number" && typeof b === "number")
    return Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b)) ? null : `${at}: ${a} != ${b}`;
  if (a === null || b === null || typeof a !== "object" || typeof b !== "object")
    return a === b ? null : `${at}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`;
  if (Array.isArray(a) !== Array.isArray(b)) return `${at}: array vs object`;
  if (Array.isArray(a)) {
    const bb = b as unknown[];
    if (a.length !== bb.length) return `${at}: length ${a.length} != ${bb.length}`;
    for (let i = 0; i < a.length; i++) { const d = same(a[i], bb[i], `${at}[${i}]`); if (d) return d; }
    return null;
  }
  const ka = Object.keys(a).sort(), kb = Object.keys(b as object).sort();
  if (ka.join() !== kb.join()) return `${at}: keys ${ka.join()} != ${kb.join()}`;
  for (const k of ka) { const d = same((a as any)[k], (b as any)[k], `${at}.${k}`); if (d) return d; }
  return null;
}

describe("Ask Hot Potato tools match the Python MCP tools", () => {
  it.each(fixtures.map((f, i) => [i, f.tool, JSON.stringify(f.args), f] as const))("%i %s %s", async (_i, tool, _a, f) => {
    const env = await loadEnv(path.join(__dirname, "..", ".."));
    const got = JSON.parse(JSON.stringify(TOOLS[tool](env, f.args)));
    expect(same(got, f.output)).toBeNull();
  });
});

describe("the parity comparison can fail", () => {
  it("catches a changed number, a changed string and a missing key", async () => {
    const env = await loadEnv(path.join(__dirname, "..", ".."));
    const f = fixtures[0];
    const got = JSON.parse(JSON.stringify(TOOLS[f.tool](env, f.args)));
    const num = JSON.parse(JSON.stringify(got)); num.data[0].public_share += 1e-6;
    const str = JSON.parse(JSON.stringify(got)); str.data[0].quarter = "1999Q1";
    const key = JSON.parse(JSON.stringify(got)); delete key.series_ids;
    for (const bad of [num, str, key]) expect(same(bad, f.output)).not.toBeNull();
  });
});
