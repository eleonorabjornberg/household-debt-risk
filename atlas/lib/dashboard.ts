// Numbers for the /dashboard tab (PLAN F7, docket 54: market reader, Core scope, merged with Findings).
// Pure functions over the mart snapshots in public/data, so the page and lib/dashboard.test.ts compute
// the same values; the test also checks each tile against its row in claims/register.csv.

export const LOAN_TYPES = ["mortgage", "heloc", "auto", "credit_card", "student", "other"] as const;
export type LoanType = (typeof LOAN_TYPES)[number];
export const LOAN_LABEL: Record<LoanType, string> = {
  mortgage: "Mortgage",
  heloc: "Home equity line",
  auto: "Auto",
  credit_card: "Credit card",
  student: "Student",
  other: "Other",
};

export interface PublicShareSnap { date: string; scope_total_musd: number; public_share: number }
export interface HolderSnap { date: string; risk_bucket: string; debt_type: string; nominal_musd: number }
export interface CoverageSnap { date: string; collateral_class: string; coverage_ratio: number | null }
export interface NyfedSnap { date: string; loan_type: string; balance_busd: number | null; transition_serious_pct: number | null }
export interface BucketSnap { risk_bucket: string; label: string; is_public: boolean; sort_order: number }

/** A tile value: the latest quarter, the change on the quarter and the change on the year (same units). */
export interface Move {
  date: string;
  value: number;
  dq: number | null;
  dy: number | null;
}

/** Latest value of a dated series, with its change on one and four quarters earlier (null when missing). */
export function move(rows: { date: string; v: number | null }[]): Move {
  const s = rows.filter((r): r is { date: string; v: number } => r.v !== null && Number.isFinite(r.v))
    .sort((a, b) => a.date.localeCompare(b.date));
  if (s.length === 0) throw new Error("move: empty series");
  const last = s[s.length - 1];
  const at = (k: number) => {
    const target = shiftQuarter(last.date, -k);
    const r = s.find((x) => x.date === target);
    return r ? last.v - r.v : null;
  };
  return { date: last.date, value: last.v, dq: at(1), dy: at(4) };
}

/** "2026-06-30" shifted by k quarters, as a quarter-end ISO date. */
export function shiftQuarter(date: string, k: number): string {
  const y = Number(date.slice(0, 4));
  const q = Math.ceil(Number(date.slice(5, 7)) / 3) - 1 + k;
  const yy = y + Math.floor(q / 4);
  const qq = ((q % 4) + 4) % 4;
  return `${yy}-${["03-31", "06-30", "09-30", "12-31"][qq]}`;
}

export interface Tiles {
  scope: Move;      // $ millions, nominal
  publicShare: Move; // share 0-1
  homeCoverage: Move; // ratio
  transitions: Record<LoanType, Move>; // % of balance, annualized
}

export function computeTiles(d: { share: PublicShareSnap[]; coverage: CoverageSnap[]; nyfed: NyfedSnap[] }): Tiles {
  const transitions = {} as Record<LoanType, Move>;
  for (const t of LOAN_TYPES) {
    transitions[t] = move(d.nyfed.filter((r) => r.loan_type === t).map((r) => ({ date: r.date, v: r.transition_serious_pct })));
  }
  return {
    scope: move(d.share.map((r) => ({ date: r.date, v: r.scope_total_musd }))),
    publicShare: move(d.share.map((r) => ({ date: r.date, v: r.public_share }))),
    homeCoverage: move(d.coverage.filter((r) => r.collateral_class === "home_backed").map((r) => ({ date: r.date, v: r.coverage_ratio }))),
    transitions,
  };
}

/** Holder mix: one row per quarter, nominal $ millions per bucket, for mortgages, consumer credit or both. */
export interface HolderMix {
  dates: string[];
  buckets: { key: string; label: string; isPublic: boolean }[];
  /** values[debtView][bucketIndex][quarterIndex] */
  values: Record<"all" | "mortgage" | "consumer_credit", number[][]>;
}

export function holderMix(rows: HolderSnap[], dim: BucketSnap[]): HolderMix {
  const buckets = [...dim].sort((a, b) => a.sort_order - b.sort_order)
    .map((b) => ({ key: b.risk_bucket, label: b.label, isPublic: b.is_public }));
  const dates = [...new Set(rows.map((r) => r.date))].sort();
  const di = new Map(dates.map((d, i) => [d, i]));
  const bi = new Map(buckets.map((b, i) => [b.key, i]));
  const zero = () => buckets.map(() => dates.map(() => 0));
  const values = { all: zero(), mortgage: zero(), consumer_credit: zero() };
  for (const r of rows) {
    const b = bi.get(r.risk_bucket);
    const q = di.get(r.date);
    if (b === undefined || q === undefined || !Number.isFinite(r.nominal_musd)) continue;
    values.all[b][q] += r.nominal_musd;
    if (r.debt_type === "mortgage" || r.debt_type === "consumer_credit") values[r.debt_type][b][q] += r.nominal_musd;
  }
  return { dates, buckets, values };
}

/** NY Fed by loan type: one array per type over the shared quarter list (null where not reported). */
export interface LoanPanel {
  dates: string[];
  transition: Record<LoanType, (number | null)[]>;
  balance: Record<LoanType, (number | null)[]>;
}

export function loanPanel(rows: NyfedSnap[]): LoanPanel {
  const dates = [...new Set(rows.map((r) => r.date))].sort();
  const di = new Map(dates.map((d, i) => [d, i]));
  const transition = {} as Record<LoanType, (number | null)[]>;
  const balance = {} as Record<LoanType, (number | null)[]>;
  for (const t of LOAN_TYPES) {
    transition[t] = dates.map(() => null);
    balance[t] = dates.map(() => null);
  }
  for (const r of rows) {
    const t = r.loan_type as LoanType;
    const q = di.get(r.date);
    if (!(t in transition) || q === undefined) continue;
    transition[t][q] = r.transition_serious_pct;
    balance[t][q] = r.balance_busd;
  }
  return { dates, transition, balance };
}
