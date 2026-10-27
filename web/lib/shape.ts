// Turns mart rows into compact, chart-ready structures (column arrays, not row objects) so the
// client components receive small payloads.
import type { StoryData } from "./data";
import type { CollateralClass, DebtType, LoanType, RiskBucket } from "./types";

export const BUCKET_ORDER: RiskBucket[] = [
  "federal_direct", "gse_agency", "state_local", "banks_credit_unions", "private_securitization", "nonbank_other",
];
export const COLLATERAL_ORDER: CollateralClass[] = ["home_backed", "vehicle_backed", "uncollateralized", "other_nonrevolving"];
export const LOAN_ORDER: LoanType[] = ["mortgage", "heloc", "auto", "credit_card", "student", "other"];

export interface Crisis {
  id: string;
  name: string;
  kind: "nber_recession" | "policy_shock";
  start: string;
  end: string | null;
}

export interface BucketMeta {
  key: RiskBucket;
  label: string;
  isPublic: boolean;
}

export interface RatchetData {
  dates: string[];
  buckets: BucketMeta[];
  nominal: Record<DebtType, Record<RiskBucket, number[]>>;
  real: Record<DebtType, Record<RiskBucket, (number | null)[]>>;
}

export interface PublicSeries {
  dates: string[];
  share: number[];
  shareMortgage: number[];
  shareCc: number[];
  scopeTotal: number[];
  fedMbsShare: (number | null)[];
}

export interface CrisisWindows {
  crises: Crisis[];
  metrics: string[];
  offsets: number[];
  /** values[crisis][metric][i] where i = q_offset + 8 */
  values: Record<string, Record<string, (number | null)[]>>;
  dates: Record<string, (string | null)[]>;
}

export interface CollateralData {
  dates: string[];
  share: Record<CollateralClass, number[]>;
  coverage: Record<CollateralClass, (number | null)[]>;
  estimatedThrough: string | null;
}

export interface NyfedData {
  dates: string[];
  transition: Record<LoanType, (number | null)[]>;
  balance: Record<LoanType, (number | null)[]>;
}

const emptyBy = <K extends string, V>(keys: readonly K[], f: () => V) =>
  Object.fromEntries(keys.map((k) => [k, f()])) as Record<K, V>;

export function crises(d: StoryData): Crisis[] {
  return [...d.tables.dim_crisis]
    .sort((a, b) => a.start_q.localeCompare(b.start_q))
    .map((c) => ({ id: c.crisis_id, name: c.name, kind: c.kind, start: c.start_q, end: c.end_q }));
}

export function bucketMeta(d: StoryData): BucketMeta[] {
  const byKey = new Map(d.tables.dim_risk_bucket.map((b) => [b.risk_bucket, b]));
  return BUCKET_ORDER.map((k) => ({
    key: k,
    label: byKey.get(k)?.label ?? k,
    isPublic: byKey.get(k)?.is_public ?? ["federal_direct", "gse_agency", "state_local"].includes(k),
  }));
}

export function ratchetData(d: StoryData): RatchetData {
  const dates = [...new Set(d.tables.debt_by_risk_holder.map((r) => r.date))].sort();
  const idx = new Map(dates.map((x, i) => [x, i]));
  const types: DebtType[] = ["mortgage", "consumer_credit"];
  const nominal = emptyBy(types, () => emptyBy(BUCKET_ORDER, () => new Array<number>(dates.length).fill(0)));
  const real = emptyBy(types, () => emptyBy(BUCKET_ORDER, () => new Array<number | null>(dates.length).fill(null)));
  for (const r of d.tables.debt_by_risk_holder) {
    const i = idx.get(r.date)!;
    if (!nominal[r.debt_type]?.[r.risk_bucket]) continue;
    nominal[r.debt_type][r.risk_bucket][i] = r.nominal_musd;
    real[r.debt_type][r.risk_bucket][i] = r.real_musd;
  }
  return { dates, buckets: bucketMeta(d), nominal, real };
}

export function publicSeries(d: StoryData): PublicSeries {
  const rows = [...d.tables.public_share].sort((a, b) => a.date.localeCompare(b.date));
  return {
    dates: rows.map((r) => r.date),
    share: rows.map((r) => r.public_share),
    shareMortgage: rows.map((r) => r.public_share_mortgage),
    shareCc: rows.map((r) => r.public_share_cc),
    scopeTotal: rows.map((r) => r.scope_total_musd),
    fedMbsShare: rows.map((r) => r.fed_mbs_share_of_scope),
  };
}

export function crisisWindows(d: StoryData): CrisisWindows {
  const cs = crises(d);
  const offsets = Array.from({ length: 25 }, (_, i) => i - 8);
  const metrics = [...new Set(d.tables.crisis_event_window.map((r) => r.metric))];
  const values: CrisisWindows["values"] = {};
  const dates: CrisisWindows["dates"] = {};
  for (const c of cs) {
    values[c.id] = Object.fromEntries(metrics.map((m) => [m, new Array(25).fill(null)]));
    dates[c.id] = new Array(25).fill(null);
  }
  for (const r of d.tables.crisis_event_window) {
    if (!values[r.crisis_id]) continue;
    const i = r.q_offset + 8;
    values[r.crisis_id][r.metric][i] = r.value;
    dates[r.crisis_id][i] = r.date;
  }
  return { crises: cs, metrics, offsets, values, dates };
}

