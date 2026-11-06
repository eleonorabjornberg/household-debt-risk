// Offline tests for the D6 paid build-test harness (scripts/ask-buildtest.ts). No API calls.
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { buildQuestions, d6SpendSoFar, roughCheck, run, RUN_BUDGET_USD, spendRow } from "../../scripts/ask-buildtest";

const ROOT = path.join(__dirname, "..", "..", "..");
const usage = (k: number) => ({ input_tokens: 100 * k, output_tokens: 100 * k, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 });
const client = (k: number) => ({ messages: { create: async (b: any) => (b.messages.length === 1
  ? { usage: usage(k), stop_reason: "tool_use", content: [{ type: "tool_use", id: "t", name: "public_share", input: {} }] }
  : { usage: usage(k), stop_reason: "end_turn", content: [{ type: "text", text: "It was 56.4% in 2026Q2." }] }) } });

describe("D6 build-test harness", () => {
  it("finds her d6-spend row in PLAN.md and nothing else", () => {
    const plan = readFileSync(path.join(ROOT, "PLAN.md"), "utf8");
    const row = spendRow(plan);
    expect(row).toMatch(/d6-spend, chosen 04:57 UTC/);
    expect(spendRow("| 2026-11-06 | D6 model (d6-model): **Sonnet** | Eleonora |")).toBeNull();
    expect(spendRow("| 2026-11-06 | D6 spend (d6-spend): **cap $20** | Coordinator |")).toBeNull();
  });

  it("uses 30 questions, none held out", () => {
    const qs = buildQuestions();
    const gold = JSON.parse(readFileSync(path.join(ROOT, "evals", "e1_sql_benchmark", "gold.json"), "utf8")).questions;
    const held = new Set(gold.filter((q: any) => q.holdout).map((q: any) => q.id));
    expect(qs).toHaveLength(30);
    expect(qs.filter((q) => held.has(q.id))).toHaveLength(0);
    expect(qs.filter((q) => q.gold.gold === "refuse")).toHaveLength(10);
  });

  it("ledger counts live runs only", () => {
    const d = mkdtempSync(path.join(tmpdir(), "d6-"));
    for (const [n, c] of [["run-a", 1.25], ["run-fake-x", 9]] as const) {
      mkdirSync(path.join(d, n));
      writeFileSync(path.join(d, n, "calls.jsonl"), JSON.stringify({ cost_usd: c }) + "\n" + JSON.stringify({ checkpoint: 1 }) + "\n");
    }
    expect(d6SpendSoFar(d)).toBeCloseTo(1.25);
  });

  it("completes a cheap run, then refuses to overwrite it", async () => {
    const out = path.join(mkdtempSync(path.join(tmpdir(), "d6-")), "run");
    const s = await run(client(1), out, 0, null);
    expect(s.stop).toBeNull();
    expect(s.done).toBe(30);
    // every logged call row carries served_model (here the fake client sends none: recorded as null, not omitted)
    const rows = readFileSync(path.join(out, "calls.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l)).filter((r) => r.qid);
    for (const r of rows) for (const u of r.usage) expect(u).toHaveProperty("served_model");
    await expect(run(client(1), out, 0, null)).rejects.toThrow(/already holds a run/);
  });

  it("stops at the 10% checkpoint when the projection exceeds the run budget", async () => {
    const out = path.join(mkdtempSync(path.join(tmpdir(), "d6-")), "run");
    const s = await run(client(60), out, 0, null); // about $0.07-0.13 per question -> projection above $2
    expect(s.stop).toMatch(/^checkpoint/);
    expect(s.spent_usd).toBeLessThan(RUN_BUDGET_USD);
  });

  it("the pre-call guard stops before the $20 D6 cap could be reached", async () => {
    const out = path.join(mkdtempSync(path.join(tmpdir(), "d6-")), "run");
    const s = await run(client(1), out, 19.97, null);
    expect(s.stop).toMatch(/\$20 cap/);
    expect(s.d6_spend_total_usd).toBeLessThan(20);
  });

  it("rough check: finds a gold share in prose and accepts refusals", () => {
    expect(roughCheck("Public holders held 56.4% in 2026Q2.", false, { gold: 0.5638, unit: "share", tolerance: 0.0005 })).toBe(true);
    expect(roughCheck("Public holders held 50.1% in 2026Q2.", false, { gold: 0.5638, unit: "share", tolerance: 0.0005 })).toBe(false);
    expect(roughCheck("The data cannot answer this.", true, { gold: "refuse" })).toBe(true);
  });
});
