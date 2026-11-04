# Trigger examples for `claim-check`

## Should trigger

| Prompt | Why |
|---|---|
| "Where does the 56.4% in the README come from?" | Asks for the trace of a printed number: register row, series, vintage. |
| "Check the numbers in this paragraph before I send it to the MBS desk." | Pre-publication check of every figure in a text. |
| "Is it true that public holders own 61.2% of household debt?" | A single claimed number; expect UNTRACED or MISMATCH with the related rows. |
| "Run a claim check on research/a1_gfc_decomposition/README.md." | Whole-file mode. |
| "The memo says the Fed's MBS runoff is $845B. Can you verify that?" | One figure, register row plus recompute. |
| "Which register rows back the numbers on line 10 of README.md?" | `--file README.md --line 10`. |
| "Does the 13.1 pp jump in this sentence still agree with the validation suite?" | Recompute through a validation check (C5). |
| "Verify every figure in the draft Slack post and flag anything without a source." | UNTRACED is exactly the flag. |

## Should NOT trigger

| Prompt | Why |
|---|---|
| "The Fed published a new Z.1, run the update." | Release refresh: `z1-release-update`. |
| "Add a register row for the new 3.8 pp figure." | Editing the register is a separate task; this skill never writes. |
| "Write a two-page memo on the public share for a rates strategist." | New writing (research-memo); claim-check runs at the end, not instead. |
| "Run the GFC decomposition on the 2007Q4 to 2011Q4 window." | New analysis. |
| "What was the public share in 1990?" | A data question: answer from the snapshot or `mart.public_share`. |
| "Fix the line numbers in claims/register.csv locations." | Register maintenance (`claims/check_register.py`). |
| "Why does validation check E8 warn on 2003Q4?" | Investigating a validation result, not tracing copy. |
| "Make the hero chart show 2026Q2." | Front-end work. |

## Recorded outputs

Recorded 2026-11-04 on branch `claude/sweet-gates-avwrcs`, unedited. The `warning: UV_NATIVE_TLS` line uv prints on stderr is omitted.

### 1. `README.md` line 10 (contains 56.4%)

```
$ uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py --file README.md --line 10
[1] '3.2%' (line 10) -> MATCH
    register public_share_1952q1: value=0.0322 share, period 1952Q1, vintage z1:2026-09-11, validation PASS (C1)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C1
    recompute: validation check C1 (PASS) observed '3.22%': the only comparable number = 3.22 (pct) -> 3.2200 in token units, rounds to 3.2
[2] '56.4%' (line 10) -> MATCH
    register public_share_2026q2: value=0.5638 share, period 2026Q2, vintage z1:2026-09-11, validation PASS (C2)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C2
    recompute: validation check C2 (PASS) observed '56.38%': the only comparable number = 56.38 (pct) -> 56.3800 in token units, rounds to 56.4
[3] '$10.77T' (line 10) -> MATCH
    register public_usd_2026q2: value=10.77 usd_tn, period 2026Q2, vintage z1:2026-09-11, validation PASS (C3)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C3
    recompute: validation check C3 (PASS) observed '$10.768T of $19.097T': first number of 'A of B' = 10.768 (T) -> 10.7680 in token units, rounds to 10.77
[4] '$19.10T' (line 10) -> MATCH
    register scope_usd_2026q2: value=19.1 usd_tn, period 2026Q2, vintage z1:2026-09-11, validation PASS (C3)
    series FL154104015 FL153165105 FL153166000; computation: C3
    recompute: validation check C3 (PASS) observed '$10.768T of $19.097T': second number of 'A of B' (row claim says scope/total) = 19.097 (T) -> 19.0970 in token units, rounds to 19.10
SUMMARY MATCH 4, MISMATCH 0, UNTRACED 0, AMBIGUOUS 0, NOT RECOMPUTABLE 0 (of 4 numbers)
(exit 0)
```

### 2. A correct sentence

```
$ uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py "The public share rose from 36.1% to 49.2% between 2007 and 2011."
[1] '36.1%' (line 1) -> MATCH
    register public_share_2007q4: value=0.3612 share, period 2007Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #1, paired with period 2007Q4 in the check description = 36.12 (pct) -> 36.1200 in token units, rounds to 36.1
[2] '49.2%' (line 1) -> MATCH
    register public_share_2011q4: value=0.4922 share, period 2011Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #2, paired with period 2011Q4 in the check description = 49.22 (pct) -> 49.2200 in token units, rounds to 49.2
SUMMARY MATCH 2, MISMATCH 0, UNTRACED 0, AMBIGUOUS 0, NOT RECOMPUTABLE 0 (of 2 numbers)
(exit 0)
```

### 3. A deliberately wrong sentence

