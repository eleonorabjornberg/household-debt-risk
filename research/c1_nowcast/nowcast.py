#!/usr/bin/env python3
"""PLAN task C1: nowcast the public share between Z.1 releases, and score it (development sample only).

    uv run --project pipeline python research/c1_nowcast/nowcast.py            # development sample
    uv run --project pipeline python research/c1_nowcast/nowcast.py --holdout  # NOT before the holdout is cleared

Specification: EVALUATION.md (committed before this script first scored anything). Inputs:
z1_vintages.py outputs (data/c1/z1_cells.csv, z1_share_vintages.csv, first_release.csv, z1_vintage_notes.csv),
z1_calendar.csv, and ALFRED vintages through pit.py. Outputs next to this file: nowcasts_dev.csv (one row per
sample x instant), scores_dev.csv, tests_dev.csv, results_dev.json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research" / "common"))
import pit  # noqa: E402

DEV_END = "2023Q2"          # holdout 2023Q3-2026Q2 (C2 frozen; coordinator ruling 66adeff): untouched
LATEST_RELEASE = "2026-09-11"
MAP_2B = {"cc_federal": "TOTALGOV", "cc_depository": "TOTALDI", "cc_finance": "TOTALFC",
          "cc_credit_unions": "TOTALTCU", "mort_banks": "RREACBW027NBOG"}
MAP_2A = {"cc_federal": "TOTALGOV"}
CC_TOTAL = "TOTALNS"
FREQ = {"TOTALGOV": "M", "TOTALDI": "M", "TOTALFC": "M", "TOTALTCU": "M", "TOTALNS": "M", "RREACBW027NBOG": "W"}
MIN_REG_PAIRS = 12


class LeakError(AssertionError):
    pass


def guard(available_at, t) -> None:
    """Raise if any datum used at instant t became public after t (C2 leakage tests 1-3)."""
    a = pd.to_datetime(pd.Series(available_at))
    if (a > pd.Timestamp(t)).any():
        raise LeakError(f"datum available {a.max().date()} used at {pd.Timestamp(t).date()}")


# ------------------------------------------------------------------ indicators
def period_end(d: pd.Timestamp, freq: str) -> pd.Timestamp:
    return d if freq == "W" else d.to_period("M").end_time.normalize()


def growth_from_rows(rows: pd.DataFrame, t, t_end, q_end, freq: str) -> tuple[float, str]:
    """Growth of an indicator from the end of quarter T to the latest period <= end of q, from as-of rows.

    rows: the vintage rows used (date, realtime_start, value). Guarded: every row must be public at t.
    Returns (g, label of the latest period used). g = 1 when nothing after T is public yet.
    """
    guard(rows["realtime_start"], t)
    pe = rows["date"].map(lambda d: period_end(d, freq))
    r = rows.assign(pe=pe).dropna(subset=["value"]).sort_values("date")
    base = r[r["pe"] <= t_end]
    latest = r[r["pe"] <= q_end]
    if base.empty:
        raise ValueError("indicator has no observation in or before quarter T")
    b, l = base.iloc[-1], latest.iloc[-1]
    if l["date"] <= b["date"]:
        return 1.0, str(b["date"].date())
    return float(l["value"] / b["value"]), str(l["date"].date())


def indicator_growth(v: pd.DataFrame, t, t_end, q_end, freq: str):
    known = v[(v["realtime_start"] <= pd.Timestamp(t)) & (v["realtime_end"] >= pd.Timestamp(t))]
    return growth_from_rows(known, t, t_end, q_end, freq)


# ------------------------------------------------------------------ Z.1 vintages
class Z1:
    def __init__(self):
        self.cells = pd.read_csv(ROOT / "data" / "c1" / "z1_cells.csv")
        self.sv = pd.read_csv(HERE / "z1_share_vintages.csv")
        self.fr = pd.read_csv(HERE / "first_release.csv").set_index("quarter")
        notes = pd.read_csv(HERE / "z1_vintage_notes.csv")
        self.parsed = set(notes.loc[notes["last_quarter"].notna(), "release"])
        self.cal = pd.read_csv(HERE / "z1_calendar.csv")
        self.cal["z1_release"] = pd.to_datetime(self.cal["z1_release"])
        self._shares = {r: g.set_index("quarter")["share"] for r, g in self.sv.groupby("release")}
        self._cells = {r: g for r, g in self.cells.groupby("release")}

    def release_at(self, t) -> tuple[pd.Timestamp, str]:
        c = self.cal[self.cal["z1_release"] <= pd.Timestamp(t)]
        r = c.iloc[-1]
        return r["z1_release"], r["latest_quarter_published"]

    def shares(self, release: str) -> pd.Series:
        return self._shares[release]

    def cells_at(self, release: str, quarter: str) -> dict:
        g = self._cells[release]
        g = g[g["quarter"] == quarter]
        return {(row.loan, row.side, row.holder): row.usd_m for row in g.itertuples()}


def share_of(cells: dict) -> float:
    pub = sum(v for k, v in cells.items() if k[1] == "public")
    return pub / sum(cells.values())


def bridge_share(cells_T: dict, g: dict, g_cc_total: float, mapping: dict) -> float:
    """Move mapped cells by their indicator growth; consumer-credit total by TOTALNS growth, with the
    unmapped consumer-credit cells scaled together so the total matches; everything else carried."""
    out = dict(cells_T)
    for (loan, side, holder), v in cells_T.items():
        if holder in mapping:
            out[(loan, side, holder)] = v * g[mapping[holder]]
    cc_keys = [k for k in cells_T if k[0] == "consumer credit"]
    cc_total = sum(cells_T[k] for k in cc_keys) * g_cc_total
    mapped = [k for k in cc_keys if k[2] in mapping]
    rest = [k for k in cc_keys if k[2] not in mapping]
    rest_target = cc_total - sum(out[k] for k in mapped)
    rest_now = sum(cells_T[k] for k in rest)
    if rest_target <= 0 or rest_now <= 0:
        raise ValueError("consumer-credit residual not positive")
    for k in rest:
        out[k] = cells_T[k] * rest_target / rest_now
    return share_of(out)


# ------------------------------------------------------------------ benchmarks
def ar1_forecast(dq: np.ndarray) -> float:
    y, x = dq[1:], dq[:-1]
    X = np.column_stack([np.ones(len(x)), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return float(b[0] + b[1] * dq[-1])


def benchmarks(hist: pd.Series) -> dict:
    """hist: share by quarter (as of the base release), up to T. Returns forecast changes."""
    dq = hist.diff().dropna().to_numpy()
    return {"no_change": 0.0, "drift": float(dq[-4:].mean()), "ar1": ar1_forecast(dq)}


# ------------------------------------------------------------------ instants
def instants(start: str, end: str) -> list[pd.Timestamp]:
    return list(pd.date_range(start, end, freq="MS") + pd.Timedelta(days=14))


def qadd(q: str, n: int) -> str:
    return str(pd.Period(q, "Q") + n)


def run(sample: str, z: Z1, vint: dict, holdout: bool) -> pd.DataFrame:
    rt = sample == "RT"
    mapping = MAP_2A if sample == "P2a" else MAP_2B
    start = {"RT": "2016-09-01", "P2b": "2015-01-01", "P2a": "2010-06-01"}[sample]
    first_target = {"RT": "2016Q3", "P2b": "2015Q1", "P2a": "2010Q2"}[sample]
    rows, k_of = [], {}
    latest = z.shares(LATEST_RELEASE)
    for t in instants(start, "2026-10-01"):
        rdate, T = z.release_at(t)
        guard([rdate], t)
        q = qadd(T, 1)
        if q < first_target:
            continue
        if not holdout and q > DEV_END:
            continue
        k_of[q] = k_of.get(q, 0) + 1
        k = min(k_of[q], 3)
        rel = rdate.date().isoformat()
        row = {"sample": sample, "t": t.date().isoformat(), "base_release": rel, "T": T, "q": q, "k": k}
        if rt:
            if rel not in z.parsed:
                rows.append(row | {"absent": "base release has no archived CSV"})
                continue
            hist = z.shares(rel)
            cells_T = z.cells_at(rel, T)
        else:
            hist = latest
            cells_T = z.cells_at(LATEST_RELEASE, T)
        hist = hist[hist.index <= T]
        assert hist.index[-1] == T, (sample, t, T)
        t_end = pd.Period(T, "Q").end_time.normalize()
        q_end = pd.Period(q, "Q").end_time.normalize()
        g, used = {}, {}
        for sid in set(mapping.values()) | {CC_TOTAL}:
            g[sid], used[sid] = indicator_growth(vint[sid], t, t_end, q_end, FREQ[sid])
        s_T = share_of(cells_T)
        assert abs(s_T - hist.iloc[-1]) < 1e-8   # shares CSV stores 8 decimals
        row |= {"share_T": s_T, "bridge": bridge_share(cells_T, g, g[CC_TOTAL], mapping) - s_T}
        row |= benchmarks(hist)
        row |= {f"latest_{k_}": v for k_, v in used.items()}
        # Targets (never fed to any model: they are only joined here, after the forecasts)
        if q in z.fr.index:
            frel = z.fr.loc[q, "first_release"]
            row["actual_first"] = z.fr.loc[q, "share_first"] - z.shares(frel)[T]
            row["first_release_date"] = frel
        row["actual_latest"] = latest[q] - latest[T]
        rows.append(row)
    df = pd.DataFrame(rows)
    df["actual"] = df["actual_first"] if rt else df["actual_latest"]
    # Bridge regression: per k, past pairs whose target was published at t
    pub_date = (df["first_release_date"] if rt else df["q"].map(lambda qq: release_date_of(z, qq)))
    df["published"] = pd.to_datetime(pub_date)
    reg = []
    for i, r in df.iterrows():
        if pd.isna(r.get("bridge")):
            reg.append(np.nan)
            continue
        past = df[(df["k"] == r["k"]) & (df["published"] <= pd.Timestamp(r["t"])) & df["actual"].notna() & df["bridge"].notna()]
        if len(past) < MIN_REG_PAIRS:
            reg.append(np.nan)
            continue
        guard(past["published"], r["t"])
        X = np.column_stack([np.ones(len(past)), past["bridge"]])
        b = np.linalg.lstsq(X, past["actual"].to_numpy(), rcond=None)[0]
        reg.append(float(b[0] + b[1] * r["bridge"]))
    df["bridge_reg"] = reg
    return df


def release_date_of(z: Z1, q: str):
    c = z.cal[z.cal["latest_quarter_published"] == q]
    return c["z1_release"].iloc[0] if len(c) else pd.NaT


# ------------------------------------------------------------------ distributions (stdlib; checked against scipy in tests)
def norm_sf(x: float) -> float:
    return 0.5 * math.erfc(x / math.sqrt(2))


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (Numerical Recipes, betacf)."""
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1 + aa / 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(c) > 1e-300 else 1 + aa / 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-14:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_sf(t: float, df: float) -> float:
    """Upper tail P(T > t) of Student's t."""
    x = df / (df + t * t)
    p = 0.5 * betainc(df / 2, 0.5, x)
    return p if t >= 0 else 1 - p


