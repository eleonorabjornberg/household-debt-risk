from __future__ import annotations

import psycopg

from . import config


def connect(url: str | None = None) -> psycopg.Connection:
    url = url or config.database_url()
    if not url:
        raise SystemExit("DATABASE_URL is not set (see .env.example)")
    # prepare_threshold=None: Supabase's pooler (transaction mode) does not support prepared statements.
    return psycopg.connect(url, prepare_threshold=None)
