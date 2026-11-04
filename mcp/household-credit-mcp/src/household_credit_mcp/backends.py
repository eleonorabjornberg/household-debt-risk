"""Two data backends behind one interface.

* SnapshotBackend: the committed JSON snapshots of the mart tables (web/public/data). Default.
* PostgresBackend: read-only Postgres via DATABASE_URL_READONLY. Only the parameterised SELECTs
  in ALLOWED_SQL can run; the client never supplies SQL.
"""
from __future__ import annotations

import json
import os
from datetime import date
from decimal import Decimal
from functools import cached_property
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[4]


def snapshot_dir() -> Path:
    return Path(os.environ.get("HOUSEHOLD_CREDIT_SNAPSHOT_DIR") or REPO_ROOT / "web" / "public" / "data")


def repo_file(*parts: str) -> Path:
    base = os.environ.get("HOUSEHOLD_CREDIT_REPO_ROOT")
    return (Path(base) if base else REPO_ROOT).joinpath(*parts)


class SnapshotBackend:
    name = "snapshot"

    def __init__(self, directory: Path | None = None):
        self.dir = Path(directory) if directory else snapshot_dir()

    def _load(self, table: str) -> list[dict]:
        return _load_json(str(self.dir / f"{table}.json"))

    @cached_property
    def meta(self) -> dict:
        return json.loads((self.dir / "meta.json").read_text())

    def vintages(self) -> dict:
        return {**self.meta["vintages"], "snapshot_generated_at": self.meta.get("generated_at"),
                "source": f"meta.json ({self.meta.get('snapshot_source', 'snapshot')} export)"}

    def mart_range(self) -> tuple[str, str]:
        rows = self._load("public_share")
        return rows[0]["date"], rows[-1]["date"]

    def public_share(self, start: str, end: str) -> list[dict]:
        return [r for r in self._load("public_share") if start <= r["date"] <= end]

    def holdings(self, d: str) -> list[dict]:
        return [r for r in self._load("debt_by_risk_holder") if r["date"] == d]

    def risk_buckets(self) -> list[dict]:
        return self._load("dim_risk_bucket")

    def coverage(self, start: str, end: str) -> list[dict]:
        return [r for r in self._load("collateral_coverage") if start <= r["date"] <= end]

    def nyfed(self, start: str, end: str) -> list[dict]:
        return [r for r in self._load("nyfed_by_type") if start <= r["date"] <= end]

    def nyfed_range(self) -> tuple[str, str]:
        rows = self._load("nyfed_by_type")
        return min(r["date"] for r in rows), max(r["date"] for r in rows)

    def crises(self) -> list[dict]:
        return self._load("dim_crisis")

    def crisis_window(self, metric: str, crisis_id: str | None) -> list[dict]:
        return [r for r in self._load("crisis_event_window")
                if r["metric"] == metric and (crisis_id is None or r["crisis_id"] == crisis_id)]


from functools import lru_cache  # noqa: E402


@lru_cache(maxsize=32)
def _load_json(path: str) -> list[dict]:
    return json.loads(Path(path).read_text())


# ---------------------------------------------------------------------------------------------
# Postgres
# ---------------------------------------------------------------------------------------------
class GuardError(Exception):
    """Raised when something other than one of the server's own SELECTs is attempted."""


