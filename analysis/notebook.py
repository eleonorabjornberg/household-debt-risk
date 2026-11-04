"""Who Holds the Debt? -- analysis notebook.

Reproduces every number in analysis/findings.md.

    cd analysis
    uv run --with pandas --with matplotlib --with numpy python -I notebook.py

Inputs
  .cache/z1_extract.csv   Z.1 long CSV filtered to the catalog's series (see `build_extract` below)
  .cache/fred/<ID>.csv    fredgraph.csv downloads (fetched on first run if missing)
Outputs
  results.json            every headline number, keyed (findings.md quotes these)
  tables/*.csv            the tables behind each section
  figures/*.png           charts
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
FIG = HERE / "figures"
TAB = HERE / "tables"
for p in (CACHE, FIG, TAB, CACHE / "fred"):
    p.mkdir(parents=True, exist_ok=True)

Z1_CSV = os.environ.get(
    "Z1_CSV",
    "/tmp/claude-0/-home-user/81ea60fe-81d4-5e28-9cb5-4a9d650b5321/scratchpad/z1csv/ex/Z1.csv",
)
CATALOG = HERE.parent / "pipeline" / "series_catalog.yaml"
RNG = np.random.default_rng(20261027)
R: dict = {}  # results.json
BS: pd.DataFrame  # bucket shares of scope total, set in main()


# ----------------------------------------------------------------------------- data
def catalog_ids() -> list[str]:
    return sorted(set(re.findall(r"id: (FL\d{9})", CATALOG.read_text())))


def build_extract() -> Path:
    """Stream the 3.3 GB long CSV once and keep only catalog series (both .Q)."""
    out = CACHE / "z1_extract.csv"
    if out.exists():
        return out
    pats = CACHE / "patterns.txt"
    pats.write_text("".join(f"Z1/Z1/{s}.Q,\n" for s in catalog_ids()))
    with open(out, "w") as fh:
        fh.write(open(Z1_CSV).readline())
        fh.flush()
        grep = subprocess.run(["grep", "-F", "-f", str(pats), Z1_CSV], capture_output=True, text=True, check=True)
        for line in grep.stdout.splitlines():
            if re.match(r"^Z1/Z1/FL\d{9}\.Q,", line):
                fh.write(line + "\n")
    return out


def load_z1() -> pd.DataFrame:
    d = pd.read_csv(build_extract(), usecols=["series_name", "date", "value"])
    d["sid"] = d.series_name.str.slice(6, 17)
    w = d.pivot(index="date", columns="sid", values="value").astype(float)
    w.index = pd.to_datetime(w.index)
    # annual observations 1945-1951, quarterly from 1952Q1: keep the quarterly span
    return w.loc["1952-03-31":]


def fred_asof() -> str | None:
    """FRED as-of date (PLAN F2-1): env FRED_ASOF, else the committed snapshot's vintages.fred."""
    if os.environ.get("FRED_ASOF"):
        return os.environ["FRED_ASOF"]
    meta = HERE.parent / "web" / "public" / "data" / "meta.json"
    return json.loads(meta.read_text()).get("vintages", {}).get("fred") if meta.exists() else None


