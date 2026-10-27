"""NY Fed Household Debt & Credit (HHDC) report workbook, 2003Q1+.

The hhdc page renders its download links client-side, so we (1) look for xlsx links in the page
HTML and (2) probe the stable media path HHD_C_Report_<YYYY>Q<n>.xlsx from the current quarter back.
Parsed tables (located through the workbook's table of contents, not fixed sheet numbers):
  * "Total Debt Balance and its Composition"       -> NYFED_HHDC.balance.<loan_type>       (USD billions)
  * "Flow into Serious Delinquency (90+) by Loan Type" -> NYFED_HHDC.transition90.<loan_type> (% of balance,
    annualized: four-quarter moving sum, as published)
Vintage = HTTP Last-Modified of the workbook when sent, else the download date.
"""
from __future__ import annotations

import datetime as dt
import io
import logging
import re
from email.utils import parsedate_to_datetime
from pathlib import Path

import openpyxl
import pandas as pd

from .. import config
from . import http_get, write_staging

log = logging.getLogger(__name__)

LOAN_TYPES = {
    "mortgage": "mortgage", "he revolving": "heloc", "heloc": "heloc",
    "auto loan": "auto", "auto": "auto", "credit card": "credit_card", "cc": "credit_card",
    "student loan": "student", "student loans": "student", "other": "other",
}
TABLES = {
    # metric: (TOC title regex, sheet title regex fallback, multiplier to target unit)
    "balance": (r"total debt balance and its composition", r"total debt balance and its composition", 1000.0),
    "transition90": (r"(flow|transition) into serious delinquency \(90\+\) by loan type",
                     r"new seriously delinquent.*balances by loan type", 1.0),
}
NYFED_SERIES = [f"NYFED_HHDC.{m}.{t}" for m in TABLES for t in sorted(set(LOAN_TYPES.values()))]


def _quarter_candidates(today: dt.date, n: int = 6) -> list[str]:
    y, q = today.year, (today.month - 1) // 3 + 1
    out = []
    for _ in range(n):
        out.append(f"{y}Q{q}")
        y, q = (y, q - 1) if q > 1 else (y - 1, 4)
    return out


def find_latest_xlsx(today: dt.date | None = None) -> tuple[str, bytes, dt.date]:
    today = today or dt.date.today()
    urls: list[str] = []
    try:
        html = http_get(config.NYFED_PAGE_URL).text
        urls += sorted(set(re.findall(r'href="([^"]*HHD_C_Report_\d{4}Q\d\.xlsx)"', html)), reverse=True)
    except Exception as e:  # page is optional; the probe below is the main path
        log.warning("nyfed: could not read hhdc page (%s)", e)
    urls += [config.NYFED_XLSX_URL.format(yq=yq) for yq in _quarter_candidates(today)]
    for url in urls:
        if url.startswith("/"):
            url = "https://www.newyorkfed.org" + url
        try:
            r = http_get(url, allow_redirects=False)
        except Exception:
            continue
        if r.status_code == 200 and r.content[:2] == b"PK":
            lm = r.headers.get("Last-Modified")
            vintage = parsedate_to_datetime(lm).date() if lm else today
            log.info("nyfed: using %s (vintage %s)", url, vintage)
            return url, r.content, vintage
    raise RuntimeError("nyfed: no HHD_C_Report xlsx found for the last 6 quarters")


def _quarter_end(label) -> pd.Timestamp | None:
    if isinstance(label, dt.datetime):
        return pd.Timestamp(label) + pd.offsets.QuarterEnd(0)
    m = re.fullmatch(r"\s*(\d{2}|\d{4})\s*:?\s*Q([1-4])\s*", str(label or ""))
    if not m:
        return None
    y = int(m.group(1))
    y = y if y > 999 else (2000 + y if y < 50 else 1900 + y)
    return pd.Period(f"{y}Q{m.group(2)}", "Q").end_time.normalize()


def _find_sheet(wb, toc_re: str, title_re: str):
    toc = next((ws for ws in wb.worksheets if "content" in ws.title.lower()), None)
    if toc is not None:
        for row in toc.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None]
            if any(re.search(toc_re, c.lower()) for c in cells):
                page = next((c for c in cells if re.fullmatch(r"Page \d+", c.strip())), None)
                if page and f"{page.strip()} Data" in wb.sheetnames:
                    return wb[f"{page.strip()} Data"]
    for ws in wb.worksheets:  # fallback: match the title cell
        first = next(ws.iter_rows(values_only=True, max_row=1), ())
        if first and first[0] and re.search(title_re, str(first[0]).lower()):
            return ws
    raise LookupError(f"nyfed: sheet not found for /{toc_re}/")


def _parse_table(ws, mult: float) -> pd.DataFrame:
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows)
                 if sum(1 for c in r[1:] if isinstance(c, str) and c.strip().lower() in LOAN_TYPES) >= 4)
    cols = {j: LOAN_TYPES[c.strip().lower()] for j, c in enumerate(rows[hdr_i])
            if j > 0 and isinstance(c, str) and c.strip().lower() in LOAN_TYPES}
    out = []
    for r in rows[hdr_i + 1:]:
        d = _quarter_end(r[0]) if r else None
        if d is None:
            continue
        for j, lt in cols.items():
            v = r[j] if j < len(r) else None
            if isinstance(v, (int, float)):
                out.append((lt, d, float(v) * mult))
    return pd.DataFrame(out, columns=["loan_type", "date", "value"])


def parse_workbook(content: bytes) -> pd.DataFrame:
    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    frames = []
    for metric, (toc_re, title_re, mult) in TABLES.items():
        t = _parse_table(_find_sheet(wb, toc_re, title_re), mult)
        t["series_id"] = f"NYFED_HHDC.{metric}." + t.loan_type
        frames.append(t)
    return pd.concat(frames, ignore_index=True)


def extract(xlsx_path: Path | None = None) -> pd.DataFrame:
    if xlsx_path:
        content, vintage = xlsx_path.read_bytes(), dt.date.fromtimestamp(xlsx_path.stat().st_mtime)
    else:
        url, content, vintage = find_latest_xlsx()
        dest = config.DATA_DIR / "nyfed" / url.rsplit("/", 1)[-1]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    df = parse_workbook(content)
    df["source"], df["vintage"] = "nyfed", vintage
    return df


def run(**kw) -> None:
    write_staging("nyfed", extract(**kw))
