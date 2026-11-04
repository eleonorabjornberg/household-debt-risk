#!/usr/bin/env python3
"""Fannie Mae outstanding cover at each year end, from its 10-K filings (cached by fannie_10k.py in data/a2/fannie/).

    uv run --project pipeline python research/a2_net_exposure/fannie_extract.py

Unlike Freddie (tenk.py), Fannie does not print a table of outstanding CRT maximum coverage. Its 10-Ks state it in a
sentence, rounded to $1 billion: "The risk in force of these transactions, which refers to the maximum amount of losses
that could be absorbed by credit risk transfer investors, was approximately $X billion as of December 31, YYYY" (FY2017
and FY2020 on; not stated in FY2013-16, FY2018-19, which stay missing). Mortgage insurance: "our (total) mortgage
insurance risk in force was $X billion" (FY2017 on); "total mortgage insurance coverage risk in force of $X billion" (FY2013-16). Each value keeps the 10-K it came from, that file's SHA-256 and
the quoted sentence; where a later 10-K restates a year end, both must agree.
Output: fannie_ce_outstanding.csv (committed).
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "a2" / "fannie"
OUT = Path(__file__).resolve().parent / "fannie_ce_outstanding.csv"
CRT = re.compile(r"absorbed by (?:the )?credit risk transfer investors,? (?:was|were) (?:approximately )?\$([\d.]+) billion as of "
                 r"December 31, (\d{4})(?:\s?,?\s?compared (?:with|to) (?:approximately )?\$([\d.]+) billion as of December 31, (\d{4}))?")
MI = re.compile(r"(?:As of December 31, (\d{4}), )?[Oo]ur (?:total )?(?:primary )?mortgage insurance risk in force was \$([\d.]+) billion")
# FY2013-FY2016 wording: "We had total mortgage insurance coverage risk in force of $X billion and $Y billion on the
# single-family mortgage loans in our guaranty book of business as of December 31, FY and FY-1"
MI_OLD = re.compile(r"total mortgage insurance coverage risk in force of \$([\d.]+) billion and \$[\d.]+ billion on the single-family "
                    r"mortgage loans in our (?:single-family )?guaranty book of business as of December 31, (\d{4})")


def text(p: Path) -> str:
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", p.read_text(errors="replace"))
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def extract(t: str, fy: int) -> dict:
    out = {}
    m = CRT.search(t)
    if m:
        assert int(m.group(2)) == fy, f"FY{fy}: CRT sentence dated {m.group(2)}"
        out["crt_rif_bn"] = float(m.group(1))
        out["crt_quote"] = m.group(0)
        if m.group(3):
            out["crt_prior"] = (int(m.group(4)), float(m.group(3)))
    m = MI.search(t)
    if not m:
        mo = MI_OLD.search(t)
        if mo:
            assert int(mo.group(2)) == fy, f"FY{fy}: MI sentence dated {mo.group(2)}"
            out["mi_rif_bn"] = float(mo.group(1))
            out["mi_quote"] = mo.group(0)
    if m:
        assert m.group(1) in (None, str(fy)), f"FY{fy}: MI sentence dated {m.group(1)}"
        out["mi_rif_bn"] = float(m.group(2))
        out["mi_quote"] = m.group(0)
    return out


def main() -> int:
    rows, prior = [], {}
    for fy in range(2013, 2026):
        p = DATA / f"fnma_10k_fy{fy}.htm"
        if not p.exists():
            print(f"{p} missing; run fannie_10k.py", file=sys.stderr)
            return 2
        e = extract(text(p), fy)
        if "crt_prior" in e:
            prior[e["crt_prior"][0]] = e["crt_prior"][1]
        rows.append({"year_end": fy, "crt_rif_bn": e.get("crt_rif_bn"), "mi_rif_bn": e.get("mi_rif_bn"),
                     "source_10k": p.name, "source_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                     "crt_quote": e.get("crt_quote", ""), "mi_quote": e.get("mi_quote", "")})
    df = pd.DataFrame(rows)
    for y, v in prior.items():  # restated in the next 10-K: must agree
        cur = df.loc[df.year_end == y, "crt_rif_bn"]
        if len(cur) and pd.notna(cur.iloc[0]):
            assert cur.iloc[0] == v, f"{y}: CRT {cur.iloc[0]} vs restated {v}"
        elif len(cur):
            df.loc[df.year_end == y, ["crt_rif_bn", "crt_quote"]] = [v, f"restated in the FY{y + 1} 10-K"]
    df.to_csv(OUT, index=False)
    print(df[["year_end", "crt_rif_bn", "mi_rif_bn"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
