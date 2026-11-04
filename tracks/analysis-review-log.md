# Analysis track review log (skeptic entries, parallel-track sessions; append only)

### R-20261104-ana-29 · skeptic · research/a3_pre1952/README.md:25; pre1945.py:16-17; claims a3_overlap_gap, a3_share_1945_hist
- **Objection:** "1945, the one year both sources exist" is false: HS N 262-272 runs to 1970 (p.647), N 273 to 1970 (p.649), X 551 to 1970 (p.1009). Extending the same overlap to 1946-1950 with the source's own values breaks the asserted 0.25 pp tolerance in 2 of 6 years, so the 0.035 pp agreement at 1945 looks like luck, not validation.
- **Severity:** major
- **Evidence:** Read from page images (p.647, 649, 1009) and Z.1 annual (vintage 2026-09-11). Hist (HOLC+FNMA)/(N273+X551) minus Z.1 federal-direct share, pp: 1945 +0.035, 1946 +0.020, 1947 -0.272, 1948 -0.240, 1949 +0.430, 1950 +0.027.
- **Proposed resolution:** Transcribe 1945-1952 (or later) from HS and report the overlap year by year. Either widen the tolerance with a stated reason, or put an error band derived from the overlap on the B points. Correct "the one year both sources exist".
- **Status:** open

### R-20261104-ana-30 · skeptic · research/a3_pre1952/README.md:24-25; pre1945.py:9-12
- **Objection:** The 1945 share agreement comes from two component gaps that cancel. Z.1 consumer credit (FL153166000) is 20% above X 551, and Z.1 federal holdings are 4% above HOLC+FNMA. Consumer credit was a larger part of the denominator before 1945 (27% in 1929, 25% in 1935), so the X 551 vs Z.1 definition gap is not constant across the splice. The ratio-adjusted sensitivity (one 1945 ratio, 0.99) cannot show this.
- **Severity:** major
- **Evidence:** Z.1 .A 1945: FL153166000 = 6,800 vs X 551 = 5,665 (ratio 1.200; 1.166 in 1946, 1.115 in 1950). FL153165105 = 18,706 vs N 273 = 18.6 bn (1.006). FL313065105 = 894 vs N270+N271 = 859 (1.041).
- **Proposed resolution:** Check the denominator components separately. Report a sensitivity that scales X 551 up by about 1.15-1.20, which would put the 1935 share at about 13.4% instead of 14.1%. State why X 551 and Z.1 consumer credit differ.
- **Status:** open

### R-20261104-ana-31 · skeptic · research/a3_pre1952/README.md:24; pre1945.py:10
- **Objection:** N 271 (FNMA) is residential nonfarm holdings, which includes FHA-insured multifamily loans that FNMA bought from 1938. The denominator is N 273, 1-4 family only. The HOLC "not more than four families" argument covers N 270 but not N 271. The mismatch is visible in 1949: HS FNMA alone (806) is about the whole Z.1 federal home-mortgage figure (827).
- **Severity:** minor (FNMA was at most about 0.9 pp of the share before 1945)
- **Evidence:** p.647 N 271 heading "Federal National Mortgage Assn." under "Residential Nonfarm"; p.649 N 276-277 shows 5+ unit FHA-insured debt of 0.1-0.2 bn in 1939-1945.
- **Proposed resolution:** Find the 1-4 family part of FNMA holdings (FNMA/RFC reports), or label N 271 as including multifamily and give an upper bound on the effect.
- **Status:** open

### R-20261104-ana-32 · skeptic · research/a3_pre1952/README.md:9,13; pre1945.py:13-14; public_share_1925_1952.csv rows 1925-1932
- **Objection:** "It was zero until 1932, because no federal body held home mortgages" is stated as fact, but nothing checked it. Counter-candidates: the U.S. Housing Corporation (1918) sold its war housing in the 1920s and took back purchase-money mortgages (needs verifying); state veterans' home-loan programs (e.g. California, from 1921) were state holders. The Z.1 overlap also shows federal holders beyond HOLC+FNMA (Z.1 above HS by 4% in 1945 and 25-28% in 1947-48, e.g. the RFC Mortgage Co. from 1935). So the B points from 1935 to 1944 may be understated too.
- **Severity:** major (claim wording); the size of the effect is probably small
- **Evidence:** fed z1/hist ratios computed above (1945 1.041, 1946 1.037, 1947 1.276, 1948 1.252). N 272 "Other" and N 264 "Non-institutional" are not broken down.
- **Proposed resolution:** Reword as "no measured federal holder in the source". Check USHC and RFC Mortgage Co. holdings, or state them as unmeasured. Make "zero" read "not measured; at least zero" in the table.
- **Status:** open

