# Track: Data analysis

Branch: `claude/track-analysis` · Tasks, in order: A2, A5, A8 · Rules: PLAN.md "Parallel tracks".

## Status
| Task | Status | Notes |
|---|---|---|
| A2 | ready for review (bounds; skeptic run, 6 objections, 5 fixed, see `tracks/analysis-review-log.md`); the net series itself waits on Q1 | `research/a2_net_exposure/` |
| A5 | in progress: availability note, borrower tables, state maps done; register rows and skeptic pending; borrower-to-holder link waits on Q4 | `research/a5_distribution/` |
| A8 | blocked (network: every national source refused by the proxy; see `research/a8_international/AVAILABILITY.md`); availability note and unverified crosswalk draft done; metric choice is Q5 | `research/a8_international/` |

## Log notes for the coordinator
(Tasks done, models and subagents used with tokens, errors and who caught them. The coordinator folds these into docs/building-with-claude.md.)

### 2026-11-04, A2
- Environment: FRED_API_KEY set, DATABASE_URL_READONLY set, DATABASE_URL set, ANTHROPIC_API_KEY unset (this session).
- Network on 2026-11-04: www.fhfa.gov, www.federalreserve.gov, www.ginniemae.gov, www.newyorkfed.org reachable. Refused by the proxy policy (403 on CONNECT): www.sec.gov, efts.sec.gov, www.freddiemac.com, crt.freddiemac.com, capitalmarkets.fanniemae.com, www.fanniemae.com, www.usmi.org; and for A8: www.cmhc-schl.gc.ca, www150.statcan.gc.ca, www.bankofengland.co.uk, www.ons.gov.uk, www.bundesbank.de, www.statbank.dk, api.statbank.dk, www.nationalbanken.dk, data.bis.org, stats.bis.org, data-api.ecb.europa.eu, www.huduser.gov. PLAN listed CMHC, BoE, Bundesbank, Statbank DK, BIS and ECB as reachable on 2026-11-03; they are not today.
- A2 built (main model): FHFA CRT Progress Reports Dec 2016–4Q23 and Reports to Congress 2024–25 transcribed to `crt_fhfa.csv`; bounds on net Fannie/Freddie exposure 2013–2025 from Z.1 via A1's cells; asserts net ≤ gross, positive lower bound, transcription consistency (planted-typo test). A1 reproduces unchanged on the same Z.1 vintage.
- Subagents: register-keeper (Sonnet), 12 rows in `claims/tracks/analysis.csv`, about 32k tokens; reviewed by the main session (one key name in its report was wrong, the CSV itself was right).
- Skeptic (A2, 55k tokens): 6 objections, none blocking. Skeptic caught: the 55.2% "at least" was a floor only net of CRT, not of MI; the table subtracted RIF from UPB without saying so; FHFA's "majority" quote covers CRT and MI together, not CRT alone; an unsourced clause on where stress losses fall. All fixed.
- A5 built (main model): DFA borrower shares and leverage, NY Fed state per-capita tables and three tile maps, Z.1 loan-type public shares; no county file exists, so state level only. register-keeper (Sonnet), 26 rows, about 32k tokens.
- Error caught by register-keeper (A5): the README printed 31.4% for the public share of consumer credit; the source is 0.31349 (31.3%, same as the existing C8 row). Claude had rounded twice. Fixed.
- Error caught by Claude (main, A5 figures): the tile-map legend rendered "$...$" as mathtext (italic, no dollar signs); escaped and re-rendered after looking at the PNG.
- Errors caught: Claude (main) caught its own method-note claim that 2023 Fannie attach points run 60–155 bp; the deal table shows 60–165 bp. Fixed before commit. The 4Q23 PMI cumulative box has no text layer; read from the image and checked that Fannie + Freddie add to the total and to FHFA's "$3.3 trillion".

## Questions for Eleonora
(Design choices are hers. List each with the options and a recommendation; do not proceed on that point until she answers.)

