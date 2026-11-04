Review entries from the analysis track after the coordinator's fold of R-20261104-ana-1..21; the coordinator moves them into `claims/review-log.md` on merge.

### R-20261104-ana-22 · skeptic · research/a8_international/README.md:9,11,18 (US holder column (a))
- **Objection:** Column (a) is defined as "held by publicly owned lenders" (README:9, compare.py:11), but the US 56.4% is the project's Z.1 public bucket, which includes `gse_agency` = GSE and agency *pools*. Those pools are guarantees on MBS that are mostly held by private investors, so the US (a) figure is largely a risk-bearer (guarantee) measure. Germany's 29.1% is strict ownership. If the US convention were applied to Canada, NHA MBS/CMB (CMHC guarantees-in-force $573B, in the same CMHC release) would count as public holdings. Line 18 ("the holder measure misleads across systems") draws its contrast from this asymmetry.
- **Severity:** blocker
- **Evidence:** pipeline/series_catalog.yaml:17 (`gse_agency: {label: "GSEs & agency pools", public: true}`); compare.py:45 uses a2 public_share_gross_pct_last (56.386); CMHC page text "Guarantees-in-force ($B) 577 573".
- **Proposed resolution:** compute a strict US holder share (federal direct + GSE retained portfolios + state/local, with Fed MBS treated explicitly) or relabel the US (a) cell as "Z.1 holder view incl. guaranteed pools, not comparable". Then revisit line 18.
- **Status:** open

