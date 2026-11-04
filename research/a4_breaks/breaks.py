#!/usr/bin/env python3
"""PLAN task A4: structural breaks in the public share, implemented to the frozen pre-registration.

    uv run --project pipeline python research/a4_breaks/breaks.py

Pre-registration: docs/decisions/breaks.md, frozen in commit 02cc47f ("prereg: A4 (frozen)"); every choice below is
quoted from its "Decided" lines. Deviations, if any, are listed in DEVIATIONS and must also be added, dated, to the
"Deviations" section of breaks.md (a shared file: proposed to the coordinator).

Model (Decided (a), trend and unit root): first differences of the share, in percentage points, with a mean-shift
model y_t = mu_j + u_t in regime j. Sample 1952Q2-2026Q2 (297 changes), Z.1 release of 2026-09-11.
Series (Decided (b), target): total share primary; mortgage and consumer-credit shares descriptive. Computed with
validation/run.py compute(), independently of the pipeline.

Known dates (Decided (b) and date rule (b)): 2008Q1, 2008Q2, 2008Q3, 2009Q1, 2010Q3. Chow: HAC Wald test of a mean
shift at D. Holm-Bonferroni at 5% family-wise across the five on the primary series (Decided (a)).
Level step at D, descriptive (Decided (b)): robust-z of the one-quarter change, |z| > 6 and at least 1 pp, as in
validation/run.py robust_z.
Unknown dates: Bai-Perron global SSR minimisation by dynamic programming, at most M = 5 breaks (Decided (b)), trimming
eps = 0.10 (Decided (b)), h = floor(eps * T). Number of breaks: UDmax/WDmax, then sequential sup-F(l+1|l) at 5%
(Decided (a)); BIC and LWZ reported alongside. 95% confidence intervals for break dates after Bai (1997).
HAC (Decided (a)): Quadratic Spectral kernel, Andrews (1991) AR(1) automatic bandwidth, AR(1) prewhitening, error
variance allowed to differ across regimes (each regime's long-run variance is estimated on its own residuals).
Placebo (H3): the Chow test at every admissible quarter inside the trimming bounds, excluding the four measurement
quarters 1968Q1, 1977Q1, 2006Q1, 2010Q1.
Vintage sensitivity (Decided (b)): rerun on the June 2026 vintage with both samples cut to 2026Q1.
R cross-check (Decided (b) tolerance; decision rule leg 3): not runnable here (no R, CRAN unreachable), so no break
can be called "confirmed"; the verdict sentences follow the pre-registered wording with that leg unmet.

Critical values are SIMULATED here (the Bai-Perron 2003 tables are not available in this environment): the
asymptotic null distributions of sup-F(k), UDmax, WDmax and sup-F(l+1|l) are approximated by Monte Carlo on i.i.d.
normal series of length SIM_T with the same trimming, seed SEED. sup-F(l+1|l) uses the Bai-Perron (1998) result that
its limit is the maximum of l+1 independent sup-F(1) statistics, so its 5% value is the 0.95^(1/(l+1)) quantile of
the simulated sup-F(1). The Bai (1997) interval uses simulated quantiles of argmax(W(s) - |s|/2) with the
regime-specific long-run variances (heterogeneous case), see bai_ci().
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "validation"))

PREREG_COMMIT = "02cc47f"
EPS, M, ALPHA = 0.10, 5, 0.05
KNOWN = {"2008Q1": "Economic Stimulus Act of 2008", "2008Q2": "ECASLA", "2008Q3": "HERA + conservatorship",
         "2009Q1": "ARRA", "2010Q3": "SAFRA effective"}
MEASUREMENT = ["1968Q1", "1977Q1", "2006Q1", "2010Q1"]
SEED, SIM_T, SIM_N = 20261104, 600, 2000
DEVIATIONS = ["Critical values simulated (tables not available offline); see module docstring."]


# ---------------------------------------------------------------- HAC: QS kernel, Andrews AR(1) bandwidth, prewhitened
def qs_kernel(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    out = np.ones_like(x)
    nz = x != 0
    z = 6 * np.pi * x[nz] / 5
    out[nz] = 25 / (12 * np.pi ** 2 * x[nz] ** 2) * (np.sin(z) / z - np.cos(z))
    return out


def lrv(u: np.ndarray) -> float:
    """Long-run variance of a scalar residual series: AR(1) prewhitening, QS kernel, Andrews (1991) AR(1) bandwidth."""
    u = np.asarray(u, float) - 0.0
    n = len(u)
    if n < 5:
        return float(np.var(u))
    rho = float(np.dot(u[1:], u[:-1]) / np.dot(u[:-1], u[:-1]))
    rho = max(min(rho, 0.97), -0.97)  # Andrews-Monahan style bound so recolouring stays finite
    e = u[1:] - rho * u[:-1]
    m = len(e)
    # Andrews (1991) plug-in for QS on the prewhitened residuals, AR(1) approximating model
    r = float(np.dot(e[1:], e[:-1]) / np.dot(e[:-1], e[:-1])) if m > 2 else 0.0
    r = max(min(r, 0.97), -0.97)
    a2 = 4 * r ** 2 / (1 - r) ** 4
    bw = 1.3221 * (a2 * m) ** 0.2 if a2 > 0 else 0.0
    gam0 = float(np.dot(e, e) / m)
    s = gam0
    if bw > 0:
        for j in range(1, m):
            w = float(qs_kernel(np.array([j / bw]))[0])
            if abs(w) < 1e-6 and j > 5 * bw:
                break
            s += 2 * w * float(np.dot(e[j:], e[:-j]) / m)
    return s / (1 - rho) ** 2


# ---------------------------------------------------------------- Bai-Perron, mean shift
def ssr_matrix(y: np.ndarray, h: int) -> np.ndarray:
    """ssr[i, j] = SSR of a constant fitted to y[i:j+1], for segments of length >= h (else inf)."""
    n = len(y)
    c1 = np.concatenate([[0.0], np.cumsum(y)])
    c2 = np.concatenate([[0.0], np.cumsum(y * y)])
    S = np.full((n, n), np.inf)
    for i in range(n):
        j = np.arange(i + h - 1, n)
        L = j - i + 1
        s1, s2 = c1[j + 1] - c1[i], c2[j + 1] - c2[i]
        S[i, j] = s2 - s1 * s1 / L
    return S


def dp_breaks(y: np.ndarray, h: int, m_max: int):
    """Global SSR minimisation (Bai-Perron 2003 dynamic programme). Returns {m: (ssr, [break indices])}, where a break
    index b means the new regime starts at observation b."""
    n = len(y)
    S = ssr_matrix(y, h)
    best = {0: (S[0, n - 1], [])}
    # V[m][j] = min SSR of y[0:j+1] with m breaks; P[m][j] = start of the last segment
    V = {0: S[0, :].copy()}
    P = {}
    for m in range(1, m_max + 1):
        Vm = np.full(n, np.inf)
        Pm = np.full(n, -1, dtype=int)
        for j in range((m + 1) * h - 1, n):
            ks = np.arange(m * h, j - h + 2)  # start of the last segment
            if len(ks) == 0:
                continue
            cand = V[m - 1][ks - 1] + S[ks, j]
            k = int(np.argmin(cand))
            Vm[j], Pm[j] = cand[k], ks[k]
        V[m], P[m] = Vm, Pm
        if not np.isfinite(Vm[n - 1]):
            break
        bk, j = [], n - 1
        for mm in range(m, 0, -1):
            s = int(P[mm][j])
            bk.append(s)
            j = s - 1
        best[m] = (float(Vm[n - 1]), sorted(bk))
    return best


def segments(n: int, bk: list[int]) -> list[tuple[int, int]]:
    edges = [0] + list(bk) + [n]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def wald_means(y: np.ndarray, bk: list[int]) -> float:
    """Wald statistic for equal regime means, HAC and heterogeneous variances: delta' R'(R V R')^-1 R delta."""
    segs = segments(len(y), bk)
    mu = np.array([y[a:b].mean() for a, b in segs])
    v = np.array([lrv(y[a:b] - y[a:b].mean()) / (b - a) for a, b in segs])
    k = len(segs) - 1
    R = np.zeros((k, k + 1))
    for i in range(k):
        R[i, i], R[i, i + 1] = -1.0, 1.0
    d = R @ mu
    return float(d @ np.linalg.solve(R @ np.diag(v) @ R.T, d))


def supF(y: np.ndarray, bk: list[int]) -> float:
    n, k = len(y), len(bk)
    return wald_means(y, bk) / k * (n - (k + 1)) / n


def seq_test(y: np.ndarray, bk: list[int], h: int) -> tuple[float, int | None]:
    """sup-F(l+1|l): largest one-break sup-F over the l+1 segments given the l estimated breaks."""
    best, where = 0.0, None
    for a, b in segments(len(y), bk):
        seg = y[a:b]
        if len(seg) < 2 * h:
            continue
        for s in range(h, len(seg) - h + 1):
            f = supF(seg, [s])
            if f > best:
                best, where = f, a + s
    return best, where


# ---------------------------------------------------------------- simulated critical values
def simulate_cvs(h_frac: float = EPS, m_max: int = M, n: int = SIM_T, reps: int = SIM_N, seed: int = SEED) -> dict:
    """Null distribution under i.i.d. N(0,1): sup-F(k) at the SSR-minimising partition (as in the test), k = 1..M.
    Known variance (1) is used in the simulation so that the statistic is the limit functional, not its HAC estimate."""
    rng = np.random.default_rng(seed)
    h = int(h_frac * n)
    F = np.zeros((reps, m_max))
    for r in range(reps):
        y = rng.standard_normal(n)
        best = dp_breaks(y, h, m_max)
        for k in range(1, m_max + 1):
            segs = segments(n, best[k][1])
            mu = np.array([y[a:b].mean() for a, b in segs])
            v = np.array([1.0 / (b - a) for a, b in segs])
            R = np.zeros((k, k + 1))
            for i in range(k):
                R[i, i], R[i, i + 1] = -1.0, 1.0
            d = R @ mu
            F[r, k - 1] = float(d @ np.linalg.solve(R @ np.diag(v) @ R.T, d)) / k
    cv = {k: float(np.quantile(F[:, k - 1], 1 - ALPHA)) for k in range(1, m_max + 1)}
    ud = F.max(axis=1)
    wd = (F * np.array([cv[1] / cv[k] for k in range(1, m_max + 1)])).max(axis=1)
    seq = {l: float(np.quantile(F[:, 0], (1 - ALPHA) ** (1 / (l + 1)))) for l in range(1, m_max)}
    return {"supF": cv, "UDmax": float(np.quantile(ud, 1 - ALPHA)), "WDmax": float(np.quantile(wd, 1 - ALPHA)),
            "seq": seq, "sim": {"T": n, "reps": reps, "seed": seed, "h": h}}


def argmax_quantiles(phi: float, reps: int = 4000, smax: float = 200.0, ds: float = 0.02, seed: int = SEED) -> tuple[float, float]:
    """2.5% and 97.5% quantiles of argmax_s Z(s): Z(s) = W1(-s) - |s|/2 (s<0), sqrt(phi) W2(s) - |s|/2 (s>0).
    This is Bai (1997) / Bai-Perron (1998) for a mean shift (xi = 1) with long-run variance ratio phi = w2^2 / w1^2,
    scaled by (delta^2 / w1^2)."""
    rng = np.random.default_rng(seed)
    g = np.arange(ds, smax + ds, ds)
    out = np.empty(reps)
    for r in range(reps):
        wl = np.cumsum(rng.standard_normal(len(g)) * math.sqrt(ds)) - g / 2
        wr = math.sqrt(phi) * np.cumsum(rng.standard_normal(len(g)) * math.sqrt(ds)) - g / 2
        il, ir = int(np.argmax(wl)), int(np.argmax(wr))
        if max(wl[il], wr[ir]) <= 0:
            out[r] = 0.0
        elif wl[il] > wr[ir]:
            out[r] = -g[il]
        else:
            out[r] = g[ir]
    return float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))


