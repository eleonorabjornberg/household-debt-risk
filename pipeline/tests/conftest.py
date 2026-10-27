"""Data tests read the pipeline's own outputs: data/staging (extract) and data/out (transform).
They skip when those files are missing, unless HHDEBT_REQUIRE_DATA=1 (set in CI), where they fail."""
from __future__ import annotations

import os

import pandas as pd
import pytest

from hhdebt import config, transform
from hhdebt.extract import read_staging

REQUIRE = os.environ.get("HHDEBT_REQUIRE_DATA") == "1"


def _missing(msg):
    if REQUIRE:
        pytest.fail(msg)
    pytest.skip(msg)


@pytest.fixture(scope="session")
def z1_wide() -> pd.DataFrame:
    try:
        z = read_staging("z1")
    except FileNotFoundError as e:
        _missing(str(e))
    return z.pivot(index="date", columns="series_id", values="value").sort_index()


@pytest.fixture(scope="session")
def out() -> dict[str, pd.DataFrame]:
    try:
        return transform.read_out()
    except FileNotFoundError as e:
        _missing(str(e))


@pytest.fixture(scope="session")
def scope_total(out) -> pd.Series:
    return out["mart.public_share"].set_index("date")["scope_total_musd"]
