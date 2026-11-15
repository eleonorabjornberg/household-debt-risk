// Ask Hot Potato (PLAN D6) limits, Eleonora's d6-preview (PLAN 0e0dd6c): 5 questions per visitor per UTC day and a
// $2/day hard stop for the whole app, enforced here, server-side, before any model call. Both need a store shared
// across serverless instances: Supabase counters (her choice of 2026-11-15; SupabaseStore), or Vercel KV / Upstash Redis
// (her earlier d6-store (a), PLAN e272d09; kept as a fallback). MemoryStore is for tests and local dev ONLY.

export interface Store {
  /** Add `by` to the number at `key` (creating it at 0), expire it after `ttlSeconds`, return the new value. */
  add(key: string, by: number, ttlSeconds: number): Promise<number>;
  get(key: string): Promise<number>;
}

export class MemoryStore implements Store {
  private m = new Map<string, number>();
  async add(key: string, by: number): Promise<number> {
    const v = (this.m.get(key) ?? 0) + by;
    this.m.set(key, v);
    return v;
  }
  async get(key: string): Promise<number> {
    return this.m.get(key) ?? 0;
  }
}

/** The three Upstash Redis client methods the store uses (@upstash/redis); a fake implements them in tests. */
export interface RedisLike {
  incrbyfloat(key: string, value: number): Promise<number>;
  expire(key: string, seconds: number): Promise<0 | 1>;
  get<T>(key: string): Promise<T | null>;
}

/** Vercel KV / Upstash Redis on its free tier (Eleonora, d6-store (a), PLAN e272d09). She adds the store; this only reads it. */
export class RedisStore implements Store {
  constructor(private redis: RedisLike) {}
  async add(key: string, by: number, ttlSeconds: number): Promise<number> {
    const v = await this.redis.incrbyfloat(key, by);
    await this.redis.expire(key, ttlSeconds);
    return Number(v);
  }
  async get(key: string): Promise<number> {
    const v = await this.redis.get<number | string>(key);
    return v === null || v === undefined ? 0 : Number(v);
  }
}

/** Calls a Postgres function through Supabase's REST API (PostgREST /rpc). A fake implements it in tests. */
export type RpcCall = (fn: string, args: Record<string, unknown>) => Promise<unknown>;

/** Supabase counters (Eleonora, 2026-11-15; migration 20261115000000_ask_limits.sql). The functions run as
 *  service_role only, so this needs the project's secret key, server side. */
export class SupabaseStore implements Store {
  constructor(private rpc: RpcCall) {}
  async add(key: string, by: number, ttlSeconds: number): Promise<number> {
    return Number(await this.rpc("ask_limit_add", { p_key: key, p_by: by, p_ttl_seconds: ttlSeconds }));
  }
  async get(key: string): Promise<number> {
    const v = await this.rpc("ask_limit_get", { p_key: key });
    return v === null || v === undefined ? 0 : Number(v);
  }
}

/** The Supabase URL (the site's public one) and the server-only secret key; null when either is missing. */
export function supabaseStoreEnv(env: Record<string, string | undefined> = process.env): { url: string; key: string } | null {
  const url = env.SUPABASE_URL ?? env.NEXT_PUBLIC_SUPABASE_URL;
  const key = env.SUPABASE_SECRET_KEY ?? env.SUPABASE_SERVICE_ROLE_KEY;
  return url && key ? { url: url.replace(/\/+$/, ""), key } : null;
}

export function supabaseRpc(cfg: { url: string; key: string }, fetchImpl: typeof fetch = fetch): RpcCall {
  return async (fn, args) => {
    const headers: Record<string, string> = { apikey: cfg.key, "content-type": "application/json" };
    if (cfg.key.startsWith("eyJ")) headers.authorization = `Bearer ${cfg.key}`; // legacy JWT service_role key
    const res = await fetchImpl(`${cfg.url}/rest/v1/rpc/${fn}`, { method: "POST", headers, body: JSON.stringify(args), cache: "no-store" });
    if (!res.ok) throw new Error(`limit store error ${res.status}`); // never echo the key or the response body
    return res.json();
  };
}

/** True when either shared limit store (Supabase or Redis) is configured. */
export const hasSharedStore = (env: Record<string, string | undefined> = process.env) =>
  !!(supabaseStoreEnv(env) || storeEnv(env));

/** The REST URL and token the Vercel KV or Upstash integration sets; null when either is missing (the gate then refuses). */
export function storeEnv(env: Record<string, string | undefined> = process.env): { url: string; token: string } | null {
  const url = env.KV_REST_API_URL ?? env.UPSTASH_REDIS_REST_URL;
  const token = env.KV_REST_API_TOKEN ?? env.UPSTASH_REDIS_REST_TOKEN;
  return url && token ? { url, token } : null;
}

export async function storeFromEnv(env: Record<string, string | undefined> = process.env): Promise<Store | null> {
  const sb = supabaseStoreEnv(env);
  if (sb) return new SupabaseStore(supabaseRpc(sb));
  const cfg = storeEnv(env);
  if (!cfg) return null;
  const { Redis } = await import("@upstash/redis");
  return new RedisStore(new Redis({ url: cfg.url, token: cfg.token }) as unknown as RedisLike);
}

export const QUESTIONS_PER_VISITOR_PER_DAY = 5;
export const APP_USD_PER_DAY = 2.0;
const DAY_TTL = 2 * 24 * 3600;

export class LimitError extends Error {
  constructor(public code: "visitor_daily_limit" | "app_daily_budget", message: string) { super(message); }
}

export const utcDay = (now: Date) => now.toISOString().slice(0, 10);

export class Limiter {
  constructor(private store: Store, private now: () => Date = () => new Date()) {}

  private key(kind: string, extra = "") { return `ask:${kind}:${utcDay(this.now())}${extra ? ":" + extra : ""}`; }

  /** Count one question for this visitor; refuse the 6th and later in a UTC day. Call once per question. */
  async admitVisitor(visitorHash: string): Promise<number> {
    const n = await this.store.add(this.key("visitor", visitorHash), 1, DAY_TTL);
    if (n > QUESTIONS_PER_VISITOR_PER_DAY)
      throw new LimitError("visitor_daily_limit",
        `This preview allows ${QUESTIONS_PER_VISITOR_PER_DAY} questions per visitor per day. Please come back tomorrow (UTC).`);
    return n;
  }

  async spentToday(): Promise<number> { return this.store.get(this.key("usd")); }

  /** Pre-call guard: refuse if the day's spend plus the worst case of the next call would reach the daily stop. */
  async guard(worstCaseUsd: number): Promise<void> {
    const spent = await this.spentToday();
    if (spent + worstCaseUsd >= APP_USD_PER_DAY)
      throw new LimitError("app_daily_budget",
        "Ask Hot Potato has reached its daily budget for this preview. Please try again tomorrow (UTC).");
  }

  /** Record a call's measured cost (logged usage x price). */
  async record(usd: number): Promise<number> { return this.store.add(this.key("usd"), usd, DAY_TTL); }
}