ALLOWED_SQL: dict[str, str] = {
    "mart_range": "SELECT min(date) AS lo, max(date) AS hi FROM mart.public_share",
    "public_share": ("SELECT date, scope_total_musd, public_musd, public_share, public_share_mortgage, "
                     "public_share_cc, fed_mbs_musd, fed_mbs_share_of_scope FROM mart.public_share "
                     "WHERE date BETWEEN %s AND %s ORDER BY date"),
    "holdings": ("SELECT date, risk_bucket, debt_type, nominal_musd, real_musd, share_of_total, pct_of_dpi "
                 "FROM mart.debt_by_risk_holder WHERE date = %s ORDER BY risk_bucket, debt_type"),
    "risk_buckets": "SELECT risk_bucket, label, is_public, sort_order FROM mart.dim_risk_bucket ORDER BY sort_order",
    "coverage": ("SELECT date, collateral_class, debt_musd, collateral_value_musd, coverage_ratio, share_of_debt, "
                 "is_estimated FROM mart.collateral_coverage WHERE date BETWEEN %s AND %s "
                 "ORDER BY date, collateral_class"),
    "nyfed": ("SELECT date, loan_type, balance_busd, transition_serious_pct FROM mart.nyfed_by_type "
              "WHERE date BETWEEN %s AND %s ORDER BY date, loan_type"),
    "nyfed_range": "SELECT min(date) AS lo, max(date) AS hi FROM mart.nyfed_by_type",
    "crises": "SELECT crisis_id, name, kind, start_q, end_q, notes FROM mart.dim_crisis ORDER BY start_q",
    "crisis_window": ("SELECT crisis_id, metric, q_offset, date, value, value_at_t0, delta_from_t0 "
                      "FROM mart.crisis_event_window WHERE metric = %s AND (%s::text IS NULL OR crisis_id = %s) "
                      "ORDER BY crisis_id, q_offset"),
}
STATEMENT_TIMEOUT_MS = 15000


def _clean(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, date):
        return v.isoformat()
    return v


class ReadOnlyDB:
    """Runs only ALLOWED_SQL, inside a read-only transaction with a 15 s statement timeout."""

    def __init__(self, url: str, connect: Callable[..., Any] | None = None):
        self.url = url
        self._connect = connect

    def _open(self):
        if self._connect is None:
            import psycopg
            self._connect = psycopg.connect
        conn = self._connect(self.url, connect_timeout=10)
        conn.read_only = True  # BEGIN READ ONLY; must be set before the first statement
        return conn

    def run_sql(self, sql: str, params: tuple = ()) -> list[dict]:
        if sql not in ALLOWED_SQL.values():
            raise GuardError("refused: only the server's own parameterised SELECTs may run")
        conn = self._open()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SET LOCAL statement_timeout = {STATEMENT_TIMEOUT_MS}")
                cur.execute(sql, params)
                cols = [c[0] for c in cur.description]
                rows = [{c: _clean(v) for c, v in zip(cols, row)} for row in cur.fetchall()]
            return rows
        finally:
            try:
                conn.rollback()
            finally:
                conn.close()

    def fetch(self, name: str, *params: Any) -> list[dict]:
        if name not in ALLOWED_SQL:
            raise GuardError(f"refused: unknown query {name!r}")
        return self.run_sql(ALLOWED_SQL[name], tuple(params))


class PostgresBackend:
    name = "postgres"

    def __init__(self, url: str, snapshot: SnapshotBackend | None = None, db: ReadOnlyDB | None = None):
        self.db = db or ReadOnlyDB(url)
        self._snap = snapshot or SnapshotBackend()

    def vintages(self) -> dict:
        # research_reader cannot read raw.observations / core.fact_quarterly, so the DB cannot report vintages.
        v = self._snap.vintages()
        v["source"] = ("meta.json snapshot; research_reader cannot read raw/core vintages, "
                       "so the live DB may be newer than this vintage")
        return v

    def mart_range(self):
        r = self.db.fetch("mart_range")[0]
        return r["lo"], r["hi"]

    def public_share(self, start, end):
        return self.db.fetch("public_share", start, end)

    def holdings(self, d):
        return self.db.fetch("holdings", d)

    def risk_buckets(self):
        return self.db.fetch("risk_buckets")

    def coverage(self, start, end):
        return self.db.fetch("coverage", start, end)

    def nyfed(self, start, end):
        return self.db.fetch("nyfed", start, end)

    def nyfed_range(self):
        r = self.db.fetch("nyfed_range")[0]
        return r["lo"], r["hi"]

    def crises(self):
        return self.db.fetch("crises")

    def crisis_window(self, metric, crisis_id):
        return self.db.fetch("crisis_window", metric, crisis_id, crisis_id)


def get_backend():
    url = os.environ.get("DATABASE_URL_READONLY")
    return PostgresBackend(url) if url else SnapshotBackend()
