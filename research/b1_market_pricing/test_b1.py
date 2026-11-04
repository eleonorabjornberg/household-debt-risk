"""Synthetic tests for B1's statistics (no data, no network)."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("b1", Path(__file__).with_name("b1.py"))
b1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b1)


def _ar1(n, rho, rng):
    e = rng.standard_normal(n)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = rho * x[t - 1] + e[t]
    return x


def test_ols_recovers_coefficients():
    rng = np.random.default_rng(0)
    n = 400
    x = rng.standard_normal((n, 2))
    y = 1.0 + 2.0 * x[:, 0] - 0.5 * x[:, 1] + 0.01 * rng.standard_normal(n)
    X = np.column_stack([np.ones(n), x])
    b, se, u, r2 = b1.ols_hac(y, X, 4)
    assert np.allclose(b, [1.0, 2.0, -0.5], atol=1e-2)
    assert r2 > 0.999


def test_hac_lag0_equals_white():
    rng = np.random.default_rng(1)
    n = 200
    x = rng.standard_normal(n)
    y = 0.3 * x + rng.standard_normal(n) * (1 + np.abs(x))
    X = np.column_stack([np.ones(n), x])
    b, se, u, _ = b1.ols_hac(y, X, 0)
    XtXi = np.linalg.inv(X.T @ X)
    white = np.sqrt(np.diag(XtXi @ (X * u[:, None] ** 2).T @ X @ XtXi))
    assert np.allclose(se, white)


def test_hac_wider_than_ols_with_autocorrelated_errors():
    rng = np.random.default_rng(2)
    n = 300
    x = _ar1(n, 0.9, rng)
    y = 0.5 * x + _ar1(n, 0.9, rng)
    X = np.column_stack([np.ones(n), x])
    _, se0, _, _ = b1.ols_hac(y, X, 0)
    _, se8, _, _ = b1.ols_hac(y, X, 8)
    assert se8[1] > se0[1]


def test_hac_matches_statsmodels_if_available():
    sm = pytest.importorskip("statsmodels.api")
    rng = np.random.default_rng(3)
    n = 160
    x = np.column_stack([_ar1(n, 0.8, rng), rng.standard_normal(n)])
    y = 0.2 + 0.7 * x[:, 0] + _ar1(n, 0.6, rng)
    X = np.column_stack([np.ones(n), x])
    b, se, _, _ = b1.ols_hac(y, X, 4)
    r = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
    assert np.allclose(b, r.params) and np.allclose(se, r.bse)


def test_adf_separates_stationary_from_random_walk():
    rng = np.random.default_rng(4)
    stat = b1.adf_stat(rng.standard_normal(300))
    rw = b1.adf_stat(np.cumsum(rng.standard_normal(300)))
    assert stat < -4 and rw > -3


def test_nw_lag_rule():
    assert b1.nw_lag(100) == 4 and b1.nw_lag(162) == 4 and b1.nw_lag(400) == 5


def test_verdict_rule():
    def frame(lo_L, hi_L, lo_D, hi_D):
        return pd.DataFrame([
            dict(variant="main", form="L", term="public_share", ci_lo=lo_L, ci_hi=hi_L),
            dict(variant="main", form="D", term="public_share", ci_lo=lo_D, ci_hi=hi_D),
        ])
    assert b1.verdict(frame(-2, -1, -3, -0.1), "main").startswith("compression")
    assert b1.verdict(frame(-2, -1, -3, 0.5), "main") == "no robust association"
    assert b1.verdict(frame(1, 2, 0.1, 3), "main").startswith("widening")
