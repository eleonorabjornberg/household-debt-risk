#!/usr/bin/env python3
"""B3 presets (Q-B3, decided by Eleonora 2026-11-04: both families, DFAST first, labelled a proxy).

    uv run --project pipeline python research/b3_scenarios/presets.py

Preset "dfast2026_proxy": the Federal Reserve's 2026 stress test, severely adverse scenario, Table 9 portfolio
loss rates (projected loan losses over the nine quarters 2026:Q1-2028:Q1 divided by average balances), for the
largest banks' portfolios. Applied to every holder's balance as a PROXY: GSE, FHA/VA and federal books are not
bank portfolios. Each loss rate is net of recoveries, so it enters the engine as pd = loss rate, lgd = 1, with
losses spread evenly over nine quarters (DFAST publishes the total, not the path: an assumption).

Federal student loans are not covered by DFAST: in the main preset they are left out (absent, not given a default);
the variant "dfast2026_proxy_with_student" applies DFAST's "other consumer" rate to them, labelled a weak proxy.
Writes presets/dfast2026.json and results_dfast2026.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_s = importlib.util.spec_from_file_location("engine", HERE / "engine.py")
eng = importlib.util.module_from_spec(_s)
_s.loader.exec_module(eng)

# Federal Reserve, 2026 Supervisory Stress Test Results (June 2026), Table 9, report page 21 (PDF page 27);
# checked against the rendered page. Percent of average balances, cumulative over nine quarters.
DFAST2026 = {"first_lien_mortgages": 1.5, "junior_liens_helocs": 3.2, "credit_cards": 17.1, "other_consumer": 7.3}
QUARTERS = 9
CC_TYPES = {"revolving": "FL153166100", "auto": "FL153166400", "student": "FL153166220", "other_nonrevolving": "FL153166205"}


def cc_mix(zip_path: Path) -> dict:
    """Z.1 consumer credit by type at the latest quarter, $M; private student = student - federal student."""
    sys.path.insert(0, str(ROOT / "validation"))
    import zparse
    ids = list(CC_TYPES.values()) + ["FL313066220", "FL153166000"]
    ser = zparse.load_z1_zip(zip_path, ids)
    ser = ser[0] if isinstance(ser, tuple) else ser
    last = max(ser["FL153166000"])
    v = {k: ser[i][last] for k, i in CC_TYPES.items()}
    fed = ser["FL313066220"][last]
    total = ser["FL153166000"][last]
    assert abs(sum(v.values()) - total) / total < 1e-6, "consumer-credit types do not sum to the total"
    return {"as_of": str(last), "revolving": v["revolving"], "nonrevolving_ex_federal_student":
            v["auto"] + v["other_nonrevolving"] + (v["student"] - fed), "federal_student": fed}


def build(mix: dict) -> dict:
    w_rev = mix["revolving"] / (mix["revolving"] + mix["nonrevolving_ex_federal_student"])
    cons = w_rev * DFAST2026["credit_cards"] + (1 - w_rev) * DFAST2026["other_consumer"]
    timing = [1 / QUARTERS] * QUARTERS
    main = {"mortgage": {"pd": DFAST2026["first_lien_mortgages"] / 100, "lgd": 1.0, "timing": timing},
            "consumer_other": {"pd": cons / 100, "lgd": 1.0, "timing": timing}}
    with_student = dict(main, student_federal={"pd": DFAST2026["other_consumer"] / 100, "lgd": 1.0, "timing": timing})
    return {"source": "Federal Reserve, 2026 Supervisory Stress Test Results, Table 9 (severely adverse, 2026:Q1-2028:Q1)",
            "label": "PROXY: bank portfolio loss rates applied to all holders",
            "consumer_other_revolving_weight": w_rev, "consumer_other_rate_pct": cons,
            "presets": {"dfast2026_proxy": {"classes": main, "note": "federal student loans absent (not covered by DFAST)"},
                        "dfast2026_proxy_with_student": {"classes": with_student,
                                                         "note": "federal student loans at DFAST 'other consumer' rate: weak proxy"}}}


def main() -> int:
    zip_path = ROOT / "data" / "validation" / "FRB_Z1_csv.zip"
    ex = json.loads((HERE / "exposures.json").read_text())
    mix = cc_mix(zip_path)
    assert mix["as_of"] == ex["as_of"], (mix["as_of"], ex["as_of"])
    p = build(mix)
    (HERE / "presets").mkdir(exist_ok=True)
    (HERE / "presets" / "dfast2026.json").write_text(json.dumps(p | {"cc_mix_musd": mix}, indent=1) + "\n")
    out = {"as_of": ex["as_of"], "units": "USD millions", "label": p["label"]}
    for name, pr in p["presets"].items():
        r = eng.run(ex["exposures"], pr["classes"])
        s = r["sum"]
        out[name] = {"public_musd": s["public"], "private_musd": s["private"], "total_musd": s["total"],
                     "public_share_of_losses": s["public"] / s["total"],
                     "by_class": {c: sum(e["balance"] * pr["classes"][c]["pd"] for e in ex["exposures"] if e["class"] == c)
                                  for c in pr["classes"]}}
    pub_hold = sum(e["balance"] for e in ex["exposures"] if e["side"] == "public")
    out["public_share_of_holdings"] = pub_hold / sum(e["balance"] for e in ex["exposures"])
    (HERE / "results_dfast2026.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