```
$ uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py "Public holders own 61.2% of household debt in 2026Q2."
[1] '61.2%' (line 1) -> UNTRACED
    no register row prints this token
    related, not a match: public_share_2026q2 prints '56.4%' (2026Q2)
    related, not a match: public_share_mortgage_2026q2 prints '65.6%' (2026Q2)
    related, not a match: public_share_cc_2026q2 prints '31.3%' (2026Q2)
    related, not a match: mortgage_share_of_scope_2026q2 prints '73.2% | 73%' (2026Q2)
SUMMARY MATCH 0, MISMATCH 0, UNTRACED 1, AMBIGUOUS 0, NOT RECOMPUTABLE 0 (of 1 numbers)
(exit 1)
```

### 4. Whole file: `research/a1_gfc_decomposition/README.md`

```
$ uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py --file research/a1_gfc_decomposition/README.md
[1] '36.1%' (line 11) -> MATCH
    register public_share_2007q4: value=0.3612 share, period 2007Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #1, paired with period 2007Q4 in the check description = 36.12 (pct) -> 36.1200 in token units, rounds to 36.1
[2] '49.2%' (line 11) -> MATCH
    register public_share_2011q4: value=0.4922 share, period 2011Q4, vintage z1:2026-09-11, validation PASS (C4)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C4
    recompute: validation check C4 (PASS) observed '36.12% -> 49.22%': number #2, paired with period 2011Q4 in the check description = 49.22 (pct) -> 49.2200 in token units, rounds to 49.2
[3] '13.1 pp' (line 11) -> MATCH
    register gfc_jump_pp: value=13.11 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation PASS (C5)
    series FL154104015 FL153165105 FL153166000 FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005; computation: C5
    recompute: validation check C5 (PASS) observed '+13.11 pp (rounded pts: +13.1)': the only comparable number = 13.11 (pp) -> 13.1100 in token units, rounds to 13.1
[4] '7.1 pp' (line 13) -> MATCH
    register a1_public_growth_pp: value=7.1268 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json from_public_growth_pp
    recompute: research/a1_gfc_decomposition/results.json from_public_growth_pp = 7.126829 -> 7.1268 in token units, rounds to 7.1
[5] '6.0 pp' (line 13) -> MATCH
    register a1_private_change_pp: value=5.9788 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json from_private_change_pp
    recompute: research/a1_gfc_decomposition/results.json from_private_change_pp = 5.97876 -> 5.9788 in token units, rounds to 6.0
[6] '$746B' (line 19) -> MATCH
    register a1_ginnie_change_usd: value=745.9510 usd_bn, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL413065110 FL413065133 FL153165105 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json change_usd_bn.ginnie_pools
    recompute: research/a1_gfc_decomposition/results.json change_usd_bn.ginnie_pools = 745.951 -> 745.9510 in token units, rounds to 746
[7] '3.8 pp' (line 19) -> MATCH
    1 row(s) pinned by locations research/a1_gfc_decomposition/README.md:19
    register a1_ginnie_pp: value=3.8090 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL413065110 FL413065133 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json groups_pp.ginnie_pools
    recompute: research/a1_gfc_decomposition/results.json groups_pp.ginnie_pools = 3.808975 -> 3.8090 in token units, rounds to 3.8
[8] '$379B' (line 20) -> MATCH
    register a1_student_change_usd: value=379.1020 usd_bn, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL313066220; computation: research/a1_gfc_decomposition/decompose.py -> results.json change_usd_bn.federal_student_loans
    recompute: research/a1_gfc_decomposition/results.json change_usd_bn.federal_student_loans = 379.102 -> 379.1020 in token units, rounds to 379
[9] '1.9 pp' (line 20) -> MATCH
    register a1_student_pp: value=1.9358 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL313066220 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json groups_pp.federal_student_loans
    recompute: research/a1_gfc_decomposition/results.json groups_pp.federal_student_loans = 1.935771 -> 1.9358 in token units, rounds to 1.9
[10] '$278B' (line 21) -> MATCH
    register a1_ff_change_usd: value=278.3680 usd_bn, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123; computation: research/a1_gfc_decomposition/decompose.py -> results.json change_usd_bn.fannie_freddie
    recompute: research/a1_gfc_decomposition/results.json change_usd_bn.fannie_freddie = 278.368 -> 278.3680 in token units, rounds to 278
[11] '1.4 pp' (line 21) -> MATCH
    1 row(s) pinned by locations research/a1_gfc_decomposition/README.md:21
    register a1_ff_pp: value=1.4214 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json groups_pp.fannie_freddie
    recompute: research/a1_gfc_decomposition/results.json groups_pp.fannie_freddie = 1.421405 -> 1.4214 in token units, rounds to 1.4
[12] '$1.71T' (line 25) -> MATCH
    register a1_pls_change_usd: value=1.7067 usd_tn, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL673065105 FL643065173 FL673066000; computation: research/a1_gfc_decomposition/decompose.py -> results.json change_usd_bn.private_label_and_mreits
    recompute: research/a1_gfc_decomposition/results.json change_usd_bn.private_label_and_mreits = -1706.7 -> 1.7067 in token units, rounds to 1.71
[13] '4.9 pp' (line 25) -> MATCH
    register a1_pls_pp: value=4.9267 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL673065105 FL643065173 FL673066000 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json groups_pp.private_label_and_mreits
    recompute: research/a1_gfc_decomposition/results.json groups_pp.private_label_and_mreits = 4.926664 -> 4.9267 in token units, rounds to 4.9
[14] '6.0 pp' (line 25) -> MATCH
    register a1_private_change_pp: value=5.9788 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> results.json from_private_change_pp
    recompute: research/a1_gfc_decomposition/results.json from_private_change_pp = 5.97876 -> 5.9788 in token units, rounds to 6.0
[15] '6.1 pp' (line 27) -> NOT RECOMPUTABLE
    1 row(s) pinned by locations research/a1_gfc_decomposition/README.md:27
    register a1_ginnie_own_pp: value=6.1191 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL413065110 FL413065133 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> own_share_change.csv
    recompute: none (no results.json key in computation; own_share_change.csv: cannot identify one value column in '')
    - no recompute: no results.json key in computation; own_share_change.csv: cannot identify one value column in ''
[16] '3.9 pp' (line 27) -> NOT RECOMPUTABLE
    register a1_ff_own_pp: value=3.8875 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> own_share_change.csv
    recompute: none (no results.json key in computation; own_share_change.csv: cannot identify one value column in '')
    - no recompute: no results.json key in computation; own_share_change.csv: cannot identify one value column in ''
[17] '3.1 pp' (line 27) -> NOT RECOMPUTABLE
    register a1_student_own_pp: value=3.0775 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL313066220 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> own_share_change.csv
    recompute: none (no results.json key in computation; own_share_change.csv: cannot identify one value column in '')
    - no recompute: no results.json key in computation; own_share_change.csv: cannot identify one value column in ''
[18] '1.3 pp' (line 31) -> MATCH
    register a1_ff_chained_2008q3: value=1.3412 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> path.csv fannie_freddie 2008Q3
    recompute: path.csv [2008Q3] fannie_freddie = 1.3412 -> 1.3412 in token units, rounds to 1.3
[19] '2.3 pp' (line 31) -> MATCH
    register a1_ff_chained_peak: value=2.2946 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> path.csv fannie_freddie max (2009Q4)
    recompute: path.csv max(fannie_freddie) = 2.2946 -> 2.2946 in token units, rounds to 2.3
[20] '1.4 pp' (line 31) -> MATCH
    1 row(s) pinned by locations research/a1_gfc_decomposition/README.md:31
    register a1_ff_chained_2011q4: value=1.3992 pp, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065110 FL403065120 FL413065143 FL413065123 FL154104015 FL153165105 FL153166000 FL893065105; computation: research/a1_gfc_decomposition/decompose.py -> path.csv fannie_freddie 2011Q4
    recompute: path.csv [2011Q4] fannie_freddie = 1.3992 -> 1.3992 in token units, rounds to 1.4
[21] '$20B' (line 53) -> MISMATCH
    register a1_other_gse_bound: value=19.4750 usd_bn, period 2007Q4-2011Q4, vintage z1:2026-09-11, validation UNVERIFIED
    series FL403065105 FL403065110 FL403065120 FL403065130; computation: research/a1_gfc_decomposition/decompose.py -> decomposition.csv (max of 2007Q4, 2011Q4)
    recompute: none (no results.json key in computation; decomposition.csv: cannot identify one value column in '(max of 2007Q4, 2011Q4)')
    - register value 19.4750 usd_bn = 19.4750 in token units, rounds to 19 not 20 (off by 1)
[22] '6.1 pp' (line 54) -> AMBIGUOUS
    candidate gfc_counterfactual_pp: Had private debt stayed at its 2007Q4 level the public share would have risen 6.1 pp, not 13.1. value=6.11 pp 2007Q4-2011Q4 at analysis/findings.md:12
    candidate a1_ginnie_own_pp: Ginnie Mae pools' own share of in-scope debt rose 6.1 pp, 2007Q4-2011Q4. value=6.1191 pp 2007Q4-2011Q4 at research/a1_gfc_decomposition/README.md:27
    Several rows print this token; which claim is meant?
SUMMARY MATCH 17, MISMATCH 1, UNTRACED 0, AMBIGUOUS 1, NOT RECOMPUTABLE 3 (of 22 numbers)
(exit 1)
```

Reading example 4: the three `NOT RECOMPUTABLE` rows (`a1_*_own_pp`) point at `own_share_change.csv` with no column or key in `computation`; the `AMBIGUOUS` `6.1 pp` is on a line (54) that no row lists in `locations`, so two rows print the same token; the `MISMATCH` `$20B` is a bound ("at most $20B") against a register value of 19.475. All three are register tidy-ups for a human, not things this skill fixes.
