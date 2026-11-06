// Offline tests for her d6-store (a) and d6-data (b) choices: the Redis limit store against a fake client, and the
// read-only mart source against a fake Supabase client built from the snapshot. No network, no store, no production.
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { loadEnv } from "./env";
import { deploymentGate } from "./gate";
import { Limiter, LimitError, RedisStore, storeEnv, storeFromEnv, type RedisLike } from "./limits";
import { MART_TABLES, martEnv, readMartTable, type MartClient } from "./mart";
import { askEnv, askStore, martConfig, resetDataCache, DATA_TTL_MS } from "./runtime";
import { TOOLS, type Env, type Row } from "./tools";

const ROOT = path.join(__dirname, "..", "..");

class FakeRedis implements RedisLike {
  m = new Map<string, string>(); ttl = new Map<string, number>(); calls: string[] = [];
  async incrbyfloat(k: string, v: number) { this.calls.push("incrbyfloat"); const n = Number(this.m.get(k) ?? 0) + v; this.m.set(k, String(n)); return n; }
  async expire(k: string, s: number) { this.calls.push("expire"); this.ttl.set(k, s); return 1 as const; }
  async get<T>(k: string) { this.calls.push("get"); return (this.m.get(k) ?? null) as T | null; }
}

describe("RedisStore (d6-store (a), fake client)", () => {
  it("counts, expires and reads back; the Limiter enforces both limits through it", async () => {
    const r = new FakeRedis();
    const lim = new Limiter(new RedisStore(r), () => new Date("2026-11-06T12:00:00Z"));
    for (let i = 1; i <= 5; i++) await expect(lim.admitVisitor("v")).resolves.toBe(i);
    await expect(lim.admitVisitor("v")).rejects.toBeInstanceOf(LimitError);
    expect(r.ttl.get("ask:visitor:2026-11-06:v")).toBe(2 * 24 * 3600);
    await lim.record(1.25);
    expect(await lim.spentToday()).toBeCloseTo(1.25, 9); // read back from a string, as Redis returns it
    await expect(lim.guard(0.8)).rejects.toMatchObject({ code: "app_daily_budget" });
    expect(new Set(r.calls)).toEqual(new Set(["incrbyfloat", "expire", "get"]));
  });

  it("reads a missing key as zero", async () => {
    expect(await new RedisStore(new FakeRedis()).get("nope")).toBe(0);
  });

  it("finds the store from Vercel KV or Upstash env vars, and nothing without both URL and token", async () => {
    expect(storeEnv({ KV_REST_API_URL: "https://x", KV_REST_API_TOKEN: "t" })).toEqual({ url: "https://x", token: "t" });
    expect(storeEnv({ UPSTASH_REDIS_REST_URL: "https://y", UPSTASH_REDIS_REST_TOKEN: "u" })).toEqual({ url: "https://y", token: "u" });
    expect(storeEnv({ KV_REST_API_URL: "https://x" })).toBeNull();
    expect(await storeFromEnv({})).toBeNull();
  });

  it("fails closed on Vercel without a store; local dev gets the in-memory store", async () => {
    await expect(askStore({ VERCEL: "1" })).rejects.toThrow(/no shared limit store/);
    const s = await askStore({});
    expect(s.constructor.name).toBe("MemoryStore");
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "preview", NEXT_PUBLIC_ASK_ENABLED: "1", HHDEBT_ANTHROPIC_API_KEY: "x" })).toMatchObject({ ok: false, status: 503 });
  });
});

/** A fake Supabase client serving snapshot rows, recording every call. Numbers come back as strings and dates as
 *  timestamps, the worst case of what PostgREST may return, so normalization is exercised. */
function fakeMart(env: Env) {
  const calls: string[][] = [];
  const client: MartClient = {
    from(table: string) {
      calls.push(["from", table]);
      return {
        select(cols: string) {
          calls.push(["select", cols]);
          const order: string[] = [];
          const q = {
            order(c: string, o: { ascending: boolean }) { calls.push(["order", c, String(o.ascending)]); order.push(c); return q; },
            async range(a: number, b: number) {
              calls.push(["range", String(a), String(b)]);
              const rows = [...((env.tables as Row)[table] as Row[])].sort((x, y) => {
                for (const c of order) { if (x[c] < y[c]) return -1; if (x[c] > y[c]) return 1; } return 0; });
              const data = rows.slice(a, b + 1).map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) =>
                [k, typeof v === "number" ? String(v) : typeof v === "string" && /^\d{4}-\d\d-\d\d$/.test(v) ? `${v}T00:00:00` : v])));
              return { data, error: null };
            },
          };
          return q;
        },
      };
    },
  };
  return { client, calls };
}

