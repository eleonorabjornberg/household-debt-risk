"""Snapshot JSON shape, and (when DATABASE_URL is set) the loaded database."""
import json
import os

import pytest

from hhdebt import config, transform
from hhdebt.export import SNAPSHOT_TABLES


@pytest.mark.parametrize("table", SNAPSHOT_TABLES)
def test_snapshot_files(table):
    path = config.SNAPSHOT_DIR / f"{table.split('.', 1)[1]}.json"
    if not path.exists():
        pytest.skip(f"{path} not exported")
    rows = json.loads(path.read_text())
    assert isinstance(rows, list) and rows
    assert list(rows[0]) == transform.COLUMNS[table]
    for col in ("date", "start_q", "end_q"):
        if col in rows[0]:
            assert all(r[col] is None or (isinstance(r[col], str) and len(r[col]) == 10) for r in rows)


needs_db = pytest.mark.skipif(not config.database_url(), reason="DATABASE_URL not set")


@needs_db
def test_db_tables_match_transform_output(out):
    from hhdebt import db
    with db.connect() as conn, conn.cursor() as cur:
        for name in transform.TABLE_ORDER:
            cur.execute(f"SELECT count(*) FROM {name}")
            assert cur.fetchone()[0] == len(out[name]), name
        cur.execute("SELECT count(*) FROM raw.observations")
        assert cur.fetchone()[0] >= len(out["core.fact_quarterly"]) - 1000  # raw keeps native frequency + vintages


@pytest.mark.skipif(not os.environ.get("DATABASE_URL_READONLY"), reason="DATABASE_URL_READONLY not set")
def test_research_reader_is_read_only():
    """research_reader (supabase/migrations/20261103000000_research_reader.sql): reads mart and the
    core dims, cannot read raw or core.fact_quarterly, cannot write, and starts every session read-only."""
    import psycopg
    with psycopg.connect(os.environ["DATABASE_URL_READONLY"], autocommit=True) as conn:
        assert conn.execute("SELECT current_user").fetchone()[0] == "research_reader"
        conn.execute("SELECT count(*) FROM mart.public_share").fetchone()
        conn.execute("SELECT count(*) FROM mart.dim_crisis").fetchone()
        conn.execute("SELECT count(*) FROM core.dim_series").fetchone()
        assert conn.execute("SHOW default_transaction_read_only").fetchone()[0] == "on"
        for sql in ("SELECT 1 FROM raw.observations LIMIT 1", "SELECT 1 FROM core.fact_quarterly LIMIT 1"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute(sql)
        with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
            conn.execute("DELETE FROM mart.public_share")
        with conn.transaction():
            conn.execute("SET TRANSACTION READ WRITE")
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute("DELETE FROM mart.public_share")
