// Ask Hot Potato data source at question time (Eleonora, d6-data (b), PLAN e272d09): READ-ONLY queries to the
// production `mart` schema through Supabase's API with the publishable key, as atlas does at build time
// (lib/data.ts). Her choice authorizes read-only mart reads and nothing else on production. This module can only
// SELECT (with ordering and paging) from the seven allowlisted mart tables; tests check that.
import type { Env, Row, Tables } from "./tools";

export const MART_TABLES = ["public_share", "debt_by_risk_holder", "dim_risk_bucket", "collateral_coverage",
                            "crisis_event_window", "dim_crisis", "nyfed_by_type"] as const;
export type MartTable = (typeof MART_TABLES)[number];
const ORDER: Record<MartTable, string[]> = {
  public_share: ["date"], debt_by_risk_holder: ["date", "risk_bucket", "debt_type"], dim_risk_bucket: ["sort_order"],
  collateral_coverage: ["date", "collateral_class"], crisis_event_window: ["crisis_id", "metric", "q_offset"],
  dim_crisis: ["start_q"], nyfed_by_type: ["date", "loan_type"],
};
const PAGE = 1000;
const TEXT_KEYS = new Set(["date", "start_q", "end_q", "crisis_id", "metric", "name", "kind", "notes", "risk_bucket",
                           "debt_type", "label", "collateral_class", "loan_type"]);

/** The only query shape used: from(table).select("*").order(...).range(a, b). */
type Query = { order(col: string, o: { ascending: boolean }): Query; range(a: number, b: number): PromiseLike<{ data: Row[] | null; error: { message: string } | null }> };
export type MartClient = { from(table: string): { select(cols: string): Query } };

export function martClient(url: string, key: string): Promise<MartClient> {
  return import("@supabase/supabase-js").then(({ createClient }) =>
    createClient(url, key, { db: { schema: "mart" }, auth: { persistSession: false, autoRefreshToken: false } }) as unknown as MartClient);
}

function normalize(rows: Row[]): Row[] {
  return rows.map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) => {
    if (typeof v === "string" && (k === "date" || k === "start_q" || k === "end_q")) return [k, v.slice(0, 10)];
    if (typeof v === "string" && !TEXT_KEYS.has(k) && /^-?\d+(\.\d+)?(e[-+]?\d+)?$/i.test(v)) return [k, Number(v)];
    return [k, v];
  })));
}

export async function readMartTable(client: MartClient, table: MartTable): Promise<Row[]> {
  if (!MART_TABLES.includes(table)) throw new Error(`not an allowlisted mart table: ${table}`);
  const rows: Row[] = [];
  for (let from = 0; ; from += PAGE) {
    let q = client.from(table).select("*");
    for (const c of ORDER[table]) q = q.order(c, { ascending: true });
    const { data, error } = await q.range(from, from + PAGE - 1);
    if (error) throw new Error(`supabase mart.${table}: ${error.message}`);
    rows.push(...(data ?? []));
    if (!data || data.length < PAGE) break;
  }
  return normalize(rows);
}

/** Build the tool environment from the live mart (tables) plus the snapshot's meta.json (vintages), catalog and register. */
export async function martEnv(client: MartClient, base: Env): Promise<Env> {
  const entries = await Promise.all(MART_TABLES.map(async (t) => [t, await readMartTable(client, t)] as const));
  const tables = { ...Object.fromEntries(entries), meta: base.tables.meta } as Tables;
  const check = vintageCheck(tables);
  return { tables, catalog: base.catalog, claims: base.claims, backend: "mart_api", vintage_check: check,
           note: "Live mart via Supabase's read-only API; vintages are from the committed snapshot's meta.json." +
                 (check.matches ? "" : ` ${check.message}`) };
}

/** The live rows and the snapshot's vintages can drift apart after a mart refresh: compare the latest quarter in
 *  each live table with meta.json's mart_end, and the live public_share's first quarter with mart_start. */
export function vintageCheck(tables: Tables): Row {
  const meta = tables.meta ?? {};
  const last = (rows: Row[]) => rows.reduce((m: string | null, r) => (r.date && (!m || r.date > m) ? r.date : m), null);
  const ends: Row = {};
  for (const t of ["public_share", "debt_by_risk_holder", "collateral_coverage"] as const) ends[t] = last(tables[t]);
  const start = tables.public_share.reduce((m: string | null, r) => (r.date && (!m || r.date < m) ? r.date : m), null);
  const bad = Object.entries(ends).filter(([, d]) => d !== meta.mart_end).map(([t, d]) => `${t} ends ${d}`);
  if (start !== meta.mart_start) bad.push(`public_share starts ${start}`);
  const matches = bad.length === 0;
  return { matches, snapshot_mart_start: meta.mart_start ?? null, snapshot_mart_end: meta.mart_end ?? null, live_ends: ends,
           message: matches ? "Live mart coverage matches the snapshot's meta.json."
             : `VINTAGE MISMATCH: the live mart (${bad.join("; ")}) does not match the snapshot's meta.json ` +
               `(${meta.mart_start} to ${meta.mart_end}); the vintages shown may be older than the live data.` };
}
