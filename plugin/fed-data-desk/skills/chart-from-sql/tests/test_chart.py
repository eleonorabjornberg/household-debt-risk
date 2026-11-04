import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import chart  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
Q = pd.date_range("2000-03-31", periods=12, freq="QE")


@pytest.fixture
def df():
    return pd.DataFrame({"date": Q.strftime("%Y-%m-%d"), "a": [0.10, 0.11, 0.13, 0.12, 0.15, 0.20, 0.18, 0.17, 0.16, 0.19, 0.22, 0.21],
                         "b": [0.30] * 12, "c": [0.05 + i / 100 for i in range(12)],
                         "lo": [0.09 + i / 100 for i in range(12)], "hi": [0.2 + i / 100 for i in range(12)]})


COMMON = dict(title="T", source="Test source", vintage="2026-01-01", ylabel="USD trillion", unit="USD trillion")


def run(df, tmp_path, kind, **kw):
    args = dict(COMMON, kind=kind, x="date", y=kw.pop("y", ["a"]), out=tmp_path / kind, **kw)
    return chart.make_chart(df, **args)


@pytest.mark.parametrize("kind,kw", [
    ("line", {"y": ["a", "b"]}), ("area", {"y": ["a", "b", "c"]}), ("bar", {"y": ["a", "b"]}),
    ("fan", {"bands": [("lo", "hi", "90% interval")], "origin": "2002-03-31"}),
    ("multiples", {"y": ["a", "b", "c"]}),
])
def test_each_kind_renders(df, tmp_path, kind, kw):
    s = run(df, tmp_path, kind, **kw)
    for f in ("png", "svg", "alt.txt", "json"):
        assert (tmp_path / f"{kind}.{f}").stat().st_size > 0
    assert (tmp_path / f"{kind}.png").read_bytes()[:4] == b"\x89PNG"
    assert s["row_count"] == 12


def test_hbar_renders_and_alt(tmp_path):
    d = pd.DataFrame({"label": ["A", "B", "C"], "v": [3.0, -1.5, 0.5], "side": ["public", "private", "public"]})
    s = chart.make_chart(d, kind="hbar", x="label", y="v", group="side", out=tmp_path / "h", **COMMON)
    assert "Largest positive: A, +3.00 USD trillion" in s["alt_text"]
    assert "Largest negative: B, -1.50" in s["alt_text"]
    assert "sum to +2.00" in s["alt_text"]


def test_alt_text_values_come_from_data(df, tmp_path):
    s = run(df, tmp_path, "line", y=["a"], as_percent=True, ylabel=None, unit=None)
    alt = (tmp_path / "line.alt.txt").read_text().strip()
    assert alt == s["alt_text"]
    assert "A rose from 10.0% in 2000Q1 to 21.0% in 2002Q4" in alt
    assert "(high 22.0% in 2002Q3" in alt
    assert "12 observations" in alt


def test_alt_text_changes_with_data(df, tmp_path):
    df2 = df.copy()
    df2["a"] = df2["a"] * 2
    s = run(df2, tmp_path, "line", as_percent=True, ylabel=None, unit=None)
    assert "from 20.0% in 2000Q1 to 42.0%" in s["alt_text"]


def test_recession_shading_and_alt(df, tmp_path):
    crisis = tmp_path / "crisis.json"
    crisis.write_text(json.dumps([
        {"kind": "nber_recession", "name": "r", "start_q": "2001-03-31", "end_q": "2001-12-31"},
        {"kind": "policy_shock", "name": "p", "start_q": "2001-06-30", "end_q": "2001-09-30"},
        {"kind": "nber_recession", "name": "out of range", "start_q": "1990-06-30", "end_q": "1991-03-31"}]))
    s = run(df, tmp_path, "line", recessions=str(crisis))
    assert s["recession_shading"] is True
    assert "1 NBER recession " in s["alt_text"] and "2001Q1 to 2001Q4" in s["alt_text"]


def test_default_crisis_file_has_nber_dates():
    rows = chart.load_recessions()
    assert len(rows) >= 5 and all(a < b for a, b, _ in rows)


