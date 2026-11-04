#!/usr/bin/env python3
"""List published claims whose displayed number would change after a Z.1 release (PLAN task 0.8).

    uv run --project pipeline python .claude/skills/z1-release-update/scripts/stale_claims.py \
        [--register claims/register.csv] [--results validation/results.json]

Reads claims/register.csv (claim_id,claim,display,value,unit,period,locations,computation,series_ids,
vintage,validation,check_id,notes). For each row whose check_id is in the new validation results, it takes
the newly observed number from that check's `observed` text, rounds it and the register `value` to the
precision of the row's `display`, and lists the claim if they differ. It NEVER edits the register or any
copy; a human decides what to change. Rows with no check_id or a check_id absent from the results are
counted, not judged.

Matching the observed number: the check's `observed` text is searched for numbers with the same unit as the
row (%, pp, $T, $B, $M); when several fit (e.g. "36.12% -> 49.22%") the one closest to the register value is
used and the line is marked "ambiguous". Rows where no number of that unit is found are listed as "cannot
compare" so nothing is silently skipped.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NUM = r"[-+]?\d[\d,]*\.?\d*"


def unit_kind(unit: str, display: str) -> str | None:
    u = f"{unit} {display}".lower()
    if "pp" in u or "percentage point" in u or "pts" in u:
        return "pp"
    if "%" in u or "pct" in u or "percent" in u or "share" in u:
        return "%"
    if re.search(r"\d\s*t\b", u) or "trillion" in u:
        return "$T"
    if re.search(r"\d\s*b\b", u) or "billion" in u:
        return "$B"
    if re.search(r"\d\s*m\b", u) or "million" in u:
        return "$M"
    return None


def candidates(observed: str, kind: str) -> list[float]:
    pats = {
        "%": rf"({NUM})\s*%",
        "pp": rf"({NUM})\s*pp",
        "$T": rf"\$\s*({NUM})\s*T",
        "$B": rf"\$\s*({NUM})\s*B",
        "$M": rf"\$\s*({NUM})\s*M",
    }
    vals = []
    for m in re.finditer(pats[kind], observed):
        try:
            vals.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return vals


def display_decimals(display: str) -> int | None:
    m = re.search(r"\d[\d,]*(?:\.(\d+))?", display)
    return None if not m else len(m.group(1) or "")


def rnd(x: float, nd: int) -> Decimal:
    q = Decimal(1).scaleb(-nd)
    return Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP)


def to_float(s: str) -> float | None:
    try:
        return float(str(s).replace(",", "").replace("%", "").replace("$", "").strip())
    except ValueError:
        return None


def analyse(rows, checks_by_id):
    stale, same, cannot, no_check = [], [], [], []
    for r in rows:
        cid = (r.get("check_id") or "").strip()
        if not cid or cid not in checks_by_id:
            no_check.append(r)
            continue
        kind = unit_kind(r.get("unit", ""), r.get("display", ""))
        nd = display_decimals(r.get("display", ""))
        reg = to_float(r.get("value", ""))
        if kind is None or nd is None or reg is None:
            cannot.append((r, "unit, display precision or value not readable"))
            continue
        cands = candidates(checks_by_id[cid]["observed"], kind)
        if not cands:
            cannot.append((r, f"no {kind} number in check {cid} observed text: {checks_by_id[cid]['observed']!r}"))
            continue
        new = min(cands, key=lambda c: abs(c - reg))
        ambiguous = len(cands) > 1
        item = (r, reg, new, nd, kind, ambiguous)
        (stale if rnd(new, nd) != rnd(reg, nd) else same).append(item)
    return stale, same, cannot, no_check


def render(stale, same, cannot, no_check, results_label) -> str:
    L = [f"Stale-claim scan against {results_label}", "",
         f"changed: {len(stale)}   unchanged: {len(same)}   cannot compare: {len(cannot)}   "
         f"no check in this run: {len(no_check)}", ""]
    if stale:
        L.append("Claims whose displayed number would change (copy NOT edited):")
        for r, reg, new, nd, kind, amb in stale:
            L.append(f"- {r['claim_id']}: shows {r['display']!r}, register value {reg} -> now {rnd(new, nd)} {kind} "
                     f"[check {r['check_id']}{', ambiguous match' if amb else ''}]")
            L.append(f"    claim: {r['claim']}")
            L.append(f"    locations: {r.get('locations') or '(none recorded)'}")
    else:
        L.append("No displayed number changes.")
    if cannot:
        L += ["", "Could not compare (check by hand):"]
        L += [f"- {r['claim_id']} ({r['check_id']}): {why}" for r, why in cannot]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--register", type=Path, default=ROOT / "claims" / "register.csv")
    ap.add_argument("--results", type=Path, default=ROOT / "validation" / "results.json")
    a = ap.parse_args(argv)
    if not a.register.exists():
        print(f"{a.register} does not exist yet (task 0.5); skipping the stale-copy scan.")
        return 0
    if not a.results.exists():
        print(f"{a.results} not found; run validation first.", file=sys.stderr)
        return 2
    results = json.loads(a.results.read_text())
    checks = {c["id"]: c for c in results["checks"]}
    with a.register.open(newline="") as f:
        rows = list(csv.DictReader(f))
    label = f"{a.results.name} (vintage {results.get('meta', {}).get('vintage', '?')}, latest {results.get('meta', {}).get('latest', '?')})"
    print(render(*analyse(rows, checks), label), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
