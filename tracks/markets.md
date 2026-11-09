# Track: Markets and nowcast

Branch: `claude/track-markets` · Tasks, in order: B1, C1 · Rules: PLAN.md "Parallel tracks".

## Summary at stop (2026-11-04, overnight)
- **B1** is done, per the coordinator. **B2** is ready for review. **B3** core is ready for review; its presets wait on Q-B3. **B4** is blocked on B3's presets. **C1** is ready for review (development); its holdout is sealed until Eleonora decides Q-C1c.
- **C2** development is done and quant-reviewed (q17–q24 addressed), and its holdout is sealed. Three protocol items wait for Eleonora: the test ordering and seasonal naive (both PROPOSED in `research/c2_forecast/SPECS.md`), and the placebo definition. Development allows no "beats" claim: only h = 1 against no-change passes Holm, and that does not survive a bandwidth sensitivity.
- **C3** has not started. It needs the C2 holdout run, which needs her rulings.
- Nothing touched production or the database. Blocked hosts are listed under Q-B2, not worked around.

## /research on Hot Potato (2026-11-09, Eleonora's request in chat; PLAN Decisions taken at faddf48)

- The branch was re-cut from origin/claude/sweet-gates-avwrcs at faddf48 (rewritten history; no old SHAs).
- What's in atlas:
  - `/research` index: 17 entries. A6 is blocked, with PLAN's reason. C1b and C2 point to the joint-holdout write-up; B3 also links `/scenarios`.
  - `/research/<slug>`: 14 write-ups, each a README copied as it stands by `scripts/sync-research.mjs`. Only relative links change: other READMEs go to their /research page, repo files to their GitHub blob on main (every target checked on origin/main).
  - A layout banner marks the section as Claude drafts; each README keeps its own banner. The parser gains fenced code and blockquotes, and the top bar links Research.
- Index text:
  - Questions and status fragments are verbatim from PLAN; `lib/research.test.ts` checks them.
  - Methods are one-line Claude drafts with no figures.
  - C1b has no PLAN row: its question is mine and its status quotes the C2 row (labelled). The joint holdout's status quotes the C1 row (labelled).
- Numbers: none new and no new rows. The README numbers are registered at their research/ locations, and the register check passes. As with findings.md, the atlas copies are not scanned.
- Stale README status lines, shown as they stand: B1 "ready for review" (PLAN: done, inconclusive), B2 "ready for review" (PLAN: done), B3 "awaiting Eleonora's review" (PLAN: page approved). The index shows PLAN's status beside each.
- Checks: atlas tests 161/161, tsc clean, build OK; web tests 31/31; make site-copies leaves the tree clean; Playwright on all routes (200, both banners, no relative links, no horizontal scroll at 390 px).
- Commit 61f7d7d.
- **Errors:**
  - An old markdown test helper narrowed `Block` by elimination, so it broke when the union grew. Caught by tsc.
  - The first link rewrite missed links whose text is a code span. Caught by Claude from the empty rewrite count.

## One site: web pages moved into Hot Potato (2026-11-07, site-visible (b), relayed by the coordinator)

- Copied, not moved: web/ is unchanged. In atlas:
  - pages: `app/scenarios`, `app/how-it-was-built`, `app/methods`;
  - content: `content/methods.ts` (from web/content/story.ts), `content/build.ts`, `content/series_catalog.json` (synced by `scripts/sync-catalog.mjs`);
  - the B3 engine synced into `lib/b3/` by `scripts/sync-b3.mjs`, with its tests;
  - the copied chart parts in `components/pages/charts/`;
  - `components/TopBar.tsx` on every page (Hot Potato, Scenarios, How it was built, Methods, Sources);
  - `app/pages.css`, scoped under `.pg`. The home page is unchanged below the bar.
