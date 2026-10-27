// Row types mirror the `mart` tables (and two `core` dims) in
// supabase/migrations/20261027000000_init.sql. Column names are the DB names, dates are ISO
// strings (quarter-end), numerics are JS numbers. Keep this file in sync with the migration.

export type RiskBucket =
  | "federal_direct"
  | "gse_agency"
  | "state_local"
  | "banks_credit_unions"
  | "private_securitization"
  | "nonbank_other";

export type DebtType = "mortgage" | "consumer_credit";

export type CollateralClass = "home_backed" | "vehicle_backed" | "uncollateralized" | "other_nonrevolving";

export type LoanType = "mortgage" | "heloc" | "auto" | "credit_card" | "student" | "other";

export interface DebtByRiskHolderRow {
  date: string;
  risk_bucket: RiskBucket;
  debt_type: DebtType;
  nominal_musd: number;
  real_musd: number | null;
  share_of_total: number;
  pct_of_dpi: number | null;
}

export interface PublicShareRow {
  date: string;
  scope_total_musd: number;
  public_musd: number;
  public_share: number;
  public_share_mortgage: number;
  public_share_cc: number;
  fed_mbs_musd: number | null;
  fed_mbs_share_of_scope: number | null;
}

export interface CollateralCoverageRow {
  date: string;
  collateral_class: CollateralClass;
  debt_musd: number;
  collateral_value_musd: number | null;
  coverage_ratio: number | null;
  share_of_debt: number;
  is_estimated: boolean;
}

export interface CrisisEventWindowRow {
  crisis_id: string;
  metric: string;
  q_offset: number;
  date: string;
  value: number;
  value_at_t0: number;
  delta_from_t0: number;
}

export interface NyfedByTypeRow {
  date: string;
  loan_type: LoanType;
  balance_busd: number | null;
  transition_serious_pct: number | null;
}

export interface DimCrisisRow {
  crisis_id: string;
  name: string;
  kind: "nber_recession" | "policy_shock";
  start_q: string;
  end_q: string | null;
  notes: string | null;
}

export interface DimRiskBucketRow {
  risk_bucket: RiskBucket;
  label: string;
  is_public: boolean;
  sort_order: number;
}

export interface TableMap {
  debt_by_risk_holder: DebtByRiskHolderRow;
  public_share: PublicShareRow;
  collateral_coverage: CollateralCoverageRow;
  crisis_event_window: CrisisEventWindowRow;
  nyfed_by_type: NyfedByTypeRow;
  dim_crisis: DimCrisisRow;
  dim_risk_bucket: DimRiskBucketRow;
}

export type TableName = keyof TableMap;

/** Where a table's rows came from, so the page can say so. */
export type DataSource = "supabase" | "snapshot" | "fixture";
