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
