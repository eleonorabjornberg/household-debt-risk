#!/usr/bin/env python3
"""PLAN task B4: policy-regime scenarios as ranges (METHOD.md). Computes the recession range from B3's two presets;
the GSE-release and student-loan scenarios wait for Eleonora's choices (Q-B4).

    uv run --project pipeline python research/b4_policy_scenarios/b4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B3 = HERE.parents[0] / "b3_scenarios"


def main() -> int:
    d = json.loads((B3 / "results_dfast2026.json").read_text())["dfast2026_proxy"]
    r = json.loads((B3 / "results_replay_2008_2012.json").read_text())["replay_2008_2012_proxy"]
    lo, hi = sorted([d, r], key=lambda x: x["total_musd"])
    res = {"recession": {"source": "B3 presets: dfast2026_proxy (lower), replay_2008_2012_proxy (upper); both proxies",
                         "total_musd": [lo["total_musd"], hi["total_musd"]],
                         "public_musd": [min(d["public_musd"], r["public_musd"]), max(d["public_musd"], r["public_musd"])],
                         "public_share_of_losses": [min(d["public_share_of_losses"], r["public_share_of_losses"]),
                                                    max(d["public_share_of_losses"], r["public_share_of_losses"])],
                         "transfer": "none (cap 0); A2 bounds not yet an input"},
           "gse_release": "pending Q-B4 (status 2026-11-04: in conservatorship, sources.md)",
           "student_loan_reform": "pending Q-B4 (status: P.L. 119-21 approved 2025-07-04, sources.md)"}
    assert res["recession"]["total_musd"][0] <= res["recession"]["total_musd"][1]
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
