"""Offline tests for analyze_e1.py on synthetic results (no E1 result exists)."""
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("e1_analyze", HERE / "analyze_e1.py")
an = importlib.util.module_from_spec(s)
sys.modules["e1_analyze"] = an
s.loader.exec_module(an)


def test_wilson_matches_prereg_arithmetic():
    assert an.wilson(56 / 68, 68)[0] >= 0.70 > an.wilson(55 / 68, 68)[0]  # "T=70% needs 56/68"


def test_icc_extremes():
    assert an.icc([[1, 1, 1], [0, 0, 0]] * 10) == pytest.approx(1.0)
    assert an.icc([[1, 0, 1], [0, 1, 0], [1, 1, 0], [0, 0, 1]] * 5) == 0.0  # floored


def test_durkalski_hand_example():
    # 2 questions: q1 A beats B on all 3 reps, q2 B beats A once
    r = an.paired_test({"q1": [(1, 0)] * 3, "q2": [(0, 1), (1, 1), (0, 0)]}, "deff", None)
    assert (r["discordant_a_only"], r["discordant_b_only"]) == (3, 1)
    assert r["chi2_clustered"] == pytest.approx((3 - 1) ** 2 / (3 ** 2 + 1 ** 2))


def test_holm():
    assert an.holm({"a": 0.01, "b": 0.04, "c": 0.03}) == {"a": 0.03, "c": 0.06, "b": 0.06}


def _results(acc: dict, n_q=68, n_un=12, reps=3):
    out = []
    for m, p in acc.items():
        for i in range(n_q + n_un):
            fam = "UN" if i >= n_q else "PS"
            for r in range(reps):
                out.append({"model": m, "qid": f"q{i}", "rep": r, "family": fam,
                            "correct": (i * 7 + r) % 100 < p * 100})
    return out


@pytest.mark.parametrize("method", ["deff", "bootstrap"])
def test_verdicts(method):
    res = an.analyze(_results({"claude-opus-5-5": 0.99, "claude-sonnet-5-5": 0.95, "claude-haiku-5-5": 0.3}), method)
    assert res["H1"]["claude-opus-5-5"]["verdict"] == "supported"
    assert res["H1"]["claude-haiku-5-5"]["verdict"] == "against"
    assert res["H3"] == {"status": "not tested: R not given"}
    assert res["H2"]["claude-sonnet-5-5 vs claude-haiku-5-5"]["verdict"] == "supported (differ)"


def test_clustering_widens_the_interval():
    cl = [[1, 1, 1]] * 50 + [[0, 0, 0]] * 18  # perfectly clustered: 3 reps carry the information of 1
    import random
    r = an.rate_test(cl, 0.7, "deff", random.Random(0))
    assert r["deff"] == pytest.approx(3.0) and r["n_eff"] == pytest.approx(68)
    assert r["ci95"][0] == pytest.approx(an.wilson(50 / 68, 68)[0])


def test_bootstrap_is_seeded():
    res = _results({"claude-opus-5-5": 0.8, "claude-sonnet-5-5": 0.8, "claude-haiku-5-5": 0.8})
    assert an.analyze(res, "bootstrap") == an.analyze(res, "bootstrap")
