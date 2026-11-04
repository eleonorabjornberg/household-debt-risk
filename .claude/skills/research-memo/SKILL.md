---
name: research-memo
description: Turns the project's findings into a two-page research memo for a named market audience (agency MBS desk, rates strategist, bank treasury, insurer ALM, CRT investor), using only numbers that have a row in claims/register.csv, and gates it with memo_check.py so every number passes claim-check before it is shown to anyone. Every memo is a labelled Claude draft for Eleonora to rewrite. Use when someone asks for a memo, note, brief or client write-up of the findings for a market or institutional reader. Not for new analysis, the working paper or op-ed (F6), site copy, or checking a single number (claim-check).
---

# research-memo

Goal: a memo of about two pages (at most 1,000 words before Sources) that tells one kind of institutional
reader what the household-debt findings mean for their decisions. Every number in it is traceable to the
claims register and passes `claim-check`.

## Hard rules
- **Authorship (CLAUDE.md):** the memo starts with the banner `> **Claude draft.** ...` and stays a draft until
  Eleonora replaces it with her own text. Do not write in her voice or sign it as hers.
- **Numbers come only from the register** (`claims/register.csv`, `claims/tracks/*.csv`). Print them in one of
  the row's `display` spellings, exactly, so claim-check can trace them. No new numbers, no arithmetic of your
  own (a difference or ratio that has no row is a new claim: leave it out, or ask for a row first). Years and
  quarters used as labels are fine.
- Never use a row marked `STALE`. Say "estimate" next to any `ESTIMATE` row. An `UNVERIFIED` row is allowed,
  but its status shows in the Sources table.
- Holdings are not guarantees: "the public sector holds" never means "taxpayers bear the loss". Never put a NY
  Fed credit-report figure next to a Z.1 figure without saying which is which.
- No investment advice: describe what the data show and what to watch, not trades.

## Steps
1. **Audience.** Pick a profile from `audiences.md` (or add one there first). The decided target readers are
   financial institutions; `policy_shop` only if Eleonora asks.
2. **Facts.** List the candidate rows: `uv run --project pipeline python .claude/skills/research-memo/scripts/facts.py [words...]`
   (filters on claim text; shows id, display spellings, period, status, vintage). Choose 6–12 rows that matter
   to this reader. Read the row's `notes` for its caveats.
3. **Write** `MEMO.md` with the template below. Keep the body at or under 1,000 words.
4. **Gate:** `uv run --project pipeline python .claude/skills/research-memo/scripts/memo_check.py MEMO.md`.
   Fix the memo (never the register) until it passes. AMBIGUOUS means a spelling is shared by several rows:
   list the one you mean in Sources. NOT RECOMPUTABLE or UNTRACED means use another row or drop the number.
5. **Review** (optional but recommended before anyone outside sees it): the `editor` subagent for sourcing and
   overclaiming.
6. **Hand over** to Eleonora as a draft, with the memo_check output. Do not send it anywhere.

## Template
```markdown
> **Claude draft.** Written by Claude from the project's claims register for Eleonora to review and rewrite; not her text. Numbers: <vintages>.

# <Title: the finding, in words this reader uses>
**Audience:** <profile key and reader> · **Date:** <YYYY-MM-DD> · **Data:** Fed Z.1 Financial Accounts <vintage>; <others>

## Bottom line
<3–4 sentences.>

## What the data show
<3–5 short paragraphs or bullets, each with its numbers.>

## What it means for you
<What this reader should take from it, tied to their decisions. No trade recommendations.>

## Caveats
<Holdings vs guarantees, Z.1 vs NY Fed, estimates, revisions.>

## What to watch
<2–4 dated or conditional items.>

## Sources
| Register row | Claim | Period | Status | Vintage |
|---|---|---|---|---|
| `claim_id` | <claim, no numbers needed> | <period> | <validation> | <vintage> |
```

## Files
- `scripts/memo_check.py`: the gate (read-only); calls `claim-check`.
- `scripts/facts.py`: lists register rows to choose from.
- `audiences.md`: reader profiles.
- `examples/`: three logged memos with their memo_check output; `examples/triggers.md`.
- `tests/test_memo_check.py`: synthetic memos, pass and fail cases.
