#!/usr/bin/env python3
"""Compare the A4 Python results with R strucchange (crosscheck.R) under the pre-registered tolerance (b):
break dates and SSR exact (relative difference < 1e-6), test statistics within 5%, interval bounds within one quarter.

    uv run --project pipeline python research/a4_breaks/rcheck/compare.py   (after Rscript research/a4_breaks/rcheck/crosscheck.R)
"""
import json
from pathlib import Path

import pandas as pd

H = Path(__file__).resolve().parent
py = json.loads((H / "python_side.json").read_text())
r = dict(l.split("\t", 1) for l in (H / "r_side.tsv").read_text().splitlines())
q = list(pd.read_csv(H / "dy_total.csv")["quarter"])
out = {"dates_equal": all(r[f"breaks_{m}"].split(",") == py["dp"][str(m)]["breaks"] for m in range(1, 6)),
       "ssr_max_rel_diff": max(abs(float(r[f"ssr_{m}"]) - py["dp"][str(m)]["ssr"]) / py["dp"][str(m)]["ssr"] for m in range(0, 6)),
       "bic_choice_r": min(range(0, 6), key=lambda m: float(r[f"bic_{m}"])),
       "supF_hac_r_homogeneous": float(r["supF_hac_homogeneous"]), "supF_hac_py_heterogeneous": py["chow_wald_hetero_max"],
       "supF_argmax_r": r["supF_hac_argmax"], "supF_argmax_py": py["chow_wald_hetero_argmax"]}
out["supF_rel_diff"] = abs(out["supF_hac_r_homogeneous"] - out["supF_hac_py_heterogeneous"]) / out["supF_hac_r_homogeneous"]
lo, bk, hi = (int(x) for x in r["ci_1break_kernHAC_obs"].split(","))
# R: breakpoint b = last observation of the first regime (1-based), so the new regime starts at q[b] (0-based)
out["ci_r"] = ["before sample start" if lo < 1 else q[lo], q[bk], q[hi]]
out["ci_py"] = py["ci_1break"][0]
out["ci_upper_diff_quarters"] = q.index(q[hi]) - q.index(py["ci_1break"][0][1])
out["within_tolerance"] = bool(out["dates_equal"] and out["ssr_max_rel_diff"] < 1e-6 and out["supF_rel_diff"] <= 0.05
                               and abs(out["ci_upper_diff_quarters"]) <= 1 and lo < 1)
out["not_cross_checked"] = "sequential sup-F(l+1|l), UDmax/WDmax and the simulated critical values (not in strucchange)"
(H / "comparison.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
