#!/usr/bin/env python3
"""B2 deal level (Q-B2.2 (c)): Freddie Mac's STACR pricing workbook, tranche by tranche, 2013 to the latest deal.

    uv run --project pipeline python research/b2_crt_pricing/stacr_pricing.py           # fetch (if absent) and parse
    uv run --project pipeline python research/b2_crt_pricing/stacr_pricing.py --fetch   # fetch again

Source: https://capitalmarkets.freddiemac.com/crt/xlsxs/stacr-pricing.xlsx, linked from
https://capitalmarkets.freddiemac.com/crt/securities/pricing (host added by Eleonora 2026-11-05, card crt-host).
Plain request, no extra headers. The workbook is saved to data/b2/stacr/ (outside git) with its SHA-256 printed;
sources.md records the retrieval. One sheet, "STACR": one column per deal, rows labelled in column A.

Output: stacr_tranches.csv (committed), one row per deal and tranche: deal, closing date, benchmark, tranche,
issued amount ($), spread over the benchmark (decimal, as printed), initial credit enhancement of that tranche
(decimal, the tranche's attachment point as printed), and each cell's text as printed (*_raw). "Retained" tranches
have no amount (issued_note); "(Indicative)" spreads are flagged (spread_indicative); a dash, or the 2017-HRP1
par/discount/IO three-way values, give no parsed value and keep the raw text. Any other text that does not parse
raises; nothing is filled in.
This is the source table only: no cost measure is computed here (that needs a method choice, see METHOD.md).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
URL = "https://capitalmarkets.freddiemac.com/crt/xlsxs/stacr-pricing.xlsx"
RAW = ROOT / "data" / "b2" / "stacr" / "stacr-pricing.xlsx"
OUT = HERE / "stacr_tranches.csv"
LABELS = {"deal": None, "closing": "Closing Date", "benchmark": "Benchmark", "issuance": "Bond Issuance",
          "spread": "Spread", "ce": "Initial Credit Enhancement"}

STATUS = {"Retained"}           # printed in place of an amount: the tranche was kept by Freddie Mac, not sold
_ITEM = re.compile(r"(?<![^\s])([A-Z][A-Z0-9-]*)\s*:\s*(.+?)(?=\s+[A-Z][A-Z0-9-]*\s*:|\s*$)", re.S)


def fetch() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sS", "-L", "--fail", "--max-time", "120", "-o", str(RAW), URL], check=True)
    print(f"{URL} -> {RAW} {RAW.stat().st_size} bytes sha256 {hashlib.sha256(RAW.read_bytes()).hexdigest()}")


def items(cell) -> dict[str, str]:
    """'M-1: 1.35%\\nM-2: 1.55%' -> {'M-1': '1.35%', 'M-2': '1.55%'}; empty cell -> {}."""
    if cell is None or (isinstance(cell, float) and cell != cell):
        return {}
    text = str(cell)
    text = re.sub(r"^\s*Par/Disc\./IO\s*", "", text)                    # 2017-HRP1: header of a 3-way split
    text = re.sub(r"(?m)^(\s*[A-Z]-?\d)\s+(?=\d)", r"\1: ", text)       # 2018-HQA2 prints "M-1 3.00%" (no colon)
    out, end = {}, 0
    for m in _ITEM.finditer(text):
        if text[end:m.start()].strip():
            raise ValueError(f"unparsed text {text[end:m.start()]!r} in {text!r}")
        out[m.group(1)] = m.group(2).strip()
        end = m.end()
    if not out or text[end:].strip():
        raise ValueError(f"cannot parse {text!r}")
    return out


NA = {"–", "-", ""}


def money(s: str) -> float | None:
    if s.strip() in NA or "/" in s:      # dash = none; "a/b/c" = 2017-HRP1 par/discount/IO split, kept raw only
        return None
    m = re.fullmatch(r"\$?\s*([\d,]+(?:\.\d+)?)", s.strip())
    if not m:
        raise ValueError(f"not an amount: {s!r}")
    return float(m.group(1).replace(",", ""))


def pct(s: str) -> float | None:
    s = re.sub(r"\s*\(indicative\)\s*$", "", s.strip(), flags=re.I)
    if s in NA or "/" in s:
        return None
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*%", s)
    if m:
        return float(m.group(1)) / 100
    m = re.fullmatch(r"-?\d+(?:\.\d+)?", s)        # a bare number is already a decimal (e.g. 'B: 0.0')
    if m:
        return float(s)
    raise ValueError(f"not a percentage: {s!r}")


def parse(path: Path) -> pd.DataFrame:
    d = pd.read_excel(path, sheet_name="STACR", header=None)
    lab = {str(v).strip(): i for i, v in d[0].items() if isinstance(v, str)}
    for k, v in LABELS.items():
        if v and v not in lab:
            raise ValueError(f"row label {v!r} not found")
    rows = []
    for c in range(1, d.shape[1]):
        deal = d.iat[0, c]
        if not isinstance(deal, str) or not deal.strip():
            continue
        deal = re.sub(r"^STACR\s+", "", deal.strip())
        size, spread, ce = (items(d.iat[lab[LABELS[k]], c]) for k in ("issuance", "spread", "ce"))
        # tranche names are matched without hyphens: 2018-DNA2 prints "M1" in one row and "M-1" in another
        spread, ce = ({k.replace("-", ""): v for k, v in x.items()} for x in (spread, ce))
        for tr in size:
            key = tr.replace("-", "")
            rows.append({"deal": deal, "closing_date": pd.Timestamp(d.iat[lab["Closing Date"], c]).date().isoformat(),
                         "benchmark": str(d.iat[lab["Benchmark"], c]).strip(), "tranche": tr,
                         "issued_usd": None if size[tr] in STATUS else money(size[tr]),
                         "issued_note": size[tr] if size[tr] in STATUS else "",
                         "spread": pct(spread[key]) if key in spread else None,
                         "spread_indicative": "indicative" in spread.get(key, "").lower(),
                         "initial_ce": pct(ce[key]) if key in ce else None,
                         "issued_raw": size[tr], "spread_raw": spread.get(key, ""), "initial_ce_raw": ce.get(key, "")})
    return pd.DataFrame(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args(argv)
    if a.fetch or not RAW.exists():
        fetch()
    df = parse(RAW)
    df.to_csv(OUT, index=False)
    print(f"{OUT.relative_to(ROOT)}: {len(df)} tranches, {df['deal'].nunique()} deals, "
          f"{df['closing_date'].min()} to {df['closing_date'].max()}; "
          f"spread missing {int(df['spread'].isna().sum())}, initial CE missing {int(df['initial_ce'].isna().sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
