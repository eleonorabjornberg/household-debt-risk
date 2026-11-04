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