def bai_ci(y: np.ndarray, bk: list[int]) -> list[tuple[int, int]]:
    """95% interval (observation indices) for each break, heterogeneous long-run variances."""
    segs = segments(len(y), bk)
    out = []
    for i, b in enumerate(bk):
        (a1, b1), (a2, b2) = segs[i], segs[i + 1]
        u1, u2 = y[a1:b1] - y[a1:b1].mean(), y[a2:b2] - y[a2:b2].mean()
        w1, w2 = lrv(u1), lrv(u2)
        delta = y[a2:b2].mean() - y[a1:b1].mean()
        lo, hi = argmax_quantiles(w2 / w1)
        scale = delta ** 2 / w1
        out.append((b + int(math.floor(lo / scale)) - 1, b + int(math.ceil(hi / scale)) + 1))
    return out


# ---------------------------------------------------------------- Chow at a known date
def chow(y: np.ndarray, b: int) -> tuple[float, float, float]:
    """HAC Wald test of a mean shift starting at observation b. Returns (shift in pp, Wald, p-value chi2(1))."""
    w = wald_means(y, [b])
    shift = float(y[b:].mean() - y[:b].mean())
    return shift, w, math.erfc(math.sqrt(max(w, 0.0) / 2))  # chi2(1) survival function


def holm(p: dict[str, float], alpha: float = ALPHA) -> dict[str, bool]:
    order = sorted(p, key=p.get)
    out, m, stop = {}, len(p), False
    for i, k in enumerate(order):
        rej = (not stop) and p[k] <= alpha / (m - i)
        stop = stop or not rej
        out[k] = rej
    return out


