#!/usr/bin/env python3
"""B4 student-loan scenario, budget-side PROXY (card cbo-repo-55 (b), 2026-11-11; METHOD.md section 3b).

    uv run --project pipeline python research/b4_policy_scenarios/student_proxy.py

Reads cbo_direct_loan_outlays.csv (from cbo_extract.py) and writes student_proxy.json: the Direct Loan program account's
projected outlays in CBO's January 2025 baseline (last before P.L. 119-21) and February 2026 baseline (first after),
summed over the fiscal years both cover, and their difference. These outlays are the federal subsidy cost of the loans
(2 U.S.C. 661a), not loan volume, and the change between baselines includes every other revision CBO made: a labelled
proxy, not a CBO estimate of the law's effect or of any shift to private lending. Nothing here enters the B3 engine.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IN = HERE / "cbo_direct_loan_outlays.csv"
OUT = HERE / "student_proxy.json"
BEFORE, AFTER, CONTEXT = "2025-01", "2026-02", "2024-06"


def compute(rows: list[dict]) -> dict:
    path = {}
    for r in rows:
        path.setdefault(r["baseline"], {})[int(r["fiscal_year"])] = float(r["outlays_musd"])
    common = sorted(set(path[BEFORE]) & set(path[AFTER]))
    if common != list(range(common[0], common[-1] + 1)):
        raise ValueError(f"common fiscal years are not contiguous: {common}")
    before = sum(path[BEFORE][y] for y in common)
    after = sum(path[AFTER][y] for y in common)
    return {
        "label": "PROXY: change in CBO's projected subsidy-cost outlays of the Direct Loan program account between "
                 "baselines; not a CBO estimate of P.L. 119-21's effect, not lending volume, not a shift to private lenders",
        "account": "091-0243-0-1-502 Federal Direct Student Loan Program Account (Mandatory)",
        "units": "USD millions, federal fiscal years",
        "baseline_before": BEFORE, "baseline_after": AFTER, "baseline_context": CONTEXT,
        "fy_first": common[0], "fy_last": common[-1], "n_years": len(common),
        "sum_before_musd": before, "sum_after_musd": after,
        "change_musd": after - before, "change_share": (after - before) / before,
        "path_musd": {b: {str(y): v for y, v in sorted(p.items())} for b, p in sorted(path.items())},
    }


def main() -> int:
    with open(IN, newline="") as f:
        res = compute(list(csv.DictReader(f)))
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(f"{OUT.name}: FY{res['fy_first']}-FY{res['fy_last']} {res['sum_before_musd']:.0f} -> {res['sum_after_musd']:.0f} "
          f"($M), change {res['change_musd']:.0f} ({100 * res['change_share']:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
