# B3 method note: scenario engine (written before the engine)

> **Claude draft, not the author's text.** A proposed design for Eleonora to accept or change. Scenario values (default rates, severities, timing) are not chosen here. Every preset needs a primary source and her sign-off (Q-B3 in `tracks/markets.md`).

PLAN task B3: "Scenario engine: default rate, loss severity, recovery path → losses split public vs private; interactive in the app." Acceptance:
- a Python core with unit tests (losses sum to total; public + private = total; zero default → zero loss);
- a browser version that matches the Python core on fixed cases;
- preview deployment only.

## Exposures
- **Holdings.** Household 1–4 family mortgages and consumer credit by holder bucket, at the latest Z.1 quarter (release 2026-09-11). They are computed at catalog level, as `validation/run.py` does: mortgage holders apportioned with FL153165105 / FL893065105, buckets from `pipeline/series_catalog.yaml`.
- **Federal student loans.** Kept as their own exposure (FL313066220), because their loss behaviour differs from other consumer credit.
- **No-cell rule.** Exposures carry no loss parameters of their own. Parameters attach to loan classes: `mortgage`, `student_federal`, `consumer_other`.

## Losses
For each exposure i in loan class c:
- **Loss:** L_i = B_i × PD_c × LGD_c, where B is the balance, PD the cumulative default rate over the scenario, and LGD the loss given default net of recoveries.
- **Timing:** the loss is spread over quarters by a timing vector w_c (non-negative, summing to 1). The default is all in one quarter; the vector is a parameter.
- **Side:** a loss is public or private by its holder's bucket (`public: true` buckets).

## Optional transfer (ties to A2)
- **What moves.** A share τ of the losses on the GSE and agency-pool mortgage exposures is moved from the public to the private side, standing for CRT and mortgage-insurance cover.
- **Cap.** The amount moved is capped at C, the cover available ($). It defaults to 0, so nothing moves. A2's net-exposure bounds are the intended source for C. They are an input, not built in, because A2 is still in progress.
- **Totals.** The transfer moves losses; it never creates or removes them.

## Invariants (tests, Python and JavaScript)
1. Public + private = total, for every quarter and in sum.
2. The sum over quarters equals B × PD × LGD.
3. PD = 0 or LGD = 0 gives zero loss.
4. Losses are linear in PD and in LGD.
5. The transfer conserves the total and never exceeds C or the GSE-side loss.
6. Invalid input is refused: PD or LGD outside [0, 1], timing vectors that don't sum to 1, negative balances.

## Browser version
`engine.mjs`, a dependency-free ES module with the same functions. `fixtures/cases.json` holds fixed cases written by the Python core. A Node test (run from pytest when `node` is present) asserts that both agree to 1e-9. Putting it into the app (`atlas/`) is site work for the coordinator, proposed in `tracks/markets.md`. No deployment is done from this track.

## Changes after results
None yet.
