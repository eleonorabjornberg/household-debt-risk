#!/usr/bin/env python3
"""PLAN task A7: event study around the 2008 conservatorship (H1-H3) and the SAFRA mechanical check (H4).

    uv run --project pipeline python research/a7_causal/causal.py

Pre-registration: docs/decisions/a7-causal-prereg.md (frozen 206e126), with the dated addenda of 2026-11-04 (checklist
item 3; implementation details fixed before any A7 data was fetched, commit 8b09d7c) and Eleonora's Q8 decisions.
Every rule below is quoted from those texts; nothing here was chosen after seeing A7 data.

H1  weekly S1 = PMMS 30-year (FRED MORTGAGE30US) minus the mean of daily DGS10 over the same week up to the PMMS date.
    Week 0 = first PMMS release after 6 Sep 2008. Abnormal change over [-1, +4] = S1(+4) - S1(-1) - 5 * predicted
    weekly change. Estimation: 104 weekly changes ending with the change into the last PMMS before 30 Jul 2008 (HERA);
    changes into the first PMMS on/after 13 Feb 2008 (ESA) and 7 May 2008 (ECASLA) dummied out. Predicted change:
    constant mean (primary), AR(1) (sensitivity). Inference: one-sided rank among all five-change windows inside the
    estimation window with no dummied week; HAC t (QS, Andrews AR(1), as in A4) secondary.
H2  ABS issuers' + mortgage REITs' home mortgages (FL673065105 + FL643065173), $bn. H3 public share (validation compute).
    Linear trend on 2000Q1-2007Q4; holdout fit 2000Q1-2005Q4 checked on 2006Q1-2007Q4 against the 2006-07 standard
    deviation; post window 2008Q3-2009Q4; statistic post/pre RMSPE ratio; placebo dates 2004Q1-2006Q4 (trend on the
    32 quarters before each, same six-quarter post window); rank p.
H4  non-federal student loans (FL153166220 - FL313066220): mean quarterly change 2010Q3-2012Q4 vs 2006Q2-2010Q2, HAC t,
    one-sided for a fall. A mechanical check, not a behavioural test.
Holm at 5% across H1-H4. Outputs: results.json, s1_weekly.csv (the event-window path), its_paths.csv.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "a7"
sys.path.insert(0, str(ROOT / "validation"))
_s = importlib.util.spec_from_file_location("a4b", ROOT / "research" / "a4_breaks" / "breaks.py")
a4 = importlib.util.module_from_spec(_s)
sys.modules["a4b"] = a4
_s.loader.exec_module(a4)

EVENT = pd.Timestamp("2008-09-06")
HERA, ESA, ECASLA = pd.Timestamp("2008-07-30"), pd.Timestamp("2008-02-13"), pd.Timestamp("2008-05-07")
ALPHA = 0.05


# ------------------------------------------------------------------ data
def fred(series: str) -> pd.Series:
    p = DATA / f"{series}.json"
    if not p.exists():
        key = os.environ["FRED_API_KEY"]
        q = urllib.parse.urlencode({"series_id": series, "api_key": key, "file_type": "json",
                                    "observation_start": "2004-01-01", "observation_end": "2010-12-31"})
        DATA.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(f"https://api.stlouisfed.org/fred/series/observations?{q}", timeout=60) as r:
            p.write_bytes(r.read())
    obs = json.loads(p.read_text())["observations"]
    s = pd.Series({pd.Timestamp(o["date"]): float(o["value"]) for o in obs if o["value"] not in (".", "")})
    return s.sort_index()


def weekly_s1(pmms: pd.Series, dgs10: pd.Series) -> pd.Series:
    """S1 at each PMMS date: PMMS minus the mean of daily DGS10 over the same week (Mon..PMMS date)."""
    out = {}
    for d, v in pmms.items():
        wk = dgs10[(dgs10.index >= d - pd.Timedelta(days=d.weekday())) & (dgs10.index <= d)]
        if len(wk):
            out[d] = v - wk.mean()
    return pd.Series(out).sort_index()


# ------------------------------------------------------------------ H1
def first_on_or_after(idx: pd.DatetimeIndex, t: pd.Timestamp) -> int:
    return int(np.searchsorted(idx.values, t.to_datetime64(), side="left"))


def event_study(s1: pd.Series) -> dict:
    idx = s1.index
    d = s1.diff()  # d[i] = change into release i
    w0 = int(np.searchsorted(idx.values, EVENT.to_datetime64(), side="right"))  # first release after the event
    end_est = int(np.searchsorted(idx.values, HERA.to_datetime64(), side="left")) - 1  # last release before HERA
    est = list(range(end_est - 103, end_est + 1))
    dummies = {first_on_or_after(idx, ESA), first_on_or_after(idx, ECASLA)}
    est_clean = [i for i in est if i not in dummies]
    mu = float(d.iloc[est_clean].mean())
    actual = float(s1.iloc[w0 + 4] - s1.iloc[w0 - 1])
    ab_mean = actual - 5 * mu
    # AR(1) on weekly changes in the estimation window (clean), iterated 5 steps from the last change before the window
    x, y = d.iloc[[i - 1 for i in est_clean if i - 1 in est_clean]].values, d.iloc[[i for i in est_clean if i - 1 in est_clean]].values
    X = np.c_[np.ones(len(x)), x]
    c, phi = np.linalg.lstsq(X, y, rcond=None)[0]
    last, pred = float(d.iloc[w0 - 1]), 0.0
    for _ in range(5):
        last = c + phi * last
        pred += last
    ab_ar = actual - pred
    # placebo in time: five-change windows inside the estimation window with no dummied week
    plac = []
    for s in range(est[0], est[-1] - 4 + 1):
        win = list(range(s, s + 5))
        if any(i in dummies for i in win):
            continue
        plac.append(float(d.iloc[win].sum()) - 5 * mu)
    plac = np.array(plac)
    p_rank = float((np.sum(plac <= ab_mean) + 1) / (len(plac) + 1))
    resid = d.iloc[est_clean].values - mu
    se = math.sqrt(5 * a4.lrv(resid))
    t_hac = ab_mean / se
    return {"week0": str(idx[w0].date()), "window": [str(idx[w0 - 1].date()), str(idx[w0 + 4].date())],
            "estimation": [str(idx[est[0]].date()), str(idx[est[-1]].date())], "n_est_changes": len(est_clean),
            "dummied": sorted(str(idx[i].date()) for i in dummies),
            "actual_change_pp": round(actual, 4), "mean_weekly_change_pp": round(mu, 5),
            "abnormal_constant_mean_pp": round(ab_mean, 4), "abnormal_ar1_pp": round(ab_ar, 4),
            "ar1": {"c": round(float(c), 5), "phi": round(float(phi), 4)},
            "placebo_n": int(len(plac)), "p_rank_one_sided": round(p_rank, 4),
            "hac_t": round(t_hac, 3), "hac_p_one_sided": round(0.5 * math.erfc(-t_hac / math.sqrt(2)), 4)}


# ------------------------------------------------------------------ H2, H3
def qi(label: str) -> pd.Period:
    return pd.Period(label, freq="Q")


def its(y: pd.Series, treat: str = "2008Q3", post_len: int = 6) -> dict:
    """y indexed by quarterly Period. Interrupted time series with a linear-trend counterfactual."""
    def fit(lo, hi):
        seg = y.loc[lo:hi]
        tt = np.array([(p - seg.index[0]).n for p in seg.index], float)
        b = np.polyfit(tt, seg.values, 1)
        return seg.index[0], b

    def pred(origin, b, periods):
        return np.array([np.polyval(b, (p - origin).n) for p in periods])

    def ratio(T: pd.Period, pre_lo: pd.Period):
        origin, b = fit(pre_lo, T - 1)
        pre = y.loc[pre_lo:T - 1]
        post = y.loc[T:T + post_len - 1]
        e_pre = pre.values - pred(origin, b, pre.index)
        e_post = post.values - pred(origin, b, post.index)
        return math.sqrt(np.mean(e_post ** 2)) / math.sqrt(np.mean(e_pre ** 2)), float(e_post.mean()), e_post

    # holdout check (CHOICE 7 level)
    origin, b = fit(qi("2000Q1"), qi("2005Q4"))
    ho = y.loc[qi("2006Q1"):qi("2007Q4")]
    ho_rmspe = math.sqrt(np.mean((ho.values - pred(origin, b, ho.index)) ** 2))
    sd = float(ho.std(ddof=1))
    fit_ok = ho_rmspe <= sd
    T = qi(treat)
    r, mean_dev, e_post = ratio(T, qi("2000Q1"))
    plac = [ratio(P, P - 32)[0] for P in pd.period_range("2004Q1", "2006Q4", freq="Q")]
    p = float((np.sum(np.array(plac) >= r) + 1) / (len(plac) + 1))
    return {"holdout_rmspe": round(ho_rmspe, 4), "holdout_sd_2006_07": round(sd, 4), "fit_ok": bool(fit_ok),
            "post_pre_rmspe_ratio": round(r, 4), "mean_post_deviation": round(mean_dev, 4),
            "post_deviations": [round(float(v), 4) for v in e_post],
            "placebo_ratios": [round(v, 4) for v in plac], "p_rank": round(p, 4)}


# ------------------------------------------------------------------ H4
def h4(nonfed: pd.Series) -> dict:
    dq = nonfed.diff().dropna()
    pre = dq.loc[qi("2006Q2"):qi("2010Q2")]
    post = dq.loc[qi("2010Q3"):qi("2012Q4")]
    diff = float(post.mean() - pre.mean())
    se = math.sqrt(a4.lrv(pre.values - pre.mean()) / len(pre) + a4.lrv(post.values - post.mean()) / len(post))
    t = diff / se
    return {"mean_change_pre_bn": round(float(pre.mean()), 3), "mean_change_post_bn": round(float(post.mean()), 3),
            "difference_bn": round(diff, 3), "hac_t": round(t, 3), "p_one_sided": round(0.5 * math.erfc(-t / math.sqrt(2)), 6),
            "n_pre": len(pre), "n_post": len(post)}


def quarterly(zip_path: Path) -> tuple[pd.Series, pd.Series, pd.Series]:
    import run
    import zparse
    cat, rows, public, groups = run.load_catalog()
    ids = sorted({s["id"] for s in rows} | {"FL673065105", "FL643065173", "FL153166220", "FL313066220"})
    z = zparse.load_z1_zip(zip_path, ids)
    df = run.to_frame(z[0] if isinstance(z, tuple) else z)
    share = run.compute(df, groups, public)["share"] * 100
    pls = (df["FL673065105"] + df["FL643065173"]) / 1e3
    nonfed = (df["FL153166220"] - df["FL313066220"]) / 1e3
    to_p = lambda s: pd.Series(s.values, index=pd.PeriodIndex(s.index, freq="Q"))  # noqa: E731
    return to_p(pls), to_p(share), to_p(nonfed)


def holm(p: dict) -> dict:
    return a4.holm(p, ALPHA)


def main() -> int:
    pmms, dgs = fred("MORTGAGE30US"), fred("DGS10")
    s1 = weekly_s1(pmms, dgs)
    h1 = event_study(s1)
    pls, share, nonfed = quarterly(ROOT / "data" / "validation" / "FRB_Z1_csv.zip")
    r2, r3, r4 = its(pls.loc["1999Q1":]), its(share.loc["1999Q1":]), h4(nonfed.loc["2006Q1":])
    ps = {"H1": h1["p_rank_one_sided"], "H2": r2["p_rank"] if r2["fit_ok"] else 1.0,
          "H3": r3["p_rank"] if r3["fit_ok"] else 1.0, "H4": r4["p_one_sided"]}
    hr = holm(ps)
    verdict = {
        "H1": ("supported" if hr["H1"] and h1["abnormal_constant_mean_pp"] < 0 else
               "against" if h1["abnormal_constant_mean_pp"] > 0 and (1 - h1["p_rank_one_sided"]) <= ALPHA else "null"),
        "H2": "fit failed" if not r2["fit_ok"] else ("supported" if hr["H2"] and r2["mean_post_deviation"] < 0 else "null"),
        "H3": "fit failed" if not r3["fit_ok"] else ("supported" if hr["H3"] and r3["mean_post_deviation"] > 0 else "null"),
        "H4": "mechanics as expected" if hr["H4"] and r4["difference_bn"] < 0 else "not as expected"}
    res = {"prereg": "docs/decisions/a7-causal-prereg.md (206e126) + addenda 0f9aaff, 8b09d7c",
           "vintages": {"z1": "2026-09-11", "fred": "retrieved 2026-11-04 (data/a7/*.json)"},
           "H1": h1, "H2": r2, "H3": r3, "H4": r4, "holm_reject": hr, "verdict": verdict}
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    i0 = s1.index.get_loc(pd.Timestamp(h1["week0"]))
    s1.iloc[i0 - 10:i0 + 10].round(4).to_csv(HERE / "s1_weekly_event.csv", header=["s1_pp"], index_label="pmms_date")
    print(json.dumps({"H1": {k: h1[k] for k in ("week0", "actual_change_pp", "abnormal_constant_mean_pp", "abnormal_ar1_pp",
                                                  "p_rank_one_sided", "hac_t")},
                      "H2": {k: r2[k] for k in ("fit_ok", "post_pre_rmspe_ratio", "mean_post_deviation", "p_rank")},
                      "H3": {k: r3[k] for k in ("fit_ok", "post_pre_rmspe_ratio", "mean_post_deviation", "p_rank")},
                      "H4": r4, "holm": hr, "verdict": verdict}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
