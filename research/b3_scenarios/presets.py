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
Preset "replay_2008_2012_proxy" (second family): realised net charge-off rates of all commercial banks,
2008Q1-2012Q4 (Fed charge-off release via FRED: CORSFRMACBS, CORCCACBS, COROCLACBS). Each quarter's loss is the
annualised rate / 400 (the release multiplies the quarterly ratio by 400); the quarterly path gives the timing
vector. Again a PROXY for non-bank holders; federal student loans absent.
Writes presets/dfast2026.json, presets/replay_2008_2012.json, results_dfast2026.json, results_replay_2008_2012.json.
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
REPLAY = {"mortgage": "CORSFRMACBS", "cards": "CORCCACBS", "other_consumer": "COROCLACBS"}
REPLAY_WINDOW = ("2008-01-01", "2012-10-01")
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


def build_replay(w_rev: float) -> dict:
    sys.path.insert(0, str(ROOT / "research" / "common"))
    import fred
    q = {k: fred.observations(sid)[REPLAY_WINDOW[0]:REPLAY_WINDOW[1]] / 400 for k, sid in REPLAY.items()}
    assert all(len(v) == 20 and v.notna().all() for v in q.values()), {k: len(v) for k, v in q.items()}
    cons = w_rev * q["cards"] + (1 - w_rev) * q["other_consumer"]
    classes = {}
    for name, path in [("mortgage", q["mortgage"]), ("consumer_other", cons)]:
        tot = float(path.sum())
        classes[name] = {"pd": tot, "lgd": 1.0, "timing": [float(x) / tot for x in path]}
    man = {m["tag"]: m for m in fred.manifest()}
    return {"source": "Federal Reserve charge-off rates, all commercial banks, via FRED (SA, annualised x400), 2008Q1-2012Q4",
            "label": "PROXY: realised bank net charge-off rates applied to all holders",
            "series": {k: {"id": sid, "sha256": man.get(f"obs_{sid}", {}).get("sha256"),
                           "retrieved_utc": man.get(f"obs_{sid}", {}).get("retrieved_utc")} for k, sid in REPLAY.items()},
            "cumulative_loss_pct": {"mortgage": 100 * classes["mortgage"]["pd"], "consumer_other": 100 * classes["consumer_other"]["pd"]},
            "presets": {"replay_2008_2012_proxy": {"classes": classes, "note": "federal student loans absent (no bank series)"}}}


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
    rp = build_replay(p["consumer_other_revolving_weight"])
    (HERE / "presets" / "replay_2008_2012.json").write_text(json.dumps(rp, indent=1) + "\n")
    out_r = {"as_of": ex["as_of"], "units": "USD millions", "label": rp["label"], "cumulative_loss_pct": rp["cumulative_loss_pct"]}
    for name, pr in rp["presets"].items():
        r = eng.run(ex["exposures"], pr["classes"])
        s = r["sum"]
        out_r[name] = {"public_musd": s["public"], "private_musd": s["private"], "total_musd": s["total"],
                       "public_share_of_losses": s["public"] / s["total"], "quarters": len(r["total"])}
    (HERE / "results_replay_2008_2012.json").write_text(json.dumps(out_r, indent=1) + "\n")
    print(json.dumps(out_r, indent=1))
    pub_hold = sum(e["balance"] for e in ex["exposures"] if e["side"] == "public")
    out["public_share_of_holdings"] = pub_hold / sum(e["balance"] for e in ex["exposures"])
    # Same holding share without federal student loans, which carry no loss in the main preset (skeptic mkt-s23)
    ex_nf = [e for e in ex["exposures"] if e["class"] != "student_federal"]
    out["public_share_of_holdings_ex_federal_student"] = (sum(e["balance"] for e in ex_nf if e["side"] == "public")
                                                          / sum(e["balance"] for e in ex_nf))
    (HERE / "results_dfast2026.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
