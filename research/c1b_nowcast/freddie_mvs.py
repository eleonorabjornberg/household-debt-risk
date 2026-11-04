#!/usr/bin/env python3
"""C1b input: Freddie Mac Monthly Volume Summaries (MVS), Table 1 "Total mortgage portfolio", with publication dates.

    uv run --project pipeline python research/c1b_nowcast/freddie_mvs.py

Fetches the listing page and every report from FIRST_MONTH on into data/c1b/mvs/ (git-ignored; manifest.jsonl
records URL, bytes, SHA-256 and retrieval time), then writes next to this file:
  freddie_mvs_reports.csv  one row per report: report month, PDF creation date, publication date used, rule, label
  freddie_mvs_rows.csv     every monthly row of Table 1 in every report (report month, row month, ending balance $M)

Publication date (Eleonora, card c1b-pubdate-2, option (a2)): the PDF creation date where it is plausible, i.e. after
month end and within 45 days of it; otherwise month end + FIXED_LAG days, where FIXED_LAG is the largest lag among the
plausible reports. Reports with an implausible creation date were re-issued later (e.g. a batch dated 2024-01-18):
their timing is the fixed lag, their content is labelled "content possibly revised".
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / "data" / "c1b" / "mvs"
LISTING = "https://www.freddiemac.com/investors/financials/monthly-volume-summaries"
PDF = "https://www.freddiemac.com/investors/financials/pdf/{mmyy}mvs.pdf"
FIRST_MONTH = "2016-01"      # C1's real-time sample starts at 2016-09 instants (T = 2016Q2)
PLAUSIBLE_DAYS = 45
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
ROW = re.compile(r"^(Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.?(?:\s+(\d{4}))?\s+(.*)$")
NUM = re.compile(r"\(?\$?[\d,]+(?:\.\d+)?%?\)?|-")


def get(url: str) -> bytes:
    import requests
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("unreachable")


def fetch(name: str, url: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if p.exists():
        return p
    body = get(url)
    p.write_bytes(body)
    with open(CACHE / "manifest.jsonl", "a") as f:
        f.write(json.dumps({"file": name, "url": url, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                            "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
    return p


def creation_date(pdf: Path) -> pd.Timestamp:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    line = next(l for l in info.splitlines() if l.startswith("CreationDate:"))
    return pd.Timestamp(datetime.strptime(line.split(":", 1)[1].strip(), "%a %b %d %H:%M:%S %Y %Z"))


def table1_rows(text: str, report_month: str) -> list[tuple[str, float]]:
    """(YYYY-MM, ending balance $M) for each monthly row of Table 1 (full-year and YTD rows skipped).

    Some layouts omit the year on the first row, so years are assigned backwards from the report month (the last
    row) and checked against every year the table does print."""
    m = re.search(r"TABLE 1\b.*?(?=TABLE 2\b)", text, re.S)
    if not m:
        raise ValueError("Table 1 not found")
    parsed = []
    for line in m.group(0).splitlines():
        r = ROW.match(line.strip())
        if not r:
            continue
        mon, yr, rest = r.groups()
        nums = NUM.findall(rest)
        if len(nums) < 5:
            raise ValueError(f"short row: {line!r}")
        parsed.append((MONTHS[mon[:3].lower()], int(yr) if yr else None, float(nums[4].strip("()$").replace(",", ""))))
    if not parsed:
        raise ValueError("no monthly rows in Table 1")
    y, mo = int(report_month[:4]), int(report_month[5:])
    if parsed[-1][0] != mo:
        raise ValueError(f"last Table 1 row is month {parsed[-1][0]}, report month {report_month}")
    out = []
    for i in range(len(parsed) - 1, -1, -1):
        pm, pyr, v = parsed[i]
        if i < len(parsed) - 1 and pm >= parsed[i + 1][0]:
            y -= 1
        if pyr is not None and pyr != y:
            raise ValueError(f"year mismatch in Table 1 of {report_month}: printed {pyr}, inferred {y}")
        out.append((f"{y}-{pm:02d}", v))
    return out[::-1]


def main() -> int:
    listing = fetch("listing.html", LISTING).read_text(errors="replace")
    codes = sorted(set(re.findall(r"(\d{4})mvs\.pdf", listing)))
    months = sorted(f"20{c[2:]}-{c[:2]}" for c in codes)
    months = [m for m in months if m >= FIRST_MONTH]
    reps, rows = [], []
    for ym in months:
        mmyy = ym[5:] + ym[2:4]
        pdf = fetch(f"{mmyy}mvs.pdf", PDF.format(mmyy=mmyy))
        text = subprocess.run(["pdftotext", "-raw", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
        tr = table1_rows(text, ym)
        rows += [{"report_month": ym, "row_month": rm, "ending_balance_usd_m": v} for rm, v in tr]
        reps.append({"report_month": ym, "file": pdf.name, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                     "pdf_created_utc": creation_date(pdf)})
    rep = pd.DataFrame(reps)
    month_end = pd.to_datetime(rep["report_month"]).dt.to_period("M").dt.end_time.dt.normalize()
    lag = (rep["pdf_created_utc"].dt.normalize() - month_end).dt.days
    rep["plausible"] = (lag > 0) & (lag <= PLAUSIBLE_DAYS)
    fixed = int(lag[rep["plausible"]].max())
    rep["pub_date"] = rep["pdf_created_utc"].dt.normalize().where(rep["plausible"], month_end + pd.Timedelta(days=fixed))
    rep["pub_rule"] = rep["plausible"].map({True: "pdf creation date", False: f"fixed lag {fixed} days"})
    rep["content_label"] = rep["plausible"].map({True: "", False: "content possibly revised"})
    rep["pdf_created_utc"] = rep["pdf_created_utc"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    rep["pub_date"] = rep["pub_date"].dt.strftime("%Y-%m-%d")
    rep.to_csv(HERE / "freddie_mvs_reports.csv", index=False)
    pd.DataFrame(rows).to_csv(HERE / "freddie_mvs_rows.csv", index=False, float_format="%.0f")
    print(f"{len(rep)} reports {months[0]}..{months[-1]}; plausible creation date {int(rep['plausible'].sum())}, "
          f"fixed lag {fixed} days for {int((~rep['plausible']).sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
