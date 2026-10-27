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


@pytest.mark.skipif(not os.environ.get("TABLEAU_READER_URL"), reason="TABLEAU_READER_URL not set")
def test_tableau_reader_permissions():
    import psycopg
    with psycopg.connect(os.environ["TABLEAU_READER_URL"], autocommit=True) as conn:
        assert conn.execute("SELECT count(*) FROM mart.public_share").fetchone()[0] > 0
        assert conn.execute("SELECT count(*) FROM core.dim_crisis").fetchone()[0] == 14
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("SELECT 1 FROM raw.observations LIMIT 1")