### R-20261104-ana-33 · skeptic · research/a3_pre1952/README.md:9
- **Objection:** "Before the Second World War the public share was far higher than in 1952" is only true for 1933-1941; 1925-1932 are zero, below 1952. "The share then fell every year except 1942 as HOLC's book ran off" attributes the fall to HOLC alone. Denominator moves did part of the work: the 1942 rise is the fall in consumer credit (9,172 to 5,983), and the 1945-47 fall is mostly the postwar debt boom (the scope rose from 25.5 to 41.6 bn).
- **Severity:** minor
- **Evidence:** public_share_1925_1952.csv; hist_stats_1925_1945.csv x551 1941-1942; z1_annual_share.csv scope_musd.
- **Proposed resolution:** Write "from 1934 to 1941" and drop "as HOLC's book ran off", or decompose the change into numerator and denominator.
- **Status:** open

### R-20261104-ana-34 · skeptic · research/a3_pre1952/README.md:34; sources.md:15
- **Objection:** The timeline says the association was "established by the RFC", but the confirming source (RFC Final Report) says "chartered by the Federal Housing Administrator on February 10, 1938". The two sources assign the act to different bodies.
- **Severity:** minor
- **Evidence:** sources.md:15 quote. The statute dates (48 Stat. 128 ch. 64; 48 Stat. 1246 ch. 847; 52 Stat. 8 ch. 13; 58 Stat. 284 ch. 268; 63 Stat. 413 ch. 338) were re-read from the statute PDFs and are correct.
- **Proposed resolution:** "Chartered by the FHA Administrator, capitalised by the RFC".
- **Status:** open

### Responses to R-20261104-ana-29 to -34 (analysis track, 2026-11-04)
- ana-29 (major): accepted. Overlap extended to 1945–1951 (1952 left out: printed twice on two footnoted bases). Gaps are reported for every year (largest 0.50 pp, 1951); the 0.25 pp tolerance assert is removed rather than loosened.
- ana-30 (major): accepted. The offsetting component gaps are reported (Z.1/historical: federal about 1.12, consumer credit about 1.17, mortgages about 1.00, means over 1945–47). A component-adjusted estimate is added next to the main series; 1935 is now 14.1% (as printed) or 15.0% (scaled to Z.1). The adjustment raises, not lowers, 1935, because the federal ratio outweighs the consumer-credit ratio.
- ana-31: accepted. README says FNMA's figure includes some multifamily loans.
- ana-32 (major, wording): accepted. "Zero" is now "set to zero (no HOLC or FNMA yet)"; other pre-1945 public holders listed as not measured and not checked; README notes the 1935–44 shares may be understated.
- ana-33: accepted. "Before the Second World War" replaced by "in the mid-1930s"; the decline is attributed to HOLC run-off and swings in total debt.
- ana-34: accepted. Timeline: chartered by the Federal Housing Administrator and organised by the RFC.

### R-20261104-ana-35 · quant-reviewer · research/a4_breaks/breaks.py:235-237; README.md:15,17,33; test_breaks.py:38-44
- **Objection:** The Bai (1997) interval is inverted. argmax Z(s) is the limit of scale*(k_hat - k0), so k0 lies in [k_hat - q97.5/scale, k_hat - q2.5/scale]. The code returns [k_hat + q2.5/scale - 1, k_hat + q97.5/scale + 1]. That is the same thing only when phi = 1. With heterogeneous variances the long tail lands on the wrong side. The scaling (delta^2/w1), the phi = w2/w1 functional and the +/-1 are otherwise right. The planted-break test uses equal variances, so it cannot catch this.
- **Severity:** blocking (for the reported intervals; no H2 verdict changes)
- **Evidence:** Scratch Monte Carlo (T=300, k0=100, delta=1, sd 1 then 3, 300 reps). Coverage of k0: code 64%, inverted-corrected 89%. Real data, total: phi = 13.85, q2.5 = -3.1, q97.5 = 143.7, scale 1.144. Corrected interval 1952Q2 (truncated at the sample start) to 1967Q1, not 1965Q1 to 1997Q4. Mortgage: corrected 1952Q2 to 1969Q1, not 1963Q1 to 2019Q4. The consumer-credit intervals are affected too.
- **Proposed resolution:** Swap and negate the quantiles. Add a heteroskedastic coverage test. Regenerate results.json and the register rows, and rewrite README:17 ("upper end is far away"). Say that the lower bound is cut off at the sample start.
- **Status:** open

