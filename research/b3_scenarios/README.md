# B3: Scenario engine, who bears the losses

> **Claude draft, not the author's text.** The engine and its tests are built and checked. Its scenario presets follow Eleonora's Q-B3 decision (2026-11-04). The DFAST preset and the 2008–12 replay are built, both labelled proxies. The design is Claude's proposal ([`METHOD.md`](METHOD.md)).

**PLAN task B3. Status: engine, tests and both preset families done (proxies); the in-app version is the coordinator's site work.**

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

**Reading (Claude draft).** In this proxy recession the public sector bears 23% of losses.
- **Like for like,** that compares with a public share of holdings of 52.4% once federal student loans are excluded, as they are from the losses (56.4% with them).
- **Why the gap:** the public book is mostly mortgages, which have low stressed loss rates, while the high-loss consumer credit is privately held.
- **With federal student loans** at the weak proxy rate, the public share of losses rises to 36%.

These are ESTIMATES under a proxy, and three biases are known:
- **Junior liens.** Using the first-lien rate for every mortgage understates junior-lien and HELOC losses, which banks mostly hold. So the public share of losses is biased **up**.
- **FFEL loans.** Z.1's "private" student loans include federally guaranteed FFEL loans held by private lenders, whose credit risk is largely federal. The public share is biased **down** on that count. A split needs ED data, and ED is unreachable.
- **No transfer.** No CRT or mortgage-insurance cover is applied (the cap is 0); A2's bounds would lower the public figure.

## 2008–12 replay preset (Q-B3 (c), second family): labelled a proxy

**What it is.** The banks' realised net charge-off rates, quarter by quarter, from 2008Q1 to 2012Q4. They come from the Fed's charge-off release for all commercial banks, via FRED: `CORSFRMACBS` (single-family mortgages), `CORCCACBS` (cards), `COROCLACBS` (other consumer). The release defines them as "net charge-offs (gross charge-offs minus recoveries) during a quarter divided by the average level of its loans outstanding", multiplied by 400 to annualise (`sources.md`).
- Each quarter's loss is therefore rate ÷ 400, and the twenty-quarter path sets the timing.
- Over the window, cumulative charge-offs were 8.7% for mortgages and 18.9% for other consumer credit (cards and other consumer, weighted as in the DFAST preset).
- Federal student loans are absent: there is no bank series for them.

| Preset | Total losses | Public | Private | Public share of losses |
|---|---|---|---|---|
| 2008–12 replay, bank charge-offs (proxy) | $1,886B | $801B | $1,085B | 42% |

**Limits (Claude draft).**
- **Horizon.** The cumulative figure sums twenty quarterly loss rates, each a share of that quarter's average balance, and applies the sum to today's balances. It is an approximation, not a share of a starting balance, and it covers five years where DFAST covers nine quarters, so the two presets differ in horizon as well as severity.
- **Upper bound.** The public bucket includes Ginnie (FHA, VA) pools and the GSEs. Bank loss rates on those books likely overstate their losses, so the 42% public share is probably an upper bound.
- **Whose crisis.** This replays the banks' crisis, not the GSEs'. Bank mortgage books in 2008–12 included subprime and option-ARM loans that the GSEs did not guarantee, so applying bank charge-offs to the GSE book likely overstates public losses. The GSEs' own realised losses (from their 10-Ks) would be the better source for that book, and are a possible refinement. The figures apply one historical path to today's balances, so they are ESTIMATES.

## Not done here
- **2008–12 replay preset** (Q-B3 (c), second family): not yet built.
- **In-app version.** `atlas/` is site code; the coordinator owns it. A proposal is in `tracks/markets.md`, and only preview deployments would be made.

## Use
```bash
uv run --project pipeline python research/b3_scenarios/engine.py                       # exposures + fixed cases
uv run --project pipeline python research/b3_scenarios/engine.py --params my.json      # your own parameters
uv run --project pipeline pytest -q research/b3_scenarios
```
