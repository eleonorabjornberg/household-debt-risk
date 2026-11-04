"""Annual Z.1 levels (series suffix .A) in the same shape zparse gives for quarterly ones: {series_id: {Timestamp: $M}}."""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import pandas as pd


def load_annual(zip_path: Path, ids) -> pd.DataFrame:
    want = {f"Z1/Z1/{i}.A": i for i in ids}
    out: dict[str, dict] = {i: {} for i in ids}
    with zipfile.ZipFile(zip_path) as z, z.open("Z1.csv") as fh:
        r = csv.reader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"))
        hdr = next(r)
        si, di, vi, mi = hdr.index("series_name"), hdr.index("date"), hdr.index("value"), hdr.index("unit_mult")
        for row in r:
            sid = want.get(row[si])
            if sid is None or row[vi] in ("", "ND"):
                continue
            mult = {"Millions": 1.0, "Billions": 1e3, "Thousands": 1e-3, "Units": 1e-6, "": 1.0}[row[mi]]  # to $ millions
            out[sid][pd.Timestamp(f"{row[di][:4]}-12-31")] = float(row[vi]) * mult
    df = pd.DataFrame(out).sort_index()
    return df
