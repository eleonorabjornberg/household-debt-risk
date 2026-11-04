#!/usr/bin/env python3
"""B2: fetch the EDGAR material listed in tracks/markets.md (Q-B2.2 (c); SEC access for markets decided by
Eleonora 2026-11-04).

    SEC_USER_AGENT='<declared value>' uv run --project pipeline python research/b2_crt_pricing/edgar.py discover

The User-Agent is read from the SEC_USER_AGENT environment variable only. It is never written to any file, log or
output, and requests go only to www.sec.gov and efts.sec.gov. SEC fair access: at most one request every 2 s
here (the limit is 10/s); the script stops at the first 403, 429 or rate-threshold page. Each fetch is logged to
data/edgar/manifest.jsonl (URL, status, bytes, SHA-256, UTC), without the User-Agent. Raw responses go to
data/edgar/ (outside git).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "edgar"
ALLOWED = {"www.sec.gov", "efts.sec.gov"}
SPACING_S = 2.0
_last = [0.0]

CIK = {"freddie": "0001026214", "fannie": "0000310522"}   # to confirm from the filing lists themselves


class Stop(Exception):
    pass


def fetch(url: str, tag: str) -> bytes:
    host = urllib.parse.urlparse(url).hostname
    if host not in ALLOWED:
        raise Stop(f"host {host} not allowed")
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise Stop("SEC_USER_AGENT not set (pass it as a per-command prefix)")
    OUT.mkdir(parents=True, exist_ok=True)
    wait = SPACING_S - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    status, body = None, b""
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read() if hasattr(e, "read") else b""
    _last[0] = time.time()
    rec = {"tag": tag, "url": url, "status": status, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
           "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with open(OUT / "manifest.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    text = body[:4000].decode("utf-8", "ignore").lower()
    if status in (403, 429) or "request rate threshold exceeded" in text or "undeclared automated tool" in text:
        raise Stop(f"stopped: {status} at {url} (no retry, no workaround)")
    (OUT / f"{tag}").write_bytes(body)
    return body


def discover() -> dict:
    """Small first pass (4 requests): full-text search for deal documents, and the two GSEs' 10-K filing lists."""
    res = {}
    for name, phrase in [("stacr", '"Structured Agency Credit Risk"'), ("cas", '"Connecticut Avenue Securities"')]:
        q = urllib.parse.urlencode({"q": phrase, "dateRange": "custom", "startdt": "2017-01-01", "enddt": "2023-12-31",
                                    "forms": "8-K,FWP,424B2,424B5"})
        body = fetch(f"https://efts.sec.gov/LATEST/search-index?{q}", f"fts_{name}.json")
        d = json.loads(body)
        hits = d.get("hits", {})
        res[f"fts_{name}"] = {"total": hits.get("total", {}).get("value"),
                              "forms": sorted({h["_source"].get("form") for h in hits.get("hits", []) if "_source" in h}),
                              "filers": sorted({n for h in hits.get("hits", []) for n in h.get("_source", {}).get("display_names", [])})[:10]}
    for gse, cik in CIK.items():
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=40&output=atom"
        body = fetch(url, f"list10k_{gse}.atom")
        t = body.decode("utf-8", "ignore")
        import re
        res[f"10k_{gse}"] = {"company": (re.findall(r"<conformed-name>([^<]+)", t) or [None])[0],
                             "n_10k": t.count("<category label=\"form type\" term=\"10-K\""),
                             "filing_dates": re.findall(r"<filing-date>([^<]+)", t)[:12]}
    return res


def main(argv) -> int:
    if argv[1:] == ["discover"]:
        try:
            r = discover()
        except Stop as e:
            print(e)
            return 3
        (OUT / "discover_summary.json").write_text(json.dumps(r, indent=1) + "\n")
        print(json.dumps(r, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
