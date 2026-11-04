> **Claude draft, not the author's text.** Fact checks for the A4, A7 and C2 pre-registrations.

Checked 2026-11-04 (about 00:59 to 01:06 UTC) from the project cloud environment. Raw downloads are in the session scratchpad (`.../scratchpad/factcheck/`), not the repo; sizes and SHA-256 identify the copy read. Quotes are exact excerpts. No faked user agent was used; hosts that refused are listed under each item.

Summary

| # | Item | Status |
|---|---|---|
| 1 | Fed agency-MBS programme: announced 25 Nov 2008; purchases began 5 Jan 2009; expanded 18 Mar 2009 | VERIFIED |
| 2 | Six A4 statutes: public law, Statutes at Large page, date | VERIFIED (govinfo PDFs exist for all six) |
| 3 | Abadie-Diamond-Hainmueller (2010) citation and the 5x placebo cutoff | NOT VERIFIED (paper text unreachable) |
| 4 | R / `strucchange` here; HAC support | R NOT INSTALLED and CRAN NOT REACHABLE; package behaviour VERIFIED from the package's own man pages |
| 5 | June 2026 Z.1 release date | VERIFIED: 2026-06-11 (REPORT.md "2026-06-10" is a file timestamp) |
| 6 | Depth of Z.1 per-release CSV archive; ALFRED vintages | VERIFIED (details below) |

---

## 1. Fed agency-MBS purchase programme

**Result.**
- Announced Tuesday **25 November 2008** (press release, "Last Update: November 25, 2008"; 25 Nov 2008 was a Tuesday).
- Purchases **began 5 January 2009** (Fed H.4.1 release of 15 Jan 2009). This is the trade start; the first holdings settled in the week to 14 Jan 2009 (H.4.1 text; consistent with FRED `WSHOMCB`: 0 on 2009-01-07, 5,634 on 2009-01-14, in millions of dollars, weekly Wednesday level).
- Expanded by the FOMC on **18 March 2009**: "up to an additional $750 billion of agency mortgage-backed securities, bringing its total purchases of these securities to up to $1.25 trillion this year".
- Detail the drafts may want: the November announcement was "up to $500 billion in MBS" and "up to $100 billion" of GSE direct obligations; the MBS purchases were announced with "a goal of beginning these purchases before year-end", so the start slipped to January.

**Effect on the drafts.** A7's "announced late 2008, purchases from early 2009" is confirmed. For the A7 event window (a7-causal-prereg.md line 71, "ends before the Fed MBS announcement"): the announcement is 25 Nov 2008, the first day of the news, not 5 Jan 2009. 25 Nov 2008 falls in 2008Q4; 5 Jan 2009 falls in 2009Q1; 18 Mar 2009 also in 2009Q1. `WSHOMCB` first nonzero is dated 14 Jan 2009 (settlement), so it dates settlement, not the first purchase, by about a week.

