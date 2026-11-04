---
name: claim-check
description: Traces every number in a sentence, paragraph or file line to its row in claims/register.csv and independently recomputes it (validation check, results.json key, committed CSV/JSON), returning MATCH, MISMATCH (with the size), UNTRACED, AMBIGUOUS or NOT RECOMPUTABLE per number. Use when someone asks "where does this number come from", "is this figure right", "check the numbers in this paragraph / memo / README line", or before any prose with numbers is published or sent (research-memo, README, story copy). Not for refreshing data after a Z.1 release (z1-release-update), for adding or editing register rows, for writing new analysis, or for fixing copy.
---

# claim-check

Goal: for each number in a piece of text, say which register row backs it, whether the register value and an independent recompute agree with what is printed, and if not, by how much. It reads, it reports, it never edits.

Run from the repo root. The script reuses the token regex, normalisation and register parser of `claims/check_register.py`.

## Hard rules
- Never edit `claims/register.csv`, `validation/results.json`, `analysis/`, `research/` or any copy to make a verdict come out. Report; a human fixes the row or the copy (a register change is its own task, CLAUDE.md "Every published number needs a row").
- Never guess. If a row's `computation` cannot be parsed, or its recompute needs a judgement, the verdict is NOT RECOMPUTABLE with the reason. Never invent a number, a row or a source.
- UNTRACED is a finding, not an invitation to add a row from memory. "Related" rows it lists are leads, not matches.
- Report estimates as estimates: show the row's `validation` (`ESTIMATE`, `STALE`, `UNVERIFIED`) next to the verdict; a MATCH on an `UNVERIFIED` row only means register and recompute agree.

## Steps

### 1. Run it
```bash
uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py "The public share rose from 36.1% to 49.2%."
uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py --file README.md --line 10
uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py --file path/to/memo.md   # whole file
```
Add `--json` for machine output (`summary`, `items[]` with `verdict`, `rows[]`, `recompute`, `notes`). With `--file` inside the repo, lines in fenced code, `inline code` (.md) and comments (.ts) are skipped, as in `check_register.py`, and a row's `locations` can pin an otherwise ambiguous token to its line. Exit 0: no MISMATCH or UNTRACED; 1: at least one; 2: usage error.

### 2. Read the verdicts
| Verdict | Meaning | What to tell the human |
|---|---|---|
| MATCH | Printed token, register value and recompute agree at the token's precision (ROUND_HALF_UP). | Row id, validation status, vintage, how it was recomputed. Mention any "edge case" note (a source printed to fewer digits than the token). |
| MISMATCH | Register value or recompute rounds to a different number. | Both numbers and the size of the gap. State which side is stale (the row says STALE) or which looks wrong; do not fix it. |
| UNTRACED | No register row prints the token. | Say so; list related rows only as leads. The fix is a register row with a computation (separate task) or removing the number. |
| AMBIGUOUS | Several rows print the same token and no `locations` entry pins the line. | List the candidates (id, claim, period) and ask which is meant. |
| NOT RECOMPUTABLE | A row exists but no recompute path ran. | Give the reason (e.g. external source, derived expression, no key in the CSV reference, unit not comparable). Never fill the gap by hand. |

### 3. Recompute paths (in this order; the first that yields a number wins)
1. **Validation check**: the row's `check_id` names a check in `validation/results.json`; the number comes from its `observed`. When `observed` holds several numbers: a pair `A -> B` is matched to the quarters in the check description by the row's `period`; `A of B` takes A, or B if the row's claim says scope/total; otherwise the first comparable number (the note says which).
2. **results.json key** in `computation`: `analysis/results.json a.b.c`, a list element `windows[2007Q4].percentile_among_all_windows`, `research/<task>/... -> results.json change_usd_bn.x`, or `results.json obj: a / b - 1` (arithmetic over that object's fields). Computations that say `derived` or `recompute` are not single keys and are reported NOT RECOMPUTABLE.
3. **Committed CSV/JSON** named in `computation`: `X.csv col (KEY = v)`, `X.csv (KEY col)`, `X.csv col KEY`, `X.csv col max`; `X.json: sum(col) where k='v' and date='D'`; `min|max col for date >= D`; `sum of col for date D in X.json`. Anything else is NOT RECOMPUTABLE.

Units: shares stored as fractions are compared as percent for `%` tokens; `usd_tn` / `usd_bn` convert between $T, $B, $M tokens; sources named `*musd`, `*busd`, `*usd_bn` are converted to the row's unit; fractional percentiles are x100. CSV and check numbers keep their printed decimals, so the recompute is an interval; results.json numbers are read as exact. Signs are not verified (the register normalisation drops them); a sign that disagrees with the register value is noted.

### 4. Report
Group by verdict; MISMATCH and UNTRACED first. For each number: token, row id, verdict, one line of evidence. End with the SUMMARY line the script prints. If the text will be published, the count of non-MATCH numbers must be zero or each one accounted for by a human.

## Files
- `scripts/claim_check.py`: the CLI (read-only).
- `tests/test_claim_check.py`: synthetic register and results fixtures; `uv run --project pipeline pytest -q .claude/skills/claim-check/tests`.
- `examples/triggers.md`: prompts that should and should not trigger this skill, with recorded outputs.

## When NOT to use
- A new Z.1 release: use `z1-release-update` (its stale-claims step compares register values to new checks).
- Adding, correcting or promoting register rows (`claims/README.md`), or `claims/check_register.py` (the whole-repo scan for unregistered tokens).
- Writing new analysis, charts or memos (the memo skill calls this one at the end).
- Prose with no figures, or questions answered from the data directly ("what was the public share in 1990?").
