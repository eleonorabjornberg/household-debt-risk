#!/usr/bin/env python3
"""PLAN task C1b: C1's accounting bridge plus Freddie Mac's monthly growth on the GSE + pool cells (Freddie only).

    uv run --project pipeline python research/c1b_nowcast/nowcast_c1b.py              # development sample
    uv run --project pipeline python research/c1b_nowcast/nowcast_c1b.py --dry-run    # holdout code on a dev split
    uv run --project pipeline python research/c1b_nowcast/nowcast_c1b.py --holdout --approval <commit>   # SEALED

Pre-registration: docs/decisions/c1b-prereg.md (choices filled in commit 0acbde6, before this script existed).
Inputs: C1's inputs (research/c1_nowcast; this script imports C1's nowcast.py unchanged, so C1's frozen code is the
baseline) and freddie_mvs_reports.csv / freddie_mvs_rows.csv (freddie_mvs.py). Real-time sample only.

Development outputs next to this file: nowcasts_dev.csv, scores_dev.csv, tests_dev.csv, results_dev.json.
The holdout path is gated exactly like research/c2_forecast/holdout_run.py: an Eleonora "unseal ... holdout" row in
PLAN.md at --approval, a clean tree, and every file in FREEZE.json unchanged. It writes holdout_results.json.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "FREEZE.json"
PREREG_COMMIT = "0acbde6"
DRY_SPLIT = "2019Q2"          # dry run: targets after this play the holdout


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


nc = _load("c1_nowcast", ROOT / "research" / "c1_nowcast" / "nowcast.py")
GSE_CELLS = ("mort_gse", "mort_pools")


# ------------------------------------------------------------------ Freddie at instant t
class Freddie:
    def __init__(self, reports: pd.DataFrame | None = None, rows: pd.DataFrame | None = None):
        self.rep = reports if reports is not None else pd.read_csv(HERE / "freddie_mvs_reports.csv")
        self.rows = rows if rows is not None else pd.read_csv(HERE / "freddie_mvs_rows.csv")
        self.rep = self.rep.assign(pub_date=pd.to_datetime(self.rep["pub_date"])).sort_values("report_month")
        self._by = {r: g.set_index("row_month")["ending_balance_usd_m"] for r, g in self.rows.groupby("report_month")}

    def at(self, t, T: str, q: str) -> dict:
        """Latest report published strictly before t; Freddie's level at the end of T and its growth to the latest
        month <= end of q, both from that one report (prereg: growth from a single report)."""
        t = pd.Timestamp(t)
        known = self.rep[self.rep["pub_date"] < t]
        if known.empty:
            raise ValueError(f"no Freddie report published before {t.date()}")
        r = known.iloc[-1]
        nc.guard([r["pub_date"] + pd.Timedelta(days=1)], t)   # published strictly before t
        s = self._by[r["report_month"]]
        base_m = str(pd.Period(T, "Q").asfreq("M", "end"))
        end_m = str(pd.Period(q, "Q").asfreq("M", "end"))
        if base_m not in s.index:
            raise ValueError(f"report {r['report_month']} has no row for {base_m}")
        later = s[(s.index > base_m) & (s.index <= end_m)]
        m_star = later.index.max() if len(later) else base_m
        return {"report": r["report_month"], "report_pub_date": r["pub_date"].date().isoformat(),
                "report_label": r["content_label"] if isinstance(r["content_label"], str) else "",
                "F_T": float(s[base_m]), "g": float(s[m_star] / s[base_m]), "latest_month": m_star}


def c1b_share(cells_T: dict, g: dict, fred: dict, mapping: dict) -> tuple[float, float]:
    """C1's bridge after scaling the combined GSE + pool cell by 1 + s (g_F - 1), s = min(1, F_T / C_T)."""
    keys = [k for k in cells_T if k[2] in GSE_CELLS]
    assert len(keys) == 2, keys
    C_T = sum(cells_T[k] for k in keys)
    s = min(1.0, fred["F_T"] / C_T)
    f = 1 + s * (fred["g"] - 1)
    moved = {k: (v * f if k in keys else v) for k, v in cells_T.items()}
    return nc.bridge_share(moved, g, g[nc.CC_TOTAL], mapping), s


