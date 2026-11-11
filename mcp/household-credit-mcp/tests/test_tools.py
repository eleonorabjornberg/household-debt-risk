import json
import re

import pytest

from household_credit_mcp import core
from household_credit_mcp.backends import repo_file


def assert_envelope(r, backend="snapshot"):
    assert r["ok"] is True and r["backend"] == backend
    for k in ("units", "series_ids", "vintage", "limits", "data"):
        assert k in r
    assert r["vintage"]["source_vintage"]
    assert r["limits"]


def test_list_and_describe(be):
    r = core.list_series(be, role="cc_type")
    assert_envelope(r)
    assert {s["id"] for s in r["data"]} == {"FL153166100", "FL153166220", "FL153166400", "FL153166205"}
    d = core.describe_series(be, "fl153166400")
    assert_envelope(d)
    assert d["data"]["desc"] == "Auto loans" and any("holder" in c for c in d["limits"])
    bad = core.describe_series(be, "NOPE")
    assert bad["refused"] and bad["reason_code"] == "unknown_series"


def test_public_share_latest_and_measures(be):
    r = core.public_share(be)
    assert_envelope(r)
    assert r["data"][0]["quarter"] == "2026Q2" and r["vintage"]["source_vintage"] == "2026-09-11"
    assert any("Holding is not bearing" in c for c in r["limits"])
    m = core.public_share(be, "2026Q2", "2026Q2", "mortgage")
    c = core.public_share(be, "2026Q2", "2026Q2", "consumer_credit")
    assert m["data"][0]["public_share_display"] == "65.6%" and c["data"][0]["public_share_display"] == "31.3%"
    rng = core.public_share(be, "2007Q1", "2007Q4")
    assert [x["quarter"] for x in rng["data"]] == ["2007Q1", "2007Q2", "2007Q3", "2007Q4"]
    assert core.public_share(be, measure="bogus")["reason_code"] == "bad_measure"
    assert core.public_share(be, "2026-Q9")["reason_code"] == "bad_quarter"


def test_holdings_by_bucket(be):
    r = core.holdings_by_bucket(be, "2007Q4")
    assert_envelope(r)
    assert len(r["data"]) == 6
    assert sum(x["share_of_scope"] for x in r["data"]) == pytest.approx(1.0, abs=1e-6)
    assert r["summary"]["public_share_display"] == "36.1%"  # validation B8: 36.12%
    assert r["summary"]["scope_total_musd"] == pytest.approx(13186611, abs=1)  # B7
    assert core.holdings_by_bucket(be, "2011Q4")["summary"]["quarter"] == "2011Q4"


def test_crisis_windows(be):
    r = core.crisis_windows(be)
    assert_envelope(r)
    assert len(r["data"]) == 14
    g = next(x for x in r["data"] if x["crisis_id"] == "gfc_2007")
    assert g["delta_q16"] is not None
    one = core.crisis_windows(be, "gfc_2007", "coverage:home_backed")
    assert len(one["data"]) == 1
    assert core.crisis_windows(be, "nope")["reason_code"] == "unknown_crisis"
    assert core.crisis_windows(be, metric="nope")["reason_code"] == "unknown_metric"


def test_collateral_coverage(be):
    r = core.collateral_coverage(be, "2026Q2", "2026Q2")
    assert_envelope(r)
    assert {x["collateral_class"] for x in r["data"]} == {"home_backed", "vehicle_backed", "uncollateralized", "other_nonrevolving"}
    assert any("durable" in c for c in r["limits"])


def test_nyfed_labelled(be):
    r = core.nyfed_by_type(be, "2003Q1", "2003Q2")
    assert_envelope(r)
    assert r["source"] == "nyfed" and r["vintage"]["source_vintage"] == "2026-10-27"
    assert "NEW YORK FED" in r["limits"][0] and "NOT FEDERAL RESERVE Z.1" in r["limits"][0]
    assert core.nyfed_by_type(be, "2002Q4", "2003Q1")["reason_code"] == "before_coverage"


