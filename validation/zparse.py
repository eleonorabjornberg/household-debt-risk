"""Independent streaming parser for the Fed Z.1 long CSV (no hhdebt imports)."""
from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from collections import defaultdict
from datetime import date, datetime

PREFIX = b"Z1/Z1/"


def sha256_file(path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def parse_line(line: bytes):
    """Return (series_name, date_str, value_str) from one Z1.csv line, or None.

    Series name is the first field (no commas inside); the last two fields are date,value.
    Descriptions in between may contain commas inside quotes, so we split from both ends.
    """
    line = line.rstrip(b"\r\n")
    i = line.find(b",")
    if i < 0:
        return None
    parts = line.rsplit(b",", 2)
    if len(parts) != 3:
        return None
    return line[:i].decode(), parts[1].decode(), parts[2].decode()


def parse_value(s: str):
    s = s.strip()
    if not s or s in ("ND", "NA", "NaN"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def zip_member_info(zip_path, member="Z1.csv"):
    with zipfile.ZipFile(zip_path) as z:
        info = z.getinfo(member)
        return datetime(*info.date_time), info.file_size


def stream_series(lines, ids):
    """Collect quarterly series. `lines` is any iterable of bytes lines; `ids` bare IDs (no Z1/Z1/ or .Q).

    Returns {id: {date(YYYY-MM-DD): float}}. Only names ending in '.Q' are kept.
    """
    want = {PREFIX + i.encode() + b".Q" for i in ids}
    out = defaultdict(dict)
    for line in lines:
        if not line.startswith(PREFIX):
            continue
        j = line.find(b",")
        if line[:j] not in want:
            continue
        rec = parse_line(line)
        if rec is None:
            continue
        name, d, v = rec
        val = parse_value(v)
        if val is None:
            continue
        out[name[6:-2]][d] = val
    return dict(out)


def load_z1_zip(zip_path, ids, member="Z1.csv"):
    with zipfile.ZipFile(zip_path) as z, z.open(member) as f:
        return stream_series(f, ids)


def load_table_zip(zip_path, ids):
    """Fallback for the Fed's per-table `z1_csv_files.zip` (wide tables, dates like 2026:Q1).

    Returns ({id: {date: value}}, conflicts) - conflicts lists ids whose duplicated columns disagree.
    """
    want = set(ids)
    out, conflicts = defaultdict(dict), set()
    with zipfile.ZipFile(zip_path) as z:
        for n in z.namelist():
            if not n.endswith(".csv"):
                continue
            with z.open(n) as f:
                r = csv.reader(io.TextIOWrapper(f, "utf-8"))
                h = next(r, None)
                if not h or h[0] != "date":
                    continue
                for row in r:
                    m = re.fullmatch(r"(\d{4}):Q([1-4])", row[0])
                    if not m:
                        continue
                    y, q = int(m[1]), int(m[2])
                    d = date(y, 3 * q, 30 if q in (2, 3) else 31).isoformat()
                    for c, v in zip(h[1:], row[1:]):
                        b = c[:-2] if c.endswith(".Q") else c
                        if b in want and (val := parse_value(v)) is not None:
                            if d in out[b] and abs(out[b][d] - val) > 0.5:
                                conflicts.add(b)
                            out[b].setdefault(d, val)
    return dict(out), sorted(conflicts)
