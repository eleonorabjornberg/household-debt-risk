# A4: Structural breaks in the public share

> **Claude draft, not the author's text.** Results of the pre-registered tests and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write.

**PLAN task A4. Status: run to the frozen pre-registration ([`docs/decisions/breaks.md`](../../docs/decisions/breaks.md), commit `02cc47f`); accepted by Eleonora 2026-11-04.** The code was committed (`eed0ce7`) before the first run on the target series. Deviations (also listed in `breaks.md`, Deviations): critical values are simulated, because the Bai-Perron tables are not available offline; and the break-date interval was corrected after the first run (a sign error, caught by the quant reviewer; `breaks.py`, docstring). The R `strucchange` cross-check (R installed from the Ubuntu archive) has been run and agrees within the pre-registered tolerance on every part R implements (`rcheck/comparison.json`); no known date is confirmed, because no Chow test at a known date rejects.

Data: quarterly change in the public share of household mortgages and consumer credit, 1952Q2–2026Q2 (297 quarters), Z.1 release of 2026-09-11. Results: [`results.json`](results.json).

## Results

**H1, any break: supported.** The test of no break rejects at 5% (UDmax 15.07 against a simulated 5% critical value of 9.24). The pre-registered sequential rule selects one break:

| Break | 95% interval | Mean quarterly change before → after |
|---|---|---|
| 1966Q1 | 1952Q2 (sample start) to 1967Q1 | −0.01 pp → +0.22 pp |

This is "a break the pre-named dates do not explain"; it is not attributed here. The interval is wide and reaches the start of the sample, so the timing is loosely pinned. The quarterly changes are also much more variable after the break than before, so part of what the test finds may be a change in volatility rather than in pace. The nearest measurement quarter (1968Q1, revolving credit enters Z.1) lies just outside the interval. BIC and LWZ, reported alongside as pre-registered, would pick 4 breaks.

**H2, breaks at the known 2008–2010 dates: no evidence at any of the five.** For each date, the pre-registered sentence is "No evidence of a break at D":

| Date | Event | Chow p (HAC) | Holm | Bai-Perron interval covers D |
|---|---|---|---|---|
| 2008Q1 | Economic Stimulus Act | 0.19 | not rejected | no |
| 2008Q2 | ECASLA | 0.23 | not rejected | no |
| 2008Q3 | HERA and conservatorship | 0.30 | not rejected | no |
| 2009Q1 | ARRA | 0.44 | not rejected | no |
| 2010Q3 | SAFRA effective | 0.76 | not rejected | no |

No one-quarter step at these dates meets the pre-registered robust-z rule either. This does not say the policies had no effect. The model looks for a lasting change in the pace of the series; A1 shows the 2007–11 rise was a large move in level, half of it private debt shrinking.

**H3, are the known dates special? No.** Between 51% and 91% of the admissible placebo quarters give a larger Chow statistic than each known date.

**Descriptive series.** The mortgage share also breaks at 1966Q1 (interval 1952Q2 to 1969Q1). The consumer-credit share breaks at 2009Q1 (interval 2007Q4 to 2009Q3) and 2016Q2 (2015Q1 to 2017Q4); these are descriptive only, not tests, and the 2009Q1 date is not evidence for H2.

**Vintage.** On the June 2026 vintage, both samples cut to 2026Q1, the break date and every verdict are unchanged.

## Limits

- **R cross-check.** Dates and SSR identical, HAC sup-F within 2.5%, interval within one quarter. The sequential test, UDmax/WDmax and the simulated critical values are not in `strucchange` and are not cross-checked.
- **Simulated critical values** (2,000 replications, seed in `breaks.py`); they replace published tables, which are not reachable offline.
- **Timing, not cause.** A break says the series changed course; causal questions are A7.
- **The pre-1952 history (A3) is not in this test**, as pre-registered; it would need an annual-frequency addendum.

## Files and how to rerun

```bash
uv run --project pipeline python research/a4_breaks/breaks.py   # needs data/validation/FRB_Z1_csv.zip and prev_z1_csv_files.zip
```
