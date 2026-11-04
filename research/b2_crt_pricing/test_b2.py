"""B2 tests: transcription of FHFA's Dec 2016 tables (hand-checked rows, planted typo) and the EL engine."""
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b2", HERE / "b2.py")
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)

TEXT = b2.FIXTURE.read_text()

# Hand-checked against the rendered PDF (report pages 6, 9, 13 and 14 of the December 2016 report; first, last and
# middle rows), not only against the text layer.
HAND = {
    ("CAS", "2013-1"): dict(date="10/24/13", ref_upb_musd=26756, attach_bp=30, detach_bp=300, sold_musd=675, credit_cost_bp=12),
    ("CAS", "2015-2 (2)"): dict(date="05/27/15", ref_upb_musd=17007, attach_bp=80, detach_bp=425, sold_musd=557, credit_cost_bp=12),
    ("CAS", "2016-7"): dict(date="12/08/16", ref_upb_musd=22515, attach_bp=0, detach_bp=400, sold_musd=702, credit_cost_bp=25),
    ("STACR", "2013-DN1"): dict(date="07/26/13", ref_upb_musd=22587, attach_bp=30, detach_bp=300, sold_musd=500, credit_cost_bp=17),
    ("STACR", "2015-HQA1"): dict(date="09/28/15", ref_upb_musd=19377, attach_bp=0, detach_bp=595, sold_musd=872, credit_cost_bp=32),
    ("STACR", "2016-HQA4"): dict(date="10/25/16", ref_upb_musd=13847, attach_bp=0, detach_bp=550, sold_musd=478, credit_cost_bp=27),
}


def _table(text):
    deals, costs = b2.parse(text)
    return b2.join(deals, costs).set_index(["program", "name"])


def test_hand_checked_rows():
    df = _table(TEXT)
    for key, want in HAND.items():
        row = df.loc[key]
        assert row["date_deal_table"] == want["date"]
        for k in ["ref_upb_musd", "attach_bp", "detach_bp", "sold_musd", "credit_cost_bp"]:
            assert row[k] == want[k], (key, k, row[k], want[k])


def test_unnamed_rows_matched_and_blank_cost_absent():
    df = _table(TEXT)
    assert df.loc[("CAS", "2016-3 (1)"), "ref_upb_musd"] == 11862      # FHFA's deal table prints no name for this row
    assert df.loc[("STACR", "2016-HQA4"), "ref_upb_musd"] == 13847
    assert df.loc[("CAS", "2016-6"), "credit_cost_bp"] != df.loc[("CAS", "2016-6"), "credit_cost_bp"]   # NaN: blank in FHFA


def test_planted_typo_is_caught():
    bad = TEXT.replace("26,756", "27,656", 1)    # transpose two digits of CAS 2013-1's reference UPB
    df = _table(bad)
    with pytest.raises(AssertionError):
        assert df.loc[("CAS", "2013-1"), "ref_upb_musd"] == HAND[("CAS", "2013-1")]["ref_upb_musd"]


def test_row_count_guard():
    lines = TEXT.splitlines()
    i = next(k for k, l in enumerate(lines) if "2016-7" in l and "CAS" in l)
    with pytest.raises(AssertionError):
        b2.parse("\n".join(lines[:i] + lines[i + 1:]))


def test_el_full_pool_and_additivity():
    full = b2.tranche_el_bp(0, 10000)
    assert full == pytest.approx(b2.tranche_el_bp(0, 15) + b2.tranche_el_bp(15, 10000), rel=1e-12)
    assert full == pytest.approx(5.0, abs=0.1)      # CDR 0.2% x LGD 25% = 5 bp a year of the outstanding balance


def test_el_zero_above_baseline_losses():
    assert b2.tranche_el_bp(100, 400) == 0.0       # baseline cumulative loss (about 31 bp) never reaches 100 bp


def test_zero_default_zero_loss():
    assert b2.tranche_el_bp(0, 400, cdr=0.0) == 0.0
