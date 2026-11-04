#!/usr/bin/env python3
"""Fetch Fannie Mae's 10-K filings (FY2013-FY2025) from SEC EDGAR into data/a2/fannie/ (cached; never re-fetched).

    SEC_USER_AGENT='<declared UA>' uv run --project pipeline python research/a2_net_exposure/fannie_10k.py

Eleonora's Q6 decision (2026-11-04): the SEC User-Agent is supplied in-shell for this command only and is never
written to any file; this script reads it from the environment and refuses to run without it. SEC fair access: one
request at a time with a pause (well under 10 requests per second); a 403 or the SEC rate-threshold page stops the
script, with no retry. Raw files stay out of git (data/ is ignored); fetch_log.json records URL, status, bytes,
SHA-256 and UTC time for each request, without the User-Agent.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "a2" / "fannie"
CIK = "0000310522"
HOSTS = ("https://www.sec.gov/",)
PAUSE = 2.0  # seconds between requests (a 503 on the first run at 0.5 s)


class Stop(Exception):
    pass


def get(url: str, ua: str, log: list) -> bytes:
    assert url.startswith(HOSTS), "the declared User-Agent is only ever sent to www.sec.gov"
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    time.sleep(PAUSE)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        log.append({"url": url, "status": e.code, "utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds")})
        raise Stop(f"HTTP {e.code} from {url}")
    if b"Request Rate Threshold Exceeded" in body[:5000] or b"Your Request Originates from an Undeclared" in body[:5000]:
        log.append({"url": url, "status": status, "note": "SEC rate-threshold page"})
        raise Stop(f"SEC rate-threshold page at {url}")
    log.append({"url": url, "status": status, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds")})
    return body


def main() -> int:
    ua = os.environ.get("SEC_USER_AGENT", "")
    if not ua:
        print("SEC_USER_AGENT is not set; nothing fetched (Q6).", file=sys.stderr)
        return 2
    DATA.mkdir(parents=True, exist_ok=True)
    logp = DATA / "fetch_log.json"
    log = json.loads(logp.read_text()) if logp.exists() else []
    try:
        atom = DATA / "fnma_10k_list.atom"
        if not atom.exists():
            atom.write_bytes(get(f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK}&type=10-K"
                                 f"&dateb=&owner=include&count=40&output=atom", ua, log))
        t = atom.read_text(errors="replace")
        entries = re.findall(r"<entry>(.*?)</entry>", t, re.S)
        for e in entries:
            date = re.search(r"<filing-date>(\d{4})-", e).group(1)
            typ = re.search(r"<filing-type>(.*?)<", e).group(1)
            if typ != "10-K" or not 2014 <= int(date) <= 2026:
                continue
            fy = int(date) - 1
            out = DATA / f"fnma_10k_fy{fy}.htm"
            if out.exists():
                continue
            idx_url = re.search(r"<filing-href>(.*?)<", e).group(1)
            idx_p = DATA / f"fnma_10k_fy{fy}_index.htm"
            if not idx_p.exists():
                idx_p.write_bytes(get(idx_url, ua, log))
            idx = idx_p.read_text(errors="replace")
            # main document: first row of the document table whose type is 10-K
            m = None
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", idx, re.S):
                cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
                if len(cells) >= 4 and re.sub(r"<[^>]+>|\s", "", cells[3]) == "10-K":
                    m = re.search(r'href="([^"]+\.htm)"', cells[2])
                    break
            if not m:
                log.append({"url": idx_url, "note": f"FY{fy}: main 10-K document not identified in index"})
                continue
            url = "https://www.sec.gov" + m.group(1).replace("/ix?doc=", "")
            log.append({"note": f"FY{fy}: main document {url}"})
            out.write_bytes(get(url, ua, log))
    except Stop as s:
        print(f"Stopped: {s}", file=sys.stderr)
        logp.write_text(json.dumps(log, indent=1) + "\n")
        return 3
    logp.write_text(json.dumps(log, indent=1) + "\n")
    print(f"{len([x for x in log if x.get('status') == 200])} successful requests logged; files: "
          f"{sorted(p.name for p in DATA.glob('fnma_10k_fy*.htm'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
