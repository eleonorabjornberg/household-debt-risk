// Build-time data access. Prefers Supabase (`mart` schema via PostgREST, publishable key) and
// falls back to the JSON snapshots that scripts/copy-data.mjs copies from ../web/public/data.
import { readFile } from "node:fs/promises";
import path from "node:path";
import { createClient } from "@supabase/supabase-js";
import {
  BUCKETS, DEBT_TYPES,
  type DebtByRiskHolderRow, type DimCrisisRow, type PublicShareRow, type Series,
} from "./types";

type Tables = {
  debt_by_risk_holder: DebtByRiskHolderRow;
  public_share: PublicShareRow;
  dim_crisis: DimCrisisRow;
};
type TableName = keyof Tables;

const ORDER: Record<TableName, string[]> = {
  debt_by_risk_holder: ["date", "risk_bucket", "debt_type"],
  public_share: ["date"],
  dim_crisis: ["start_q"],
};

function supabaseKey(): string | undefined {
  return process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || undefined;
}

function normalize<T>(rows: Record<string, unknown>[]): T[] {
  return rows.map((row) => {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(row)) {
      if (typeof v === "string" && (k === "date" || k === "start_q" || k === "end_q")) out[k] = v.slice(0, 10);
      else if (typeof v === "string" && (k.endsWith("_musd") || k === "public_share")) out[k] = Number(v);
      else out[k] = v;
    }
    return out as T;
  });
}

async function fromSupabase<K extends TableName>(table: K): Promise<Tables[K][]> {
  const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, supabaseKey()!, {
    db: { schema: "mart" },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const PAGE = 1000;
  const rows: Record<string, unknown>[] = [];
  for (let from = 0; ; from += PAGE) {
    let q = supabase.from(table).select("*");
    for (const col of ORDER[table]) q = q.order(col, { ascending: true });
    const { data, error } = await q.range(from, from + PAGE - 1);
    if (error) throw new Error(`supabase mart.${table}: ${error.message}`);
    rows.push(...(data ?? []));
    if (!data || data.length < PAGE) break;
  }
  return normalize<Tables[K]>(rows);
}

async function readJson<T>(name: string): Promise<T | null> {
  try {
    return JSON.parse(await readFile(path.join(process.cwd(), "public", "data", `${name}.json`), "utf8")) as T;
  } catch {
    return null;
  }
}

async function load<K extends TableName>(table: K): Promise<{ rows: Tables[K][]; fromDb: boolean }> {
  if (process.env.NEXT_PUBLIC_SUPABASE_URL && supabaseKey()) {
    try {
      return { rows: await fromSupabase(table), fromDb: true };
    } catch (err) {
      console.warn(`[data] ${(err as Error).message}; falling back to snapshot`);
    }
  }
  const rows = await readJson<Record<string, unknown>[]>(table);
  if (!rows) throw new Error(`No data for ${table}: run scripts/copy-data.mjs`);
  return { rows: normalize<Tables[K]>(rows), fromDb: false };
}

/** Everything the page needs, shaped into compact per-quarter arrays. */
export async function getSeries(): Promise<Series> {
  const [debt, share, crises] = await Promise.all([
    load("debt_by_risk_holder"), load("public_share"), load("dim_crisis"),
  ]);
  const meta = await readJson<{ cpi_base_quarter?: string }>("meta");

  const dates = [...new Set(debt.rows.map((r) => r.date))].sort();
  const qIndex = new Map(dates.map((d, i) => [d, i]));
  const real = dates.map(() => BUCKETS.map(() => DEBT_TYPES.map(() => 0)));
  for (const r of debt.rows) {
    const q = qIndex.get(r.date);
    const b = BUCKETS.indexOf(r.risk_bucket);
    const t = DEBT_TYPES.indexOf(r.debt_type);
    if (q === undefined || b < 0 || t < 0) continue;
    real[q][b][t] += Math.max(0, r.real_musd ?? 0);
  }
  const shareByDate = new Map(share.rows.map((r) => [r.date, r.public_share]));
  const publicShare = dates.map((d) => shareByDate.get(d) ?? NaN);

  const recessions = crises.rows
    .filter((c) => c.kind === "nber_recession" && c.end_q)
    .map((c) => ({ id: c.crisis_id, name: c.name, start: c.start_q, end: c.end_q! }));

  return {
    dates, real, publicShare, recessions,
    source: debt.fromDb && share.fromDb ? "supabase" : "snapshot",
    cpiBase: meta?.cpi_base_quarter ?? null,
  };
}
