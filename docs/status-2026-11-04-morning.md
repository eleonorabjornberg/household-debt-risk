# Morning status, 2026-11-04

> **Superseded.** A point-in-time snapshot from 2026-11-04, kept as history. For the current state see `PLAN.md` and `docs/challenge-readiness.md`.

> Written by Claude (coordinator) for Eleonora. This is a status report, not analysis text. Every decision below is open and waits for you; nothing here has been decided on your behalf.

Coordinator branch `claude/sweet-gates-avwrcs`, HEAD `aba93f0` at the time of writing. The three tracks are merged up to their last pushes and are idle. Register: 352 rows, and the hook checks pass. Production (Vercel, Supabase) was not touched. The C2 holdout (2023Q3–2026Q2) is still sealed.

## What got done overnight

### Analysis track (`claude/track-analysis`, last merged `cf6972b`)
| Task | State | Headline (development results, for review) |
|---|---|---|
| A2, A5, A8 | ready for review | merged earlier in the night |
| A3 pre-1952 | ready for review | Z.1 annual data for 1945–51 joins the quarterly series exactly. Historical Statistics covers 1925–44 and differs from Z.1 by at most 0.50 pp where the two overlap. Peak in 1935: 14.1% (15.0% when scaled to Z.1). The 1933–1970 policy timeline was checked against the statutes. |
| A4 structural breaks | ready for review | One break, at 1966Q1 (CI 1952Q2–1967Q1). No evidence of a break at any of the five 2008–10 dates. Placebo 51–91%. Robust across vintages. The quant-reviewer caught a sign error in the Bai (1997) interval, which is now fixed. The deviations are listed in `docs/decisions/breaks.md`. Simulated critical values are themselves a deviation; they could not be cross-checked because R is not available. |
| A7 synthetic control | waiting on Q8 | Prereg addendum committed |
| A6 | not started | Needs Q6 and a CBO replication; `cbo.gov` returned 403 |

### Markets track (`claude/track-markets`, last merged `e2a856f`)
| Task | State | Headline |
|---|---|---|
| B2 CRT pricing | ready for review | Uses the FHFA December 2016 tables as a fixture |
| B3 scenario engine | core ready | Python and JS twins match on 5 cases. The presets wait on Q-B3. |
| B4 | blocked | Needs the B3 presets |
| C1 nowcast | holdout sealed | Q-C1c and Q-C1b below |
| C2 forecast | development run done | RMSE relative to no-change, at h=1/4/8: Z-DIR 0.75/0.71/0.79, Z-DAMP 0.73/0.70/0.81, AR 0.76/0.70/0.79. Only h=1 vs no-change survives Holm, and that result does not hold up under the post-hoc Bartlett lag-8 p-values. No model beats AR. Coverage falls short at h=8. The quant review (q17–q24) found one blocker and four major issues, all fixed; the scores did not change. |
| C3 | not started | Waits on the C2 decisions and on `SEC_USER_AGENT` |

### Infra track (`claude/track-infra`, last merged `0eb373e`, CI green)
- **F3:** release workflow.
- **D3:** memo skill, plus three example memos labelled as Claude drafts.
- **D7:** plugin.
- **D5:** the MCP server now falls back to the committed snapshots when the DB is unreachable. It says so in each answer. Setting `HOUSEHOLD_CREDIT_REQUIRE_DB=1` turns the fallback off.
- **E2:** pre-registration drafted, not frozen.
- **E3:** blocked on E1 and E2.

## Decisions waiting for you

Each item names the file where the options and the track's recommendation are written out.

**Analysis (`tracks/analysis.md`)**
1. **Q6:** set `SEC_USER_AGENT` in the cloud environment settings. Every SEC/EDGAR fetch is off until it is set. This blocks A6 and C3.
2. **Q7:** German public banks (A8 scope).
3. **Q8:** A7 donor-pool design.
4. **A7 addendum flags** (checklist item 3 of the addendum): the S1 weekly alignment fix, and making the constant-mean model primary.
5. **A4:** accept or reject the deviations listed in `docs/decisions/breaks.md`.

**Markets (`tracks/markets.md`, `research/c2_forecast/SPECS.md`)**

6. **C2 test ordering deviation.** Status: PROPOSED.
7. **C2 seasonal-naive benchmark in the Holm family.** Status: PROPOSED (the stricter reading).
8. **C2 placebo.** Options: (a) demean; (b) compare against drift; (c) record it as a failure. These options were written down *after* the result was seen, so treat them with that in mind.
9. **Q-B2:** the price measure. Recommendation: (a)+(c), with 2017–23 prices from (c) if those hosts are allowed, otherwise (b).
10. **Q-B3:** the scenario presets. Recommendation: (c), starting with DFAST.
11. **Q-C1c:** recommendation (b), run the C1 holdout together with C2's.
12. **Q-C1b (later):** pre-register a 2c run with Freddie and Ginnie. Recommendation: (a).

**Infra (`tracks/infra.md`)**

13. **F3-1:** `refresh.yml` still loads production on a schedule. Recommendation: (a) drop the schedule and default `load` to false. Not applied.
14. **F3-2:** who drafts the release notes. Recommendation: (a), a Claude session runs the skill.
15. **E2-1:** prereg choices CHOICE-1 to CHOICE-9 in `docs/decisions/e2-prereg.md`. E2 is frozen only after you choose.
16. **D7-1:** plugin icon and distribution. Recommendation: repo marketplace only.
17. **F2-2 (optional):** you said you would add `DATABASE_URL_READONLY` yourself.
18. **GitHub settings:** turn on "Allow GitHub Actions to create and approve pull requests", and confirm the `FRED_API_KEY` secret.
19. **Cost approvals:** D6, E1 and E4 need API spend or an API key.

**Copy review (preview deployments only)**

20. **2008 copy revision.** The A1 Shapley split is now used on the story site, Hot Potato, the recommendation draft and the findings: private retreat 6.9 pts, public growth 6.2 pts, Fannie and Freddie 1.2 pts.
21. **Nav links and the `/sources` and `/data` page intros** added by infra.
22. **`public_share_2001q1` / `_2005q1`:** their only location is an unrendered fact. Keep, render, or drop?

## Blocked hosts (seen from the cloud container)
- **SEC EDGAR** (`www.sec.gov`, `efts.sec.gov`): allowlisted, but no request goes out until `SEC_USER_AGENT` is set (Q6).
- **Fannie Mae hosts** and **`crt.freddiemac.com`:** refused by the sites themselves.
- **`cbo.gov`:** 403.
- **Census, USMI, ALFRED and the foreign central banks:** listed in PLAN prerequisites.

## Slips to know about
- Commit `174354e` carries the markets session's trailer instead of the coordinator's. Fixing it needs a force push, which was refused, so it stays.
- Before 04:40 UTC, the analysis track sent one EDGAR request with your address exported in its shell. I stopped it, and SEC fetches stay off until `SEC_USER_AGENT` is set. Your address is not in any commit.
- All other errors and who caught them are in `docs/building-with-claude.md`.

## Cost (approximate, from session usage)
| Session | USD |
|---|---|
| Coordinator | 46.3 |
| Analysis | 47.5 |
| Markets | 34.9 |
| Infra | 28.9 |
| **Total** | **≈157.6** |

## Next, once you have decided
- **Analysis:** A7 can run after Q8. A6 can start after Q6.
- **Markets:** the C1 and C2 holdouts can be unsealed after items 6–8 and 11. B3 presets and B4 can follow after Q-B3.
- **Infra:** E2 can be frozen after E2-1, then E3.
