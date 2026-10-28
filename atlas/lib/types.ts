// Row shapes of the Supabase `mart` views this site reads. Mirrors web/lib/types.ts.

export const BUCKETS = [
  "federal_direct",
  "gse_agency",
  "state_local",
  "banks_credit_unions",
  "private_securitization",
  "nonbank_other",
] as const;
export type RiskBucket = (typeof BUCKETS)[number];

export const DEBT_TYPES = ["mortgage", "consumer_credit"] as const;
export type DebtType = (typeof DEBT_TYPES)[number];

export interface DebtByRiskHolderRow {
  date: string;
  risk_bucket: RiskBucket;
  debt_type: DebtType;
  nominal_musd: number;
  real_musd: number | null;
}

export interface PublicShareRow {
  date: string;
  scope_total_musd: number;
  public_musd: number;
  public_share: number;
}

export interface DimCrisisRow {
  crisis_id: string;
  name: string;
  kind: "nber_recession" | "policy_shock";
  start_q: string;
  end_q: string | null;
}

/** Compact, client-ready series: one entry per quarter, values in real $ millions. */
export interface Series {
  dates: string[];
  /** real[q][bucketIndex][debtTypeIndex] */
  real: number[][][];
  /** nominal public share as published (used for the headline counter) */
  publicShare: number[];
  recessions: { id: string; name: string; start: string; end: string }[];
  source: "supabase" | "snapshot";
  cpiBase: string | null;
}
