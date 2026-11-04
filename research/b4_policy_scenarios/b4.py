#!/usr/bin/env python3
"""PLAN task B4: policy-regime scenarios as ranges (METHOD.md).

    uv run --project pipeline python research/b4_policy_scenarios/b4.py [--z1-zip data/validation/FRB_Z1_csv.zip]

Recession: the range between B3's two presets. GSE release (Eleonora, card b4-gse, option (a)): 0, 25, 50, 75 and
100% of the losses on Fannie Mae's and Freddie Mac's books (portfolio + pools) turn private, under each B3 preset;
Ginnie Mae (and FmHA) pools, the FHLBs and the other GSEs stay public. The split of B3's "GSEs & agency pools"
mortgage exposure uses the finer Z.1 series of the same release (2026-09-11), household-apportioned like B3.
The student-loan scenario waits for a sourced estimate (card b4-student, option (c)).
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B3 = HERE.parents[0] / "b3_scenarios"
_s = importlib.util.spec_from_file_location("b3engine", B3 / "engine.py")
eng = importlib.util.module_from_spec(_s)
_s.loader.exec_module(eng)

# Z.1 holder series (asset side, $M), as in research/a1_gfc_decomposition/decompose.py PUBLIC_MORT
RELEASED = {"Fannie Mae (portfolio + pools)": ["FL403065110", "FL413065143"],
            "Freddie Mac (portfolio + pools)": ["FL403065120", "FL413065123"]}
STAY_PUBLIC = {"Ginnie Mae and FmHA pools": ["FL413065110", "FL413065133"],
               "FHLBs and other GSEs": ["FL403065105", "-FL403065110", "-FL403065120"]}   # GSE sector total less Fannie, Freddie
SHARES = [0.0, 0.25, 0.5, 0.75, 1.0]
PRESETS = {"dfast2026_proxy": "presets/dfast2026.json", "replay_2008_2012_proxy": "presets/replay_2008_2012.json"}


def gse_split(zip_path: Path) -> dict:
    """Household-apportioned balances ($M) of the released book and the parts that stay public, at B3's quarter."""
    sys.path.insert(0, str(ROOT / "validation"))
    import zparse
    ids = sorted({c.lstrip("-") for v in list(RELEASED.values()) + list(STAY_PUBLIC.values()) for c in v}
                 | {"FL153165105", "FL893065105", "FL403065105", "FL413065105"})
    ser = zparse.load_z1_zip(zip_path, ids)
    ser = ser[0] if isinstance(ser, tuple) else ser
    last = max(ser["FL153165105"])
    v = lambda i: ser[i].get(last, 0.0) or 0.0
    a = v("FL153165105") / v("FL893065105")
    f = lambda codes: a * sum(-v(c[1:]) if c.startswith("-") else v(c) for c in codes)
    out = {"as_of": str(last), "apportion": a,
           "released": {k: f(c) for k, c in RELEASED.items()}, "stay_public": {k: f(c) for k, c in STAY_PUBLIC.items()}}
    out["released_total"] = sum(out["released"].values())
    out["bucket_total"] = a * (v("FL403065105") + v("FL413065105"))
    assert abs(out["released_total"] + sum(out["stay_public"].values()) - out["bucket_total"]) < 1e-6
    return out


def gse_release(split: dict) -> dict:
    ex0 = json.loads((B3 / "exposures.json").read_text())
    assert ex0["as_of"] == split["as_of"], (ex0["as_of"], split["as_of"])
    gse = [e for e in ex0["exposures"] if e["class"] == "mortgage" and e["holder"] == "gse_agency"]
    assert len(gse) == 1 and abs(gse[0]["balance"] - split["bucket_total"]) < 1e-3, "B3 bucket != Z.1 split"
    rel = split["released_total"]
    res = {}
    for name, path in PRESETS.items():
        classes = json.loads((B3 / path).read_text())["presets"][name]["classes"]
        base = eng.run(ex0["exposures"], classes)["sum"]
        grid = []
        for x in SHARES:
            ex = [copy.deepcopy(e) for e in ex0["exposures"] if e is not gse[0] and not (e["class"] == "mortgage" and e["holder"] == "gse_agency")]
            ex += [dict(gse[0], holder="gse_agency_stays_public", balance=gse[0]["balance"] - rel),
                   dict(gse[0], holder="fannie_freddie_public", balance=rel * (1 - x)),
                   dict(gse[0], holder="fannie_freddie_private", side="private", balance=rel * x, transfer_eligible=False)]
            s = eng.run(ex, classes)["sum"]
            assert abs(s["total"] - base["total"]) < 1e-6
            grid.append({"share_private": x, "public_musd": s["public"], "private_musd": s["private"],
                         "total_musd": s["total"], "public_share_of_losses": s["public"] / s["total"]})
        assert abs(grid[0]["public_musd"] - base["public"]) < 1e-6
        res[name] = grid
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", type=Path, default=ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    a = ap.parse_args(argv)
    d = json.loads((B3 / "results_dfast2026.json").read_text())["dfast2026_proxy"]
    r = json.loads((B3 / "results_replay_2008_2012.json").read_text())["replay_2008_2012_proxy"]
    lo, hi = sorted([d, r], key=lambda x: x["total_musd"])
    res = {"recession": {"source": "B3 presets: dfast2026_proxy (lower), replay_2008_2012_proxy (upper); both proxies",
                         "total_musd": [lo["total_musd"], hi["total_musd"]],
                         "public_musd": [min(d["public_musd"], r["public_musd"]), max(d["public_musd"], r["public_musd"])],
                         "public_share_of_losses": [min(d["public_share_of_losses"], r["public_share_of_losses"]),
                                                    max(d["public_share_of_losses"], r["public_share_of_losses"])],
                         "transfer": "none (cap 0); A2 bounds not yet an input"},
           "gse_release": None,
           "student_loan_reform": "pending Q-B4 (status: P.L. 119-21 approved 2025-07-04, sources.md)"}
    assert res["recession"]["total_musd"][0] <= res["recession"]["total_musd"][1]
    split = gse_split(a.z1_zip)
    grid = gse_release(split)
    res["gse_release"] = {
        "decision": "Eleonora, card b4-gse (a), 2026-11-04: 0-100% of GSE-book losses turn private, points at 25/50/75%",
        "status": "in conservatorship per FHFA's page retrieved 2026-11-04 (sources.md)",
        "released_book": "Fannie Mae and Freddie Mac, portfolio + pools (Z.1 FL403065110+FL413065143, FL403065120+FL413065123)",
        "stays_public": "Ginnie Mae and FmHA pools (FL413065110+FL413065133); FHLBs and other GSEs (FL403065105 less Fannie and Freddie)",
        "balances_musd": {"as_of": split["as_of"], "released_total": split["released_total"], **split["released"],
                          **split["stay_public"], "bucket_total": split["bucket_total"]},
        "transfer": "none (cap 0), as the recession range",
        "by_preset": grid,
        "public_share_of_losses_range": [min(g["public_share_of_losses"] for v in grid.values() for g in v),
                                         max(g["public_share_of_losses"] for v in grid.values() for g in v)],
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
