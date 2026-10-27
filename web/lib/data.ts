// Data access for the story site.
//
// Order of preference per table:
//   1. Supabase (`mart` schema via PostgREST) when NEXT_PUBLIC_SUPABASE_URL and
//      NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY (or legacy NEXT_PUBLIC_SUPABASE_ANON_KEY) are set. The two `core` dims are read from `mart` views of
//      the same name (see README: "Exposing the mart schema"); if those views don't exist yet we
//      fall through to the files below for just those tables.
//   2. Snapshots written by the pipeline: public/data/<table>.json
//   3. Synthetic development fixtures: fixtures/<table>.json (clearly fake; see fixtures/README.md)
//
// Everything is fetched at build time and cached with `use cache` + cacheLife('days'), so pages are
// statically generated and revalidated roughly daily (ISR).
import { readFile } from "node:fs/promises";
import path from "node:path";
import { cacheLife, cacheTag } from "next/cache";
import { createClient } from "@supabase/supabase-js";
import type { DataSource, TableMap, TableName } from "./types";

const STRING_KEYS = new Set([
  "date", "start_q", "end_q", "risk_bucket", "debt_type", "collateral_class", "crisis_id", "metric",
  "loan_type", "name", "kind", "notes", "label",
]);

/** Coerce numeric strings (Postgres numeric via some drivers) to numbers and trim timestamps to dates. */
function normalize<T>(rows: Record<string, unknown>[]): T[] {
  return rows.map((row) => {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(row)) {
      if (typeof v === "string" && (k === "date" || k === "start_q" || k === "end_q")) out[k] = v.slice(0, 10);
      else if (typeof v === "string" && !STRING_KEYS.has(k) && v.trim() !== "" && Number.isFinite(Number(v))) out[k] = Number(v);
      else out[k] = v;
    }
    return out as T;
  });
}

/** Publishable key (sb_publishable_...), falling back to the legacy anon key name. */
function supabaseKey(): string | undefined {
  return process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || undefined;
}

export function supabaseConfigured(): boolean {
  return Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && supabaseKey());
}

const ORDER: Record<TableName, string[]> = {
  debt_by_risk_holder: ["date", "risk_bucket", "debt_type"],
  public_share: ["date"],
  collateral_coverage: ["date", "collateral_class"],
  crisis_event_window: ["crisis_id", "metric", "q_offset"],
  nyfed_by_type: ["date", "loan_type"],
  dim_crisis: ["start_q"],
  dim_risk_bucket: ["sort_order"],
};

async function fromSupabase<K extends TableName>(table: K): Promise<TableMap[K][]> {
  const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, supabaseKey()!, {
    db: { schema: "mart" },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const PAGE = 1000; // PostgREST default max-rows
  const rows: Record<string, unknown>[] = [];
  for (let from = 0; ; from += PAGE) {
    let q = supabase.from(table).select("*");
    for (const col of ORDER[table]) q = q.order(col, { ascending: true });
    const { data, error } = await q.range(from, from + PAGE - 1);
    if (error) throw new Error(`supabase mart.${table}: ${error.message}`);
    rows.push(...(data ?? []));
    if (!data || data.length < PAGE) break;
  }
  return normalize<TableMap[K]>(rows);
}

async function readJson(file: string): Promise<Record<string, unknown>[] | null> {
  try {
    const parsed = JSON.parse(await readFile(file, "utf8"));
    return Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

async function fromFiles<K extends TableName>(table: K): Promise<{ rows: TableMap[K][]; source: DataSource }> {
  const root = process.cwd();
  const snapshot = await readJson(path.join(root, "public", "data", `${table}.json`));
  if (snapshot && snapshot.length > 0) return { rows: normalize<TableMap[K]>(snapshot), source: "snapshot" };
  const fixture = await readJson(path.join(root, "fixtures", `${table}.json`));
  if (fixture) return { rows: normalize<TableMap[K]>(fixture), source: "fixture" };
  throw new Error(`No data for ${table}: expected public/data/${table}.json or fixtures/${table}.json`);
}

async function loadTable<K extends TableName>(table: K): Promise<{ rows: TableMap[K][]; source: DataSource }> {
  if (supabaseConfigured()) {
    try {
      return { rows: await fromSupabase(table), source: "supabase" };
    } catch (err) {
      // Dims may not be exposed as mart views yet; any other failure also degrades to files
      // rather than breaking the build, but we say so in the build log.
      console.warn(`[data] ${(err as Error).message}; falling back to files`);
    }
  }
  return fromFiles(table);
}

export interface StoryData {
  tables: { [K in TableName]: TableMap[K][] };
  sources: Record<TableName, DataSource>;
  fetchedAt: string;
}

/** All tables the story needs, cached for about a day. */
export async function getStoryData(): Promise<StoryData> {
  "use cache";
  cacheLife("days");
  cacheTag("story-data");

  const names: TableName[] = [
    "debt_by_risk_holder", "public_share", "collateral_coverage", "crisis_event_window",
    "nyfed_by_type", "dim_crisis", "dim_risk_bucket",
  ];
  const loaded = await Promise.all(names.map((n) => loadTable(n)));
  const tables = {} as StoryData["tables"];
  const sources = {} as StoryData["sources"];
  names.forEach((n, i) => {
    (tables as Record<string, unknown>)[n] = loaded[i].rows;
    sources[n] = loaded[i].source;
  });
  return { tables, sources, fetchedAt: new Date().toISOString() };
}

/** "fixture" if any table is synthetic, else the most common source. */
export function overallSource(sources: Record<TableName, DataSource>): DataSource {
  const vals = Object.values(sources);
  if (vals.includes("fixture")) return "fixture";
  if (vals.every((v) => v === "supabase")) return "supabase";
  return "snapshot";
}

export interface SnapshotMeta {
  mart_start?: string;
  mart_end?: string;
  cpi_base_quarter?: string;
  vintages?: Record<string, string>;
  generated_at?: string;
}

/** public/data/meta.json written by the pipeline alongside the snapshots (optional). */
export async function getSnapshotMeta(): Promise<SnapshotMeta | null> {
  "use cache";
  cacheLife("days");
  try {
    const parsed = JSON.parse(await readFile(path.join(process.cwd(), "public", "data", "meta.json"), "utf8"));
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as SnapshotMeta) : null;
  } catch {
    return null;
  }
}