def load_fred(sid: str) -> pd.Series:
    """Pinned: ALFRED observations as they stood on fred_asof() (needs FRED_API_KEY), so reruns
    reproduce results.json. Without a key, falls back to the latest fredgraph.csv and says so."""
    asof, key = fred_asof(), os.environ.get("FRED_API_KEY")
    if asof and key:
        f = CACHE / "fred" / f"{sid}@{asof}.csv"
        if not f.exists():
            import urllib.parse
            import urllib.request
            q = urllib.parse.urlencode({"series_id": sid, "api_key": key, "file_type": "json",
                                        "realtime_start": asof, "realtime_end": asof})
            with urllib.request.urlopen(f"https://api.stlouisfed.org/fred/series/observations?{q}", timeout=60) as r:
                obs = json.load(r)["observations"]
            # "." marks a missing observation; ALFRED also writes some whole numbers as "1721271.0".
            # Normalise both so values parse exactly as they do from fredgraph.csv.
            d = pd.DataFrame([o for o in obs if o["value"] != "."])[["date", "value"]]
            v = pd.to_numeric(d.value)
            d["value"] = v.astype("int64") if (v % 1 == 0).all() else v
            d.to_csv(f, index=False)
    else:
        print(f"WARNING: FRED {sid} not pinned (no FRED_API_KEY or as-of date): latest data, results may drift", file=sys.stderr)
        f = CACHE / "fred" / f"{sid}.csv"
        if not f.exists():
            subprocess.run(["curl", "-sS", "-o", str(f), f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"], check=True)
    s = pd.read_csv(f)
    s.columns = ["date", "value"]
    s["date"] = pd.to_datetime(s.date)
    s["value"] = pd.to_numeric(s.value, errors="coerce")
    return s.dropna().set_index("date").value


def q_end(s: pd.Series, how: str = "last") -> pd.Series:
    g = s.groupby(s.index.to_period("Q"))
    out = g.last() if how == "last" else g.mean()
    out.index = out.index.to_timestamp(how="end").normalize()
    return out


MH = {  # mortgage holders -> bucket
    "FL313065105": "federal_direct", "FL403065105": "gse_agency", "FL413065105": "gse_agency",
    "FL213065103": "state_local", "FL763065105": "banks_credit_unions", "FL753065103": "banks_credit_unions",
    "FL743065103": "banks_credit_unions", "FL473065100": "banks_credit_unions",
    "FL673065105": "private_securitization", "FL643065173": "private_securitization",
    "FL153065103": "nonbank_other", "FL103065105": "nonbank_other", "FL113065103": "nonbank_other",
    "FL543065105": "nonbank_other", "FL573065103": "nonbank_other", "FL223065143": "nonbank_other",
    "FL613065105": "nonbank_other",
}
CH = {  # consumer credit holders -> bucket
    "FL313066220": "federal_direct", "FL403066005": "gse_agency", "FL763066005": "banks_credit_unions",
    "FL473066000": "banks_credit_unions", "FL673066000": "private_securitization", "FL613066005": "nonbank_other",
    "FL103066003": "nonbank_other", "FL113066003": "nonbank_other", "FL163066223": "nonbank_other",
}
BUCKETS = ["federal_direct", "gse_agency", "state_local", "banks_credit_unions", "private_securitization", "nonbank_other"]
PUBLIC = BUCKETS[:3]
LABEL = {
    "federal_direct": "Federal government (direct)", "gse_agency": "GSEs & agency pools",
    "state_local": "State & local governments", "banks_credit_unions": "Banks & credit unions",
    "private_securitization": "Private securitization & mREITs", "nonbank_other": "Finance cos. & other private",
}
# Validated with the dataviz validator (light surface #fcfcfb): all gates pass; cool = public, warm = private.
COLOR = {
    "federal_direct": "#1c5cab", "gse_agency": "#1baf7a", "state_local": "#3987e5",
    "banks_credit_unions": "#e34948", "private_securitization": "#eda100", "nonbank_other": "#e87ba4",
}
INK, INK2, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#ecebe6"

NBER = {  # peak quarter -> trough quarter (quarter-end dates)
    "1953Q2": "1954Q2", "1957Q3": "1958Q2", "1960Q2": "1961Q1", "1969Q4": "1970Q4", "1973Q4": "1975Q1",
    "1980Q1": "1980Q3", "1981Q3": "1982Q4", "1990Q3": "1991Q1", "2001Q1": "2001Q4", "2007Q4": "2009Q2",
    "2019Q4": "2020Q2",
}
SHOCKS = ["2020Q1", "2023Q4", "2025Q2"]


def qd(q: str) -> pd.Timestamp:
    return pd.Period(q, "Q").to_timestamp(how="end").normalize()


def qs(ts) -> str:
    return str(pd.Timestamp(ts).to_period("Q"))


# ----------------------------------------------------------------------------- core build
def build(w: pd.DataFrame) -> dict[str, pd.DataFrame]:
    mort, cc = w.FL153165105, w.FL153166000
    total = mort + cc
    assert (total - w.FL154104015).abs().max() < 1, "scope total identity"
    assert (w[list(MH)].sum(axis=1) - w.FL893065105).abs().max() < 1, "mortgage holder identity"
    assert (w[list(CH)].sum(axis=1) - cc).abs().max() < 1, "cc holder identity"
    types = ["FL153166100", "FL153166220", "FL153166400", "FL153166205"]
    assert (w[types].sum(axis=1) - cc).abs().max() < 1, "cc type identity"

    k = mort / w.FL893065105  # apportioning factor: household share of all 1-4 family mortgages
    mb = pd.DataFrame({b: sum(w[s] for s, bb in MH.items() if bb == b) * k for b in BUCKETS})
    cb = pd.DataFrame({b: sum((w[s] for s, bb in CH.items() if bb == b), start=pd.Series(0.0, index=w.index)) for b in BUCKETS})
    both = mb + cb
    ps = pd.DataFrame({
        "total": total, "mort": mort, "cc": cc,
        "public": both[PUBLIC].sum(axis=1), "public_m": mb[PUBLIC].sum(axis=1), "public_c": cb[PUBLIC].sum(axis=1),
    })
    ps["share"] = ps.public / ps.total
    ps["share_m"] = ps.public_m / ps.mort
    ps["share_c"] = ps.public_c / ps.cc
    ps["mort_w"] = ps.mort / ps.total
    ps["k"] = k
    return {"mb": mb, "cb": cb, "both": both, "ps": ps, "bshare": both.div(total, axis=0)}


# ----------------------------------------------------------------------------- charts
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlecolor": INK,
    "legend.frameon": False, "lines.linewidth": 2,
})


def crisis_bands(ax, start="1952-01-01", over=False):
    """NBER recession bands, peak quarter to trough quarter. over=True draws a translucent band above filled areas."""
    for p, t in NBER.items():
        if qd(p) >= pd.Timestamp(start):
            if over:
                ax.axvspan(qd(p) - pd.offsets.QuarterEnd(1), qd(t), color=INK, alpha=0.16, lw=0, zorder=2)
            else:
                ax.axvspan(qd(p) - pd.offsets.QuarterEnd(1), qd(t), color=BAND, lw=0, zorder=0)


def pct_axis(ax):
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=6, steps=[1, 2, 5, 10]))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))


