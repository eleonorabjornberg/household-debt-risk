// Ask Hot Potato's per-request wiring: which limit store and which data source the route uses. Server only.
//  * Store: Supabase counters (2026-11-15) or Vercel KV / Upstash Redis, from their env vars. Without them: an in-memory store for local
//    dev only; on Vercel the gate already refuses (503), and this throws rather than fall back.
//  * Data (d6-data (b)): read-only mart reads through Supabase's API with the publishable key when the site's public
//    Supabase URL and key are set, cached for DATA_TTL_MS; else the committed snapshot. ASK_DATA=snapshot forces
//    the snapshot (tests, parity, local work that must not touch production).
import { loadEnv } from "./env";
import { MemoryStore, storeFromEnv, type Store } from "./limits";
import { martClient, martEnv, type MartClient } from "./mart";
import type { Env } from "./tools";

type ProcEnv = Record<string, string | undefined>;
export const DATA_TTL_MS = 10 * 60 * 1000;

let devStore: Store | null = null;
export async function askStore(env: ProcEnv = process.env): Promise<Store> {
  const s = await storeFromEnv(env);
  if (s) return s;
  if (env.VERCEL) throw new Error("no shared limit store configured");
  return (devStore ??= new MemoryStore());
}

/** The mart's public URL and publishable key (as lib/data.ts reads them), or null for the snapshot. */
export function martConfig(env: ProcEnv = process.env): { url: string; key: string } | null {
  if (env.ASK_DATA === "snapshot") return null;
  const url = env.NEXT_PUBLIC_SUPABASE_URL;
  const key = env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  return url && key ? { url, key } : null;
}

let cache: { at: number; env: Promise<Env> } | null = null;
export function resetDataCache() { cache = null; }

/** The tool environment for this request. A failed mart read is not cached and is not replaced by the snapshot. */
export async function askEnv(env: ProcEnv = process.env, deps: { client?: (url: string, key: string) => Promise<MartClient>;
                             base?: () => Promise<Env>; now?: () => number } = {}): Promise<Env> {
  const base = deps.base ?? (() => loadEnv());
  const cfg = martConfig(env);
  if (!cfg) return base();
  const now = (deps.now ?? Date.now)();
  if (!cache || now - cache.at > DATA_TTL_MS) {
    const p = (async () => martEnv(await (deps.client ?? martClient)(cfg.url, cfg.key), await base()))();
    cache = { at: now, env: p };
    p.catch(() => { if (cache?.env === p) cache = null; });
  }
  return cache.env;
}