def run(z, vint, fr: Freddie, holdout: bool) -> pd.DataFrame:
    """C1's real-time run (unchanged code) plus the C1b bridge on the same instants and targets."""
    df = nc.run("RT", z, vint, holdout)
    out = []
    for _, r in df.iterrows():
        row = {"t": r["t"], "base_release": r["base_release"], "T": r["T"], "q": r["q"], "k": r["k"]}
        if pd.isna(r.get("bridge")):
            out.append(row)
            continue
        t = pd.Timestamp(r["t"])
        t_end = pd.Period(r["T"], "Q").end_time.normalize()
        q_end = pd.Period(r["q"], "Q").end_time.normalize()
        g = {sid: nc.indicator_growth(vint[sid], t, t_end, q_end, nc.FREQ[sid])[0]
             for sid in sorted(set(nc.MAP_2B.values()) | {nc.CC_TOTAL})}
        cells_T = z.cells_at(r["base_release"], r["T"])
        s_T = nc.share_of(cells_T)
        assert abs((nc.bridge_share(cells_T, g, g[nc.CC_TOTAL], nc.MAP_2B) - s_T) - r["bridge"]) < 1e-12
        fred = fr.at(t, r["T"], r["q"])
        sh, s = c1b_share(cells_T, g, fred, nc.MAP_2B)
        row |= {"bridge_c1": r["bridge"], "bridge_c1b": sh - s_T, "no_change": 0.0, "actual": r["actual"],
                "freddie_report": fred["report"], "freddie_pub_date": fred["report_pub_date"],
                "freddie_label": fred["report_label"], "freddie_latest_month": fred["latest_month"],
                "freddie_g": fred["g"], "freddie_share_s": s}
        out.append(row)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ scoring and tests (prereg)
MODELS = ["bridge_c1b", "bridge_c1", "no_change"]


def score(df: pd.DataFrame, label: str) -> pd.DataFrame:
    out = []
    d0 = df[(df["k"] <= 3)].dropna(subset=["bridge_c1b", "actual"])
    for k, g in list(d0.groupby("k")) + [("all", d0)]:
        e0 = 100 * (g["no_change"] - g["actual"])
        for m in MODELS:
            e = 100 * (g[m] - g["actual"])
            out.append({"set": label, "k": k, "model": m, "n": len(g), "rmse_pp": math.sqrt((e ** 2).mean()),
                        "mae_pp": e.abs().mean(), "mean_error_pp": e.mean(),
                        "rel_rmse_vs_no_change": math.sqrt((e ** 2).mean() / (e0 ** 2).mean())})
    return pd.DataFrame(out)


def paired_t_hln(d: np.ndarray) -> tuple[float, float]:
    """Mean of d against 0, lag 0, HLN small-sample factor (h = 1), two-sided t(n-1)."""
    n = len(d)
    stat = d.mean() / math.sqrt(d.var(ddof=0) / n) * math.sqrt((n - 1) / n)
    return float(stat), float(2 * nc.t_sf(abs(stat), n - 1))


