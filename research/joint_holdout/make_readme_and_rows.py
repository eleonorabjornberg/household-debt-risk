#!/usr/bin/env python3
"""README and register rows for the one joint C2 + C1 + C1b holdout run (commit a0d9151, approval 432fed0).

    uv run --project pipeline python research/joint_holdout/make_readme_and_rows.py

Reads only the committed result files (never reruns anything) and writes research/joint_holdout/README.md and the
"hold_" rows of claims/tracks/markets.csv through research/common/track_rows.py.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "common"))
from track_rows import REGISTER, write_track_rows  # noqa: E402

C2 = "research/c2_forecast/holdout_results.json"
C1B = "research/c1b_nowcast/holdout_results.json"
PERIOD = "2023Q3-2026Q2"
VINTAGE = "z1:2016-09-16 z1:2026-09-11 fred:2026-11-04"


def c1_series() -> str:
    with open(REGISTER, newline="") as f:
        return next(r for r in csv.DictReader(f) if r["claim_id"] == "c1_rt_k1_relrmse_bridge")["series_ids"]


SERIES = c1_series()
NOTE = ("One joint holdout run (a0d9151, approval 432fed0, after deviation c1b-dev-1 in cddd3ca); "
        "12 holdout targets; not to be rerun. ")


def f2(x: float) -> str:
    return f"{x:.2f}"


class Doc:
    def __init__(self):
        self.lines, self.rows = [], []

    def add(self, text: str, nums: list[tuple]) -> None:
        """nums: (claim_id, claim, display, value, unit, computation, extra_series, note)."""
        self.lines.append(text)
        ln = len(self.lines)
        for cid, claim, disp, val, unit, comp, ser, note in nums:
            assert disp in text, (cid, disp, text)
            self.rows.append({"claim_id": cid, "claim": claim, "display": disp, "value": repr(float(val)), "unit": unit,
                              "period": PERIOD, "locations": f"research/joint_holdout/README.md:{ln}",
                              "computation": comp, "series_ids": (SERIES + (" " + ser if ser else "")).strip(),
                              "vintage": VINTAGE, "validation": "UNVERIFIED", "check_id": "", "notes": NOTE + note})


def main() -> int:
    c2 = json.loads((ROOT / C2).read_text())
    c1b = json.loads((ROOT / C1B).read_text())
    assert c2["approval_commit"] == "432fed0" and "C1b" in c1b["approval"]
    d = Doc()
    for t in ["# Joint holdout results (C2 forecast, C1 and C1b nowcasts)", "",
              "> **Claude draft.** Written by the markets track from the result files. Eleonora replaces it with her "
              "own text before anything here is published.", "",
              "The holdout is 2023Q3–2026Q2. It was opened once, in commit a0d9151, under Eleonora's approval "
              "432fed0 and after deviation c1b-dev-1 (cddd3ca). Source files: `research/c2_forecast/holdout_results.json`, "
              "`research/c1b_nowcast/holdout_results.json` and `research/c1b_nowcast/nowcasts_holdout.csv`. "
              "Every number below comes from those files through `make_readme_and_rows.py`; none was typed by hand.", "",
              "Each cell rests on 12 targets or fewer, so these are small-sample numbers.", "",
              "## C1b: does Freddie Mac's monthly data improve the real-time nowcast?", "",
              "RMSE in percentage points of the public share, real-time first-release targets. k is the nowcast "
              "instant within the quarter.", "",
              "| k | scored instants | C1b bridge | C1 bridge | no change |", "|---|---|---|---|---|"]:
        d.lines.append(t)
    h = c1b["holdout"]
    comp = f"research/c1b_nowcast/nowcast_c1b.py --holdout -> {C1B} holdout.rmse_pp"
    for k in ["1", "2", "3", "all"]:
        r = h["rmse_pp"][k]
        n = h["n_scored"].get(k, sum(h["n_scored"].values()))
        cells = {m: f"{f2(r[m])} pp" for m in ("bridge_c1b", "bridge_c1", "no_change")}
        lab = f"k = {k}" if k != "all" else "pooled k = 1–3"
        d.add(f"| {lab} | {n} | {cells['bridge_c1b']} | {cells['bridge_c1']} | {cells['no_change']} |",
              [(f"hold_c1b_k{k}_rmse_{m}", f"C1b holdout, {lab}: {m} RMSE {cells[m]}.", cells[m], r[m], "pp",
                f"{comp}.{k}.{m}", "Freddie Mac monthly volume summaries (research/c1b_nowcast/freddie_mvs_reports.csv)"
                if m == "bridge_c1b" else "", "Real-time, first-release targets; Freddie only, Fannie and Ginnie flat.")
               for m in cells])
    d.lines += ["", f"Pre-registered verdict (`docs/decisions/c1b-prereg.md`, decision rules): **{c1b['verdict_rule']}**. "
                "The rule needs lower RMSE at every k on development, significant after Holm at one or more k, "
                "and a lower pooled RMSE in the holdout. The holdout part is a comparison of RMSEs, with no test.", "",
                "## C1: the accounting bridge in real time", "",
                "Bridge RMSE relative to no-change on the same instants. The holdout carries no tests.", ""]
    c1 = c2["c1"]
    cells = []
    for s in c1["scores"]:
        if s["model"] == "bridge":
            cells.append((s["k"], s["n"], s["rel_rmse_vs_no_change"]))
    d.lines += ["| k | instants | bridge / no change |", "|---|---|---|"]
    for k, n, v in cells:
        lab = f"k = {k}" if k != "all" else "pooled k = 1–3"
        d.add(f"| {lab} | {n} | {f2(v)} |",
              [(f"hold_c1_k{k}_relrmse_bridge", f"C1 holdout, {lab}: bridge RMSE relative to no-change {f2(v)}.",
                f2(v), v, "ratio", f"research/c2_forecast/holdout_run.py -> {C2} c1.scores[k={k},bridge].rel_rmse_vs_no_change",
                "", "Real-time, first-release targets; descriptive.")])
    d.lines.append("")
    me = c1["bridge_mean_error_pp"]
    me_d = f"{me:.2f} pp".replace("-", "−")
    d.add(f"Mean bridge error over the holdout instants: {me_d} (negative: the bridge nowcast is below the outcome).",
          [("hold_c1_bridge_mean_error", f"C1 holdout: mean bridge error {me_d}.", me_d, me, "pp",
            f"research/c2_forecast/holdout_run.py -> {C2} c1.bridge_mean_error_pp", "", "Descriptive, k = 1–3.")])
    d.lines += ["", f"Targets scored: {c1['n_targets']} quarters. The {c1['n_no_target_instants']} instants that target "
                f"{', '.join(c1['no_target_quarters'])} are recorded as \"no target\" (deviation c1b-dev-1): no Z.1 "
                "has published that quarter, and it lies outside the holdout window.", "",
                "## C2: the share forecasts (h = 1, 4 and 8 quarters ahead) against their benchmarks", "",
                "Holdout RMSE of the candidate divided by the benchmark's, with the pre-registered verdict "
                "(`docs/decisions/scoring-protocol.md`, option (a)): \"beats\" needs a lower loss on development, "
                "significant after Holm, and a lower loss in the holdout. \"Does not beat\" means the benchmark's loss is lower in either sample, so it can sit beside a holdout ratio below 1 when the development loss was higher. Pseudo out-of-sample on latest-vintage "
                "data, not real time.", "",
                "| design | h | candidate | vs no change | vs AR (BIC) | vs seasonal naive |", "|---|---|---|---|---|---|"]
    vs = {}
    for v in c2["c2"]["verdicts"]:
        vs.setdefault((v["design"], v["h"], v["candidate"]), {})[v["benchmark"]] = v
    for (des, hh, cand), b in vs.items():
        nums, cells = [], []
        for bench in ("no_change", "ar_bic", "seasonal_naive"):
            v = b.get(bench)
            if v is None or v.get("holdout_rel_rmse") is None:
                cells.append("–")
                continue
            disp = f2(v["holdout_rel_rmse"])
            cells.append(f"{disp} ({v['verdict']})")
            cid = f"hold_c2_{des.replace('latest-', '')}_h{hh}_{cand.lower().replace('-', '')}_vs_{bench}"
            nums.append((cid, f"C2 holdout, {des}, h={hh}: {cand} RMSE relative to {bench} {disp} ({v['verdict']}).",
                         disp, v["holdout_rel_rmse"], "ratio",
                         f"research/c2_forecast/holdout_run.py -> {C2} c2.verdicts[{des},h={hh},{cand},{bench}].holdout_rel_rmse",
                         "", f"Pseudo out-of-sample, latest vintage; n = {v['n_holdout']}; verdict {v['verdict']}."))
        d.add(f"| {des.replace('latest-', '')} | {hh} | {cand} | " + " | ".join(cells) + " |", nums)
    n_beats = sum(v["verdict"] == "beats" for v in c2["c2"]["verdicts"])
    beats_nc = [v for v in c2["c2"]["verdicts"] if v["benchmark"] == "no_change" and v["verdict"] == "beats"]
    assert all(v["benchmark"] == "seasonal_naive" and v["h"] == 1 for v in c2["c2"]["verdicts"] if v["verdict"] == "beats")
    d.lines += ["", f"No candidate beats no-change at any horizon or design ({len(beats_nc)} \"beats\" verdicts against "
                f"no-change). The {n_beats} \"beats\" verdicts are all against the seasonal naive at h = 1. Coverage "
                "of the intervals and the full score tables are in the results file.", ""]
    (HERE / "README.md").write_text("\n".join(d.lines))
    new = write_track_rows(d.rows, prefix="hold_")
    print(f"README.md: {len(d.lines)} lines; {len(d.rows)} rows, {len(new)} written to claims/tracks/markets.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
