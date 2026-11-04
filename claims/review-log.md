# Review log

Objections raised by the review subagents (`.claude/agents/skeptic.md`, `quant-reviewer.md`, `editor.md`) and by people, with their resolutions. Append only: entries are never deleted or rewritten; a resolution is added under the entry.

Entry format:

```
### R-<YYYYMMDD>-<n> · <reviewer> · <target file or claim_id>
- **Objection:**
- **Severity:** blocker / major / minor
- **Evidence:**
- **Proposed resolution:**
- **Status:** open | resolved (<date>, by <who>): <what was done> | rejected (<date>, by <who>): <why>
```

Resolutions are written by the main session or Eleonora, never by the reviewer that raised the objection.

---

### R-20261104-1 · quant-reviewer · research/a1_gfc_decomposition/README.md (growth vs retreat split)
- **Objection:** The headline "public growth 7.1 pp, private retreat 6.0 pp" depends on the chosen weighting and the ordering reverses under the alternatives. The endpoint identity weights by the start share P0 (36.1%), which favours the public term while P rises. Chaining the same identity by quarter (the script's own path.csv) gives public 6.27 pp, private 6.83 pp; a Shapley split of the two counterfactuals gives public 6.25, private 6.87. The README says the split "is exact" but does not mention that it depends on the path. The docstring says "chained and endpoint totals both equal P1 - P0", which holds only for the grand total, not for groups. The results.json groups and the 2011Q4 row of path.csv disagree with no note: Ginnie 3.81 vs 3.29, PLS/mREITs 4.93 vs 5.71, student loans 1.94 vs 1.62. The decision doc rejected Shapley for "no gain", but here it changes the headline.
- **Severity:** major
- **Evidence:** Reran in the scratchpad by importing decompose.py; no repo files were written. Endpoint public/private 7.127/5.979; chained 6.274/6.832; the Shapley public term is 6.245. path.csv 2011Q4 row: ginnie_pools 3.2879, private_label_and_mreits 5.7088.
- **Proposed resolution:** Report endpoint, chained and Shapley side by side, or call the split "roughly even (6.0-6.9 pp private, by method)". State that group totals depend on the path, and fix the docstring.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session, on Eleonora's decision): Eleonora chose Shapley (2026-11-04). README headline is now Shapley public 6.2 / private 6.9 pp, with the endpoint identity (7.1/6.0) and chained Shapley (6.2/6.9) reported in results.json `sensitivity` and named in the README. Docstring fixed.

### R-20261104-2 · quant-reviewer · docs/decisions/a1-decomposition.md
- **Objection:** The design was not set before the results. The decision doc was added in the same commit as decompose.py, results.json and the CSVs (f8b7ddc, 2026-11-04T00:30:57Z). It quotes the result (+13.1 pp) and is "Decided by: Claude", so it is not Eleonora's design (the authorship rule). The README cites it as "Method decision" and declares neither point.
- **Severity:** major
- **Evidence:** `git log --name-status -- docs/decisions research/a1_gfc_decomposition`.
- **Proposed resolution:** Say in the README that the method was chosen at the same time as the results, by Claude, and is awaiting Eleonora's decision. Record her choice in PLAN.md "Decisions taken".
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session, on Eleonora's decision): Decision note rewritten: decided by Eleonora, 2026-11-04 (Shapley); notes the first draft was Claude's choice made alongside the results. Decision added to PLAN.md "Decisions taken".

### R-20261104-3 · quant-reviewer · research/a1_gfc_decomposition/README.md (counterfactual comparison)
- **Objection:** The comparison with findings.md item 4 is not like for like. The 6.1 pp counterfactual (private held at 2007Q4) measures the public-growth side; it reproduces at 6.11. Under it, private retreat is the remaining 6.99 pp, not 6.0. The README puts 6.1 right after the 6.0 private figure, which invites reading the two as the same quantity. "Both say about half" holds only loosely (46% vs 53%).
- **Severity:** minor
- **Evidence:** pub_t1/(pub_t1+priv_t0) - P0 = 6.115 pp; residual 6.991 pp.
- **Proposed resolution:** State that 6.1 pp is the counterpart of the 7.1 pp public term, and give the counterfactual's private piece (7.0 pp).
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README Limits item now says 6.1 pp is the public side of a private-held-fixed split and both views put about half on private retreat.

### R-20261104-4 · quant-reviewer · research/a1_gfc_decomposition/README.md (causal wording)
- **Objection:** An accounting split cannot carry causal or counterfactual statements, but the README makes some. "Conservatorship ... didn't change how much they held" and "doesn't fit these data" need a counterfactual (the GSEs' holdings without conservatorship), which this method cannot supply and the README itself defers to A7. "Their share rose mostly because private holders shrank around them" is the own-share view (3.9 pp vs 1.4 pp growth term) restated as a cause. The README's limit "accounting, not a causal estimate" is contradicted in "What this changes".
- **Severity:** major
- **Evidence:** README "What this changes", bullets 2-3.
- **Proposed resolution:** Rephrase descriptively. For example: "GSE balances rose $278B; most of their own-share gain is arithmetic from a shrinking denominator; whether conservatorship changed holdings is A7."
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Reworded: conservatorship bullet now says the data cannot test the claim; GSE balances (+$278B) and the chained path are stated descriptively.

### R-20261104-5 · quant-reviewer · research/a1_gfc_decomposition/test_decompose.py, decompose.py
- **Objection:** The tests would not catch a missing holder. They exercise contrib() only, on synthetic data, and do catch a flipped sign through the exact-sum check. cells(), the PUBLIC_* lists, the group partition and the own-share view are untested. The README says the script "asserts ... that the cells reproduce the scope total", but scope_gap is only recorded, not asserted. A dropped public holder would move the share with no error. The gap is in fact about 0, at most 4e-9 $M across the window.
- **Severity:** minor
- **Evidence:** decompose.py main(): `scope_gap = ...` with no assert; tests cover contrib() only. Both tests pass.
- **Proposed resolution:** Assert scope_gap < tolerance at every quarter in [t0, t1]. Add a test that the groups partition the cell columns, and one that removing a cell trips the scope check.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): decompose.py now asserts the scope reconstruction at every quarter in [t0, t1] and that the groups partition the cells; two Shapley tests added. The remove-a-cell test is not added (the per-quarter scope assert covers it at run time).

### R-20261104-6 · skeptic · a1_ff_chained_2008q3 (research/a1_gfc_decomposition/README.md, "What this changes" bullet 2)
- **Objection:** "Fannie and Freddie had contributed 1.3 pp by 2008Q3, before the September 2008 conservatorship" gets the timing wrong. 2008Q3 is the 30 Sep 2008 stock, more than three weeks after the 6 Sep conservatorship and 7 Sep PSPAs. The last quarter-end before conservatorship is 2008Q2, at 1.1 pp. The conclusion ("came early") survives, but the sentence and the register row both attach a post-event number to a pre-event label.
- **Severity:** major
- **Evidence:** path.csv: 2008Q2 fannie_freddie 1.0971; 2008Q3 1.3412. sources.md FHFA row: conservatorship 6 Sep 2008.
- **Proposed resolution:** Say "1.1 pp by 2008Q2, the last quarter-end before conservatorship". Update the register row, and note that quarterly stocks cannot place within-quarter events.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README and register now say 1.1 pp by 2008Q2, the last quarter-end before conservatorship (row a1_ff_chained_2008q2).

### R-20261104-7 · skeptic · a1_pls_change_usd, a1_pls_pp (README "Which private holders shrank")
- **Objection:** The Result section presents "private-label securitization and mortgage REITs held $1.71T less ... 4.9 pp" with no qualifier, but a large part is FAS 166/167 consolidation onto banks and finance companies, not a retreat. The README's own Limits bullet says the split between private lines around 2010Q1 is accounting. The headline sentence and both register rows ignore that bullet. Only the private total (6.0 pp under this weighting) is robust to the reclassification.
- **Severity:** major
- **Evidence:** path.csv 2009Q4 to 2010Q1: private_label_and_mreits 2.236 to 4.330 (+2.09 pp in one quarter), banks_and_credit_unions 0.869 to -0.064, other_private 0.679 to 0.278. decomposition.csv: consumer-credit ABS issuers 652.5 to 46.2 $bn (-606), while bank consumer credit rose +298 and finance-company consumer credit +110.
- **Proposed resolution:** Report only the private total as a finding. If the PLS line is kept, give it net of the 2010Q1 step, or caveat it in the same sentence. Re-word the register claim text.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): PLS sentence now carries the FAS 166/167 caveat in place and says the private total is unaffected; register claim text reworded.

