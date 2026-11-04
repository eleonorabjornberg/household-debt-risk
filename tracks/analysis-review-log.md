Review entries from the analysis track; the coordinator moves them into `claims/review-log.md` on merge (renumbering if ids collide).

### R-20261104-1 · skeptic · research/a2_net_exposure/README.md:16 (a2_public_share_net_lower_2025q4, a2_net_ff_lower_hh)
- **Objection:** The table labels G − cumulative CRT RIF as "Net, lower bound" and the public share as "at least 55.2%". That is a lower bound only on net-of-CRT exposure. Once mortgage insurance is netted (FHFA PMI RIF is 12.5% of 2023 gross by the same method), true net exposure can be well below $6.05T and 55.2%. Read alone, the table row says the public share cannot be below 55.2%.
- **Severity:** major
- **Evidence:** README.md:13-16 table header "Net, lower bound (all issued CRT still in force)"; README.md:21 and net_exposure.csv 2023 pmi_issued_pct_of_gross = 12.5191; register rows 4 and 8 say "at least".
- **Proposed resolution:** Relabel as "net of CRT only, before mortgage insurance" in the table and in register claims 4 and 8, and add one sentence saying PMI could lower net further.
- **Status:** open

### R-20261104-2 · skeptic · research/a2_net_exposure/README.md:16,19 (a2_public_share_gap_pp)
- **Objection:** "Public share net" is (public principal − RIF)/S. That mixes loss capacity with principal and treats $1 of RIF as $1 of principal moved to the private side, so 55.2% is not a share of anything observable. Line 19 adds a caveat, but the table cell at line 16 (and register row 8) carries the number without it.
- **Severity:** major
- **Evidence:** net_exposure.py:85 `100 * (pub - crt["cum_rif_musd"] * a) / s`; METHOD.md:15.
- **Proposed resolution:** Put the "loss capacity against principal" caveat in the table and in the register claim text, or report the gap as RIF/S rather than as a "share".
- **Status:** open

### R-20261104-3 · skeptic · research/a2_net_exposure/README.md:20
- **Objection:** The FHFA "majority" quote is attributed to CRT ("the share transferred on covered loans is much larger"). FHFA says "Through CRT **and mortgage insurance**, the majority…". The claim that the CRT slice is "where most stress losses fall" is unsourced.
- **Severity:** major
- **Evidence:** sources.md:9 (4Q2019 quote); same wording in the Dec 2016 extract, line 38.
- **Proposed resolution:** Quote FHFA in full, including "and mortgage insurance", and source the stress-loss statement or label it as an assumption.
- **Status:** open

### R-20261104-4 · skeptic · research/a2_net_exposure/README.md:21 (a2_pmi_cum_rif)
- **Objection:** "Mortgage insurance is larger than CRT in RIF terms" contradicts the project's own source: FHFA 4Q23 p.8 says "the RIF figures for these two categories are not strictly comparable".
- **Severity:** minor
- **Evidence:** sources.md:13 quote.
- **Proposed resolution:** Drop the comparison or carry FHFA's caveat next to it.
- **Status:** open

### R-20261104-5 · skeptic · research/a2_net_exposure/README.md:22, METHOD.md:14 (a2_crt_ref_upb_over_gross)
- **Objection:** The 1.1× is explained only "because refinanced loans are counted again". FHFA's own footnote says the same reference UPB may back both a STACR and an ACIS deal, and cumulative UPB also keeps loans that have paid off without refinancing.
- **Severity:** minor
- **Evidence:** CRT-Progress-Report-4Q22 extract, Freddie table footnote 5: "The same reference pool UPB may back STACR and ACIS transactions."
- **Proposed resolution:** List all three causes; drop "because".
- **Status:** open

### R-20261104-6 · skeptic · research/a2_net_exposure/crt_fhfa.csv:7-8
- **Objection:** The PMI UPB for 2018 and 2019 uses the rounded text figures ($1.2T, $1.6T). The chart boxes in the same reports give $1,231B and $1,570B, and 2020 onward uses the boxes. The column is not used in any output; RIF values match.
- **Severity:** minor
- **Evidence:** 4Q18 extract line 611 "Total $1,231"; 4Q2019 extract shows "Total $1,570".
- **Proposed resolution:** Use the box values, or document the mixed basis.
- **Status:** open

### Responses (analysis track, 2026-11-04)
- R-20261104-1: accepted. Table header and register rows now say "net of CRT only, mortgage insurance not netted"; README states 55.2% is not a floor once MI is netted.
- R-20261104-2: accepted. Table header now says principal less CRT loss capacity; register claims say "RIF subtracted from principal".
- R-20261104-3: accepted. The FHFA "majority" quote is now attributed to CRT and mortgage insurance together; the unsourced "most stress losses fall" clause is removed.
- R-20261104-4: accepted. README quotes FHFA's "not strictly comparable".
- R-20261104-5: accepted. README and METHOD now give all three reasons (paid-off loans kept at issuance balance, refinanced loans counted again, STACR/ACIS sharing a pool).
- R-20261104-6: noted, not changed. The column is unused; the basis column already says the 2018–19 PMI UPB is the rounded text figure.
