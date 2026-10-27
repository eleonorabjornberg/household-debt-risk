"""Write web/public/data/<table>.json snapshots (offline fallback for the website).

Each file is a JSON array of row objects with the DB column names; dates are ISO strings
(YYYY-MM-DD), numerics are JSON numbers, NULL is null. Source: the database when DATABASE_URL is
set (the published state), else the local transform output in data/out/.
"""
from __future__ import annotations

import datetime as dt
import decimal
import json
import logging

import pandas as pd

from . import config, db, transform

log = logging.getLogger(__name__)
ORDER_BY = {"core.dim_crisis": ["start_q", "crisis_id"], "core.dim_risk_bucket": ["sort_order"]}
SNAPSHOT_TABLES = ["mart.debt_by_risk_holder", "mart.public_share", "mart.collateral_coverage",
                   "mart.crisis_event_window", "mart.nyfed_by_type", "core.dim_crisis", "core.dim_risk_bucket"]


def _json_value(v):
    """DB/pandas value -> JSON-native value (integral numbers are written without '.0')."""
    if v is None:
        return None
    if isinstance(v, (pd.Timestamp, dt.datetime)):
        return None if pd.isna(v) else v.date().isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    if hasattr(v, "item"):  # numpy scalar
        v = v.item()
    if isinstance(v, bool):
        return v
    if isinstance(v, (decimal.Decimal, float)):
        if v != v:  # NaN
            return None
        return int(v) if v == int(v) else float(v)
    return v


def _order(name: str) -> list[str]:
    return ORDER_BY.get(name, transform.PRIMARY_KEYS[name])


def _rows_from_db() -> dict[str, list[dict]]:
    out = {}
    with db.connect() as conn, conn.cursor() as cur:
        for name in SNAPSHOT_TABLES:
            cols = transform.COLUMNS[name]
            cur.execute(f"SELECT {', '.join(cols)} FROM {name} ORDER BY {', '.join(_order(name))}")
            out[name] = [dict(zip(cols, map(_json_value, r))) for r in cur.fetchall()]
    return out


def _rows_from_out() -> dict[str, list[dict]]:
    tables = transform.read_out()
    out = {}
    for name in SNAPSHOT_TABLES:
        df = tables[name].sort_values(_order(name))
        out[name] = [{k: _json_value(v) for k, v in zip(df.columns, row)} for row in df.itertuples(index=False, name=None)]
    return out


def run(source: str = "auto") -> None:
    use_db = source == "db" or (source == "auto" and config.database_url())
    rows = _rows_from_db() if use_db else _rows_from_out()
    config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in rows.items():
        path = config.SNAPSHOT_DIR / f"{name.split('.', 1)[1]}.json"
        path.write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")
        log.info("export: %s (%d rows) -> %s", name, len(data), path)
    meta_path = config.OUT_DIR / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["snapshot_source"] = "database" if use_db else "local transform output"
        meta["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        (config.SNAPSHOT_DIR / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
