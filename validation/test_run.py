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
