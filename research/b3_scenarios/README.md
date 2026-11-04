# B3: Scenario engine, who bears the losses

> **Claude draft, not the author's text.** The engine and its tests are built and checked. No scenario has been run with real loss parameters, because each preset needs a primary source and Eleonora's sign-off (Q-B3 in `tracks/markets.md`). The design is Claude's proposal ([`METHOD.md`](METHOD.md)).

**PLAN task B3. Status: engine and tests done; presets and the in-app version wait on Q-B3 and the coordinator.**

## What it does
- **Inputs.** Loss parameters for each loan class (mortgages, federal student loans, other consumer credit): a cumulative default rate, a loss given default, and a quarterly timing vector.
- **Outputs.** Losses by quarter, split public and private by who holds each exposure.
- **Optional transfer.** A share of the losses on GSE and agency-pool mortgages can be moved to private hands, up to a cap. That stands for credit-risk transfer and mortgage insurance; the cap is meant to come from A2's net-exposure bounds.
- **Exposures.** `exposures.json` holds the latest Z.1 balances (2026Q2, release 2026-09-11) by holder bucket, at catalog level, so its public share reproduces the project's 56.4% (test).

## Checks
- **`test_engine.py`.** Public + private = total in every quarter. The total equals balance × default rate × severity. A zero default rate or zero severity gives zero loss. Losses are linear in the default rate. The transfer conserves the total and respects its cap. Invalid input is refused.
- **`engine.mjs`** is the browser version, with no dependencies. `test_engine.mjs` checks it against the Python core on five fixed cases (`fixtures/cases.json`) to 1e-9. Pytest runs that check whenever Node is installed.

## Not done here
- **Presets.** A recession case, a 2008–12 replay and so on would each need sourced parameters. Candidate free sources are in Q-B3.
- **In-app version.** `atlas/` is site code; the coordinator owns it. A proposal is in `tracks/markets.md`, and only preview deployments would be made.

## Use
```bash
uv run --project pipeline python research/b3_scenarios/engine.py                       # exposures + fixed cases
uv run --project pipeline python research/b3_scenarios/engine.py --params my.json      # your own parameters
uv run --project pipeline pytest -q research/b3_scenarios
```
