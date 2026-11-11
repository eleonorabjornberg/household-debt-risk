"""B4 student-loan proxy (card cbo-repo-55 (b)): the committed extract and the proxy totals."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


sp, ex = load("student_proxy"), load("cbo_extract")
ROWS = list(csv.DictReader(open(HERE / "cbo_direct_loan_outlays.csv", newline="")))


def test_extract_is_one_account_three_baselines_with_recorded_hashes():
    assert {r["tin"] for r in ROWS} == {ex.TIN} and {r["title"] for r in ROWS} == {ex.TITLE}
    assert {r["baseline"] for r in ROWS} == set(ex.FILES)
    for r in ROWS:
        assert r["file_sha256"] == ex.FILES[r["baseline"]][1]
    # the sources.md record carries the same hashes and the commit
    src = (HERE / "sources.md").read_text()
    assert ex.COMMIT in src and all(h in src for _, h in ex.FILES.values())


def test_proxy_totals_recomputed_independently():
    res = sp.compute(ROWS)
    years = range(res["fy_first"], res["fy_last"] + 1)
    before = sum(float(r["outlays_musd"]) for r in ROWS if r["baseline"] == "2025-01" and int(r["fiscal_year"]) in years)
    after = sum(float(r["outlays_musd"]) for r in ROWS if r["baseline"] == "2026-02" and int(r["fiscal_year"]) in years)
    assert (res["fy_first"], res["fy_last"]) == (2026, 2035)
    assert res["sum_before_musd"] == pytest.approx(before) and res["sum_after_musd"] == pytest.approx(after)
    assert res["change_musd"] == pytest.approx(after - before)
    assert "PROXY" in res["label"] and "not lending volume" in res["label"]


def test_committed_json_is_current():
    assert json.loads((HERE / "student_proxy.json").read_text()) == json.loads(json.dumps(sp.compute(ROWS)))


def test_extract_refuses_a_changed_file(tmp_path):
    for name, _ in ex.FILES.values():
        (tmp_path / name).write_text("date,tin,title,disc_or_mand,outlays,budget_authority\n")
    with pytest.raises(SystemExit):
        ex.extract(tmp_path)