def save(fig, name):
    fig.savefig(FIG / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- Q0: headline series + verify first pass
def q0_verify(ps, mb, cb):
    first_pass = {"1957Q3": (.029, .033), "1960Q2": (.035, .022), "1969Q4": (.046, .068), "1973Q4": (.068, .107),
                  "1980Q1": (.132, .215), "1981Q3": (.145, .225), "1990Q3": (.328, .402), "2001Q1": (.396, .360),
                  "2007Q4": (.355, .483), "2019Q4": (.552, .559)}
    rows = []
    for q in NBER:
        t0 = qd(q)
        t16 = t0 + pd.offsets.QuarterEnd(16)
        a, b = ps.share.get(t0), ps.share.get(t16)
        fp = first_pass.get(q)
        exsl = (ps.public - mb.state_local) / ps.total
        rows.append({"crisis": q, "share_t0": round(a, 4), "share_t16": round(b, 4), "delta_pp": round(100 * (b - a), 2),
                     "first_pass_t0": fp[0] if fp else None, "first_pass_t16": fp[1] if fp else None,
                     "matches_first_pass": (abs(a - fp[0]) < .0006 and abs(b - fp[1]) < .0006) if fp else None,
                     "ex_state_local_t0": round(exsl[t0], 4), "ex_state_local_t16": round(exsl[t16], 4),
                     "state_local_share_t0": round(mb.state_local[t0] / ps.total[t0], 4)})
    t = pd.DataFrame(rows)
    t.to_csv(TAB / "crisis_public_share.csv", index=False)
    last = ps.index[-1]
    R["latest_quarter"] = qs(last)
    R["latest_public_share"] = round(ps.share.iloc[-1], 4)
    R["latest_scope_total_busd"] = round(ps.total.iloc[-1] / 1e3, 1)
    R["latest_public_busd"] = round(ps.public.iloc[-1] / 1e3, 1)
    exsl = (ps.public - mb.state_local) / ps.total
    R["latest_public_share_ex_state_local"] = round(exsl.iloc[-1], 4)
    R["ex_state_local_2020Q1"] = round(exsl[qd("2020Q1")], 4)
    R["state_local_share_max"] = round((mb.state_local / ps.total).max(), 4)
    R["state_local_share_max_q"] = qs((mb.state_local / ps.total).idxmax())
    R["first_quarter"] = qs(ps.index[0])
    R["first_public_share"] = round(ps.share.iloc[0], 4)
    R["peak_public_share"] = round(ps.share.max(), 4)
    R["peak_public_share_q"] = qs(ps.share.idxmax())
    R["crisis_table"] = rows
    return t


# ----------------------------------------------------------------------------- Q1: ratchet test
def q1_ratchet(ps, S, mb, cb):
    H = 16
    s = S.share
    d16 = (s.shift(-H) - s).dropna()  # forward 16q change, indexed by start quarter
    prior = (s - s.shift(H))  # trailing 16q change
    peaks = [qd(q) for q in NBER if qd(q) in d16.index]
    E = d16.index

    def stat(series, idx, starts):
        c = series.loc[starts]
        o = series.loc[idx.difference(starts)]
        return c.mean() - o.mean(), c.mean(), o.mean()

    out = {}

    def run(name, series, starts, n_perm=20000):
        series = series.dropna()
        starts = [x for x in starts if x in series.index]
        idx = series.index
        diff, cm, om = stat(series, idx, starts)
        n = len(starts)
        vals = series.values
        # (a) random placebo dates: n distinct start quarters drawn at random
        draws = np.array([vals[RNG.choice(len(vals), n, replace=False)].mean() for _ in range(n_perm)])
        p_rand = float((draws >= cm).mean())
        # (b) circular shift of the whole crisis calendar (keeps spacing/clustering of the real dates)
        pos = np.array([idx.get_loc(x) for x in starts])
        shifts = np.array([vals[(pos + k) % len(vals)].mean() for k in range(1, len(vals))])
        p_shift = float((shifts >= cm).mean())
        # (c) sign: how many crisis windows beat the median non-crisis window
        med = series.loc[idx.difference(starts)].median()
        beat = int((series.loc[starts] > med).sum())
        out[name] = {"n_crises": n, "crisis_mean_pp": round(100 * cm, 2), "other_mean_pp": round(100 * om, 2),
                     "excess_pp": round(100 * diff, 2), "p_random_dates": round(p_rand, 4),
                     "p_circular_shift": round(p_shift, 4), "crises_above_median_window": f"{beat}/{n}",
                     "crisis_median_pp": round(100 * series.loc[starts].median(), 2),
                     "other_median_pp": round(100 * series.loc[idx.difference(starts)].median(), 2)}
        return draws, cm

    draws_all, cm_all = run("all_nber_1953_2019", d16, peaks)
    run("post1970_nber", d16.loc["1970":], [p for p in peaks if p.year >= 1970])
    run("ex_1980_1981_2007", d16, [p for p in peaks if p.year not in (1980, 1981, 2007)])
    run("ex_2007", d16, [p for p in peaks if p.year != 2007])
    # acceleration: forward change minus the preceding 16q change (strips a locally-linear trend)
    accel = (d16 - prior).dropna()
    run("acceleration_all", accel, peaks)
    run("acceleration_post1970", accel.loc["1970":], [p for p in peaks if p.year >= 1970])
    # mortgage-only public share (removes federal student lending entirely)
    dm = (S.share_m.shift(-H) - S.share_m).dropna()
    run("mortgage_only_share", dm, peaks)
    run("mortgage_only_post1970", dm.loc["1970":], [p for p in peaks if p.year >= 1970])
    # share excluding federal direct student loans (FL313066220) from the public numerator AND the total? keep total.
    pub_ex_stud = (S.public - cb.federal_direct) / S.total
    dx = (pub_ex_stud.shift(-H) - pub_ex_stud).dropna()
    run("ex_federal_student_loans", dx, peaks)
    # 2-quarter "trough-aligned" variant: start at the trough
    troughs = [qd(t) for t in NBER.values() if qd(t) in d16.index]
    run("trough_start", d16, troughs)

    # attribution of the long-run rise: quarterly changes inside the union of crisis windows (t0, t0+16] vs outside
    dq = s.diff().dropna()
    inwin = pd.Series(False, index=dq.index)
    for q in NBER:
        p0 = qd(q)
        inwin |= (dq.index > p0) & (dq.index <= p0 + pd.offsets.QuarterEnd(H))
    R["rise_attribution"] = {
        "total_rise_pp": round(100 * dq.sum(), 2), "inside_windows_pp": round(100 * dq[inwin].sum(), 2),
        "outside_windows_pp": round(100 * dq[~inwin].sum(), 2), "share_of_quarters_inside": round(float(inwin.mean()), 3),
        "share_of_rise_inside": round(float(dq[inwin].sum() / dq.sum()), 3),
        "inside_ex_2007_pp": round(100 * dq[inwin & ~((dq.index > qd("2007Q4")) & (dq.index <= qd("2011Q4")))].sum(), 2),
        "gfc_window_pp": round(100 * dq[(dq.index > qd("2007Q4")) & (dq.index <= qd("2011Q4"))].sum(), 2),
        "per_quarter_inside_pp": round(100 * dq[inwin].mean(), 3), "per_quarter_outside_pp": round(100 * dq[~inwin].mean(), 3),
    }
    gfc = (dq.index > qd("2007Q4")) & (dq.index <= qd("2011Q4"))
    R["rise_attribution"]["ex_2007_share_of_quarters_inside"] = round(float(inwin[~gfc].mean()), 3)
    R["rise_attribution"]["ex_2007_share_of_rise_inside"] = round(float(dq[inwin & ~gfc].sum() / dq[~gfc].sum()), 3)

    # leave-one-out on the main test
    loo = []
    for p in peaks:
        rest = [x for x in peaks if x != p]
        c = d16.loc[rest].mean()
        o = d16.loc[E.difference(peaks)].mean()
        loo.append({"dropped": qs(p), "excess_pp": round(100 * (c - o), 2)})
    R["ratchet_loo"] = loo
    R["ratchet"] = out

    # per-crisis window: forward change, prior change, bucket contributions
    rows = []
    for p in peaks:
        e = p + pd.offsets.QuarterEnd(H)
        bs = BS
        contrib = {f"d_{b}_pp": round(100 * (bs.loc[e, b] - bs.loc[p, b]), 2) for b in BUCKETS}
        pct = float((d16 < d16.loc[p]).mean())
        pub0, pub1 = S.public[p], S.public[e]
        prv0, prv1 = S.total[p] - pub0, S.total[e] - pub1
        cf = pub1 / (pub1 + prv0)  # share if private debt had stayed at its t0 level
        contrib["public_dollar_growth_pct"] = round(100 * (pub1 / pub0 - 1), 1)
        contrib["private_dollar_growth_pct"] = round(100 * (prv1 / prv0 - 1), 1)
        contrib["from_public_growth_pp"] = round(100 * (cf - S.share[p]), 2)
        contrib["from_private_change_pp"] = round(100 * (S.share[e] - cf), 2)
        rows.append({"crisis": qs(p), "fwd16_pp": round(100 * d16.loc[p], 2), "prior16_pp": round(100 * prior.loc[p], 2)
                     if pd.notna(prior.loc[p]) else None, "accel_pp": round(100 * accel.loc[p], 2) if p in accel.index else None,
                     "percentile_among_all_windows": round(pct, 3), **contrib})
    tw = pd.DataFrame(rows)
    tw.to_csv(TAB / "ratchet_windows.csv", index=False)
    R["ratchet_windows"] = rows
    R["all_windows"] = {"n": int(len(d16)), "mean_pp": round(100 * d16.mean(), 2), "median_pp": round(100 * d16.median(), 2),
                        "share_negative": round(float((d16 < 0).mean()), 3), "first": qs(d16.index[0]), "last": qs(d16.index[-1])}
    # largest non-crisis windows (not within 8q of any peak)
    near = pd.Series(False, index=d16.index)
    for p in peaks:
        near |= (d16.index >= p - pd.offsets.QuarterEnd(8)) & (d16.index <= p + pd.offsets.QuarterEnd(8))
    top = d16[~near].sort_values(ascending=False).head(6)
    R["largest_noncrisis_windows"] = [{"start": qs(i), "fwd16_pp": round(100 * v, 2)} for i, v in top.items()]
    top_all = d16.sort_values(ascending=False).head(10)
    R["largest_windows_any"] = [{"start": qs(i), "fwd16_pp": round(100 * v, 2)} for i, v in top_all.items()]

    # structural episodes: where did the public-share gains come from, by decade and bucket
    dec = []
    bs = BS
    for a, b in [("1952Q1", "1969Q4"), ("1969Q4", "1979Q4"), ("1979Q4", "1989Q4"), ("1989Q4", "1999Q4"),
                 ("1999Q4", "2007Q4"), ("2007Q4", "2012Q4"), ("2012Q4", "2019Q4"), ("2019Q4", R["latest_quarter"])]:
        A, B = qd(a), qd(b)
        dec.append({"from": a, "to": b, "d_public_pp": round(100 * (S.share[B] - S.share[A]), 2),
                    **{f"d_{x}_pp": round(100 * (bs.loc[B, x] - bs.loc[A, x]), 2) for x in PUBLIC}})
    R["structural_periods"] = dec
    pd.DataFrame(dec).to_csv(TAB / "structural_periods.csv", index=False)

    # GFC window split: GSE vs federal (student loans vs FHA/VA mortgages)
    p, e = qd("2007Q4"), qd("2011Q4")
    tot = S.total
    R["gfc_window_split_pp"] = {
        "gse_agency": round(100 * (BS.loc[e, "gse_agency"] - BS.loc[p, "gse_agency"]), 2),
        "federal_student_loans": round(100 * (cb.federal_direct[e] / tot[e] - cb.federal_direct[p] / tot[p]), 2),
        "federal_mortgages": round(100 * (mb.federal_direct[e] / tot[e] - mb.federal_direct[p] / tot[p]), 2),
        "state_local": round(100 * (BS.loc[e, "state_local"] - BS.loc[p, "state_local"]), 2),
        "private_securitization": round(100 * (BS.loc[e, "private_securitization"] - BS.loc[p, "private_securitization"]), 2),
        "banks_credit_unions": round(100 * (BS.loc[e, "banks_credit_unions"] - BS.loc[p, "banks_credit_unions"]), 2),
    }
    # how much of the GFC-window public gain is the denominator (private debt shrinking) vs public dollars growing
    R["gfc_dollars_busd"] = {
        "public_t0": round(S.public[p] / 1e3, 1), "public_t16": round(S.public[e] / 1e3, 1),
        "total_t0": round(tot[p] / 1e3, 1), "total_t16": round(tot[e] / 1e3, 1),
        "private_t0": round((tot[p] - S.public[p]) / 1e3, 1), "private_t16": round((tot[e] - S.public[e]) / 1e3, 1),
    }

    # --- figure: event windows (-8..+16) small multiples, public share relative to t0
    fig, axs = plt.subplots(2, 6, figsize=(12, 4.4), sharex=True, sharey=True)
    for ax, p in zip(axs.flat, peaks):
        win = s.loc[p - pd.offsets.QuarterEnd(8): p + pd.offsets.QuarterEnd(H)]
        x = [round((i - p).days / 91.31) for i in win.index]
        ax.axhline(0, color="#c3c2b7", lw=1)
        ax.axvline(0, color=MUTED, lw=0.8, ls=":")
        ax.plot(x, 100 * (win - s[p]), color="#1c5cab")
        ax.set_title(qs(p), fontsize=10)
        ax.tick_params(labelsize=8)
    axs.flat[-1].axis("off")
    fig.suptitle("Public share around each NBER peak (pp change from the peak quarter; quarters −8 to +16)", x=0.01, ha="left",
                 fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout()
    save(fig, "q1_event_windows.png")

    # --- figure: permutation distribution
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.hist(100 * draws_all, bins=60, color="#86b6ef", edgecolor="#fcfcfb", linewidth=0.5)
    ax.axvline(100 * cm_all, color=INK, lw=2)
    ax.annotate(f"Actual crisis mean: +{100 * cm_all:.1f} pp\nshare of placebos ≥ actual: {out['all_nber_1953_2019']['p_random_dates']:.2f}",
                xy=(100 * cm_all, ax.get_ylim()[1] * .85), xytext=(8, 0), textcoords="offset points", color=INK, fontsize=9)
    ax.set_title("Crisis windows vs. 20,000 sets of 11 random start quarters")
    ax.set_xlabel("Mean change in public share over 16 quarters (percentage points)")
    ax.set_yticks([])
    ax.grid(False)
    save(fig, "q1_permutation.png")

    # --- figure: every window's forward change, crisis windows marked
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(d16.index, 100 * d16, color="#86b6ef", lw=1.5, label="All 16-quarter windows (by start quarter)")
    ax.scatter(peaks, [100 * d16[p] for p in peaks], s=40, color=INK, zorder=3, edgecolor="#fcfcfb", linewidth=1.5,
               label="Windows starting at an NBER peak")
    for p in peaks:
        ax.annotate(str(p.year), (p, 100 * d16[p]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=INK2)
    ax.axhline(0, color="#c3c2b7", lw=1)
    crisis_bands(ax)
    ax.set_title("Change in public share over the next 16 quarters")
    ax.set_ylabel("percentage points")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "q1_forward_windows.png")
    return d16


# ----------------------------------------------------------------------------- Q2: decomposition
def q2_decompose(S):
    ps = S
    rows = []
    for q in list(NBER) + SHOCKS:
        t0 = qd(q)
        t1 = t0 + pd.offsets.QuarterEnd(16)
        if t1 not in ps.index:
            t1 = ps.index[-1]
        a, b = ps.loc[t0], ps.loc[t1]
        dS = b.share - a.share
        # (i) mortgage vs consumer-credit dollars:  S = PM/T + PC/T
        mpart = b.public_m / b.total - a.public_m / a.total
        cpart = b.public_c / b.total - a.public_c / a.total
        # (ii) composition vs within (exact midpoint/Shapley):  S = w*pm + (1-w)*pc
        wbar = (a.mort_w + b.mort_w) / 2
        comp = (b.mort_w - a.mort_w) * ((a.share_m + b.share_m) / 2 - (a.share_c + b.share_c) / 2)
        within_m = wbar * (b.share_m - a.share_m)
        within_c = (1 - wbar) * (b.share_c - a.share_c)
        assert abs(comp + within_m + within_c - dS) < 1e-12
        assert abs(mpart + cpart - dS) < 1e-12
        rows.append({"event": q, "kind": "nber" if q in NBER else "shock", "t1": qs(t1),
                     "d_public_share_pp": round(100 * dS, 2), "mortgage_part_pp": round(100 * mpart, 2),
                     "cc_part_pp": round(100 * cpart, 2), "composition_pp": round(100 * comp, 2),
                     "within_mortgage_pp": round(100 * within_m, 2), "within_cc_pp": round(100 * within_c, 2),
                     "mort_weight_t0": round(a.mort_w, 3), "mort_weight_t1": round(b.mort_w, 3),
                     "public_share_mort_t0": round(a.share_m, 3), "public_share_mort_t1": round(b.share_m, 3),
                     "public_share_cc_t0": round(a.share_c, 3), "public_share_cc_t1": round(b.share_c, 3)})
    t = pd.DataFrame(rows)
    t.to_csv(TAB / "decomposition.csv", index=False)
    R["decomposition"] = rows

    tn = t[t.kind == "nber"]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = np.arange(len(tn))
    parts = [("within_mortgage_pp", "Within mortgages (holder shift)", "#1baf7a"),
             ("within_cc_pp", "Within consumer credit (holder shift)", "#1c5cab"),
             ("composition_pp", "Composition (mortgage weight)", "#eda100")]
    pos_b, neg_b = np.zeros(len(tn)), np.zeros(len(tn))
    for col, lab, c in parts:
        v = tn[col].values
        base = np.where(v >= 0, pos_b, neg_b)
        ax.bar(x, v, 0.62, bottom=base, color=c, label=lab, edgecolor="#fcfcfb", linewidth=1.5)
        pos_b += np.where(v >= 0, v, 0)
        neg_b += np.where(v < 0, v, 0)
    ax.scatter(x, tn.d_public_share_pp, color=INK, s=28, zorder=3, label="Net change")
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.set_xticks(x, tn.event)
    ax.set_ylabel("pp change in public share, t0 → +16q")
    ax.set_title("What moved the public share in each crisis window")
    ax.legend(fontsize=8.5, loc="upper left")
    save(fig, "q2_decomposition.png")
    return t


# ----------------------------------------------------------------------------- Q3: FAS 166/167
def q3_fas167(w, S):
    k = S.k
    s40 = w.FL403065105 / w.FL893065105
    s41 = w.FL413065105 / w.FL893065105
    q4, q1 = qd("2009Q4"), qd("2010Q1")
    jump40 = s40[q1] - s40[q4]
    jump41 = s41[q1] - s41[q4]
    comb = s40 + s41
    dcomb = comb.diff()
    R["fas167"] = {
        "sector40_share_2009Q4": round(s40[q4], 4), "sector40_share_2010Q1": round(s40[q1], 4),
        "sector41_share_2009Q4": round(s41[q4], 4), "sector41_share_2010Q1": round(s41[q1], 4),
        "sector40_level_jump_busd": round((w.FL403065105[q1] - w.FL403065105[q4]) / 1e3, 1),
        "sector41_level_jump_busd": round((w.FL413065105[q1] - w.FL413065105[q4]) / 1e3, 1),
        "jump40_pp": round(100 * jump40, 2), "jump41_pp": round(100 * jump41, 2),
        "combined_change_2010Q1_pp": round(100 * dcomb[q1], 2),
        "combined_qoq_abs_mean_2005_2015_pp": round(100 * dcomb.loc["2005":"2015"].abs().mean(), 2),
        "combined_qoq_abs_max_2005_2015_pp": round(100 * dcomb.loc["2005":"2015"].abs().max(), 2),
        # the same standard pulled bank-sponsored consumer ABS (mostly card trusts) back onto bank balance sheets
        "cc_abs_2009Q4_busd": round(w.FL673066000[q4] / 1e3, 1), "cc_abs_2010Q1_busd": round(w.FL673066000[q1] / 1e3, 1),
        "cc_banks_2009Q4_busd": round(w.FL763066005[q4] / 1e3, 1), "cc_banks_2010Q1_busd": round(w.FL763066005[q1] / 1e3, 1),
        "cc_abs_share_of_scope_2009Q4": round(w.FL673066000[q4] / S.total[q4], 4),
        "cc_abs_share_of_scope_2010Q1": round(w.FL673066000[q1] / S.total[q1], 4),
    }
    fig, ax = plt.subplots(figsize=(8, 3.6))
    r = slice("2005-01-01", "2015-12-31")
    ax.plot(s40.loc[r].index, s40.loc[r], color="#3987e5", label="GSE balance sheets (sector 40)")
    ax.plot(s41.loc[r].index, s41.loc[r], color="#eda100", label="Agency & GSE pools (sector 41)")
    ax.plot(comb.loc[r].index, comb.loc[r], color=INK, label="40 + 41 combined")
    ax.axvline(qd("2009Q4") + pd.Timedelta(days=45), color=MUTED, lw=1, ls="--")
    ax.annotate("FAS 166/167\n2010Q1", (qd("2010Q1"), 0.22), xytext=(6, 0), textcoords="offset points", fontsize=8.5, color=INK2)
    pct_axis(ax)
    ax.set_title("Share of all 1-4 family mortgages held: the 2010 break disappears when combined")
    ax.legend(fontsize=8.5, loc="center left")
    save(fig, "q3_fas167.png")


# ----------------------------------------------------------------------------- Q4: Fed QE overlay
def q4_fed(S, mb):
    wk = load_fred("WSHOMCB")
    fed = q_end(wk)
    fed = fed[(fed.index <= S.index[-1]) & (fed > 0)]  # WSHOMCB is zero until QE1 purchases begin (Jan 2009)
    df = pd.DataFrame({"fed": fed}).join(S[["total", "mort"]]).join(mb.gse_agency.rename("agency"))
    df["share_scope"] = df.fed / df.total
    df["share_agency"] = df.fed / df.agency
    df = df.dropna()
    latest_wk = wk.index[-1]
    pk = df.share_scope.idxmax()
    R["fed_mbs"] = {
        "first_q": qs(df.index[0]),
        "first_share": round(df.share_scope.iloc[0], 4),
        "q_2009Q4": round(df.share_scope[qd("2009Q4")], 4),
        "q_2014Q4": round(df.share_scope[qd("2014Q4")], 4),
        "q_2019Q4": round(df.share_scope[qd("2019Q4")], 4),
        "q_2022Q2": round(df.share_scope[qd("2022Q2")], 4),
        "peak_q": qs(pk), "peak_share_scope": round(df.share_scope[pk], 4), "peak_busd": round(df.fed[pk] / 1e3, 1),
        "peak_share_of_apportioned_agency": round(df.share_agency.max(), 4),
        "latest_q": qs(df.index[-1]), "latest_share_scope": round(df.share_scope.iloc[-1], 4),
        "latest_q_busd": round(df.fed.iloc[-1] / 1e3, 1),
        "latest_weekly_date": str(latest_wk.date()), "latest_weekly_busd": round(wk.iloc[-1] / 1e3, 1),
        "max_weekly_busd": round(wk.max() / 1e3, 1), "max_weekly_date": str(wk.idxmax().date()),
        "runoff_from_max_busd": round((wk.max() - wk.iloc[-1]) / 1e3, 1),
        "share_agency_latest": round(df.share_agency.iloc[-1], 4),
    }
    df.to_csv(TAB / "fed_mbs.csv")
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.fill_between(df.index, 0, df.share_scope, color="#86b6ef", lw=0)
    ax.plot(df.index, df.share_scope, color="#1c5cab")
    for a, b, lab in [("2008Q4", "2014Q4", "QE1-QE3"), ("2020Q1", "2022Q1", "Pandemic QE")]:
        ax.axvspan(qd(a), qd(b), color=BAND, lw=0, zorder=0)
        ax.annotate(lab, (qd(a), df.share_scope.max() * 1.02), fontsize=8.5, color=INK2)
    pct_axis(ax)
    ax.set_ylim(0, df.share_scope.max() * 1.12)
    ax.set_title("Fed-held agency MBS as a share of household mortgages + consumer credit")
    save(fig, "q4_fed_mbs.png")


# ----------------------------------------------------------------------------- Q5: collateral lens
def q5_collateral(w, S):
    cov = w.FL155035015 / w.FL153165105
    veh = w.FL155111005 / w.FL153166400
    rev, stu = w.FL153166100, w.FL153166220
    unc = (rev + stu) / S.total
    rev_sh = rev / S.total
    rows = []
    for p, t in NBER.items():
        P, T = qd(p), qd(t)
        E = P + pd.offsets.QuarterEnd(16)
        row = {"crisis": p, "trough": t}
        for lab, x in (("peak", P), ("trough", T), ("t16", E)):
            row[f"home_cov_{lab}"] = round(cov[x], 3) if x in cov.index else None
            row[f"equity_share_{lab}"] = round(1 - 1 / cov[x], 3) if x in cov.index else None
            row[f"uncoll_share_{lab}"] = round(unc[x], 4) if x in unc.index else None
            row[f"revolving_share_{lab}"] = round(rev_sh[x], 4) if x in rev_sh.index else None
            row[f"vehicle_cov_{lab}"] = round(veh[x], 3) if x in veh.index else None
        # min coverage in the window
        win = cov.loc[P:E]
        row["home_cov_min"] = round(win.min(), 3)
        row["home_cov_min_q"] = qs(win.idxmin())
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(TAB / "collateral_crisis.csv", index=False)
    R["collateral_crisis"] = rows
    R["collateral"] = {
        "revolving_first_q": qs(rev[rev > 0].index[0]), "student_first_q": qs(stu[stu > 0].index[0]),
        "other_nonrev_2005Q4_busd": round(w.FL153166205[qd("2005Q4")] / 1e3, 1),
        "other_nonrev_2006Q1_busd": round(w.FL153166205[qd("2006Q1")] / 1e3, 1),
        "student_2006Q1_busd": round(stu[qd("2006Q1")] / 1e3, 1),
        # 1977Q1 reclassification: revolving jumps while other non-revolving falls by about the same amount
        "revolving_1976Q4_busd": round(rev[qd("1976Q4")] / 1e3, 1), "revolving_1977Q1_busd": round(rev[qd("1977Q1")] / 1e3, 1),
        "other_nonrev_1976Q4_busd": round(w.FL153166205[qd("1976Q4")] / 1e3, 1),
        "other_nonrev_1977Q1_busd": round(w.FL153166205[qd("1977Q1")] / 1e3, 1),
        "revolving_share_1976Q4": round(rev_sh[qd("1976Q4")], 4), "revolving_share_1977Q1": round(rev_sh[qd("1977Q1")], 4),
        "uncoll_share_2005Q4_rev_only": round(unc[qd("2005Q4")], 4), "uncoll_share_2006Q1": round(unc[qd("2006Q1")], 4),
        "uncoll_latest": round(unc.iloc[-1], 4), "revolving_latest": round(rev_sh.iloc[-1], 4),
        "student_latest_share": round(stu.iloc[-1] / S.total.iloc[-1], 4),
        "uncoll_max": round(unc.max(), 4), "uncoll_max_q": qs(unc.idxmax()),
        "revolving_share_max": round(rev_sh.max(), 4), "revolving_share_max_q": qs(rev_sh.idxmax()),
        "home_cov_latest": round(cov.iloc[-1], 3), "home_cov_min_all": round(cov.min(), 3), "home_cov_min_q": qs(cov.idxmin()),
        "home_cov_max_all": round(cov.max(), 3), "home_cov_max_q": qs(cov.idxmax()),
        "home_cov_2006Q1": round(cov[qd("2006Q1")], 3),
        "home_cov_last_q_at_or_above_latest_before_2022": qs(cov.loc[:"2021"][cov.loc[:"2021"] >= cov.iloc[-1]].index.max()),
        "home_cov_max_1965_2021": round(cov.loc["1965":"2021"].max(), 3), "home_cov_max_1965_2021_q": qs(cov.loc["1965":"2021"].idxmax()),
        "home_cov_max_since_2022": round(cov.loc["2022":].max(), 3), "home_cov_max_since_2022_q": qs(cov.loc["2022":].idxmax()),
        "vehicle_cov_latest": round(veh.iloc[-1], 3), "vehicle_cov_1990Q3": round(veh[qd("1990Q3")], 3),
        "vehicle_cov_2007Q4": round(veh[qd("2007Q4")], 3), "vehicle_cov_min": round(veh.min(), 3), "vehicle_cov_min_q": qs(veh.idxmin()),
        "auto_share_latest": round(w.FL153166400.iloc[-1] / S.total.iloc[-1], 4),
        "home_share_latest": round(S.mort.iloc[-1] / S.total.iloc[-1], 4),
        "other_nonrev_share_latest": round(w.FL153166205.iloc[-1] / S.total.iloc[-1], 4),
    }
    # federal student loans as share of all student loans
    R["collateral"]["fed_share_of_student_latest"] = round(w.FL313066220.iloc[-1] / stu.iloc[-1], 3)
    R["collateral"]["fed_share_of_student_2007Q4"] = round(w.FL313066220[qd("2007Q4")] / stu[qd("2007Q4")], 3)

    fig, axs = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True)
    ax = axs[0]
    ax.plot(cov.index, cov, color="#1baf7a")
    crisis_bands(ax)
    ax.axhline(1, color="#c3c2b7", lw=1)
    ax.set_title("Home-backed coverage: owner-occupied real estate ÷ household mortgages")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}×"))
    ax = axs[1]
    ax.plot(rev_sh.index, rev_sh, color="#e34948", label="Revolving (cards) only, 1968+")
    ax.plot(unc.loc["2006":].index, unc.loc["2006":], color=INK, label="Revolving + student loans, 2006+")
    crisis_bands(ax)
    pct_axis(ax)
    ax.set_title("Uncollateralized debt as a share of mortgages + consumer credit")
    ax.legend(fontsize=8.5, loc="upper left")
    save(fig, "q5_collateral.png")

    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.plot(veh.index, veh, color="#eda100")
    crisis_bands(ax)
    ax.set_title("Vehicle proxy: all consumer durables ÷ auto loans (overstates vehicle collateral)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}×"))
    save(fig, "q5_vehicle_proxy.png")
    return cov, unc


