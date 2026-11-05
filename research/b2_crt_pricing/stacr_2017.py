#!/usr/bin/env python3
"""B2 STACR 2017+: issuance spread and an FHFA-style multiple (spread / baseline expected loss), by tranche class.

    uv run --project pipeline python research/b2_crt_pricing/stacr_2017.py

Eleonora's choices of 2026-11-05 15:55 UTC (PLAN.md "Decisions taken", cards b2-1723-*): measure (ii) spread plus an
FHFA-style multiple under FHFA's 2016 baseline, a labelled assumption for the later deals; tranches (b) each
seniority class (M-1, M-2, B) separately; "(Indicative)" retained tranches (b) kept and flagged; LIBOR -> SOFR (b)
add a published LIBOR-SOFR spread adjustment to the pre-SOFR deals. Method: METHOD.md, "STACR 2017+".

Input: stacr_tranches.csv (from stacr_pricing.py; Freddie Mac's STACR pricing workbook). The loss engine is b2.py's
(FHFA's December 2016 baseline: CPR 10%, CDR 0.2%, LGD 25%, redemption at month 120).
Outputs next to this file: stacr_2017_tranches.csv, stacr_2017_by_year_class.csv, stacr_2017_results.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IN = HERE / "stacr_tranches.csv"
OUT_TR = HERE / "stacr_2017_tranches.csv"
OUT_YC = HERE / "stacr_2017_by_year_class.csv"
OUT_JS = HERE / "stacr_2017_results.json"

_spec = importlib.util.spec_from_file_location("b2", HERE / "b2.py")
b2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b2)

START = "2017-01-01"

# LIBOR -> SOFR tenor spread adjustment for one-month LIBOR, bps, added to the spread of 1M LIBOR deals so that
# every spread is over SOFR. Federal Reserve, Regulation ZZ final rule, 12 CFR 253.4(c)(2): "0.11448 percent for
# one-month LIBOR" (sources.md). Source approved by Eleonora, card b2-sofr-src (a), 2026-11-05 18:54 UTC.
LIBOR_1M_ADJ_BP: float | None = 11.448

# Her three seniority classes (b). Tranche names are matched without hyphens (the workbook prints both).
CLASS = {"M1": "M-1", "M1A": "M-1", "M1B": "M-1", "M2": "M-2", "B": "B", "B1": "B", "B2": "B"}
OUTSIDE = {"A1": "A-1", "M3": "M-3"}          # sold classes outside her three; kept in the tranche file, not summarised


def program(deal: str) -> str:
    return deal.split("-", 1)[1].rstrip("0123456789")


def frame(df: pd.DataFrame, adj_bp: float | None = LIBOR_1M_ADJ_BP) -> pd.DataFrame:
    t = df[df["closing_date"] >= START].copy()
    key = t["tranche"].str.replace("-", "", regex=False)
    bad = sorted(set(key) - set(CLASS) - set(OUTSIDE))
    if bad:
        raise ValueError(f"tranche names with no class: {bad}")
    t["year"] = t["closing_date"].str[:4].astype(int)
    t["program"] = t["deal"].map(program)
    t["cls"] = key.map(CLASS).fillna(key.map(OUTSIDE))
    t["in_her_classes"] = key.isin(list(CLASS))
    t["sub_tranche"] = key.map(lambda k: {"M1A": "M-1A", "M1B": "M-1B", "B1": "B-1", "B2": "B-2"}.get(k, ""))
    t["retained_indicative"] = t["spread_indicative"].astype(bool)
    if not set(t["benchmark"]) <= {"1M LIBOR", "SOFR"}:
        raise ValueError(f"unexpected benchmark: {set(t['benchmark'])}")

    t["spread_bp"] = t["spread"] * 1e4
    t["libor_adj_bp"] = adj_bp if adj_bp is not None else float("nan")
    t.loc[t["benchmark"] == "SOFR", "libor_adj_bp"] = 0.0
    t["spread_sofr_bp"] = t["spread_bp"] + t["libor_adj_bp"]

    t["attach_bp"] = t["initial_ce"] * 1e4
    t["detach_bp"] = t["detach"] * 1e4
    # A B or M-2 class sitting directly under A-H means retained mezzanine classes are missing from the list
    # (2019-FTR1/3/4 sell only B-2): its detachment point is not known from the workbook.
    unverified = (t["detach_from"] == "AH") & t["cls"].isin(["B", "M-2"])
    t["detach_known"] = t["detach_bp"].notna() & t["attach_bp"].notna() & ~unverified

    cum_bp = 1e4 * b2.pool_path()[1][-1]
    rows = []
    for r in t.itertuples():
        el_o = el_g = el_tr_o = el_tr_g = float("nan")
        why = ""
        if not r.detach_known:
            why = "no detachment point" if pd.isna(r.detach_bp) or pd.isna(r.attach_bp) else "detachment point not known: unlisted retained classes above"
        else:
            el_o = b2.tranche_el_bp(r.attach_bp, r.detach_bp, basis="outstanding")
            el_g = b2.tranche_el_bp(r.attach_bp, r.detach_bp, basis="original")
            thick = (r.detach_bp - r.attach_bp) / 1e4
            el_tr_o, el_tr_g = el_o / thick, el_g / thick          # bps a year per dollar of tranche
            if el_o == 0:
                why = f"absent: attaches at or above the baseline cumulative loss ({cum_bp:.1f} bps)"
        rows.append((el_o, el_g, el_tr_o, el_tr_g, why))
    el_cols = ["el_pool_out_bp", "el_pool_orig_bp", "el_tranche_out_bp", "el_tranche_orig_bp"]
    t[el_cols + ["multiple_note"]] = rows
    t[el_cols] = t[el_cols].astype(float)
    pos = t["el_tranche_out_bp"] > 0
    for basis in ("out", "orig"):
        t[f"multiple_{basis}"] = (t["spread_bp"] / t[f"el_tranche_{basis}_bp"]).where(pos)
        t[f"multiple_sofr_{basis}"] = (t["spread_sofr_bp"] / t[f"el_tranche_{basis}_bp"]).where(pos)
    # no spread takes precedence over "absent" (skeptic mkt-s49: 2017-HRP1 prints a par/discount/IO split)
    t.loc[t["spread_bp"].isna() & ~t["multiple_note"].str.startswith("detachment"), "multiple_note"] = "no spread printed"
    return t


def by_year_class(t: pd.DataFrame) -> pd.DataFrame:
    h = t[t["in_her_classes"] & t["spread_bp"].notna()]
    out = []
    for (y, c), g in h.groupby(["year", "cls"]):
        m = g["multiple_out"].dropna()
        out.append({"year": y, "cls": c, "tranches": len(g), "deals": g["deal"].nunique(),
                    "retained_indicative": int(g["retained_indicative"].sum()),
                    "libor_tranches": int((g["benchmark"] == "1M LIBOR").sum()),
                    "spread_bp_median": g["spread_bp"].median(), "spread_bp_min": g["spread_bp"].min(),
                    "spread_bp_max": g["spread_bp"].max(),
                    "spread_sofr_bp_median": g["spread_sofr_bp"].median(),
                    "with_multiple": len(m), "with_multiple_indicative": int(g.loc[g["multiple_out"].notna(), "retained_indicative"].sum()), "multiple_out_median": m.median() if len(m) else float("nan"),
                    "multiple_orig_median": g["multiple_orig"].dropna().median() if len(m) else float("nan"),
                    "multiple_sofr_out_median": g["multiple_sofr_out"].dropna().median() if len(m) else float("nan"),
                    "multiple_sofr_orig_median": g["multiple_sofr_orig"].dropna().median() if len(m) else float("nan"),
                    "spread_sofr_bp_min": g["spread_sofr_bp"].min(), "spread_sofr_bp_max": g["spread_sofr_bp"].max()})
    return pd.DataFrame(out)


def main() -> int:
    t = frame(pd.read_csv(IN))
    yc = by_year_class(t)
    cols = ["deal", "closing_date", "year", "program", "benchmark", "tranche", "cls", "sub_tranche", "in_her_classes",
            "issued_usd", "issued_note", "retained_indicative", "spread_bp", "libor_adj_bp", "spread_sofr_bp",
            "attach_bp", "detach_bp", "detach_from", "detach_known", "el_pool_out_bp", "el_pool_orig_bp",
            "el_tranche_out_bp", "el_tranche_orig_bp", "multiple_out", "multiple_orig", "multiple_sofr_out",
            "multiple_sofr_orig", "multiple_note"]
    t[cols].to_csv(OUT_TR, index=False, float_format="%.6g")
    yc.to_csv(OUT_YC, index=False, float_format="%.6g")

    h = t[t["in_her_classes"]]
    mult = h["multiple_out"].dropna()
    res = {
        "source": "stacr_tranches.csv (Freddie Mac STACR pricing workbook, sha256 e10971eb...; sources.md)",
        "scope": f"STACR deals closing on or after {START}",
        "baseline": {"CPR": b2.CPR, "CDR": b2.CDR, "LGD": b2.LGD, "horizon_months": b2.HORIZON_M,
                     "cum_loss_bp_of_original": round(1e4 * b2.pool_path()[1][-1], 3),
                     "label": "FHFA's December 2016 baseline, applied to 2017+ deals as an assumption"},
        "libor_1m_adj_bp": LIBOR_1M_ADJ_BP,
        "libor_adj_status": "set" if LIBOR_1M_ADJ_BP is not None else "pending: source held as a proposed card",
        "deals": int(t["deal"].nunique()), "tranches": int(len(t)),
        "tranches_her_classes": int(len(h)), "tranches_outside_classes": int((~t["in_her_classes"]).sum()),
        "tranches_no_spread": int(h["spread_bp"].isna().sum()),
        "retained_indicative": int(h["retained_indicative"].sum()),
        "with_multiple": int(len(mult)),
        "with_multiple_by_class": {c: int(h.loc[h["cls"] == c, "multiple_out"].notna().sum()) for c in ("M-1", "M-2", "B")},
        "detach_unknown": sorted(h.loc[~h["detach_known"], "deal"].unique().tolist()),
        "multiple_out_median": round(float(mult.median()), 3) if len(mult) else None,
        "count_breakdown_her_classes": {
            "with_multiple": int(h["multiple_out"].notna().sum()),
            "attach_at_or_above_baseline_loss": int(h["multiple_note"].str.startswith("absent").sum()),
            "detach_unknown": int(h["multiple_note"].str.startswith("detachment").sum()),
            "no_spread": int((h["multiple_note"] == "no spread printed").sum())},
        "outside_classes": {c: int((t["cls"] == c).sum()) for c in sorted(OUTSIDE.values())},
        "first_year_no_multiple": int(min(y for y in h["year"].unique() if h.loc[h["year"] >= y, "multiple_out"].isna().all())),
        "fixed_slice_25_75": {str(y): round(float(g["multiple_sofr_out"].median()), 3) for y, g in
                              h[h["multiple_out"].notna() & (h["attach_bp"] == 25) & (h["detach_bp"] == 75)].groupby("year")},
        "fixed_slice_25_75_n": {str(y): int(len(g)) for y, g in
                                h[h["multiple_out"].notna() & (h["attach_bp"] == 25) & (h["detach_bp"] == 75)].groupby("year")},
        "by_attach": [{"attach_bp": float(a), "detach_bp_slice": float(dd), "tranches": int(len(g)),
                       "indicative": int(g["retained_indicative"].sum()), "years": f"{g['year'].min()}-{g['year'].max()}",
                       # every detach here lies above the baseline loss, so the slice takes (cum - attach)
                       "slice_loss_bp": round(1e4 * b2.pool_path()[1][-1] - a, 3) if g["detach_bp"].min() > 1e4 * b2.pool_path()[1][-1] else None,
                       "detach_bp": sorted(g["detach_bp"].unique().tolist()),
                       "multiple_sofr_out_median": round(float(g["multiple_sofr_out"].median()), 3),
                       "multiple_sofr_out_min": round(float(g["multiple_sofr_out"].min()), 3),
                       "multiple_sofr_out_max": round(float(g["multiple_sofr_out"].max()), 3)}
                      for (a, dd), g in h[h["multiple_out"].notna()].groupby(["attach_bp", "detach_bp"])],
        "multiple_orig_median": round(float(h["multiple_orig"].dropna().median()), 3) if len(mult) else None,
    }
    OUT_JS.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: res[k] for k in ("deals", "tranches", "tranches_her_classes", "with_multiple",
                                          "with_multiple_by_class", "libor_adj_status")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
