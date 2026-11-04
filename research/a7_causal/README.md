# A7: Did the 2008 conservatorship and the 2010 student-loan takeover change who bears the risk, or its price?

> **Claude draft, not the author's text.** Results of the pre-registered tests and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A7. Status: run to the pre-registration ([`docs/decisions/a7-causal-prereg.md`](../../docs/decisions/a7-causal-prereg.md), frozen `206e126`) and its two addenda (`0f9aaff`, `8b09d7c`, both committed before any A7 data was fetched), with Eleonora's Q8 decisions; the code was committed (`98a8d7a`) before the first run. Quant review done (`R-20261104-ana-42` to `-47`); the corrections it asked for are in. The second addendum's header says 16:55 UTC; it was committed at 16:47 UTC, before any A7 data was fetched (16:50).** Results: [`results.json`](results.json).

## Results

**H1, mortgage pricing around the conservatorship (6–7 Sep 2008): a fall, not significant after the pre-registered correction.** Weekly S1 (30-year PMMS rate minus the 10-year Treasury yield of the same week) fell 0.35 pp from 4 Sep to 9 Oct 2008. Against its normal drift (constant-mean model, 104 weeks to July 2008) that is an abnormal fall of 0.39 pp; the AR(1) sensitivity gives 0.39 pp too. Almost all of it (0.37 pp) came in week 0, the release of 11 Sep 2008, before the Lehman bankruptcy. In the placebo-in-time test only one of the 90 comparable (overlapping) five-week windows before HERA fell as much, a one-sided rank p of 0.022; the HAC t statistic is −2.49 (−2.37 with the exact five-week variance). On its own that clears 5%. With Holm across the four pre-registered hypotheses it would have needed p ≤ 0.0167, so under the pre-registered rule H1 is **not supported**. The pre-registered sentence for a supported H1 is therefore not used.

- *Sensitivity, examined after the results:* the family of four includes H2 and H3, whose fits failed (below); their rank p-values (0.77 and 0.54) enter Holm as the addendum says. Had the family counted only the hypotheses with a credible test (H1 and H4), H1 would pass. The addendum fixed the family at four before any data was seen, so the verdict above stands; whether failed-fit hypotheses should count is a question for Eleonora.
- Other news inside the window that the design cannot remove: the Lehman bankruptcy (15 Sep 2008) and the market turmoil that followed fall inside it, though nearly all of the fall came in the week before.

**H2, private-label holdings, and H3, the public share: fit failed.** For both, a linear trend fitted on 2000Q1–2005Q4 misses the 2006–07 holdout by more than the outcome's own 2006–07 standard deviation, the pre-registered failure level: holdout RMSPE $657B against a standard deviation of $170B for H2, and 2.23 pp against 0.81 pp for H3. Under the decision rule no effect is estimated: "no credible counterfactual". (Both series move sharply after 2008Q3, but without a credible counterfactual that movement is not attributed.)

**H4, student loans after SAFRA: the mechanics are as expected.** Non-federal student-loan holdings grew by $10.3B a quarter on average from 2006Q2 to 2010Q2 and shrank by $11.4B a quarter from 2010Q3 to 2012Q4 (HAC t −4.67; rejected after Holm). This is what the end of new FFEL lending implies mechanically; it is not evidence of a behavioural effect, as the pre-registration says. The pre-period is itself partly treated: ECASLA (May 2008) already let the Education Department buy FFEL loans.

## What is and is not identified

- A fall in S1 around the conservatorship is timing, not cause: the window also holds Lehman and the wider crisis.
- H2 and H3 have no credible counterfactual with the data available (Eleonora's Q8(a) fallback; A5 has no state series by holder).
- H4 tests accounting.
- Results are reported in full, including the non-significant H1 and the failed fits.

## Files and how to rerun

```bash
uv run --project pipeline python research/a7_causal/causal.py   # needs FRED_API_KEY (cached in data/a7/) and the Z.1 zip
```