def test_sidecar_contents(df, tmp_path):
    f = tmp_path / "in.csv"
    df.to_csv(f, index=False)
    d = chart.load_file(f)
    run(d, tmp_path, "line", data_source={"type": "file", "path": str(f)}, mode="both")
    side = json.loads((tmp_path / "line.json").read_text())
    assert side["data_source"]["path"] == str(f) and len(side["data_source"]["sha256"]) == 64
    assert side["vintage"] == "2026-01-01" and side["row_count"] == 12
    assert side["source_line"] == "Source: Test source (vintage 2026-01-01); chart: household-debt-risk"
    assert "line-dark.png" in side["files"] and (tmp_path / "line-dark.png").exists()


def test_requires_units_title_source_vintage(df, tmp_path):
    with pytest.raises(ValueError, match="units required"):
        chart.make_chart(df, kind="line", x="date", y="a", title="T", source="s", vintage="v", out=tmp_path / "x")
    for bad in ("title", "source", "vintage"):
        kw = dict(COMMON, **{bad: ""})
        with pytest.raises(ValueError, match=bad):
            chart.make_chart(df, kind="line", x="date", y="a", out=tmp_path / "x", **kw)


def test_stacked_rejects_negative(df, tmp_path):
    df["a"] = -df["a"]
    with pytest.raises(ValueError, match="non-negative"):
        run(df, tmp_path, "area")


def test_long_format_group(tmp_path):
    d = pd.DataFrame({"date": ["2000-03-31", "2000-06-30"] * 2, "g": ["u", "u", "w", "w"], "v": [1.0, 2.0, 3.0, 4.0]})
    s = chart.make_chart(d, kind="line", x="date", y="v", group="g", out=tmp_path / "g", **COMMON)
    assert "U rose from 1.00 USD trillion" in s["alt_text"]


def test_load_json_and_quarter_strings(tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps([{"quarter": "2008Q1", "v": 1}, {"quarter": "2008Q2", "v": 2}]))
    d = chart.load_file(p)
    s = chart.make_chart(d, kind="line", x="quarter", y="v", out=tmp_path / "q", **COMMON)
    assert "2008Q1 to 2008Q2" in s["alt_text"]


# ---- SQL path
@pytest.mark.parametrize("sql", [
    "DELETE FROM mart.public_share", "drop table x", "INSERT INTO t VALUES (1)", "UPDATE t SET a=1",
    "SELECT 1; SELECT 2", "SELECT 1; DROP TABLE x", "WITH d AS (DELETE FROM t RETURNING *) SELECT * FROM d",
    "SELECT * INTO newtab FROM t", "SELECT * FROM t FOR UPDATE", "COPY t TO '/tmp/x'", "SET ROLE postgres",
    "CREATE TABLE a AS SELECT 1", "", "-- hi\nDROP TABLE x", "/* SELECT */ DELETE FROM x", "SELECT $$x$$",
])
def test_sql_refuses_non_select(sql):
    with pytest.raises(ValueError):
        chart.check_select(sql)


@pytest.mark.parametrize("sql", [
    "SELECT date, public_share FROM mart.public_share ORDER BY date;",
    "  with t as (select 1 as a) select * from t",
    "SELECT 'drop table' AS s, \"update\" FROM x -- delete",
    "SELECT 1 /* insert */",
])
def test_sql_accepts_select(sql):
    assert chart.check_select(sql)


def test_run_sql_refuses_before_connecting(monkeypatch):
    monkeypatch.setenv("DATABASE_URL_READONLY", "postgresql://nobody@127.0.0.1:1/none")
    with pytest.raises(ValueError):
        chart.run_sql("DELETE FROM t")


def test_run_sql_without_env_var(monkeypatch):
    monkeypatch.delenv("DATABASE_URL_READONLY", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL_READONLY"):
        chart.run_sql("SELECT 1")


def test_cli_file_roundtrip(df, tmp_path):
    f = tmp_path / "in.csv"
    df.to_csv(f, index=False)
    rc = chart.main(["--file", str(f), "--kind", "line", "--x", "date", "--y", "a", "--as-percent", "--title", "T",
                     "--source", "Test", "--vintage", "v1", "--out", str(tmp_path / "cli")])
    assert rc == 0 and (tmp_path / "cli.png").exists()
