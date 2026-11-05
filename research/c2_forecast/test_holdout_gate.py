"""The holdout stays sealed: every gate of holdout_run.py refuses before any data is read. Offline."""
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("holdout_run", HERE / "holdout_run.py")
hr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hr)


def test_refuses_without_prereg():
    with pytest.raises(SystemExit, match="prereg"):
        hr.main([])


def test_refuses_wrong_prereg():
    with pytest.raises(SystemExit, match="prereg"):
        hr.main(["--prereg", "deadbee", "--approval", "HEAD"])


def test_refuses_without_approval():
    with pytest.raises(SystemExit, match="approval"):
        hr.main(["--prereg", hr.fc.FROZEN])


def test_refuses_approval_commit_without_eleonora_go():
    # The freeze commit's PLAN.md records no go for the holdout run (HEAD may, once she approves)
    with pytest.raises(SystemExit, match="no Eleonora decision row|cannot read"):
        hr.check_approval("949acec")


def test_freeze_detects_a_changed_file(tmp_path, monkeypatch):
    f = tmp_path / "FREEZE.json"
    f.write_text(json.dumps({"files": {"research/c2_forecast/forecast.py": "0" * 64}}))
    monkeypatch.setattr(hr, "FREEZE", f)
    with pytest.raises(SystemExit, match="changed since the freeze"):
        hr.check_freeze()


def test_refuses_approval_from_before_the_last_freeze():
    # mkt-q29: an approval at or before the last commit that changed FREEZE.json (e.g. 77460b4, which approved the
    # crashed first run, before the c1b-dev-1 re-freeze) must not open the holdout
    import subprocess
    fz = subprocess.run(["git", "log", "-1", "--format=%H", "--", "research/c2_forecast/FREEZE.json"],
                        cwd=hr.ROOT, capture_output=True, text=True).stdout.strip()
    for c in (fz, fz + "~1"):
        with pytest.raises(SystemExit, match="after the last commit"):
            hr.check_order(c)
