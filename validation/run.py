#!/usr/bin/env python3
"""Independent validation suite for the household-debt public-share numbers (PLAN task 0.3).

Run:  uv run --project pipeline python validation/run.py [--z1-zip PATH] [--prev-z1-zip PATH]

Deliberately does NOT import the `hhdebt` package. It re-parses the Fed Z.1 CSV zip, recomputes every
headline from the raw series and compares against published aggregates, committed snapshots, the
database (if reachable) and a previous vintage. It never changes a number; it only reports.
Exit code 1 if any check FAILs. WARN and NOT RUN do not fail the run (but NOT RUN is never a PASS).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import zparse  # noqa: E402

ROOT = HERE.parent
CATALOG = ROOT / "pipeline" / "series_catalog.yaml"
SNAPSHOT = ROOT / "web" / "public" / "data" / "public_share.json"
DATA_DIR = ROOT / "data" / "validation"
Z1_URL = "https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip"
PREV_RELEASE = "20260611"  # June 2026 release folder on the Fed's site
PREV_CANDIDATES = [
    f"https://www.federalreserve.gov/releases/z1/{PREV_RELEASE}/",
    f"https://www.federalreserve.gov/releases/z1/{PREV_RELEASE}/data/FRB_Z1_csv.zip",
    f"https://www.federalreserve.gov/releases/z1/{PREV_RELEASE}/FRB_Z1_csv.zip",
    f"https://www.federalreserve.gov/releases/z1/{PREV_RELEASE}/Z1_csv.zip",
    f"https://www.federalreserve.gov/releases/z1/{PREV_RELEASE}/z1_csv_files.zip",
]
FIRST_Q = pd.Timestamp("1952-03-31")
ID_TOL = 0.5          # $M, identity tolerance
JUMP_Z = 6.0          # robust-z threshold on quarter-on-quarter change of a share
JUMP_MIN_PP = 1.0     # ...and the change must also be at least this many percentage points
Z_SCALE_FLOOR = 0.001 # robust-z scale never below 0.1 pp (stops near-zero MAD inflating z)
KNOWN_BREAKS = ["1968-03-31", "1977-03-31", "2006-03-31", "2010-03-31"]


@dataclass
class Check:
    id: str
    description: str
    expected: str
    observed: str
    tolerance: str
    status: str  # PASS / FAIL / WARN / NOT RUN
    note: str = ""


def q(ts) -> str:
    ts = pd.Timestamp(ts)
    return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"


# ----------------------------------------------------------------------------------------------
# data model
# ----------------------------------------------------------------------------------------------
def load_catalog():
    cat = yaml.safe_load(CATALOG.read_text())
    rows = [s for s in cat["series"] if s["source"] == "z1"]
    public = {k for k, v in cat["risk_buckets"].items() if v["public"]}
    groups = {
        "mort_holders": [s for s in rows if s["role"] == "mortgage_holder"],
        "cc_holders": [s for s in rows if s["role"] == "cc_holder"],
        "cc_types": [s for s in rows if s["role"] == "cc_type"],
    }
    return cat, rows, public, groups


def to_frame(series: dict) -> pd.DataFrame:
    df = pd.DataFrame(series).sort_index()
    df.index = pd.to_datetime(df.index)
    return df


def compute(df: pd.DataFrame, groups, public) -> pd.DataFrame:
    """Recompute scope, public and shares from components (independent of hhdebt)."""
    mh = groups["mort_holders"]
    pub_m = [s["id"] for s in mh if s["risk_bucket"] in public]
    pub_c = [s["id"] for s in groups["cc_holders"] if s["risk_bucket"] in public]
    out = pd.DataFrame(index=df.index)
    out["scope"] = df["FL154104015"]
    out["mort"] = df["FL153165105"]
    out["cc"] = df["FL153166000"]
    out["pub_mort"] = df[pub_m].sum(axis=1, min_count=len(pub_m)) / df["FL893065105"] * df["FL153165105"]
    out["pub_cc"] = df[pub_c].sum(axis=1, min_count=len(pub_c))
    out["public"] = out["pub_mort"] + out["pub_cc"]
    out["share"] = out["public"] / out["scope"]
    out["share_mort"] = out["pub_mort"] / out["mort"]
    out["share_cc"] = out["pub_cc"] / out["cc"]
    return out


def pct(x, nd=1) -> str:
    return f"{x * 100:.{nd}f}%"


# ----------------------------------------------------------------------------------------------
# (a) identities
# ----------------------------------------------------------------------------------------------
def check_identities(df, groups):
    q_ = df[df.index >= FIRST_Q]
    mh = [s["id"] for s in groups["mort_holders"]]
    ch = [s["id"] for s in groups["cc_holders"]]
    ct = [s["id"] for s in groups["cc_types"]]
    specs = [
        ("A1", f"{len(mh)} mortgage holders sum to FL893065105", q_[mh].sum(axis=1, min_count=len(mh)), q_["FL893065105"]),
        ("A2", f"{len(ch)} consumer-credit holders sum to FL153166000", q_[ch].sum(axis=1, min_count=len(ch)), q_["FL153166000"]),
        ("A3", f"{len(ct)} consumer-credit types sum to FL153166000", q_[ct].sum(axis=1, min_count=len(ct)), q_["FL153166000"]),
        ("A4", "FL153165105 + FL153166000 = FL154104015", q_["FL153165105"] + q_["FL153166000"], q_["FL154104015"]),
    ]
    out = []
    for cid, desc, lhs, rhs in specs:
        diff = (lhs - rhs).abs()
        n_nan = int(diff.isna().sum())
        if n_nan or diff.empty:
            out.append(Check(cid, desc, "max |diff| <= 0.5", f"{n_nan} quarters not computable", "$0.5M", "FAIL",
                             "missing component values"))
            continue
        worst = diff.idxmax()
        out.append(Check(cid, desc + f", {q(q_.index[0])}-{q(q_.index[-1])}", "max |diff| <= $0.5M",
                         f"max |diff| ${diff.max():.3f}M ({len(diff)} qtrs)", "$0.5M",
                         "PASS" if diff.max() <= ID_TOL else "FAIL",
                         f"worst quarter {q(worst)}"))
    return out


# ----------------------------------------------------------------------------------------------
# (b) reconciliation
# ----------------------------------------------------------------------------------------------
def check_reconcile(df, groups, public, cat):
    mh, ch = groups["mort_holders"], groups["cc_holders"]
    out, n = [], 0
    for d in ["1990-09-30", "2007-12-31", "2011-12-31", "2026-06-30"]:
        t = pd.Timestamp(d)
        tag = q(t)
        if t not in df.index:
            for k in range(4):
                n += 1
                out.append(Check(f"B{n}", f"{tag} reconciliation", "-", "quarter absent", "$0.5M", "FAIL", "date missing in Z.1"))
            continue
        r = df.loc[t]
        mort_app = sum(r[s["id"]] / r["FL893065105"] * r["FL153165105"] for s in mh)
        cc_sum = sum(r[s["id"]] for s in ch)
        scope_re = mort_app + cc_sum
        pub = sum(r[s["id"]] / r["FL893065105"] * r["FL153165105"] for s in mh if s["risk_bucket"] in public) \
            + sum(r[s["id"]] for s in ch if s["risk_bucket"] in public)
        priv = sum(r[s["id"]] / r["FL893065105"] * r["FL153165105"] for s in mh if s["risk_bucket"] not in public) \
            + sum(r[s["id"]] for s in ch if s["risk_bucket"] not in public)
        rows = [
            (f"{tag} mortgages: sum of apportioned holders vs FL153165105", mort_app, r["FL153165105"], f"${mort_app:,.1f}M"),
            (f"{tag} consumer credit: sum of holders vs FL153166000", cc_sum, r["FL153166000"], f"${cc_sum:,.1f}M"),
            (f"{tag} scope total: holders vs FL154104015", scope_re, r["FL154104015"], f"${scope_re:,.1f}M"),
            (f"{tag} public + private vs FL154104015 (public share {pct(pub / r['FL154104015'], 2)})", pub + priv,
             r["FL154104015"], f"pub ${pub:,.0f}M+priv ${priv:,.0f}M"),
        ]
        for desc, got, want, obs in rows:
            n += 1
            diff = abs(got - want)
            out.append(Check(f"B{n}", desc, f"= ${want:,.1f}M", f"{obs}; diff {diff:.3f}", "$0.5M",
                             "PASS" if diff <= ID_TOL else "FAIL"))
    return out


# ----------------------------------------------------------------------------------------------
# (c) headlines
# ----------------------------------------------------------------------------------------------
def check_headlines(res):
    s = res["share"]
    first, last = s.index[s.index >= FIRST_Q][0], s.index[-1]
    t07, t11 = pd.Timestamp("2007-12-31"), pd.Timestamp("2011-12-31")
    out = []

    def rnd(cid, desc, expected, got_str, ok, note=""):
        out.append(Check(cid, desc, expected, got_str, "rounded as published", "PASS" if ok else "FAIL", note))

    v = s[first]
    rnd("C1", f"Public share {q(first)}", "3.2%", pct(v, 2), round(v * 100, 1) == 3.2)
    v = s[last]
    rnd("C2", f"Public share {q(last)}", "56.4%", pct(v, 2), round(v * 100, 1) == 56.4)
    pub_t, scope_t = res["public"][last] / 1e6, res["scope"][last] / 1e6
    rnd("C3", f"Public $ and scope {q(last)}", "$10.77T of $19.10T", f"${pub_t:.3f}T of ${scope_t:.3f}T",
        round(pub_t, 2) == 10.77 and round(scope_t, 2) == 19.10)
    a, b = s[t07], s[t11]
    ok = round(a * 100, 1) == 36.1 and round(b * 100, 1) == 49.2
    rnd("C4", "Public share 2007Q4 -> 2011Q4", "36.1% -> 49.2%", f"{pct(a, 2)} -> {pct(b, 2)}", ok)
    pp = (b - a) * 100
    rnd("C5", "Jump 2007Q4 -> 2011Q4", "+13.1 pp", f"+{pp:.2f} pp (rounded pts: {round(b*100,1)-round(a*100,1):+.1f})",
        round(pp, 1) == 13.1)
    imax = s.idxmax()
    rnd("C6", "All-time high public share", "58.6% in 2021Q1", f"{pct(s[imax], 2)} in {q(imax)}",
        round(s[imax] * 100, 1) == 58.6 and q(imax) == "2021Q1")
    vm, vc = res["share_mort"][last], res["share_cc"][last]
    rnd("C7", f"{q(last)} public share of mortgages", "65.6%", pct(vm, 2), round(vm * 100, 1) == 65.6)
    rnd("C8", f"{q(last)} public share of consumer credit", "31.3%", pct(vc, 2), round(vc * 100, 1) == 31.3)

    # never reversed: two readings
    post = s[s.index >= pd.Timestamp("2012-03-31")]
    mn_q, mn = post.idxmin(), post.min()
    h_i, h_ii = mn >= b, mn >= a
    obs = f"min {pct(mn, 2)} in {q(mn_q)}; vs 2011Q4 {pct(b, 2)} ({(mn-b)*100:+.2f} pp); vs 2007Q4 {pct(a, 2)} ({(mn-a)*100:+.2f} pp)"
    if h_i:
        st, note = "PASS", "(i) holds: share never fell below its 2011Q4 level after 2011Q4"
    elif h_ii:
        st, note = "FAIL", "(i) fails, (ii) holds: only the weaker claim 'never fell back to the 2007Q4 level' is supported; the claim needs rewording"
    else:
        st, note = "FAIL", "neither (i) nor (ii) holds"
    out.append(Check("C9", "'The 2007-11 jump never reversed': min share 2012Q1..latest", ">= 2011Q4 level (i); also report vs 2007Q4 (ii)",
                     obs, "none (strict)", st, note))
    return out


# ----------------------------------------------------------------------------------------------
# (d) snapshots and database
# ----------------------------------------------------------------------------------------------
SNAP_FIELDS = [("scope_total_musd", "scope", 1.0), ("public_musd", "public", 1.0),
               ("public_share", "share", 1e-6), ("public_share_mortgage", "share_mort", 1e-6),
               ("public_share_cc", "share_cc", 1e-6)]


def compare_rows(rows: list[dict], res: pd.DataFrame, label: str, cid: str):
    snap = pd.DataFrame(rows)
    snap["date"] = pd.to_datetime(snap["date"])
    snap = snap.set_index("date").sort_index()
    ours = res.dropna(subset=["scope"])
    missing = sorted(set(ours.index[ours.index >= FIRST_Q]) - set(snap.index))
    extra = sorted(set(snap.index) - set(ours.index))
    out = []
    worst_all, bad = [], False
    for fld, col, tol in SNAP_FIELDS:
        j = snap[fld].astype(float).to_frame("s").join(ours[col].to_frame("o"), how="inner")
        d = (j["s"] - j["o"]).abs()
        both_nan_mismatch = int((j["s"].isna() ^ j["o"].isna()).sum())
        mx = d.max() if len(d.dropna()) else float("nan")
        ok = (mx <= tol) and both_nan_mismatch == 0
        bad |= not ok
        worst_all.append(f"{fld} {mx:.2e}" if tol < 1 else f"{fld} ${mx:.3f}M")
    cov_ok = not missing and not extra
    out.append(Check(cid, f"{label} vs recomputation, every quarter ({len(snap)} rows)",
                     "max abs diff within tol; same quarter set", "; ".join(worst_all)
                     + ("" if cov_ok else f"; missing {len(missing)} extra {len(extra)}"),
                     "1e-6 shares, $1M levels", "FAIL" if (bad or not cov_ok) else "PASS",
                     "" if cov_ok else f"missing: {[q(m) for m in missing][:5]} extra: {[q(e) for e in extra][:5]}"))
    return out


def check_snapshots(res):
    out = []
    if SNAPSHOT.exists():
        out += compare_rows(json.loads(SNAPSHOT.read_text()), res, "web/public/data/public_share.json", "D1")
    else:
        out.append(Check("D1", "committed snapshot web/public/data/public_share.json", "file present", "missing",
                         "-", "FAIL", str(SNAPSHOT)))
    url = os.environ.get("DATABASE_URL_READONLY")
    if not url:
        out.append(Check("D2", "mart.public_share (database) vs recomputation", "match", "DATABASE_URL_READONLY not set",
                         "1e-6 shares, $1M levels", "NOT RUN", "no read-only database URL in the environment"))
        return out
    try:
        import psycopg
        with psycopg.connect(url, connect_timeout=15, options="-c default_transaction_read_only=on") as con:
            con.read_only = True
            with con.cursor() as cur:
                cur.execute("select date, scope_total_musd, public_musd, public_share, public_share_mortgage, "
                            "public_share_cc from mart.public_share order by date")
                cols = [c.name for c in cur.description]
                rows = [dict(zip(cols, [float(v) if hasattr(v, "as_tuple") else v for v in r])) for r in cur.fetchall()]
        for r in rows:
            r["date"] = str(r["date"])
        out += compare_rows(rows, res, "mart.public_share", "D2")
    except Exception as e:  # connection problems are NOT a pass
        out.append(Check("D2", "mart.public_share (database) vs recomputation", "match", f"{type(e).__name__}",
                         "1e-6 shares, $1M levels", "NOT RUN", f"could not query database: {str(e)[:120]}"))
    return out


# ----------------------------------------------------------------------------------------------
# (e) breaks and gaps
# ----------------------------------------------------------------------------------------------
def share_panel(df, groups) -> dict[str, pd.Series]:
    """Share of its own total, for every catalog component series (the quantity whose jumps we track)."""
    panel = {}
    for s in groups["mort_holders"]:
        panel[s["id"]] = df[s["id"]] / df["FL893065105"]
    for s in groups["cc_holders"] + groups["cc_types"]:
        panel[s["id"]] = df[s["id"]] / df["FL153166000"]
    panel["FL153165105"] = df["FL153165105"] / df["FL154104015"]
    panel["FL153166000"] = df["FL153166000"] / df["FL154104015"]
    return panel


def robust_z(dq: pd.Series) -> pd.Series:
    med = dq.median()
    mad = (dq - med).abs().median()
    scale = max(1.4826 * mad, Z_SCALE_FLOOR)
    return (dq - med) / scale


def find_jumps(df, groups):
    panel = share_panel(df, groups)
    jumps = []
    for sid, ser in panel.items():
        ser = ser[ser.index >= FIRST_Q]
        dq = ser.diff().dropna()
        z = robust_z(dq)
        for t in dq.index[(z.abs() > JUMP_Z) & (dq.abs() * 100 >= JUMP_MIN_PP)]:
            jumps.append({"series": sid, "quarter": q(t), "date": t.strftime("%Y-%m-%d"),
                          "delta_pp": float(dq[t] * 100), "robust_z": float(z[t])})
    return jumps, panel


def check_breaks(df, groups, res, desc_of):
    out, jumps, panel = [], *find_jumps(df, groups)
    by_q = {}
    for j in jumps:
        by_q.setdefault(j["date"], []).append(j)

    def best(sid, t):
        ser = panel[sid][panel[sid].index >= FIRST_Q]
        dq = ser.diff().dropna()
        z = robust_z(dq)
        return dq[pd.Timestamp(t)] * 100, z[pd.Timestamp(t)]

    # 1968Q1
    rev = df["FL153166100"]
    first_pos = rev[rev > 0].index[0]
    ok = first_pos == pd.Timestamp("1968-03-31") and (rev[rev.index < first_pos] == 0).all()
    out.append(Check("E1", "1968Q1: revolving credit (FL153166100) starts", "zero before, > 0 from 1968Q1",
                     f"first positive {q(first_pos)} (${rev[first_pos]:,.0f}M)", "exact", "PASS" if ok else "FAIL"))
    # 1977Q1: reclassification, look at cc type shares
    cands = {sid: best(sid, "1977-03-31") for sid in [s["id"] for s in groups["cc_types"]]}
    sid, (dpp, z) = max(cands.items(), key=lambda kv: abs(kv[1][1]))
    vis = abs(z) > JUMP_Z and abs(dpp) >= JUMP_MIN_PP
    out.append(Check("E2", "1977Q1: revolving reclassification visible in cc-type shares", f"|robust z| > {JUMP_Z:g} in a cc type",
                     f"{sid} {dpp:+.2f} pp of cc, z={z:+.1f}", f"z>{JUMP_Z:g} & >={JUMP_MIN_PP}pp",
                     "PASS" if vis else "WARN", "" if vis else "break not detectable at the documented threshold"))
    # 2006Q1
    st = df["FL153166220"]
    sp = st[st > 0].index[0]
    onr = df["FL153166205"]
    drop = onr[sp] - onr[sp - pd.offsets.QuarterEnd(1)]
    ok = sp == pd.Timestamp("2006-03-31")
    out.append(Check("E3", "2006Q1: student loans (FL153166220) split out of other non-revolving", "first positive 2006Q1",
                     f"first positive {q(sp)} (${st[sp]:,.0f}M); other non-revolving {drop:+,.0f}M q/q", "exact",
                     "PASS" if ok else "FAIL", "student loans are zero before; inside other non-revolving"))
    # 2010Q1: GSE (40) up, pools (41) down, card ABS (67) down, banks (76) up; 40+41 continuous
    t = pd.Timestamp("2010-03-31")
    p = pd.Timestamp("2009-12-31")
    d40 = (df.loc[t, "FL403065105"] - df.loc[p, "FL403065105"]) / 1e6
    d41 = (df.loc[t, "FL413065105"] - df.loc[p, "FL413065105"]) / 1e6
    ok = d40 > 0 and d41 < 0
    s40, s41 = best("FL403065105", t), best("FL413065105", t)
    out.append(Check("E4", "2010Q1 FAS 166/167: GSE pools move from sector 41 to 40", "40 up, 41 down at 2010Q1",
                     f"FL403065105 {d40:+.2f}T (z={s40[1]:+.1f}); FL413065105 {d41:+.2f}T (z={s41[1]:+.1f})",
                     "sign + visible", "PASS" if ok and abs(s40[1]) > JUMP_Z else ("WARN" if ok else "FAIL")))
    dabs = (df.loc[t, "FL673066000"] - df.loc[p, "FL673066000"]) / 1e6
    dbk = (df.loc[t, "FL763066005"] - df.loc[p, "FL763066005"]) / 1e6
    zabs, zbk = best("FL673066000", t)[1], best("FL763066005", t)[1]
    ok = dabs < 0 and dbk > 0
    out.append(Check("E5", "2010Q1 FAS 166/167: card ABS moves onto banks (cc holders)", "ABS issuers down, banks up",
                     f"ABS {dabs:+.2f}T (z={zabs:+.1f}); banks {dbk:+.2f}T (z={zbk:+.1f})", "sign + visible",
                     "PASS" if ok and abs(zabs) > JUMP_Z else ("WARN" if ok else "FAIL")))
    # continuity of public share through 2010 (40 + 41 summed)
    s = res["share"]
    ds = s.diff().dropna()
    ds = ds[ds.index >= FIRST_Q]
    z = robust_z(ds)
    win = ds[(ds.index >= "2009-12-31") & (ds.index <= "2010-12-31")]
    zmax = z[win.index].abs().max()
    mx = win.abs().max() * 100
    two = (df["FL403065105"] + df["FL413065105"]) / df["FL893065105"]
    d2 = two.diff()[(two.index >= "2009-12-31") & (two.index <= "2010-12-31")] * 100
    out.append(Check("E6", "Public share continuous through 2010 (sectors 40+41 summed)", f"no |robust z| > {JUMP_Z:g} in 2009Q4-2010Q4",
                     f"max |q/q| {mx:.2f} pp (z={zmax:.1f}); 40+41 share max |q/q| {d2.abs().max():.2f} pp",
                     f"z<={JUMP_Z:g}", "PASS" if zmax <= JUMP_Z else "FAIL",
                     "40 and 41 individually jump; the sum should not"))

    # gaps
    ids = [s["id"] for s in desc_of if True]
    grid = pd.date_range(FIRST_Q, df.index[-1], freq="QE")
    gaps = {}
    for sid in ids:
        if sid not in df:
            gaps[sid] = ["series absent"]
            continue
        ser = df[sid].dropna()
        ser = ser[ser.index >= FIRST_Q]
        miss = [q(x) for x in grid if x not in ser.index and x > ser.index[0] - pd.Timedelta(days=1)] if len(ser) else ["no data"]
        if len(ser) and ser.index[0] > FIRST_Q:
            miss = [q(x) for x in grid if x >= ser.index[0] and x not in ser.index]
        if miss:
            gaps[sid] = miss
    ends = {sid: df[sid].dropna().index[-1] for sid in ids if sid in df}
    ragged = {k: q(v) for k, v in ends.items() if v != df.index[-1]}
    out.append(Check("E7", f"No missing quarters in any of {len(ids)} Z.1 catalog series after first value ({q(grid[0])}-{q(grid[-1])})",
                     "0 gaps, common end date", f"{sum(len(v) for v in gaps.values())} gaps in {len(gaps)} series; {len(ragged)} short",
                     "exact", "PASS" if not gaps and not ragged else "FAIL",
                     "; ".join(f"{k}: {v[:3]}" for k, v in list(gaps.items())[:3]) + (f" ragged {ragged}" if ragged else "")))

    # unexplained jumps
    explained_q = set(KNOWN_BREAKS)
    unexpl = [j for j in jumps if j["date"] not in explained_q]
    expl = [j for j in jumps if j["date"] in explained_q]
    out.append(Check("E8", f"Other quarter-on-quarter jumps in component shares (robust z > {JUMP_Z:g}, >= {JUMP_MIN_PP} pp)",
                     "none unexplained", f"{len(unexpl)} unexplained (+{len(expl)} at known breaks) of {len(panel)} series",
                     f"|z|>{JUMP_Z:g} & >={JUMP_MIN_PP}pp", "PASS" if not unexpl else "WARN",
                     "see list in report" if unexpl else ""))
    return out, unexpl, expl


# ----------------------------------------------------------------------------------------------
# (f) revisions
# ----------------------------------------------------------------------------------------------
def probe_prev_vintage(log: list[str]):
    """Try the Fed's archive for the June 2026 release; returns a local zip path or None."""
    import requests
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for u in PREV_CANDIDATES:
        try:
            r = requests.get(u, timeout=60, stream=True)
            ctype = r.headers.get("content-type", "")
            log.append(f"{u} -> HTTP {r.status_code} {ctype.split(';')[0]}")
            if r.status_code == 200 and u.endswith(".zip"):
                dest = DATA_DIR / ("prev_" + u.rsplit("/", 1)[1])
                if not dest.exists():
                    with open(dest, "wb") as f:
                        for chunk in r.iter_content(1 << 20):
                            f.write(chunk)
                r.close()
                return dest
            r.close()
        except Exception as e:
            log.append(f"{u} -> {type(e).__name__}: {str(e)[:80]}")
    return None


