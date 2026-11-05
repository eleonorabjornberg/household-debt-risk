#!/usr/bin/env python3
"""C3, the accuracy report: README and register rows built from committed results only.

    uv run --project pipeline python research/c3_accuracy/make_report.py

Reads committed result files of C2, C1 and C1b (and, for superseded specifications, the committed versions of those
files in git history through `git show`). Runs no model, opens no holdout and fetches nothing. Writes
research/c3_accuracy/README.md, the full tables under research/c3_accuracy/tables/, and the "c3_" rows of
claims/tracks/markets.csv through research/common/track_rows.py.

The holdout was opened once, in a0d9151 (approval 432fed0). Its C2 part saved scores, coverage and verdicts, not
per-forecast errors, so C2's holdout errors cannot be listed here (see card c3-errors, sent to the coordinator).
"""
from __future__ import annotations

import csv
import io
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "common"))
from track_rows import REGISTER, write_track_rows  # noqa: E402

C2D, C1D, C1BD = "research/c2_forecast", "research/c1_nowcast", "research/c1b_nowcast"
HOLD = f"{C2D}/holdout_results.json"
C1B_HOLD = f"{C1BD}/holdout_results.json"
VINTAGE = "z1:2016-09-16 z1:2026-09-11 fred:2026-11-04"
REGIMES = [("GFC", "2007Q4", "2011Q4"), ("2020", "2020Q1", "2020Q4")]  # fixed by the protocol (frozen 192d60c)
C2_CANDS = ["Z-DIR", "Z-DAMP", "ZC1-DIR"]
C2_BENCH = ["no_change", "drift", "ar_bic", "seasonal_naive"]
MINUS = "−"


def reg_series(cid: str) -> str:
    with open(REGISTER, newline="") as f:
        return next(r for r in csv.DictReader(f) if r["claim_id"] == cid)["series_ids"]


SER_C2 = reg_series("public_share_2026q2")
SER_C1 = reg_series("c1_rt_k1_relrmse_bridge")


def read_csv(rel: str) -> list[dict]:
    with open(ROOT / rel, newline="") as f:
        return list(csv.DictReader(f))


def git_csv(commit: str, rel: str) -> list[dict]:
    txt = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{rel}"], capture_output=True, text=True,
                         check=True).stdout
    return list(csv.DictReader(io.StringIO(txt)))


def git_json(commit: str, rel: str):
    return json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{rel}"], capture_output=True,
                                     text=True, check=True).stdout)


C1_PERIOD = {"RT": "2016Q3-2023Q2", "P2b": "2015Q1-2023Q2", "P2a": "2010Q2-2023Q2"}


def commit_date(commit: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", "-s", "--format=%ad", "--date=short", commit],
                          capture_output=True, text=True, check=True).stdout.strip()


def nmark(n) -> str:
    """n as text, with ‡ when fewer than ten forecasts stand behind the cell (quant-reviewer mkt-q36)."""
    return f"{n}‡" if int(n) < 10 else str(n)


def fl(x) -> float | None:
    return None if x in (None, "", "None") else float(x)


def qadd(q: str, h: int) -> str:
    y, n = int(q[:4]), int(q[5]) - 1 + h
    return f"{y + n // 4}Q{n % 4 + 1}"


def inwin(q: str, lo: str, hi: str) -> bool:
    return lo <= q <= hi


def rmse(e: list[float]) -> float:
    return math.sqrt(sum(x * x for x in e) / len(e))


def f2(x: float) -> str:
    s = f"{x:.2f}"
    return s.replace("-", MINUS) if s.startswith("-") else s


def fp(p: float) -> str:
    return f"{p:.1e}" if p < 0.001 else f"{p:.3f}"


class Doc:
    """Lines of the README plus one register row per number shown."""

    def __init__(self):
        self.lines: list[str] = []
        self.rows: list[dict] = []
        self.ids: set[str] = set()

    def text(self, *ts: str) -> None:
        self.lines.extend(ts)

    def add(self, line: str, nums: list[dict]) -> None:
        self.lines.append(line)
        ln = len(self.lines)
        for n in nums:
            assert n["display"] in line, (n["claim_id"], n["display"], line)
            assert n["claim_id"] not in self.ids, n["claim_id"]
            self.ids.add(n["claim_id"])
            self.rows.append({**n, "locations": f"research/c3_accuracy/README.md:{ln}", "vintage": VINTAGE,
                              "validation": "UNVERIFIED", "check_id": ""})


def num(cid: str, claim: str, disp: str, val: float, unit: str, period: str, comp: str, note: str,
        series: str = SER_C2) -> dict:
    return {"claim_id": "c3_" + cid.lower().replace("-", "").replace(" ", "_"), "claim": claim, "display": disp,
            "value": repr(float(val)), "unit": unit, "period": period, "computation": comp, "series_ids": series,
            "notes": "C3 accuracy report (Claude draft), built from committed results only; nothing rerun. " + note}


def cell(cid, claim, val, unit, period, comp, note, series=SER_C2, fmt=f2, suffix=""):
    """(table cell text, register row) for one number; '—' and no row when the value is missing."""
    if val is None:
        return "—", None
    disp = fmt(val) + suffix
    return disp, num(cid, claim.format(d=disp), disp, val, unit, period, comp, note, series)


def table_row(d: Doc, label_cells: list[str], cells: list[tuple]) -> None:
    d.add("| " + " | ".join(label_cells + [c[0] for c in cells]) + " |", [c[1] for c in cells if c[1]])


