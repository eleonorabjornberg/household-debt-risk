"""Synthetic tests for the A1 identity (no data, no network)."""
import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location("decompose", Path(__file__).with_name("decompose.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def _cells(vals):
    idx = pd.MultiIndex.from_tuples(list(vals), names=["loan", "side", "holder"])
    return pd.Series(list(vals.values()), index=idx, dtype=float)


def test_contributions_sum_exactly_and_signs():
    c0 = _cells({("m", "public", "g"): 30, ("m", "public", "f"): 10, ("m", "private", "pls"): 40, ("m", "private", "bank"): 20})
    c1 = _cells({("m", "public", "g"): 45, ("m", "public", "f"): 10, ("m", "private", "pls"): 10, ("m", "private", "bank"): 25})
    con = d.contrib(c0, c1)
    p0, p1 = 40 / 100, 55 / 90
    assert abs(con.sum() - 100 * (p1 - p0)) < 1e-12
    assert con[("m", "private", "pls")] > 0      # private retreat raises the share
    assert con[("m", "private", "bank")] < 0     # private growth lowers it
    assert con[("m", "public", "f")] == 0        # unchanged public holder contributes nothing


def test_reclassification_between_private_holders_cancels():
    c0 = _cells({("m", "public", "g"): 40, ("c", "private", "abs"): 30, ("c", "private", "bank"): 30})
    c1 = _cells({("m", "public", "g"): 40, ("c", "private", "abs"): 0, ("c", "private", "bank"): 60})
    con = d.contrib(c0, c1)
    assert abs(con.sum()) < 1e-12 and abs(con.xs("private", level="side").sum()) < 1e-12


def test_shapley_is_average_of_both_orderings():
    c0 = _cells({("m", "public", "g"): 30, ("m", "private", "pls"): 70})
    c1 = _cells({("m", "public", "g"): 50, ("m", "private", "pls"): 40})
    f = lambda a, b: a / (a + b)  # noqa: E731
    pub_first = f(50, 70) - f(30, 70)
    pub_last = f(50, 40) - f(30, 40)
    con = d.shapley(c0, c1)
    assert abs(con[("m", "public", "g")] - 100 * (pub_first + pub_last) / 2) < 1e-12
    assert abs(con.sum() - 100 * (f(50, 40) - f(30, 70))) < 1e-12


def test_shapley_pro_rata_within_side_and_identity_sums():
    c0 = _cells({("m", "public", "g"): 20, ("m", "public", "f"): 20, ("m", "private", "pls"): 60})
    c1 = _cells({("m", "public", "g"): 35, ("m", "public", "f"): 25, ("m", "private", "pls"): 50})
    con = d.shapley(c0, c1)
    assert abs(con[("m", "public", "g")] / con[("m", "public", "f")] - 3.0) < 1e-12
    assert abs(d.identity(c0, c1).sum() - con.sum()) < 1e-12
