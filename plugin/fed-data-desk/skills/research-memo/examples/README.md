# Logged examples (PLAN D3 acceptance: three audience examples)

All three are **Claude drafts** for Eleonora to review and rewrite. None has been sent anywhere. Written
2026-11-04 by three subagents (one per audience, running in parallel) from `SKILL.md`; then reviewed and corrected by
the main session. Each `.check.txt` is the final `memo_check.py` output.

| Memo | Audience profile | Body words | claim-check | Register rows |
|---|---|---|---|---|
| `mbs_desk.md` | `mbs_desk` (agency MBS trader / PM) | 796 | 15 MATCH, 5 AMBIGUOUS resolved by Sources | 16 |
| `rates_strategist.md` | `rates_strategist` (rates / macro strategist) | 761 | 17 MATCH, 2 AMBIGUOUS resolved | 16 |
| `bank_treasury.md` | `bank_treasury` (bank treasury / credit risk) | 848 | 16 MATCH, 7 AMBIGUOUS resolved | 22 |

PLAN.md's D3 lists "MBS desk, rates strategist, policy shop" as examples. Eleonora's decision of 2026-11-03 says
memos target financial institutions, so the third example is a bank treasury team. `policy_shop` stays in
`audiences.md` for use only if she asks.

## What the gate caught (subagents, before hand-back)
- "13.1 percentage points" was UNTRACED (not a register spelling); it became "+13.1 pp".
- These rows came back NOT RECOMPUTABLE in claim-check and were dropped: `nyfed_sample_share` (5% sample), `private_label_2026q2_real` ($681B),
  `a1_ginnie_holdings_2011q4` ($1.13T) and `nyfed_mortgage_change` ($74B).
- `uncoll_break_2005q4`, the only ESTIMATE row: claim-check returned **MISMATCH** on "11.5%". The number was dropped
  and the register row reported to the coordinator.

## What the main session caught on review (the gate cannot)
- **Definition error, in 2 of 3 memos:** `mbs_desk` and `bank_treasury` listed "the Fed" among public holders, and
  `bank_treasury` left out state and local governments. Fed MBS sit inside the agency pools and are never added.
  Fixed, and the rule is now in `SKILL.md`.
- **Wrong mechanism:** `mbs_desk` said Fed runoff "is the part of the public share that is moving"; `rates_strategist`
  said runoff "has not moved the public share much". By definition it does not move it at all. Fixed in both.
- **Garbled claim:** `bank_treasury` said the FFEL book "is what the public share now reflects". Rewritten to what the
  `ffel_guarantee` row supports: the bank-held part carried little private credit risk.

## Gaps found
- No register row for **banks' share of household debt**, the lead item for the bank audience. The memo says so
  in Caveats. Proposed to the coordinator as a new row.
- No register row for a **Fed runoff path or caps**, so the memos describe none.

Subagent tokens: mbs_desk 95.8k, rates_strategist 86.9k, bank_treasury 95.9k.
