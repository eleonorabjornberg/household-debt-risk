#!/usr/bin/env python3
"""Outstanding single-family credit-enhancement coverage at each year end, from Freddie Mac's 10-K filings.

    uv run --project pipeline python research/a2_net_exposure/freddie_10k.py

Downloads each FY2013-FY2025 10-K PDF from Freddie Mac's investor site into data/a2/freddie/ (if absent; raw files stay
out of git), converts it with `pdftotext -layout` (poppler-utils), parses the coverage table with tenk.py, and writes
freddie_ce_outstanding.csv (committed): one row per year end, maximum coverage in $M by category, the filing it came
from and that file's SHA-256.

Each year end appears in two filings (the 10-K for that year and the next one). The value used is the one from that
year's own 10-K (first publication); the next filing's figure is kept in `restated_*` columns. The table totals must
agree between the two filings to $1M or the script stops; a shift between categories (Freddie reclassified some
coverage between "STACR/ACIS" and "Other" in later filings) is kept and reported, not smoothed.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import tenk  # noqa: E402

BASE = "https://www.freddiemac.com/investors/financials/pdf/"
DATA = ROOT / "data" / "a2" / "freddie"
OUT = HERE / "freddie_ce_outstanding.csv"


def fetch(name: str) -> Path:
    p = DATA / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(BASE + name, headers={"User-Agent": "household-debt-risk research"})
        with urllib.request.urlopen(req, timeout=300) as r:
            p.write_bytes(r.read())
    return p


def text_of(pdf: Path) -> str:
    txt = pdf.with_suffix(".txt")
    if not txt.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True, capture_output=True)
    return txt.read_text(errors="replace")


def build(parsed: dict[int, tuple[str, str, dict]]) -> pd.DataFrame:
    """parsed: {fy: (pdf name, sha256, {year_end: values})} -> one row per year end."""
    rows = []
    for fy, (name, sha, res) in sorted(parsed.items()):
        v = res[fy]
        row = {"year_end": fy, "crt_maxcov_musd": v["crt"], "pmi_maxcov_musd": v["pmi"],
               "other_maxcov_musd": v["other"], "total_maxcov_musd": v["total"],
               "sf_portfolio_upb_musd": v["portfolio_upb"], "source_pdf": name, "source_sha256": sha}
        nxt = parsed.get(fy + 1)
        if nxt:
            r2 = nxt[2][fy]
            assert abs(r2["total"] - v["total"]) <= 1, f"{fy}: total coverage differs between FY{fy} and FY{fy + 1} 10-Ks"
            row.update({"restated_crt_maxcov_musd": r2["crt"], "restated_other_maxcov_musd": r2["other"],
                        "restated_in": nxt[0]})
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    parsed = {}
    for fy, (name, layout) in tenk.FILINGS.items():
        pdf = fetch(name)
        sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        parsed[fy] = (name, sha, tenk.parse(text_of(pdf), fy, layout))
    df = build(parsed)
    df.to_csv(OUT, index=False)
    print(df[["year_end", "crt_maxcov_musd", "pmi_maxcov_musd", "other_maxcov_musd", "total_maxcov_musd"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
