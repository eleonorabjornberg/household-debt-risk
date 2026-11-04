# B3: Scenario engine, who bears the losses

> **Claude draft, not the author's text.** The engine and its tests are built and checked. Its scenario presets follow Eleonora's Q-B3 decision (2026-11-04). The DFAST preset is built and labelled a proxy; the 2008–12 replay is still to come. The design is Claude's proposal ([`METHOD.md`](METHOD.md)).

**PLAN task B3. Status: engine, tests and the DFAST preset done; the 2008–12 replay and the in-app version are to come.**

## What it does
- **Inputs.** Loss parameters for each loan class (mortgages, federal student loans, other consumer credit): a cumulative default rate, a loss given default, and a quarterly timing vector.
- **Outputs.** Losses by quarter, split public and private by who holds each exposure.
- **Optional transfer.** A share of the losses on GSE and agency-pool mortgages can be moved to private hands, up to a cap. That stands for credit-risk transfer and mortgage insurance; the cap is meant to come from A2's net-exposure bounds.
- **Exposures.** `exposures.json` holds the latest Z.1 balances (2026Q2, release 2026-09-11) by holder bucket, at catalog level, so its public share reproduces the project's 56.4% (test).

## Checks
- **`test_engine.py`.** Public + private = total in every quarter. The total equals balance × default rate × severity. A zero default rate or zero severity gives zero loss. Losses are linear in the default rate. The transfer conserves the total and respects its cap. Invalid input is refused.
- **`engine.mjs`** is the browser version, with no dependencies. `test_engine.mjs` checks it against the Python core on five fixed cases (`fixtures/cases.json`) to 1e-9. Pytest runs that check whenever Node is installed.

## DFAST preset (Q-B3, decided by Eleonora 2026-11-04): a recession case, labelled a proxy

**What it is.** The Fed's 2026 stress test gives projected loss rates by loan type for the largest banks under its severely adverse scenario, over the nine quarters 2026Q1–2028Q1 (`sources.md`). The preset applies those rates to **every** holder's balances at 2026Q2. That is a proxy: GSE, FHA/VA and federal books are not bank portfolios.
- **Mortgages** take the first-lien rate, 1.5%. Junior liens and HELOCs, at 3.2%, are part of Z.1's mortgages but are not separated, so mortgage losses are understated.
- **Other consumer credit** takes a blend: cards at 17.1% and "other consumer" at 7.3%, weighted by Z.1's revolving share (37%). The blended rate is 10.9%.
- **Federal student loans** are not in DFAST, so the main preset leaves them out. A variant gives them the "other consumer" rate, a weak proxy.

| Preset | Total losses | Public | Private | Public share of losses |
|---|---|---|---|---|
| DFAST proxy (federal student loans absent) | $595B | $137B | $457B | 23% |
| DFAST proxy, federal student loans at 7.3% (weak proxy) | $712B | $255B | $457B | 36% |

**Reading (Claude draft).** In this proxy recession the public sector bears 23% of losses while holding 56.4% of the debt. Its book is mostly mortgages, which have low stressed loss rates, and the high-loss consumer credit is privately held. Counting federal student loans at the weak proxy rate raises the public share of losses to 36%. These are ESTIMATES under a proxy. No transfer to CRT or mortgage-insurance cover is applied (the cap is 0); A2's bounds would lower the public figure.

## Not done here
- **2008–12 replay preset** (Q-B3 (c), second family): not yet built.
- **In-app version.** `atlas/` is site code; the coordinator owns it. A proposal is in `tracks/markets.md`, and only preview deployments would be made.

## Use
```bash
uv run --project pipeline python research/b3_scenarios/engine.py                       # exposures + fixed cases
uv run --project pipeline python research/b3_scenarios/engine.py --params my.json      # your own parameters
uv run --project pipeline pytest -q research/b3_scenarios
```
