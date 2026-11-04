#!/usr/bin/env python3
"""PLAN task B3: scenario engine, losses split public vs private (METHOD.md).

    uv run --project pipeline python research/b3_scenarios/engine.py            # exposures + fixed cases
    uv run --project pipeline python research/b3_scenarios/engine.py --params scenario.json

No preset scenario values are built in: parameters are inputs (METHOD.md, Q-B3). `--params` takes a JSON file
{"classes": {"mortgage": {"pd": .., "lgd": .., "timing": [..]}, ...}, "transfer": {"share": .., "cap_musd": ..}}.
Writes exposures.json (latest Z.1 balances by holder bucket) and fixtures/cases.json (fixed test cases for the
browser version, engine.mjs).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSES = ("mortgage", "student_federal", "consumer_other")
TOL = 1e-9


def validate(exposures: list[dict], classes: dict, transfer: dict | None = None) -> None:
    for e in exposures:
        if e["class"] not in CLASSES or e["side"] not in ("public", "private"):
            raise ValueError(f"bad exposure {e}")
        if not (e["balance"] >= 0 and math.isfinite(e["balance"])):
            raise ValueError(f"negative or non-finite balance {e}")
    for c, p in classes.items():
        if c not in CLASSES:
            raise ValueError(f"unknown class {c}")
        if not (0 <= p["pd"] <= 1 and 0 <= p["lgd"] <= 1):
            raise ValueError(f"pd/lgd outside [0,1] for {c}")
        w = p.get("timing", [1.0])
        if any(x < 0 for x in w) or abs(sum(w) - 1) > 1e-12:
            raise ValueError(f"timing for {c} must be non-negative and sum to 1")
    if transfer:
        if not (0 <= transfer.get("share", 0) <= 1) or transfer.get("cap_musd", 0) < 0:
            raise ValueError("transfer share must be in [0,1] and cap >= 0")


def run(exposures: list[dict], classes: dict, transfer: dict | None = None) -> dict:
    """Losses by quarter, public / private / total, $M. Classes absent from `classes` have zero loss."""
    validate(exposures, classes, transfer)
    n = max([len(p.get("timing", [1.0])) for p in classes.values()] + [1])
    pub, priv = [0.0] * n, [0.0] * n
    gse_pub = [0.0] * n            # public losses eligible for transfer (GSE and agency pools, mortgages)
    for e in exposures:
        p = classes.get(e["class"])
        if not p:
            continue
        loss = e["balance"] * p["pd"] * p["lgd"]
        for q, w in enumerate(p.get("timing", [1.0])):
            if e["side"] == "public":
                pub[q] += loss * w
                if e.get("transfer_eligible"):
                    gse_pub[q] += loss * w
            else:
                priv[q] += loss * w
    moved = [0.0] * n
    if transfer and transfer.get("share", 0) > 0 and transfer.get("cap_musd", 0) > 0:
        room = transfer["cap_musd"]
        for q in range(n):
            m = min(gse_pub[q] * transfer["share"], room)
            moved[q], room = m, room - m
            pub[q] -= m
            priv[q] += m
    total = [a + b for a, b in zip(pub, priv)]
    return {"public": pub, "private": priv, "total": total, "transferred": moved,
            "sum": {"public": sum(pub), "private": sum(priv), "total": sum(total), "transferred": sum(moved)}}


# ------------------------------------------------------------------ exposures from the latest Z.1
def exposures_from_z1(zip_path: Path) -> tuple[list[dict], str]:
    import yaml
    sys.path.insert(0, str(ROOT / "validation"))
    import zparse
    cat = yaml.safe_load((ROOT / "pipeline" / "series_catalog.yaml").read_text())
    rows = [s for s in cat["series"] if s["source"] == "z1"]
    public = {k for k, v in cat["risk_buckets"].items() if v["public"]}
    labels = {k: v["label"] for k, v in cat["risk_buckets"].items()}
    mh = [s for s in rows if s["role"] == "mortgage_holder"]
    ch = [s for s in rows if s["role"] == "cc_holder"]
    ids = sorted({"FL153165105", "FL893065105", "FL153166000"} | {s["id"] for s in mh + ch})
    ser = zparse.load_z1_zip(zip_path, ids)
    ser = ser[0] if isinstance(ser, tuple) else ser
    last = max(ser["FL153165105"])
    val = lambda i: ser[i].get(last, 0.0) or 0.0
    a = val("FL153165105") / val("FL893065105")
    agg: dict[tuple, float] = {}
    for s in mh:
        k = ("mortgage", s["risk_bucket"])
        agg[k] = agg.get(k, 0.0) + val(s["id"]) * a
    for s in ch:
        cls = "student_federal" if s["id"] == "FL313066220" else "consumer_other"
        k = (cls, s["risk_bucket"])
        agg[k] = agg.get(k, 0.0) + val(s["id"])
    ex = [{"class": c, "holder": b, "label": labels[b], "side": "public" if b in public else "private",
           "balance": v, "transfer_eligible": c == "mortgage" and b == "gse_agency"} for (c, b), v in sorted(agg.items())]
    total = val("FL153165105") + val("FL153166000")
    assert abs(sum(e["balance"] for e in ex) - total) / total < 1e-9, "exposures do not sum to the scope total"
    return ex, str(last)


# ------------------------------------------------------------------ fixed cases for engine.mjs
def fixed_cases() -> list[dict]:
    ex = [
        {"class": "mortgage", "holder": "gse_agency", "side": "public", "balance": 8000.0, "transfer_eligible": True},
        {"class": "mortgage", "holder": "federal_direct", "side": "public", "balance": 150.0},
        {"class": "mortgage", "holder": "banks_credit_unions", "side": "private", "balance": 3000.0},
        {"class": "student_federal", "holder": "federal_direct", "side": "public", "balance": 1500.0},
        {"class": "consumer_other", "holder": "banks_credit_unions", "side": "private", "balance": 2500.0},
    ]
    cases = [
        ("zero default", {"mortgage": {"pd": 0.0, "lgd": 0.4}}, None),
        ("mortgage only, one quarter", {"mortgage": {"pd": 0.05, "lgd": 0.3}}, None),
        ("three classes, timing", {"mortgage": {"pd": 0.04, "lgd": 0.35, "timing": [0.1, 0.3, 0.4, 0.2]},
                                   "student_federal": {"pd": 0.2, "lgd": 0.5, "timing": [0.25, 0.25, 0.25, 0.25]},
                                   "consumer_other": {"pd": 0.08, "lgd": 0.8, "timing": [0.5, 0.5]}}, None),
        ("transfer capped", {"mortgage": {"pd": 0.04, "lgd": 0.35, "timing": [0.5, 0.5]}}, {"share": 0.6, "cap_musd": 40.0}),
        ("transfer uncapped", {"mortgage": {"pd": 0.04, "lgd": 0.35, "timing": [0.5, 0.5]}}, {"share": 0.6, "cap_musd": 1e9}),
    ]
    return [{"name": n, "exposures": ex, "classes": c, "transfer": t, "expected": run(ex, c, t)} for n, c, t in cases]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    ap.add_argument("--params", type=Path, help="scenario JSON (no presets are built in)")
    a = ap.parse_args(argv)
    (HERE / "fixtures").mkdir(exist_ok=True)
    (HERE / "fixtures" / "cases.json").write_text(json.dumps(fixed_cases(), indent=1) + "\n")
    if a.z1_zip.exists():
        ex, q = exposures_from_z1(a.z1_zip)
        (HERE / "exposures.json").write_text(json.dumps({"as_of": q, "z1_release": "2026-09-11", "units": "USD millions",
                                                         "exposures": ex}, indent=1) + "\n")
        if a.params:
            p = json.loads(a.params.read_text())
            print(json.dumps(run(ex, p["classes"], p.get("transfer"))["sum"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