**Q1 (A2). What counts as "transferred"?** Details in `research/a2_net_exposure/METHOD.md`.
- (a) Bounds only, as now: net between gross minus all CRT risk in force ever issued and gross. No assumptions; wide in principle, though in RIF terms the gap is at most about 1 pp of the public share.
- (b) Observed outstanding CRT and mortgage-insurance cover from Fannie's and Freddie's 10-K/10-Q. Free and primary, but needs `www.sec.gov` (and `efts.sec.gov`) added to Allowed domains, or you download the filings.
- (c) Runoff estimate: decay each year's issued RIF at an assumed paydown rate. Labelled estimate; sensitive to the 2020–21 refinancing wave.
- (d) Expected or stress loss transferred (needs deal attach/detach points and a loss model; overlaps with A6).
- Recommendation: (b) for the net series in RIF terms, with (a) kept as the check it must sit inside, and (d) deferred to A6. Until then A2 stays at (a).

**Q2 (A2). Mortgage insurance: net it out or not?** Private insurers pay first, but the Enterprises keep the counterparty risk, and FHFA says MI and CRT RIF are "not strictly comparable". Options: net of CRT only; net of CRT and MI; show MI as a separate line. Recommendation: separate line, from outstanding 10-K figures once (b) is available.

**Q3 (A2). Ginnie Mae pools.** VA guarantees only part of each loan, so Ginnie pools overstate public risk. Keep Ginnie at gross (now), or source VA guaranty data and net the unguaranteed part? Recommendation: keep gross and state it, unless A6 needs it.

**Q4 (A5). How to link borrowers to holders ("who borrows vs who carries the risk").** No free source crosses borrower group with holder (DFA: borrower, no holder; Z.1: holder, no borrower; NY Fed state data: loan type, no holder).
- (a) Side by side only, as now: borrower shares and holder shares by loan type, never multiplied.
- (b) Uniform holder mix within each loan type: a group's public exposure = its mortgages × public mortgage share + its consumer credit × public consumer-credit share. Easy, but it ignores that FHA borrowers and student-loan borrowers skew lower-income, so it understates public exposure at the bottom. Labelled estimate.
- (c) As (b), but split consumer credit into student loans (mostly federal) and the rest using the NY Fed state/age student-loan data or the SCF. Better, but needs another source (SCF public file, `www.federalreserve.gov`, reachable) and its own availability check.
- (d) Leave the link to A7 (state panel) and keep A5 descriptive.
- Recommendation: (c) as a labelled estimate, with (b) shown next to it so the size of the assumption is visible. Until you answer, A5 stays at (a).


**Q5 (A8). Which comparison metric, and can the national hosts be allowed?** The US share is a holder measure; Canada's public exposure is mostly insurance on privately held loans; Germany's public-law banks are publicly owned but do not guarantee borrowers (draft crosswalk, unverified: `research/a8_international/CROSSWALK.md`).
- (a) Holder only: who owns the loan. Comparable with the US series, but misses Canadian mortgage insurance and would put Germany's Sparkassen either at 100% or at 0% depending on how ownership is treated.
- (b) Credit-risk bearer: who takes the loss on default (holder, unless an insurer or guarantor stands in front). Closest to the project's question; needs insurance-in-force data (CMHC) and scheme data (UK).
- (c) Report both (a) and (b), with the gaps stated.
- Recommendation: (c), with (b) as the headline, since the project's question is who carries the risk. Either way A8 needs the hosts in `research/a8_international/AVAILABILITY.md` ("What would unblock A8") added to Allowed domains, or the national tables downloaded by hand into `data/a8/`.

## Proposed changes to shared files
(PLAN.md, register, README, site copy: describe or attach a patch; the coordinator applies them.)

- PLAN.md "Environment prerequisites": CMHC, Bank of England, Bundesbank, Statbank DK, BIS and ECB are listed as reachable on 2026-11-03, but all were refused (403) on 2026-11-04. Also refused: `www.sec.gov`, `efts.sec.gov`, all freddiemac.com and fanniemae.com hosts, `api.census.gov`, `www2.census.gov`, `www.usmi.org`. Suggest updating that table.
- PLAN.md row A2: suggested status "bounds done (net series waits on Q1/Q2)"; row A5: "descriptive part done (borrower-to-holder link waits on Q4)"; row A8: "blocked (network; Q5)".
- claims/register.csv: on merge, fold `a5_public_share_cc_2026q2_readme` into `public_share_cc_2026q2` as an extra location (same claim, C8).
- `tracks/analysis-review-log.md` → `claims/review-log.md` on merge.
