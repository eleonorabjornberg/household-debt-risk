#!/usr/bin/env python3
"""Step 1: is there a Z.1 release newer than the one in the repo?  Read-only; one HEAD request.

    uv run --project pipeline python .claude/skills/z1-release-update/scripts/detect_release.py

Compares the live zip's Content-Length and Last-Modified with the latest z1 line of data/manifest.jsonl and
with web/public/data/meta.json (vintages.z1). Prints a verdict and the path of the previous zip.
Exit code: 0 nothing new, 10 new release (or possibly new), 2 could not decide.
"""
import json
import sys
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
URL = "https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip"


def latest_manifest_z1(path: Path):
    last = None
    for line in path.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("source") == "z1":
                last = r
    return last


def verdict(live_bytes, live_modified, rec, meta_vintage):
    """Pure decision so it can be tested: returns (code, text)."""
    if rec is None:
        return 2, "No z1 line in data/manifest.jsonl; cannot compare."
    have = datetime.fromisoformat(rec["vintage"]).date() if rec.get("vintage") else None
    facts = (f"live: {live_bytes} bytes, Last-Modified {live_modified:%Y-%m-%d %H:%M} GMT; "
             f"repo: {rec['bytes']} bytes, Z1.csv dated {rec.get('vintage')}, meta.json vintages.z1 {meta_vintage}")
    if live_bytes != rec["bytes"]:
        return 10, "NEW RELEASE (size differs). " + facts
    if have and live_modified.date() > have:
        return 10, "POSSIBLY NEW (same size, later Last-Modified); confirm with the Z1.csv member date after extract. " + facts
    return 0, "Nothing new. " + facts


def main() -> int:
    rec = latest_manifest_z1(ROOT / "data" / "manifest.jsonl")
    meta = json.loads((ROOT / "web" / "public" / "data" / "meta.json").read_text())
    req = urllib.request.Request(URL, method="HEAD", headers={"User-Agent": "Mozilla/5.0 hhdebt"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            n, lm = int(r.headers["Content-Length"]), parsedate_to_datetime(r.headers["Last-Modified"])
    except Exception as e:
        print(f"HEAD failed: {e}")
        return 2
    code, text = verdict(n, lm, rec, meta.get("vintages", {}).get("z1"))
    print(text)
    if rec:
        print(f"previous zip (keep as comparison vintage): {rec['path']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
