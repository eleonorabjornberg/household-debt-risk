> **Claude draft.** Claude collected these questions from the three track sessions and wrote the recommendations. The decisions are Eleonora's. Each answer goes into PLAN.md "Decisions taken" under her name.

**Status:** decided by Eleonora 2026-11-04: every recommendation accepted (PLAN.md "Decisions taken").

# Open questions from the tracks, 2026-11-04

Answer each item by its ID ("Q1 b", "Q-C1.4 a"), or reply "accept all" to take every recommendation. Sources: `tracks/analysis.md`, `tracks/markets.md` and `tracks/infra.md` on the track branches.

## Analysis track (A2, A5, A8)

| ID | Question | Options | Recommendation | Unblocks |
|---|---|---|---|---|
| Q1 | A2: what counts as credit risk "transferred" off the GSEs? | (a) bounds only; (b) outstanding CRT and MI from 10-K/10-Q filings; (c) runoff estimate; (d) expected loss | **(b)**, with (a) as the check; (d) waits for A6. (b) needs `www.sec.gov` and `efts.sec.gov` allowed | A2 net series |
| Q2 | A2: how to treat private mortgage insurance | separate line, or netted into the transfer | **Separate line** | A2 net series |
| Q3 | A2: Ginnie Mae pools | gross, or net of FHA/VA guarantees | **Keep gross** and say so in the note | A2 |
| Q4 | A5: how to link borrowers to holders | (a)–(d) in `tracks/analysis.md` | **(c)** as a labelled estimate, with (b) shown beside it | A5 link |
| Q5 | A8: which metric to compare across countries | (a) who holds the debt; (b) who bears the risk; (c) both | **(c)**, with (b) as the headline | A8 (also needs the hosts below) |

## Markets track (B1, C1)

| ID | Question | Recommendation |
|---|---|---|
| Q-B1 | Accept the B1 spread proxy as built? | **(a) accept as is.** Add a guarantee-fee control (b) only if B1 feeds A6 |
| Q-C1.1 | Target vintage for the nowcast | **(c)**, with the first release as the primary target |
| Q-C1.2 | Indicators | **(b) now**; (c) later if `www.freddiemac.com` and `www.fanniemae.com` are allowed |
| Q-C1.3 | When to nowcast | **Monthly** |
| Q-C1.4 | Model | **(c)**, with the accounting bridge as the primary model |
| Q-C1.5 | Benchmarks | **All three**; the no-change forecast is the headline benchmark |
| Q-C1.6 | Metrics and holdout | RMSE and MAE; Diebold–Mariano and Clark–West tests; holdout 2024Q3–2026Q2; 2b from 2015Q1, plus 2a from 2010Q2. **Must agree with the frozen C2 protocol** (`scoring-protocol.md`, 192d60c); any conflict goes in as a dated deviation there, not a silent change |
| Q-C1.7 | Forecast the level or the share? | **The headline share** |
| Q-C1.8 | Seasonal adjustment | **NSA** (not seasonally adjusted) |
| Q-C1.9 | How to define a change | **(a)**, computed within the same vintage |

## Infra track (F2, F4)

| ID | Question | Recommendation | Why |
|---|---|---|---|
| F2-1 | Pin FRED series to a fixed vintage? | **(a) yes, via ALFRED `realtime_end`** | Published values already drift between pulls (Fed MBS weekly $1.90T → $1.88T; runoff $845B → $857B) |
| F2-2 | Add `DATABASE_URL_READONLY` as a GitHub Actions secret? | **Optional.** It turns on the live DB tests in CI. You would add it yourself in the GitHub settings | — |
| F4-1 | NY Fed data in the public snapshot | **(a) redistribute under the NY Fed's terms, with their attribution** | — |
| F4-2 | API exposure | **A now, B later, never C** | — |
| F4-3 | Archive old vintages? | **Yes** | Needed for the C2 real-time check |
