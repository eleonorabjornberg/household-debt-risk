"""memo_check.py against the real register and claim-check (PLAN D3)."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("memo_check", HERE.parent / "scripts" / "memo_check.py")
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

GOOD = """> **Claude draft.** Written by Claude from the claims register for Eleonora to review; not her text.

# Test memo
**Audience:** mbs_desk · **Date:** 2026-11-04

## Bottom line
The public share of household debt went from 36.1% at the end of 2007 to 49.2% four years later.

## What the data show
That jump of 13.1 points is the one real ratchet in the record.

## What it means for you
Holder mix matters for supply.

## Caveats
Holdings are not guarantees.

## What to watch
The next Z.1 release.

## Sources
| Register row | Claim | Period | Status | Vintage |
|---|---|---|---|---|
| `public_share_2007q4` | public share | 2007Q4 | PASS | z1:2026-09-11 |
| `public_share_2011q4` | public share | 2011Q4 | PASS | z1:2026-09-11 |
| `gfc_jump_pp` | jump | 2007Q4-2011Q4 | PASS | z1:2026-09-11 |
"""


def run(tmp_path, text, **kw):
    p = tmp_path / "memo.md"
    p.write_text(text)
    return mc.check(p, kw.get("max_words", 1000))


def test_good_memo_passes(tmp_path):
    r = run(tmp_path, GOOD)
    assert r["pass"], r["errors"]
    assert set(r["rows_used"]) == {"public_share_2007q4", "public_share_2011q4", "gfc_jump_pp"}


def test_missing_banner_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("**Claude draft.**", "Draft."))
    assert not r["pass"] and any("banner" in e for e in r["errors"])


def test_untraced_number_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("Holder mix matters for supply.", "Holder mix moved 77.7% this year."))
    assert not r["pass"] and any("77.7%" in e and "UNTRACED" in e for e in r["errors"])


def test_unlisted_row_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("| `gfc_jump_pp` | jump | 2007Q4-2011Q4 | PASS | z1:2026-09-11 |\n", ""))
    assert not r["pass"] and any("gfc_jump_pp" in e and "Sources" in e for e in r["errors"])


def test_word_limit(tmp_path):
    r = run(tmp_path, GOOD, max_words=20)
    assert not r["pass"] and any("word" in e for e in r["errors"])