| Supports | Source | URL | Bytes | SHA-256 | Retrieved (UTC) | Quote |
|---|---|---|---|---|---|---|
| Announcement 25 Nov 2008 | Federal Reserve Board press release | https://www.federalreserve.gov/newsevents/pressreleases/monetary20081125b.htm | 82646 | `849695e26714c753fe41713e18ae61822291ddfe2015c328cdc2dbb024111999` | 2026-11-04T00:59:48Z | "The Federal Reserve announced on Tuesday that it will initiate a program to purchase the direct obligations of housing-related government-sponsored enterprises (GSEs)--Fannie Mae, Freddie Mac, and the Federal Home Loan Banks--and mortgage-backed securities (MBS) backed by Fannie Mae, Freddie Mac, and Ginnie Mae." ... "Purchases of up to $500 billion in MBS will be conducted by asset managers selected via a competitive process with a goal of beginning these purchases before year-end." Page footer: "Last Update: November 25, 2008" |
| Announcement date, second source | FOMC minutes, 15-16 Dec 2008 | https://www.federalreserve.gov/monetarypolicy/fomcminutes20081216.htm | 60082 | `5424674c705f64c1c70794f9391051058a3e282bb73a5bd64b6223d76953d5cc` | 2026-11-04T01:00:18Z | "The Federal Reserve also announced on November 25 that, to help reduce the cost and increase the availability of residential mortgage credit, it would initiate a program to purchase up to $100 billion in direct obligations of housing-related government-sponsored enterprises (GSEs) and up to $500 billion in MBS backed by Fannie Mae, Freddie Mac, and Ginnie Mae." |
| Purchases began 5 Jan 2009 | Federal Reserve H.4.1 release, 15 Jan 2009 | https://www.federalreserve.gov/releases/h41/20090115/ | 51208 | `e9f8c31c9b08a42c557fb10a7304a8fcca172a7edc890ae03dde872e674aca73` | 2026-11-04T01:01:29Z | "On November 25, 2008, the Federal Reserve announced a program to purchase mortgage-backed securities guaranteed by Fannie Mae, Freddie Mac, and Ginnie Mae." ... "Purchases of these securities began on January 5, 2009. Outright transactions in mortgage-backed securities have settlement dates that can extend several months into the future. Federal Reserve purchases that settled during the week ended January 14, 2009, are reflected on this release." |
| Expansion 18 Mar 2009 | FOMC statement | https://www.federalreserve.gov/newsevents/pressreleases/monetary20090318a.htm | 82313 | `f98e845844943283fadda443ee8c8f1298070c8e57233ecaffc2ca7c926d58c6` | 2026-11-04T00:59:49Z | "the Committee decided today to increase the size of the Federal Reserve's balance sheet further by purchasing up to an additional $750 billion of agency mortgage-backed securities, bringing its total purchases of these securities to up to $1.25 trillion this year, and to increase its purchases of agency debt this year by up to $100 billion to a total of up to $200 billion." Page footer: "Last Update: March 18, 2009" |
| First holdings in data | FRED API, `WSHOMCB` observations 2008-11-01 to 2009-03-01 (JSON, key not recorded) | https://api.stlouisfed.org/fred/series/observations?series_id=WSHOMCB | 1862 | `fd5457947fb99456...` (first 16 hex only recorded) | 2026-11-04T01:03Z | 2009-01-07: 0; 2009-01-14: 5634; 2009-01-21: 5991; 2009-01-28: 7377 |

Not reached: the New York Fed's MBS operations pages (`newyorkfed.org/markets/ambs...`) returned a "URL has changed" stub with no operations table; the 5 Jan date therefore rests on the Fed Board's H.4.1 text only.

**Status: VERIFIED** (all three dates, from federalreserve.gov).

---

## 2. A4 statutes

govinfo.gov **does** carry Statutes at Large PDFs for all six (OCR text layer; the OCR is imperfect, so the headers below were read from the page-header line, e.g. "PUBLIC LAW 89-329-NOV. 8, 1965"). URL pattern: `https://www.govinfo.gov/content/pkg/STATUTE-<vol>/pdf/STATUTE-<vol>-Pg<page>.pdf`. Each PDF is the statute only (page ranges 15 to 426 pages).

| Statute | Public law | Statutes at Large | Enacted | Notes |
|---|---|---|---|---|
| Higher Education Act of 1965 | Pub. L. 89-329 | 79 Stat. 1219 | 8 Nov 1965 | Title IV, Part B is "Federal, State, and Private Programs of Low-Interest Insured Loans to Students in Institutions of Higher Education" (the guaranteed-loan programme), at 79 Stat. 1236. |
| Housing and Urban Development Act of 1968 | Pub. L. 90-448 | 82 Stat. 476 | 1 Aug 1968 | Title VIII, Sec. 801 (82 Stat. 536) partitions the Federal National Mortgage Association into two corporations: Fannie Mae (government-sponsored private) and Ginnie Mae (stays in government). |
| Emergency Home Finance Act of 1970 | Pub. L. 91-351 | 84 Stat. 450 | 24 Jul 1970 | Title III, Sec. 301: "may be cited as the 'Federal Home Loan Mortgage Corporation Act'" (Freddie Mac). |
| Financial Institutions Reform, Recovery, and Enforcement Act of 1989 (FIRREA) | Pub. L. 101-73 | 103 Stat. 183 | 9 Aug 1989 | The OCR of one line misreads the number as "101-78"; the page header reads 101-73. |
| Federal Housing Enterprises Financial Safety and Soundness Act of 1992 | Pub. L. 102-550 (Housing and Community Development Act of 1992), Title XIII | Title XIII at 106 Stat. 3941 (act begins 106 Stat. 3672) | 28 Oct 1992 | It is a title of the 1992 housing act, not a separate public law: "SEC. 1301. SHORT TITLE. This title may be cited as the 'Federal Housing Enterprises Financial Safety and Soundness Act of 1992'". |
| Student Loan Reform Act of 1993 | Pub. L. 103-66 (Omnibus Budget Reconciliation Act of 1993), Title IV, Subtitle A, Sec. 4011 | Sec. 4011 at 107 Stat. 341 (act begins 107 Stat. 312) | 10 Aug 1993 | Also a subtitle of a larger act: "SEC. 4011. SHORT TITLE; REFERENCES. (a) SHORT TITLE.-This subtitle may be cited as the 'Student Loan Reform Act of 1993'." |

