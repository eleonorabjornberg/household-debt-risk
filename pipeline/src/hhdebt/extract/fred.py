"""FRED context series. Uses the API when FRED_API_KEY is set, else fredgraph.csv (no key).

Observations are stored at native frequency in raw (monthly CPI, weekly WSHOMCB...); the transform
step converts them to quarters. Vintage = series `last_updated` date from the API when available,
otherwise the download date (fredgraph.csv carries no release date).

Pinned runs (PLAN F2, decision F2-1): with HHDEBT_FRED_ASOF=YYYY-MM-DD the API is asked for the data as
they stood on that date (ALFRED realtime_start = realtime_end = as-of), so a rerun reproduces the
committed numbers exactly; the vintage recorded is the as-of date. `make` sets it from the committed
web/public/data/meta.json (vintages.fred); a refresh moves it on purpose. Pinning needs FRED_API_KEY.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import logging
import os

import pandas as pd

from .. import config
from . import download_raw, write_staging

log = logging.getLogger(__name__)


def asof() -> dt.date | None:
    v = os.environ.get("HHDEBT_FRED_ASOF") or None
    return dt.date.fromisoformat(v) if v else None


def _via_alfred(sid: str, key: str, day: dt.date) -> tuple[pd.DataFrame, dt.date]:
    obs = json.loads(download_raw(
        "fred", f"{config.FRED_API_URL}/series/observations", f"{sid}_observations_asof_{day}.json",
        params={"series_id": sid, "api_key": key, "file_type": "json",
                "realtime_start": day.isoformat(), "realtime_end": day.isoformat()}, vintage=day,
    ).path.read_bytes())["observations"]
    return pd.DataFrame(obs)[["date", "value"]], day


def _via_api(sid: str, key: str) -> tuple[pd.DataFrame, dt.date]:
    meta = json.loads(download_raw(
        "fred", f"{config.FRED_API_URL}/series", f"{sid}_series.json",
        params={"series_id": sid, "api_key": key, "file_type": "json"}).path.read_bytes())
    last_updated = pd.Timestamp(meta["seriess"][0]["last_updated"][:10]).date()
    obs = json.loads(download_raw(
        "fred", f"{config.FRED_API_URL}/series/observations", f"{sid}_observations.json",
        params={"series_id": sid, "api_key": key, "file_type": "json"}, vintage=last_updated,
    ).path.read_bytes())["observations"]
    df = pd.DataFrame(obs)[["date", "value"]]
    return df, last_updated


def _via_csv(sid: str) -> tuple[pd.DataFrame, dt.date]:
    vintage = dt.date.today()
    rec = download_raw("fred", config.FRED_CSV_URL.format(id=sid), f"{sid}.csv", vintage=vintage)
    df = pd.read_csv(io.StringIO(rec.path.read_text(encoding="utf-8")))
    df.columns = ["date", "value"]
    return df, vintage


def extract() -> pd.DataFrame:
    key = os.environ.get("FRED_API_KEY") or None
    day = asof()
    if day and not key:
        raise RuntimeError("HHDEBT_FRED_ASOF needs FRED_API_KEY (ALFRED vintages are API-only)")
    frames = []
    for sid in config.series_ids("fred"):
        df, vintage = _via_alfred(sid, key, day) if day else _via_api(sid, key) if key else _via_csv(sid)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")  # "." = missing
        df = df.dropna(subset=["value"])
        df["series_id"], df["source"], df["vintage"] = sid, "fred", vintage
        log.info("fred: %s %d obs %s..%s (vintage %s)", sid, len(df), df.date.min(), df.date.max(), vintage)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def run() -> None:
    write_staging("fred", extract())
