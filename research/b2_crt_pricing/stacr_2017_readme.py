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
           "> **Claude draft, not the author's text.** Built to Eleonora's choices of 2026-11-05: on cards b2-1723 "
           "(15:55 UTC) measure (ii), tranches (b), indicative (b) and LIBOR→SOFR (b); on cards b2-sofr-src (a), "
           "b2-upb (a) and b2-empty (a) (18:54 UTC). Method: `METHOD.md`, \"STACR 2017+\". Code: `stacr_2017.py`; "
           "data: `stacr_2017_tranches.csv`, `stacr_2017_by_year_class.csv`.", "")
    s.add(f"Freddie Mac's STACR pricing workbook prints, for each deal, every sold tranche's spread at issuance and its "
          f"credit enhancement. From 2017 it covers {R['deals']} deals and {R['tranches']} tranches. "
          f"{R['tranches_her_classes']} are in her three classes (M-1, including M-1A and M-1B; M-2; B, including "
          f"B-1 and B-2); the other {R['tranches_outside_classes']} ({oc['A-1']} A-1, {oc['M-3']} M-3) are kept in the "
          "tranche file but not summarised. Fannie Mae's CAS deals are not covered: its host is not reachable "
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
          "adjustment is a fixed fallback spread, not the LIBOR–SOFR gap on each deal's pricing date.",
          [num("libor_adj", f"LIBOR-to-SOFR adjustment for one-month LIBOR: {adj} bps (Regulation ZZ).", f"{adj} bps",
               adj, "bp", "n/a", "LIBOR_1M_ADJ_BP", "UNVERIFIED",
               "Source constant: Federal Reserve Regulation ZZ final rule, 12 CFR part 253 section 4(c)(2), quoted in sources.md.",
               "Federal Reserve Board, Regulation ZZ final rule (2022-12-16)")])
    s.add(f"- **Multiple.** Spread ÷ the tranche's expected loss per dollar of tranche under FHFA's December 2016 "
          f"baseline (10% prepayment, 0.2% annual defaults, 25% loss given default, redemption at 10 years), on the "
          f"average outstanding balance. Applying that 2016 baseline to later deals is an assumption. The baseline "
          f"pool loses {f1(cum)} bps of its original balance over ten years, so only a tranche attaching below "
          f"{f1(cum)} bps has an expected loss and a multiple.",
          [num("cum_loss", f"Baseline cumulative pool loss, ten years: {f1(cum)} bps of original balance.",
               f"{f1(cum)} bps", cum, "bp", "n/a", "stacr_2017_results.json baseline.cum_loss_bp_of_original",
               "ESTIMATE", "Model output under FHFA's 2016 baseline scenario.")])
    s.add(f"- **\"(Indicative)\" tranches.** {R['retained_indicative']} tranches in 2017–2018 were retained by Freddie "
          "and carry an indicative spread, not a sale price. They are kept and flagged (`retained_indicative`).",
          [num("indicative", f"Retained tranches with an indicative spread, 2017+: {R['retained_indicative']}.",
               str(R["retained_indicative"]), R["retained_indicative"], "count", "2017-2018",
               "stacr_2017_results.json retained_indicative")])
    s.text("", "**By year and class** (spreads over SOFR in bps, median with range; multiples for B tranches that "
           "have one, median):", "",
           "| Year | M-1: tranches | M-1 spread | M-2: tranches | M-2 spread | B: tranches (indicative) | B spread "
           "(range) | B with a multiple | Multiple, outstanding basis | Multiple, original basis |",
           "|---|---|---|---|---|---|---|---|---|---|")
    for y in sorted(YC["year"].unique()):
        g = YC[YC["year"] == y].set_index("cls")
        cells, nums = [str(y)], []
        for c in ("M-1", "M-2", "B"):
            if c not in g.index:
                cells += ["—", "—"] if c != "B" else ["—", "—", "—", "—", "—"]
                continue
            r = g.loc[c]
            k = c.lower().replace("-", "")
            nt = int(r["tranches"])
            ind = int(r["retained_indicative"])
            tcell = f"{nt}" + (f" ({ind})" if c == "B" and ind else "")
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
            mcell = [str(wm), "—", "—"]
            nums.append(num(f"{y}_b_with_multiple", f"{y}, class B: {wm} tranches with a multiple.", str(wm), wm,
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
          f"point (2019-FTR1, -FTR3 and -FTR4 list only B-2 and the senior class), and {cb['no_spread']} has no spread "
          f"printed. M-1, M-2 and B-1 never get a multiple; for them the measure is the spread alone. From "
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
           num("first_year_none", f"First year from which no sold STACR tranche has a multiple: "
               f"{R['first_year_no_multiple']}.", str(R["first_year_no_multiple"]), R["first_year_no_multiple"],
               "year", f"{R['first_year_no_multiple']}-{YC['year'].max()}", "stacr_2017_results.json first_year_no_multiple")])
    s.text("- **The multiple moves with where B-2 attaches.** Freddie moved B-2's attachment point up over these years. "
           "A B-2 that attaches higher takes less of the baseline loss, so the same spread gives a higher multiple. "
           "Much of the rise in the yearly median multiple comes from that, not from a change in price:", "",
           "| B-2 attaches at | Tranches | Years | Baseline loss taken (bps of original balance) | Multiple, median (range) |",
           "|---|---|---|---|---|")
    for b in ba:
        a = f0(b["attach_bp"])
        k = f"attach{a}"
        med, lo, hi = (f1(b[f"multiple_sofr_out_{x}"]) for x in ("median", "min", "max"))
        nums = [num(f"{k}_n", f"B-2 tranches attaching at {a} bps with a multiple: {b['tranches']}.", str(b["tranches"]),
                    b["tranches"], "count", b["years"].replace("–", "-"), f"stacr_2017_results.json by_attach[{a}].tranches"),
                num(f"{k}_loss", f"Baseline loss taken by a slice attaching at {a} bps: {f1(b['slice_loss_bp'])} bps.",
                    f1(b["slice_loss_bp"]), b["slice_loss_bp"], "bp", "n/a",
                    f"stacr_2017_results.json by_attach[{a}].slice_loss_bp", "ESTIMATE")]
        for x, d in (("median", med), ("min", lo), ("max", hi)):
            nums.append(num(f"{k}_multiple_{x}", f"B-2 attaching at {a} bps: {x} multiple (outstanding basis) {d}.", d,
                            b[f"multiple_sofr_out_{x}"], "ratio", b["years"], f"stacr_2017_results.json "
                            f"by_attach[{a}].multiple_sofr_out_{x}", "ESTIMATE"))
        s.add(f"| {a} bps | {b['tranches']} | {b['years'].replace('-', '–')} | {f1(b['slice_loss_bp'])} | {med} ({lo}–{hi}) |",
              nums)
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