def ic(best: dict, n: int) -> dict[str, int]:
    """BIC (Yao) and LWZ (Liu-Wu-Zidek) choice of the number of breaks, mean-shift model."""
    bic, lwz = {}, {}
    for m, (ssr, _) in best.items():
        p = 2 * m + 1  # m+1 means and m break dates
        bic[m] = math.log(ssr / n) + p * math.log(n) / n
        lwz[m] = math.log(ssr / (n - p)) + p * 0.299 * math.log(n) ** 2.1 / n
    return {"BIC": min(bic, key=bic.get), "LWZ": min(lwz, key=lwz.get)}


# ---------------------------------------------------------------- data
def load_series(zip_path: Path, end: str | None = None) -> pd.DataFrame:
    import run  # validation/run.py
    import zparse
    cat, rows, public, groups = run.load_catalog()
    ids = sorted({s["id"] for s in rows})
    z = zparse.load_z1_zip(zip_path, ids)
    df = run.to_frame(z[0] if isinstance(z, tuple) else z)
    res = run.compute(df, groups, public)
    out = pd.DataFrame({"total": res["share"], "mortgage": res["pub_mort"] / res["mort"],
                        "consumer_credit": res["pub_cc"] / res["cc"]})
    out.index = [run.q(t) for t in out.index]
    out = out.loc["1952Q1":end] if end else out.loc["1952Q1":]
    assert not out.isna().any().any(), "gap in the share series"
    return out


