// Types for engine.mjs (copied from research/b3_scenarios by scripts/sync-b3.mjs; do not edit the copy).
export type LoanClass = "mortgage" | "student_federal" | "consumer_other";
export interface Exposure {
  class: LoanClass;
  holder: string;
  label?: string;
  side: "public" | "private";
  balance: number;
  transfer_eligible?: boolean;
}
export interface ClassParams { pd: number; lgd: number; timing?: number[] }
export type Classes = Partial<Record<LoanClass, ClassParams>>;
export interface Transfer { share: number; cap_musd: number }
export interface Result {
  public: number[];
  private: number[];
  total: number[];
  transferred: number[];
  sum: { public: number; private: number; total: number; transferred: number };
}
export const CLASSES: LoanClass[];
export function validate(exposures: Exposure[], classes: Classes, transfer?: Transfer | null): void;
export function run(exposures: Exposure[], classes: Classes, transfer?: Transfer | null): Result;