# ------------------------------------------------------------------ scoring
MODELS = ["bridge", "bridge_reg", "no_change", "drift", "ar1"]


def score(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (sample, k), g in list(df.groupby(["sample", "k"])) + [((s, "all"), g) for s, g in df.groupby("sample")]:
        for m in MODELS:
            d = g.dropna(subset=[m, "actual"])
            if d.empty:
                continue
            e = 100 * (d[m] - d["actual"])
            e0 = 100 * (d["no_change"] - d["actual"])
            sign = np.nan if m == "no_change" else float((np.sign(d[m]) == np.sign(d["actual"])).mean())
            out.append({"sample": sample, "k": k, "model": m, "n": len(d), "rmse_pp": math.sqrt((e ** 2).mean()),
                        "mae_pp": e.abs().mean(), "rel_rmse_vs_no_change": math.sqrt((e ** 2).mean() / (e0 ** 2).mean()),
                        "sign_accuracy": sign})
    return pd.DataFrame(out)


def dm_hln(e1: np.ndarray, e2: np.ndarray) -> tuple[float, float]:
    """DM with HLN correction, h=1 (lag 0): positive stat = model 2 has lower squared loss. Two-sided p, t(n-1)."""
    d = e1 ** 2 - e2 ** 2
    n = len(d)
    dm = d.mean() / math.sqrt(d.var(ddof=0) / n)
    stat = dm * math.sqrt((n - 1) / n)
    return float(stat), float(2 * t_sf(abs(stat), n - 1))


def clark_west(e_small: np.ndarray, e_big: np.ndarray, f_small: np.ndarray, f_big: np.ndarray) -> tuple[float, float]:
    """Clark-West (2007) for nested models, lag 0. One-sided p: the larger model forecasts better."""
    adj = e_small ** 2 - (e_big ** 2 - (f_small - f_big) ** 2)
    n = len(adj)
    stat = adj.mean() / math.sqrt(adj.var(ddof=1) / n)
    return float(stat), float(norm_sf(stat))


def holm(p: pd.Series) -> pd.Series:
    order = p.sort_values().index
    m = len(p)
    adj, run = {}, 0.0
    for i, idx in enumerate(order):
        run = max(run, min(1.0, (m - i) * p[idx]))
        adj[idx] = run
    return pd.Series(adj)[p.index]


def tests(df: pd.DataFrame) -> pd.DataFrame:
    pairs = [("bridge", "no_change", "DM-HLN"), ("bridge", "ar1", "DM-HLN"), ("bridge_reg", "no_change", "CW"),
             ("bridge_reg", "ar1", "DM-HLN"), ("drift", "no_change", "CW"), ("ar1", "no_change", "CW")]
    out = []
    for (sample, k), g in df.groupby(["sample", "k"]):
        for cand, bench, kind in pairs:
            d = g.dropna(subset=[cand, bench, "actual"])
            if len(d) < 8:
                continue
            ec, eb = 100 * (d[cand] - d["actual"]).to_numpy(), 100 * (d[bench] - d["actual"]).to_numpy()
            if kind == "DM-HLN":
                stat, p = dm_hln(eb, ec)
            else:
                stat, p = clark_west(eb, ec, 100 * d[bench].to_numpy(), 100 * d[cand].to_numpy())
            primary = sample == "RT" and cand in ("bridge", "bridge_reg") and bench in ("no_change", "ar1")
            out.append({"sample": sample, "k": k, "candidate": cand, "benchmark": bench, "test": kind, "n": len(d),
                        "stat": stat, "p": p, "candidate_lower_rmse": bool((ec ** 2).mean() < (eb ** 2).mean()),
                        "primary_family": primary})
    t = pd.DataFrame(out)
    t["p_holm"] = np.nan
    fam = t["primary_family"]
    if fam.any():
        t.loc[fam, "p_holm"] = holm(t.loc[fam, "p"]).values
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--holdout", action="store_true", help="include holdout targets (only once the holdout is cleared)")
    a = ap.parse_args(argv)
    if a.holdout:
        raise SystemExit("holdout run not cleared: see EVALUATION.md 'Open conflicts'")
    z = Z1()
    inputs = [i for i in pit.load_inputs() if i["id"] in FREQ]
    vint, _ = pit.load_vintages(inputs)
    df = pd.concat([run(s, z, vint, a.holdout) for s in ["RT", "P2b", "P2a"]], ignore_index=True)
    # Secondary target for RT (EVALUATION.md): same real-time nowcasts scored against the latest vintage.
    # The bridge regression is dropped there: it was trained on first-release targets.
    rt_latest = df[df["sample"] == "RT"].assign(sample="RT-latest", bridge_reg=np.nan)
    rt_latest["actual"] = rt_latest["actual_latest"]
    df = pd.concat([df, rt_latest], ignore_index=True)
    assert (df["q"] <= DEV_END).all(), "holdout target leaked into the development run"
    df.to_csv(HERE / "nowcasts_dev.csv", index=False, float_format="%.8g")
    sc = score(df)
    sc.to_csv(HERE / "scores_dev.csv", index=False, float_format="%.6g")
    ts = tests(df)
    ts.to_csv(HERE / "tests_dev.csv", index=False, float_format="%.6g")

    def s_(sample, k, m, col="rmse_pp"):
        r = sc[(sc["sample"] == sample) & (sc["k"].astype(str) == str(k)) & (sc["model"] == m)]
        return float(r[col].iloc[0]) if len(r) else None

    res = {
        "spec": "research/c1_nowcast/EVALUATION.md",
        "dev_end": DEV_END,
        "n_instants": {s: int((df["sample"] == s).sum()) for s in df["sample"].unique()},
        "n_absent_rt": int(df.loc[df["sample"] == "RT", "absent"].notna().sum()) if "absent" in df else 0,
        "rmse_pp": {s: {str(k): {m: s_(s, k, m) for m in MODELS} for k in [1, 2, 3, "all"]} for s in ["RT", "RT-latest", "P2b", "P2a"]},
        "rel_rmse_vs_no_change": {s: {str(k): {m: s_(s, k, m, "rel_rmse_vs_no_change") for m in MODELS}
                                      for k in [1, 2, 3, "all"]} for s in ["RT", "RT-latest", "P2b", "P2a"]},
        "n_scored": {s: {str(k): s_(s, k, "bridge", "n") for k in [1, 2, 3, "all"]} for s in ["RT", "RT-latest", "P2b", "P2a"]},
        "n_scored_bridge_reg": {s: {str(k): s_(s, k, "bridge_reg", "n") for k in [1, 2, 3, "all"]} for s in ["RT", "P2b", "P2a"]},
        # Descriptive diagnostic (not a test): mean bridge error by sample and k, pp of share
        "bridge_mean_error_pp": {s: {str(k): float(100 * (g["bridge"] - g["actual"]).mean())
                                     for k, g in list(df[df["sample"] == s].dropna(subset=["bridge", "actual"]).groupby("k"))
                                     + [("all", df[df["sample"] == s].dropna(subset=["bridge", "actual"]))]}
                                 for s in ["RT", "RT-latest", "P2b", "P2a"]},
        "primary_tests": ts[ts["primary_family"]][["k", "candidate", "benchmark", "test", "n", "stat", "p", "p_holm",
                                                  "candidate_lower_rmse"]].to_dict(orient="records"),
    }
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, float) and o != o:
            return None
        if isinstance(o, (np.floating, np.integer, np.bool_)):
            return clean(o.item())
        return o
    (HERE / "results_dev.json").write_text(json.dumps(clean(res), indent=2, allow_nan=False) + "\n")
    print(sc[sc["k"].astype(str) == "all"].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