def analyse(share: pd.Series, cvs: dict, primary: bool) -> dict:
    q = list(share.index[1:])
    y = 100 * np.diff(share.values)  # pp per quarter
    n = len(y)
    h = int(EPS * n)
    best = dp_breaks(y, h, M)
    F = {k: supF(y, best[k][1]) for k in best if k >= 1}
    ud = max(F.values())
    wd = max(F[k] * cvs["supF"][1] / cvs["supF"][k] for k in F)
    reject0 = ud > cvs["UDmax"] or wd > cvs["WDmax"]
    m_seq, seq_log = 0, []
    if reject0:
        m_seq = 1
        for l in range(1, M):
            if l + 1 not in best:
                break
            s, where = seq_test(y, best[l][1], h)
            rej = s > cvs["seq"][l]
            seq_log.append({"l": l, "supF_l1_given_l": round(s, 4), "cv5": round(cvs["seq"][l], 4), "reject": rej,
                            "at": q[where] if where is not None else None})
            if not rej:
                break
            m_seq = l + 1
    bk = best[m_seq][1] if m_seq else []
    cis = bai_ci(y, bk) if bk else []
    segs = segments(n, bk)
    out = {"T": n, "h": h, "sample": f"{q[0]}-{q[-1]}",
           "supF": {k: round(v, 4) for k, v in F.items()}, "UDmax": round(ud, 4), "WDmax": round(wd, 4),
           "H1_reject_no_break": bool(reject0), "sequential": seq_log, "m_selected": m_seq,
           "m_BIC_LWZ": ic(best, n),
           "breaks": [{"quarter": q[b], "ci95": [q[max(lo, 0)], q[min(hi, n - 1)]]} for b, (lo, hi) in zip(bk, cis)],
           "regime_means_pp": [round(float(y[a:b].mean()), 4) for a, b in segs]}
    if primary:
        import run
        z = run.robust_z(pd.Series(y, index=q))
        p, chows = {}, {}
        for d, name in KNOWN.items():
            b = q.index(d)
            shift, w, pv = chow(y, b)
            p[d] = pv
            covered = any(q[max(lo, 0)] <= d <= q[min(hi, n - 1)] for lo, hi in cis)
            step = float(y[b])
            chows[d] = {"event": name, "shift_pp_per_quarter": round(shift, 4), "wald": round(w, 4), "p": pv,
                        "bp_ci_covers": bool(covered), "step_pp": round(step, 4), "step_robust_z": round(float(z.iloc[b]), 3),
                        "step_flag": bool(abs(z.iloc[b]) > 6 and abs(step) >= 1)}
        hr = holm(p)
        adm = [i for i in range(h, n - h + 1) if q[i] not in MEASUREMENT]
        plac = np.array([chow(y, i)[1] for i in adm])
        for d in KNOWN:
            chows[d]["holm_reject"] = bool(hr[d])
            chows[d]["placebo_share_larger"] = round(float((plac > chows[d]["wald"]).mean()), 4)
            legs = chows[d]["holm_reject"], chows[d]["bp_ci_covers"]
            chows[d]["verdict"] = ("Consistent with a break near D, not confirmed (R cross-check not run)" if all(legs)
                                   else "Consistent with a break near D, not confirmed" if any(legs)
                                   else "No evidence of a break at D")
        out["known_dates"] = chows
        out["placebo_n"] = len(adm)
    return out


