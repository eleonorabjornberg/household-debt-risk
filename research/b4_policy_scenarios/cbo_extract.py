#!/usr/bin/env python3
"""B4 student-loan proxy (card cbo-repo-55 (b), 2026-11-11): the Direct Loan program account's projected outlays from
CBO's account-level baseline files, extracted into cbo_direct_loan_outlays.csv (committed; the raw files are not).

    uv run --project pipeline python research/b4_policy_scenarios/cbo_extract.py           # fetch (if absent) + extract
    uv run --project pipeline python research/b4_policy_scenarios/cbo_extract.py --fetch   # fetch again

Source: https://github.com/US-CBO/cbo-data, commit 284a956 (git clone, sparse; api.github.com is not used). Each file's
SHA-256 is checked against the values recorded in sources.md before anything is read; a mismatch stops the run.
Units as the files state: outlays and budget authority in millions of dollars, by federal fiscal year.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data" / "b4" / "cbo" / "cbo-data"
REPO = "https://github.com/US-CBO/cbo-data.git"
COMMIT = "284a95665f9f2f74ed1f482feb629b43fce323da"
SUBDIR = "data/budget/spending_detail"
OUT = HERE / "cbo_direct_loan_outlays.csv"
TIN = "091-0243-0-1-502"
TITLE = "Federal Direct Student Loan Program Account"
# baseline label -> (file, SHA-256 recorded in sources.md)
FILES = {
    "2024-06": ("annual_fy_2024-06.csv", "e3ba6b8ab26036fde23b0c0e0234930dfecb001669f3806c83680b9ca51b5559"),
    "2025-01": ("annual_fy_2025-01.csv", "a56b2b37b38f7345cce6a2c173d86ed7fd3534d9742e130236178a52ec63fcac"),
    "2026-02": ("annual_fy_2026-02.csv", "161e2432d955fe37815a761454299a0b61de06298aff9bf4fcd89bb88939e1db"),
}


def fetch() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not (RAW / ".git").exists():
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--sparse", "--no-checkout", REPO, str(RAW)], check=True)
    subprocess.run(["git", "-C", str(RAW), "sparse-checkout", "set", SUBDIR], check=True)
    subprocess.run(["git", "-C", str(RAW), "checkout", "-q", COMMIT], check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(raw_dir: Path) -> list[dict]:
    rows = []
    for baseline, (name, want) in FILES.items():
        path = raw_dir / name
        got = sha256(path)
        if got != want:
            raise SystemExit(f"{name}: SHA-256 {got} does not match the recorded {want}")
        with open(path, newline="") as f:
            mine = [r for r in csv.DictReader(f) if r["tin"] == TIN]
        if not mine:
            raise SystemExit(f"{name}: no row for {TIN}")
        for r in mine:
            if r["title"] != TITLE or r["disc_or_mand"] != "Mandatory":
                raise SystemExit(f"{name}: unexpected title or class for {TIN}: {r['title']!r} {r['disc_or_mand']!r}")
            fy = int(r["date"].removeprefix("FY"))
            rows.append({"baseline": baseline, "fiscal_year": fy, "tin": TIN, "title": TITLE,
                         "outlays_musd": float(r["outlays"]), "budget_authority_musd": float(r["budget_authority"]),
                         "file": f"{SUBDIR}/{name}", "file_sha256": got})
        years = [x["fiscal_year"] for x in rows if x["baseline"] == baseline]
        if years != sorted(set(years)):
            raise SystemExit(f"{name}: fiscal years repeat or are out of order: {years}")
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args(argv)
    if a.fetch or not (RAW / SUBDIR / FILES["2026-02"][0]).exists():
        fetch()
    head = subprocess.run(["git", "-C", str(RAW), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != COMMIT:
        raise SystemExit(f"raw clone at {head}, expected {COMMIT}")
    rows = extract(RAW / SUBDIR)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{OUT.relative_to(ROOT)}: {len(rows)} rows ({TIN}), baselines {', '.join(FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