**Caveats (read before freezing).**
- The enactment dates are the dates in the page-header line of each public law ("Aug. 10, 1993" etc.); I did not locate a separate "Approved" line for each. The Fed MBS and A1 rows use the same approach.
- Dates here are enactment dates only. Effective dates are not checked and can differ (for example, Direct Lending under the 1993 act started with the 1994-95 academic year, not checked here). The draft should say "enacted" and not "effective" unless an effective-date source is added.
- Two of the six are parts of larger acts (FHEFSSA, Student Loan Reform Act). Their enactment date is the date of the parent act.
- Quarters containing the dates: 1965Q4, 1968Q3, 1970Q3, 1989Q3, 1992Q4, 1993Q3 (calendar-quarter arithmetic from the dates above; the draft's own quarter convention should be applied).

| Supports | Source | URL | Bytes | SHA-256 | Retrieved (UTC) |
|---|---|---|---|---|---|
| HEA 1965 | GovInfo, 79 Stat. 1219 | https://www.govinfo.gov/content/pkg/STATUTE-79/pdf/STATUTE-79-Pg1219.pdf | 9768396 | `61dbbb4ccefcc1a432925e17e6754fe9ccfa68048a8d022717ee178cee4209a2` | 2026-11-04T01:01:39Z |
| HUD Act 1968 | GovInfo, 82 Stat. 476 | https://www.govinfo.gov/content/pkg/STATUTE-82/pdf/STATUTE-82-Pg476.pdf | 25575763 | `d12da570e1e0785cb74a31bac0e30e5f9fca881d43355c8793cb2358fc354cc0` | 2026-11-04T01:01:43Z |
| Emergency Home Finance Act 1970 | GovInfo, 84 Stat. 450 | https://www.govinfo.gov/content/pkg/STATUTE-84/pdf/STATUTE-84-Pg450.pdf | 3035147 | `e042dfec433f6a2c1dc67502e9f5e161ced01ad770d32a8b6af0813ce9051642` | 2026-11-04T01:01:44Z |
| FIRREA 1989 | GovInfo, 103 Stat. 183 | https://www.govinfo.gov/content/pkg/STATUTE-103/pdf/STATUTE-103-Pg183.pdf | 59227576 | `fd3246cd816eaa5d8f82508d24d42b3675b3291b148e78b9bc4f16dfb54d6364` | 2026-11-04T01:01:53Z |
| HCDA 1992 incl. FHEFSSA | GovInfo, 106 Stat. 3672 | https://www.govinfo.gov/content/pkg/STATUTE-106/pdf/STATUTE-106-Pg3672.pdf | 70080456 | `a96ca11549308749d196334471bfbbcd245a2d602ce29948ad3482324a976c2b` | 2026-11-04T01:02:03Z |
| OBRA 1993 incl. SLRA | GovInfo, 107 Stat. 312 | https://www.govinfo.gov/content/pkg/STATUTE-107/pdf/STATUTE-107-Pg312.pdf | 61302685 | `da2019293df36e19762ee03c28daa24aba730f396896e934e1025e71f4da3711` | 2026-11-04T01:02:13Z |

Quotes (exact, from the PDF text layer): HEA, "This Act may be cited as the 'Higher Education Act of 1965'" under header "PUBLIC LAW 89-329-NOV. 8, 1965"; HUD Act, "SEC. 801. The purposes of this title include the partition of the Federal National Mortgage Association as heretofore existing into two separate and distinct corporations" under header "PUBLIC LAW 90-448-AUG. 1, 1968"; EHFA header "PUBLIC LAW 91-351-JULY 24, 1970"; FIRREA header "PUBLIC LAW 101-73-AUG. 9, 1989" and "(a) SHORT TITLE.-This Act may be cited as the 'Financial Institutions Reform, Recovery, and Enforcement Act of 1989'"; HCDA header "PUBLIC LAW 102-550-OCT. 28, 1992"; OBRA header "PUBLIC LAW 103-66-AUG. 10, 1993".

**Status: VERIFIED** (public law, Statutes at Large location and enactment date for all six, with the caveats above).

---

## 3. Abadie, Diamond and Hainmueller (2010)

**Result: NOT VERIFIED.** I could not read the paper or any record of it. Every host that holds it was refused by the network policy (HTTP 403 on the CONNECT tunnel, no retry with other settings): `doi.org`, `api.crossref.org`, `api.openalex.org`, `www.tandfonline.com`, `web.stanford.edu`, `economics.mit.edu`, `dash.harvard.edu`, `scholar.harvard.edu`, `www.jstatsoft.org`, `cran.r-project.org`. Hosts to add to the allowlist if wanted: `api.crossref.org` (citation metadata), `www.tandfonline.com` or `scholar.harvard.edu` / `web.stanford.edu` (paper text).

What is *not* asserted:
- The citation below is from memory only and is **unchecked**: Abadie, A., Diamond, A., Hainmueller, J. (2010), "Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program", *Journal of the American Statistical Association* 105(490), 493-505, DOI 10.1198/jasa.2009.ap08746. Note the full title has a subtitle; the A7 draft should cite it in full once confirmed.
- The "5x" attribution is **not confirmed**. I have an unchecked recollection that the paper's placebo figures exclude units by several different pre-treatment MSPE multiples, not one; that is memory, not a finding. Do not freeze "5x follows Abadie-Diamond-Hainmueller" on the strength of this check.

**Effect on the draft.** A7 line 100 says the 5x rule "follows the usual Abadie-Diamond-Hainmueller practice (citation to be checked before freezing)". It cannot be checked from here. Either (a) Eleonora reads the paper (section on placebo studies and the post/pre MSPE ratio figure) and supplies the multiple and page, or (b) the draft states the cutoff as the project's own choice, without attribution, and keeps the post/pre RMSPE ratio rank as the primary inference (which, as the draft says, needs no cutoff).

---

## 4. R and `strucchange`

**Environment.** `which R Rscript` returns nothing: **R is not installed**. `apt-cache policy r-base-core` shows "Installed: (none), Candidate: (none)", so it is not installable via apt from the configured sources either; I did not try to install R. **CRAN is not reachable**: `cran.r-project.org`, `cloud.r-project.org`, `r-universe.dev` and `github.com` (HTML) all returned 403 on CONNECT, so `install.packages("strucchange")` could not be tried even with R. PLAN.md row A4 says "(CRAN reachable)"; that is **not true from this environment** on 2026-11-04. The cross-check in R therefore needs R and a CRAN mirror in the cloud environment, or a local machine. Reachable: `raw.githubusercontent.com` (read of the `cran/` GitHub mirror), which is how the docs below were read.

**Package documentation read** (`cran/strucchange` and `cran/sandwich` mirrors on raw.githubusercontent.com, retrieved 2026-11-04 ~01:03 to 01:04 UTC): strucchange 1.6-0 (DESCRIPTION dated 2026-08-04), sandwich 3.1-3 (2026-08-02). These are mirror copies of the CRAN source, not the CRAN web pages.

Findings:
- **`breakpoints()` has no HAC option.** Its usage is `breakpoints(formula, h = 0.15, breaks = NULL, data = list(), hpc = c("none","foreach"), ...)`. The break dates come from least-squares SSR minimisation (Bai-Perron dynamic programme); the number of breaks is the minimum-BIC partition (man page: "the breakpoints of the minimum BIC partition"; the man page also warns "Perron (2003) report that the BIC has problems in dynamic regressions", which matters for the draft's "BIC (the strucchange default)" option). Sequential sup-F(l+1|l) and UDmax/WDmax are **not** implemented in this man page's `breakpoints`. The draft's recommended option (a) therefore cannot be cross-checked in strucchange; only the BIC/RSS table can. (I did not search the other help pages for sequential tests; the `breakpoints.Rd` text contains no "UDmax", "WDmax" or "sequential".)
- **HAC is supported for the confidence intervals and covariances**: `confint(<breakpointsfull>, level, breaks, het.reg = TRUE, het.err = TRUE, vcov. = NULL, sandwich = TRUE)` and `vcov(<breakpointsfull>, ..., vcov. = NULL, sandwich = TRUE)`. `vcov.` is "a function to extract the covariance matrix for the coefficients of a fitted model of class lm"; `sandwich` says whether that function returns the full sandwich or only the middle part.
- **HAC is supported for known-date Chow / sup-F tests**: `Fstats(formula, from = 0.15, to = NULL, data = list(), vcov. = NULL)`, with `sctest(<Fstats>, type = c("supF","aveF","expF"))`. `gefp(..., vcov = NULL, ...)` also takes a covariance function (the man page example uses `vcov = kernHAC`).
- **The requested HAC settings exist in `sandwich`**: `kernHAC(x, order.by = NULL, prewhite = 1, bw = bwAndrews, kernel = c("Quadratic Spectral", "Truncated", "Bartlett", "Parzen", "Tukey-Hanning"), ...)`. Defaults: Quadratic Spectral kernel, Andrews (1991) data-driven bandwidth (`bwAndrews`), VAR(1) prewhitening ("The default is to use VAR(1) prewhitening"). `vcovHAC(prewhite = FALSE, weights = weightsAndrews)` is the lower-level function; `NeweyWest()` gives Bartlett. So `Fstats(y ~ 1, vcov. = kernHAC)` and `confint(bp, vcov. = kernHAC)` are the intended calls.
- **Not checked:** whether the numeric output of `breakpoints`/`confint` with `kernHAC` is what the Python version should match (that needs R running; no run was done), and whether strucchange's `sctest`/`Fstats` p-values use the HAC covariance for the whole supF distribution (the man page only says `vcov.` is a covariance function). Treat "HAC-valid sup-F p-values" as **not verified**.

| Supports | Source | URL | Bytes | SHA-256 |
|---|---|---|---|---|
| `breakpoints` usage, BIC, `vcov`/`confint` args | strucchange `man/breakpoints.Rd` | https://raw.githubusercontent.com/cran/strucchange/master/man/breakpoints.Rd | 13601 | `244b81ea6cc7e0b60916ea92f17e1c97dcde8bb05a97c4fec9aed5ea883cc6d2` |
| `confint` usage | strucchange `man/confint.breakpointsfull.Rd` | https://raw.githubusercontent.com/cran/strucchange/master/man/confint.breakpointsfull.Rd | 3361 | `17e5669faa3ab20d104593040ac11f4e09ad6480ab9d59b3982e727cf6dd1248` |
| `Fstats` usage (`vcov.`) | strucchange `man/Fstats.Rd` | https://raw.githubusercontent.com/cran/strucchange/master/man/Fstats.Rd | 4540 | `af77a0289ecdb5982897cb1860232a60fe8e6d39add1e7d383d72e4966fc632c` |
| `gefp` usage (`vcov`) | strucchange `man/gefp.Rd` | https://raw.githubusercontent.com/cran/strucchange/master/man/gefp.Rd | 3849 | `25063f7b7cec1fdf6f5a17b62e3bfa204e1371a143e8ef6ae88c8077058ad360` |
| Package version | strucchange `DESCRIPTION` | https://raw.githubusercontent.com/cran/strucchange/master/DESCRIPTION | 2847 | `33ff9f5aae906f14c2d347dabdcc1f429c056813cbc4ab8bbb0d3c5efb9a9fb8` |
| `kernHAC`, `weightsAndrews`, `bwAndrews` | sandwich `man/weightsAndrews.Rd` | https://raw.githubusercontent.com/cran/sandwich/master/man/weightsAndrews.Rd | 6676 | `b1f25b452e2ef7210595bc70ddcb185c109fd4e330a64fdba21c8ff3f901d06b` |
| `vcovHAC`, `prewhite`, `weights` | sandwich `man/vcovHAC.Rd` | https://raw.githubusercontent.com/cran/sandwich/master/man/vcovHAC.Rd | 5740 | `959aa6d943b02e4de097a857592faa26414ad878abe0efd161fc76fca7bc076e` |

Quotes: `kernHAC(x, order.by = NULL, prewhite = 1, bw = bwAndrews, kernel = c("Quadratic Spectral", "Truncated", "Bartlett", "Parzen", "Tukey-Hanning"), ...`; "The default is to use VAR(1) prewhitening."; breakpoints.Rd: "the BIC would choose 0 breakpoints although the RE and supF test ... Perron (2003) report that the BIC has problems in dynamic regressions."

**Status.** R and CRAN: NOT AVAILABLE here. Package capability: VERIFIED from the man pages (HAC with Quadratic Spectral, Andrews bandwidth, prewhitening is available through `vcov. = kernHAC` for `Fstats`, `confint` and `vcov`; **not** inside `breakpoints()` itself). Numeric agreement with the Python implementation: NOT VERIFIED (nothing run).

**Effect on the draft.** breaks.md "agreement with R strucchange" should say which parts R can cross-check: dates and SSR/BIC (yes), CIs with HAC through `confint(vcov. = kernHAC)` (yes, but the CI method in strucchange is Bai (1997) with the supplied covariance; settings must be pinned), sup-F(l+1|l) sequential selection (no, not in the man page read). Also PLAN.md row A4's "(CRAN reachable)" is false here.

---

## 5. June 2026 Z.1 release date

**Result: 11 June 2026.** `validation/run.py` (line 35, `PREV_RELEASE = "20260611"`) is right. `validation/REPORT.md` "prev vintage 2026-06-10" is **not a release date**: it is `prev_member_timestamp`, the timestamp of a file inside the zip (`2026-06-10T16:02:22`), the day the Fed built the files. The report prints `ts.date()` under the label "prev vintage" (run.py line 489), which mislabels the build date as the vintage. The repo's `data/validation/prev_z1_csv_files.zip` has the same SHA-256 as the zip downloaded from the 20260611 folder (`b23e0ad3...`).

Evidence:
- The Fed's Z.1 release-dates page lists "June 2026:Q1" with the links `/releases/z1/20260611/html/default.htm`, `/releases/z1/20260611/z1.pdf`, `/releases/z1/20260611/z1_csv_files.zip`.
- The zip's HTTP `Last-Modified` is "Thu, 11 Jun 2026 16:00:16 GMT" (noon Eastern, the release time). Zip member timestamps are 2026-06-10 16:01:52 to 16:02:54.
- The Z.1 landing page states that Z.1 is released at noon (the next release is "Thursday, December 10, 2026, at 12:00 noon"); the folder `20260610` returns 404.
- ALFRED/FRED vintage dates for `HHMSDODNS` and `CMDEBT` in 2026 are 2026-01-09, 2026-03-19, 2026-06-11, 2026-09-11 (matches).
- Warning for the probe code: the server returns the **same file** for a nearby wrong date: `.../z1/20260612/z1_csv_files.zip` also returned HTTP 200 with the identical bytes and SHA-256 as 20260611. A 200 on a probed folder does not prove that a release exists on that date. Use the release-dates page, not blind probing.
- A second minor oddity: the folder name is the scheduled date and can differ from the actual release date. `.../z1/20170305/` has `Last-Modified` 9 Mar 2017 and member timestamps of 8 Mar 2017; the March 2017 release was therefore 9 March, not 5 March (a Sunday).

| Supports | Source | URL | Bytes | SHA-256 | Retrieved (UTC) |
|---|---|---|---|---|---|
| Release-dates listing | Federal Reserve, Z.1 release dates | https://www.federalreserve.gov/releases/z1/release-dates.htm | 186942 | `6877ddda479347ba163f58b03593801363392acc62732e53b846e3fbfaf2ace8` | 2026-11-04T01:04:31Z |
| June 2026 CSV zip | Federal Reserve | https://www.federalreserve.gov/releases/z1/20260611/z1_csv_files.zip | 8075952 | `b23e0ad3a5afc700c3608863707b0514e6e119b43efeaf89ec6e746da8dbea24` | 2026-11-04T01:04Z |
| Release timing, next release | Federal Reserve Z.1 landing page | https://www.federalreserve.gov/releases/z1/ | 121001 | `7e1bcd1ac8d213714737c5b11f5f1a442be7f2d3103e5adfecf54450e871b2a3` | 2026-11-04T00:59:49Z |

Quote (landing page): "The next Z.1 release will be Thursday, December 10, 2026, at 12:00 noon." (Note: the current release on the landing page is the 11 September 2026 release, 2026:Q2, which postdates the June vintage the repo uses as "previous".)

**Status: VERIFIED.** Fix needed: REPORT.md label (and run.py line 489) should say the member timestamp is a build date, and the vintage is 2026-06-11. scoring-protocol.md line 28 ("2026-06-11 release") is correct.

---

## 6. Z.1 archive depth and ALFRED

**Fed per-release CSV zips.** The release-dates page links `z1_csv_files.zip` for every release from **16 September 2016 (2016:Q2)** onwards: folders 20160916, 20161208, 20170305, 20170608, ... through 20260611 (about 40 listed CSV zips; the September 2026 release at 20260911 also downloads, 8,336,582 bytes). Earlier releases are listed as HTML and PDF only; the listing offers no CSV before the 20160916 folder, and direct requests for `z1_csv_files.zip` in 20160609, 20160310 and 20150611 return **404**. The listing goes back to 1996 (folders 19960912 to 20160609 are HTML/PDF).

Probed and confirmed to exist (HTTP 200, `Content-Length`, `Last-Modified`): 20160916 (6,201,297 bytes; members dated 15 Sep 2016), 20161208 (6,241,221), 20170305 (6,249,231), 20180308 (5,939,826), 20200312 (6,290,691), 20220310 (6,830,183), 20240307 (7,170,558), 20250313 (7,431,488), 20260109 (7,511,138), 20260319 (7,546,422), 20260611 (8,075,952). The 2016 zips (downloaded and opened) contain `csv/*.csv` per-table files (566 members, for example `csv/l100.csv`), a different member layout from the 2026 zip (574 members, `csv/F4_1_s.csv` etc. naming), so a parser written for the 2026 layout (`validation/zparse.py`) should be tested on old zips before use. I did not parse any old zip's values.

Practical depth: **about 10 years (Sep 2016 to Jun 2026), about 40 vintages**, which is too short for a 1990Q1 real-time start (scoring-protocol.md line 54) and covers only the 2016-onward vintages. Before 2016 only PDF/HTML tables (not machine-readable CSV) were seen on the listing page; I did not check whether those older folders contain other machine-readable files (for example `Z1.csv`, `z1_data`); the `Z1.csv` request for 20160609 and 20160916 returned 404.

**ALFRED / FRED API vintages** (queried via the FRED API `series/vintagedates`, `realtime_start=1776-07-04`, `realtime_end=9999-12-31`; key set in the environment, never recorded; retrieved 2026-11-04T01:05Z):

| FRED series | Title (FRED) | Earliest vintage | Vintages | Latest vintage | Note |
|---|---|---|---|---|---|
| `HHMSDODNS` | Households and Nonprofit Organizations; One-to-Four-Family Residential Mortgages; Liability, Level (Z.1), observations from 1945Q4 | **2010-06-10** | 67 | 2026-09-11 | First vintage returned 242 observations, 1949Q4 to 2010Q1 (last value 10,235.76, millions of dollars). |
| `CMDEBT` | Households and Nonprofit Organizations; Debt Securities and Loans; Liability, Level (Z.1), from 1945Q4 | **1999-06-11** | 111 | 2026-09-11 | First vintage returned 185 observations, 1953Q1 to 1999Q1 (last value 6,041.37, millions of dollars). |
| `TOTALSL` | Total Consumer Credit Owned and Securitized (G.19, not Z.1), monthly | 1996-12-06 | 359 | 2026-10-07 | For the monthly G.19 consumer credit, not a Z.1 series. |
| `HDTGPDUSQ163N` | Household Debt to GDP for United States (BIS-based ratio), from 2005Q1 | 2011-11-01 | 54 | 2026-10-01 | Not Z.1. |

The 2010-06-10 first vintage of `HHMSDODNS` matches the Fed's Z.1 release of 10 June 2010 (the date in the A1 sources.md URL for FAS 166/167). `HHMDODNS` (a series name I tried) does not exist in ALFRED.

Key point: ALFRED vintages for Z.1 level series are series-specific and the earliest vintage is 2010-06-10 for the household mortgage series versus 1999-06-11 for total household debt. Whether other component series (the C1 features) have vintages, and from when, is **not verified** beyond these two Z.1 series; each C1 feature must be checked individually. The project's own target (public share of household credit-market debt, built from Z.1 codes such as FL154104015) is not a FRED series, as scoring-protocol.md already says.

| Supports | Source | URL (key omitted) | Bytes | SHA-256 (first 16 hex) |
|---|---|---|---|---|
| Vintage dates | FRED API `series/vintagedates` | https://api.stlouisfed.org/fred/series/vintagedates?series_id=HHMSDODNS | 1029 | `54bac2ebbfa81b8a` |
| Vintage dates | FRED API `series/vintagedates` | https://api.stlouisfed.org/fred/series/vintagedates?series_id=CMDEBT | 1602 | `5c2e94ac3d8cc882` |
| Series titles | FRED API `series` | https://api.stlouisfed.org/fred/series?series_id=HHMSDODNS (and CMDEBT, TOTALSL, HDTGPDUSQ163N) | 1399 / 1381 / 734 / 921 | `5a36f278e4a45f6a`, `d8f249f315b3b2c8`, `c85e0a9cd679258f`, `b5d681903ad8d2cd` |
| First-vintage content | FRED API `series/observations` at the earliest vintage | https://api.stlouisfed.org/fred/series/observations?series_id=HHMSDODNS&realtime_start=2010-06-10&realtime_end=2010-06-10 (and CMDEBT at 1999-06-11) | 23823 / 18302 | `eaf10f6243589aca`, `ddb176de85bdc88c` |
| Older release-folder zips | Federal Reserve | https://www.federalreserve.gov/releases/z1/20160916/z1_csv_files.zip | 6201297 | `d814a067af11cb7545168ef5ef874ddb207901db9c2a21e02cc57a45c4924331` |
| | | https://www.federalreserve.gov/releases/z1/20161208/z1_csv_files.zip | 6241221 | `4cfe9f56435dbbe8a8cdde8bc2dde8255ce4637389cd1149e02d2e5b63f9f798` |
| | | https://www.federalreserve.gov/releases/z1/20170305/z1_csv_files.zip | 6249231 | `1b730b3a987f1401a72708e0a1566d3382bc8c1cec184afe6c6f4df89bf2bf74` |

**Status: VERIFIED** for the existence and depth of Fed CSV zips (2016 onward) and for the earliest ALFRED vintages of the two Z.1 series above. **NOT VERIFIED:** values in older zips; other Z.1 component series on ALFRED; whether older HTML/PDF folders carry machine-readable data.

**Effect on the drafts.** (i) scoring-protocol.md line 29: "How far back these folders have usable CSVs is not verified" can now read "per-release CSV zips exist from the 16 Sep 2016 release (20160916); earlier releases are HTML/PDF only on the Fed site". (ii) The 1990Q1 real-time evaluation start (line 54) cannot be backed by Fed CSV vintages before 2016, and ALFRED coverage for at least the household mortgage series starts only in June 2010. That start date needs a different justification (latest-vintage data with a declared "not real-time" label), or the evaluation window must start later for any series with vintages.