def main() -> int:
    z1 = ROOT / "data" / "validation" / "FRB_Z1_csv.zip"
    prev = ROOT / "data" / "validation" / "prev_z1_csv_files.zip"
    cvs = simulate_cvs()
    s = load_series(z1)
    res = {"prereg_commit": PREREG_COMMIT, "deviations": DEVIATIONS,
           "critical_values_simulated": {"supF": {k: round(v, 3) for k, v in cvs["supF"].items()},
                                         "UDmax": round(cvs["UDmax"], 3), "WDmax": round(cvs["WDmax"], 3),
                                         "seq": {k: round(v, 3) for k, v in cvs["seq"].items()}, **cvs["sim"]},
           "vintage_primary": "z1:2026-09-11",
           "total": analyse(s["total"], cvs, True),
           "mortgage_descriptive": analyse(s["mortgage"], cvs, False),
           "consumer_credit_descriptive": analyse(s["consumer_credit"], cvs, False)}
    if prev.exists():
        a, b = load_series(z1, "2026Q1"), load_series(prev, "2026Q1")
        ra, rb = analyse(a["total"], cvs, True), analyse(b["total"], cvs, True)
        res["vintage_june_2026_cut_2026Q1"] = {
            "sept_breaks": [x["quarter"] for x in ra["breaks"]], "june_breaks": [x["quarter"] for x in rb["breaks"]],
            "verdicts_sept": {d: v["verdict"] for d, v in ra["known_dates"].items()},
            "verdicts_june": {d: v["verdict"] for d, v in rb["known_dates"].items()}}
        res["vintage_june_2026_cut_2026Q1"]["vintage_sensitive"] = (
            res["vintage_june_2026_cut_2026Q1"]["sept_breaks"] != res["vintage_june_2026_cut_2026Q1"]["june_breaks"]
            or res["vintage_june_2026_cut_2026Q1"]["verdicts_sept"] != res["vintage_june_2026_cut_2026Q1"]["verdicts_june"])
    (HERE / "results.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