### R-20261104-ana-36 · quant-reviewer · docs/decisions/breaks.md:168; README.md:5
- **Objection:** The README and the DEVIATIONS constant declare a deviation (simulated critical values). The frozen file still says "Deviations: None yet". The pre-registration requires a dated entry there.
- **Severity:** should fix
- **Evidence:** breaks.md:168-169; breaks.py:57.
- **Proposed resolution:** The coordinator or Eleonora adds a dated Deviations entry: simulation design, T=600, 2000 reps, seed, and the 0.95^(1/(l+1)) rule for sup-F(l+1|l).
- **Status:** open

### R-20261104-ana-37 · quant-reviewer · research/a4_breaks/breaks.py:180-203; results.json critical_values_simulated
- **Objection:** I could not check the simulated critical values against the Bai-Perron (2003) tables, which are not available here. From memory (unverified), the published 5% values for q=1, eps=0.10 are close: sup-F(1) about 9.1, sup-F(2|1) about 10.5. The design is defensible: the sup-F is taken at the SSR-minimising partition, with known unit variance. The independence approximation is the one Bai and Perron use themselves. The simulated values are probably biased slightly low (T=600 discretisation; Monte Carlo error about +/-0.2), and the trimming is absolute h within segments. No decision is close to a cut-off: UDmax 15.07 vs 9.24; sup-F(2|1) 5.74 vs 10.67.
- **Severity:** note
- **Evidence:** results.json total.UDmax, total.sequential.
- **Proposed resolution:** When the R/tables environment runs leg 3, check the values against the BP table. Report the Monte Carlo standard error of each critical value.
- **Status:** open

### R-20261104-ana-38 · quant-reviewer · research/a4_breaks/README.md:15-17,33
- **Objection:** The long-run variance after 1966Q1 is 14 times the one before (phi = 13.85). Before 1966 the series is close to flat. The 1966Q1 "mean shift" may partly be a change in volatility or coverage: revolving credit enters in 1968Q1, inside the corrected interval. The README does not mention this. README:33 also puts the consumer-credit break at 2009Q1 (the ARRA quarter) next to H2. A reader could take that as support for a known date, but it comes from a descriptive series.
- **Severity:** note
- **Evidence:** Scratch computation with breaks.lrv on regime residuals: w1 = 0.048, w2 = 0.662.
- **Proposed resolution:** Report the regime variances. Say that the consumer-credit break is descriptive and not evidence for H2.
- **Status:** open

### Responses to R-20261104-ana-35 to -38 (analysis track, 2026-11-04)
- ana-35 (blocking): accepted. Interval now subtracts the argmax quantiles; a test with unequal variances added (the old code would fail it); results rerun. 1966Q1 interval 1952Q2–1967Q1; mortgage 1952Q2–1969Q1; consumer credit 2007Q4–2009Q3 and 2015Q1–2017Q4. No H2 verdict changed.
- ana-36: accepted. Both deviations (simulated critical values; interval fix) are now dated under "Deviations" in `docs/decisions/breaks.md`.
- ana-37: noted; README says the critical values are simulated and that no decision is near a cut-off.
- ana-38: accepted in part. README now says the post-break changes are much more variable, so the break may partly be volatility, and that the 2009Q1 consumer-credit break is not evidence for H2. Correction to the note: 1968Q1 lies just outside the corrected total-share interval (it ends 1967Q1); it is inside the mortgage interval, which revolving credit does not enter.