def tests(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    d0 = df[df["k"] <= 3].dropna(subset=["bridge_c1b", "actual"])
    for k, g in d0.groupby("k"):
        e1 = 100 * (g["bridge_c1"] - g["actual"]).to_numpy()
        eb = 100 * (g["bridge_c1b"] - g["actual"]).to_numpy()
        stat, p = nc.dm_hln(e1, eb)
        sens = nc.dm_hac1(e1, eb)
        out.append({"k": k, "hypothesis": "H1 RMSE", "test": "DM-HLN", "n": len(g), "stat": stat, "p": p,
                    "c1b_better": bool((eb ** 2).mean() < (e1 ** 2).mean()), "posthoc_dm_hac1_p": sens[1]})
        stat, p = paired_t_hln(eb - e1)
        out.append({"k": k, "hypothesis": "H2 bias", "test": "paired t (HLN)", "n": len(g), "stat": stat, "p": p,
                    "c1b_better": bool(abs(eb.mean()) < abs(e1.mean())), "posthoc_dm_hac1_p": np.nan})
    t = pd.DataFrame(out)
    t["p_holm"] = nc.holm(t["p"]).values
    return t


def verdict(sc: pd.DataFrame, ts: pd.DataFrame, holdout_sc: pd.DataFrame | None = None) -> str:
    """Prereg decision rules (development part; the holdout condition is added when holdout_sc is given)."""
    r = sc[sc["k"] != "all"].pivot(index="k", columns="model", values="rmse_pp")
    if (r["bridge_c1"] < r["bridge_c1b"]).any():
        return "does not improve"
    h1 = ts[ts["hypothesis"] == "H1 RMSE"]
    if not (h1["p_holm"] < 0.05).any():
        return "comparable"
    if holdout_sc is not None:
        a = holdout_sc[holdout_sc["k"] == "all"].set_index("model")["rmse_pp"]
        if not a["bridge_c1b"] < a["bridge_c1"]:
            return "comparable"
    return "improves on C1"


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return clean(o.item())
    return o


def summary(df, sc, ts) -> dict:
    d = df[df["k"] <= 3].dropna(subset=["bridge_c1b"])
    return {
        "prereg": f"docs/decisions/c1b-prereg.md @ {PREREG_COMMIT}",
        "run": "Freddie only (Fannie and Ginnie carried flat)",
        "n_instants": int(len(df)), "n_scored": {str(k): int(n) for k, n in d.dropna(subset=["actual"]).groupby("k").size().items()},
        "rmse_pp": {str(k): {m: float(g.set_index("model").loc[m, "rmse_pp"]) for m in MODELS} for k, g in sc.groupby("k", sort=False)},
        "mean_error_pp": {str(k): {m: float(g.set_index("model").loc[m, "mean_error_pp"]) for m in MODELS} for k, g in sc.groupby("k", sort=False)},
        "tests": ts.to_dict(orient="records"),
        "verdict_rule": verdict(sc, ts),
        "freddie_share_s_range": [float(d["freddie_share_s"].min()), float(d["freddie_share_s"].max())],
        "instants_using_reissued_report": int((d["freddie_label"] == "content possibly revised").sum()),
    }


# ------------------------------------------------------------------ holdout gate (as research/c2_forecast/holdout_run.py)
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze() -> dict:
    fz = json.loads(FREEZE.read_text())
    bad = sorted(p for p, h in fz["files"].items() if sha(ROOT / p) != h)
    if bad:
        raise SystemExit(f"frozen files changed since the freeze: {bad}")
    return fz


def check_approval(commit: str) -> str:
    plan = subprocess.run(["git", "show", f"{commit}:PLAN.md"], cwd=ROOT, capture_output=True, text=True)
    if plan.returncode != 0:
        raise SystemExit(f"cannot read PLAN.md at {commit}")
    rows = [l for l in plan.stdout.splitlines() if l.startswith("| 20") and "holdout" in l.lower()
            and "unseal" in l.lower() and "c1b" in l.lower() and "| Eleonora" in l]
    if not rows:
        raise SystemExit(f"no Eleonora row in PLAN.md at {commit} that unseals the holdout for C1b")
    return rows[-1]


def clean_tree() -> None:
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if st.strip():
        raise SystemExit("working tree not clean: the holdout run must be one clean commit")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--approval", help="commit with Eleonora's unseal row (holdout only)")
    ap.add_argument("--dry-run", action="store_true", help="run the holdout code on a split inside development")
    a = ap.parse_args(argv)
    if a.holdout:
        if not a.approval:
            raise SystemExit("--holdout needs --approval <commit>")
        clean_tree()
        check_freeze()
        row = check_approval(a.approval)
    z = nc.Z1()
    inputs = [i for i in nc.pit.load_inputs() if i["id"] in nc.FREQ]
    vint, _ = nc.pit.load_vintages(inputs)
    fr = Freddie()
    df = run(z, vint, fr, a.holdout)
    if not a.holdout:
        assert (df["q"] <= nc.DEV_END).all(), "holdout target leaked into the development run"
    dev = df[df["q"] <= nc.DEV_END]
    if a.holdout or a.dry_run:
        split = nc.DEV_END if a.holdout else DRY_SPLIT
        fit, ho = df[df["q"] <= split], df[df["q"] > split]
        sc_fit, ts_fit = score(fit, "development"), tests(fit)
        sc_ho = score(ho, "holdout")
        res = {"split_after": split, "development": summary(fit, sc_fit, ts_fit),
               "holdout": {"rmse_pp": {str(k): {m: float(g.set_index("model").loc[m, "rmse_pp"]) for m in MODELS}
                                       for k, g in sc_ho.groupby("k", sort=False)},
                           "n_scored": {str(k): int(n) for k, n in ho[ho["k"] <= 3].dropna(subset=["bridge_c1b", "actual"]).groupby("k").size().items()}},
               "verdict_rule": verdict(sc_fit, ts_fit, sc_ho)}
        if a.holdout:
            res |= {"approval": row, "freeze": "research/c1b_nowcast/FREEZE.json"}
            ho.to_csv(HERE / "nowcasts_holdout.csv", index=False, float_format="%.8g")
            (HERE / "holdout_results.json").write_text(json.dumps(clean(res), indent=2, allow_nan=False) + "\n")
        else:
            out = ROOT / "data" / "holdout_dryrun"
            out.mkdir(parents=True, exist_ok=True)
            (out / "c1b_dryrun.json").write_text(json.dumps(clean(res), indent=2, allow_nan=False) + "\n")
        print(json.dumps(clean({"verdict_rule": res["verdict_rule"], "holdout_rmse_all": res["holdout"]["rmse_pp"].get("all")})))
        return 0
    dev.to_csv(HERE / "nowcasts_dev.csv", index=False, float_format="%.8g")
    sc, ts = score(dev, "development"), tests(dev)
    sc.to_csv(HERE / "scores_dev.csv", index=False, float_format="%.6g")
    ts.to_csv(HERE / "tests_dev.csv", index=False, float_format="%.6g")
    (HERE / "results_dev.json").write_text(json.dumps(clean(summary(dev, sc, ts)), indent=2, allow_nan=False) + "\n")
    print(sc.to_string(index=False))
    print(ts.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
