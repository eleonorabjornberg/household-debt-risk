"""Synthetic tests for the A4 implementation (no Z.1 data)."""
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("breaks", HERE / "breaks.py")
b = importlib.util.module_from_spec(spec)
sys.modules["breaks"] = b
spec.loader.exec_module(b)


def _brute(y, h, m):
    n, best = len(y), (np.inf, None)
    for bk in itertools.combinations(range(h, n - h + 1), m):
        edges = (0,) + bk + (n,)
        if any(edges[i + 1] - edges[i] < h for i in range(len(edges) - 1)):
            continue
        ssr = sum(((y[edges[i]:edges[i + 1]] - y[edges[i]:edges[i + 1]].mean()) ** 2).sum() for i in range(len(edges) - 1))
        if ssr < best[0]:
            best = (ssr, list(bk))
    return best


def test_dynamic_programme_matches_brute_force():
    rng = np.random.default_rng(1)
    y = rng.standard_normal(40) + np.r_[np.zeros(15), np.ones(12) * 2, np.zeros(13)]
    dp = b.dp_breaks(y, 5, 3)
    for m in (1, 2, 3):
        ssr, bk = _brute(y, 5, m)
        assert dp[m][1] == bk and dp[m][0] == pytest.approx(ssr)


def test_planted_break_is_found_and_covered():
    rng = np.random.default_rng(2)
    y = np.r_[rng.standard_normal(150), rng.standard_normal(150) + 1.0]
    best = b.dp_breaks(y, 30, 1)
    assert abs(best[1][1][0] - 150) <= 5
    lo, hi = b.bai_ci(y, best[1][1])[0]
    assert lo <= 150 <= hi


def test_lrv_of_iid_noise_is_close_to_variance():
    rng = np.random.default_rng(3)
    u = rng.standard_normal(4000)
    assert b.lrv(u) == pytest.approx(1.0, rel=0.1)


def test_lrv_of_ar1_matches_theory():
    rng = np.random.default_rng(4)
    e = rng.standard_normal(20000)
    u = np.zeros_like(e)
    for t in range(1, len(e)):
        u[t] = 0.5 * u[t - 1] + e[t]
    assert b.lrv(u) == pytest.approx(1 / (1 - 0.5) ** 2, rel=0.15)


def test_holm():
    out = b.holm({"a": 0.001, "b": 0.02, "c": 0.04})
    assert out == {"a": True, "b": True, "c": True} or out["a"]  # a always rejected
    assert b.holm({"a": 0.001, "b": 0.03, "c": 0.04}) == {"a": True, "b": False, "c": False}


def test_simulated_cv_order_and_size_plausible():
    cv = b.simulate_cvs(n=200, reps=200, seed=5)
    s = cv["supF"]
    assert s[1] > s[2] > s[3]  # per-break statistic falls with k, as in Bai-Perron's tables
    assert cv["UDmax"] >= s[1] and all(cv["seq"][l] >= s[1] for l in cv["seq"])
