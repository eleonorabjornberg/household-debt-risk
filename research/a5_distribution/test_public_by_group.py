"""Offline tests for the A5 Q4 estimate (synthetic inputs, no downloads)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("public_by_group", HERE / "public_by_group.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

GROUPS = [("Low", ["Low"], 0, 50), ("High", ["High"], 50, 100)]


def _levels(mort_lo, cc_lo, mort_hi, cc_hi):
    return pd.DataFrame({"Date": [m.WHEN] * 2, "Category": ["Low", "High"],
                         "Home mortgages": [mort_lo, mort_hi], "Consumer credit": [cc_lo, cc_hi]})


def test_weighted_quantile():
    x, w = np.array([1.0, 2.0, 3.0, 4.0]), np.array([1.0, 1.0, 1.0, 1.0])
    assert m.wquantile(x, w, 50) == 2.0 and m.wquantile(x, w, 100) == np.inf


def test_both_methods_add_up_and_c_moves_public_cc_to_student_borrowers():
    z = {"p_M": 0.5, "p_CC": 0.2, "public_mort": 100.0, "public_cc": 40.0, "SL": 50.0, "SL_public": 40.0}
    scf_t = pd.DataFrame({"student": [0.8, 0.2]}, index=["Low", "High"])
    t = m.estimate(_levels(80, 100, 120, 100), scf_t, GROUPS, z)
    m.check(t, z)
    assert t.at["Low", "public_c_musd"] > t.at["Low", "public_b_musd"]  # Low owes most student loans
    assert t["public_c_share_of_total"].sum() == pytest.approx(1.0)


def test_imputed_student_loans_above_consumer_credit_is_refused():
    z = {"p_M": 0.5, "p_CC": 0.2, "public_mort": 100.0, "public_cc": 40.0, "SL": 50.0, "SL_public": 40.0}
    scf_t = pd.DataFrame({"student": [1.0, 0.0]}, index=["Low", "High"])
    t = m.estimate(_levels(80, 30, 120, 170), scf_t, GROUPS, z)  # Low's imputed $50 student loans > its $30 consumer credit
    with pytest.raises(AssertionError):
        m.check(t, z)
