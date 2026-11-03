"""Extractors. Each writes data/staging/<source>.csv with columns
source, series_id, date, value, vintage (the raw.observations shape, minus loaded_at).

Provenance: every HTTP download (Z.1 zip, each FRED request, the NY Fed page and workbook) is saved
immutably under data/raw/<source>/<sha256[:16]>_<filename> (content-addressed; an existing file is
never overwritten, identical bytes reuse it) and appends one JSON line to data/manifest.jsonl:
source, url (api_key redacted), retrieved_at (UTC), bytes, sha256, path (relative to the repo root),
http_status, vintage, source_path. Local-file shortcuts (--z1-zip, --z1-csv, --nyfed-xlsx) and the
reused data/z1 cache are recorded with url null and source_path set. All of it goes through
`download_raw` / `record_local` below. Failed or rejected downloads leave no raw file or line.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import os
import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

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


# ---------------------------------------------------------------------------------------------
# Raw-download provenance
# ---------------------------------------------------------------------------------------------
COPY_MAX_BYTES = 256 << 20   # local files above this (e.g. the unzipped 3 GB Z1.csv) are hashed, not copied
_API_KEY_RE = re.compile(r"(?i)([?&]api_key=)[^&#\s]*")


def redact_url(url: str) -> str:
    return _API_KEY_RE.sub(r"\1REDACTED", url)


def manifest_path() -> Path:
    return config.DATA_DIR / "manifest.jsonl"


def _rel(p: Path) -> str:
    p = Path(p)
    try:
        return p.resolve().relative_to(config.REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(p)


@dataclass
class RawRecord:
    path: Path          # where the immutable raw bytes live (or the source file if too large to copy)
    sha256: str
    bytes: int
    status: int | None
    headers: dict


def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name) or "download"


def _finalize(source: str, tmp: Path, sha: str, filename: str) -> Path:
    """Move tmp into the content-addressed store without ever overwriting an existing file."""
    dest = tmp.parent / f"{sha[:16]}_{_safe_name(filename)}"
    if dest.exists():
        tmp.unlink()
        log.info("%s: identical bytes already stored at %s", source, dest)
        return dest
    try:
        os.link(tmp, dest)          # fails if dest appeared meanwhile; never clobbers
    except FileExistsError:
        pass
    except OSError:                 # filesystem without hard links
        if not dest.exists():
            shutil.copyfile(tmp, dest)
    tmp.unlink()
    try:
        dest.chmod(0o444)
    except OSError:
        pass
    return dest


def append_manifest(*, source: str, url: str | None, path: Path, sha256: str, nbytes: int,
                    http_status: int | None, vintage, source_path: Path | None = None) -> dict:
    entry = {
        "source": source,
        "url": redact_url(url) if url else None,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "bytes": nbytes,
        "sha256": sha256,
        "path": _rel(path),
        "http_status": http_status,
        "vintage": vintage.isoformat() if hasattr(vintage, "isoformat") else vintage,
        "source_path": _rel(source_path) if source_path else None,
    }
    mp = manifest_path()
    mp.parent.mkdir(parents=True, exist_ok=True)
    with open(mp, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def download_raw(source: str, url: str, filename: str, *, params: dict | None = None, vintage=None,
                 vintage_fn: Callable[[RawRecord], object] | None = None,
                 validate: Callable[[RawRecord, bytes], bool] | None = None, **kw) -> RawRecord:
    """GET `url`, streaming the body to data/raw/<source>/ while hashing it (constant memory), then
    store it content-addressed and append a manifest line. `vintage_fn(record)` may derive the vintage
    from the stored file/headers; `validate(record, first_bytes)` may reject the response (nothing is
    kept). Nothing is recorded if the request fails. Errors never contain the api_key."""
    import requests

    full_url = requests.Request("GET", url, params=params).prepare().url
    raw_dir = config.DATA_DIR / "raw" / source
    raw_dir.mkdir(parents=True, exist_ok=True)
    tmp = raw_dir / f".{uuid.uuid4().hex}.part"
    h, n, head = hashlib.sha256(), 0, b""
    try:
        with http_get(url, params=params, stream=True, **kw) as r:
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    if not head:
                        head = chunk[:64]
                    h.update(chunk)
                    f.write(chunk)
                    n += len(chunk)
            rec = RawRecord(tmp, h.hexdigest(), n, r.status_code, dict(r.headers))
    except requests.RequestException as e:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(redact_url(f"{type(e).__name__}: {e}")) from None
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    if validate is not None and not validate(rec, head):
        tmp.unlink(missing_ok=True)
        raise ValueError(f"{source}: response from {redact_url(full_url)} rejected")
    rec.path = _finalize(source, tmp, rec.sha256, filename)
    if vintage_fn is not None:
        vintage = vintage_fn(rec)
    append_manifest(source=source, url=full_url, path=rec.path, sha256=rec.sha256, nbytes=n,
                    http_status=rec.status, vintage=vintage)
    return rec


def sha256_file(path: Path) -> tuple[str, int]:
    h, n = hashlib.sha256(), 0
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def record_local(source: str, path: Path, *, vintage=None, skip_if_recorded: bool = False) -> RawRecord:
    """Register an existing local file (dev shortcut or reused cache): hash it, copy it into the raw
    store (unless larger than COPY_MAX_BYTES, then it is referenced in place) and append a manifest
    line with url null and source_path set. `skip_if_recorded` adds no line if this exact content
    is already in the manifest (used for the Z.1 cache so reruns do not repeat lines)."""
    path = Path(path)
    sha, n = sha256_file(path)
    if n <= COPY_MAX_BYTES:
        raw_dir = config.DATA_DIR / "raw" / source
        raw_dir.mkdir(parents=True, exist_ok=True)
        stored = raw_dir / f"{sha[:16]}_{_safe_name(path.name)}"
        if not stored.exists():
            tmp = raw_dir / f".{uuid.uuid4().hex}.part"
            shutil.copyfile(path, tmp)
            stored = _finalize(source, tmp, sha, path.name)
    else:
        stored = path
    if skip_if_recorded and manifest_path().exists():
        with open(manifest_path(), encoding="utf-8") as f:
            if any(f'"sha256": "{sha}"' in line for line in f):
                return RawRecord(stored, sha, n, None, {})
    append_manifest(source=source, url=None, path=stored, sha256=sha, nbytes=n, http_status=None,
                    vintage=vintage, source_path=path)
    return RawRecord(stored, sha, n, None, {})
