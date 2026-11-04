"""Helpers for the scheduled Z.1 release workflow (PLAN F3, .github/workflows/z1-release.yml).

    python tools/z1_release.py detect ZIP          # is ZIP newer than web/public/data/meta.json vintages.z1?
    python tools/z1_release.py pr-body DIR         # PR description from the files the run wrote to DIR

`detect` reads the Z1.csv member date inside the zip (the release date, as the pipeline and validation
use it), so it needs no data/manifest.jsonl and works in a fresh CI checkout. It prints key=value lines
for $GITHUB_OUTPUT: new=true|false, vintage, previous, prev_url (the Fed's archive of the previous
release, which validation and what_moved.py read as the comparison vintage).

`pr-body` assembles the pull-request text: a header saying nothing is published or loaded until
Eleonora merges, the validation summary, the "what moved" note, the stale published numbers and the
reproduction check. It reports; it never edits a number or copy. Stdlib only.
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_URL = "https://www.federalreserve.gov/releases/z1/{d}/z1_csv_files.zip"


def member_date(zip_path: Path) -> date:
    with zipfile.ZipFile(zip_path) as z:
        y, m, d, *_ = z.getinfo("Z1.csv").date_time
    return date(y, m, d)


def detect(zip_path: Path, meta_path: Path = ROOT / "web" / "public" / "data" / "meta.json") -> dict:
    have = date.fromisoformat(json.loads(meta_path.read_text())["vintages"]["z1"])
    live = member_date(zip_path)
    return {
        "new": "true" if live > have else "false",
        "vintage": live.isoformat(),
        "previous": have.isoformat(),
        "prev_url": ARCHIVE_URL.format(d=have.strftime("%Y%m%d")),
    }


def _read(p: Path, limit: int = 60_000) -> str:
    if not p.exists():
        return f"_{p.name} was not produced (see the workflow log)._"
    t = p.read_text()
    return t if len(t) <= limit else t[:limit] + "\n\n_(truncated; full file in the PR)_"


def pr_body(d: Path) -> str:
    res = ROOT / "validation" / "results.json"
    summary = json.loads(res.read_text()).get("summary", {}) if res.exists() else {}
    fails = summary.get("FAIL", "?")
    gate = "PASSED" if fails == 0 else "FAILED: do not merge until the failing checks are explained"
    meta = json.loads((ROOT / "web" / "public" / "data" / "meta.json").read_text())
    return f"""**Automated Z.1 release draft (PLAN F3). Nothing is published or loaded until Eleonora reviews and merges this PR.**

Z.1 vintage {meta['vintages'].get('z1')} · FRED as-of {meta['vintages'].get('fred')} · NY Fed retrieved {meta['vintages'].get('nyfed')}.
Validation gate: **{gate}** ({', '.join(f'{k} {v}' for k, v in summary.items())}).

The numbers and copy have not been edited. The register rows and copy listed under "Stale published numbers"
need a human decision.

**Release notes (decision F3-2):** open a Claude Code session on this PR's branch and run the `z1-release-update`
skill from step 5; it turns the note below into reader-facing release notes marked "Claude draft" and stops at its
approval gates. Eleonora edits and approves them before merging.

After merging: the database is loaded by hand (Actions → refresh-data → Run workflow, load = true).

## What moved
{_read(d / 'what_moved.md')}

## Stale published numbers
```
{_read(d / 'stale_claims.txt', 20_000)}
```

## Reproduction check against the previous commit
```
{_read(d / 'repro.txt', 10_000)}
```
"""


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "detect":
        for k, v in detect(Path(argv[2])).items():
            print(f"{k}={v}")
        return 0
    if len(argv) == 3 and argv[1] == "pr-body":
        sys.stdout.write(pr_body(Path(argv[2])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
