"""Extractors. Each writes data/staging/<source>.csv with columns
source, series_id, date, value, vintage (the raw.observations shape, minus loaded_at)."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import requests

from .. import config

log = logging.getLogger(__name__)
STAGING_COLUMNS = ["source", "series_id", "date", "value", "vintage"]


def staging_path(source: str) -> Path:
    return config.STAGING_DIR / f"{source}.csv"


def write_staging(source: str, df: pd.DataFrame) -> Path:
    df = df[STAGING_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["vintage"] = pd.to_datetime(df["vintage"]).dt.date
    df = df.dropna(subset=["value"]).sort_values(["series_id", "date"])
    if df.duplicated(["series_id", "date", "vintage"]).any():
        raise ValueError(f"{source}: duplicate (series_id, date, vintage) in extract")
    path = staging_path(source)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log.info("%s: wrote %d rows (%d series) to %s", source, len(df), df.series_id.nunique(), path)
    return path


def read_staging(source: str) -> pd.DataFrame:
    path = staging_path(source)
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run `hhdebt extract` first")
    df = pd.read_csv(path, dtype={"series_id": str})
    df["date"] = pd.to_datetime(df["date"])
    df["vintage"] = pd.to_datetime(df["vintage"])
    return df


def http_get(url: str, **kw) -> requests.Response:
    kw.setdefault("timeout", 120)
    headers = {**config.HTTP_HEADERS, **kw.pop("headers", {})}
    r = requests.get(url, headers=headers, **kw)
    r.raise_for_status()
    return r
