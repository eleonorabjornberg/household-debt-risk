# Job 1, after: `/fed-data-desk:check` (claim-check skill)

Sentence: The public share rose from 36.1% to 49.2% between 2007 and 2011, a jump of 13.1 points.

```
$ uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py "The public share rose from 36.1% to 49.2% between 2007 and 2011, a jump of 13.1 points."
[1] '36.1%' (line 1) -> MATCH
    register public_share_2007q4: value=0.3612 share, period 2007Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #1, paired with period 2007Q4 in the check description = 36.12 (pct) -> 36.1200 in token units, rounds to 36.1
[2] '49.2%' (line 1) -> MATCH
    register public_share_2011q4: value=0.4922 share, period 2011Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #2, paired with period 2011Q4 in the check description = 49.22 (pct) -> 49.2200 in token units, rounds to 49.2
[3] '13.1 points' (line 1) -> MATCH
    register gfc_jump_pp: value=13.11 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation PASS (C5)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C5
    recompute: validation check C5 (PASS) observed '+13.11 pp (rounded pts: +13.1)': the only comparable number = 13.11 (pp) -> 13.1100 in token units, rounds to 13.1
SUMMARY MATCH 3, MISMATCH 0, UNTRACED 0, AMBIGUOUS 0, NOT RECOMPUTABLE 0 (of 3 numbers)
```
