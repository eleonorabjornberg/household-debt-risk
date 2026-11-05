"""Write a task's register rows to the markets track file without re-adding rows already folded into the register.

Rows whose claim_id is already in claims/register.csv are not written again. Each must still match what the task's
generator produces (display, value, locations); a mismatch stops the run, because a folded row can only be changed in
claims/register.csv (by the coordinator). The remaining rows go to claims/tracks/markets.csv, which is created (with
the register's header) only if there is something to write; the task's own earlier rows there (by prefix) are replaced.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "claims" / "register.csv"
TRACK = ROOT / "claims" / "tracks" / "markets.csv"
CHECKED = ("display", "value", "locations")


class FoldedRowChanged(SystemExit):
    pass


def write_track_rows(rows: list[dict], prefix: str, register: Path = REGISTER, track: Path = TRACK) -> list[dict]:
    with open(register, newline="") as f:
        rd = csv.DictReader(f)
        header, reg = rd.fieldnames, {r["claim_id"]: r for r in rd}
    changed = [(r["claim_id"], c, reg[r["claim_id"]][c], r[c]) for r in rows if r["claim_id"] in reg
               for c in CHECKED if reg[r["claim_id"]][c] != r[c]]
    if changed:
        raise FoldedRowChanged("rows already in claims/register.csv would change (ask the coordinator to edit the "
                               "register; nothing written):\n" + "\n".join(f"  {i}.{c}: {a!r} -> {b!r}" for i, c, a, b in changed))
    new = [r for r in rows if r["claim_id"] not in reg]
    keep = []
    if track.exists():
        with open(track, newline="") as f:
            keep = [r for r in csv.DictReader(f) if not r["claim_id"].startswith(prefix)]
    dup = {r["claim_id"] for r in keep} & {r["claim_id"] for r in new}
    if dup:
        raise SystemExit(f"duplicate ids in {track}: {sorted(dup)}")
    if keep or new:
        track.parent.mkdir(parents=True, exist_ok=True)
        with open(track, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(keep + new)
    elif track.exists():
        track.unlink()
    return new
