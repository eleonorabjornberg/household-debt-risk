"""Load into Postgres in ONE transaction:
  1. upsert data/staging/*.csv into raw.observations (every vintage kept; same vintage -> value updated)
  2. replace the contents of core.* and mart.* with data/out/*.csv (DELETE + COPY, so concurrent
     readers such as Tableau live connections keep seeing the previous version until commit).
"""
from __future__ import annotations

import datetime as dt
import logging
import math

import pandas as pd

from . import db, transform
from .extract import read_staging

log = logging.getLogger(__name__)
RAW_COLS = ["source", "series_id", "date", "value", "vintage"]


def _py(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.date()
    if v is pd.NaT:
        return None
    if hasattr(v, "item"):  # numpy scalar
        v = v.item()
        if isinstance(v, float) and math.isnan(v):
            return None
    return v


def _copy(cur, table: str, df: pd.DataFrame) -> None:
    cols = list(df.columns)
    with cur.copy(f"COPY {table} ({', '.join(cols)}) FROM STDIN") as cp:
        for row in df.itertuples(index=False, name=None):
            cp.write_row([_py(v) for v in row])


def upsert_raw(cur, raw: pd.DataFrame) -> int:
    cur.execute("CREATE TEMP TABLE _raw_stage (LIKE raw.observations INCLUDING DEFAULTS) ON COMMIT DROP")
    _copy(cur, "_raw_stage", raw[RAW_COLS])
    cur.execute("""
        INSERT INTO raw.observations (source, series_id, date, value, vintage)
        SELECT source, series_id, date, value, vintage FROM _raw_stage
        ON CONFLICT (series_id, date, vintage) DO UPDATE
           SET value = EXCLUDED.value, source = EXCLUDED.source, loaded_at = now()
         WHERE raw.observations.value IS DISTINCT FROM EXCLUDED.value
    """)
    return cur.rowcount


def replace_tables(cur, tables: dict[str, pd.DataFrame]) -> None:
    for name in reversed(transform.TABLE_ORDER):
        cur.execute(f"DELETE FROM {name}")
    for name in transform.TABLE_ORDER:
        _copy(cur, name, tables[name][transform.COLUMNS[name]])
        log.info("load: %s <- %d rows", name, len(tables[name]))


def run(raw: pd.DataFrame | None = None, tables: dict[str, pd.DataFrame] | None = None) -> None:
    if raw is None:
        raw = pd.concat([read_staging(s) for s in ("z1", "fred", "nyfed") if _exists(s)], ignore_index=True)
    tables = tables or transform.read_out()
    with db.connect() as conn, conn.cursor() as cur:
        n = upsert_raw(cur, raw)
        log.info("load: raw.observations upserted %d new/changed rows (of %d staged)", n, len(raw))
        replace_tables(cur, tables)
    log.info("load: committed")


def _exists(source: str) -> bool:
    from .extract import staging_path
    return staging_path(source).exists()
