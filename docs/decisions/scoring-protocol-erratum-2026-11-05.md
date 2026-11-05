# Erratum to the frozen scoring protocol (2026-11-05)

> **Claude draft.** Written by the markets track on Eleonora's decision on card c3-rule (PLAN.md "Decisions taken", 2026-11-05, chosen 15:55 UTC, recorded by the coordinator at ccc1fc6). It corrects the record. It does not change the protocol's design. `docs/decisions/scoring-protocol.md`, `research/c2_forecast/SPECS.md` and `research/c2_forecast/FREEZE.json` are left unedited; this file is the correction.

## 1. The "beats" decision rule is (b), not (a)

**What the frozen file says.** `docs/decisions/scoring-protocol.md` at the freeze commit 192d60c, section "Decision rules", has the choice "when the write-up may say a model 'beats' a benchmark at horizon h" with three options:

- (a) lower primary loss on development, significant after correction, and lower loss in the holdout;
- (b) "As (a), plus relative loss ≤ 0.95 (at least 5% better) in both samples, and 80% coverage not rejected on development data. (Claude recommends.)";
- (c) holdout only.

Under the options it reads: "**Decided: (a).** Eleonora, 2026-11-04 (accepted the recommended option)."

**Why that is wrong.** The two parts of that line contradict each other. The recommended option is (b): it is the only option marked "(Claude recommends.)". The file's own header also says that Eleonora "chose them on 2026-11-04 by accepting every recommended option". Every other **Decided** line in the file names the recommended option. "(a)" was a transcription error by the coordinator when the protocol was frozen at 192d60c. The quant-reviewer flagged the contradiction during the C3 review, and the coordinator confirmed it as their error.

**Correction.** The decided rule is **(b)**, as Eleonora chose at the freeze and confirmed on card c3-rule (option (b), 2026-11-05).

**Effect.**
- Every verdict computed under (a) is superseded: in `research/c2_forecast/holdout_results.json` (field `verdicts`, written by the one holdout run at a0d9151), in `research/joint_holdout/README.md`, and in the first C3 drafts.
- C3 recomputes the verdicts under (b) from the committed results, with no rerun. Verdicts under (a) may appear only as a labelled superseded line.
- The committed results files are not edited.
- How C3 reads "relative loss" and "80% coverage not rejected" is stated in `research/c3_accuracy/README.md` as an implementation reading, not as part of this correction.

## 2. Size of the Holm family: 28 + 14 = 42, not "36 + 6"

`research/c2_forecast/SPECS.md` says the seasonal-naive comparisons grow the Holm family "from 36 to 42 tests", and in another place "42 tests (36 + 6 seasonal-naive)". The end count of 42 is right; the split is wrong.

The family on record (`research/c2_forecast/tests_dev.csv`) has two parts:
- **28 tests** against no-change and AR. In each window design (expanding, rolling), `Z-DIR` and `Z-DAMP` are tested at h = 1, 4, 8 against both benchmarks, which gives 24. `ZC1-DIR` (expanding only) adds 4 at h = 1 and 4. It has no test at h = 8, because `forecast.py` skips any pair with fewer than 8 development forecasts.
- **14 tests** against the seasonal naive, on the same grid.

The quant-reviewer found the miscount (mkt-q39). No p-value changes: the Holm adjustment in `tests_dev.csv` was computed over the 42 tests that exist.
