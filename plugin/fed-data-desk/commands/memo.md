---
description: Draft a two-page research memo for a named market audience, gated by memo_check (research-memo)
argument-hint: <audience key: mbs_desk | rates_strategist | bank_treasury | insurer_alm | crt_investor> [topic]
---
Use the `research-memo` skill for the audience and topic in: $ARGUMENTS

Follow its hard rules (Claude-draft banner, numbers only from the register, the public-holder definition), write the memo under `research/memos/<date>-<audience>.md`, run `memo_check.py` until it passes, and report the gate output. Do not send the memo anywhere.
