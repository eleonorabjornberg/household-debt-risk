"""Minimal FRED / ALFRED client for the research tasks (B1, C1).

Raw API responses are cached under data/fred/ (git-ignored) and every download appends a line to
data/fred/manifest.jsonl with URL (API key removed), retrieval time (UTC), bytes and SHA-256, as the
standard of evidence asks. Reads are served from the cache when present, so a rerun reads the same bytes.

    from fred import observations, vintages
    obs = observations("MORTGAGE30US")                     # latest vintage, pandas Series
    v = vintages("TOTALSL")                                # every ALFRED vintage, long DataFrame

The API key comes from FRED_API_KEY in the environment and is never written to disk or printed.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "fred"
API = "https://api.stlouisfed.org/fred/"


def _get(endpoint: str, params: dict, tag: str, refresh: bool = False) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{tag}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_bytes())
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError("FRED_API_KEY is not set (cloud environment settings)")
    public_url = API + endpoint + "?" + urllib.parse.urlencode({**params, "file_type": "json"})
    url = public_url + "&api_key=" + key
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                body = r.read()
            break
        except Exception:  # network hiccup or FRED rate limit (120 requests/minute)
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
    path.write_bytes(body)
    rec = {
        "tag": tag,
        "url": public_url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    with open(CACHE / "manifest.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    return json.loads(body)


def _num(v: str) -> float:
    return float("nan") if v in (".", "") else float(v)


def observations(series_id: str, refresh: bool = False) -> pd.Series:
    """Latest-vintage observations as a float Series indexed by date (missing '.' -> NaN)."""
    d = _get("series/observations", {"series_id": series_id}, f"obs_{series_id}", refresh)
    obs = d["observations"]
    s = pd.Series([_num(o["value"]) for o in obs], index=pd.to_datetime([o["date"] for o in obs]), name=series_id)
    return s


def vintages(series_id: str, refresh: bool = False) -> pd.DataFrame:
    """All ALFRED vintages: one row per (date, realtime_start, realtime_end, value).

    realtime_start is the day the value became public; realtime_end the last day it was current
    ('9999-12-31' for the current value). A value known on day t is the row with
    realtime_start <= t <= realtime_end.
    """
    params = {"series_id": series_id, "realtime_start": "1776-07-04", "realtime_end": "9999-12-31",
              "output_type": 1, "limit": 100000}
    d = _get("series/observations", params, f"alfred_{series_id}", refresh)
    if "count" not in d:
        raise RuntimeError(f"{series_id}: ALFRED response has no 'count'; cannot check completeness")
    if int(d["count"]) > len(d["observations"]):
        raise RuntimeError(f"{series_id}: {d['count']} vintage rows, only {len(d['observations'])} returned; paginate")
    df = pd.DataFrame(d["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["realtime_start"] = pd.to_datetime(df["realtime_start"])
    df["realtime_end"] = pd.to_datetime(df["realtime_end"].replace("9999-12-31", "2262-04-11"))
    df["value"] = df["value"].map(_num)
    return df[["date", "realtime_start", "realtime_end", "value"]]


def series_info(series_id: str, refresh: bool = False) -> dict:
    return _get("series", {"series_id": series_id}, f"info_{series_id}", refresh)["seriess"][0]


def manifest() -> list[dict]:
    p = CACHE / "manifest.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def units_history(series_id: str, refresh: bool = False) -> pd.DataFrame:
    """Units label of a series over real time (ALFRED series metadata): realtime_start, realtime_end, units."""
    d = _get("series", {"series_id": series_id, "realtime_start": "1776-07-04", "realtime_end": "9999-12-31"},
             f"units_{series_id}", refresh)
    h = pd.DataFrame(d["seriess"])[["realtime_start", "realtime_end", "units"]]
    h["realtime_start"] = pd.to_datetime(h["realtime_start"])
    h["realtime_end"] = pd.to_datetime(h["realtime_end"].replace("9999-12-31", "2262-04-11"))
    return h


SCALE = {"thousands": 1e-3, "millions": 1.0, "billions": 1e3, "trillions": 1e6}


def to_millions(v: pd.DataFrame, units: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Rescale every vintage row to millions using the units label that was current when it was published.

    Returns the rescaled frame and the number of rows changed. Units without a dollar scale word
    (percent, index) are returned unchanged. Uses only the label in force at each row's realtime_start,
    so it adds no look-ahead.
    """
    def factor(label: str):
        w = label.lower().split()[0]
        return SCALE.get(w)

    out = v.copy()
    f = pd.Series(1.0, index=out.index)
    for _, u in units.iterrows():
        k = factor(u["units"])
        if k is None:
            labels = set(units["units"])
            if any(factor(x) is not None for x in labels):
                raise ValueError(f"mixed units labels, some without a dollar scale: {labels}")
            return v, 0  # non-dollar series (percent, index): nothing to rescale
        m = (out["realtime_start"] >= u["realtime_start"]) & (out["realtime_start"] <= u["realtime_end"])
        f[m] = k
    out["value"] = out["value"] * f
    return out, int((f != 1.0).sum())