# ----------------------------------------------------------------------------- Q6: linking the lenses
def q6_link(w, S, mb, cb):
    pub_m = mb[PUBLIC].sum(axis=1)
    pub_c = cb[PUBLIC].sum(axis=1)  # federal student loans (FL313066220) + Sallie Mae as GSE (FL403066005)
    pub = pub_m + pub_c
    unc_sh = pub_c / pub
    rows = []
    for q in list(NBER):
        P = qd(q)
        E = P + pd.offsets.QuarterEnd(16)
        dm, dc = pub_m[E] - pub_m[P], pub_c[E] - pub_c[P]
        rows.append({"crisis": q, "d_public_busd": round((dm + dc) / 1e3, 1), "d_public_mortgage_busd": round(dm / 1e3, 1),
                     "d_public_cc_busd": round(dc / 1e3, 1),
                     "cc_share_of_increase": round(dc / (dm + dc), 3) if (dm + dc) > 0 else None,
                     "public_book_cc_share_t0": round(unc_sh[P], 4), "public_book_cc_share_t16": round(unc_sh[E], 4)})
    pd.DataFrame(rows).to_csv(TAB / "public_book_mix.csv", index=False)
    R["public_book_windows"] = rows
    # public share of each collateral class
    stu = w.FL153166220
    R["public_book"] = {
        "cc_share_1990Q3": round(unc_sh[qd("1990Q3")], 4), "cc_share_2007Q4": round(unc_sh[qd("2007Q4")], 4),
        "cc_share_2011Q4": round(unc_sh[qd("2011Q4")], 4), "cc_share_latest": round(unc_sh.iloc[-1], 4),
        "cc_share_max": round(unc_sh.max(), 4), "cc_share_max_q": qs(unc_sh.idxmax()),
        "public_mortgage_latest_busd": round(pub_m.iloc[-1] / 1e3, 1), "public_cc_latest_busd": round(pub_c.iloc[-1] / 1e3, 1),
        "public_share_of_home_backed_latest": round(S.share_m.iloc[-1], 4),
        "public_share_of_student_latest": round(cb.federal_direct.iloc[-1] / stu.iloc[-1], 4),
        "public_share_of_uncoll_latest": round(cb.federal_direct.iloc[-1] / (stu.iloc[-1] + w.FL153166100.iloc[-1]), 4),
        "public_share_of_uncoll_2007Q4": round(cb.federal_direct[qd("2007Q4")] / (stu[qd("2007Q4")] + w.FL153166100[qd("2007Q4")]), 4),
        # since 2007Q4: total public dollar increase split
        "since_2007Q4_d_public_busd": round((pub.iloc[-1] - pub[qd("2007Q4")]) / 1e3, 1),
        "since_2007Q4_d_public_mortgage_busd": round((pub_m.iloc[-1] - pub_m[qd("2007Q4")]) / 1e3, 1),
        "since_2007Q4_d_public_cc_busd": round((pub_c.iloc[-1] - pub_c[qd("2007Q4")]) / 1e3, 1),
    }
    # home coverage applied to the public vs private mortgage book is identical by construction (no holder-level LTV).
    fig, ax = plt.subplots(figsize=(10, 3.6))
    r = pub.loc["1970":]
    ax.stackplot(r.index, pub_m.loc["1970":] / 1e6, pub_c.loc["1970":] / 1e6, colors=["#1baf7a", "#1c5cab"],
                 labels=["Public mortgages (home-backed)", "Public consumer credit (student loans, uncollateralized)"],
                 edgecolor="#fcfcfb", linewidth=0.6)
    crisis_bands(ax, "1970", over=True)
    ax.set_ylabel("$ trillions")
    ax.set_title("What the public sector holds: mostly home-backed, a growing slice unsecured")
    ax.legend(fontsize=8.5, loc="upper left")
    save(fig, "q6_public_book.png")


