"""Gates of the second (per-forecast) holdout opening: every refusal happens before any holdout data is read."""
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hfr", HERE / "holdout_forecasts_run.py")
hfr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hfr)


def test_needs_prereg():
    with pytest.raises(SystemExit, match="--prereg"):
        hfr.main(["--approval", "HEAD"])


def test_needs_approval():
    with pytest.raises(SystemExit, match="--approval"):
        hfr.main(["--prereg", "192d60c"])


def test_refuses_an_approval_without_the_c3_errors_row():
    # d2fed5d (on main; same change as the earlier local 432fed0) approved the first (joint) opening only; it has no c3-errors row.
    with pytest.raises(SystemExit, match="c3-errors"):
        hfr.check_approval("d2fed5d")