### R-20261104-8 · skeptic · README "The largest public piece is FHA/VA, not the GSEs"
- **Objection:** This treats holdings in Ginnie pools as federal risk, and "largest" is ambiguous. (a) "Largest" holds only for the change in the share. In stock terms, Fannie+Freddie held $4.34T in 2011Q4 against Ginnie's $1.13T. (b) "Explicitly federal" overstates the risk transfer. VA and USDA guarantees are partial, and Ginnie issuers/servicers bear losses beyond them. FHA/VA loans held directly by banks, including delinquent loans bought out of Ginnie pools, are federally insured but sit in "private", so Ginnie pool holdings are not the federal FHA/VA exposure.
- **Severity:** major
- **Evidence:** decomposition.csv 2011Q4: Fannie 2680.3 + Freddie 1658.9 vs Ginnie 1129.0 $bn. README Limits bullet 1 concedes the bank-held FHA/VA point, but bullet "What this changes" 1 does not.
- **Proposed resolution:** "The largest public contribution to the change came from Ginnie Mae pools." Drop "explicitly federal", or qualify it (FHA full insurance; VA/USDA partial). Point to A2 for exposure.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): README: "the largest public increase was in Ginnie Mae pools", with 2011Q4 holdings ($4.34T GSEs vs $1.13T Ginnie) and the partial VA/USDA guarantee caveat.