# ----------------------------------------------------------------------------- Q7: now
def q7_now(w, S, cov, unc):
    L = S.index[-1]
    P = S.index[-2]
    Y = L - pd.offsets.QuarterEnd(4)
    cpi = q_end(load_fred("CPIAUCSL"), "mean")
    dpi = q_end(load_fred("DSPI"), "mean")
    ur = q_end(load_fred("UNRATE"), "mean")
    cs = q_end(load_fred("CSUSHPINSA"), "last")
    d = {
        "quarter": qs(L), "scope_total_busd": round(S.total[L] / 1e3, 1), "mort_busd": round(S.mort[L] / 1e3, 1),
        "cc_busd": round(S.cc[L] / 1e3, 1), "d_mort_qoq_busd": round((S.mort[L] - S.mort[P]) / 1e3, 1),
        "d_cc_qoq_busd": round((S.cc[L] - S.cc[P]) / 1e3, 1), "d_total_qoq_busd": round((S.total[L] - S.total[P]) / 1e3, 1),
        "d_total_yoy_pct": round(100 * (S.total[L] / S.total[Y] - 1), 2),
        "public_share": round(S.share[L], 4), "public_share_prev_q": round(S.share[P], 4),
        "public_share_yoy_pp": round(100 * (S.share[L] - S.share[Y]), 2),
        "public_share_mort": round(S.share_m[L], 4), "public_share_cc": round(S.share_c[L], 4),
        "home_cov": round(cov[L], 3), "home_cov_prev_q": round(cov[P], 3), "home_cov_yoy": round(cov[Y], 3),
        "uncoll_share": round(unc[L], 4), "uncoll_share_yoy": round(unc[Y], 4),
        "total_liab_busd": round(w.FL154190005[L] / 1e3, 1), "scope_of_total_liab": round(S.total[L] / w.FL154190005[L], 4),
        "debt_to_dpi": round(S.total[L] / 1e3 / dpi[L], 3) if L in dpi.index else None,
        "debt_to_dpi_2007Q4": round(S.total[qd("2007Q4")] / 1e3 / dpi[qd("2007Q4")], 3),
        "debt_to_dpi_max": round((S.total / 1e3 / dpi).max(), 3), "debt_to_dpi_max_q": qs((S.total / 1e3 / dpi).idxmax()),
        "unrate": round(ur[L], 2) if L in ur.index else None,
        "cs_yoy_pct": round(100 * (cs[L] / cs[Y] - 1), 2) if L in cs.index else None,
        "real_total_vs_2007Q4_pct": round(100 * ((S.total[L] / cpi[L]) / (S.total[qd("2007Q4")] / cpi[qd("2007Q4")]) - 1), 1),
    }
    # quarters with qoq decline in household mortgage liability since 2008
    dm = S.mort.diff()
    d["mort_declining_quarters_since_2019"] = [qs(i) for i in dm.loc["2019":].index[dm.loc["2019":] < 0]]
    tot_d = S.total.diff()
    d["total_declining_quarters_since_2019"] = [qs(i) for i in tot_d.loc["2019":].index[tot_d.loc["2019":] < 0]]
    R["now"] = d
    # policy shocks (short windows)
    sh = []
    for q in SHOCKS:
        t0 = qd(q)
        sh.append({"shock": q, "share_t0": round(S.share[t0], 4), "share_latest": round(S.share[L], 4),
                   "quarters": int(round((L - t0).days / 91.3)), "d_pp": round(100 * (S.share[L] - S.share[t0]), 2)})
    R["shocks"] = sh