def test_lookup_claim(be):
    r = core.lookup_claim(be, "public_share_2026q2")
    assert_envelope(r)
    assert r["data"][0]["validation"] == "PASS" and r["data"][0]["quotable_as_verified"]
    f = core.lookup_claim(be, "public share 2007Q4")
    assert f["data"] and all("validation" in d for d in f["data"])
    assert core.lookup_claim(be, "zzzqqq nothing")["reason_code"] == "no_matching_claim"
    unv = [d for d in core.lookup_claim(be, "gfc_jump_pp")["data"]]
    assert unv[0]["quotable_as_verified"] == (unv[0]["validation"] == "PASS")


def test_data_coverage(be):
    r = core.data_coverage(be)
    assert_envelope(r)
    assert r["data"]["coverage"]["mart_quarters"] == ["1951Q4", "2026Q2"]
    assert any("AND loan type" in s for s in r["data"]["cannot_answer"])


# ------------------------------------------------------------------ refusals
def refused(r, code):
    assert r["ok"] is False and r["refused"] is True and r["reason_code"] == code
    assert r["reason"] and r["nearest_answerable"]
    assert "data" not in r  # no numbers


@pytest.mark.parametrize("q,code", [
    ("How much of auto loans are held by banks?", "holder_by_type_not_available"),
    ("What share of student loans does the federal government hold, and credit card debt held by ABS issuers?", "holder_by_type_not_available"),
    ("What is the delinquency rate by holder?", "holder_by_type_not_available"),
    ("Forecast the public share for 2028", "forecast"),
    ("Will the public share rise next quarter?", "forecast"),
    ("What was the public share in 1930?", "before_coverage"),
    ("What was the public share in 2031Q1?", "forecast"),
    ("Which borrowers are most at risk? Give me loan-level data", "loan_or_borrower_level"),
    ("Household debt by state", "geography"),
    ("Mortgage holdings in California counties", "geography"),
    ("Monthly household debt in 2024", "frequency"),
])
def test_check_answerable_refuses(be, q, code):
    refused(core.check_answerable(be, q), code)


def test_check_answerable_passes(be):
    for q in ("What was the public share in 2007Q4?", "Mortgages held by banks in 2011Q4",
              "State and local governments' holdings", "Federal government share of student loans is in holdings"[:30]):
        assert core.check_answerable(be, q)["ok"], q


def test_tool_level_quarter_refusals(be):
    refused(core.public_share(be, "2027Q1", "2027Q4"), "future_or_unpublished")
    refused(core.public_share(be, "1940Q1", "1945Q1"), "before_coverage")
    refused(core.holdings_by_bucket(be, "2030Q4"), "future_or_unpublished")
    refused(core.holdings_by_bucket(be, "1950Q1"), "before_coverage")
    refused(core.collateral_coverage(be, "2026Q3", "2026Q3"), "future_or_unpublished")
    refused(core.nyfed_by_type(be, "2030Q1", "2030Q2"), "future_or_unpublished")


# ------------------------------------------------------------------ validation cross-check (C2, C3)
def test_c2_c3_match_validation_results(be):
    checks = {c["id"]: c for c in json.loads(repo_file("validation", "results.json").read_text())["checks"]}
    row = core.public_share(be, "2026Q2", "2026Q2")["data"][0]
    # C2: expected "56.4%", observed "56.38%"
    assert checks["C2"]["status"] == "PASS"
    assert row["public_share_display"] == checks["C2"]["expected"] == "56.4%"
    assert f"{row['public_share'] * 100:.2f}%" == checks["C2"]["observed"]
    # C3: expected "$10.77T of $19.10T", observed "$10.768T of $19.097T"
    assert checks["C3"]["status"] == "PASS"
    assert f"{row['public_usd_display']} of {row['scope_usd_display']}" == checks["C3"]["expected"]
    obs = f"${row['public_musd'] / 1e6:.3f}T of ${row['scope_total_musd'] / 1e6:.3f}T"
    assert obs == checks["C3"]["observed"]
    # and the register agrees
    reg = core.lookup_claim(be, "public_usd_2026q2")["data"][0]
    assert reg["display"] == row["public_usd_display"]
