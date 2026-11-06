// Ask Hot Potato (PLAN D6): the household-credit MCP tools (D5), ported from
// mcp/household-credit-mcp/src/household_credit_mcp/core.py to run inside the site's serverless route.
// Snapshot backend only (the JSON tables the site ships). Every function returns the same envelope as the
// Python tool; parity.test.ts checks the outputs against Python fixtures. Nothing here invents numbers.

export type Row = Record<string, any>;
export type Tables = {
  public_share: Row[]; debt_by_risk_holder: Row[]; dim_risk_bucket: Row[]; collateral_coverage: Row[];
  crisis_event_window: Row[]; dim_crisis: Row[]; nyfed_by_type: Row[]; meta: Row;
};
export type Catalog = { series: Row[]; risk_buckets: Record<string, Row>; collateral_classes: Record<string, Row> };
export type Env = { tables: Tables; catalog: Catalog; claims: Row[] };

const Z1_UNITS = "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)";
const COMMON_Z1 = [
  "Z.1 levels are end-of-quarter and not seasonally adjusted.",
  "Holding is not a guarantee: a public holder owning a loan is not the same as the public guaranteeing it, " +
    "and a private holder may be protected by a guarantee.",
  "Mortgage holders are reported for ALL 1-4 family mortgages (incl. business borrowers) and apportioned to " +
    "households by each holder's share; this is a method, not a published Z.1 holder split for households.",
  "Scope = household and nonprofit 1-4 family mortgages + consumer credit (FL154104015), about 87% of total " +
    "household liabilities; it excludes HELOCs-as-separate-line, business debt and other liabilities.",
];
const PUBLIC_BUCKETS = ["federal_direct", "gse_agency", "state_local"];

// ------------------------------------------------------------------ backend (SnapshotBackend)
function vintages(env: Env): Row {
  const m = env.tables.meta;
  return { ...m.vintages, snapshot_generated_at: m.generated_at ?? null,
           source: `meta.json (${m.snapshot_source ?? "snapshot"} export)` };
}
const martRange = (env: Env): [string, string] => {
  const r = env.tables.public_share;
  return [r[0].date, r[r.length - 1].date];
};
const nyfedRange = (env: Env): [string, string] => {
  const d = env.tables.nyfed_by_type.map((r) => r.date as string).sort();
  return [d[0], d[d.length - 1]];
};
const between = (rows: Row[], s: string, e: string) => rows.filter((r) => s <= r.date && r.date <= e);

// ------------------------------------------------------------------ envelope helpers
function ok(env: Env, tool: string, data: unknown, o: { units: unknown; series_ids: string[]; source: string;
  caveats: string[]; extra?: Row }): Row {
  const v = vintages(env);
  return { ok: true, tool, backend: "snapshot", source: o.source,
           vintage: { source_vintage: v[o.source in v ? o.source : "z1"] ?? null, all: v },
           units: o.units, series_ids: o.series_ids, caveats: o.caveats, data, ...(o.extra ?? {}) };
}
export function refusal(tool: string, code: string, reason: string, nearest: Row[]): Row {
  return { ok: false, refused: true, tool, backend: "snapshot", reason_code: code, reason,
           nearest_answerable: nearest, note: "No number was returned: the data cannot answer this question." };
}

