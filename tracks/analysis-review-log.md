### R-20261104-ana-39 · skeptic · research/a2_net_exposure/fannie_extract.py:28-29,63-69
- **Objection:** The restatement cross-check ("where a later 10-K restates a year end, both must agree", docstring line 11) never fires for FY2023-FY2025: those 10-Ks print "2023 , compared with" (space before the comma), which `(?:,? compared ...)` does not match, so the prior-year values for 2022, 2023 and 2024 are silently not compared. The values happen to agree (38, 42, 43), so no number moves; the check is weaker than documented and the tests (test_fannie_extract.py) cover only the no-space layouts.
- **Severity:** minor
- **Evidence:** `CRT.search("...$42 billion as of December 31, 2023 , compared with approximately $38 billion as of December 31, 2022 .").groups()` -> `('42', '2023', None, None)`; fannie_ce_outstanding.csv crt_quote for 2023-2025 lacks "compared".
- **Proposed resolution:** allow `\s*,?\s*compared` and add a fixture with the FY2023 spacing; assert the prior group matched whenever "compared with" follows.
- **Status:** open

### R-20261104-ana-40 · skeptic · research/a2_net_exposure/sources.md:55-58; fannie_ce_outstanding.csv 2013-2016
- **Objection:** Fannie's mortgage-insurance risk in force is recorded as "not found" for FY2013-16, but the 10-Ks do state it in a different wording ("We had total mortgage insurance coverage risk in force of $126.2 billion and $117.9 billion ... as of December 31, 2016 and 2015"). Not netted and not in a published claim, so nothing published is wrong, but "not found" is inaccurate.
- **Severity:** minor
- **Evidence:** fnma_10k_fy2016.htm text, offset ~1047466 (regex MI requires "mortgage insurance risk in force was").
- **Proposed resolution:** extend MI pattern to "mortgage insurance coverage risk in force of", or change "not found" to "stated in other wording, not extracted".
- **Status:** open

### R-20261104-ana-41 · skeptic · research/a2_net_exposure/README.md:40; net_exposure.py:143; tenk.py:26
- **Objection:** Stale text after the Fannie addition: README:40 still says Fannie's cover "will narrow the range from above once its filings can be read", and the two code comments say SEC was not fetched; the section at README:69-72 now reports it.
- **Severity:** minor
- **Evidence:** file:lines above.
- **Proposed resolution:** point README:40 to the 56.0% figure (and its year coverage); update the comments.
- **Status:** open


### Responses to R-20261104-ana-39 to -41 (analysis track, 2026-11-04)
- ana-39: accepted. The restatement pattern now allows a space before the comma; the check runs for every year and passes (2022–2024 restated values agree). Test added.
- ana-40: accepted. FY2013–16 wording ("total mortgage insurance coverage risk in force of $X billion ... as of December 31, FY") added, dated by its own sentence; the four cells in sources.md and the CSV now hold the figures and quotes. Not netted, so no published number changes.
- ana-41: accepted. README line 40, net_exposure.py and tenk.py no longer say Fannie's filings cannot be read.
