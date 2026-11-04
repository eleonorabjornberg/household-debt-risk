#!/usr/bin/env python3
"""PLAN task B2: price of the credit risk Fannie Mae and Freddie Mac transfer through CAS and STACR, per unit of
baseline expected loss, 2013-2016, tied to A2's CRT risk in force.

    uv run --project pipeline python research/b2_crt_pricing/b2.py

Method fixed in METHOD.md before this script was written. Input: fixtures/fhfa_dec2016_tables.txt, verbatim lines of
the text layer of FHFA's CRT Progress Report, December 2016 (sources.md); research/a2_net_exposure/crt_fhfa.csv.
Outputs next to this file: deals.csv (one row per deal, transcribed values and derived EL and multiple),
by_year.csv, results.json.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = HERE / "fixtures" / "fhfa_dec2016_tables.txt"
A2_CRT = ROOT / "research" / "a2_net_exposure" / "crt_fhfa.csv"

# FHFA's baseline scenario (Dec 2016 report, credit-cost footnote)
CPR, CDR, LGD, HORIZON_M = 0.10, 0.002, 0.25, 120

EXPECTED_ROWS = {"cas_deals": 25, "stacr_deals": 25, "cas_cost": 25, "stacr_cost": 23}


# ------------------------------------------------------------------ parsing
def sections(text: str) -> dict[str, list[str]]:
    out, cur = {}, None
    names = {"## CAS deals": "cas_deals", "## STACR deals": "stacr_deals",
             "## CAS credit cost": "cas_cost", "## STACR credit cost": "stacr_cost"}
    for line in text.splitlines():
        hit = next((v for k, v in names.items() if line.startswith(k)), None)
        if hit:
            cur = hit
            out[cur] = []
        elif cur and line.strip() and not line.startswith("#"):
            out[cur].append(line)
    return out


NUM = r"[\d,]+"
DEAL_RE = re.compile(rf"^\s*(CAS|STACR)\s+(\S+(?: \(\d\))?)?\s+(\d\d/\d\d/\d\d)\s+({NUM}|n/a\d?)\s+(\d+)\s*/\s*(\d+)\s+({NUM})\s+({NUM})")
COST_RE = re.compile(r"^\s*(20\d\d-[A-Z0-9]+(?: \(\d\))?)\s+(\d\d/\d\d/\d\d)\s+(\d+)\s*/\s*(\d+)\s+(\d+)?\s+(\d+|NA)\s+(\d+|NA)\s*$")


def _n(x: str):
    return None if x is None or x.startswith("n/a") or x == "NA" else float(x.replace(",", ""))


def parse(text: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    sec = sections(text)
    for k, n in EXPECTED_ROWS.items():
        assert len(sec.get(k, [])) == n, (k, len(sec.get(k, [])), n)
    deals = []
    for k in ["cas_deals", "stacr_deals"]:
        for line in sec[k]:
            m = DEAL_RE.match(line)
            assert m, ("deal row not parsed", line)
            prog, name, date, upb, a, d, sold, col8 = m.groups()
            # Column after "sold": Fannie's table = retained portion; Freddie's table = insured via ACIS
            # (Freddie's retained portion is a further column, not parsed). Rendered pages 6 and 9 checked.
            deals.append({"program": prog, "name_deal_table": name, "date_deal_table": date, "ref_upb_musd": _n(upb),
                          "attach_bp": int(a), "detach_bp": int(d), "sold_musd": _n(sold),
                          "cas_retained_musd": _n(col8) if prog == "CAS" else None,
                          "stacr_acis_insured_musd": _n(col8) if prog == "STACR" else None})
    costs = []
    for k, prog in [("cas_cost", "CAS"), ("stacr_cost", "STACR")]:
        for line in sec[k]:
            m = COST_RE.match(line)
            assert m, ("cost row not parsed", line)
            name, date, a, d, cost, gfee, avg = m.groups()
            costs.append({"program": prog, "name": name, "date_cost_table": date, "attach_bp": int(a), "detach_bp": int(d),
                          "credit_cost_bp": _n(cost), "est_gfee_bp": _n(gfee), "avg_gfee_bp": _n(avg)})
    return pd.DataFrame(deals), pd.DataFrame(costs)


def join(deals: pd.DataFrame, costs: pd.DataFrame) -> pd.DataFrame:
    """Match each cost row to its deal row: by name where the deal table prints it, else by program, attach/detach
    and position (FHFA's deal tables print no name for two rows: CAS 2016-3 (1) and STACR 2016-HQA4)."""
    rows, used = [], set()
    for _, c in costs.iterrows():
        cand = deals[(deals.program == c.program) & (deals.name_deal_table == c["name"])]
        if cand.empty:
            cand = deals[(deals.program == c.program) & deals.name_deal_table.isna()
                         & (deals.attach_bp == c.attach_bp) & (deals.detach_bp == c.detach_bp)]
        cand = cand[~cand.index.isin(used)]
        assert len(cand) == 1, ("ambiguous or missing deal match", c["name"], len(cand))
        i = cand.index[0]
        used.add(i)
        d = deals.loc[i]
        assert (d.attach_bp, d.detach_bp) == (c.attach_bp, c.detach_bp), ("attach/detach disagree", c["name"])
        rows.append({**c.to_dict(), **{k: d[k] for k in ["date_deal_table", "ref_upb_musd", "sold_musd", "cas_retained_musd", "stacr_acis_insured_musd"]}})
    out = pd.DataFrame(rows)
    out["date"] = pd.to_datetime(out["date_deal_table"], format="%m/%d/%y")
    out["date_tables_disagree"] = out["date_deal_table"] != out["date_cost_table"]
    out["year"] = out["date"].dt.year
    return out


# ------------------------------------------------------------------ expected loss engine
def pool_path(cpr=CPR, cdr=CDR, lgd=LGD, months=HORIZON_M):
    """Monthly pool balance (share of original UPB, start of month) and cumulative loss (share of original UPB)."""
    smm_p = 1 - (1 - cpr) ** (1 / 12)
    smm_d = 1 - (1 - cdr) ** (1 / 12)
    bal, cum, bals, cums = 1.0, 0.0, [], []
    for _ in range(months):
        bals.append(bal)
        default = bal * smm_d
        cum += default * lgd
        bal = bal - default - (bal - default) * smm_p
        cums.append(cum)
    return bals, cums


def tranche_el_bp(attach_bp: float, detach_bp: float, **kw) -> float:
    """Baseline expected loss of the slice, bps per year of reference UPB (METHOD.md item 2)."""
    bals, cums = pool_path(**kw)
    a, d = attach_bp / 1e4, detach_bp / 1e4
    slice_loss = min(max(cums[-1] - a, 0.0), d - a)
    years = len(bals) / 12
    avg_bal = sum(bals) / len(bals)
    return 1e4 * slice_loss / (avg_bal * years)


def main() -> int:
    deals, costs = parse(FIXTURE.read_text())
    df = join(deals, costs)
    # Checks (METHOD.md)
    assert (df.attach_bp < df.detach_bp).all()
    c = df.credit_cost_bp.dropna()
    assert ((c > 0) & (c < 100)).all()
    for prog, g in df.groupby("program"):
        assert g["date"].is_monotonic_increasing or g["date"].diff().dropna().min() >= pd.Timedelta(days=-31), prog
    df["el_bp"] = [tranche_el_bp(a, d) for a, d in zip(df.attach_bp, df.detach_bp)]
    df["multiple"] = [cc / el if (el > 0 and cc == cc and cc is not None) else math.nan
                      for cc, el in zip(df.credit_cost_bp, df.el_bp)]
    df["annual_cost_musd"] = df.credit_cost_bp / 1e4 * df.ref_upb_musd
    cols = ["program", "name", "date", "year", "date_deal_table", "date_cost_table", "date_tables_disagree", "ref_upb_musd",
            "attach_bp", "detach_bp", "sold_musd", "cas_retained_musd", "stacr_acis_insured_musd", "credit_cost_bp", "est_gfee_bp", "avg_gfee_bp",
            "el_bp", "multiple", "annual_cost_musd"]
    df[cols].to_csv(HERE / "deals.csv", index=False, float_format="%.6g")

    by = df.groupby("year").agg(n_deals=("name", "size"), n_priced=("credit_cost_bp", "count"),
                                ref_upb_priced_musd=("ref_upb_musd", lambda s: s[df.loc[s.index, "credit_cost_bp"].notna()].sum()),
                                annual_cost_musd=("annual_cost_musd", "sum"),
                                sold_priced_musd=("sold_musd", lambda s: s[df.loc[s.index, "credit_cost_bp"].notna()].sum()))
    by["upb_weighted_cost_bp"] = 1e4 * by.annual_cost_musd / by.ref_upb_priced_musd
    # Premium per dollar of protection sold, % per year. FHFA's cost assumes 100% of notes sold, so dividing by
    # the bonds actually sold overstates the rate where the Enterprise retained part of a tranche (METHOD.md).
    by["cost_per_sold_pct"] = 100 * by.annual_cost_musd / by.sold_priced_musd
    a2 = pd.read_csv(A2_CRT).set_index("year")
    by = by.join(a2[["annual_ref_upb_musd", "annual_rif_musd"]], how="left")
    # Priced deals cover part of each year's CRT (CIRT/ACIS insurance, unpriced and seasoned deals excluded):
    by["priced_share_of_crt_upb"] = by.ref_upb_priced_musd / by.annual_ref_upb_musd
    by.to_csv(HERE / "by_year.csv", float_format="%.6g")

    zero_attach = df[df.attach_bp == 0]
    pos = df[df.attach_bp > 0]
    bals, cums = pool_path()
    res = {
        "source": "FHFA CRT Progress Report, December 2016 (fixtures/fhfa_dec2016_tables.txt); A2 crt_fhfa.csv",
        "baseline": {"CPR": CPR, "CDR": CDR, "LGD": LGD, "horizon_months": HORIZON_M,
                     "cum_pool_loss_bp_at_120m": 1e4 * cums[-1], "el_full_pool_bp_per_year": tranche_el_bp(0, 10000)},
        "n_deals_priced": int(df.credit_cost_bp.notna().sum()),
        "n_deals_with_el": int((df.el_bp > 0).sum()),
        "n_dates_disagree": int(df.date_tables_disagree.sum()),
        "credit_cost_bp": {"zero_attach_median": float(zero_attach.credit_cost_bp.median()),
                           "positive_attach_median": float(pos.credit_cost_bp.median())},
        "multiple": {"zero_attach_median": float(zero_attach.multiple.median()),
                     "zero_attach_min": float(zero_attach.multiple.min()),
                     "zero_attach_max": float(zero_attach.multiple.max()),
                     "n_zero_attach": int(zero_attach.multiple.notna().sum()),
                     "n_positive_attach_absent": int(pos.multiple.isna().sum())},
        "gfee_bp": {"est_median_zero_attach": float(zero_attach.est_gfee_bp.median())},
        "cost_share_of_est_gfee_median": float((zero_attach.credit_cost_bp / zero_attach.est_gfee_bp).median()),
        "cost_per_sold_pct_range": [float(by.cost_per_sold_pct.min()), float(by.cost_per_sold_pct.max())],
        "by_year": {int(y): {k: (None if pd.isna(v) else float(v)) for k, v in r.items()} for y, r in by.iterrows()},
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: res[k] for k in ["baseline", "n_deals_priced", "n_deals_with_el", "credit_cost_bp", "multiple",
                                         "cost_share_of_est_gfee_median"]}, indent=1))
    print(by.round(3).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
