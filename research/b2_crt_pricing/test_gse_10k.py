"""gse_10k.py: number parsing (offline) and, if the 10-K text is present, the extracted values against the committed CSV."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gse10k", HERE / "gse_10k.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def test_values_reads_costs_as_positive():
    line = "  Credit enhancement expense                     ($693)         ($402)        ($263)"
    assert g.values(line, 3) == [693.0, 402.0, 263.0]
    line = "Credit enhancement expense                              (2,118)    (1,518)     (1,058)          (600)        (40)"
    assert g.values(line, 3) == [2118.0, 1518.0, 1058.0]
    with pytest.raises(ValueError):
        g.values("Credit enhancement expense  (12)", 3)


@pytest.mark.skipif(not (g.FRE / "10k_021320.txt").exists(), reason="Freddie 10-K text not fetched (data/ absent)")
def test_extraction_matches_committed_csv():
    rows = pd.DataFrame([r for s in g.SPECS for r in g.parse(*s)])
    got = rows[rows["filing_fy"] == 2019].set_index(["year", "field"])["musd"]
    assert got[(2019, "ce_expense")] == 693 and got[(2019, "crt_debt_interest")] == 1060
    csv = pd.read_csv(HERE / "freddie_crt_cost.csv").set_index("year")
    assert csv.loc[2023, "ce_expense"] == 2339 and csv.loc[2023, "scope"] == "consolidated"