// ------------------------------------------------------------------ quarters
const QEND: Record<number, string> = { 1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31" };
export function parseQuarter(s: unknown): string | null {
  if (typeof s !== "string") return null;
  const m = /^\s*(\d{4})\s*-?\s*Q([1-4])\s*$/i.exec(s);
  if (m) return `${m[1]}-${QEND[Number(m[2])]}`;
  const t = s.trim();
  return /^\d{4}-(03-31|06-30|09-30|12-31)$/.test(t) ? t : null;
}
export const label = (d: string) => `${d.slice(0, 4)}Q${Math.floor((Number(d.slice(5, 7)) - 1) / 3) + 1}`;
const min = (a: string, b: string) => (a < b ? a : b);
const max = (a: string, b: string) => (a > b ? a : b);

function resolveRange(tool: string, start: unknown, end: unknown, lo: string, hi: string, alt: string):
  [string, string, null] | [null, null, Row] {
  const e = end ? parseQuarter(end) : hi;
  const s = start ? parseQuarter(start) : e;
  if (s === null || e === null)
    return [null, null, refusal(tool, "bad_quarter", "Quarters must look like 2026Q2 (quarterly data only).",
      [{ tool: alt, args: { start: label(hi), end: label(hi) } }])];
  if (s > e) return [null, null, refusal(tool, "bad_range", "start is after end.", [{ tool: alt, args: { start: label(e), end: label(e) } }])];
  if (s > hi || e > hi)
    return [null, null, refusal(tool, "future_or_unpublished",
      `Latest quarter in the data is ${label(hi)}. Later quarters are future or unpublished values; ` +
      "this server reports published history only and does not forecast.",
      [{ tool: alt, args: { start: label(min(s, hi)), end: label(hi) } }])];
  if (s < lo || e < lo)
    return [null, null, refusal(tool, "before_coverage", `Earliest quarter in the data for this table is ${label(lo)}.`,
      [{ tool: alt, args: { start: label(lo), end: label(min(max(e, lo), hi)) } }])];
  return [s, e, null];
}

// ------------------------------------------------------------------ formatting (as Python)
const pct = (x: number | null) => (x === null || x === undefined ? null : `${(x * 100).toFixed(1)}%`);
const tn = (m: number | null) => (m === null || m === undefined ? null : `$${(m / 1e6).toFixed(2)}T`);
const round3 = (v: number) => Math.round(v * 1000) / 1000;

function ids(env: Env, buckets: string[] | null = null, roles = ["mortgage_holder", "cc_holder"]): string[] {
  return env.catalog.series.filter((s) => roles.includes(s.role) && (buckets === null || buckets.includes(s.risk_bucket)))
    .map((s) => s.id);
}

// ------------------------------------------------------------------ catalog tools
function seriesRow(env: Env, s: Row): Row {
  const row: Row = { ...s };
  row.units = { z1: Z1_UNITS, fred: "see FRED series page (context series; frequency varies)",
                nyfed: "USD billions / % as published by the NY Fed (CCP)" }[s.source as "z1"];
  if (s.risk_bucket) {
    row.risk_bucket_label = env.catalog.risk_buckets[s.risk_bucket].label;
    row.is_public_holder = env.catalog.risk_buckets[s.risk_bucket].public;
  }
  return row;
}

export function list_series(env: Env, a: { role?: string | null; source?: string | null } = {}): Row {
  const rows = env.catalog.series.filter((s) => (a.role == null || s.role === a.role) && (a.source == null || s.source === a.source));
  const data = rows.map((s) => ({ id: s.id, source: s.source, role: s.role, desc: s.desc,
                                  risk_bucket: s.risk_bucket ?? null, debt_type: s.debt_type ?? null }));
  const roles = [...new Set(env.catalog.series.map((s) => s.role as string))].sort();
  return ok(env, "list_series", data, { units: "n/a (catalog listing)", series_ids: rows.map((s) => s.id), source: "z1",
    caveats: [`Available roles: ${roles.join(", ")}.`,
              "Catalog is pipeline/series_catalog.yaml; it lists what is loaded, not every Z.1 series."] });
}

export function describe_series(env: Env, a: { id?: string }): Row {
  const sid = (a.id ?? "").trim().toUpperCase();
  const hit = env.catalog.series.find((s) => String(s.id).toUpperCase() === sid);
  if (!hit) return refusal("describe_series", "unknown_series",
    `'${a.id ?? ""}' is not in the series catalog (the data holds only catalogued series).`, [{ tool: "list_series", args: {} }]);
  const cav: string[] = [];
  if (hit.role === "mortgage_holder") cav.push("Holder of ALL 1-4 family mortgages (asset side); apportioned to households in the mart.");
  if (hit.role === "cc_holder") cav.push("Holder of consumer credit (asset side); one dimension only, not split by loan type.");
  if (hit.role === "cc_type") cav.push("Loan type (liability side); Z.1 does not split these by holder.");
  if (hit.id === "FL155111005") cav.push("Consumer durable goods used as a proxy for vehicle collateral; it overstates vehicles.");
  if (hit.source === "fred") cav.push("Context series; not part of the holder shares.");
  const row = seriesRow(env, hit);
  return ok(env, "describe_series", row, { units: row.units, series_ids: [hit.id], source: hit.source,
    caveats: cav.length ? cav : ["See catalog header for methods."] });
}

// ------------------------------------------------------------------ data tools
export function public_share(env: Env, a: { start?: string | null; end?: string | null; measure?: string } = {}): Row {
  const tool = "public_share";
  const measure = a.measure ?? "total";
  if (!["total", "mortgage", "consumer_credit"].includes(measure))
    return refusal(tool, "bad_measure", "measure must be total, mortgage or consumer_credit.", [{ tool, args: { measure: "total" } }]);
  const [lo, hi] = martRange(env);
  const [s, e, r] = resolveRange(tool, a.start, a.end, lo, hi, tool);
  if (r) return r;
  const key = { total: "public_share", mortgage: "public_share_mortgage", consumer_credit: "public_share_cc" }[measure as "total"];
  const rows = between(env.tables.public_share, s!, e!).map((x) => {
    const row: Row = { quarter: label(x.date), date: x.date, public_share: x[key], public_share_display: pct(x[key]) };
    if (measure === "total")
      Object.assign(row, { public_musd: x.public_musd, public_usd_display: tn(x.public_musd),
        scope_total_musd: x.scope_total_musd, scope_usd_display: tn(x.scope_total_musd), fed_mbs_musd: x.fed_mbs_musd });
    return row;
  });
  const sids = { total: ["FL154104015", "FL153165105", "FL153166000", ...ids(env, PUBLIC_BUCKETS)],
                 mortgage: ["FL153165105", "FL893065105", ...ids(env, PUBLIC_BUCKETS, ["mortgage_holder"])],
                 consumer_credit: ["FL153166000", ...ids(env, PUBLIC_BUCKETS, ["cc_holder"])] }[measure as "total"];
  return ok(env, tool, rows, { source: "z1", series_ids: sids,
    caveats: [...COMMON_Z1, "Public = federal government (direct) + GSEs & agency pools + state & local governments. Dollars are nominal.",
              "fed_mbs_musd (Fed MBS, WSHOMCB) is a QE overlay already inside agency pools; never add it."],
    units: { public_share: "fraction 0-1 (display as %)", public_musd: Z1_UNITS, scope_total_musd: Z1_UNITS, measure } });
}

export function holdings_by_bucket(env: Env, a: { quarter?: string | null } = {}): Row {
  const tool = "holdings_by_bucket";
  const [lo, hi] = martRange(env);
  const d = a.quarter ? parseQuarter(a.quarter) : hi;
  if (d === null) return refusal(tool, "bad_quarter", "quarter must look like 2026Q2.", [{ tool, args: { quarter: label(hi) } }]);
  if (d > hi) return refusal(tool, "future_or_unpublished", `Latest quarter in the data is ${label(hi)}; this server does not forecast.`,
    [{ tool, args: { quarter: label(hi) } }]);
  if (d < lo) return refusal(tool, "before_coverage", `Earliest quarter is ${label(lo)}.`, [{ tool, args: { quarter: label(lo) } }]);
  const rows = env.tables.debt_by_risk_holder.filter((r) => r.date === d);
  if (!rows.length) return refusal(tool, "no_data", `No holdings rows for ${label(d)}.`, [{ tool, args: { quarter: label(hi) } }]);
  const dims: Record<string, Row> = Object.fromEntries(env.tables.dim_risk_bucket.map((b) => [b.risk_bucket, b]));
  const agg: Record<string, Row> = {};
  for (const r of rows) {
    const x = (agg[r.risk_bucket] ??= { mortgage_musd: 0, consumer_credit_musd: 0, nominal_musd: 0, real_musd: 0, share_of_scope: 0 });
    x[`${r.debt_type}_musd`] += r.nominal_musd;
    x.nominal_musd += r.nominal_musd;
    x.real_musd += r.real_musd ?? 0;
    x.share_of_scope += r.share_of_total;
  }
  const data: Row[] = Object.keys(agg).sort((p, q) => dims[p].sort_order - dims[q].sort_order).map((b) => {
    const v: Row = Object.fromEntries(Object.entries(agg[b]).map(([k, x]) => [k, k === "share_of_scope" ? x : round3(x)]));
    return { risk_bucket: b, label: dims[b].label, is_public: dims[b].is_public, ...v,
             share_display: pct(v.share_of_scope), usd_display: tn(v.nominal_musd),
             series_ids: env.catalog.series.filter((s) => s.risk_bucket === b && ["mortgage_holder", "cc_holder"].includes(s.role)).map((s) => s.id) };
  });
  const total = data.reduce((t, x) => t + x.nominal_musd, 0);
  const pub = data.filter((x) => x.is_public).reduce((t, x) => t + x.nominal_musd, 0);
  const summary = { quarter: label(d), scope_total_musd: round3(total), scope_usd_display: tn(total),
                    public_musd: round3(pub), public_share: pub / total, public_share_display: pct(pub / total) };
  return ok(env, tool, data, { source: "z1", series_ids: ["FL154104015", "FL153165105", "FL153166000", ...ids(env)],
    units: { nominal_musd: Z1_UNITS, real_musd: "USD millions, constant dollars of the latest CPI quarter (CPIAUCSL, FRED); an estimate",
             share_of_scope: "fraction 0-1 of mortgages + consumer credit" },
    caveats: [...COMMON_Z1, "Six risk buckets are this project's grouping of Z.1 holder sectors (catalog).",
              "real_musd uses a CPI deflator and is not a published Z.1 number."],
    extra: { summary } });
}

export function crisis_windows(env: Env, a: { crisis_id?: string | null; metric?: string } = {}): Row {
  const tool = "crisis_windows";
  const metric = a.metric ?? "public_share";
  const crises: Record<string, Row> = Object.fromEntries(env.tables.dim_crisis.map((c) => [c.crisis_id, c]));
  if (a.crisis_id && !(a.crisis_id in crises))
    return refusal(tool, "unknown_crisis", `'${a.crisis_id}' is not in dim_crisis.`, [{ tool, args: {}, crisis_ids: Object.keys(crises).sort() }]);
  const rows = env.tables.crisis_event_window.filter((r) => r.metric === metric && (!a.crisis_id || r.crisis_id === a.crisis_id));
  if (!rows.length)
    return refusal(tool, "unknown_metric", `No event-window rows for metric '${metric}'. Examples: public_share, share:gse_agency, ` +
      "share:uncollateralized, coverage:home_backed.", [{ tool, args: { metric: "public_share" } }]);
  const ratio = metric.startsWith("coverage:");
  const by = new Map<string, Map<number, Row>>();
  for (const r of rows) {
    if (!by.has(r.crisis_id)) by.set(r.crisis_id, new Map());
    by.get(r.crisis_id)!.set(r.q_offset, r);
  }
  const data = [...by.entries()].map(([cid, offs]) => {
    const t0 = offs.get(0);
    const c = crises[cid];
    const ks = [...offs.keys()];
    const row: Row = { crisis_id: cid, name: c.name, kind: c.kind, start_q: c.start_q, end_q: c.end_q, notes: c.notes,
                       t0_quarter: t0 ? label(t0.date) : null, value_at_t0: t0 ? t0.value : null,
                       max_offset_available: Math.max(...ks), min_offset_available: Math.min(...ks) };
    for (const k of [4, 8, 16]) {
      const o = offs.get(k);
      row[`delta_q${k}`] = o === undefined ? null : ratio ? o.delta_from_t0 : o.delta_from_t0 * 100;
    }
    return row;
  });
  return ok(env, tool, data, { source: "z1", series_ids: ["FL154104015", ...ids(env)],
    units: { value_at_t0: ratio ? "ratio (collateral/debt)" : "fraction 0-1",
             delta_qN: ratio ? "change vs t0, in ratio units" : "percentage points vs t0 (computed here as delta*100)",
             window: "q_offset -8..+16 quarters around t0 (crisis start quarter)" },
    caveats: [...COMMON_Z1, "Event windows are descriptive; a change after a crisis start is not shown to be caused by it.",
              "Recent crises have truncated windows (see max_offset_available); missing deltas are null, not zero."],
    extra: { metric } });
}

export function collateral_coverage(env: Env, a: { start?: string | null; end?: string | null } = {}): Row {
  const tool = "collateral_coverage";
  const [lo, hi] = martRange(env);
  const [s, e, r] = resolveRange(tool, a.start, a.end, lo, hi, tool);
  if (r) return r;
  const cl = env.catalog.collateral_classes;
  const data = between(env.tables.collateral_coverage, s!, e!).map((x) => ({
    quarter: label(x.date), date: x.date, collateral_class: x.collateral_class, label: cl[x.collateral_class]?.label ?? null,
    debt_musd: x.debt_musd, collateral_value_musd: x.collateral_value_musd, coverage_ratio: x.coverage_ratio,
    share_of_scope: x.share_of_debt, is_estimated: x.is_estimated }));
  return ok(env, tool, data, { source: "z1",
    series_ids: ["FL153165105", "FL153166100", "FL153166220", "FL153166400", "FL153166205", "FL155035015", "FL155111005"],
    units: { debt_musd: Z1_UNITS, collateral_value_musd: Z1_UNITS,
             coverage_ratio: "aggregate collateral value / aggregate debt (a ratio, not per-loan LTV)", share_of_scope: "fraction 0-1" },
    caveats: [...COMMON_Z1,
      "Coverage is a sector-level aggregate; it says nothing about any individual borrower's equity.",
      "Vehicle collateral is proxied by consumer durable goods (FL155111005) and overstates vehicles.",
      "Uncollateralized and other non-revolving classes have no collateral value (null ratio).",
      "Rows with is_estimated=true use an imputed loan-type split (early years); treat as estimates."] });
}

export function nyfed_by_type(env: Env, a: { start?: string | null; end?: string | null } = {}): Row {
  const tool = "nyfed_by_type";
  const [lo, hi] = nyfedRange(env);
  const [s, e, r] = resolveRange(tool, a.start, a.end, lo, hi, tool);
  if (r) return r;
  const data = between(env.tables.nyfed_by_type, s!, e!).map((x) => ({
    quarter: label(x.date), date: x.date, loan_type: x.loan_type, balance_busd: x.balance_busd,
    transition_into_serious_delinquency_pct: x.transition_serious_pct }));
  return ok(env, tool, data, { source: "nyfed", series_ids: ["NYFED_HHDC"],
    units: { balance_busd: "USD billions as published",
             transition_into_serious_delinquency_pct: "% of balance newly 90+ days delinquent, annualized, as published" },
    caveats: ["SOURCE IS THE NEW YORK FED CONSUMER CREDIT PANEL (credit bureau data), NOT FEDERAL RESERVE Z.1.",
      "Balances use a different definition from Z.1 and do not reconcile to Z.1 totals; do not mix them.",
      "This table splits by loan TYPE only. It has no holder dimension, so it cannot say who holds the debt.",
      "Student-loan delinquency transition is null in early years (not reported).",
      "Not seasonally adjusted as loaded; transition rates are annualized as published."] });
}

// ------------------------------------------------------------------ claims
const TOK = /[a-z0-9.%$]+/g;
export function lookup_claim(env: Env, a: { text_or_id?: string; limit?: number }): Row {
  const q = (a.text_or_id ?? "").trim().toLowerCase();
  const limit = a.limit ?? 5;
  if (!q) return refusal("lookup_claim", "empty_query", "Give a claim id or some words.", []);
  let hits = env.claims.filter((c) => String(c.claim_id).toLowerCase() === q);
  if (!hits.length) {
    const toks = new Set(q.match(TOK) ?? []);
    const scored: [number, Row][] = [];
    for (const c of env.claims) {
      const hay = [c.claim_id, c.claim, c.display, c.period].join(" ").toLowerCase();
      const hayT = new Set([...(hay.match(TOK) ?? []), ...String(c.claim_id).toLowerCase().split("_")]);
      let sc = 0;
      for (const t of toks) if (hayT.has(t)) sc++;
      if (sc) scored.push([sc, c]);
    }
    scored.sort((x, y) => y[0] - x[0]); // stable, as Python's sort
    hits = scored.slice(0, limit).map(([, c]) => c);
  }
  if (!hits.length) return refusal("lookup_claim", "no_matching_claim",
    "No row in claims/register.csv matches. Unregistered numbers are not published numbers.", [{ tool: "data_coverage", args: {} }]);
  const data = hits.map((c) => ({ claim_id: c.claim_id, claim: c.claim, display: c.display, value: c.value, unit: c.unit,
    period: c.period, check_id: c.check_id, series_ids: String(c.series_ids).split(/\s+/).filter(Boolean), vintage: c.vintage,
    validation: c.validation, computation: c.computation, notes: c.notes, quotable_as_verified: c.validation === "PASS" }));
  return ok(env, "lookup_claim", data, { units: "as stated per claim",
    series_ids: [...new Set(data.flatMap((d) => d.series_ids))].sort(), source: "z1",
    caveats: ["Source is claims/register.csv (read from the repository, not the database).",
      "Only validation=PASS rows are verified. UNVERIFIED rows are registered but not yet checked; " +
        "ESTIMATE rows are labelled estimates. Do not present non-PASS rows as fact.",
      "Vintage shown is each claim's own vintage."] });
}

// ------------------------------------------------------------------ coverage & refusals
export function data_coverage(env: Env): Row {
  const [lo, hi] = martRange(env);
  const [nlo, nhi] = nyfedRange(env);
  const cat = env.catalog;
  const data = {
    can_answer: [
      `Public vs private share of household 1-4 family mortgages + consumer credit, quarterly ${label(lo)}-${label(hi)} (Z.1).`,
      `Holdings by six risk buckets, in dollars and share of scope, ${label(lo)}-${label(hi)}; mortgages and consumer credit combined or separate, but not split by loan type within a holder.`,
      "Collateral coverage (collateral value / debt) by collateral class.",
      "Crisis event windows (-8..+16 quarters) for 14 recessions/shocks.",
      `NY Fed CCP balances and serious-delinquency transitions by loan type, ${label(nlo)}-${label(nhi)} (a different source from Z.1).`,
      "Registered, validated claims (claims/register.csv).",
    ],
    cannot_answer: [
      "Consumer credit by holder AND loan type together (Z.1 gives holders or types, never the cross), e.g. auto loans held by banks.",
      "Anything outside the covered quarters, and any forecast or future value.",
      "Loan-level or borrower-level questions (individual loans, credit scores, who owes what).",
      "Geographic splits (state, county, zip, metro): the data is national.",
      "Monthly, weekly or daily household-debt values (quarterly only).",
      "Delinquency by holder (the NY Fed table has types, not holders).",
      "Guarantee or credit-risk exposure: the data shows who holds debt, not who bears the loss.",
    ],
    coverage: { mart_quarters: [label(lo), label(hi)], nyfed_quarters: [label(nlo), label(nhi)],
                student_loans_reported_from: env.tables.meta.student_loans_reported_from ?? null,
                risk_buckets: Object.fromEntries(Object.entries(cat.risk_buckets).map(([k, v]) => [k, v.label])),
                series_in_catalog: cat.series.length },
  };
  return ok(env, "data_coverage", data, { units: "n/a", series_ids: [], source: "z1",
    caveats: ["Coverage dates come from the backend in use; vintages are in the vintage field."] });
}

const CC_TYPE = /(auto|car|vehicle|student|credit[ -]?card|card|revolving)/;
const HOLDER = /(held by|holder|holders|owned by|banks?\b|credit unions?|finance compan|gses?|fannie|freddie|federal government|abs\b|securiti[sz]|who holds|which (sector|institution))/;
const RULES: [string, RegExp, string, Row[]][] = [
  ["forecast", /forecast|predict|projection|project(ed)? (to|for)|will (be|rise|fall|reach)|next (quarter|year)|going to|in 20(2[7-9]|[3-9]\d)(?!\d)|by 20(2[7-9]|[3-9]\d)(?!\d)|future|expect/,
   "Forecasts and future values are not available; the server only reports published history.",
   [{ tool: "public_share", args: { measure: "total" } }, { tool: "crisis_windows", args: {} }]],
  ["loan_or_borrower_level", /borrower|loan[- ]level|individual|credit score|fico|my (loan|mortgage|debt)|which (people|households|families)|per household|per capita|income group|race|age group|zip/,
   "The data is aggregate sector totals. There is no loan-level or borrower-level information.",
   [{ tool: "holdings_by_bucket", args: {} }, { tool: "nyfed_by_type", args: {} }]],
  ["geography", /by state|per state|each state|state[- ]level|statewide|counties|county|metro|\bmsa\b|city|cities|region|california|texas|florida|new york (city|state)|rural|urban/,
   "The data is national. There are no state, county or regional splits.", [{ tool: "public_share", args: { measure: "total" } }]],
  ["frequency", /monthly|weekly|daily|month[- ]by[- ]month/, "Household-debt holdings are quarterly (end of quarter).",
   [{ tool: "public_share", args: {} }]],
];

export function check_answerable(env: Env, a: { question?: string }): Row {
  const tool = "check_answerable";
  const qs = (a.question ?? "").toLowerCase();
  const [lo, hi] = martRange(env);
  const holderXType = CC_TYPE.test(qs) && HOLDER.test(qs);
  const delinqHolder = /delinquen|default|90\+/.test(qs) && HOLDER.test(qs) && !/loan type|by type/.test(qs);
  if (holderXType || delinqHolder) {
    const why = holderXType
      ? "Z.1 reports consumer credit by holder OR by loan type, never both together, so the number cannot be read from the data."
      : "Delinquency is available by loan type (NY Fed CCP) but not by holder.";
    return refusal(tool, "holder_by_type_not_available", why, [
      { tool: "holdings_by_bucket", args: {}, gives: "consumer credit by holder (all types combined)" },
      { tool: "collateral_coverage", args: {}, gives: "consumer credit by type (all holders combined)" },
      { tool: "nyfed_by_type", args: {}, gives: "NY Fed balances/delinquency by type (not Z.1)" }]);
  }
  for (const [code, pat, reason, alt] of RULES) if (pat.test(qs)) return refusal(tool, code, reason, alt);
  for (const m of qs.matchAll(/\b(1[89]\d\d|20\d\d)\b(?:\s*q[1-4])?/g)) {
    const y = Number(m[1]);
    if (y < Number(lo.slice(0, 4)))
      return refusal(tool, "before_coverage", `Data starts in ${label(lo)}.`, [{ tool: "public_share", args: { start: label(lo), end: label(lo) } }]);
    if (y > Number(hi.slice(0, 4)))
      return refusal(tool, "future_or_unpublished", `Latest quarter is ${label(hi)}.`, [{ tool: "public_share", args: { end: label(hi) } }]);
  }
  return ok(env, tool, { answerable: true, note: "No refusal pattern matched. Use the data tools; they still refuse out-of-coverage quarters." },
    { units: "n/a", series_ids: [], source: "z1", caveats: ["Heuristic check only."] });
}

export const TOOLS: Record<string, (env: Env, args: any) => Row> = {
  list_series, describe_series, public_share, holdings_by_bucket, crisis_windows, collateral_coverage, nyfed_by_type,
  lookup_claim, data_coverage: (env) => data_coverage(env), check_answerable,
};