export function collateralData(d: StoryData): CollateralData {
  const dates = [...new Set(d.tables.collateral_coverage.map((r) => r.date))].sort();
  const idx = new Map(dates.map((x, i) => [x, i]));
  const share = emptyBy(COLLATERAL_ORDER, () => new Array<number>(dates.length).fill(0));
  const coverage = emptyBy(COLLATERAL_ORDER, () => new Array<number | null>(dates.length).fill(null));
  let estimatedThrough: string | null = null;
  for (const r of d.tables.collateral_coverage) {
    const i = idx.get(r.date)!;
    share[r.collateral_class][i] = r.share_of_debt;
    coverage[r.collateral_class][i] = r.coverage_ratio;
    if (r.is_estimated && (!estimatedThrough || r.date > estimatedThrough)) estimatedThrough = r.date;
  }
  return { dates, share, coverage, estimatedThrough };
}

export function nyfedData(d: StoryData): NyfedData {
  const dates = [...new Set(d.tables.nyfed_by_type.map((r) => r.date))].sort();
  const idx = new Map(dates.map((x, i) => [x, i]));
  const transition = emptyBy(LOAN_ORDER, () => new Array<number | null>(dates.length).fill(null));
  const balance = emptyBy(LOAN_ORDER, () => new Array<number | null>(dates.length).fill(null));
  for (const r of d.tables.nyfed_by_type) {
    const i = idx.get(r.date)!;
    if (!transition[r.loan_type]) continue;
    transition[r.loan_type][i] = r.transition_serious_pct;
    balance[r.loan_type][i] = r.balance_busd;
  }
  return { dates, transition, balance };
}

/** Value of a series at (or nearest before) an ISO date. */
export function at<T>(dates: string[], values: T[], iso: string): T | undefined {
  let best: number | undefined;
  for (let i = 0; i < dates.length; i++) if (dates[i] <= iso) best = i;
  return best === undefined ? undefined : values[best];
}

/** Headline numbers used by the hero, the "Now" chapter and copy tokens. */
export function headline(d: StoryData) {
  const ps = publicSeries(d);
  const n = ps.dates.length - 1;
  const ny = nyfedData(d);
  const m = ny.dates.length - 1;
  const totalAt = (i: number) =>
    LOAN_ORDER.reduce((s, k) => s + (ny.balance[k][i] ?? 0), 0);
  const nyTotal = m >= 0 ? totalAt(m) : null;
  const nyPrevTotal = m >= 1 ? totalAt(m - 1) : null;
  const mortNow = m >= 0 ? ny.balance.mortgage[m] : null;
  const mortPrev = m >= 1 ? ny.balance.mortgage[m - 1] : null;
  const fedDirect = ratchetData(d);
  const j = fedDirect.dates.length - 1;
  const total = (["mortgage", "consumer_credit"] as const).reduce(
    (s, t) => s + BUCKET_ORDER.reduce((s2, b) => s2 + fedDirect.nominal[t][b][j], 0), 0);
  const share = (b: RiskBucket) =>
    (fedDirect.nominal.mortgage[b][j] + fedDirect.nominal.consumer_credit[b][j]) / total;
  const coll = collateralData(d);
  const k = coll.dates.length - 1;

  return {
    latestDate: ps.dates[n],
    firstDate: ps.dates[0],
    publicShareLatest: ps.share[n],
    publicShareFirst: ps.share[0],
    publicShare2007: at(ps.dates, ps.share, "2007-12-31"),
    publicShare2011: at(ps.dates, ps.share, "2011-12-31"),
    scopeTotalLatest: ps.scopeTotal[n],
    fedMbsShareLatest: ps.fedMbsShare[n],
    nyLatestDate: m >= 0 ? ny.dates[m] : null,
    nyTotal,
    nyTotalChange: nyTotal !== null && nyPrevTotal !== null ? nyTotal - nyPrevTotal : null,
    nyMortgageChange: mortNow !== null && mortPrev !== null ? mortNow - mortPrev : null,
    shareFederalDirect: share("federal_direct"),
    shareGse: share("gse_agency"),
    sharePrivateSec: share("private_securitization"),
    shareUncollateralized: k >= 0 ? coll.share.uncollateralized[k] : null,
    homeCoverageLatest: k >= 0 ? coll.coverage.home_backed[k] : null,
  };
}
export type Headline = ReturnType<typeof headline>;

/** One step of the "Crisis by crisis" scroll-through: dates for the zoom and the public-share move. */
export interface CrisisStep {
  id: string;
  name: string;
  kind: Crisis["kind"];
  start: string;
  end: string | null;
  /** Short label and note from content/story.ts (keyed by start year). */
  label: string;
  note: string | null;
  /** Window for the zoom: t0 − 2 years to t0 + 4 years (quarter-end ISO dates). */
  min: string;
  max: string;
  /** Public share at t0 and at the end of the window (or the latest quarter, if sooner). */
  shareStart: number | null;
  shareEnd: number | null;
  endDate: string | null;
}

const shiftYearsIso = (iso: string, years: number) => `${Number(iso.slice(0, 4)) + years}${iso.slice(4)}`;

export function crisisSteps(d: StoryData, notes: Record<string, { label: string; text: string }>): CrisisStep[] {
  const ps = publicSeries(d);
  const latest = ps.dates[ps.dates.length - 1];
  return crises(d).map((c) => {
    const note = notes[c.start.slice(0, 4)];
    const max = shiftYearsIso(c.start, 4);
    const endDate = latest && latest < max ? latest : max;
    return {
      id: c.id,
      name: c.name,
      kind: c.kind,
      start: c.start,
      end: c.end,
      label: note?.label ?? c.start.slice(0, 4),
      note: note?.text ?? null,
      min: shiftYearsIso(c.start, -2),
      max,
      shareStart: at(ps.dates, ps.share, c.start) ?? null,
      shareEnd: at(ps.dates, ps.share, endDate) ?? null,
      endDate: endDate > c.start ? endDate : null,
    };
  });
}
