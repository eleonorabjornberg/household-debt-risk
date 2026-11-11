#!/usr/bin/env python3
"""B4 student-loan scenario, volume side (Eleonora, docket 56 b4-student-proxy-map (b), 2026-11-11): ED's estimate of
federal student-loan disbursements before and after the Working Families Tax Cuts Act (P.L. 119-21), 2026-2035, from the
final rule's Regulatory Impact Analysis, 91 FR 23768, Table 3.1 (FR page 23855).

    uv run --project pipeline python research/b4_policy_scenarios/ed_volume.py

Input: fixtures/ed_rule_table_3_1.txt, the table's verbatim text layer (source PDF and hash in sources.md). Output:
ed_volume.json. Checks: the three non-consolidated rows reproduce ED's printed difference, and the graduate and Parent PLUS
falls reproduce the rule's own text ("$171 billion", "$49 billion") to the stated rounding. Nothing here enters the B3
loss engine (her ruling: no loss-engine change until she reviews it).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "ed_rule_table_3_1.txt"
OUT = HERE / "ed_volume.json"
ROWS = {"Undergrad": "undergrad", "Grad Stafford & PLUS": "grad_stafford_plus", "Parent PLUS": "parent_plus",
        "Consolidation": "consolidation"}
NONCONS = ("undergrad", "grad_stafford_plus", "parent_plus")


def num(s: str) -> float:
    s = s.replace("$", "").replace(",", "").replace("¥", "-").strip()
    return float(s)


def parse(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        for label, key in ROWS.items():
            if line.startswith(label + " ..") and key not in out:
                f = [x for x in re.split(r"\s{2,}", line[len(label) + 3:].strip()) if x]
                if len(f) != 4:
                    raise ValueError(f"row {label!r}: expected 4 numbers, got {f}")
                out[key] = {"loans_pre_m": num(f[0]), "loans_post_m": num(f[1]),
                            "disbursed_pre_musd": num(f[2]), "disbursed_post_musd": num(f[3])}
        if line.startswith("Non-Consolidated Loan Difference .."):
            f = [x for x in re.split(r"\s{2,}", line.split("..", 1)[1].strip()) if x and x != ".."]
            out["noncons_difference"] = {"loans_m": num(f[0]), "disbursed_musd": num(f[1])}
    missing = set(ROWS.values()) - set(out) | ({"noncons_difference"} - set(out))
    if missing:
        raise ValueError(f"rows not found: {sorted(missing)}")
    return out


def compute(t: dict) -> dict:
    pre = sum(t[k]["disbursed_pre_musd"] for k in NONCONS)
    post = sum(t[k]["disbursed_post_musd"] for k in NONCONS)
    if abs((post - pre) - t["noncons_difference"]["disbursed_musd"]) > 0.5:
        raise ValueError(f"rows give {post - pre}, ED prints {t['noncons_difference']['disbursed_musd']}")
    loans = sum(t[k]["loans_post_m"] - t[k]["loans_pre_m"] for k in NONCONS)
    # each row is printed to 0.1 million, so three rows can sum up to 0.15 away from the printed total (rows give -10.0, ED
    # prints -9.9); the loan counts are not published by B4, only checked
    if abs(loans - t["noncons_difference"]["loans_m"]) > 0.151:
        raise ValueError(f"loan counts give {loans}, ED prints {t['noncons_difference']['loans_m']}")
    fall = {k: t[k]["disbursed_pre_musd"] - t[k]["disbursed_post_musd"] for k in ROWS.values()}
    # the rule's text: "Graduate Stafford and Graduate PLUS Loans ($171 billion) and Parent PLUS Loans ($49 billion)"
    if round(fall["grad_stafford_plus"] / 1e3) != 171 or round(fall["parent_plus"] / 1e3) != 49:
        raise ValueError(f"falls {fall} do not match the rule's text")
    return {
        "label": "ED estimate (projection) of the reduction in FEDERAL student-loan disbursements under P.L. 119-21; "
                 "not an estimate of lending moving to private lenders, not a loss",
        "source": "ED final rule, 91 FR 23768 (2026-05-01), RIA Table 3.1, FR page 23855",
        "period": "2026-2035 (as printed; the table does not say fiscal or award years)",
        "units": "loans in millions, disbursements in USD millions",
        "table": t,
        "noncons_pre_musd": pre, "noncons_post_musd": post, "noncons_fall_musd": pre - post,
        "noncons_fall_share": (pre - post) / pre,
        "fall_musd": fall,
    }


def main() -> int:
    res = compute(parse(FIXTURE.read_text()))
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(f"{OUT.name}: non-consolidated {res['noncons_pre_musd']:.0f} -> {res['noncons_post_musd']:.0f} $M "
          f"(fall {res['noncons_fall_musd']:.0f}, {100 * res['noncons_fall_share']:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
