#!/usr/bin/env python3
"""E1 hypothesis tests (docs/decisions/e1-prereg.md). Written BEFORE any E1 result exists; offline, no API.

    uv run --project pipeline python evals/e1_sql_benchmark/analyze_e1.py RUN_DIR            # pre-registered: --method bootstrap (the default)

Reads RUN_DIR/results.jsonl (run_e1.py) and writes RUN_DIR/analysis.json. Settings are Eleonora's:
  unit of analysis (e1-unit (ii)): every repetition counted, clustered by question;
  T = 0.70 (e1-T); R = 0.70 (e1-R2);
  alpha 0.05, Holm within each family (H1: 3 tests, H2: 2, H3: 3).
How the clustering enters: e1-cluster (b), the BOOTSTRAP, chosen by Eleonora 2026-11-05 (PLAN ccc1fc6); it is the
default and the only pre-registered method. `deff` is kept for reference only and is not reported:
  deff       Wilson 95% interval on the pooled rate with n replaced by n / DEFF, DEFF = 1 + (m - 1) * ICC
             (one-way ANOVA ICC, floored at 0, m = repetitions per question); H2 by the clustered McNemar test
             of Durkalski et al. (2003): chi2 = (sum_k b_k - sum_k c_k)^2 / sum_k (b_k - c_k)^2.
  bootstrap  resample questions with replacement (10,000 draws, random.Random(20261104)); percentile 95%
             interval for the rate; H2 from the bootstrap distribution of the paired difference.
Verdicts (e1-support (i), Eleonora 2026-11-05), H1 and H3: supported if the lower bound >= threshold; against if the upper bound < threshold; else null.
H1/H3 p-values for Holm are one-sided (H0: rate <= threshold): z test on n_eff (deff) or the bootstrap share at
or below the threshold (bootstrap). H2: supported if the Holm-adjusted p < 0.05, else null.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

T = 0.70
R: float | None = 0.70  # e1-R2, Eleonora 2026-11-05 (PLAN c55701b)
ALPHA = 0.05
Z = 1.959963984540054
SEED = 20261104
B = 10_000
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]
PAIRS = [("claude-opus-5-5", "claude-sonnet-5-5"), ("claude-sonnet-5-5", "claude-haiku-5-5")]


def norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def wilson(p: float, n: float, z: float = Z) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def icc(clusters: list[list[int]]) -> float:
    """One-way ANOVA intraclass correlation for 0/1 outcomes in clusters (unequal sizes allowed), floored at 0."""
    k = len(clusters)
    n = sum(len(c) for c in clusters)
    if k < 2 or n <= k:
        return 0.0
    grand = sum(map(sum, clusters)) / n
    ssb = sum(len(c) * (sum(c) / len(c) - grand) ** 2 for c in clusters)
    ssw = sum(sum((x - sum(c) / len(c)) ** 2 for x in c) for c in clusters)
    msb, msw = ssb / (k - 1), ssw / (n - k)
    m0 = (n - sum(len(c) ** 2 for c in clusters) / n) / (k - 1)
    denom = msb + (m0 - 1) * msw
    return max(0.0, (msb - msw) / denom) if denom > 0 else 0.0


def rate_test(clusters: list[list[int]], thr: float, method: str, rng: random.Random) -> dict:
    n = sum(len(c) for c in clusters)
    p = sum(map(sum, clusters)) / n
    if method == "deff":
        rho = icc(clusters)
        m = n / len(clusters)
        deff = 1 + (m - 1) * rho
        n_eff = n / deff
        lo, hi = wilson(p, n_eff)
        se = math.sqrt(thr * (1 - thr) / n_eff)
        pval = norm_sf((p - thr) / se)
        extra = {"icc": rho, "deff": deff, "n_eff": n_eff}
    else:
        boots = []
        for _ in range(B):
            s = [clusters[rng.randrange(len(clusters))] for _ in clusters]
            boots.append(sum(map(sum, s)) / sum(map(len, s)))
        boots.sort()
        lo, hi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
        pval = sum(b <= thr for b in boots) / B
        extra = {"draws": B}
    verdict = "supported" if lo >= thr else ("against" if hi < thr else "null")
    return {"n_answers": n, "n_questions": len(clusters), "rate": p, "ci95": [lo, hi], "threshold": thr,
            "p_one_sided": pval, "verdict_unadjusted": verdict, **extra}


def paired_test(pairs: dict[str, list[tuple[int, int]]], method: str, rng: random.Random) -> dict:
    """pairs: question -> [(a_correct, b_correct) per repetition]."""
    qs = list(pairs)
    b = [sum(1 for x, y in pairs[q] if x and not y) for q in qs]
    c = [sum(1 for x, y in pairs[q] if y and not x) for q in qs]
    diff = (sum(b) - sum(c)) / sum(len(pairs[q]) for q in qs)
    if method == "deff":
        den = sum((bk - ck) ** 2 for bk, ck in zip(b, c))
        chi2 = (sum(b) - sum(c)) ** 2 / den if den else 0.0
        pval = math.erfc(math.sqrt(chi2 / 2)) if den else 1.0
        extra = {"chi2_clustered": chi2, "test": "Durkalski clustered McNemar"}
    else:
        boots = []
        for _ in range(B):
            idx = [rng.randrange(len(qs)) for _ in qs]
            nn = sum(len(pairs[qs[i]]) for i in idx)
            boots.append((sum(b[i] for i in idx) - sum(c[i] for i in idx)) / nn)
        pval = min(1.0, 2 * min(sum(x <= 0 for x in boots), sum(x >= 0 for x in boots)) / B)
        extra = {"test": "question bootstrap, two-sided"}
    return {"discordant_a_only": sum(b), "discordant_b_only": sum(c), "diff_a_minus_b": diff, "p": pval, **extra}


def holm(ps: dict[str, float]) -> dict[str, float]:
    order = sorted(ps, key=ps.get)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * ps[k]))
        out[k] = running
    return out


def analyze(results: list[dict], method: str = "bootstrap", t: float = T, r: float | None = R) -> dict:
    rng = random.Random(SEED)
    by = defaultdict(lambda: defaultdict(list))  # model -> qid -> [correct per rep]
    refuse = {}
    for x in results:
        by[x["model"]][x["qid"]].append(int(bool(x["correct"])))
        refuse[x["qid"]] = x["family"] == "UN"
    out = {"settings": {"unit": "(ii) every repetition, clustered by question", "T": t, "R": r, "alpha": ALPHA,
                        "method": method, "seed": SEED}, "H1": {}, "H2": {}, "H3": {}}
    for fam, pick, thr in (("H1", False, t), ("H3", True, r)):
        if thr is None:
            out[fam] = {"status": "not tested: R not given"}
            continue
        for m in MODELS:
            cl = [v for q, v in by[m].items() if refuse[q] == pick]
            if cl:
                out[fam][m] = rate_test(cl, thr, method, rng)
        adj = holm({m: v["p_one_sided"] for m, v in out[fam].items()})
        for m, v in out[fam].items():
            v["p_holm"] = adj[m]
            # interval verdicts stand; Holm decides only whether a "supported" survives multiplicity
            v["verdict"] = v["verdict_unadjusted"] if v["verdict_unadjusted"] != "supported" or adj[m] < ALPHA else "null"
    for a, bm in PAIRS:
        pairs = {}
        for q in by[a]:
            if not refuse[q] and q in by[bm]:
                pairs[q] = list(zip(by[a][q], by[bm][q]))
        out["H2"][f"{a} vs {bm}"] = paired_test(pairs, method, rng)
    adj = holm({k: v["p"] for k, v in out["H2"].items()})
    for k, v in out["H2"].items():
        v["p_holm"] = adj[k]
        v["verdict"] = "supported (differ)" if adj[k] < ALPHA else "null"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--method", choices=["bootstrap", "deff"], default="bootstrap",
                    help="bootstrap is the pre-registered method (e1-cluster (b)); deff is not reported")
    a = ap.parse_args()
    results = [json.loads(l) for l in (a.run_dir / "results.jsonl").read_text().splitlines() if l.strip()]
    res = analyze(results, a.method)
    (a.run_dir / "analysis.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
