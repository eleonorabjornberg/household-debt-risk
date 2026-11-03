"""Fed Z.1 Financial Accounts: download FRB_Z1_csv.zip and stream-filter Z1.csv.

Z1.csv is a 3+ GB long CSV (series_name,...,date,value; series_name like "Z1/Z1/FL153165105.Q").
We never unzip it: the member is streamed line by line and only catalog series are parsed.
Vintage = the Z1.csv member timestamp inside the zip (the release date), e.g. 2026-09-11.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import logging
import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd

from .. import config
from . import download_raw, record_local, write_staging

log = logging.getLogger(__name__)
PREFIX = b"Z1/Z1/"


def download_zip(dest: Path | None = None, force: bool = False) -> Path:
    dest = dest or config.DATA_DIR / "z1" / "FRB_Z1_csv.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        # Reuse the local copy unless the server's copy has a different size (new release).
        try:
            import requests
            head = requests.head(config.Z1_ZIP_URL, headers=config.HTTP_HEADERS, timeout=60, allow_redirects=True)
            remote_size = int(head.headers.get("content-length", -1))
        except Exception as e:  # offline: keep the cached copy
            log.warning("z1: HEAD failed (%s); using cached %s", e, dest)
            record_local("z1", dest, vintage=_zip_vintage(dest), skip_if_recorded=True)
            return dest
        if remote_size in (-1, dest.stat().st_size):
            log.info("z1: cached %s is current", dest)
            record_local("z1", dest, vintage=_zip_vintage(dest), skip_if_recorded=True)
            return dest
    log.info("z1: downloading %s", config.Z1_ZIP_URL)
    rec = download_raw("z1", config.Z1_ZIP_URL, "FRB_Z1_csv.zip", timeout=600,
                       vintage_fn=lambda r: _zip_vintage(r.path))
    tmp = dest.with_suffix(".part")
    shutil.copyfile(rec.path, tmp)      # the data/z1 cache is a mutable copy of the immutable raw file
    tmp.replace(dest)
    return dest


def _zip_vintage(path: Path) -> dt.date | None:
    try:
        with zipfile.ZipFile(path) as zf:
            member = next(i for i in zf.infolist() if i.filename.lower().endswith("z1.csv"))
            return dt.date(*member.date_time[:3])
    except Exception:
        return None


def _parse_lines(lines, wanted: set[bytes]) -> list[tuple[str, str, float]]:
    rows = []
    for line in lines:
        if not line.startswith(PREFIX):
            continue
        end = line.find(b",", 6)
        name = line[6:end]                      # e.g. b"FL153165105.Q"
        if not name.endswith(b".Q"):
            continue
        sid = name[:-2]
        if sid not in wanted:
            continue
        # date and value are the last two (unquoted) fields
        rest, date, value = line.rstrip(b"\r\n").rsplit(b",", 2)
        value = value.strip().strip(b'"')
        if not value or value in (b"ND", b"NA", b"."):
            continue
        rows.append((sid.decode(), date.decode(), float(value)))
    return rows


def _check_header(header: bytes) -> None:
    cols = next(csv.reader([header.decode("utf-8-sig")]))
    if cols[0] != "series_name" or cols[-2:] != ["date", "value"]:
        raise ValueError(f"Unexpected Z1.csv header: {cols}")


def extract(zip_path: Path | None = None, csv_path: Path | None = None, force_download: bool = False) -> pd.DataFrame:
    """Return long frame of catalog Z.1 series. `csv_path` (or env HHDEBT_Z1_CSV) reads an
    already-unzipped Z1.csv (dev cache); otherwise the zip is downloaded into data/z1/."""
    wanted = {s.encode() for s in config.series_ids("z1")}
    csv_path = csv_path or (Path(os.environ["HHDEBT_Z1_CSV"]) if os.environ.get("HHDEBT_Z1_CSV") else None)
    if csv_path:
        log.info("z1: reading local cache %s", csv_path)
        vintage = dt.date.fromtimestamp(csv_path.stat().st_mtime)
        record_local("z1", csv_path, vintage=vintage)
        with open(csv_path, "rb") as f:
            _check_header(f.readline())
            rows = _parse_lines(f, wanted)
    else:
        if zip_path:
            record_local("z1", zip_path, vintage=_zip_vintage(zip_path))
        else:
            zip_path = download_zip(force=force_download)
        with zipfile.ZipFile(zip_path) as zf:
            member = next(i for i in zf.infolist() if i.filename.lower().endswith("z1.csv"))
            vintage = dt.date(*member.date_time[:3])
            log.info("z1: streaming %s from %s (vintage %s)", member.filename, zip_path, vintage)
            with zf.open(member) as raw:
                f = io.BufferedReader(raw, buffer_size=1 << 22)
                _check_header(f.readline())
                rows = _parse_lines(f, wanted)
    df = pd.DataFrame(rows, columns=["series_id", "date", "value"])
    df["source"] = "z1"
    df["vintage"] = vintage
    missing = {w.decode() for w in wanted} - set(df.series_id)
    if missing:
        raise ValueError(f"z1: catalog series not found in Z1.csv: {sorted(missing)}")
    return df


def run(**kw) -> Path:
    return write_staging("z1", extract(**kw))
