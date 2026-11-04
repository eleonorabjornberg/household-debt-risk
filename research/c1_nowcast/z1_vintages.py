#!/usr/bin/env python3
"""C1: real-time Z.1 vintages of the public share and its holder cells, from the Fed's release archive.

    uv run --project pipeline python research/c1_nowcast/z1_vintages.py

For every Z.1 release in z1_calendar.csv from 2016-09-16 on (the first release with a CSV zip), downloads
https://www.federalreserve.gov/releases/z1/<YYYYMMDD>/z1_csv_files.zip into data/z1_archive/ (git-ignored;
size and SHA-256 appended to data/z1_archive/manifest.jsonl), parses it with validation/zparse.py
load_table_zip, and computes household-apportioned holder cells (CELLS below), so every vintage's share is computed as
validation and A1 compute the latest one.

Writes data/c1/z1_cells.parquet-like CSV (data/c1/z1_cells.csv: release, quarter, loan, side, holder, usd_m)
and research/c1_nowcast/z1_share_vintages.csv (release, quarter, share) for the quarters each release
covers from 1952Q1, plus first_release.csv (quarter, first release date, first-release share).

Checks (assert): every cell is present (alias codes allowed, listed in z1_vintage_notes.csv); the residual
private cells are positive; the latest archived release reproduces validation's 2026Q2 share and, for every
quarter from 1952Q1, the share A1 computes from the latest Z1.csv (test_z1_vintages.py).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "validation"))
import zparse  # noqa: E402

ARCH = ROOT / "data" / "z1_archive"
OUT = ROOT / "data" / "c1"
FIRST_CSV_RELEASE = "2016-09-16"
KEEP_FROM = "1952Q1"


# Cells built from codes present in every layout since 2016 (aliases: the 2016 tables used older codes for
# two consumer-credit holders). Mortgage cells are apportioned to households with FL153165105 / FL893065105,
# as validation and A1 do. Private holdings without a named cell are the residual of each liability total,
# so the share never depends on private holder codes that were renamed between layouts.
CELLS = {
    # name: (loan, side, [alias codes, first found wins])
    "mort_federal": ("mortgages", "public", ["FL313065105"]),
    "mort_gse": ("mortgages", "public", ["FL403065105"]),
    "mort_pools": ("mortgages", "public", ["FL413065105"]),
    "mort_state_local": ("mortgages", "public", ["FL213065103"]),
    "mort_banks": ("mortgages", "private", ["FL763065105"]),
    "cc_federal": ("consumer credit", "public", ["FL313066220"]),
    "cc_sallie_gse": ("consumer credit", "public", ["FL403066005"]),
    "cc_depository": ("consumer credit", "private", ["FL763066005", "FL763066000"]),
    "cc_finance": ("consumer credit", "private", ["FL613066005"]),
    "cc_credit_unions": ("consumer credit", "private", ["FL473066000"]),
}
TOTALS = ["FL153165105", "FL153166000", "FL893065105"]


def ids_needed() -> list[str]:
    return sorted(set(TOTALS) | {c for _, _, al in CELLS.values() for c in al})


def fetch(release: str) -> Path | None:
    ARCH.mkdir(parents=True, exist_ok=True)
    d = release.replace("-", "")
    path = ARCH / f"{d}.zip"
    if path.exists():
        return path
    url = f"https://www.federalreserve.gov/releases/z1/{d}/z1_csv_files.zip"
    import requests  # same client and defaults as validation/run.py ensure_zip
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=180)
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code == 404:
            return None  # release has no CSV zip (2017-03-09): recorded as absent
        r.raise_for_status()  # any other refusal stops the run; it is not retried with a different client
        body = r.content
        break
    path.write_bytes(body)
    with open(ARCH / "manifest.jsonl", "a") as f:
        f.write(json.dumps({"release": release, "url": url, "bytes": len(body),
                            "sha256": hashlib.sha256(body).hexdigest(),
                            "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
    return path


def vintage_cells(path: Path, ids):
    """Cells ($M, household-apportioned) of one release; columns MultiIndex (loan, side, holder)."""
    ser, conflicts = zparse.load_table_zip(path, ids)
    df = pd.DataFrame(ser).sort_index()
    df.index = pd.to_datetime(df.index)
    df = df[df.index >= pd.Period(KEEP_FROM, "Q").start_time]
    missing = [t for t in TOTALS if t not in df]
    assert not missing, (path.name, "totals missing", missing)
    a = df["FL153165105"] / df["FL893065105"]
    out, used = {}, {}
    for name, (loan, side, aliases) in CELLS.items():
        code = next((c for c in aliases if c in df), None)
        if code is None:
            if name == "cc_sallie_gse":   # Sallie Mae left the GSE sector in 2004: series dropped, value 0 since
                out[(loan, side, name)] = pd.Series(0.0, index=df.index)
                used[name] = "absent (0 after 2004 privatisation)"
                continue
            raise AssertionError((path.name, "cell missing", name, aliases))
        x = df[code].fillna(0.0) if name == "cc_sallie_gse" else df[code]
        out[(loan, side, name)] = x * a if loan == "mortgages" else x
        used[name] = code
    mort_named = sum(v for k, v in out.items() if k[0] == "mortgages")
    cc_named = sum(v for k, v in out.items() if k[0] == "consumer credit")
    out[("mortgages", "private", "mort_other_private")] = df["FL153165105"] - mort_named
    out[("consumer credit", "private", "cc_other_private")] = df["FL153166000"] - cc_named
    c = pd.DataFrame(out)
    c.columns = pd.MultiIndex.from_tuples(c.columns, names=["loan", "side", "holder"])
    assert c.notna().all().all(), (path.name, c.columns[c.isna().any()].tolist())
    assert (c[("mortgages", "private", "mort_other_private")] > 0).all()
    assert (c[("consumer credit", "private", "cc_other_private")] > 0).all()
    return c, used, conflicts


def main() -> int:
    cal = pd.read_csv(HERE / "z1_calendar.csv")
    rel = [r for r in cal["z1_release"] if r >= FIRST_CSV_RELEASE]
    ids = ids_needed()
    long, shares, notes = [], [], []
    for r in rel:
        path = fetch(r)
        if path is None:
            notes.append({"release": r, "last_quarter": "", "codes_used": "NO CSV ZIP IN FED ARCHIVE",
                          "conflicting_series": ""})
            continue
        c, used, conflicts = vintage_cells(path, ids)
        sh = c.xs("public", level="side", axis=1).sum(axis=1) / c.sum(axis=1)
        q = [str(pd.Period(t, "Q")) for t in sh.index]
        shares.append(pd.DataFrame({"release": r, "quarter": q, "share": sh.values}))
        s = c.stack(level=[0, 1, 2], future_stack=True).rename("usd_m").reset_index()
        s.columns = ["date", "loan", "side", "holder", "usd_m"]
        s.insert(0, "release", r)
        s["quarter"] = s["date"].dt.to_period("Q").astype(str)
        long.append(s.drop(columns="date"))
        notes.append({"release": r, "last_quarter": q[-1],
                      "codes_used": " ".join(f"{k}={v}" for k, v in used.items() if v not in CELLS[k][2][:1]),
                      "conflicting_series": " ".join(conflicts)})
    sv = pd.concat(shares, ignore_index=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.concat(long, ignore_index=True).to_csv(OUT / "z1_cells.csv", index=False, float_format="%.6g")
    sv.to_csv(HERE / "z1_share_vintages.csv", index=False, float_format="%.8f")
    pd.DataFrame(notes).to_csv(HERE / "z1_vintage_notes.csv", index=False)

    # First release of each quarter: the earliest release whose last quarter it is
    fr = sv.merge(pd.DataFrame(notes)[["release", "last_quarter"]], on="release")  # absent releases drop out
    fr = fr[fr["quarter"] == fr["last_quarter"]].sort_values("release").groupby("quarter").first().reset_index()
    fr[["quarter", "release", "share"]].rename(columns={"release": "first_release", "share": "share_first"}).to_csv(
        HERE / "first_release.csv", index=False, float_format="%.8f")

    # Check: the latest archived release reproduces validation's latest share (register public_share_2026q2)
    last = sv[sv["release"] == rel[-1]].set_index("quarter")["share"]
    if "2026Q2" in last.index:
        assert abs(last["2026Q2"] - 0.5638) < 5e-4, last["2026Q2"]
    print(f"{len(rel)} calendar releases, {sv.release.nunique()} parsed {rel[0]}..{rel[-1]}; first releases for {len(fr)} quarters "
          f"{fr.quarter.iloc[0]}..{fr.quarter.iloc[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