### R-20261104-9 · skeptic · README conservatorship bullet ("doesn't fit these data")
- **Objection:** The measure cannot test the claim, which is separate from the causal-wording point in R-20261104-4. The catalog classes GSEs and their pools as public at every date (`risk_buckets.gse_agency.public: true`), so a holdings share cannot register a move of GSE credit risk from shareholders and an implicit guarantee to Treasury under the PSPAs. "Doesn't fit these data" should be "these data cannot speak to it". Also, the PSPAs backed the GSEs' guarantees on about $4T of MBS pools, not only "debt the GSEs already held". The bullet misstates what conservatorship changed.
- **Severity:** major
- **Evidence:** pipeline/series_catalog.yaml:17 (gse_agency public: true) and :50-51 (FL403065105, FL413065105 both gse_agency). README "What this changes" bullet 3.
- **Proposed resolution:** Recast as a definitional limit: "Because GSEs count as public throughout, this decomposition cannot detect a conservatorship ratchet; that is a question about who bears GSE losses (A2/A7)."
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Recast as a definitional limit ("the data are silent, not contrary"); counterfactual left to A7.

### R-20261104-10 · skeptic · README "Dated policy events" table
- **Objection:** The "lines up with" column is assigned by subject, not by any observed change in the path, and some rows do not align. Federal student loans had moved 0.03 pp by 2008Q2 (ECASLA, May 2008) and 0.09 pp by 2008Q4. Most of the component (0.66 to 1.62 pp) came after SAFRA's 30 Jun 2010 cutoff, and the Z.1 line cannot separate ECASLA purchases from Direct Loan originations. Ginnie rises roughly steadily all window, so any date "lines up". Fannie/Freddie rose before HERA and peaked in 2009Q4, after both acts.
- **Severity:** minor
- **Evidence:** path.csv federal_student_loans: 2008Q2 0.0322, 2008Q4 0.0917, 2009Q4 0.5229, 2010Q2 0.6618, 2011Q4 1.6222. ginnie_pools increments roughly 0.15-0.37 pp per quarter throughout.
- **Proposed resolution:** Rename the column "related component". For each component, give the quarters of its largest steps, and state that quarterly stocks cannot date effects within a quarter.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Table intro says events are matched by topic, not by breaks, with the student-loan example (0.03 pp by 2008Q2); column renamed "Component it lines up with".

### R-20261104-11 · skeptic · decompose.py PUBLIC_MORT "Ginnie Mae pools (FHA, VA, USDA)"
- **Objection:** FL413065133 is the Z.1 "FmHA pool, including ... mortgages held by the Federal Financing Bank" line, not a Ginnie Mae pool. It is grouped under the Ginnie label. It is 0 in 2007Q4 and 2011Q4, so no number moves, but the label misdescribes the series if it is ever non-zero.
- **Severity:** minor
- **Evidence:** `unzip -p data/validation/FRB_Z1_csv.zip Z1.csv | grep FL413065133`: "one-to-four-family residential mortgages held in a Federal Farmers Home Administration (FmHA) pool, including ... held by the Federal Financing Bank". Value 0.0 at both endpoints.
- **Proposed resolution:** Relabel the cell "Ginnie Mae and FmHA pools", or split FmHA out.
- **Status:** open
- **Resolution:** resolved (2026-11-04, by main session): Label is now "Ginnie Mae pools (FHA, VA, USDA) and FmHA pools"; README Limits notes FmHA is zero at both endpoints.

### R-20261104-12 · skeptic · research/a1_gfc_decomposition (vintage coverage)
- **Objection:** The issuer-level split (Ginnie vs Fannie vs Freddie vs FHLB vs Other GSEs) cannot be checked against the June 2026 vintage. The committed previous file is the per-table zip, which lacks FL403065110/120/130 and FL413065110/123/133/143. The README "Revisions" bullet does not say this. At bucket level nothing moves: total, growth/private split, gse_agency, student loans, PLS and the dollar changes are identical to 3 d.p. across vintages. So the risk is low but unverified.
- **Severity:** minor
- **Evidence:** Scratchpad rerun, nothing written to the repo. Sep vs Jun vintages: P0 36.115/36.115, P1 49.221/49.221, pub 7.127/7.127, gse_agency 5.003/5.003, PLS $-1706.7bn both. load_table_zip reported those 7 issuer ids as missing in prev_z1_csv_files.zip.
- **Proposed resolution:** State in Revisions that the issuer split is checked only at bucket level, or obtain the June Z1.csv long file.
- **Status:** open
