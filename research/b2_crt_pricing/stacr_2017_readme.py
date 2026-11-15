"""The "STACR 2017+" section of the B2 README and its register rows, from stacr_2017.py's committed outputs.

Called by make_readme_and_rows.py, which places the section and turns each row's line index into a README location.
Every number shown gets a row: section() returns (lines, rows), where each row carries "_line" (index into lines).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "stacr_2017_results.json").read_text())
YC = pd.read_csv(HERE / "stacr_2017_by_year_class.csv")
SRC = "Freddie Mac STACR pricing workbook (stacr-pricing.xlsx, sha256 e10971eb...)"
VINT = "stacr:2026-11-05"
P = "research/b2_crt_pricing/stacr_2017.py -> "


class Section:
    def __init__(self):
        self.lines: list[str] = []
        self.rows: list[dict] = []

    def text(self, *ts: str) -> None:
        self.lines.extend(ts)

    def add(self, line: str, nums: list[dict]) -> None:
        for n in nums:
            assert n["display"] in line, (n["claim_id"], n["display"], line)
            n["_line"] = len(self.lines)
        self.lines.append(line)
        self.rows.extend(nums)


def num(cid, claim, disp, val, unit, period, comp, status="UNVERIFIED", notes="", sids=SRC):
    return {"claim_id": "b2_stacr_" + cid, "claim": claim, "display": disp, "value": f"{float(val):.6g}", "unit": unit,
            "period": period, "computation": P + comp, "series_ids": sids, "vintage": VINT, "validation": status,
            "check_id": "", "notes": ("Claude draft section (B2 STACR 2017+). " + notes).strip()}


f0 = lambda x: f"{x:.0f}"
f1 = lambda x: f"{x:.1f}"


def section() -> tuple[list[str], list[dict]]:
    s = Section()
    cb, oc, ba = R["count_breakdown_her_classes"], R["outside_classes"], R["by_attach"]
    cum = R["baseline"]["cum_loss_bp_of_original"]
    adj = R["libor_1m_adj_bp"]
    assert R["libor_adj_status"] == "set" and adj == 11.448
    years = f"{YC['year'].min()}–{YC['year'].max()}"
    lib = YC[YC["libor_tranches"] > 0]["year"]
    s.text("## STACR 2017+: issuance spread and baseline-loss multiple, by tranche class", "",
           "> Built to Eleonora's choices of 2026-11-05: on cards b2-1723 "
           "(15:55 UTC) measure (ii), tranches (b), indicative (b) and LIBOR→SOFR (b); on cards b2-sofr-src (a), "
           "b2-upb (a) and b2-empty (a) (18:54 UTC). Method: `METHOD.md`, \"STACR 2017+\". Code: `stacr_2017.py`; "
           "data: `stacr_2017_tranches.csv`, `stacr_2017_by_year_class.csv`.", "")
    s.add(f"Freddie Mac's STACR pricing workbook prints, for each deal, the spread at issuance and the credit "
          f"enhancement of every tranche it lists (sold, and a few retained). From 2017 it covers {R['deals']} deals and {R['tranches']} tranches. "
          f"{R['tranches_her_classes']} are in her three classes (M-1, including M-1A and M-1B; M-2; B, including "
          f"B-1 and B-2); the other {R['tranches_outside_classes']} ({oc['A-1']} A-1, {oc['M-3']} M-3) are kept in the "
          "tranche file but not summarized. Fannie Mae's CAS deals are not covered: its host is not reachable "
          "(`sources.md`).",
          [num("deals", f"STACR deals closing 2017 or later in the workbook: {R['deals']}.", str(R["deals"]), R["deals"],
               "count", years, "stacr_2017_results.json deals"),
           num("tranches", f"STACR tranches 2017+: {R['tranches']}.", str(R["tranches"]), R["tranches"], "count", years,
               "stacr_2017_results.json tranches"),
           num("tranches_her", f"STACR tranches 2017+ in classes M-1, M-2, B: {R['tranches_her_classes']}.",
               str(R["tranches_her_classes"]), R["tranches_her_classes"], "count", years,
               "stacr_2017_results.json tranches_her_classes"),
           num("tranches_outside", f"STACR tranches 2017+ outside the three classes: {R['tranches_outside_classes']}.",
               str(R["tranches_outside_classes"]), R["tranches_outside_classes"], "count", years,
               "stacr_2017_results.json tranches_outside_classes"),
           num("n_a1", f"A-1 tranches 2017+: {oc['A-1']}.", str(oc["A-1"]), oc["A-1"], "count", years,
               "stacr_2017_results.json outside_classes.A-1"),
           num("n_m3", f"M-3 tranches 2017+: {oc['M-3']}.", str(oc["M-3"]), oc["M-3"], "count", years,
               "stacr_2017_results.json outside_classes.M-3")])
    s.text("")
    s.add(f"- **Spread.** As printed at issuance, over the deal's benchmark. Deals on one-month LIBOR "
          f"({lib.min()}–{lib.max()}) get the published LIBOR-to-SOFR adjustment of {adj} bps added (Federal "
          "Reserve, Regulation ZZ, 12 CFR part 253, section 4(c)(2); `sources.md`), so every spread below is over SOFR. The "
          "adjustment is a fixed fallback spread; the LIBOR–SOFR gap on each deal's pricing date would differ.",
          [num("libor_adj", f"LIBOR-to-SOFR adjustment for one-month LIBOR: {adj} bps (Regulation ZZ).", f"{adj} bps",
               adj, "bp", "n/a", "LIBOR_1M_ADJ_BP", "UNVERIFIED",
               "Source constant: Federal Reserve Regulation ZZ final rule, 12 CFR part 253 section 4(c)(2), quoted in sources.md.",
               "Federal Reserve Board, Regulation ZZ final rule (2022-12-16)")])
    s.add(f"- **Multiple.** Spread ÷ the tranche's expected loss a year per dollar of tranche under FHFA's December 2016 "
          f"baseline (10% prepayment, 0.2% annual defaults, 25% loss given default, redemption at 10 years), on the "
          f"average outstanding balance. Applying that 2016 baseline to later deals is an assumption. The baseline "
          f"pool loses {f1(cum)} bps of its original balance over ten years, so only a tranche attaching below "
          f"{f1(cum)} bps has an expected loss and a multiple.",
          [num("cum_loss", f"Baseline cumulative pool loss, ten years: {f1(cum)} bps of original balance.",
               f"{f1(cum)} bps", cum, "bp", "n/a", "stacr_2017_results.json baseline.cum_loss_bp_of_original",
               "ESTIMATE", "Model output under FHFA's 2016 baseline scenario.")])
    s.add(f"- **\"(Indicative)\" tranches.** {R['retained_indicative']} tranches in 2017–2018 were retained by Freddie "
          "and carry an indicative spread in place of a sale price. They are kept and flagged (`retained_indicative`).",
          [num("indicative", f"Retained tranches with an indicative spread, 2017+: {R['retained_indicative']}.",
               str(R["retained_indicative"]), R["retained_indicative"], "count", "2017-2018",
               "stacr_2017_results.json retained_indicative")])
    s.text("", "**By year and class** (spreads over SOFR in bps, median with range; multiples for B tranches that "
           "have one, median):", "",
           "| Year | M-1: tranches (indicative) | M-1 spread | M-2: tranches | M-2 spread | B: tranches (indicative) | "
           "B spread (range) | B with a multiple (indicative) | Multiple, outstanding basis | Multiple, original basis |",
           "|---|---|---|---|---|---|---|---|---|---|")
    for y in sorted(YC["year"].unique()):
        g = YC[YC["year"] == y].set_index("cls")
        cells, nums = [str(y)], []
        for c in ("M-1", "M-2", "B"):
            if c not in g.index:
                cells += ["–", "–"] if c != "B" else ["–", "–", "–", "–", "–"]
                continue
            r = g.loc[c]
            k = c.lower().replace("-", "")
            nt = int(r["tranches"])
            ind = int(r["retained_indicative"])
            tcell = f"{nt}" + (f" ({ind})" if ind else "")
            nums.append(num(f"{y}_{k}_n", f"{y}, class {c}: {nt} tranches with a spread.", tcell, nt, "count", str(y),
                            f"stacr_2017_by_year_class.csv tranches[{y},{c}]"))
            sp = f0(r["spread_sofr_bp_median"])
            nums.append(num(f"{y}_{k}_spread", f"{y}, class {c}: median issuance spread over SOFR {sp} bps.", sp,
                            r["spread_sofr_bp_median"], "bp", str(y),
                            f"stacr_2017_by_year_class.csv spread_sofr_bp_median[{y},{c}]",
                            notes="LIBOR deals adjusted by +11.448 bps." if r["libor_tranches"] else ""))
            if c != "B":
                cells += [tcell, sp]
                continue
            rng = f"{sp} ({f0(r['spread_sofr_bp_min'])}–{f0(r['spread_sofr_bp_max'])})"
            for nm in ("min", "max"):
                nums.append(num(f"{y}_b_spread_{nm}", f"{y}, class B: {nm} issuance spread over SOFR "
                                f"{f0(r[f'spread_sofr_bp_{nm}'])} bps.", f0(r[f"spread_sofr_bp_{nm}"]),
                                r[f"spread_sofr_bp_{nm}"], "bp", str(y),
                                f"stacr_2017_by_year_class.csv spread_sofr_bp_{nm}[{y},B]"))
            wm = int(r["with_multiple"])
            wi = int(r["with_multiple_indicative"])
            mcell = [str(wm) + (f" ({wi})" if wi else ""), "–", "–"]
            nums.append(num(f"{y}_b_with_multiple", f"{y}, class B: {wm} tranches with a multiple.", mcell[0], wm,
                            "count", str(y), f"stacr_2017_by_year_class.csv with_multiple[{y},B]"))
            if wm:
                for basis, i in (("out", 1), ("orig", 2)):
                    v = r[f"multiple_sofr_{basis}_median"]
                    mcell[i] = f1(v)
                    nums.append(num(f"{y}_b_multiple_{basis}", f"{y}, class B: median multiple of baseline expected "
                                    f"loss ({'outstanding' if basis == 'out' else 'original'} basis) {f1(v)}.", f1(v), v,
                                    "ratio", str(y), f"stacr_2017_by_year_class.csv multiple_sofr_{basis}_median[{y},B]",
                                    "ESTIMATE", "Spread over SOFR / baseline EL per dollar of tranche."))
            cells += [tcell, rng] + mcell
        s.add("| " + " | ".join(cells) + " |", nums)
    s.text("")
    s.add(f"- **The multiple exists for few tranches.** Of the {R['tranches_her_classes']} tranches in her classes, "
          f"{cb['with_multiple']} have a multiple, all of them B-2 tranches. The rest: {cb['attach_at_or_above_baseline_loss']} "
          f"attach at or above the baseline's {f1(cum)} bps loss, {cb['detach_unknown']} have no known detachment "
          f"point (2019-FTR1, -FTR3 and -FTR4 list only B-2 and the senior class), and {cb['no_spread']} have no single "
          f"spread (2017-HRP1's M-2, B-1 and B-2 print a par/discount/IO split, not parsed), so the table above covers "
          f"{R['tranches_her_classes'] - cb['no_spread']}. Of the {cb['with_multiple']} multiples, "
          f"{int(YC['with_multiple_indicative'].sum())} are on retained B-2 tranches with an indicative spread "
          f"(2017–2018). M-1, M-2 and B-1 never get a multiple; for them the measure is the spread alone. From "
          f"{R['first_year_no_multiple']} no sold tranche attaches below {f1(cum)} bps.",
          [num("with_multiple", f"Tranches 2017+ in her classes with a multiple: {cb['with_multiple']}.",
               str(cb["with_multiple"]), cb["with_multiple"], "count", years,
               "stacr_2017_results.json count_breakdown_her_classes.with_multiple"),
           num("above_loss", f"Tranches 2017+ in her classes attaching at or above the baseline loss: "
               f"{cb['attach_at_or_above_baseline_loss']}.", str(cb["attach_at_or_above_baseline_loss"]),
               cb["attach_at_or_above_baseline_loss"], "count", years,
               "stacr_2017_results.json count_breakdown_her_classes.attach_at_or_above_baseline_loss"),
           num("detach_unknown", f"Tranches 2017+ in her classes with no known detachment point: {cb['detach_unknown']}.",
               str(cb["detach_unknown"]), cb["detach_unknown"], "count", "2019",
               "stacr_2017_results.json count_breakdown_her_classes.detach_unknown"),
           num("no_spread", f"Tranches 2017+ in her classes with no spread printed: {cb['no_spread']}.",
               str(cb["no_spread"]), cb["no_spread"], "count", "2017",
               "stacr_2017_results.json count_breakdown_her_classes.no_spread"),
           num("table_n", f"Tranches 2017+ in her classes with a spread (table): {R['tranches_her_classes'] - cb['no_spread']}.",
               str(R["tranches_her_classes"] - cb["no_spread"]), R["tranches_her_classes"] - cb["no_spread"], "count",
               years, "stacr_2017_results.json tranches_her_classes - count_breakdown_her_classes.no_spread"),
           num("multiple_indicative", f"B-2 multiples on retained tranches with an indicative spread: "
               f"{int(YC['with_multiple_indicative'].sum())}.", str(int(YC["with_multiple_indicative"].sum())),
               int(YC["with_multiple_indicative"].sum()), "count", "2017-2018",
               "stacr_2017_by_year_class.csv sum(with_multiple_indicative)"),
           num("first_year_none", f"First year from which no sold STACR tranche has a multiple: "
               f"{R['first_year_no_multiple']}.", str(R["first_year_no_multiple"]), R["first_year_no_multiple"],
               "year", f"{R['first_year_no_multiple']}-{YC['year'].max()}", "stacr_2017_results.json first_year_no_multiple")])
    fs, fsn = R["fixed_slice_25_75"], R["fixed_slice_25_75_n"]
    fnums = []
    for y, v in fs.items():
        fnums.append(num(f"fixed_25_75_{y}", f"{y}: median multiple (outstanding basis) of B-2 tranches on a 25-75 bps "
                         f"slice: {f1(v)} ({fsn[y]} tranches).", f1(v), v, "ratio", y,
                         f"stacr_2017_results.json fixed_slice_25_75[{y}]", "ESTIMATE"))
    s.add("- **The multiple moves with where B-2 sits, and with price.** A B-2 that attaches higher takes less of the "
          "baseline loss, and a thicker one spreads that loss over more notional; either raises the multiple at the "
          "same spread. Freddie moved B-2's attachment point up over these years, which moves the yearly medians "
          "above. Holding the slice fixed (attach 25 bps, detach 75 bps), the median multiple is "
          + ", ".join(f"{f1(v)} in {y}" for y, v in fs.items())
          + ", so changes on a fixed slice are changes in spread. By slice:", fnums)
    s.text("", "| B-2 slice (attach–detach, bps) | Tranches (indicative) | Years | Baseline loss taken (bps of original "
           "balance) | Multiple, median (range) |", "|---|---|---|---|---|")
    for b in ba:
        a, dd = f0(b["attach_bp"]), f0(b["detach_bp_slice"])
        k = f"slice{a}_{dd}"
        yrs = b["years"] if b["years"][:4] != b["years"][5:] else b["years"][:4]
        med, lo, hi = (f1(b[f"multiple_sofr_out_{x}"]) for x in ("median", "min", "max"))
        ncell = str(b["tranches"]) + (f" ({b['indicative']})" if b["indicative"] else "")
        nums = [num(f"{k}_n", f"B-2 tranches on a {a}-{dd} bps slice with a multiple: {b['tranches']}.", ncell,
                    b["tranches"], "count", yrs, f"stacr_2017_results.json by_attach[{a},{dd}].tranches"),
                num(f"{k}_loss", f"Baseline loss taken by a slice attaching at {a} bps: {f1(b['slice_loss_bp'])} bps.",
                    f1(b["slice_loss_bp"]), b["slice_loss_bp"], "bp", "n/a",
                    f"stacr_2017_results.json by_attach[{a},{dd}].slice_loss_bp", "ESTIMATE")]
        xs = (("median", med), ("min", lo), ("max", hi)) if b["tranches"] > 1 else (("median", med),)
        for x, d in xs:
            nums.append(num(f"{k}_multiple_{x}", f"B-2 on a {a}-{dd} bps slice: {x} multiple (outstanding basis) {d}.",
                            d, b[f"multiple_sofr_out_{x}"], "ratio", yrs, f"stacr_2017_results.json "
                            f"by_attach[{a},{dd}].multiple_sofr_out_{x}", "ESTIMATE"))
        mcell = f"{med} ({lo}–{hi})" if b["tranches"] > 1 else med
        s.add(f"| {a}–{dd} | {ncell} | {yrs.replace('-', '–')} | {f1(b['slice_loss_bp'])} | {mcell} |", nums)
    s.text("",
           "- **Each class's contents change by year.** B holds B-1 and B-2 in shifting shares, and only B-1 in 2023 "
           "and 2026; M-1 holds M-1A and M-1B from 2022; attachment points drift within each class. A change in a "
           "class's median spread can therefore reflect its make-up as well as price. Tranche detail is in "
           "`stacr_2017_tranches.csv`.")
    s.text("",
           "- **Not like for like with 2013–2016.** There, FHFA's credit cost is a cost per dollar of the reference "
           "pool for the whole transferred slice; here, each tranche's spread is set against that tranche's own "
           "expected loss. Both use the same baseline and the same loss engine.",
           "- **What a multiple above 1 means** is the same as for 2013–2016: the premium over FHFA's baseline loss, "
           "mixing risk aversion with any belief that losses will exceed the baseline. Below 1, the spread is less "
           "than the baseline loss on the tranche, which the baseline (a 2016 scenario) may overstate for later "
           "pools. The expected loss per dollar of tranche also assumes the tranche runs down with the pool.",
           "- **Issuance only.** These are new-issue spreads. Secondary-market spreads are paywalled (`sources.md`).",
           "- **Reference-pool size is not used** (Eleonora's b2-upb (a)): the measure is per tranche, and tranche "
           "thickness comes from the printed credit enhancement, so no deal cost in dollars or in bps of the "
           "reference pool is given.")
    return s.lines, s.rows