def load_prev(path: Path, ids):
    """Previous vintage as {id: {date: value}} plus a description of the format used."""
    import zipfile
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    if "Z1.csv" in names:
        ts, _ = zparse.zip_member_info(path)
        return zparse.load_z1_zip(path, ids), ts, "Z1.csv (long format)", []
    ts = datetime(*zipfile.ZipFile(path).infolist()[1].date_time)
    ser, conflicts = zparse.load_table_zip(path, ids)
    return ser, ts, "per-table wide CSVs (z1_csv_files.zip); scope total derived as FL153165105+FL153166000", conflicts


def check_revisions(df_now, res_now, groups, public, prev_arg, urls_log):
    note_urls = ""
    prev_path = Path(prev_arg) if prev_arg else None
    if prev_path is None:
        prev_path = probe_prev_vintage(urls_log)
        note_urls = "URLs tried: " + " | ".join(urls_log)
    if prev_path is None or not Path(prev_path).exists():
        return [Check("F1", "Revisions vs previous (June 2026) vintage", "compare headlines and scope totals",
                      "no previous vintage obtained", "-", "NOT RUN", note_urls)], None
    ids = list(df_now.columns)
    ser, ts, fmt, conflicts = load_prev(Path(prev_path), ids)
    prev = to_frame(ser)
    if "FL154104015" not in prev:
        prev["FL154104015"] = prev["FL153165105"] + prev["FL153166000"]
    res_prev = compute(prev, groups, public)
    common = res_now.index.intersection(res_prev.dropna(subset=["share"]).index)
    common = common[common >= FIRST_Q]
    last_prev = common[-1]
    dscope = (res_now.loc[common, "scope"] - res_prev.loc[common, "scope"])
    dshare = (res_now.loc[common, "share"] - res_prev.loc[common, "share"]) * 100
    dpub = (res_now.loc[common, "public"] - res_prev.loc[common, "public"])
    n_rev = int((dscope.abs() > ID_TOL).sum())
    info = {"prev_path": str(prev_path), "prev_member_timestamp": ts.isoformat(), "format": fmt,
            "common_quarters": len(common), "last_common": q(last_prev), "conflicts": conflicts}
    out = []
    out.append(Check("F1", f"Scope total FL154104015 revisions, {q(common[0])}-{q(last_prev)} ({len(common)} qtrs)",
                     "report", f"{n_rev} quarters revised > $0.5M; max |rev| ${dscope.abs().max():,.0f}M in {q(dscope.abs().idxmax())}",
                     "report only", "WARN" if n_rev else "PASS", f"prev vintage {ts.date()} [{fmt}]" + (f"; duplicate-column conflicts {conflicts}" if conflicts else "")))
    out.append(Check("F2", "Public share revisions across common quarters", "report",
                     f"max |rev| {dshare.abs().max():.3f} pp in {q(dshare.abs().idxmax())}; mean {dshare.mean():+.4f} pp; "
                     f"public $ max |rev| ${dpub.abs().max():,.0f}M",
                     "headline 0.1 pp", "PASS" if dshare.abs().max() < 0.05 else "WARN"))
    rows = []
    for lab, t in [("2026Q1 (latest common)", last_prev), ("2011Q4", pd.Timestamp("2011-12-31")), ("2007Q4", pd.Timestamp("2007-12-31")),
                   ("1952Q1", FIRST_Q)]:
        if t in common:
            a, b = res_prev.loc[t, "share"], res_now.loc[t, "share"]
            rows.append(f"{lab}: {a*100:.2f}% -> {b*100:.2f}%")
    same = all(round(res_prev.loc[t, "share"] * 100, 1) == round(res_now.loc[t, "share"] * 100, 1)
               for t in [last_prev, pd.Timestamp("2011-12-31"), pd.Timestamp("2007-12-31"), FIRST_Q] if t in common)
    out.append(Check("F3", "Headline shares, previous -> current vintage", "equal at published 0.1 pp precision",
                     "; ".join(rows), "0.1 pp", "PASS" if same else "WARN"))
    hi_prev = res_prev["share"].idxmax()
    hi_now = res_now.loc[res_now.index <= last_prev, "share"].idxmax()
    out.append(Check("F4", "All-time-high quarter, previous vs current (through common quarters)", "same quarter",
                     f"prev {q(hi_prev)} {res_prev['share'].max()*100:.2f}%; now {q(hi_now)} {res_now.loc[hi_now,'share']*100:.2f}%",
                     "exact quarter", "PASS" if hi_prev == hi_now else "WARN"))
    new_q = [q(x) for x in res_now.index[res_now.index > last_prev]]
    out.append(Check("F5", "New quarter(s) in current vintage", "report", ", ".join(new_q) or "none", "-", "PASS" if new_q else "WARN",
                     note_urls))
    return out, info


