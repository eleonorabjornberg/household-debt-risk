"""C1 vintage loader checks. Data tests skip unless data/ exists (as the pipeline's data tests do)."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LATEST_ZIP = ROOT / "data" / "validation" / "FRB_Z1_csv.zip"
SV = HERE / "z1_share_vintages.csv"


@pytest.mark.skipif(not (LATEST_ZIP.exists() and SV.exists()), reason="needs data/validation zip and z1_vintages.py output")
def test_latest_archived_vintage_matches_a1_share_every_quarter():
    spec = importlib.util.spec_from_file_location("b1", ROOT / "research" / "b1_market_pricing" / "b1.py")
    b1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b1)
    a1_share = b1.public_shares(LATEST_ZIP)["headline_share"]
    sv = pd.read_csv(SV)
    last = sv[sv.release == sv.release.max()].set_index("quarter")["share"]
    a1_share.index = a1_share.index.astype(str)
    j = pd.concat([last, a1_share], axis=1, keys=["vint", "a1"]).dropna()
    assert len(j) >= 80
    assert (j["vint"] - j["a1"]).abs().max() < 1e-8   # CSV stores 8 decimals


def test_first_release_unique_and_2016q4_from_its_own_release():
    fr = pd.read_csv(HERE / "first_release.csv").set_index("quarter")
    assert fr.index.is_unique
    # The 2017-03-09 release lives in archive folder 20170305 (skeptic mkt-s9); 2016Q4 must come from it
    assert fr.loc["2016Q4", "first_release"] == "2017-03-09"