# ----------------------------------------------------------------------------- the ratchet chart
def fig_ratchet(S, fed_share):
    bs = BS
    fig, ax = plt.subplots(figsize=(11, 4.8))
    crisis_bands(ax, over=True)
    ax.stackplot(bs.index, [bs[b] for b in BUCKETS], colors=[COLOR[b] for b in BUCKETS], labels=[LABEL[b] for b in BUCKETS],
                 edgecolor="#fcfcfb", linewidth=0.4, alpha=0.95)
    ax.plot(S.index, S.share, color=INK, lw=2, label="Public share (federal + GSE/agency + state & local)")
    ax.plot(fed_share.index, fed_share, color="#fcfcfb", lw=2.5)
    ax.plot(fed_share.index, fed_share, color=INK, lw=1.2, ls=(0, (3, 2)), label="Fed-held agency MBS (rate risk, not credit risk)")
    pct_axis(ax)
    ax.set_ylim(0, 1)
    ax.set_xlim(S.index[0], S.index[-1])
    ax.set_title(f"Who holds household mortgages + consumer credit, 1952–{S.index[-1].year} (grey = NBER recessions)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=8.5)
    save(fig, "ratchet.png")


def main():
    w = load_z1()
    S = build(w)
    ps, mb, cb = S["ps"], S["mb"], S["cb"]
    global BS
    BS = S["bshare"]
    ps_full = ps
    q0_verify(ps, mb, cb)
    q1_ratchet(ps, ps_full, mb, cb)
    q2_decompose(ps)
    q3_fas167(w, ps)
    q4_fed(ps, mb)
    cov, unc = q5_collateral(w, ps)
    q6_link(w, ps, mb, cb)
    q7_now(w, ps, cov, unc)
    fed = pd.read_csv(TAB / "fed_mbs.csv", index_col=0, parse_dates=True).share_scope
    fig_ratchet(ps_full, fed)
    # export the core series (for the pipeline team to cross-check mart.public_share)
    out = ps[["total", "public", "share", "share_m", "share_c"]].join(S["bshare"].add_prefix("share_"))
    out.index.name = "date"
    out.round(6).to_csv(TAB / "public_share_quarterly.csv")
    (HERE / "results.json").write_text(json.dumps(R, indent=1, default=str))
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())
