"""B3 engine invariants (METHOD.md) and the Python/JavaScript match. Offline, synthetic inputs."""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("engine", HERE / "engine.py")
eng = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eng)

EX = eng.fixed_cases()[0]["exposures"]
P3 = {"mortgage": {"pd": 0.04, "lgd": 0.35, "timing": [0.1, 0.3, 0.4, 0.2]},
      "student_federal": {"pd": 0.2, "lgd": 0.5, "timing": [0.25] * 4},
      "consumer_other": {"pd": 0.08, "lgd": 0.8, "timing": [0.5, 0.5]}}


def test_public_plus_private_equals_total_every_quarter():
    r = eng.run(EX, P3)
    for a, b, t in zip(r["public"], r["private"], r["total"]):
        assert a + b == pytest.approx(t, abs=1e-12)


def test_sum_equals_balance_times_pd_times_lgd():
    r = eng.run(EX, P3)
    want = sum(e["balance"] * P3[e["class"]]["pd"] * P3[e["class"]]["lgd"] for e in EX)
    assert r["sum"]["total"] == pytest.approx(want, rel=1e-12)


@pytest.mark.parametrize("k", ["pd", "lgd"])
def test_zero_default_or_zero_severity_zero_loss(k):
    p = {c: dict(v, **{k: 0.0}) for c, v in P3.items()}
    r = eng.run(EX, p)
    assert r["sum"]["total"] == 0.0 and all(x == 0.0 for x in r["total"])


def test_linear_in_pd():
    r1 = eng.run(EX, {"mortgage": {"pd": 0.02, "lgd": 0.3}})["sum"]["total"]
    r2 = eng.run(EX, {"mortgage": {"pd": 0.04, "lgd": 0.3}})["sum"]["total"]
    assert r2 == pytest.approx(2 * r1, rel=1e-12)


def test_transfer_conserves_and_respects_cap():
    base = eng.run(EX, P3)
    for cap in [0.0, 10.0, 1e9]:
        r = eng.run(EX, P3, {"share": 0.6, "cap_musd": cap})
        assert r["sum"]["total"] == pytest.approx(base["sum"]["total"], rel=1e-12)
        assert r["sum"]["transferred"] <= cap + 1e-12
        gse_loss = 8000 * 0.04 * 0.35
        assert r["sum"]["transferred"] <= 0.6 * gse_loss + 1e-12
        assert r["sum"]["public"] == pytest.approx(base["sum"]["public"] - r["sum"]["transferred"], rel=1e-12)


@pytest.mark.parametrize("bad", [
    {"mortgage": {"pd": 1.2, "lgd": 0.3}},
    {"mortgage": {"pd": 0.1, "lgd": -0.1}},
    {"mortgage": {"pd": 0.1, "lgd": 0.3, "timing": [0.5, 0.4]}},
    {"autos": {"pd": 0.1, "lgd": 0.3}},
])
def test_invalid_input_refused(bad):
    with pytest.raises(ValueError):
        eng.run(EX, bad)


def test_negative_balance_refused():
    with pytest.raises(ValueError):
        eng.run([dict(EX[0], balance=-1.0)], {"mortgage": {"pd": 0.1, "lgd": 0.3}})


def test_fixture_is_current():
    committed = json.loads((HERE / "fixtures" / "cases.json").read_text())
    assert committed == json.loads(json.dumps(eng.fixed_cases()))


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_browser_engine_matches_python():
    out = subprocess.run(["node", str(HERE / "test_engine.mjs")], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


EXPOSURES = HERE / "exposures.json"


@pytest.mark.skipif(not EXPOSURES.exists(), reason="exposures.json not built")
def test_exposures_sum_to_scope_and_share():
    d = json.loads(EXPOSURES.read_text())
    ex = d["exposures"]
    pub = sum(e["balance"] for e in ex if e["side"] == "public")
    tot = sum(e["balance"] for e in ex)
    assert pub / tot == pytest.approx(0.5638, abs=5e-4)   # register public_share_2026q2 (validation C2)


RESULTS = HERE / "results_dfast2026.json"


@pytest.mark.skipif(not RESULTS.exists(), reason="presets not built")
def test_dfast_preset_identities():
    r = json.loads(RESULTS.read_text())
    for k in ["dfast2026_proxy", "dfast2026_proxy_with_student"]:
        x = r[k]
        assert x["public_musd"] + x["private_musd"] == pytest.approx(x["total_musd"], rel=1e-12)
        assert sum(x["by_class"].values()) == pytest.approx(x["total_musd"], rel=1e-12)
    assert "student_federal" not in r["dfast2026_proxy"]["by_class"]          # absent, not defaulted


REPLAY = HERE / "results_replay_2008_2012.json"


@pytest.mark.skipif(not REPLAY.exists(), reason="presets not built")
def test_replay_preset_identities():
    r = json.loads(REPLAY.read_text())["replay_2008_2012_proxy"]
    assert r["public_musd"] + r["private_musd"] == pytest.approx(r["total_musd"], rel=1e-12)
    assert r["quarters"] == 20
    p = json.loads((HERE / "presets" / "replay_2008_2012.json").read_text())["presets"]["replay_2008_2012_proxy"]["classes"]
    assert all(abs(sum(c["timing"]) - 1) < 1e-12 for c in p.values())
    assert "student_federal" not in p
