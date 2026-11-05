#!/usr/bin/env python3
"""Write the E1 gold register rows (claims/tracks/infra.csv) from the E1-<id> checks in validation/results.json.

    uv run --project pipeline python evals/e1_sql_benchmark/build_register.py

One row per answerable question that has no existing register row: value = the raw-rebuild value
(`observed`) rounded to 1/100 of the question's scoring tolerance (whole numbers for counts), validation =
that check's status, check_id = E1-<id>, location = its line in gold_values.tsv (written here). Rows for other claims in the track file are kept. Re-run after validation/run.py; never edit
the values by hand.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QFILE = HERE / "questions.yaml"
RESULTS = ROOT / "validation" / "results.json"
TRACK = ROOT / "claims" / "tracks" / "infra.csv"
VALUES = HERE / "gold_values.tsv"  # one line per row: the register location that shows the value
SCHEMA = ["claim_id", "claim", "display", "value", "unit", "period", "locations", "computation", "series_ids",
          "vintage", "validation", "check_id", "notes"]
SERIES = {
    "public_share": "FL154104015 FL153165105 FL153166000 FL893065105 (+ public holder series)",
    "debt_by_risk_holder": "FL154104015 FL153165105 FL893065105 (+ bucket holder series)",
    "collateral_coverage": "FL153165105 FL155035015 FL153166400 FL155111005 FL153166100 FL153166220 FL153166205",
    "crisis_event_window": "as the metric's table (Z.1)",
    "nyfed_by_type": "NYFED_HHDC (HHD_C_Report_2026Q2.xlsx)",
    "dim_risk_bucket": "pipeline/series_catalog.yaml risk_buckets",
}


def _tables(check: dict) -> set[str]:
    if "combine" in check:
        return set().union(*(_tables(a) for a in check["combine"]["args"]))
    return {check["table"]}


def _dates(check: dict) -> list[str]:
    if "combine" in check:
        return sorted(set(sum((_dates(a) for a in check["combine"]["args"]), [])))
    return [check[k] for k in ("date", "from", "to", "start", "end") if k in check]


def _q(d: str) -> str:
    return f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"


def rounded(value: float, tolerance: float) -> str:
    if not tolerance:
        return str(int(round(value)))
    nd = max(0, math.ceil(-math.log10(tolerance / 100)))
    return f"{value:.{nd}f}"


def main() -> None:
    import yaml
    checks = {c["id"]: c for c in json.loads(RESULTS.read_text())["checks"]}
    vint = json.loads((ROOT / "web/public/data/meta.json").read_text())["vintages"]
    rows, values = [], ["# E1 gold values (raw rebuild, validation/e1_gold.py), written by build_register.py; do not edit"]
    doc = yaml.safe_load(QFILE.read_text())
    allq = sorted(doc["questions"] + doc.get("retired", []), key=lambda q: int(q["id"][1:]))  # stable tsv lines
    for q in allq:
        if q.get("refuse") or q.get("register"):
            continue
        c = checks[f"E1-{q['id']}"]
        tables = _tables(q["check"])
        dates = _dates(q["check"])
        val = rounded(float(c["observed"]), q["tolerance"])
        values.append(f"{q['id']}\t{val}")
        rows.append({
            "claim_id": f"e1_{q['id']}", "claim": f"E1 gold answer, {q['id']}: {q['question']}",
            "display": val, "value": val, "unit": q["unit"],
            "period": " ".join(_q(d) for d in dates) or "all quarters in the data",
            "locations": f"evals/e1_sql_benchmark/gold_values.tsv:{len(values)}",
            "computation": "validation/e1_gold.py rebuild from raw Z.1 zip / NY Fed workbook, evaluated with "
                           "evals/e1_sql_benchmark/spec.py; compared with the MCP snapshot",
            "series_ids": " ".join(SERIES[t] for t in sorted(tables)),
            "vintage": " ".join([f"z1:{vint['z1']}"] * any(t != "nyfed_by_type" for t in tables)
                                + [f"nyfed:{vint['nyfed']}"] * ("nyfed_by_type" in tables)),
            "validation": c["status"], "check_id": c["id"] if c["status"] in ("PASS", "FAIL") else "",
            "notes": (f"Retired from the E1 set {q['retired_on']} (e1-set-h3 replace, by {q['replaced_by']}); remove this row."
                      if q.get("retired_on") else
                      "E1 benchmark gold, not published copy. Draft question set awaiting Eleonora's approval."),
        })
    VALUES.write_text("\n".join(values) + "\n")
    main_reg = {r["claim_id"]: r for r in csv.DictReader((ROOT / "claims" / "register.csv").open())}
    changed = [r["claim_id"] for r in rows if r["claim_id"] in main_reg
               and (main_reg[r["claim_id"]]["value"], main_reg[r["claim_id"]]["validation"]) != (r["value"], r["validation"])]
    if changed:  # the coordinator owns register.csv: report, never overwrite
        raise SystemExit(f"register.csv rows differ from the rebuild (coordinator must update them): {changed}")
    rows = [r for r in rows if r["claim_id"] not in main_reg]  # already folded into register.csv on merge
    keep = []
    if TRACK.exists():
        keep = [r for r in csv.DictReader(TRACK.open()) if not r["claim_id"].startswith("e1_q")]
    if not keep and not rows:
        TRACK.unlink(missing_ok=True)
        print("all E1 rows are already in claims/register.csv and match; no track rows written")
        return
    with TRACK.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        w.writerows(keep + rows)
    print(f"{len(rows)} E1 rows written to {TRACK.relative_to(ROOT)} ({len(keep)} other rows kept)")


if __name__ == "__main__":
    main()
