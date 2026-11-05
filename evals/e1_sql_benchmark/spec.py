"""E1 question specs: evaluate one `check` against a set of tables (no model, no network).

The same evaluator runs on two independently built table sets:
  * path 1, the snapshot the MCP server serves (`load_snapshot()`, web/public/data/*.json);
  * path 2, tables rebuilt from the raw Fed Z.1 zip and the raw NY Fed workbook by validation/e1_gold.py,
    which does not use the pipeline or the export.
The evaluator itself is shared (argmax, differences, sums); the data are not.

A check is a dict:
  table   public_share | debt_by_risk_holder | collateral_coverage | crisis_event_window | nyfed_by_type
          | dim_risk_bucket | catalog (series catalog rows; count only)
  where   {column: value} filter; `where_range: {column: [lo, hi]}` for numeric ranges
  field   column to read; rows matching `where` on the same date are summed (so a bucket's mortgage and
          consumer-credit rows add up)
  op      at (date) | diff (from, to: value(to) - value(from)) | pct_change (from, to, in %) |
          mean (start, end) | argmax / argmin (optional start, end; returns the quarter too) |
          max / min (over matching rows, no date grouping) | count (matching rows) | count_dates
  scale   multiplier applied to the result (default 1)
or a combination:
  combine {op: add | sub | mul | div, args: [check, check], scale}
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / "web" / "public" / "data"
TABLES = ["public_share", "debt_by_risk_holder", "collateral_coverage", "crisis_event_window", "nyfed_by_type",
          "dim_risk_bucket"]


def quarter(date: str) -> str:
    y, m = int(date[:4]), int(date[5:7])
    return f"{y}Q{(m - 1) // 3 + 1}"


CATALOG = ROOT / "pipeline" / "series_catalog.yaml"


def load_snapshot(snap: Path = SNAP, catalog: Path = CATALOG) -> dict[str, list[dict]]:
    """Path 1: the snapshot tables the MCP server serves, plus the series catalog (what list_series serves)."""
    import yaml
    tables = {t: json.loads((snap / f"{t}.json").read_text()) for t in TABLES}
    tables["catalog"] = yaml.safe_load(catalog.read_text())["series"]
    return tables


def _rows(check: dict, tables: dict) -> list[dict]:
    rows = tables[check["table"]]
    for k, v in (check.get("where") or {}).items():
        rows = [r for r in rows if r.get(k) == v]
    for k, (lo, hi) in (check.get("where_range") or {}).items():
        rows = [r for r in rows if r.get(k) is not None and lo <= r[k] <= hi]
    return rows


def _series(check: dict, tables: dict) -> dict[str, float]:
    """date -> sum of field over matching rows (None if any matching row has no value)."""
    out: dict[str, float | None] = {}
    for r in _rows(check, tables):
        v = r.get(check["field"])
        d = r["date"]
        if v is None or (isinstance(v, float) and v != v):
            out[d] = None
        elif out.get(d, 0.0) is not None:
            out[d] = out.get(d, 0.0) + v
    return {d: v for d, v in sorted(out.items()) if v is not None}


def _at(s: dict, date: str) -> float:
    if date not in s:
        raise KeyError(f"no value at {date}")
    return s[date]


def _window(s: dict, check: dict) -> dict:
    lo, hi = check.get("start", "0000"), check.get("end", "9999")
    w = {d: v for d, v in s.items() if lo <= d <= hi}
    if not w:
        raise KeyError("empty window")
    return w


def evaluate(check: dict, tables: dict) -> tuple[float, str | None]:
    """Return (value, quarter or None)."""
    if "combine" in check:
        c = check["combine"]
        (a, qa), (b, qb) = (evaluate(x, tables) for x in c["args"])
        v = {"add": a + b, "sub": a - b, "mul": a * b, "div": a / b}[c["op"]]
        return v * c.get("scale", 1.0), qa or qb
    op, scale = check.get("op", "at"), check.get("scale", 1.0)
    if op in ("max", "min", "count"):
        rows = _rows(check, tables)
        if op == "count":
            return float(len(rows)) * scale, None
        vals = [r[check["field"]] for r in rows if r.get(check["field"]) is not None]
        return (max(vals) if op == "max" else min(vals)) * scale, None
    s = _series(check, tables)
    if op == "at":
        return _at(s, check["date"]) * scale, None
    if op == "count_dates":
        return float(len(_window(s, check))) * scale, None
    if op == "diff":
        return (_at(s, check["to"]) - _at(s, check["from"])) * scale, None
    if op == "pct_change":
        return (_at(s, check["to"]) / _at(s, check["from"]) - 1) * 100 * scale, None
    if op == "mean":
        w = _window(s, check)
        return sum(w.values()) / len(w) * scale, None
    if op in ("argmax", "argmin"):
        w = _window(s, check)
        d = (max if op == "argmax" else min)(w, key=w.get)
        return w[d] * scale, quarter(d)
    raise ValueError(f"unknown op {op}")