describe("mart source (d6-data (b), fake client)", () => {
  it("only ever selects from allowlisted mart tables, with order and range: no writes, no RPC, no other schema", async () => {
    const snap = await loadEnv(ROOT);
    const { client, calls } = fakeMart(snap);
    await martEnv(client, snap);
    expect(new Set(calls.map((c) => c[0]))).toEqual(new Set(["from", "select", "order", "range"]));
    expect(new Set(calls.filter((c) => c[0] === "from").map((c) => c[1]))).toEqual(new Set(MART_TABLES));
    expect(calls.filter((c) => c[0] === "select").every((c) => c[1] === "*")).toBe(true);
    // paging: the largest table needs more than one 1000-row page
    expect(calls.filter((c) => c[0] === "range" && c[1] === "1000").length).toBeGreaterThan(0);
    await expect(readMartTable(client, "raw_series" as any)).rejects.toThrow(/allowlisted/);
  });

  it("gives the same tool data as the snapshot it was built from (parity)", async () => {
    const snap = await loadEnv(ROOT);
    const live = await martEnv(fakeMart(snap).client, snap);
    expect(live.backend).toBe("mart_api");
    const strip = (o: Row) => { const { backend, backend_note, vintage, ...rest } = o; return rest; };
    const calls: [string, Row][] = [
      ["public_share", {}], ["public_share", { start: "2006Q1", end: "2010Q4", measure: "mortgage" }],
      ["holdings_by_bucket", { quarter: "2007Q4" }], ["holdings_by_bucket", {}],
      ["crisis_windows", {}], ["crisis_windows", { crisis_id: "gfc_2008", metric: "public_share" }],
      ["collateral_coverage", { start: "2019Q1", end: "2020Q4" }], ["nyfed_by_type", { start: "2008Q1", end: "2009Q4" }],
      ["data_coverage", {}], ["lookup_claim", { text_or_id: "public share" }],
    ];
    for (const [t, a] of calls) {
      const s = TOOLS[t](snap, a), l = TOOLS[t](live, a);
      expect(strip(l), `${t} ${JSON.stringify(a)}`).toEqual(strip(s));
      if (l.ok) expect(l.backend).toBe("mart_api");
      if (l.ok) expect(l.vintage.all.source).toMatch(/mart API cannot report vintages/);
    }
  });

  it("uses the mart only when the public Supabase URL and key are set, caches it, and never falls back on failure", async () => {
    resetDataCache();
    const snap = await loadEnv(ROOT);
    expect(martConfig({})).toBeNull();
    expect(martConfig({ NEXT_PUBLIC_SUPABASE_URL: "https://p", NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "k", ASK_DATA: "snapshot" })).toBeNull();
    expect((await askEnv({}, { base: async () => snap })).backend).toBeUndefined();
    const cfg = { NEXT_PUBLIC_SUPABASE_URL: "https://p", NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "k" };
    let made = 0, t = 0;
    const deps = { base: async () => snap, now: () => t, client: async () => { made++; return fakeMart(snap).client; } };
    expect((await askEnv(cfg, deps)).backend).toBe("mart_api");
    await askEnv(cfg, deps);
    expect(made).toBe(1);
    t = DATA_TTL_MS + 1;
    await askEnv(cfg, deps);
    expect(made).toBe(2);
    resetDataCache();
    const broken = { ...deps, client: async () => ({ from: () => ({ select: () => {
      const q: any = { order: () => q, range: async () => ({ data: null, error: { message: "down" } }) }; return q; } }) }) };
    await expect(askEnv(cfg, broken)).rejects.toThrow(/down/);
    resetDataCache();
  });

  it("no Ask code writes through the API or names the core or raw schemas (static scan)", () => {
    const files: string[] = [];
    const walk = (d: string) => { for (const f of readdirSync(d)) { const p = path.join(d, f);
      if (statSync(p).isDirectory()) walk(p); else if (/\.(ts|tsx)$/.test(f) && !/\.test(-helpers)?\.ts$|\.test\.ts$/.test(f)) files.push(p); } };
    walk(path.join(ROOT, "lib", "ask")); walk(path.join(ROOT, "app", "api", "ask"));
    expect(files.length).toBeGreaterThan(5);
    for (const f of files) {
      const src = readFileSync(f, "utf8");
      expect(src, f).not.toMatch(/\.(insert|upsert|delete|rpc)\s*\(/);
      // .update( only as a hash update (createHash(...).update), never on a table query
      expect(src.replace(/createHash\([^)]*\)\s*\.update\(/g, ""), f).not.toMatch(/\.update\s*\(/);
      expect(src, f).not.toMatch(/schema:\s*["'](core|raw|public)["']|\b(core|raw)\.(?!py\b)[a-z_]+\b/);
      expect(src, f).not.toMatch(/SERVICE_ROLE|DATABASE_URL/);
    }
  });
});

describe("vintage drift check (mart rows live, vintages from the snapshot)", () => {
  it("passes when the live coverage matches meta.json and flags a mart refresh the snapshot has not seen", async () => {
    const snap = await loadEnv(ROOT);
    const same = await martEnv(fakeMart(snap).client, snap);
    expect(same.vintage_check).toMatchObject({ matches: true });
    expect(same.note).not.toMatch(/MISMATCH/);
    // a refreshed mart: one quarter newer than the snapshot
    const newer = { ...snap, tables: { ...snap.tables,
      public_share: [...snap.tables.public_share, { ...snap.tables.public_share.at(-1), date: "2026-09-30" }] } };
    const live = await martEnv(fakeMart(newer as Env).client, snap);
    expect(live.vintage_check).toMatchObject({ matches: false, snapshot_mart_end: snap.tables.meta.mart_end });
    expect(live.vintage_check!.message).toMatch(/VINTAGE MISMATCH.*public_share ends 2026-09-30/);
    const out = TOOLS.public_share(live, {});
    expect(out.backend_note).toMatch(/VINTAGE MISMATCH/);
    expect(out.vintage.all.vintage_check.matches).toBe(false);
  });
});
