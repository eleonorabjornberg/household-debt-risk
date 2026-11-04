"""DATABASE_URL_READONLY set but the database unreachable: fall back to snapshots, say so (D5 fix, 2026-11-04)."""
import pytest

from household_credit_mcp import core
from household_credit_mcp.backends import PostgresBackend, SnapshotBackend, get_backend

# .invalid never resolves (RFC 2606), so this fails at name resolution like the cloud sandbox's pooler host.
UNRESOLVABLE = "postgresql://research_reader:x@db.does-not-exist.invalid:5432/postgres"


def test_unresolvable_host_falls_back_to_snapshots(monkeypatch):
    monkeypatch.setenv("DATABASE_URL_READONLY", UNRESOLVABLE)
    monkeypatch.delenv("HOUSEHOLD_CREDIT_REQUIRE_DB", raising=False)
    be = get_backend()
    assert isinstance(be, SnapshotBackend) and "database unreachable" in be.note
    out = core.public_share(be, "2026Q2", "2026Q2", "total")
    assert out["ok"] and out["backend"] == "snapshot"
    assert "database unreachable" in out["backend_note"] and out["data"]


def test_require_db_keeps_the_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL_READONLY", UNRESOLVABLE)
    monkeypatch.setenv("HOUSEHOLD_CREDIT_REQUIRE_DB", "1")
    with pytest.raises(Exception):
        get_backend()


def test_reachable_database_uses_postgres(monkeypatch):
    class Conn:
        read_only = False

        def rollback(self):
            pass

        def close(self):
            pass

    monkeypatch.setenv("DATABASE_URL_READONLY", "postgresql://ok")
    assert isinstance(get_backend(connect=lambda url, **kw: Conn()), PostgresBackend)


def test_no_url_is_plain_snapshot(monkeypatch):
    monkeypatch.delenv("DATABASE_URL_READONLY", raising=False)
    be = get_backend()
    assert isinstance(be, SnapshotBackend) and be.note is None
    assert "backend_note" not in core.public_share(be, "2026Q2", "2026Q2", "total")