# ----------------------------------------------------------------------------------------------
# output
# ----------------------------------------------------------------------------------------------
def fit(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "~"


def render_table(checks, width=100) -> str:
    wid, wst, wd = 4, 7, 40
    wo = width - wid - wst - wd - 3
    lines = [f"{'ID':<{wid}} {'STATUS':<{wst}} {'CHECK':<{wd}} OBSERVED", "-" * width]
    for c in checks:
        lines.append(f"{c.id:<{wid}} {c.status:<{wst}} {fit(c.description, wd):<{wd}} {fit(c.observed, wo)}")
    counts = {k: sum(c.status == k for c in checks) for k in ["PASS", "FAIL", "WARN", "NOT RUN"]}
    lines.append("-" * width)
    lines.append("  ".join(f"{k}: {v}" for k, v in counts.items()))
    return "\n".join(lines)


def md_table(checks) -> str:
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    lines = ["| ID | Status | Description | Expected | Observed | Tolerance | Note |", "|---|---|---|---|---|---|---|"]
    for c in checks:
        lines.append(f"| {c.id} | **{c.status}** | {esc(c.description)} | {esc(c.expected)} | {esc(c.observed)} | {esc(c.tolerance)} | {esc(c.note)} |")
    return "\n".join(lines)


def write_report(path, checks, meta, unexpl, expl, prev_info, urls_log):
    counts = {k: sum(c.status == k for c in checks) for k in ["PASS", "FAIL", "WARN", "NOT RUN"]}
    txt = f"""# Validation report

Generated by `validation/run.py`. Independent of the `hhdebt` package: re-parses the Fed Z.1 CSV and
recomputes everything from components. No number is changed by this suite; it only reports.

| | |
|---|---|
| Z.1 vintage (Z1.csv member timestamp in zip) | {meta['vintage']} |
| Latest quarter in data | {meta['latest']} |
| Zip file | `{meta['zip_name']}` ({meta['zip_bytes']:,} bytes) |
| Zip SHA-256 | `{meta['sha256']}` |
| Source URL | {Z1_URL} |
| Run timestamp (UTC) | {meta['run_at']} |
| Result | {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['WARN']} WARN, {counts['NOT RUN']} NOT RUN |

## Results

{md_table(checks)}

## Method

* Series are streamed from `Z1.csv` inside the zip (never unzipped to disk). Names look like `Z1/Z1/FL153165105.Q`;
  the last two CSV fields are date and value, in $ millions. Only `.Q` series are used.
* Series IDs and risk-bucket membership come from `pipeline/series_catalog.yaml`. Public = `federal_direct` +
  `gse_agency` + `state_local`. Mortgage holders are apportioned to households as holder / FL893065105 x FL153165105;
  consumer-credit holders are used as-is. Public share = public / FL154104015.
* (a) identities hold every quarter 1952Q1 to latest within $0.5M. (b) the same components are re-summed at four
  reference quarters and compared with the published totals. (c) each headline is recomputed and compared after
  rounding to the precision it is published at. The "never reversed" claim is tested in two readings: (i) the
  minimum share from 2012Q1 on is at least the 2011Q4 level, (ii) it is at least the 2007Q4 level; only (i) passes the check.
* (d) the committed `public_share.json` (and `mart.public_share` if `DATABASE_URL_READONLY` is set, read-only
  session) is compared quarter by quarter: tolerance 1e-6 on shares, $1M on levels.
* (e) jump rule: for every component series, the share of its own total (holders / FL893065105 for mortgages,
  holders and types / FL153166000 for consumer credit, mortgage and consumer credit / FL154104015); take the
  quarter-on-quarter change, compute a robust z = (x - median) / max(1.4826 x MAD, 0.1 pp) over 1952Q1 to latest, and flag
  |z| > {JUMP_Z:g} with |change| >= {JUMP_MIN_PP} pp (the pp floor suppresses statistically odd but economically tiny moves in
  small series). Flags at the four known break quarters are listed as explained; all others are WARN, never FAIL.
  Gaps are missing quarters between 1952Q1 and the latest quarter in any catalog Z.1 series.
* (f) previous vintage: see section below.

## Unexplained jumps (WARN)

{jump_table(unexpl)}

Count by series: {from_counts(unexpl)}

## Jumps at known break quarters (explained)

{jump_table(expl)}

## Previous-vintage lookup (f)

"""
    if prev_info:
        txt += "\n".join(f"* {k}: {v}" for k, v in prev_info.items()) + "\n"
    if urls_log:
        txt += "\nURLs tried:\n\n" + "\n".join(f"* `{u}`" for u in urls_log) + "\n"
    elif not prev_info:
        txt += "No previous vintage supplied or located.\n"
    path.write_text(txt)


def from_counts(js):
    from collections import Counter
    c = Counter(j["series"] for j in js)
    return ", ".join(f"{k} x{v}" for k, v in c.most_common()) or "none"


def jump_table(js):
    if not js:
        return "None."
    lines = ["| Quarter | Series | Change in share (pp) | Robust z |", "|---|---|---|---|"]
    for j in sorted(js, key=lambda j: (j["date"], j["series"])):
        lines.append(f"| {j['quarter']} | {j['series']} | {j['delta_pp']:+.2f} | {j['robust_z']:+.1f} |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------
def ensure_zip(arg):
    if arg:
        return Path(arg)
    dest = DATA_DIR / "FRB_Z1_csv.zip"
    if dest.exists():
        return dest
    import requests
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"downloading {Z1_URL} ...", file=sys.stderr)
    with requests.get(Z1_URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--z1-zip", help="path to FRB_Z1_csv.zip (default: data/validation/, downloaded if absent)")
    ap.add_argument("--prev-z1-zip", help="previous-vintage Z.1 zip (Z1.csv long format, or per-table z1_csv_files.zip)")
    ap.add_argument("--no-network-prev", action="store_true", help="skip probing the Fed archive for the previous vintage")
    args = ap.parse_args(argv)

    zip_path = ensure_zip(args.z1_zip)
    cat, rows, public, groups = load_catalog()
    ids = [s["id"] for s in rows]
    ts, _ = zparse.zip_member_info(zip_path)
    sha = zparse.sha256_file(zip_path)
    print(f"parsing {zip_path.name} ...", file=sys.stderr)
    df = to_frame(zparse.load_z1_zip(zip_path, ids))
    res = compute(df, groups, public)
    res_q = res[res.index >= FIRST_Q]

    checks = []
    checks += check_identities(df, groups)
    checks += check_reconcile(df, groups, public, cat)
    checks += check_headlines(res_q)
    checks += check_snapshots(res)
    e_checks, unexpl, expl = check_breaks(df, groups, res, rows)
    checks += e_checks
    urls_log: list[str] = []
    if args.no_network_prev and not args.prev_z1_zip:
        f_checks, prev_info = [Check("F1", "Revisions vs previous vintage", "compare", "skipped (--no-network-prev)", "-", "NOT RUN",
                                     "no previous vintage supplied")], None
    else:
        f_checks, prev_info = check_revisions(df, res, groups, public, args.prev_z1_zip, urls_log)
    checks += f_checks

    meta = {"vintage": ts.strftime("%Y-%m-%d %H:%M"), "latest": q(df.index[-1]), "zip_name": zip_path.name,
            "zip_bytes": zip_path.stat().st_size, "sha256": sha,
            "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
    table = render_table(checks)
    print(f"Z.1 vintage {meta['vintage']} (latest {meta['latest']})  sha256 {sha[:16]}...  run {meta['run_at']}Z")
    print(table)
    write_report(HERE / "REPORT.md", checks, meta, unexpl, expl, prev_info, urls_log)
    (HERE / "results.json").write_text(json.dumps({
        "meta": meta, "checks": [asdict(c) for c in checks], "unexplained_jumps": unexpl, "known_break_jumps": expl,
        "previous_vintage": prev_info, "previous_vintage_urls_tried": urls_log,
        "summary": {k: sum(c.status == k for c in checks) for k in ["PASS", "FAIL", "WARN", "NOT RUN"]},
    }, indent=2, default=str))
    return 1 if any(c.status == "FAIL" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
