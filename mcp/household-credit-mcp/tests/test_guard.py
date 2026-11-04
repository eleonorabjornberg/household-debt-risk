import os
from datetime import date
from decimal import Decimal

import pytest

from household_credit_mcp import backends
from household_credit_mcp.backends import ALLOWED_SQL, GuardError, ReadOnlyDB


class FakeCursor:
    description = [("date",), ("x",)]

    def __init__(self, log): self.log = log
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, sql, params=None): self.log.append(("execute", sql, params))
    def fetchall(self): return [(date(2026, 6, 30), Decimal("1.5"))]


class FakeConn:
    def __init__(self): self.log = []; self._ro = None; self.closed = False
    @property
    def read_only(self): return self._ro
    @read_only.setter
    def read_only(self, v): self._ro = v; self.log.append(("read_only", v))
    def cursor(self): return FakeCursor(self.log)
    def rollback(self): self.log.append(("rollback",))
    def close(self): self.closed = True


def make():
    conn = FakeConn()
    return ReadOnlyDB("postgres://x", connect=lambda url, **kw: conn), conn


def test_sets_read_only_and_timeout_before_query():
    db, conn = make()
    rows = db.fetch("public_share", "2026-06-30", "2026-06-30")
    assert conn.log[0] == ("read_only", True)
    assert conn.log[1][1] == "SET LOCAL statement_timeout = 15000"
    assert conn.log[2][1] == ALLOWED_SQL["public_share"] and conn.log[2][2] == ("2026-06-30", "2026-06-30")
    assert conn.log[-1] == ("rollback",) and conn.closed
    assert rows == [{"date": "2026-06-30", "x": 1.5}]


@pytest.mark.parametrize("sql", [
    "DELETE FROM mart.public_share", "SELECT 1", "SELECT * FROM raw.observations",
    ALLOWED_SQL["public_share"] + " ; DROP TABLE x", "insert into mart.public_share values (1)",
    "SELECT date FROM mart.public_share WHERE date = '2026-06-30'",
])
def test_refuses_anything_but_own_selects(sql):
    db, conn = make()
    with pytest.raises(GuardError):
        db.run_sql(sql)
    assert conn.log == []  # never even connected


def test_refuses_unknown_query_name():
    db, _ = make()
    with pytest.raises(GuardError):
        db.fetch("drop_everything")


def test_all_allowed_sql_are_selects_on_mart_only():
    for name, sql in ALLOWED_SQL.items():
        s = sql.strip().lower()
        assert s.startswith("select"), name
        assert ";" not in s and "raw." not in s and "core." not in s, name
        assert "mart." in s, name
        assert not any(w in s.split() for w in ("insert", "update", "delete", "drop", "alter", "create", "grant")), name


def test_get_backend_default_is_snapshot(monkeypatch):
    monkeypatch.delenv("DATABASE_URL_READONLY", raising=False)
    assert backends.get_backend().name == "snapshot"
    monkeypatch.setenv("DATABASE_URL_READONLY", "postgres://u@h/db")
    # Since 2026-11-04 get_backend probes the database once: reachable -> postgres (tests/test_fallback.py
    # covers the unreachable case, which falls back to the snapshots).
    conn = type("Conn", (), {"read_only": False, "rollback": lambda self: None, "close": lambda self: None})
    assert backends.get_backend(connect=lambda url, **kw: conn()).name == "postgres"


@pytest.mark.skipif(not os.environ.get("DATABASE_URL_READONLY"), reason="DATABASE_URL_READONLY not set")
def test_live_db_read_only_and_matches_snapshot():
    from household_credit_mcp import core
    be = backends.PostgresBackend(os.environ["DATABASE_URL_READONLY"])
    import psycopg
    try:
        r = core.public_share(be, "2026Q2", "2026Q2")
    except psycopg.OperationalError as e:
        pytest.skip(f"database unreachable from this environment: {type(e).__name__}")
    assert r["backend"] == "postgres" and r["data"][0]["public_share_display"]
    with pytest.raises(Exception):
        be.db._open().cursor().execute("CREATE TABLE mart.zz (x int)")
