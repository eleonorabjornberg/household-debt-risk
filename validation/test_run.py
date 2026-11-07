"""Tests for the validation suite parser and checks (synthetic data only, no network)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402
import zparse  # noqa: E402

LINE = (b'Z1/Z1/FL153165105.Q,"Households; one-to-four, family mortgages; liability","x, y","United States / '
        b'United States Dollar",Quarterly,"inst","Level",Millions,2026-06-30,13976938\r\n')


def test_parse_line_handles_quoted_commas():
    assert zparse.parse_line(LINE) == ("Z1/Z1/FL153165105.Q", "2026-06-30", "13976938")


def test_parse_value():
    assert zparse.parse_value("ND") is None
    assert zparse.parse_value("") is None
    assert zparse.parse_value("12.5") == 12.5


def test_stream_series_filters_ids_and_frequency():
    annual = LINE.replace(b".Q,", b".A,")
    other = LINE.replace(b"FL153165105", b"FL999999999")
    nd = LINE.replace(b"2026-06-30,13976938", b"2026-03-31,ND")
    out = zparse.stream_series([b"header\n", LINE, annual, other, nd], ["FL153165105"])
    assert out == {"FL153165105": {"2026-06-30": 13976938.0}}


def synthetic(share_after):
    """Tiny catalog-shaped frame: 2 mortgage holders (1 public), 2 cc holders (1 public)."""
    idx = pd.to_datetime(["2011-12-31", "2012-03-31", "2012-06-30"])
    df = pd.DataFrame(index=idx)
    df["FL893065105"] = 100.0
    df["FL153165105"] = 80.0
    df["FL313065105"] = [50.0] + [share_after * 100] * 2        # public holder
    df["FL763065105"] = 100.0 - df["FL313065105"]               # private holder
    df["FL153166000"] = 20.0
    df["FL313066220"] = 10.0
    df["FL763066005"] = 10.0
    df["FL154104015"] = 100.0
    return df


GROUPS = {
    "mort_holders": [{"id": "FL313065105", "risk_bucket": "federal_direct"}, {"id": "FL763065105", "risk_bucket": "banks_credit_unions"}],
    "cc_holders": [{"id": "FL313066220", "risk_bucket": "federal_direct"}, {"id": "FL763066005", "risk_bucket": "banks_credit_unions"}],
    "cc_types": [],
}


def test_compute_apportions_mortgages():
    res = run.compute(synthetic(0.5), GROUPS, {"federal_direct"})
    # public mortgage = 50/100*80 = 40; public cc = 10; share = 50/100
    assert abs(res["public"].iloc[0] - 50) < 1e-9
    assert abs(res["share"].iloc[0] - 0.5) < 1e-9
    assert abs(res["share_mort"].iloc[0] - 0.5) < 1e-9


def test_identity_check_passes_and_fails():
    df = synthetic(0.5)
    # A4 needs FIRST_Q onwards; synthetic dates are after 1952
    assert {c.id: c.status for c in run.check_identities(df, GROUPS)}["A4"] == "PASS"
    assert {c.id: c.status for c in run.check_identities(df, GROUPS)}["A1"] == "PASS"
    bad = df.copy()
    bad.loc[bad.index[1], "FL893065105"] = 105.0   # holders no longer sum to the total
    assert {c.id: c.status for c in run.check_identities(bad, GROUPS)}["A1"] == "FAIL"


def test_never_reversed_rule_distinguishes_readings():
    # share dips below 2011Q4 level but stays above 2007Q4 level -> (ii) holds, (i) fails -> FAIL
    idx = pd.to_datetime(["2007-12-31", "2011-12-31", "2012-03-31", "2012-06-30"])
    mk = lambda vals: pd.DataFrame({"share": vals, "public": 1.0, "scope": 1.0, "share_mort": 0.5, "share_cc": 0.5}, index=idx)
    c9 = lambda df: {c.id: c for c in run.check_headlines(df)}["C9"]
    assert c9(mk([0.36, 0.49, 0.50, 0.51])).status == "PASS"
    weaker = c9(mk([0.36, 0.49, 0.45, 0.51]))
    assert weaker.status == "FAIL" and "rewording" in weaker.note


# ---- (h) Hot Potato checks (sources-verify (a)) ------------------------------------------------
import csv  # noqa: E402
import itertools  # noqa: E402
import math  # noqa: E402

import numpy as np  # noqa: E402
import pytest  # noqa: E402

REGISTER = Path(__file__).resolve().parent.parent / "claims" / "register.csv"


def test_rounds_to_is_half_away_from_zero_at_display_precision():
    assert run.rounds_to(56.249, 1, 56.2) and not run.rounds_to(56.25, 1, 56.2)
    assert run.rounds_to(0.6305, 2, 0.63) and run.rounds_to(19.097, 0, 19)
    assert run.rounds_to(-1.05, 1, -1.1)
    assert not run.rounds_to(3.565, 2, 3.56)


def test_cpi_quarterly_skips_missing_month(tmp_path):
    f = tmp_path / "cpi.csv"
    f.write_text("observation_date,CPIAUCSL\n2025-10-01,.\n2025-11-01,10\n2025-12-01,20\n2026-01-01,30\n")
    q = run.cpi_quarterly(f)
    assert q[pd.Timestamp("2025-12-31")] == 15  # two-month mean, as the pipeline documents
    assert q[pd.Timestamp("2026-03-31")] == 30


def test_private_label_apportions_mortgage_holders():
    idx = pd.to_datetime(["2007-12-31"])
    df = pd.DataFrame({"FL893065105": [200.0], "FL153165105": [100.0], "FL673065105": [40.0],
                       "FL643065173": [20.0], "FL673066000": [5.0]}, index=idx)
    _, _, _, groups = run.load_catalog()
    assert run.private_label(df, groups)[idx[0]] == pytest.approx((40 + 20) / 200 * 100 + 5)


def test_placebo_p_matches_exact_enumeration():
    d16 = pd.Series([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], index=pd.date_range("2000-03-31", periods=8, freq="QE"))
    starts = list(d16.index[[2, 6, 7]])
    cm = d16[starts].mean()
    combos = list(itertools.combinations(d16.values, 3))
    exact = sum(np.mean(c) >= cm for c in combos) / len(combos)
    p, se = run.placebo_p(d16, starts, n_draws=200_000, seed=1)
    assert abs(p - exact) < 4 * se + 1e-9


def _synthetic_full(value=1.0):
    """Every catalog Z.1 series constant over 1952Q1-2026Q2: the checks run end to end and must FAIL."""
    cat, rows, public, groups = run.load_catalog()
    idx = pd.date_range("1951-12-31", "2026-06-30", freq="QE")
    df = pd.DataFrame({s["id"]: value for s in rows}, index=idx)
    return df, groups, public


def test_hotpotato_checks_wiring_and_failures_are_reported(monkeypatch):
    monkeypatch.setattr(run, "PLACEBO_DRAWS", 2_000)
    df, groups, public = _synthetic_full()
    res = run.compute(df, groups, public)
    cpi = pd.Series(100.0, index=pd.date_range("1947-03-31", "2026-09-30", freq="QE"))
    out = run.check_hotpotato(df, res, cpi, groups, public)
    assert [c.id for c in out] == [f"H{i}" for i in range(1, 23)]
    assert all(c.status == "FAIL" for c in out)  # nothing is adjusted to pass
    reg = {r["claim_id"]: r for r in csv.DictReader(REGISTER.open(newline="", encoding="utf-8"))}
    for c in out:
        cid = c.note.split(";")[0].removeprefix("register ").strip()
        assert cid in reg, cid
        spellings = [d.strip() for d in reg[cid]["display"].split("|")]
        assert any(sp in c.expected for sp in spellings), (c.id, c.expected, spellings)


def test_hotpotato_not_run_without_cpi_base():
    df, groups, public = _synthetic_full()
    res = run.compute(df, groups, public)
    cpi = pd.Series(100.0, index=pd.date_range("1947-03-31", "2026-06-30", freq="QE"))
    out = run.check_hotpotato(df, res, cpi, groups, public)
    assert len(out) == 1 and out[0].status == "NOT RUN"
