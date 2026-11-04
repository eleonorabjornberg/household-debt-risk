Review entries from the analysis track after the coordinator's fold at 6dafdac (ana-1..34); the coordinator moves them into `claims/review-log.md` on merge.

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