def write_table(name: str, rows: list[dict]) -> None:
    (HERE / "tables").mkdir(exist_ok=True)
    with open(HERE / "tables" / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ----------------------------------------------------------------------------------------------- checks on inputs
def check_c2_dev_errors(fc: list[dict], scores: list[dict]) -> None:
    """Recompute development RMSE from forecasts_dev.csv and compare with scores_dev.csv (sign and units check)."""
    for s in scores:
        if s["comparison"] != "Z family, all origins":
            continue
        rows = [r for r in fc if r["design"] == s["design"] and r["h"] == s["h"] and r[s["model"]] != ""]
        e = [100 * (float(r[s["model"]]) - float(r["actual"])) for r in rows]
        assert len(e) == int(s["n"]) and abs(rmse(e) - float(s["rmse_pp"])) < 1e-4, (s, len(e), rmse(e))


def check_c1_dev_errors(nc: list[dict], scores: list[dict]) -> None:
    for s in scores:
        if s["sample"] != "RT" or s["model"] not in ("bridge", "no_change") or s["k"] == "all":
            continue
        rows = [r for r in nc if r["sample"] == "RT" and r["k"] == s["k"] and r[s["model"]] != "" and r["actual"] != ""]
        e = [100 * (float(r[s["model"]]) - float(r["actual"])) for r in rows]
        assert len(e) == int(s["n"]) and abs(rmse(e) - float(s["rmse_pp"])) < 1e-4, (s, len(e), rmse(e))


def check_c1b_hold(nh: list[dict], c1b: dict, c1: dict) -> None:
    for k in ("1", "2", "3"):
        rows = [r for r in nh if r["k"] == k and r["actual"] != ""]
        for m in ("bridge_c1", "bridge_c1b", "no_change"):
            e = [100 * (float(r[m]) - float(r["actual"])) for r in rows]
            assert abs(rmse(e) - c1b["holdout"]["rmse_pp"][k][m]) < 1e-6, (k, m)  # CSV is rounded
        c1row = next(s for s in c1["scores"] if str(s["k"]) == k and s["model"] == "bridge")
        assert abs(c1row["rmse_pp"] - c1b["holdout"]["rmse_pp"][k]["bridge_c1"]) < 1e-12, k


def check_verdicts(verdicts: list[dict], tests: list[dict]) -> None:
    key = {(t["design"], t["h"], t["candidate"], t["benchmark"]): t for t in tests}
    assert len(key) == len(verdicts) == 42, (len(key), len(verdicts))
    for v in verdicts:
        t = key[(v["design"], str(v["h"]), v["candidate"], v["benchmark"])]
        assert abs(float(t["p"]) - v["p"]) <= 1e-6 * max(1, v["p"]) and abs(float(t["p_holm"]) - v["p_holm"]) < 1e-6


# ----------------------------------------------------------------------------------------------- sections
def banner(d: Doc) -> None:
    d.text("# C3: how accurate are the share forecasts and nowcasts?", "",
           "> **Claude draft.** Written by the markets track from committed result files by `make_report.py`. "
           "Eleonora replaces it with her own text before anything here is published. No number below was typed "
           "by hand, and nothing was rerun to produce it.", "",
           "This is the report that `docs/decisions/scoring-protocol.md` (\"What C3 must publish\") asks for. It "
           "covers three tasks: C2, which forecasts the public share of household mortgages and consumer credit "
           "h = 1, 4 and 8 quarters ahead; C1, which nowcasts the next quarter's change from monthly and weekly "
           "indicators; and C1b, the second C1 run with Freddie Mac's monthly data.", "",
           "The holdout is 2023Q3–2026Q2. It was opened once, in commit a0d9151, under Eleonora's approval 432fed0. "
           "It is not to be reopened. Everything else is the development sample, scored before the holdout was "
           "opened.", "",
           "**What a reader should take from it**", "")


def fail_counts(d: Doc, fc: list[dict]) -> None:
    """Z-DIR's ten largest development errors (expanding) that fall in a protocol regime window, by target and by
    origin quarter, against the count expected if the ten were drawn at random from all forecasts (quant-reviewer
    mkt-q34)."""
    parts, nums = [], []
    for by in ("target", "origin"):
        sub = []
        for h in (1, 4, 8):
            rows = [r for r in fc if r["design"] == "latest-expanding" and r["h"] == str(h)]
            q = (lambda r: qadd(r["T"], h)) if by == "target" else (lambda r: r["T"])
            inw = lambda r: any(inwin(q(r), a, b) for _, a, b in REGIMES)  # noqa: E731
            top = sorted(rows, key=lambda r: -abs(float(r["Z-DIR"]) - float(r["actual"])))[:10]
            hits = [q(r) for r in top if inw(r)]
            base = 10 * sum(inw(r) for r in rows) / len(rows)
            c = cell(f"fail_{by}_h{h}_base", f"C2 development, expanding, h={h}: expected number of the ten largest "
                     f"Z-DIR errors in a regime window ({by} quarter) if drawn at random, {{d}}.", base, "count",
                     "1990Q1-2023Q2", f"{C2D}/forecasts_dev.csv [latest-expanding,h={h}] 10 * share of forecasts with "
                     f"{by} quarter in a window", "Base rate for the count beside it.", fmt=lambda x: f"{x:.1f}")
            nums.append(c[1])
            sub.append(f"{len(hits)} at h = {h} (chance about {c[0]}" + (f"; {', '.join(sorted(hits))}" if hits else "")
                       + ")")
        parts.append(f"by {by} quarter, " + "; ".join(sub))
    d.add("- **Where the models fail.** Of Z-DIR's ten largest development errors per horizon, the number in the "
          "2007Q4–2011Q4 or 2020 windows is, " + ". And ".join(parts) + ". Errors at h = 4 and 8 overlap, so "
          "neighbouring quarters in these lists are one episode, not separate failures. Section 3 lists them.", nums)


def c1_reg_note(hold: dict) -> str:
    """The bridge regression: best development ratio, but pooled holdout RMSE not below no-change (mkt-q38)."""
    r = next(x for x in hold["c1"]["scores"] if x["k"] == "all" and x["model"] == "bridge_reg")
    assert r["rel_rmse_vs_no_change"] >= 1, r
    return ("The bridge regression, which had the lowest development ratio, has a pooled holdout RMSE no lower than "
            "no-change's.")


def headline(d: Doc, verdicts: list[dict], c1b: dict, fc: list[dict], hold: dict, c1v: list[dict]) -> None:
    nc = [v for v in verdicts if v["benchmark"] == "no_change"]
    n_beats_nc = sum(v["verdict"] == "beats" for v in nc)
    beats = [v for v in verdicts if v["verdict"] == "beats"]
    assert n_beats_nc == 0 and all(v["benchmark"] == "seasonal_naive" and v["h"] == 1 for v in beats)
    cand_rel = [s["rel_rmse_vs_no_change"] for s in hold["c2"]["scores_holdout"] if s["model"] in C2_CANDS]
    assert len(cand_rel) == 18 and all(x > 1 for x in cand_rel), cand_rel  # 2 designs x 3 h x 2 + Z+C1 (ZC1-DIR, Z-DIR) x 3
    c1_beats = [v for v in c1v if v["verdict"] == "beats"]
    d.text(f"- **C2 forecasts.** Under the pre-registered rule (a), no frozen candidate beats the no-change forecast "
           "or the AR benchmark at any horizon, in either window design. In the holdout every candidate's RMSE is "
           "above no-change's, at every horizon and in both designs (all ratios in section 2 are above one). The "
           f"only \"beats\" verdicts ({len(beats)}) are against the seasonal naive at h = 1.",
           "- **C1 nowcast.** Under the same rule, " + (
               "no C1 model beats no-change or AR(1) at any instant k" if not c1_beats else
               "these C1 comparisons beat their benchmark: " + ", ".join(
                   f"{v['candidate']} vs {v['benchmark']} at k = {v['k']}" for v in c1_beats)) + ". This verdict is "
           "computed in this report by applying rule (a) to C1's committed tests and holdout scores; no frozen C1 code "
           "issues verdicts, and it rests on few targets (section 2). "
           + c1_reg_note(hold),
           f"- **C1b.** Its verdict under its own pre-registration is \"{c1b['verdict_rule']}\": a comparison of RMSEs "
           "on 12 target quarters, with no test.")
    fail_counts(d, fc)
    d.text("- **Gaps.** C2's holdout per-forecast errors were not saved by the one run, so its ten largest holdout "
           "errors cannot be listed (card c3-errors). The regime windows fall in development only. Many cells rest "
           "on fewer than ten forecasts; they are marked ‡.", "")


def registry(d: Doc, scores2: list[dict], placebo_old: dict, placebo: dict, sc1: list[dict], sc1_old: list[dict],
             sc1b: list[dict]) -> None:
    d.text("## 1. Specification registry, including superseded and abandoned versions", "",
           "Development scores: RMSE relative to no-change on the same targets (below 1 is better than no-change). "
           "C2: latest vintage, expanding window, h = 1 / 4 / 8. C1 and C1b: real-time sample RT, first-release "
           "targets, k = 1 / 2 / 3 (the instant within the quarter). Commits are where the version was first scored, with "
           "the commit date. n is the number of development forecasts behind each score: `bridge_reg` and `ZC1-DIR` "
           "rest on far fewer than the rows beside them, so their scores are not comparable with those rows.",
           "", "| task | ID | status | commit | date | dev score 1 (n) | dev score 2 (n) | dev score 3 (n) |",
           "|---|---|---|---|---|---|---|---|")

    def withn(c, n):
        return (f"{c[0]} ({nmark(n)})", c[1]) if n is not None and c[1] else c

    def c2n(model, h, comp):
        return next(s["n"] for s in scores2 if s["design"] == "latest-expanding" and s["comparison"] == comp
                    and s["model"] == model and s["h"] == str(h))

    def c1n(rows, model, k, sample):
        r = [s for s in rows if s["sample"] == sample and s["model"] == model and s["k"] == str(k)]
        return r[0]["n"] if r else None

    def c2rel(model, h, comp="Z family, all origins"):
        return next(fl(s["rel_rmse_vs_no_change"]) for s in scores2 if s["design"] == "latest-expanding"
                    and s["comparison"] == comp and s["model"] == model and s["h"] == str(h))

    spec2 = [("Z-DIR", "frozen candidate", "0bc647b", "Z family, all origins"),
             ("Z-DAMP", "frozen candidate", "0bc647b", "Z family, all origins"),
             ("ZC1-DIR", "frozen candidate (Z+C1 common origins only)", "0bc647b", "Z+C1 common origins"),
             ("drift", "benchmark", "0bc647b", "Z family, all origins"),
             ("ar_bic", "benchmark (AR, order by BIC)", "0bc647b", "Z family, all origins"),
             ("seasonal_naive", "benchmark (in the decision rules after the seasonality check)", "0bc647b",
              "Z family, all origins")]
    comp = f"{C2D}/forecast.py -> {C2D}/scores_dev.csv rel_rmse_vs_no_change"
    for m, status, commit, cmpn in spec2:
        cells = [cell(f"reg_c2_{m}_h{h}", f"C2 development, latest-expanding, h={h}: {m} RMSE relative to no-change {{d}}.",
                      c2rel(m, h, cmpn), "ratio", "1990Q1-2023Q2", f"{comp} [{cmpn}, {m}, h={h}]",
                      "Pseudo out-of-sample, latest vintage.") for h in (1, 4, 8)]
        cells = [withn(c, c2n(m, h, cmpn)) for c, h in zip(cells, (1, 4, 8))]
        table_row(d, ["C2", f"`{m}`", status, commit, commit_date(commit)], cells)
    for tag, pl, status, commit in [("v1", placebo_old, "placebo, first definition (shuffled target); superseded by "
                                     "option (a) at d683482", "0bc647b"),
                                    ("a", placebo, "placebo, option (a): demeaned shuffled target", "d683482")]:
        cells = [cell(f"reg_c2_placebo_{tag}_h{h}", f"C2 placebo ({tag}), h={h}: RMSE relative to no-change {{d}}.",
                      pl[str(h)]["rel_rmse_vs_no_change"], "ratio", "1990Q1-2023Q2",
                      f"{C2D}/forecast.py placebo() -> {C2D}/placebo_dev.json @ {commit} [{h}].rel_rmse_vs_no_change",
                      "Leakage test 5; Z-DIR trained on a time-shuffled target.") for h in (1, 4, 8)]
        table_row(d, ["C2", f"`placebo-{tag}`", status, commit, commit_date(commit)], cells)

    def c1rel(rows, model, k, sample="RT"):
        r = [s for s in rows if s["sample"] == sample and s["model"] == model and s["k"] == str(k)]
        return fl(r[0]["rel_rmse_vs_no_change"]) if r else None

    spec1 = [("bridge", "RT", "primary (accounting bridge)", "99d56cd", sc1),
             ("bridge_reg", "RT", "challenger (bridge regression)", "99d56cd", sc1),
             ("drift", "RT", "benchmark", "99d56cd", sc1), ("ar1", "RT", "benchmark (fixed AR(1))", "99d56cd", sc1),
             ("bridge", "P2b", "pseudo-real-time sample P2b (not real time)", "99d56cd", sc1),
             ("bridge", "P2a", "pseudo-real-time sample P2a, indicator set 2a (not real time)", "99d56cd", sc1),
             ("bridge", "RT@58a93d8", "superseded: fourth instant pooled into k = 3, 2016Q4 target missing; replaced "
              "at 99d56cd after review", "58a93d8", sc1_old)]
    for m, sample, status, commit, rows in spec1:
        smp = sample.split("@")[0]
        cid = f"reg_c1_{m}_{sample.replace('@', '_')}"
        cells = [cell(f"{cid}_k{k}", f"C1 development, sample {sample}, k={k}: {m} RMSE relative to no-change {{d}}.",
                      c1rel(rows, m, k, smp), "ratio", C1_PERIOD[smp],
                      f"{C1D}/nowcast.py -> {C1D}/scores_dev.csv @ {commit} [{smp}, {m}, k={k}].rel_rmse_vs_no_change",
                      "Development sample.", SER_C1) for k in (1, 2, 3)]
        cells = [withn(c, c1n(rows, m, k, smp)) for c, k in zip(cells, (1, 2, 3))]
        table_row(d, ["C1", f"`{m}` ({sample})", status, commit, commit_date(commit)], cells)
    cells = [cell(f"reg_c1b_k{k}", f"C1b development, k={k}: bridge_c1b RMSE relative to no-change {{d}}.",
                  next(fl(s["rel_rmse_vs_no_change"]) for s in sc1b if s["k"] == str(k) and s["model"] == "bridge_c1b"),
                  "ratio", "2016Q3-2023Q2", f"{C1BD}/nowcast_c1b.py -> {C1BD}/scores_dev.csv [k={k}, bridge_c1b]",
                  "Freddie only; Fannie and Ginnie carried flat.", SER_C1) for k in (1, 2, 3)]
    cells = [withn(c, next(s["n"] for s in sc1b if s["k"] == str(k) and s["model"] == "bridge_c1b"))
             for c, k in zip(cells, (1, 2, 3))]
    table_row(d, ["C1b", "`bridge_c1b`", "frozen (Freddie Mac monthly data; Fannie Mae carried flat)", "577c572",
                  commit_date("577c572")], cells)
    d.text("| C1b | Ginnie Mae input | planned, not built: no downloadable file found on 2026-11-04 | — | — | — | — | — |", "",
           "Not specifications, listed for completeness: the dry run of the holdout script on a pretend holdout inside "
           "development (2026-11-04, not committed, not a result), and the first joint holdout run approved at "
           "77460b4, which stopped with an error before anything was written (deviation c1b-dev-1).", "")


def holdout_count_note(hold: dict) -> str:
    """How the run counted holdout forecasts, against the protocol's option text (quant-reviewer mkt-q32)."""
    rows = [s for s in hold["c2"]["scores_holdout"] if s["model"] == "no_change"]
    assert all(s["n"] == 12 for s in rows)
    first = {s["h"]: s["first_T"] for s in rows if s["design"] == "latest-expanding" and s["comparison"] == "Z family, holdout"}
    assert first == {1: "2023Q2", 4: "2022Q3", 8: "2021Q3"}, first
    return ("**How the holdout was counted.** The run scored every forecast whose target quarter is in 2023Q3–2026Q2: "
            "12 per horizon. Their origins start at 2023Q2 for h = 1, " + first[4] + " for h = 4 and " + first[8] +
            " for h = 8, so most h = 4 and h = 8 origins lie in development, and consecutive h = 8 forecasts share up "
            "to seven quarters of outcome. The protocol's option text (holdout choice (b)) says \"origins 2023Q2 "
            "onward give 12, 9 and 5 holdout forecasts at h = 1, 4, 8\", which counts by origin. The two readings "
            "differ at h = 4 and 8, and this was not declared before the run. Found by quant-reviewer (mkt-q32) and "
            "sent to the coordinator as a proposed card. Because per-forecast holdout errors were not saved, the "
            "origin-based subset cannot be scored without reopening the holdout.")


def c2_holdout(d: Doc, hold: dict) -> list[dict]:
    sh = hold["c2"]["scores_holdout"]
    d.text("## 2. Holdout results for every frozen candidate", "", "### C2 forecasts (12 targets per horizon)", "",
           "RMSE relative to no-change on the holdout. Pseudo out-of-sample on latest-vintage data, not real time. "
           "`ZC1-DIR` is scored on its own comparison (Z+C1 holdout, expanding design only).", "",
           holdout_count_note(hold), "",
           "| design | h | no-change RMSE | Z-DIR | Z-DAMP | ZC1-DIR | drift | AR (BIC) | seasonal naive |",
           "|---|---|---|---|---|---|---|---|---|")
    comp = f"{C2D}/holdout_run.py -> {HOLD} c2.scores_holdout"

    def get(des, h, m, cmpn="Z family, holdout"):
        if m == "ZC1-DIR":
            cmpn, des = "Z+C1 holdout", "latest-expanding"
        r = [s for s in sh if s["design"] == des and s["h"] == h and s["model"] == m and s["comparison"] == cmpn]
        return r[0] if r else None

    for des in ("latest-expanding", "latest-rolling"):
        dn = des.replace("latest-", "")
        for h in (1, 4, 8):
            nc = get(des, h, "no_change")
            cells = [cell(f"hold_c2_{dn}_h{h}_nc_rmse", f"C2 holdout, {dn}, h={h}: no-change RMSE {{d}}.", nc["rmse_pp"],
                          "pp", "2023Q3-2026Q2", f"{comp}[{des},h={h},no_change].rmse_pp", "n = 12.", suffix=" pp")]
            for m in ["Z-DIR", "Z-DAMP", "ZC1-DIR", "drift", "ar_bic", "seasonal_naive"]:
                r = get(des, h, m) if not (m == "ZC1-DIR" and dn == "rolling") else None
                cells.append(cell(f"hold_c2_{dn}_h{h}_{m}_rel", f"C2 holdout, {dn}, h={h}: {m} RMSE relative to "
                                  f"no-change {{d}}.", r and r["rel_rmse_vs_no_change"], "ratio", "2023Q3-2026Q2",
                                  f"{comp}[{des},h={h},{m}].rel_rmse_vs_no_change", f"n = {r and r['n']}."))
            table_row(d, [dn, str(h)], cells)
    d.text("", "All losses, expanding design (the primary window). Interval scores and CRPS are in pp; lower is "
           "better. The rolling design's full table is in `tables/c2_holdout_scores.csv`.", "",
           "| h | model | RMSE | MAE | interval score 80 | interval score 95 | CRPS |", "|---|---|---|---|---|---|---|")
    for h in (1, 4, 8):
        for m in ["no_change", "Z-DIR", "Z-DAMP", "ZC1-DIR", "drift", "ar_bic", "seasonal_naive"]:
            r = get("latest-expanding", h, m)
            cells = [cell(f"hold_c2_exp_h{h}_{m}_{k}", f"C2 holdout, expanding, h={h}: {m} {k} {{d}}.",
                          fl(r.get(k)) if r.get("n_intervals") or k in ("rmse_pp", "mae_pp") else None, "pp",
                          "2023Q3-2026Q2", f"{comp}[latest-expanding,h={h},{m}].{k}", f"n = {r['n']}.")
                     for k in ("rmse_pp", "mae_pp", "interval_score80_pp", "interval_score95_pp", "crps_pp")]
            table_row(d, [str(h), m], cells)
    d.text("")
    return sh


def verdict_table(d: Doc, verdicts: list[dict]) -> None:
    d.text("### C2 tests and verdicts", "",
           "Development tests (Clark–West for nested pairs, DM with the HLN correction otherwise; HAC lag h − 1), with "
           "raw p-values and Holm-adjusted p-values over the family of 42 tests, and the holdout RMSE ratio. The "
           "verdict follows rule (a): \"beats\" needs a lower development loss, significant after Holm, and a lower "
           "holdout loss. The holdout carries no test. `posthoc_p_bartlett8` (a lag-8 sensitivity) is in "
           "`tables/c2_verdicts.csv`; under it the h = 1 p-values are far larger.", "",
           "| design | h | candidate | benchmark | test | dev n | raw p | Holm p | holdout ratio | verdict |",
           "|---|---|---|---|---|---|---|---|---|---|")
    comp = f"{C2D}/holdout_run.py -> {HOLD} c2.verdicts"
    for v in verdicts:
        dn = v["design"].replace("latest-", "")
        base = f"{dn}_h{v['h']}_{v['candidate']}_{v['benchmark']}"
        lab = f"C2 {dn}, h={v['h']}, {v['candidate']} vs {v['benchmark']}"
        cells = [cell(f"t_{base}_p", lab + " (development " + v["test"] + "): raw p {d}.", v["p"], "p", "1990Q1-2023Q2",
                      f"{comp}[{base}].p", "Development test.", fmt=fp),
                 cell(f"t_{base}_holm", lab + ": Holm-adjusted p {d}.", v["p_holm"], "p", "1990Q1-2023Q2",
                      f"{comp}[{base}].p_holm", "Holm over 42 tests.", fmt=fp),
                 cell(f"t_{base}_hold", lab + ": holdout RMSE ratio {d}.", v.get("holdout_rel_rmse"), "ratio",
                      "2023Q3-2026Q2", f"{comp}[{base}].holdout_rel_rmse", f"n = {v['n_holdout']}; descriptive.")]
        table_row(d, [dn, str(v["h"]), v["candidate"], v["benchmark"], v["test"], str(v["n"])],
                  cells[:3] + [("**" + v["verdict"] + "**", None)])
    d.text("")


def high_h_note(dc: list[dict]) -> str:
    """Development 95% coverage at h = 4 and 8 for the models in the table: say what it is, computed."""
    vals = [r["coverage"] for r in dc if r["design"] == "latest-expanding" and r["h"] in (4, 8) and r["level"] == 0.95
            and r["model"] in ("Z-DIR", "Z-DAMP", "no_change", "ar_bic")]
    assert len(vals) == 8
    if all(v < 0.95 for v in vals):
        return "There, development coverage of the 95% intervals is below nominal for every model shown."
    return "There, development coverage of the 95% intervals is below nominal for some models shown and not others."


def coverage(d: Doc, hold: dict, cov_dev: list[dict]) -> None:
    d.text("### Interval coverage (expanding design)", "")
    lv = [num(f"cov_level_{L}", f"C2 interval nominal level {L}% (protocol coverage target).", f"{L}%", L / 100, "share",
              "n/a", "docs/decisions/scoring-protocol.md 'Coverage targets'", "A protocol setting, not a result.")
          for L in (80, 95)]
    d.add("Share of outcomes inside the model's 80% and 95% intervals, with Clopper–Pearson binomial intervals "
          "in brackets. The protocol judges coverage on development only: at h = 1 with the Kupiec (unconditional) and "
          "Christoffersen (independence) tests; at h > 1 the errors overlap, so there are no tests and the "
          "Clopper–Pearson brackets, which assume independent outcomes, are too narrow. Holdout coverage is reported "
          "without p-values, as the protocol requires. `ZC1-DIR` has no intervals (too few past errors for the "
          "burn-in). Full tables: `tables/c2_coverage.csv`.", lv)
    d.text("", "| sample | h | model | n | 80% coverage | 95% coverage | Kupiec p (80, 95) | Christoffersen p (80, 95) |",
           "|---|---|---|---|---|---|---|---|")
    h3 = {}
    hc = [{**r, "sample": "holdout"} for r in hold["c2"]["coverage_holdout"]]
    dc = [{**{k: (fl(v) if k in ("coverage", "cp_lo", "cp_hi", "kupiec_p", "christoffersen_p") else v) for k, v in r.items()},
           "sample": "development", "h": int(r["h"]), "level": float(r["level"]), "n": int(r["n"])} for r in cov_dev]
    for smp, rows, period, comp in [("development", dc, "1990Q1-2023Q2", f"{C2D}/forecast.py -> {C2D}/coverage_dev.csv"),
                                    ("holdout", hc, "2023Q3-2026Q2", f"{C2D}/holdout_run.py -> {HOLD} c2.coverage_holdout")]:
        for h in (1, 4, 8):
            for m in ("Z-DIR", "Z-DAMP", "no_change", "ar_bic"):
                rr = {r["level"]: r for r in rows if r["design"] == "latest-expanding" and r["h"] == h and r["model"] == m}
                nums, txt = [], []
                for lev in (0.8, 0.95):
                    r = rr[lev]
                    L = int(lev * 100)
                    parts = []
                    for key in ("coverage", "cp_lo", "cp_hi"):
                        c = cell(f"cov_{smp}_h{h}_{m}_{L}_{key}", f"C2 {smp}, expanding, h={h}, {m}: {L}% interval "
                                 f"{key} {{d}}.", r[key], "share", period, f"{comp}[latest-expanding,h={h},{m},{lev}].{key}",
                                 f"n = {r['n']}; Clopper-Pearson.")
                        parts.append(c[0])
                        nums.append(c[1])
                    txt.append(f"{parts[0]} [{parts[1]}, {parts[2]}]")
                tests = {"kupiec_p": [], "christoffersen_p": []}
                if h == 1 and smp == "development":
                    for key, nm in (("kupiec_p", "Kupiec"), ("christoffersen_p", "Christoffersen")):
                        for lev in (0.8, 0.95):
                            c = cell(f"cov_{smp}_h1_{m}_{int(lev*100)}_{key}", f"C2 {smp}, expanding, h=1, {m}: {nm} p "
                                     f"({int(lev*100)}%) {{d}}.", rr[lev][key], "p", period,
                                     f"{comp}[latest-expanding,h=1,{m},{lev}].{key}", f"{nm} coverage test.", fmt=fp)
                            tests[key].append(c[0])
                            if c[1]:
                                nums.append(c[1])
                            if m in ("Z-DIR", "Z-DAMP"):
                                h3.setdefault(m, []).append(rr[lev][key])
                d.add(f"| {smp} | {h} | {m} | {rr[0.8]['n']} | {txt[0]} | {txt[1]} | {', '.join(tests['kupiec_p']) or '—'} "
                      f"| {', '.join(tests['christoffersen_p']) or '—'} |", [n for n in nums if n])
    lines = []
    for m, ps in h3.items():
        ok = all(p is not None and p >= 0.05 for p in ps)
        lines.append(f"`{m}`: {'not rejected' if ok else 'rejected'} at h = 1" + ("" if all(p is not None for p in ps)
                                                                                    else " (a test is missing)"))
    d.text("", "**H3 (\"intervals are reliable\").** The protocol's wording needs coverage \"not rejected at either "
           "level on development data\" and sets no test level; reading \"rejected\" as p below five per cent (a "
           "reading, not a protocol rule): " + "; ".join(lines) + ". At h = 4 and 8 no test exists, so the wording "
           "cannot be used there. " + high_h_note(dc), "")


def nowcast_holdout(d: Doc, hold: dict, c1b: dict) -> None:
    d.text("### C1 and C1b nowcasts (real time, first-release targets)", "",
           "RMSE relative to no-change on the holdout, by instant k; pooled is k = 1–3. The C1b column compares "
           "C1b's bridge with no-change on the same instants.", "",
           "| k | instants | no-change RMSE | C1 bridge | bridge regression | drift | AR(1) | C1b bridge |",
           "|---|---|---|---|---|---|---|---|")
    sc = hold["c1"]["scores"]
    comp = f"{C2D}/holdout_run.py -> {HOLD} c1.scores"
    for k in (1, 2, 3, "all"):
        g = {s["model"]: s for s in sc if s["k"] == k}
        lab = "pooled" if k == "all" else str(k)
        cells = [cell(f"hold_c1_k{k}_nc_rmse", f"C1 holdout, k={lab}: no-change RMSE {{d}}.", g["no_change"]["rmse_pp"],
                      "pp", "2023Q3-2026Q2", f"{comp}[k={k},no_change].rmse_pp", "Real time.", SER_C1, suffix=" pp")]
        for m in ("bridge", "bridge_reg", "drift", "ar1"):
            cells.append(cell(f"hold_c1_k{k}_{m}_rel", f"C1 holdout, k={lab}: {m} RMSE relative to no-change {{d}}.",
                              g[m]["rel_rmse_vs_no_change"], "ratio", "2023Q3-2026Q2",
                              f"{comp}[k={k},{m}].rel_rmse_vs_no_change", "Real time; descriptive.", SER_C1))
        r = c1b["holdout"]["rmse_pp"][str(k)]
        cells.append(cell(f"hold_c1b_k{k}_rel", f"C1b holdout, k={lab}: C1b bridge RMSE relative to no-change {{d}}.",
                          r["bridge_c1b"] / r["no_change"], "ratio", "2023Q3-2026Q2",
                          f"{C1BD}/nowcast_c1b.py --holdout -> {C1B_HOLD} holdout.rmse_pp[{k}] bridge_c1b / no_change",
                          "Real time; descriptive.", SER_C1))
        table_row(d, [lab, str(g["bridge"]["n"])], cells)
    d.text("")


def c1_verdicts(hold: dict, t1: list[dict]) -> list[dict]:
    """C1 under rule (a), as C1's EVALUATION.md says ("Beats" follows C2's rule): the code mirrors holdout_run.py's
    wording logic. Holdout losses come from the committed holdout scores (same instants for every model at each k)."""
    out = []
    for t in t1:
        if t["sample"] != "RT" or t["primary_family"] != "True":
            continue
        g = {s["model"]: s for s in hold["c1"]["scores"] if str(s["k"]) == t["k"]}
        assert g[t["candidate"]]["n"] == g[t["benchmark"]]["n"]
        ratio = g[t["candidate"]]["rmse_pp"] / g[t["benchmark"]]["rmse_pp"]
        dev_ok = float(t["p_holm"]) < 0.05 and t["candidate_lower_rmse"] == "True"
        hold_lower = ratio < 1
        v = "beats" if dev_ok and hold_lower else (
            "does not beat" if t["candidate_lower_rmse"] != "True" or not hold_lower else "comparable")
        out.append({"k": t["k"], "candidate": t["candidate"], "benchmark": t["benchmark"], "p_holm": float(t["p_holm"]),
                    "n_holdout": g[t["candidate"]]["n"], "holdout_ratio": ratio, "verdict": v})
    return out


def c1_verdict_table(d: Doc, c1v: list[dict]) -> None:
    d.text("### C1 verdicts under rule (a)", "",
           "C1's EVALUATION.md says its wording follows C2's rule (a). Development Holm p from the table above; holdout "
           "ratio = candidate RMSE / benchmark RMSE on the same holdout instants (descriptive).", "",
           "| k | candidate | benchmark | holdout n | holdout ratio | verdict |", "|---|---|---|---|---|---|")
    for v in c1v:
        c = cell(f"c1v_k{v['k']}_{v['candidate']}_{v['benchmark']}", f"C1 holdout, k={v['k']}: {v['candidate']} RMSE "
                 f"relative to {v['benchmark']} {{d}} (verdict {v['verdict']}).", v["holdout_ratio"], "ratio",
                 "2023Q3-2026Q2", f"{HOLD} c1.scores[k={v['k']}] rmse_pp({v['candidate']}) / rmse_pp({v['benchmark']})",
                 "Real time; descriptive.", SER_C1)
        table_row(d, [v["k"], v["candidate"], v["benchmark"], str(v["n_holdout"])], [c, ("**" + v["verdict"] + "**", None)])
    d.text("")


def c1b_bias(d: Doc, nc1b: list[dict], nh: list[dict], bias_dev: list[dict]) -> None:
    """C1b's pre-registered bias report: mean error with a Newey-West lag-1 s.e., using C1b's own mean_hac1."""
    import importlib.util
    import numpy as np
    spec = importlib.util.spec_from_file_location("nowcast_c1b", ROOT / C1BD / "nowcast_c1b.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def table(rows):
        rows = [r for r in rows if r["k"] in ("1", "2", "3") and r["bridge_c1b"] != "" and r["actual"] != ""]
        out = {}
        for k in ("1", "2", "3", "all"):
            g = rows if k == "all" else [r for r in rows if r["k"] == k]
            if k == "all":
                g = sorted(g, key=lambda r: int(r["k"]))  # bias_table pools by concatenating the k groups
            for m in ("bridge_c1b", "bridge_c1", "no_change"):
                e = np.array([100 * (float(r[m]) - float(r["actual"])) for r in g])
                out[(k, m)] = (*mod.mean_hac1(e), len(g))
        return out

    dev = table(nc1b)
    for r in bias_dev:
        me, se, n = dev[(r["k"], r["model"])]
        assert n == int(r["n"]) and abs(me - float(r["mean_error_pp"])) < 1e-5, r
    hold = table(nh)
    d.text("### C1b: bias (pre-registered H2, reported descriptively)", "",
           "Mean error in pp (negative: nowcast below the outcome), with its Newey–West lag-1 standard error in "
           "brackets, computed with C1b's own `mean_hac1` on the committed tables. Development values reproduce "
           "`bias_dev.csv`.", "",
           "| sample | k | n | C1b bridge | C1 bridge | no change |", "|---|---|---|---|---|---|")
    for smp, tab, period, src in (("development", dev, "2016Q3-2023Q2", f"{C1BD}/nowcasts_dev.csv"),
                                  ("holdout", hold, "2023Q3-2026Q2", f"{C1BD}/nowcasts_holdout.csv")):
        for k in ("1", "2", "3", "all"):
            cells = []
            for m in ("bridge_c1b", "bridge_c1", "no_change"):
                me, se, n = tab[(k, m)]
                a = cell(f"bias_{smp}_k{k}_{m}", f"C1b {smp}, k={k}: {m} mean error {{d}}.", me, "pp", period,
                         f"{src} [k={k}] nowcast_c1b.mean_hac1(100*({m} - actual))[0]", f"n = {n}.", SER_C1, suffix=" pp")
                b = cell(f"bias_{smp}_k{k}_{m}_se", f"C1b {smp}, k={k}: {m} mean-error HAC(1) s.e. {{d}}.", se, "pp",
                         period, f"{src} [k={k}] nowcast_c1b.mean_hac1(100*({m} - actual))[1]", f"n = {n}.", SER_C1)
                cells.append((f"{a[0]} ({b[0]})", None))
                d_rows = [a[1], b[1]]
                cells[-1] = (cells[-1][0], d_rows)
            line = "| " + " | ".join([smp, "pooled" if k == "all" else k, str(tab[(k, 'no_change')][2])]
                                     + [c[0] for c in cells]) + " |"
            d.add(line, [r for c in cells for r in c[1]])
    d.text("")


def dev_tests_c1(d: Doc, t1: list[dict], t1b: list[dict]) -> None:
    d.text("### C1 and C1b development tests", "",
           "C1's primary family (bridge and bridge regression against no-change and AR(1), k = 1–3, real time), Holm "
           "over 12 tests; C1b's hypotheses H1 (RMSE) and H2 (bias) against C1, Holm over its own family. The "
           "Newey–West lag-1 sensitivity is in the source files.", "",
           "| task | k | candidate | benchmark or hypothesis | test | n | raw p | Holm p |", "|---|---|---|---|---|---|---|---|")
    for t in t1:
        if t["sample"] != "RT" or t["primary_family"] != "True":
            continue
        base = f"c1_k{t['k']}_{t['candidate']}_{t['benchmark']}"
        comp = f"{C1D}/nowcast.py -> {C1D}/tests_dev.csv [RT,k={t['k']},{t['candidate']},{t['benchmark']}]"
        cells = [cell(f"t_{base}_p", f"C1 development, k={t['k']}, {t['candidate']} vs {t['benchmark']}: raw p {{d}}.",
                      fl(t["p"]), "p", "2016Q3-2023Q2", comp + ".p", "Development test.", SER_C1, fmt=fp),
                 cell(f"t_{base}_holm", f"C1 development, k={t['k']}, {t['candidate']} vs {t['benchmark']}: Holm p {{d}}.",
                      fl(t["p_holm"]), "p", "2016Q3-2023Q2", comp + ".p_holm", "Holm over 12 tests.", SER_C1, fmt=fp)]
        table_row(d, ["C1", t["k"], t["candidate"], t["benchmark"], t["test"], t["n"]], cells)
    for t in t1b:
        base = f"c1b_k{t['k']}_{t['hypothesis'].split()[0]}"
        comp = f"{C1BD}/nowcast_c1b.py -> {C1BD}/tests_dev.csv [k={t['k']},{t['hypothesis']}]"
        cells = [cell(f"t_{base}_p", f"C1b development, k={t['k']}, {t['hypothesis']}: raw p {{d}}.", fl(t["p"]), "p",
                      "2016Q3-2023Q2", comp + ".p", "Development test.", SER_C1, fmt=fp),
                 cell(f"t_{base}_holm", f"C1b development, k={t['k']}, {t['hypothesis']}: Holm p {{d}}.", fl(t["p_holm"]),
                      "p", "2016Q3-2023Q2", comp + ".p_holm", "Holm over the C1b family.", SER_C1, fmt=fp)]
        table_row(d, ["C1b", t["k"], "bridge_c1b", t["hypothesis"] + " vs C1", t["test"], t["n"]], cells)
    d.text("")


def largest_errors(d: Doc, fc: list[dict], nc1: list[dict], nh: list[dict]) -> None:
    d.text("## 3. Failure cases: the ten largest errors per horizon", "",
           "Error = forecast − outcome, in pp of the share; ranked by size. Negative: the forecast was below the "
           "outcome.", "",
           "**C2 holdout: not available.** The one holdout run saved scores, coverage and verdicts but not the "
           "individual forecasts, and the holdout may not be reopened. Card c3-errors asks Eleonora how to treat "
           "this. C2's errors below are from development (latest vintage, expanding design).", "")
    out = []
    for h in (1, 4, 8):
        cols = {}
        for m in ("Z-DIR", "Z-DAMP"):
            rows = [r for r in fc if r["design"] == "latest-expanding" and r["h"] == str(h) and r[m] != ""]
            e = sorted(((100 * (float(r[m]) - float(r["actual"])), r["T"]) for r in rows), key=lambda x: -abs(x[0]))[:10]
            cols[m] = e
            out += [{"task": "C2", "sample": "development latest-expanding", "horizon": h, "model": m, "rank": i + 1,
                     "origin": T, "target": qadd(T, h), "error_pp": x} for i, (x, T) in enumerate(e)]
        d.text(f"C2, h = {h} (origin T, target T+{h}):", "", "| rank | Z-DIR target | Z-DIR error | Z-DAMP target | Z-DAMP error |",
               "|---|---|---|---|---|")
        for i in range(10):
            cells = []
            lab = [str(i + 1)]
            for m in ("Z-DIR", "Z-DAMP"):
                x, T = cols[m][i]
                c = cell(f"err_c2_h{h}_{m}_r{i+1}", f"C2 development, expanding, h={h}: {m} error ranked {i+1}, target "
                         f"{qadd(T, h)}, {{d}}.", x, "pp", qadd(T, h),
                         f"{C2D}/forecasts_dev.csv [latest-expanding,h={h},T={T}] 100*({m} - actual)",
                         "Development, latest vintage.", suffix=" pp")
                cells.append((qadd(T, h), None))
                cells.append(c)
            table_row(d, lab, cells)
        d.text("")
    # C1 development (RT) and C1/C1b holdout
    for tag, rows_all, models, title, period, src in [
        ("dev", [r for r in nc1 if r["sample"] == "RT" and r["actual"] != "" and r["k"] in ("1", "2", "3")],
         ("bridge",), "C1 development (real time)", "2016Q3-2023Q2", f"{C1D}/nowcasts_dev.csv [RT]"),
        ("hold", [r for r in nh if r["actual"] != ""], ("bridge_c1", "bridge_c1b"), "C1 and C1b holdout (real time)",
         "2023Q3-2026Q2", f"{C1BD}/nowcasts_holdout.csv")]:
        d.text(f"{title}, by instant k (target quarter q):", "",
               "| k | rank | " + " | ".join(f"{m} target | {m} error" for m in models) + " |",
               "|---|---|" + "---|---|" * len(models))
        for k in ("1", "2", "3"):
            rows = [r for r in rows_all if r["k"] == k]
            cols = {m: sorted(((100 * (float(r[m]) - float(r["actual"])), r["q"]) for r in rows),
                              key=lambda x: -abs(x[0]))[:10] for m in models}
            for m in models:
                out += [{"task": "C1b" if m == "bridge_c1b" else "C1", "sample": tag, "horizon": f"k={k}", "model": m,
                         "rank": i + 1, "origin": "", "target": q, "error_pp": x} for i, (x, q) in enumerate(cols[m])]
            for i in range(len(cols[models[0]])):
                cells = []
                for m in models:
                    x, q = cols[m][i]
                    cells.append((q, None))
                    cells.append(cell(f"err_c1_{tag}_k{k}_{m}_r{i+1}", f"{title}, k={k}: {m} error ranked {i+1}, "
                                      f"target {q}, {{d}}.", x, "pp", q, f"{src} [k={k},q={q}] 100*({m} - actual)",
                                      "First-release target.", SER_C1, suffix=" pp"))
                table_row(d, [k, str(i + 1)], cells)
        d.text("")
    write_table("largest_errors.csv", out)


def regimes(d: Doc, fc: list[dict], nc1: list[dict], nc1b: list[dict]) -> None:
    d.text("## 4. Results by regime (development sample)", "",
           "The windows are fixed by the protocol: 2007Q4–2011Q4 (\"GFC\") and 2020Q1–2020Q4 (\"2020\"). Both lie in "
           "development; the holdout (2023Q3–2026Q2) contains neither. The protocol does not say whether a forecast "
           "belongs to a window by its target quarter or by its origin, so both are shown. \"Rest\" is every development "
           "forecast whose split quarter is in neither window; at h = 4 and 8 some of those forecasts have their other "
           "quarter (origin or target) inside a window, so \"rest\" is not a clean calm-period sample. Cells: each "
           "model's RMSE divided by no-change's RMSE on the same forecasts (below one: better than no-change); "
           "no-change RMSE in pp. ‡ marks fewer than ten forecasts: such cells are anecdotes, not estimates.", "",
           "| split by | window | h | n | no-change RMSE | Z-DIR | Z-DAMP | AR (BIC) |", "|---|---|---|---|---|---|---|---|")
    out = []
    for by in ("target", "origin"):
        for name, lo, hi in REGIMES + [("rest", None, None)]:
            for h in (1, 4, 8):
                rows = [r for r in fc if r["design"] == "latest-expanding" and r["h"] == str(h)]
                q = (lambda r: qadd(r["T"], h)) if by == "target" else (lambda r: r["T"])
                if lo:
                    rows = [r for r in rows if inwin(q(r), lo, hi)]
                else:
                    rows = [r for r in rows if not any(inwin(q(r), a, b) for _, a, b in REGIMES)]
                e = {m: rmse([100 * (float(r[m]) - float(r["actual"])) for r in rows]) for m in
                     ("no_change", "Z-DIR", "Z-DAMP", "ar_bic")}
                win = f"{lo}–{hi}" if lo else "rest"
                base = f"reg_{by}_{name}_h{h}"
                src = f"{C2D}/forecasts_dev.csv [latest-expanding,h={h}, {by} quarter in {win}]"
                cells = [cell(f"{base}_nc", f"C2 development, expanding, h={h}, {by} in {win}: no-change RMSE {{d}}.",
                              e["no_change"], "pp", win, src + " RMSE of 100*(no_change - actual)", f"n = {len(rows)}.",
                              suffix=" pp")]
                for m in ("Z-DIR", "Z-DAMP", "ar_bic"):
                    cells.append(cell(f"{base}_{m}", f"C2 development, expanding, h={h}, {by} in {win}: {m} RMSE "
                                      f"relative to no-change {{d}}.", e[m] / e["no_change"], "ratio", win,
                                      src + f" RMSE({m}) / RMSE(no_change)", f"n = {len(rows)}."))
                out += [{"task": "C2", "split_by": by, "window": win, "horizon": h, "n": len(rows), "model": m,
                         "rmse_pp": v} for m, v in e.items()]
                table_row(d, [by, f"{name} ({win})" if lo else "rest", str(h), nmark(len(rows))], cells)
    d.text("", "Nowcasts. C1's real-time sample starts with target 2016Q3, so it covers 2020 but not the GFC window; "
           "the pseudo-real-time sample P2a (not real time) covers only 2010Q2–2011Q4 of it. Split by target quarter.",
           "", "| task | sample | window | k | n | no-change RMSE | bridge / no-change | C1b bridge / no-change |",
           "|---|---|---|---|---|---|---|---|")
    for sample, (name, lo, hi) in [("RT", REGIMES[1]), ("P2a", ("GFC (part)", "2010Q2", "2011Q4"))]:
        for k in ("1", "2", "3"):
            rows = [r for r in nc1 if r["sample"] == sample and r["k"] == k and r["actual"] != "" and r["bridge"] != ""
                    and inwin(r["q"], lo, hi)]
            e = {m: rmse([100 * (float(r[m]) - float(r["actual"])) for r in rows]) for m in ("no_change", "bridge")}
            src = f"{C1D}/nowcasts_dev.csv [{sample},k={k}, target in {lo}–{hi}]"
            base = f"reg_c1_{sample}_{name.split()[0]}_k{k}"
            cells = [cell(base + "_nc", f"C1 development, {sample}, k={k}, target in {lo}–{hi}: no-change RMSE {{d}}.",
                          e["no_change"], "pp", f"{lo}-{hi}", src + " RMSE of 100*(no_change - actual)", f"n = {len(rows)}.",
                          SER_C1, suffix=" pp"),
                     cell(base + "_bridge", f"C1 development, {sample}, k={k}, target in {lo}–{hi}: bridge RMSE relative "
                          "to no-change {d}.", e["bridge"] / e["no_change"], "ratio", f"{lo}-{hi}",
                          src + " RMSE(bridge) / RMSE(no_change)", f"n = {len(rows)}.", SER_C1)]
            if sample == "RT":
                rb = [r for r in nc1b if r["k"] == k and r["actual"] != "" and inwin(r["q"], lo, hi)]
                eb = {m: rmse([100 * (float(r[m]) - float(r["actual"])) for r in rb]) for m in ("no_change", "bridge_c1b")}
                assert len(rb) == len(rows) and abs(eb["no_change"] - e["no_change"]) < 1e-9, (k, len(rb), len(rows))
                cells.append(cell(base + "_c1b", f"C1b development, k={k}, target in {lo}–{hi}: C1b bridge RMSE relative "
                                  "to no-change {d}.", eb["bridge_c1b"] / eb["no_change"], "ratio", f"{lo}-{hi}",
                                  f"{C1BD}/nowcasts_dev.csv [k={k}, target in {lo}–{hi}] RMSE(bridge_c1b) / RMSE(no_change)",
                                  f"n = {len(rb)}.", SER_C1))
            else:
                cells.append(("—", None))
            out += [{"task": "C1", "split_by": "target", "window": f"{lo}–{hi} ({sample})", "horizon": f"k={k}",
                     "n": len(rows), "model": m, "rmse_pp": v} for m, v in e.items()]
            table_row(d, ["C1", sample, f"{name} ({lo}–{hi})", k, nmark(len(rows))], cells)
    d.text("")
    write_table("regimes.csv", out)


def revisions(d: Doc, scores2: list[dict], sc1: list[dict]) -> None:
    d.text("## 5. The revision effect: first release against latest vintage", "",
           "C2 real-time check: origins at each archived Z.1 release from 2016-09-16, with the real-time data of each "
           "release. Scored against the first release of the target and against the latest vintage; the third row "
           "at each horizon re-scores the same origins with latest-vintage data throughout (the primary design). Cells: RMSE "
           "relative to no-change; no-change RMSE in pp.", "",
           "| h | scoring | n | no-change RMSE | Z-DIR | Z-DAMP | drift | AR (BIC) |", "|---|---|---|---|---|---|---|---|")
    labels = {"realtime-vs-first": "real-time data, first-release target",
              "realtime-vs-latest": "real-time data, latest-vintage target",
              "latest-on-realtime-origins": "latest-vintage data and target, same origins"}
    for h in (1, 4, 8):
        for des, lab in labels.items():
            g = {s["model"]: s for s in scores2 if s["design"] == des and s["h"] == str(h)}
            comp = f"{C2D}/forecast.py -> {C2D}/scores_dev.csv [{des},h={h}"
            cells = [cell(f"rev_c2_{des}_h{h}_nc", f"C2 real-time check, h={h}, {lab}: no-change RMSE {{d}}.",
                          fl(g["no_change"]["rmse_pp"]), "pp", "2016Q2-2023Q2", comp + ",no_change].rmse_pp",
                          f"n = {g['no_change']['n']}.", suffix=" pp")]
            for m in ("Z-DIR", "Z-DAMP", "drift", "ar_bic"):
                cells.append(cell(f"rev_c2_{des}_h{h}_{m}", f"C2 real-time check, h={h}, {lab}: {m} RMSE relative to "
                                  "no-change {d}.", fl(g[m]["rel_rmse_vs_no_change"]), "ratio", "2016Q2-2023Q2",
                                  comp + f",{m}].rel_rmse_vs_no_change", f"n = {g[m]['n']}."))
            table_row(d, [str(h), lab, g["no_change"]["n"]], cells)
    d.text("", "C1: the real-time nowcast scored against the first release (RT, primary) and against the latest "
           "vintage (RT-latest).", "", "| k | target | n | no-change RMSE | bridge / no-change |", "|---|---|---|---|---|")
    for k in ("1", "2", "3", "all"):
        for smp, lab in (("RT", "first release"), ("RT-latest", "latest vintage")):
            g = {s["model"]: s for s in sc1 if s["sample"] == smp and s["k"] == k}
            comp = f"{C1D}/nowcast.py -> {C1D}/scores_dev.csv [{smp},k={k}"
            cells = [cell(f"rev_c1_{smp}_k{k}_nc", f"C1 development, k={k}, {lab} target: no-change RMSE {{d}}.",
                          fl(g["no_change"]["rmse_pp"]), "pp", "2016Q3-2023Q2", comp + ",no_change].rmse_pp",
                          f"n = {g['no_change']['n']}.", SER_C1, suffix=" pp"),
                     cell(f"rev_c1_{smp}_k{k}_bridge", f"C1 development, k={k}, {lab} target: bridge RMSE relative to "
                          "no-change {d}.", fl(g["bridge"]["rel_rmse_vs_no_change"]), "ratio", "2016Q3-2023Q2",
                          comp + ",bridge].rel_rmse_vs_no_change", f"n = {g['bridge']['n']}.", SER_C1)]
            table_row(d, ["pooled" if k == "all" else k, lab, g["bridge"]["n"]], cells)
    d.text("")


def indicators_and_deviations(d: Doc, scores2: list[dict], hold: dict) -> None:
    d.text("## 6. Were C1's indicators used?", "",
           "Yes, in two places. (1) `ZC1-DIR` is C2's `Z-DIR` plus C1's accounting-bridge nowcast as one regressor. "
           "It can be scored only where C1's point-in-time panel exists, so its development comparison has few "
           "origins (the n column below) and its holdout comparison is on the expanding design only. (2) C1 and C1b "
           "are themselves the indicator models; their results are in section 2.", "",
           "| sample | h | n | ZC1-DIR / no-change | Z-DIR / no-change, same origins |", "|---|---|---|---|---|")
    for smp, rows, comp, period, src in [
        ("development", [s for s in scores2 if s["comparison"] == "Z+C1 common origins"], "Z+C1 common origins",
         "2018Q4-2023Q2", f"{C2D}/scores_dev.csv"),
        ("holdout", [s for s in hold["c2"]["scores_holdout"] if s["comparison"] == "Z+C1 holdout"], "Z+C1 holdout",
         "2023Q3-2026Q2", f"{HOLD} c2.scores_holdout")]:
        for h in (1, 4, 8):
            g = {s["model"]: s for s in rows if str(s["h"]) == str(h)}
            cells = [cell(f"ind_{smp}_h{h}_{m}", f"C2 {smp}, {comp}, h={h}: {m} RMSE relative to no-change {{d}}.",
                          fl(g[m]["rel_rmse_vs_no_change"]), "ratio", period, f"{src} [{comp},h={h},{m}].rel_rmse_vs_no_change",
                          f"n = {g[m]['n']}.") for m in ("ZC1-DIR", "Z-DIR")]
            table_row(d, [smp, str(h), nmark(g["ZC1-DIR"]["n"])], cells)
    d.text("", "## 7. Deviations and process issues, dated", "",
           "Each is recorded in full in the file named.", "",
           "- **2026-11-04, protocol fact correction** (`docs/decisions/scoring-protocol.md`): Z.1 text archives exist "
           "before 2016-09; the real-time check still starts 2016-09-16. No design change.",
           "- **2026-11-04, C1 holdout aligned to the protocol** (protocol and `research/c1_nowcast/EVALUATION.md`): "
           "C1's holdout is 2023Q3–2026Q2, and its tests are C2's.",
           "- **2026-11-04, C2 test ordering** (`research/c2_forecast/SPECS.md`, accepted by Eleonora): the first "
           "development scoring ran before the leakage tests existed. They passed with no code change.",
           "- **2026-11-04, seasonal naive in the Holm family** (SPECS.md, accepted by Eleonora): seasonal-naive "
           "comparisons joined the Holm family. The family on record has 42 tests: 28 against no-change and AR plus "
           "14 against seasonal naive. SPECS.md's deviation text says the family grew \"from 36 to 42\"; that count "
           "is wrong (the end count of 42 is right). Found by quant-reviewer (mkt-q39); SPECS.md is left as accepted.",
           "- **Not a deviation, but undocumented:** `ZC1-DIR` has no test at h = 8, because `forecast.py` skips any "
           "pair with fewer than 8 development forecasts and that comparison has 4 (mkt-q39).",
           "- **2026-11-04, placebo redefined** (SPECS.md, Eleonora's option (a)): the options were written after the "
           "first placebo result was seen, and the card said so. Both placebo versions are in section 1.",
           "- **2026-11-04, C1 rescored after review** (EVALUATION.md, quant-reviewer q11–q16, skeptic s9–s15): fourth "
           "instant made k = 4 and not scored; the missing 2017-03-09 release found; like-for-like and HAC-lag-1 "
           "sensitivities added. The superseded scores are in section 1 (58a93d8).",
           "- **2026-11-04, C1's declared differences from C2** (EVALUATION.md, q15): a fixed AR(1) benchmark (her "
           "choice for C1) instead of BIC order; in the pseudo-real-time samples the bridge regression trains on "
           "revised targets with no embargo; C2's leakage test 5 (placebo) and the outcome checks are not implemented "
           "for C1.",
           "- **2026-11-04, C2 implementation fixes after review** (SPECS.md, q17–q24): leakage tests through the "
           "production code; Clark–West for the nested h = 1 pairs against AR; a lag-8 sensitivity, under which the "
           "h = 1 result is not robust. Development scores unchanged; tests changed.",
           "- **2026-11-05, c1b-dev-1 (a)** (protocol, EVALUATION.md, `docs/decisions/c1b-prereg.md`; Eleonora's "
           "decision): the first joint holdout run (approval 77460b4) stopped on a target quarter no Z.1 had published, "
           "before writing or printing anything. Such instants are now \"no target\"; the freeze was redone, and the "
           "one run used the new approval 432fed0.",
           "- **2026-11-05, holdout counting** (found in this report's review, mkt-q32; not declared before the run): the "
           "run counted holdout forecasts by target quarter (12 at every h), while the protocol's option text counts "
           "by origin (12, 9 and 5). Sent to the coordinator as a proposed card.",
           "- **2026-11-05, this report** (not yet a recorded deviation): C2's holdout per-forecast errors were not saved, "
           "so item \"ten largest errors per horizon\" is met for development and for the C1/C1b holdout only (card "
           "c3-errors). The regime split is shown both by target and by origin quarter, because the protocol does not "
           "say which.", "",
           "## Sources", "",
           "`research/c2_forecast/` (`holdout_results.json`, `scores_dev.csv`, `tests_dev.csv`, `coverage_dev.csv`, "
           "`forecasts_dev.csv`, `placebo_dev.json` and its version at 0bc647b), `research/c1_nowcast/` (`scores_dev.csv`, "
           "`tests_dev.csv`, `nowcasts_dev.csv`, and `scores_dev.csv` at 58a93d8), `research/c1b_nowcast/` "
           "(`holdout_results.json`, `nowcasts_holdout.csv`, `scores_dev.csv`, `tests_dev.csv`, `nowcasts_dev.csv`). "
           "Full tables written by this script: `tables/c2_holdout_scores.csv`, `tables/c2_coverage.csv`, "
           "`tables/c2_verdicts.csv`, `tables/largest_errors.csv`, `tables/regimes.csv`.", "")


def main() -> int:
    hold = json.loads((ROOT / HOLD).read_text())
    c1b = json.loads((ROOT / C1B_HOLD).read_text())
    assert hold["approval_commit"] == "432fed0" and hold["mode"].startswith("HOLDOUT RUN")
    scores2, tests2 = read_csv(f"{C2D}/scores_dev.csv"), read_csv(f"{C2D}/tests_dev.csv")
    fc, cov_dev = read_csv(f"{C2D}/forecasts_dev.csv"), read_csv(f"{C2D}/coverage_dev.csv")
    placebo = json.loads((ROOT / C2D / "placebo_dev.json").read_text())
    placebo_old = git_json("0bc647b", f"{C2D}/placebo_dev.json")
    sc1, t1, nc1 = read_csv(f"{C1D}/scores_dev.csv"), read_csv(f"{C1D}/tests_dev.csv"), read_csv(f"{C1D}/nowcasts_dev.csv")
    sc1_old = git_csv("58a93d8", f"{C1D}/scores_dev.csv")
    sc1b, t1b = read_csv(f"{C1BD}/scores_dev.csv"), read_csv(f"{C1BD}/tests_dev.csv")
    nc1b, nh = read_csv(f"{C1BD}/nowcasts_dev.csv"), read_csv(f"{C1BD}/nowcasts_holdout.csv")
    verdicts = hold["c2"]["verdicts"]
    check_c2_dev_errors(fc, scores2)
    check_c1_dev_errors(nc1, sc1)
    check_c1b_hold(nh, c1b, hold["c1"])
    check_verdicts(verdicts, tests2)

    d = Doc()
    banner(d)
    c1v = c1_verdicts(hold, t1)
    headline(d, verdicts, c1b, fc, hold, c1v)
    registry(d, scores2, placebo_old, placebo, sc1, sc1_old, sc1b)
    sh = c2_holdout(d, hold)
    verdict_table(d, verdicts)
    coverage(d, hold, cov_dev)
    nowcast_holdout(d, hold, c1b)
    dev_tests_c1(d, t1, t1b)
    c1_verdict_table(d, c1v)
    c1b_bias(d, nc1b, nh, read_csv(f"{C1BD}/bias_dev.csv"))
    largest_errors(d, fc, nc1, nh)
    regimes(d, fc, nc1, nc1b)
    revisions(d, scores2, sc1)
    indicators_and_deviations(d, scores2, hold)
    write_table("c2_holdout_scores.csv", sh)
    write_table("c2_coverage.csv", [{"sample": "holdout", **r} for r in hold["c2"]["coverage_holdout"]]
                + [{"sample": "development", **r} for r in cov_dev])
    write_table("c2_verdicts.csv", verdicts)
    (HERE / "README.md").write_text("\n".join(d.lines))
    new = write_track_rows(d.rows, prefix="c3_")
    print(f"README.md: {len(d.lines)} lines; {len(d.rows)} rows, {len(new)} written to claims/tracks/markets.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