### R-20261104-ana-23 · skeptic · research/a8_international/README.md:17 ("The US is the outlier on the headline measure even before the gaps are filled")
- **Objection:** Only the US has a computed (b) share. Every gap (student loans in CA/DK/UK/DE, private-insurer federal backing in CA, Help to Buy/MGS in UK, KfW stock and BAföG in DE) can only raise the other countries' shares. So "outlier" is true only if those unsourced gaps are small, which no sourced bound shows. The phrase "even before the gaps are filled" reverses the logic. The Canadian 19.8% is a share of residential mortgages (incl. multi-unit), not of household credit, so it is not on the US denominator either.
- **Severity:** major
- **Evidence:** comparison.csv: risk_b_low/high null for CA, DK, UK, DE; national_figures.csv CA cmhc_share_of_residential_mortgages note.
- **Proposed resolution:** reword to what is shown: "the US is the only one of the five with a majority public risk-bearer share on any sourced measure; no other country's share can be computed". Alternatively, source upper bounds for the gaps (e.g. UK student-loan stock, CA private insurers' insurance-in-force) before claiming outlier status.
- **Status:** open

### R-20261104-ana-24 · skeptic · research/a8_international/README.md:18; CROSSWALK.md:47 (Sparkassen as "private risk" vs GSEs as public)
- **Objection:** The headline definition is "public body takes the credit loss". Sparkassen and Landesbanken are public-law institutions (Anstalten des öffentlichen Rechts) owned by municipalities and Länder, and they absorb the loss on their own books. Under the literal definition that is a public body taking the loss. The US side counts losses at the GSEs (shareholder-owned corporations in conservatorship) as public. The rule that separates the two (an explicit state guarantee or backstop, e.g. the PSPA, vs. none since Gewährträgerhaftung ended in 2005) is not stated and has no national source. "That 29.1% is private risk" is asserted without a quote.
- **Severity:** major
- **Evidence:** README.md:18; national_figures.csv has no DE row on Sparkassen liability/guarantee status.
- **Proposed resolution:** define (b) precisely (state or state-guaranteed entity absorbs the loss beyond the lender's own capital?), apply it to GSEs and Sparkassen alike, and source the German guarantee status (e.g. the Bundesbank or DSGV statement on the 2005 end of Anstaltslast/Gewährträgerhaftung).
- **Status:** open

### R-20261104-ana-25 · skeptic · research/a8_international/CROSSWALK.md:1-3; README.md:5
- **Objection:** README:5 points to CROSSWALK.md as "Definitions by country" and the crosswalk is the first acceptance item. But CROSSWALK still says every row is unverified, "written from general knowledge", with sources "blocked today", and it predates Eleonora's (a)/(b) decision. It does not carry the DK and KfW quotes that were since sourced, and its Canada "partial" federal backing of private insurers remains unsourced.
- **Severity:** major
- **Evidence:** CROSSWALK.md:3 and column header "National source to check (blocked today)"; AVAILABILITY.md:84-86 shows the hosts reachable later.
- **Proposed resolution:** rewrite the crosswalk against the now-sourced quotes with an (a)/(b) column per country, and mark which cells remain unverified. Until then README should not cite it as the definitions.
- **Status:** open

### R-20261104-ana-26 · skeptic · research/a8_international/README.md:15,17; national_figures.csv DE kfw_credit_risk_bearer
- **Objection:** A single programme sheet (Wohneigentumsprogramm 124/134, Stand 06/2023) is generalised to "KfW loans carry the on-lending bank's liability" and to "none found" for Germany at end 2025. KfW products not routed this way (e.g. the KfW-Studienkredit, which I understand is lent by KfW itself; not verified here) would be public risk. Separately, the (a) numerator leaves out the publicly owned blocks in the same table I.7: "Banken mit Sonder-, Förder- und sonstigen zentralen Unterstützungsaufgaben", about 17.8bn EUR to individuals in Q4 2025 by my reading (+1.1pp, which moves 29.1% at display precision), and the public Landesbausparkassen inside "Bausparkassen" (about 172bn EUR in total).
- **Severity:** major
- **Evidence:** scratchpad de2/i7.txt, Förder block Q4 2025 row "5 327  17 817 ..."; Bausparkassen row "19 365  172 111 ..."; (438448+13519+17817)/1551414 = 0.303.
- **Proposed resolution:** either include the promotional-bank block in (a) or state why it is excluded. Limit the KfW statement to programmes 124/134 and source the Studienkredit risk bearer. Note the LBS gap.
- **Status:** open

### R-20261104-ana-27 · skeptic · research/a8_international/national_figures.csv:10 (DE denominator); README.md:13,24
- **Objection:** The values check out against the raw files: CA 2,405,386 and 666,237 (REF_DATE 2025-10 = quarterly Q4); CMHC 471 and 19.8%; DK 507,711.4 and 2,081,929.1; UK 1,943,184 (amounts outstanding, Dec 2025); DE 1,551,414, 438,448 and 13,519; all hashes match. Three keys and labels are still off. (i) The DE key says column "Total (insgesamt)", but 1,551,414 is column 15 "zusammen" under "unselbständige und sonstige Privatpersonen"; insgesamt (col 1) is 3,543,546. (ii) That denominator excludes self-employed individuals and NPISH, whereas the US (HH&NP), DK (X400) and UK ("individuals") include them to varying degrees. (iii) README:13 says "80.4% of household loans", but the denominator is bank + mortgage-bank loans only (the register row says so correctly).
- **Severity:** minor
- **Evidence:** de2/i7.txt l.100-138; series_catalog.yaml:32; register a8_dk_mortgage_bank_share.
- **Proposed resolution:** fix the cell key, state the DE scope exclusion in Limits, and align README:13 with the register wording.
- **Status:** open

### R-20261104-ana-28 · skeptic · research/a8_international/README.md:5,14,23,26
- **Objection:** Small inaccuracies. "A computable share for two of the five" holds only for the holder measure; on the headline (b), only the US is computable. UK gaps also include Help to Buy equity loans and the Mortgage Guarantee Scheme (sources.md:106), which the README omits. "Year-end 2025 throughout" is wrong for the DK statement (2013) and the KfW sheet (06/2023) that carry the (b) "none" cells. The UK URL uses Dateto=now and the DK URL is a POST endpoint with no recorded query body; with raw files not committed, the hashes cannot be re-verified.
- **Severity:** minor
- **Evidence:** comparison.csv; sources.md:89,97,100,106.
- **Proposed resolution:** reword these lines, and either commit the query bodies with fixed date URLs or commit the raw files under data/a8/.
- **Status:** open

### Responses to R-20261104-ana-22 to -28 (analysis track, 2026-11-04)
- R-22 (blocker): accepted. The US 56.4% is no longer shown as a holder share; it is labelled as the public bucket including guaranteed pools. A holder-only US share was attempted by subtracting the pool sector and discarded before use: since FAS 166/167 most investor-held GSE MBS sit in the Enterprises' own Z.1 lines, so the series used cannot separate them. US (a) is recorded as not computable.
- R-23: accepted. "Outlier" claim removed; README says no ranking is possible yet and that every gap can only raise the other countries' shares; Canada's 19.8% is labelled a share of residential mortgages.
- R-24: accepted. "Private risk" for Sparkassen removed; whether losses at publicly owned banks count as public is now Q7 for Eleonora.
- R-25: accepted. CROSSWALK.md rewritten: each cell now cites its source or is marked unverified.
- R-26: accepted. KfW statement narrowed to programme 124/134; promotional banks (€17,817M, verified in the Bundesbank table, column 15, Q4 2025) added to Germany's holder share (30.3%); public building-savings banks noted as not separable.
- R-27: accepted. German cell labelled column 15 with its exclusions; Denmark's 80.4% labelled as a share of bank and mortgage-bank loans.
- R-28: accepted. Dates of the qualitative statements given; UK schemes listed as gaps; Statbank POST body recorded in sources.md and the BoE "Dateto=now" caveat stated.
