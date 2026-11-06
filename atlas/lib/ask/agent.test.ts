// Offline tests (fake client, no API calls) for Ask Hot Potato's loop and her d6-preview limits.
import path from "node:path";
import { describe, expect, it } from "vitest";
import { ask, callCost, MAX_TURNS, WORST_CALL_USD } from "./agent";
import { loadEnv } from "./env";
import { APP_USD_PER_DAY, Limiter, LimitError, MemoryStore, QUESTIONS_PER_VISITOR_PER_DAY } from "./limits";

const ROOT = path.join(__dirname, "..", "..");
const USAGE = { input_tokens: 200, output_tokens: 150, cache_read_input_tokens: 2000, cache_creation_input_tokens: 500 };

/** One tool call, then an answer (or tool calls forever with `loop`). */
function fakeClient(opts: { loop?: boolean; answer?: string } = {}) {
  const calls: any[] = [];
  return {
    calls,
    messages: {
      create: async (body: any) => {
        calls.push(body);
        const first = body.messages.length === 1;
        if (opts.loop || first)
          return { model: "claude-sonnet-5-5", usage: USAGE, stop_reason: "tool_use",
                   content: [{ type: "tool_use", id: `t${calls.length}`, name: "public_share", input: { start: "2026Q2" } }] };
        return { model: "claude-sonnet-5-5", usage: USAGE, stop_reason: "end_turn", content: [{ type: "text", text: opts.answer ?? "56.4% in 2026Q2." }] };
      },
    },
  };
}

describe("limits (d6-preview)", () => {
  it("refuses a visitor's 6th question in a UTC day and resets the next day", async () => {
    let now = new Date("2026-11-06T10:00:00Z");
    const lim = new Limiter(new MemoryStore(), () => now);
    for (let i = 0; i < QUESTIONS_PER_VISITOR_PER_DAY; i++) await lim.admitVisitor("v1");
    await expect(lim.admitVisitor("v1")).rejects.toThrow(LimitError);
    await expect(lim.admitVisitor("v2")).resolves.toBe(1); // other visitors unaffected
    now = new Date("2026-11-07T00:00:01Z");
    await expect(lim.admitVisitor("v1")).resolves.toBe(1);
  });

  it("stops the whole app before a call could reach $2 in a day", async () => {
    const lim = new Limiter(new MemoryStore(), () => new Date("2026-11-06T10:00:00Z"));
    await lim.record(APP_USD_PER_DAY - WORST_CALL_USD + 0.0001);
    await expect(lim.guard(WORST_CALL_USD)).rejects.toMatchObject({ code: "app_daily_budget" });
  });
});

describe("ask (fake client)", () => {
  it("refuses a forecast before any model call", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient();
    const a = await ask("What will the public share be in 2027Q4?", { client, env, limiter: new Limiter(new MemoryStore()) });
    expect(a.refused).toBe(true);
    expect(a.reason_code).toBe("forecast");
    expect(client.calls.length).toBe(0);
    expect(a.cost_usd).toBe(0);
  });

  it("refuses holder x loan type before any model call", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient();
    const a = await ask("How many auto loans did banks hold in 2026Q2?", { client, env, limiter: new Limiter(new MemoryStore()) });
    expect(a.reason_code).toBe("holder_by_type_not_available");
    expect(client.calls.length).toBe(0);
  });

  it("answers with its sources (tool, args, series IDs, vintage) and records the cost", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient();
    const limiter = new Limiter(new MemoryStore());
    const a = await ask("What was the public share in 2026Q2?", { client, env, limiter });
    expect(a.refused).toBe(false);
    expect(a.sources).toHaveLength(1);
    expect(a.sources[0]).toMatchObject({ tool: "public_share", args: { start: "2026Q2" }, ok: true, source: "z1" });
    expect(a.sources[0].vintage).toBe(env.tables.meta.vintages.z1);
    expect(a.sources[0].series_ids).toContain("FL154104015");
    expect(a.cost_usd).toBeCloseTo(2 * callCost(USAGE), 9);
    expect(await limiter.spentToday()).toBeCloseTo(a.cost_usd, 9);
    // the request: Sonnet, cached system prompt and tools, top-level cache, effort medium
    expect(client.calls[0]).toMatchObject({ model: "claude-sonnet-5-5", output_config: { effort: "medium" },
                                            cache_control: { type: "ephemeral" } });
    expect(client.calls[0].system[0].cache_control).toEqual({ type: "ephemeral" });
    // every call row records the model that actually answered (from the API response)
    expect(a.usage.map((u) => u.served_model)).toEqual(["claude-sonnet-5-5", "claude-sonnet-5-5"]);
  });

  it("stops at the turn limit without an answer", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient({ loop: true });
    const a = await ask("What was the public share in 2026Q2?", { client, env, limiter: new Limiter(new MemoryStore()) });
    expect(client.calls.length).toBe(MAX_TURNS);
    expect(a).toMatchObject({ refused: true, reason_code: "turn_limit", truncated: true });
  });

  it("makes no call once the app's daily budget is spent", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient();
    const limiter = new Limiter(new MemoryStore());
    await limiter.record(APP_USD_PER_DAY);
    await expect(ask("What was the public share in 2026Q2?", { client, env, limiter })).rejects.toMatchObject({ code: "app_daily_budget" });
    expect(client.calls.length).toBe(0);
  });

  it("rejects empty and over-long questions without a call", async () => {
    const env = await loadEnv(ROOT);
    const client = fakeClient();
    const limiter = new Limiter(new MemoryStore());
    expect((await ask("  ", { client, env, limiter })).reason_code).toBe("empty");
    expect((await ask("x".repeat(501), { client, env, limiter })).reason_code).toBe("too_long");
    expect(client.calls.length).toBe(0);
  });
});
