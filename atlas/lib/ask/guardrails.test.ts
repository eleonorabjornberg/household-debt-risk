// Offline tests for the E4 P1 guardrails (fake client, no API calls).
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { ask, SYSTEM } from "./agent";
import { loadEnv } from "./env";
import { answerNumbers, grounded, toolNumbers, ungrounded } from "./grounding";
import { computedNumbers, hypotheticalCheck, SYSTEM_RULES } from "./guardrails";
import { Limiter, MemoryStore } from "./limits";

const ROOT = path.join(__dirname, "..", "..");
const REPO = path.join(ROOT, "..");

describe("hypothetical pre-check", () => {
  it("refuses the P1 counterfactual (a2-1) and scenario wording", () => {
    for (const q of ["Suppose Fannie Mae and Freddie Mac were fully privatised in 2026Q2. What would the public share have been?",
                     "Imagine the Fed had never bought MBS. What would the private share have been in 2021Q4?",
                     "If house prices fell 20% tomorrow, what would home-backed collateral coverage drop to?",
                     "If the public share keeps moving at its recent pace, where does it land?",
                     "Draw the straight line through the last eight quarters and read off 2027."])
      expect(hypotheticalCheck(q), q).toMatchObject({ refused: true, reason_code: "hypothetical" });
  });

  it("refuses none of E1's answerable questions", () => {
    const gold = JSON.parse(readFileSync(path.join(REPO, "evals", "e1_sql_benchmark", "gold.json"), "utf8")).questions;
    const answerable = gold.filter((q: any) => q.gold !== "refuse");
    expect(answerable.length).toBeGreaterThan(50);
    expect(answerable.filter((q: any) => hypotheticalCheck(q.question)).map((q: any) => q.id)).toEqual([]);
  });

  it("refuses before any model call", async () => {
    const env = await loadEnv(ROOT);
    const calls: any[] = [];
    const client = { messages: { create: async (b: any) => { calls.push(b); return {}; } } };
    const a = await ask("Assume mortgage rates had stayed at 3% through 2026. How much higher would mortgage debt be?",
                        { client, env, limiter: new Limiter(new MemoryStore()) });
    expect(a).toMatchObject({ refused: true, reason_code: "hypothetical", cost_usd: 0 });
    expect(calls).toHaveLength(0);
  });
});

describe("system prompt rules", () => {
  it("carries the four E4 rules (counterfactuals, NY Fed/Z.1 arithmetic, asserted numbers, causes)", () => {
    expect(SYSTEM).toContain(SYSTEM_RULES);
    for (const w of [/hypothetical/, /NY Fed and Z\.1/, /asserts a number/, /causes/]) expect(SYSTEM_RULES).toMatch(w);
  });
});

describe("grounding v2 (P1 false-positive causes)", () => {
  const z1 = [10767594.115, 19097196, 0.5638311569, -0.34, 1263, "0.5464"];
  const g = (s: string, pool: unknown = z1) => answerNumbers(s).map((n) => grounded(n, toolNumbers(pool)));
  it("reads T and B suffixes, NY Fed billions, signs, numeric strings, ranges and decimal commas", () => {
    expect(g("about $10.77T of a $19.10T total")).toEqual([true, true]);
    expect(g("credit-card balance: $1,263 billion")).toEqual([true]);
    expect(g("$1.263T on cards")).toEqual([true]);
    expect(g("coverage was 0.34 lower")).toEqual([true]);
    expect(g("the estimate is 54.6%")).toEqual([true]);
    expect(g("2,79 billones de dólares", [2789536])).toEqual([true]);
    expect(g("in a band of about 56–58%", [0.56, 0.58])).toEqual([true, true]);
    expect(g("1 more quarter, 5 more years")).toEqual([]);
    expect(g("it would leave 9.4%")).toEqual([false]);
  });

  it("does not count numbers repeated from the question as ungrounded", () => {
    expect(ungrounded("I can't confirm 70%; the data shows 56.4%.", [{ v: 0.5638 }], "Confirm it was 70%")).toEqual([]);
    expect(ungrounded("Removing GSEs would leave 9.4%.", [{ v: 0.5638 }, { v: 0.47 }], "What if GSEs were privatised?")).toEqual(["9.4%"]);
  });
});

describe("post-answer computed-number label", () => {
  it("labels the model's own arithmetic and leaves grounded answers unchanged", async () => {
    const env = await loadEnv(ROOT);
    const reply = (text: string) => ({ messages: { create: async (b: any) => (b.messages.length === 1
      ? { model: "fake", usage: {}, stop_reason: "tool_use", content: [{ type: "tool_use", id: "t1", name: "public_share", input: { start: "2026Q2", end: "2026Q2" } }] }
      : { model: "fake", usage: {}, stop_reason: "end_turn", content: [{ type: "text", text }] }) } });
    const lim = () => new Limiter(new MemoryStore());
    const plain = await ask("What was the public share in 2026Q2?", { client: reply("It was 56.4% in 2026Q2."), env, limiter: lim() });
    expect(plain.answer).toBe("It was 56.4% in 2026Q2.");
    expect(plain.computed_numbers).toEqual([]);
    const derived = await ask("What was the private share in 2026Q2?", { client: reply("The private share was about 43.6% in 2026Q2."), env, limiter: lim() });
    expect(derived.computed_numbers).toEqual(["43.6%"]);
    expect(derived.answer).toMatch(/Computed from the data, not returned by it: 43\.6%\.$/);
  });

  it("matches the P1 failure a2-1 (counterfactual 9.4%) as computed", () => {
    expect(computedNumbers("Public share 56.4%; removing the GSE bucket would leave 9.4%.", [{ a: 0.5638, b: 0.47 }],
      "Suppose Fannie and Freddie were privatised")).toEqual(["9.4%"]);
  });
});
