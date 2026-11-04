# Track: Data analysis

Branch: `claude/track-analysis` · Tasks, in order: A2, A5, A8 · Rules: PLAN.md "Parallel tracks".

## Status
| Task | Status | Notes |
|---|---|---|
| A2 | in progress: bounds done, skeptic review pending; net series waits on Q1 | `research/a2_net_exposure/` |
| A5 | todo | |
| A8 | todo | |

## Log notes for the coordinator
(Tasks done, models and subagents used with tokens, errors and who caught them. The coordinator folds these into docs/building-with-claude.md.)

### 2026-11-04, A2
- Environment: FRED_API_KEY set, DATABASE_URL_READONLY set, DATABASE_URL set, ANTHROPIC_API_KEY unset (this session).
- Network on 2026-11-04: www.fhfa.gov, www.federalreserve.gov, www.ginniemae.gov, www.newyorkfed.org reachable. Refused by the proxy policy (403 on CONNECT): www.sec.gov, efts.sec.gov, www.freddiemac.com, crt.freddiemac.com, capitalmarkets.fanniemae.com, www.fanniemae.com, www.usmi.org; and for A8: www.cmhc-schl.gc.ca, www150.statcan.gc.ca, www.bankofengland.co.uk, www.ons.gov.uk, www.bundesbank.de, www.statbank.dk, api.statbank.dk, www.nationalbanken.dk, data.bis.org, stats.bis.org, data-api.ecb.europa.eu, www.huduser.gov. PLAN listed CMHC, BoE, Bundesbank, Statbank DK, BIS and ECB as reachable on 2026-11-03; they are not today.
- A2 built (main model): FHFA CRT Progress Reports Dec 2016–4Q23 and Reports to Congress 2024–25 transcribed to `crt_fhfa.csv`; bounds on net Fannie/Freddie exposure 2013–2025 from Z.1 via A1's cells; asserts net ≤ gross, positive lower bound, transcription consistency (planted-typo test). A1 reproduces unchanged on the same Z.1 vintage.
- Subagents: register-keeper (Sonnet), 12 rows in `claims/tracks/analysis.csv`, about 32k tokens; reviewed by the main session (one key name in its report was wrong, the CSV itself was right).
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

## Proposed changes to shared files
(PLAN.md, register, README, site copy: describe or attach a patch; the coordinator applies them.)