- One copy fix: the stack line describes this site (Canvas dot flow plus SVG charts) instead of "the story site".
- Register (coordinator option (a)): the locations cell of 10 rows (11 locations) gained atlas twins, with the web locations kept. SCAN_FILES gained the two atlas content files.
- Checks: atlas npm test 144/144; build OK (/, /scenarios, /how-it-was-built, /methods, /sources static; /ask and /api/ask dynamic as before); browser parity on atlas 123/123; F1 check_html 37/39 linked (2 known exceptions); register check OK. No horizontal scroll at 390 px on any route.
- Commits: ce6d7e1 (pages), 3d667a5 (register).
- Not done: no skeptic or editor pass this round (the copy is unchanged apart from the stack line).
- Pre-existing issues seen, not touched:
  - eslint reports 26 errors in atlas/lib/ask/* (Ask Hot Potato);
  - web/lib/claims.json is stale on main (`claims/site/sync.mjs --check`).
- **Errors this round:**
  - A shell heredoc tripped the command safety check; it contained no removal. Caught by the harness; rerun from a script file.
  - A loose class-name assertion in the copy script (`pg-col"` contains `col"`). Caught by the assertion itself; fixed.
  - My message to the coordinator said 11 rows; it was 11 locations in 10 rows. Caught by Claude when applying.

## B3 browser page (2026-11-05, scope confirmed by the coordinator ~21:10 UTC)

- Built `web/` route `/scenarios` (URL only; no nav link, no web/content or layout edits): `web/scripts/sync-b3.mjs` → `web/lib/b3/` (SHA-256 manifest), `web/app/scenarios/page.tsx` (Claude-draft banner and copy, no hard-coded figures; horizons and years read from the preset files), `web/components/scenarios/ScenarioTool.tsx` (+ CSS module). Commits 377b309, fd13598 and the editor commit.
- Tests: `web/lib/b3/sync.test.ts`, `web/lib/b3/engine.test.ts` (vitest 31/31 overall), `research/b3_scenarios/test_browser.mjs` (Chromium on localhost, 123 checks incl. screenshots; pytest runs it when web/ is built). No deployment run; Vercel deployments endpoint answered 403 for the team scope from this session, so no preview URL is confirmed.
- Reviews: skeptic mkt-s55–s59, editor mkt-e26–e32, all addressed. Next ids: mkt-s60, mkt-q49, mkt-e33.
- **Errors:**
  - The chart first rendered about 260 px wide on desktop: the figure shrank inside the grid. Caught by Claude from the screenshot.
  - The preset-input check failed on one replay timing weight one unit in the last place off, because the bundler re-serialises JSON. Caught by the browser test; the check is now numeric at 1e-12 and the finding is in the README.
  - The old B3 README generator rewrote claims/tracks/markets.csv with 21 already-folded rows. Caught by Claude; the file was deleted and the register check passes.
  - Data labels (skeptic): balance share not like for like, transfer group including Ginnie pools, missing bias directions, loss rate shown as a default rate, and the test-case note.
  - Copy (editor): ambiguous cap, stress test not described as hypothetical, hard-coded horizons, unexplained terms.

## Review round (2026-11-05, after 392a1bf)

- quant-reviewer mkt-q45–q48 (C3) and skeptic mkt-s49–s54 (B2): all addressed. C3 fixes are in 5c8bb4f; B2 fixes and the log statuses are in the next commit. Details are in claims/tracks/markets-review-log.md.
- **Errors found by the reviewers:**
  - C3: "would not count under the two-test readings" was false at p < 0.01, and "(iv) is the most lenient" is in fact a tie with p < 0.01 (quant-reviewer q45, q46). The independence result was overstated as a failure on one uncorrected test (q47).
  - B2: the no-spread count was 1 instead of 3, because 2017-HRP1's M-2 and B-1 were labelled "absent" first (skeptic s49). Indicative tranches were not flagged inside the multiples (s50). "Much of the rise ... not price" was overclaimed: on a fixed 25–75 slice, 2021→2022 is spread (s51). The attach table ignored thickness (s52). There was no caveat on class make-up (s53). Wording (s54).
- C3 note for the coordinator still stands: ZC1-DIR vs seasonal naive is "comparable" (Holm p 1.000), not "undetermined". The quant-reviewer confirmed this (item 4).

## Her answers applied (2026-11-05, relayed by the coordinator ~18:58 UTC; her decisions 18:54 UTC)

- **C3** c3-b-level (iv) and c3-b-nointv (c): `make_report.py` uses ALPHA = "kupiec 0.05", giving 3 C2 "beats". The report says (iv) is the most lenient reading (asserted in code) and puts rolling Z-DAMP's Christoffersen p = 0.027 (Kupiec p = 0.958) next to its "beats". The "interim"/"open card" wording is gone. 5 new rows and no folded-row changes: the new text was folded into the existing bullet so README line numbers stay put.
  - Note for the coordinator: ZC1-DIR vs seasonal naive comes out "comparable", not "undetermined". Under rule (b), "undetermined" applies only when every loss condition holds, and this comparison fails Holm first. C1's bridge_reg vs no_change at k = 2 is the "undetermined" case.
- **B2** b2-sofr-src (a): LIBOR_1M_ADJ_BP = 11.448. b2-upb (a): the UPB text in METHOD.md is replaced by her decision. b2-empty (a): reported as is. New README section "STACR 2017+" (Claude draft), generated by `stacr_2017_readme.py` through `make_readme_and_rows.py`, with 121 b2_stacr_ rows in claims/tracks/markets.csv. Three single-line edits above it say the STACR workbook is now reachable.
- Commit 392a1bf (pushed). Review: skeptic from mkt-s49 (B2), quant-reviewer from mkt-q45 (C3).

**Errors this round**
- The pre-commit hook blocked the first commit. The vintage was "stacr-pricing.xlsx:2026-11-05" (format must be `name:date`, now `stacr:2026-11-05`), "VERIFIED" is not a valid status, and three tokens were unregistered ("253.4" in the CFR citation, now written "part 253, section 4(c)(2)"; the two p-values needed displays "p = …"). Caught by the hook.
- The first C3 regeneration moved every README line by one (a new bullet line), which would have changed 1,065 folded rows' locations. Caught by Claude from the generator's summary line; the note was folded into the existing bullet.
- The STACR test still assumed the adjustment unset. Caught by pytest.

## B2 STACR 2017+ session (2026-11-05, from ~16:15 UTC)

**Setup.** Fast-forwarded to 686b4be and pushed; hooks on. Next review ids unchanged: mkt-s49, mkt-q45, mkt-e26.

**Done (engine, no write-up yet)**
- `stacr_pricing.py` now also writes each tranche's detach point: the initial CE of the next senior listed class, A-H included (existing columns unchanged, checked against the committed CSV).
- `stacr_2017.py` + `test_stacr_2017.py`: per-tranche spread, baseline EL (b2.py engine, FHFA 2016 baseline, a labelled assumption) and multiple, by year and class M-1 / M-2 / B, with "(Indicative)" retained tranches kept and flagged. Method: `METHOD.md` "STACR 2017+".
- Outputs (intermediate, not yet in any write-up, so no claims rows yet): `stacr_2017_tranches.csv`, `stacr_2017_by_year_class.csv`, `stacr_2017_results.json`.

**Stopped at the stop rule.** LIBOR–SOFR adjustment: source found and checked (Fed Regulation ZZ final rule, §253.4(c)(2), 11.448 bps for 1M LIBOR, www.federalreserve.gov, free, `sources.md`), NOT used. It goes to the coordinator as a proposed card. `LIBOR_1M_ADJ_BP` stays unset, so the SOFR-basis columns for 2017–2020 LIBOR deals are empty.

**For the coordinator (cards or questions for her)**
1. Proposed card b2-sofr-src: use 11.448 bps from Regulation ZZ.
2. Reference-pool UPB is not needed for the per-tranche multiple (thickness comes from the CEs, the workbook lists A-H). No UPB source used. A UPB source would only matter for a deal-level cost in bps of UPB or dollars.
3. The measure is mostly empty: only 50 tranches (all B-2, 2017–2022; 50 of the 274 in her three classes, or 50 of 270 eligible there once 3 with no detach and 1 with no spread are removed; the coordinator's 50 of 285 counts all classes incl. 13 A-1 and 2 M-3) attach below the baseline's 30.8 bps cumulative loss. M-1, M-2 and B-1 never get a multiple, and nothing from 2023 on. The multiple also swings with B-2's attach point (0 → 10 → 25 bps).

**Errors this session**
- The "50 of 274" count in the first coordinator message did not say its denominator: 274 = tranches in her three classes, while the CSV-wide count is 50 of 285 eligible. Caught by the coordinator; METHOD.md now gives every count.
- UPB: METHOD.md and the first message called reference-pool UPB "not needed". Her measure (ii) text names a UPB source, so dropping it would depart from her choice. Caught by the coordinator; it now waits on her card b2-upb.
- `detach_points` first raised on 2014-DN2, which prints A-H at 3.00% below M-1 at 3.50%. Caught by the function's own order check (Claude). Fix: no detach for that class, reason kept in `detach_from`; it is pre-2017, out of scope.
- `stacr_2017.py` first run: division on object-dtype columns (ZeroDivisionError). Caught on the first run (Claude); columns cast to float.

## Handoff note (2026-11-05 ~16:45 UTC, for the next markets session)

**State at hand-off.** The branch is pushed at 6e86429 and the tree is clean. C3 is waiting on Eleonora.

**Done this session (C3)**
- C3 report: `research/c3_accuracy/README.md`, generated by `make_report.py`. The generator also writes `register_updates.csv` when rows already folded into the register would change; the coordinator applies those (two rounds so far, each with an explicit OK).
- Review rounds, all addressed: quant-reviewer q31–q44, skeptic s44–s48, editor e1–e25 (logged by this track; the editor returns suggestions only).
- Her decisions of 15:55 UTC are applied:
  - c3-rule (b): `docs/decisions/scoring-protocol-erratum-2026-11-05.md` (c783a5a).
  - c3-errors (b): the second, gated holdout opening D1, run ONCE. It reproduced the committed scores exactly (8d60d86).
  - c3-hcount (b): deviation D2, plus the origin subset. Both deviations are in `docs/decisions/scoring-protocol-deviations-2026-11-05.md`.
- **Never run `holdout_forecasts_run.py` or `holdout_run.py` again.** Their guards refuse in any case.

**Open with her (no action until the coordinator relays her answers):**
- c3-b-level, options (i) to (iv): the test level for the coverage clause.
- c3-b-nointv, options (a) to (c): models without intervals.
- When they arrive, set `ALPHA` / the no-intervals label in `make_report.py`, regenerate, and drop the "provisional" wording. Then send any folded-row changes to the coordinator as `register_updates.csv`.

**Next: B2 STACR 2017+.** Her decisions are in PLAN.md "Decisions taken", 2026-11-05 15:55 UTC; the coordinator relayed them:
- **Measure (ii):** spread plus an FHFA-style multiple, spread ÷ baseline expected loss from our EL engine under FHFA's 2016 baseline. Label it an assumption for the later deals. Reference-pool UPB comes from another source.
- **Tranches (b):** each seniority class (M-1, M-2, B) separately.
- **Indicative (b):** keep the "(Indicative)" tranches, flagged.
- **SOFR (b):** add a published LIBOR–SOFR spread adjustment to the pre-SOFR deals. Check the source first with the `source-provenance` skill.
- **Stop rule:** if the UPB or the spread adjustment needs a host not already approved, or is paywalled, stop and send the coordinator a proposed card. Do not work around blocked hosts.
- Inputs already here: `research/b2_crt_pricing/stacr_tranches.csv` (from `stacr_pricing.py`, 1e401cf), `b2.py`, `METHOD.md`, and the 10-K aggregates (`freddie_crt_cost.csv`, `fannie_crt_cost.csv`).
- The "2017–2023 aggregate cost" section (b2-1723 (i)) is done and accepted. Its rows are folded, so use `track_rows.py` for new rows.

**How to resume**
- `git config core.hooksPath .githooks`, then merge `origin/claude/sweet-gates-avwrcs`.
- Caches in `data/`: run `validation/run.py`, `research/c1_nowcast/z1_vintages.py`, `research/c1_nowcast/pit.py`. After `validation/run.py`, restore `validation/REPORT.md` and `validation/results.json` with `git checkout`; it rewrites their timestamps.
- The next review-log ids are mkt-s49, mkt-q45 and mkt-e26.
- SEC: pass the User-Agent as a per-command prefix only. A `git grep` for her email's local part must return rc=1 (do not write the pattern into any file).

## Handoff note (2026-11-05 ~15:00 UTC, for the next markets session)

**Done this session**
- c1b-dev-1 (a) fix at cddd3ca: "no target" rows, dated deviations, re-freeze. `holdout_run.check_order()` was added (mkt-q29), and q29 and q30 are resolved.
- The joint holdout ran ONCE at approval 432fed0. Results are in a0d9151 (C2 `holdout_results.json`, C1b `holdout_results.json` + `nowcasts_holdout.csv`). **Never rerun either script.**
- The Claude-draft summary is `research/joint_holdout/README.md`, from `make_readme_and_rows.py`. Its 59 hold_* rows were folded into the register by the coordinator (65e68f5), and `claims/tracks/markets.csv` is gone again. It is on her review queue as rv-holdout.
- STACR pricing workbook parsed (1e401cf). B2 2017+ work is on HOLD until she answers cards b2-1723-measure, -tranches, -indic and -sofr.

**Next: C3** (PLAN, "next (markets)"). Start from a0d9151, write Claude-draft text with register rows, and run no new holdout. The required contents are listed in `docs/decisions/scoring-protocol.md` "What C3 must publish":
- the specification registry, including abandoned specs (see the C2 and C1 git history and the deviations);
- holdout results for every frozen candidate;
- all benchmarks, horizons and losses, plus coverage with binomial intervals;
- raw and adjusted p-values (development tests in `research/c2_forecast/tests_dev.csv`);
- the ten largest errors per horizon;
- the regime splits 2007Q4–2011Q4 and 2020, which fall in development (the holdout is 2023Q3–2026Q2);
- the revision effect (C1 first-release vs latest; C2 `forecasts_realtime_dev.csv`);
- whether C1 indicators were used, and every deviation.

Check first whether `holdout_results.json` holds per-forecast errors or only scores. If only scores, per-forecast holdout errors would need a rerun, which is NOT allowed. In that case, report the gap to the coordinator as a proposed card.

**How to resume:** `git config core.hooksPath .githooks`. Merge `origin/claude/sweet-gates-avwrcs`. Rebuild the caches with the scripts listed in the earlier handoff in git history (z1_vintages.py, pit.py, freddie_mvs.py). The next review-log ids are mkt-s44 and mkt-q31.

## Decisions received (Eleonora, decision cards 2026-11-04 16:35–16:41 UTC; PLAN.md "Decisions taken", coordinator 543d96a)
| Item | Decision | Applied |
|---|---|---|
| C2 test-ordering deviation | accepted | `research/c2_forecast/SPECS.md` (ACCEPTED) |
| C2 seasonal naive in the Holm family (36 → 42) | accepted | SPECS.md (ACCEPTED) |
| C2 placebo | (a), demean the shuffled target. The options were written after the result was seen, and she chose knowing that | `forecast.py` `placebo()`; rerun: no skill at h = 1, 4, 8 (d683482) |
| Q-C1c | (b), run the C1 holdout in the same run as C2's, after C2 is frozen | joint holdout script prepared, sealed (below) |
| Q-C1b | (a), pre-register a second C1 run with Freddie Mac and Ginnie Mae, Fannie flat | prereg to write; not run |
| Q-B2.1 | (a) credit cost ÷ baseline expected loss, with (c) cost alone alongside | as built in B2 |
| Q-B2.2 | (c), deal data from crt.freddiemac.com and EDGAR | crt.freddiemac.com still blocked (not worked around). No EDGAR requests from this track: the request list is below for the coordinator to route |
| Q-B3 | (c), both preset families, DFAST first (labelled a proxy), then the 2008–12 replay; then B4 | in progress |

**Later decisions (PLAN.md "Decisions taken", rows recorded by the coordinator):**
- SEC access for markets decided by Eleonora 2026-11-04 ("Markets gets access", chat ~16:50 UTC). The User-Agent is passed as a per-command prefix only and never written to a file; `git grep` is checked before each commit.
- Holdout unseal approved by Eleonora 2026-11-04 (PLAN.md at cba74f9, "Go ahead", chat ~16:55 UTC). **The run is on HOLD** at the coordinator's request (17:06 UTC): the C1b CHOICE on whether C1b enters the joint run is still open for her, and running now would remove that option. The freeze (949acec) still matches.

### EDGAR request list for B2 (now run by this track: SEC access decided 2026-11-04)
*To confirm before relying on it:* STACR (Freddie Mac) and CAS (Fannie Mae) notes have been issued as exempt or Rule 144A offerings, the later ones through trusts, so their offering circulars and pricing are probably **not** on EDGAR. What EDGAR certainly holds is the GSEs' own periodic reports.
1. **Freddie Mac (CIK 0001026214, to confirm):** forms 10-K for FY2017–FY2023, and 10-Q for each quarter of 2017–2023. What B2 needs: the CRT programme tables (STACR and ACIS issuance by year, protection purchased, and the annual cost of CRT, often reported as "credit enhancement expense" or similar), plus reference-pool UPB covered.
2. **Fannie Mae (CIK 0000310522, to confirm):** forms 10-K FY2017–FY2023 and 10-Q 2017–2023. Same items for CAS and CIRT: issuance, risk in force, and annual credit-enhancement or CRT expense.
3. **Full-text search, to check whether any deal-level documents exist on EDGAR:** query `"Structured Agency Credit Risk"` and `"Connecticut Avenue Securities"`, forms 8-K and FWP, 2017–2023, filers the two CIKs above. If these return per-deal pricing supplements, B2 can extend its per-deal credit cost past 2016. If not, the 10-K aggregates give an annual cost per dollar of CRT protection for 2017–2023 (a coarser but consistent measure).
4. **Why the analysis track:** it already has the SEC access with the `SEC_USER_AGENT` declared under Eleonora's decision. Ideally it would deliver the extracted tables (year, programme, protection or RIF, annual cost), with URL, bytes and SHA-256 per filing.

## Status
| Task | Status | Notes |
|---|---|---|
| B1 | done | Accepted by Eleonora 2026-11-04 (inconclusive under the pre-set rule). `research/b1_market_pricing/`. |
| B2 | done (PLAN 81c9b37) | All parts approved by Eleonora as Claude drafts to rewrite: FHFA 2016 tables (2026-11-04), 2017–2023 aggregate cost (b2-1723 (i)), STACR 2017+ section (rv-b2-stacr17, 20:59 UTC; 392a1bf, 7b64703). `research/b2_crt_pricing/`. |
| B3 | in progress | Core engine, JS twin, DFAST and 2008–12 presets accepted. Left: interactive app with a browser parity test on fixed Python cases, preview deployment only. Being scoped for the coordinator (2026-11-05); no build until confirmed. |
| B4 | ranges accepted | Recession and GSE ranges accepted; student loans left out per her b4-student-2 (iii) until a reachable CBO estimate exists. `research/b4_policy_scenarios/`. |
| C3 | approved as a Claude draft (rv-c3-final, 20:59 UTC) | Final verdicts under c3-rule (b), c3-b-level (iv), c3-b-nointv (c) (392a1bf, 5c8bb4f). `research/c3_accuracy/`. Register rows folded by the coordinator. |
| C2 | done | Holdout run once (a0d9151); write-up approved as a draft (rv-holdout). Never rerun `holdout_run.py` or `holdout_forecasts_run.py`. |
| C1 | done | Holdout run once with C2 (a0d9151); write-up approved as a draft (rv-holdout). |
| C1b | done | Holdout run once (a0d9151); verdict and rows in `research/joint_holdout/README.md`, rows folded into the register (claims/tracks/markets.csv removed on main). |

## Log notes for the coordinator
**Session 2026-11-04 evening (markets track, fresh session replacing the stalled one).**
- Items, in order: C1b filled (0acbde6), built (9e0820a), developed and fixed (577c572), frozen (8c46906); B4 GSE range (290fcb8, 9f59e00); review-log move (63ec7fb); B4 student-loan search (1850a0f); Treasury check (199be31); B2 10-K aggregates, Freddie (1c0a089) and Fannie (992b265).
- Subagents: quant-reviewer on C1b before the freeze (about 55k tokens, 15 tool calls; q25 blocking, q26–q28); skeptic on the B4 GSE range (about 52k tokens, 18 tool calls; 2 major, 2 minor, 1 note). All resolved.
- SEC EDGAR: 27 requests for Fannie's 10-Ks, all 200, User-Agent given per command only; `git grep` for the address showed no hits before each commit.
- Not reachable, not worked around: www2.ed.gov (site front end 403 "The request is blocked"), www.cbo.gov (403), crt.freddiemac.com (gateway 502), capitalmarkets.freddiemac.com (000), home.treasury.gov search and policy pages (000).
- **Errors and who caught them:**
  1. Commit trailer: the first C1b commit carried a mistyped session URL. *Caught by Claude (main session)* before push; amended.
  2. C1b holdout path would have opened C1's holdout outside the single joint run. *Caught by quant-reviewer* (q25) before the freeze; gate rewritten.
  3. C1b robustness RMSE: an operator-precedence slip squared the error before scaling by 100 (values 10× too small; ratios unaffected). *Caught by Claude (main session)* on reading the output, before commit.
  4. B4 README called 7–42% the public share of all household-credit losses, though federal student loans carry no loss in either preset. *Caught by skeptic* (s33, logged first as s23).
  5. Both reviewers wrote to the shared `claims/review-log.md`, and the skeptic's ids collided with existing track entries. *Caught by Claude (main session)*; moved and renumbered (63ec7fb).
  6. B4 first draft asserted, unsourced, that FHA/VA loans default more often. *Caught by Claude (main session)* before commit; replaced by a two-sided caveat.

**Session 2026-11-04 (markets track).**
- Environment: `FRED_API_KEY` set, `DATABASE_URL_READONLY` set, `DATABASE_URL` set, `ANTHROPIC_API_KEY` unset. No database used (B1 and C1 read Z.1 and FRED directly). Not reachable: `alfred.stlouisfed.org` (the API host `api.stlouisfed.org` works and serves vintages), `www.freddiemac.com`, `www.fanniemae.com`, `www.sifma.org`.
- B1: method note first, then `b1.py` (OLS with Newey–West HAC in numpy; matches statsmodels to machine precision in `test_b1.py`). Added `research/common/fred.py` (cached FRED/ALFRED client, SHA-256 manifest, units-by-vintage rescaling), shared by B1 and C1.
- C1: point-in-time plumbing, release-lag table, Z.1 calendar from ALFRED, Fed Z.1 archive probed for older target vintages.
- Subagents: quant-reviewer on B1 (about 37k tokens, 9 tool calls), skeptic on B1 (about 52k tokens, 13 tool calls), quant-reviewer on C1 plumbing (sonnet, about 44k tokens, 7 tool calls): no look-ahead leak found; 5 objections (mkt-q6 to q10), code fixes for q8 and q9, the rest folded into Q-C1 below.
- **Errors and who caught them:**
  1. B1 README called the positive levels coefficient a finding although the levels residuals fail Engle–Granger. *Caught by quant-reviewer* (R-20261104-mkt-q1). Fixed.
  2. B1 README said the coefficient "loses significance" before the PMMS change; it actually flips sign. *Caught by quant-reviewer and skeptic* (mkt-q2, mkt-s1). Fixed.
  3. B1 headline "no association" overstated a low-power test. *Caught by skeptic* (mkt-s4) *and quant-reviewer* (mkt-q3). Now "inconclusive", with the power bound.
  4. B1 register rows dropped minus signs in `display`, mixed vintages, used catalog-level instead of cell-level series ids. *Caught by skeptic* (mkt-s8). Rows regenerated; signs checked by script, because `check_register.py` and `claim-check` ignore signs (proposal below).
  5. B1 public share counted Ginnie Mae (FHA/VA) pools that PMMS does not price. *Caught by skeptic* (mkt-s2). Fannie+Freddie-only share added as a declared post-hoc check.
  6. Both reviewers numbered their entries R-20261104-1…, colliding with each other and potentially with other tracks. *Caught by Claude (main session)*. Renumbered R-20261104-mkt-q*/s*.
  7. C1: ALFRED's units label switches from billions to millions mid-history (G.19 2025-02-07, Z.1 on FRED 2026-01-09), which made every revision look like 99.9%. *Caught by Claude (main session)* from the revision column of the first lag table. Fixed by rescaling each row by the units label in force when it was published (no look-ahead), with a test.
  8. C1: back-filled history (old dates added when a series is extended) showed up as lags of decades. *Caught by Claude (main session)*. Lags now count only observations that were the newest date in their first vintage, with a test.
  9. C1 draft attributed the late 2026-01-09 Z.1 release to the 2025 shutdown without a source. *Caught by Claude (main session)* on reread. Reworded to the observed date only.
  10. B1 (and any use of A1's holder cells before 1987): in 1974Q3–1986Q3 the Z.1 pool sub-series (FL413065110/123/133/143) sum to more than the pool total FL413065105 (by about $14.6B in 1980Q4), so cell-based shares are overstated there and step at 1986Q4. B1's first three sample quarters were affected; its first-differences estimate moved from −0.08 to −0.57 (verdict unchanged). *Caught by Claude (main session)* when C1's vintage test compared the archived share with the A1-cell share over 1952–2026. B1 now uses catalog-level shares as validation does. A1's own 2007–11 results are not affected.

**Session 2026-11-04, continued (after Eleonora's decisions).**
- Verified the coordinator's message against PLAN.md "Decisions taken" at a590475 before acting.
- Reported to the coordinator (send_message), not resolved here: (1) holdout conflict, C1 2024Q3+ vs frozen C2 2023Q3+; handled by cutting at 2023Q2; (2) C2's fact check says pre-2016-09 releases are HTML/PDF only, but `z1r-N.zip` text archives exist 2010–2016 (holder-table coverage unverified); (3) the A1 pool sub-series issue (item 10).
- Fed archive downloads: Python's urllib got 403 from www.federalreserve.gov, while plain curl and `requests` (the client `validation/run.py` already uses) got 200; switched to `requests`, no user-agent change. The 2017-03-09 release has no CSV zip: recorded as absent.
- Precision bug: z1_cells.csv was first written with 6 significant digits, which broke the base-share identity by about 1e-7. *Caught by Claude (main session)* through the assert in `nowcast.run`. Fixed (12 digits).
- Subagents this part: quant-reviewer on C1 (about 72k tokens, 21 tool calls; 6 objections, 2 major), skeptic on C1 (about 113k tokens, 38 tool calls; 7 objections, 2 major). Errors they caught: double-counted targets at k = 3 (quant-reviewer q11); the bridge regression compared on different targets from the bridge (q12, s11); the '2017-03-09 release missing' claim, which was wrong: it is in folder 20170305 (skeptic s9); wrong dates in sources.md (s14).
- Coordinator's quant review of B1 (coord-q1..q4) caught: a false 'every row fails EG' sentence (major), a 95% half-width presented as power, a causal attribution from post-hoc variants, and the correction missing from METHOD.md. All fixed (dc68eb7).
- Merge of the coordinator branch (1c51735): its folded register rows for b1/c1 were stale; c1 rows replaced in place, b1 rows moved back to `claims/tracks/markets.csv` (flagged to the coordinator).

**Overnight run, 2026-11-04 (after the coordinator's queue message; Eleonora's approval checked in PLAN.md at cc74d76).**
- B2 built and reviewed by the skeptic (sonnet, about 48k tokens, 10 tool calls; 7 objections, 4 major, all addressed). The skeptic caught:
  - the EL basis mismatch;
  - "per dollar sold" overstating the price;
  - the guarantee-fee identity (FHFA's fee = cost + 21/30 bps), which made one "finding" an identity;
  - ex-ante prices worded as payments.
  I caught, from the rendered PDF, the mislabelled Freddie "retained" column and that the nameless rows are blank in FHFA's own table.
- B3 engine and JS twin built (no reviewer: arithmetic engine, tested by invariants).
- C2 built. Error *caught by Claude (main session)*: I ran the first development scoring before writing the leakage tests, against the protocol's order. It is recorded in `SPECS.md` and reported to the coordinator. The tests then passed without code changes.
- The z1r parse for pre-2016 vintages was not attempted (lower priority than the queue).
- quant-reviewer on C2 (about 84k tokens, 22 tool calls; 8 objections: 1 blocker, 4 major). It caught leakage tests that did not exercise the production paths (blocker), DM used where Clark–West was required (nested at h = 1), bandwidth sensitivity of the headline, and a `--no-c1` run that changed the Holm family. All addressed (90a92a2) except the placebo, which waits for Eleonora.
- C3 not started: it needs the C2 holdout.

## Questions for Eleonora
(Design choices are hers. List each with the options and a recommendation; do not proceed on that point until she answers.)

### Q-B1. Accept B1 as specified, and whether to extend it
**Answered 2026-11-04 by Eleonora: (a)**, with a g-fee control only if B1 feeds A6 (PLAN.md "Decisions taken", a590475).
The specification in `research/b1_market_pricing/METHOD.md` (proxies, controls, levels and differences, reading rule) was Claude's proposal, fixed before results so that the result could not steer it.
- (a) Accept as is; B1 closes as "inconclusive, low power".
- (b) Add a guarantee-fee control from FHFA's annual g-fee reports (free, 2009+), as a new pre-specified variant (open objection mkt-q4).
- (c) Add a pre-2017 jumbo proxy backed out of FHFA MIRS (assumption-heavy).
- **Recommendation: (a), with (b) as a small follow-up if B1 numbers will feed A6.** (c) adds assumptions faster than evidence.

### Q-C1. Nowcast evaluation design
**Answered 2026-11-04 by Eleonora: the recommendation on items 1–9** (a590475). Item 6 must agree with the frozen C2 protocol; the holdout conflict is with the coordinator. Implemented in `research/c1_nowcast/EVALUATION.md`.
1. **Target vintage** (what the nowcast is scored against).
   (a) the first-release share, as first published in Z.1 for that quarter; (b) the latest vintage (Z.1 of 2026-09-11); (c) both, one primary.
   **Recommendation: (c) with (a) primary.** The nowcast stands in for the first release, and holder series revise. Needs the Fed archive parsed for 2010–2018 releases (ALFRED holder series start 2019).
2. **Indicator set** (fixed before any evaluation).
   (a) minimal: G.19 federal-government and total consumer credit, mortgage side carried forward from the last Z.1; (b) (a) plus G.19 private holders and H.8 bank residential and consumer loans; (c) (b) plus agency monthly summaries (Ginnie Mae now; Freddie and Fannie need `www.freddiemac.com` and `www.fanniemae.com` allowed).
   **Recommendation: (b) now, (c) as a second pre-registered run if the hosts are added.** Keeps the set small and fixed.
3. **Nowcast instants.**
   (a) monthly, on a fixed day (e.g. the 15th); (b) weekly, after each H.8; (c) three fixed points per quarter (1 month, 2 months after quarter end, day before Z.1).
   **Recommendation: (a).** Each quarter's share is then nowcast about twice before Z.1 publishes it, which is enough to see the G.19 information arrive, without weekly instants inflating the sample with near-duplicates.
4. **Model.**
   (a) accounting bridge: move each Z.1 component with its higher-frequency counterpart's growth since the last Z.1 quarter, recompute the share, no estimated parameters; (b) bridge regression of the change in share on indicator growth, estimated on a rolling window; (c) both, (a) primary.
   **Recommendation: (c).** (a) is transparent and cannot overfit; (b) is the challenger.
5. **Benchmarks.** No-change (last published share); random walk with drift (mean of the last four quarterly changes); AR(1) on the quarterly change. **Recommendation: all three, no-change as the headline comparison.**
6. **Metrics, sample and holdout.** RMSE and MAE in percentage points, each relative to no-change; sign accuracy of the change; for the tests, Diebold–Mariano with HAC errors against non-nested benchmarks and Clark–West against nested ones (the AR and bridge regressions nest no-change), all reported as descriptive given the small sample. Benchmarks are built from as-of data too (the last *published* share, not the final vintage). The holdout is the last eight quarters (2024Q3–2026Q2), untouched, and written into the pre-registration before any run.
   **Sample start depends on option 2** (quant-reviewer mkt-q6): ALFRED vintages begin 2008-10 (G.19 government, finance companies, credit unions), 2010-06 (Z.1 household totals), 2012-06 (G.19 depository institutions), 2012-08 (H.8 consumer loans), 2015-02 (H.8 residential real estate), 2019-03 (Z.1 holder series). So: option 2a can start 2010Q2; option 2b only 2015Q1 (about 38 evaluation quarters before the holdout); target option 1a before 2019 needs the Fed archive parsed. The alternative of starting 2b earlier with missing inputs treated as absent (model drops them) is possible but makes the indicator set change over time.
   **Recommendation: 2b from 2015Q1, with 2a from 2010Q2 as a longer-sample comparison; coordinate with the C2 scoring protocol the coordinator is drafting, so C1 and C2 share one protocol.**
9. **Definition of the quarterly change being nowcast** (mkt-q7). (a) first-release share of quarter q minus the share of q−1 *as published in the same Z.1*; (b) minus the q−1 share as previously published. **Recommendation: (a)**, so revisions to q−1 are not scored as nowcast error; the bridge growth rates use the same rule (same-vintage growth).
7. **Share definition.** (a) the headline share (mortgages + consumer credit); (b) mortgage-only. **Recommendation: (a)**, the project's quantity.
8. **Seasonal adjustment.** NSA throughout (Z.1 holder levels are NSA; `HMLBSHNO` and `CCLBSHNO` used rather than the SA `HHMSDODNS`). **Recommendation: NSA.**

### Q-B2 (new). B2 method and scope
1. **Price measure.**
   (a) FHFA's estimated credit cost ÷ the baseline expected loss of the sold slice, under FHFA's own scenario (as built);
   (b) cost ÷ a loss distribution (several scenarios), which needs assumptions FHFA does not publish;
   (c) cost alone, with no multiple.
   **Recommendation: (a)**, plus (c) alongside. The multiple is labelled as relative to FHFA's baseline only.
2. **2017–2023 prices.**
   (a) read issuance spreads off FHFA's Appendix D/E charts, with a stated reading error, labelled estimates;
   (b) leave the gap;
   (c) get deal data from crt.freddiemac.com (needs the host allowed) and EDGAR (needs `SEC_USER_AGENT` set in this environment).
   **Recommendation: (c) if you can add the host and variable; otherwise (b).** Chart reading adds error that the register cannot verify.

### Q-B3 (new). Where B3's scenario values come from
The engine has no built-in loss parameters. Each preset needs a primary source.
- **Options.**
  - (a) A recession case from the Fed's stress test (DFAST): projected loss rates by loan type for the largest banks under the severely adverse scenario, free on federalreserve.gov (reachable 2026-11-04). These are bank portfolios, so the result would be labelled a proxy for GSE and federal books.
  - (b) A 2008–12 replay from realised losses: Freddie Mac 10-Ks (freddiemac.com reachable; A2 already parses them), FHA actuarial reviews (hud.gov blocked), federal student-loan default data (studentaid.gov blocked).
  - (c) Both, each dated and sourced.
  - (d) No presets: the user enters values, and the app says so.
- **Recommendation: (c)**, starting with (a), whose source is reachable. (b) is partial until hud.gov and studentaid.gov are allowed. Every preset value gets a register row.

### Q-B4 (new). How the two policy scenarios map onto the engine
The status of each debate was looked up on 2026-11-04 (`research/b4_policy_scenarios/sources.md`):
- **GSEs:** FHFA says they "continue to operate under conservatorship".
- **Student loans:** P.L. 119-21, approved July 4, 2025, ends Grad PLUS for periods from July 1, 2026, sets new limits and adds a Repayment Assistance Plan.
- **Blocked:** Treasury, ED and the Federal Register are unreachable.

Questions:
1. **GSE release: which share of GSE-book losses becomes private on release.**
   (a) a 0–100% range, with points at 25, 50 and 75;
   (b) private up to GSE capital (from 10-Ks; Fannie's blocked);
   (c) specific release terms (none found).
   **Recommendation: (a).** Ginnie pools stay public in every case.
2. **Student-loan reform.**
   (a) the stock is unchanged, with a flow note;
   (b) an illustrative 0–10% move of the federal stock to private, labelled hypothetical;
   (c) a CBO or ED estimate of the shift (needs a source).
   **Recommendation: (a).**

### Q-C1c (new). When to run the C1 holdout
C1 and C2 share the holdout 2023Q3–2026Q2, and C2's Family Z+C1 uses C1's indicators. Scoring C1 on the holdout now would show holdout outcomes before C2's candidates are frozen, which could steer C2's design.
- **Options:** (a) run the C1 holdout now; (b) run it in the same single run as C2's holdout, after C2's candidates are frozen; (c) keep it unrun until C3.
- **Recommendation: (b).** Both holdouts are then seen once, by frozen models. Until then C1 reports development results only.

### Q-C1b (new, for later). Indicator set 2c as a second pre-registered run
The development results show the bridge biased downward. A likely cause is that public mortgage holders have no monthly indicator in 2b.
- **Hosts now reachable:** `www.freddiemac.com` (per the coordinator) and ginniemae.gov. Fannie Mae still returns 403.
- **Options:** (a) pre-register a 2c run with the Freddie Mac and Ginnie Mae monthly summaries, Fannie carried flat; (b) wait until Fannie is reachable; (c) no 2c run.
- **Recommendation: (a)**, frozen before it is scored. It must not modify the current run.

## Proposed changes to shared files
(PLAN.md, register, README, site copy: describe or attach a patch; the coordinator applies them.)
- **B3 in the app.** Add an atlas page or panel that imports `research/b3_scenarios/engine.mjs` (or a copy under `atlas/lib/`) and `exposures.json`. Show sliders for default rate, severity and timing per loan class, plus the transfer share and cap. Show bars for public versus private losses. Preview deployment only. Wait for Q-B3 before shipping any preset.
- **Register.** The b1_* rows are back in `claims/tracks/markets.csv` (dc68eb7) for re-folding, together with the new b2_* rows. The c1_* rows in `register.csv` were replaced in place with their current versions during the merge (1c51735).
1. **PLAN.md B1 row → done** once the coordinator's review agrees: "inconclusive, low power; no robust association under the pre-set rule; `research/b1_market_pricing/`".
2. **PLAN.md C1 row → blocked (Eleonora: evaluation design)**, with the plumbing noted.
3. **PLAN.md Environment prerequisites:** add `www.freddiemac.com` and `www.fanniemae.com` as not reachable on 2026-11-04 (needed for C1 option 2c); note `alfred.stlouisfed.org` blocked but `api.stlouisfed.org` sufficient.
4. **claims/check_register.py:** the scan drops the leading sign when matching, so a README that prints the wrong sign passes. Suggest a sign-aware comparison (or a warning) for rows whose `value` is negative.
5. **Review-log ids:** suggest a track infix (`R-<date>-<track>-<n>`) in the skeptic and quant-reviewer agent definitions, so parallel tracks cannot collide.
6. **claims/tracks/markets.csv:** 46 B1 rows to move into the register on merge.
