"""raw observations -> core.* and mart.* tables (pandas, in memory).

METHODOLOGY
-----------
* core.fact_quarterly keeps the latest vintage per (series_id, date). Z.1 and NY Fed are already
  quarterly (quarter-end dates). FRED: monthly series (CPI, DSPI, UNRATE, Case-Shiller) are averaged
  over the months available once the quarter's last month is published (2025Q4 CPI has no October 2025
  observation - BLS skipped it during the shutdown); weekly WSHOMCB takes the last observation in the quarter,
  kept only once the quarter is over (an observation within 7 days of quarter end).
* Mart tables start at the first quarter of the continuous quarterly Z.1 record (1952Q1; before that
  Z.1 is annual-only) and end at the last quarter with the scope total.
* Scope total = FL154104015 (= FL153165105 mortgages + FL153166000 consumer credit, exactly).
* Mortgage holders are reported for all 1-4 family mortgages (FL893065105); each holder is
  apportioned to households: holder / FL893065105 * FL153165105. Consumer credit holders sum to
  FL153166000 and are used as-is.
* Real dollars: nominal * CPI(latest complete CPI quarter) / CPI(quarter); CPI = quarterly mean of
  CPIAUCSL (null before 1947). pct_of_dpi = musd / (DSPI quarterly mean SAAR $B * 1000); null pre-1959.
* Collateral classes: home_backed = FL153165105 (collateral FL155035015 owner-occupied real estate);
  vehicle_backed = FL153166400 auto loans (collateral FL155111005 ALL consumer durables - a generous
  proxy that overstates vehicle collateral, so vehicle coverage ratios are an upper bound);
  uncollateralized = revolving FL153166100 + student FL153166220; other_nonrevolving = FL153166205.
  The four type series sum to FL153166000 exactly in every quarter, but the split is incomplete early:
  auto and other non-revolving from 1945, revolving from 1968Q1 (zero before: G.19 starts revolving
  credit in 1968), student loans only from 2006Q1 - before then they are inside other non-revolving.
  STUDENT-LOAN IMPUTATION before the first quarter with FL153166220 > 0 (2006Q1):
     share(t) = s0 * clip((t - 1965Q4) / (t_first - 1965Q4), 0, 1)       [linear ramp in quarters]
     s0       = student / (student + other non-revolving) in the first reported quarter (~0.67)
     student_est(t) = min(max(share(t) * O(t), floor(t)), O(t))
     floor(t) = federal (FL313066220) + Sallie Mae GSE (FL403066005) + nonprofit (FL163066223)
                student-loan holdings, which are student loans by definition
  where O = reported other non-revolving (incl. student). 1965Q4 = Higher Education Act (federal
  guaranteed student loans start). student_est moves from other_nonrevolving to uncollateralized;
  totals are unchanged. Those rows get is_estimated = true (both classes, every quarter before 2006Q1).
* crisis_event_window: t0 = crisis start_q; offsets -8..+16 where data exist;
  delta_from_t0 = value - value_at_t0 in the metric's own units (shares are 0-1, so 0.05 = 5 pp).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import config
from .extract import read_staging

log = logging.getLogger(__name__)

SCOPE = "FL154104015"
MORT = "FL153165105"
CC = "FL153166000"
MORT_ALL_HOLDERS = "FL893065105"
REVOLVING, STUDENT, AUTO, OTHER_NR = "FL153166100", "FL153166220", "FL153166400", "FL153166205"
HOME_VALUE, DURABLES = "FL155035015", "FL155111005"
STUDENT_FLOOR = ["FL313066220", "FL403066005", "FL163066223"]
HEA_QUARTER = pd.Timestamp("1965-12-31")

FRED_UNITS = {
    "WSHOMCB": "USD millions", "CPIAUCSL": "index 1982-84=100", "DSPI": "USD billions SAAR",
    "UNRATE": "percent", "CSUSHPINSA": "index Jan 2000=100",
}
FRED_LAST_IN_QUARTER = {"WSHOMCB"}

# Column order of every output table = DB column order (minus defaults like loaded_at).
COLUMNS = {
    "core.dim_series": ["series_id", "source", "role", "description", "debt_type", "risk_bucket", "collateral_class", "unit"],
    "core.dim_risk_bucket": ["risk_bucket", "label", "is_public", "sort_order"],
    "core.dim_crisis": ["crisis_id", "name", "kind", "start_q", "end_q", "notes"],
    "core.fact_quarterly": ["series_id", "date", "value", "vintage"],
    "mart.debt_by_risk_holder": ["date", "risk_bucket", "debt_type", "nominal_musd", "real_musd", "share_of_total", "pct_of_dpi"],
    "mart.public_share": ["date", "scope_total_musd", "public_musd", "public_share", "public_share_mortgage",
                          "public_share_cc", "fed_mbs_musd", "fed_mbs_share_of_scope"],
    "mart.collateral_coverage": ["date", "collateral_class", "debt_musd", "collateral_value_musd", "coverage_ratio",
                                 "share_of_debt", "is_estimated"],
    "mart.crisis_event_window": ["crisis_id", "metric", "q_offset", "date", "value", "value_at_t0", "delta_from_t0"],
    "mart.nyfed_by_type": ["date", "loan_type", "balance_busd", "transition_serious_pct"],
}
PRIMARY_KEYS = {
    "core.dim_series": ["series_id"], "core.dim_risk_bucket": ["risk_bucket"], "core.dim_crisis": ["crisis_id"],
    "core.fact_quarterly": ["series_id", "date"],
    "mart.debt_by_risk_holder": ["date", "risk_bucket", "debt_type"], "mart.public_share": ["date"],
    "mart.collateral_coverage": ["date", "collateral_class"],
    "mart.crisis_event_window": ["crisis_id", "metric", "q_offset"], "mart.nyfed_by_type": ["date", "loan_type"],
}
# Load order (parents first). Deletion runs in reverse.
TABLE_ORDER = list(COLUMNS)

MUSD_DP, RATIO_DP = 3, 10


def qend(label: str) -> pd.Timestamp:
    return pd.Period(label, "Q").end_time.normalize()


# ----------------------------------------------------------------------------- raw -> core
def load_raw(sources=("z1", "fred", "nyfed")) -> pd.DataFrame:
    frames = []
    for s in sources:
        try:
            frames.append(read_staging(s))
        except FileNotFoundError as e:
            if s == "nyfed":
                log.warning("%s (NY Fed table will be empty)", e)
                continue
            raise
    return pd.concat(frames, ignore_index=True)


def latest_vintage(raw: pd.DataFrame) -> pd.DataFrame:
    raw = raw.sort_values("vintage")
    return raw.drop_duplicates(["series_id", "date"], keep="last")


def quarterize_fred(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for sid, g in df.groupby("series_id"):
        g = g.sort_values("date")
        q = g["date"].dt.to_period("Q")
        if sid in FRED_LAST_IN_QUARTER:
            last = g.groupby(q).tail(1).copy()
            last["qdate"] = last["date"].dt.to_period("Q").dt.end_time.dt.normalize()
            last = last[(last["qdate"] - last["date"]).dt.days <= 6]   # quarter complete
            agg = last.assign(date=last["qdate"])[["series_id", "date", "value", "vintage"]]
        else:
            grp = g.groupby(q).agg(value=("value", "mean"), n=("value", "size"), vintage=("vintage", "max"))
            # quarter is complete once its last month is published; average what exists (BLS skipped
            # Oct-2025 CPI during the shutdown, so 2025Q4 is a 2-month mean)
            last_month = (grp.index.end_time.normalize() + pd.offsets.MonthBegin(-1))
            grp = grp[g["date"].max() >= last_month]
            agg = pd.DataFrame({"series_id": sid, "date": grp.index.end_time.normalize(),
                                "value": grp["value"].values, "vintage": grp["vintage"].values})
        out.append(agg)
    return pd.concat(out, ignore_index=True)


def build_fact_quarterly(raw: pd.DataFrame) -> pd.DataFrame:
    lv = latest_vintage(raw)
    fred = lv[lv.source == "fred"]
    other = lv[lv.source != "fred"][["series_id", "date", "value", "vintage"]]
    fact = pd.concat([other, quarterize_fred(fred)], ignore_index=True)
    return fact.sort_values(["series_id", "date"]).reset_index(drop=True)


def build_dim_series(fact: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for s in config.series():
        role = s["role"]
        debt_type = s.get("debt_type") or {
            "mortgage_holder": "mortgage", "cc_holder": "consumer_credit", "cc_type": "consumer_credit"}.get(role)
        unit = {"z1": "USD millions", "fred": FRED_UNITS.get(s["id"], "native"), "nyfed": "mixed (see child series)"}[s["source"]]
        rows.append(dict(series_id=s["id"], source=s["source"], role=role, description=s["desc"], debt_type=debt_type,
                         risk_bucket=s.get("risk_bucket"), collateral_class=s.get("collateral_class"), unit=unit))
    # NY Fed child series (one per metric x loan type) so fact_quarterly's FK holds.
    for sid in sorted(fact.loc[fact.series_id.str.startswith("NYFED_HHDC."), "series_id"].unique()):
        _, metric, lt = sid.split(".")
        bal = metric == "balance"
        rows.append(dict(series_id=sid, source="nyfed", role="nyfed",
                         description=f"NY Fed HHDC: {'balance' if bal else 'flow into serious delinquency (90+), % of balance, annualized'} - {lt}",
                         debt_type=None, risk_bucket=None, collateral_class=None,
                         unit="USD billions" if bal else "percent"))
    return pd.DataFrame(rows, columns=COLUMNS["core.dim_series"])


def build_dim_risk_bucket() -> pd.DataFrame:
    return pd.DataFrame([dict(risk_bucket=k, label=v["label"], is_public=bool(v["public"]), sort_order=i + 1)
                         for i, (k, v) in enumerate(config.risk_buckets().items())], columns=COLUMNS["core.dim_risk_bucket"])


def build_dim_crisis() -> pd.DataFrame:
    return pd.DataFrame([dict(crisis_id=c.crisis_id, name=c.name, kind=c.kind, start_q=qend(c.start_q),
                              end_q=qend(c.end_q) if c.end_q else pd.NaT, notes=c.notes) for c in config.CRISES],
                        columns=COLUMNS["core.dim_crisis"])


# ----------------------------------------------------------------------------- helpers
def wide(fact: pd.DataFrame) -> pd.DataFrame:
    return fact.pivot(index="date", columns="series_id", values="value").sort_index()


def mart_dates(w: pd.DataFrame) -> pd.DatetimeIndex:
    """Quarter-end dates from the start of the continuous quarterly Z.1 record to the last scope total."""
    d = w.index[w[SCOPE].notna()]
    gaps = pd.Series(d).diff().dt.days > 95
    start = d[gaps.values.nonzero()[0].max()] if gaps.any() else d[0]
    return d[d >= start]


def _deflators(w: pd.DataFrame, dates) -> tuple[pd.Series, pd.Series, pd.Timestamp]:
    cpi = w["CPIAUCSL"].dropna()
    base_date = cpi.index.max()
    real_factor = (cpi.loc[base_date] / cpi).reindex(dates)
    dpi_musd = (w["DSPI"] * 1000.0).reindex(dates)
    return real_factor, dpi_musd, base_date


# ----------------------------------------------------------------------------- marts
def holder_amounts(w: pd.DataFrame, dates) -> pd.DataFrame:
    """Long frame date x risk_bucket x debt_type -> nominal_musd (apportioned mortgages)."""
    w = w.reindex(dates)
    rows = []
    for role, debt_type in (("mortgage_holder", "mortgage"), ("cc_holder", "consumer_credit")):
        holders = config.series("z1", role)
        for bucket in config.risk_buckets():
            ids = [h["id"] for h in holders if h["risk_bucket"] == bucket]
            amt = w[ids].fillna(0).sum(axis=1) if ids else pd.Series(0.0, index=w.index)
            if debt_type == "mortgage":
                amt = amt / w[MORT_ALL_HOLDERS] * w[MORT]
            rows.append(pd.DataFrame({"date": w.index, "risk_bucket": bucket, "debt_type": debt_type, "nominal_musd": amt.values}))
    return pd.concat(rows, ignore_index=True)


def build_debt_by_risk_holder(w, dates) -> pd.DataFrame:
    df = holder_amounts(w, dates)
    real_factor, dpi_musd, _ = _deflators(w, dates)
    scope = w[SCOPE].reindex(dates)
    df["real_musd"] = df["nominal_musd"] * df["date"].map(real_factor)
    df["share_of_total"] = df["nominal_musd"] / df["date"].map(scope)
    df["pct_of_dpi"] = df["nominal_musd"] / df["date"].map(dpi_musd)
    return df[COLUMNS["mart.debt_by_risk_holder"]]


def build_public_share(holders: pd.DataFrame, w, dates) -> pd.DataFrame:
    pub = holders[holders.risk_bucket.isin(config.public_buckets())]
    p = pub.pivot_table(index="date", columns="debt_type", values="nominal_musd", aggfunc="sum").reindex(dates)
    scope = w[SCOPE].reindex(dates)
    out = pd.DataFrame(index=dates)
    out["scope_total_musd"] = scope
    out["public_musd"] = p["mortgage"] + p["consumer_credit"]
    out["public_share"] = out["public_musd"] / scope
    out["public_share_mortgage"] = p["mortgage"] / w[MORT].reindex(dates)
    out["public_share_cc"] = p["consumer_credit"] / w[CC].reindex(dates)
    mbs = w["WSHOMCB"].reindex(dates) if "WSHOMCB" in w else pd.Series(np.nan, index=dates)
    mbs = mbs.where(mbs > 0)   # WSHOMCB is 0 before QE1 (2009): null, per schema
    out["fed_mbs_musd"] = mbs
    out["fed_mbs_share_of_scope"] = mbs / scope
    return out.rename_axis("date").reset_index()[COLUMNS["mart.public_share"]]


def split_consumer_credit(w: pd.DataFrame, dates) -> pd.DataFrame:
    """Consumer credit type split with imputed student loans before they are reported (see module doc)."""
    w = w.reindex(dates)
    student, other = w[STUDENT].fillna(0), w[OTHER_NR].fillna(0)
    first = student[student > 0].index.min()
    pos = pd.Series(np.arange(len(dates)), index=dates)
    s0 = student[first] / (student[first] + other[first])
    ramp = ((pos - pos.get(HEA_QUARTER, 0)) / (pos[first] - pos.get(HEA_QUARTER, 0))).clip(0, 1)
    floor = w[STUDENT_FLOOR].fillna(0).sum(axis=1)
    est = np.minimum(np.maximum(s0 * ramp * other, floor), other)
    pre = dates < first
    student_adj = student.where(~pre, est)
    other_adj = other.where(~pre, other - est)
    return pd.DataFrame({"revolving": w[REVOLVING].fillna(0), "student": student_adj, "auto": w[AUTO].fillna(0),
                         "other_nonrevolving": other_adj, "is_estimated": pre, "student_first": first}, index=dates)


def build_collateral_coverage(w, dates) -> pd.DataFrame:
    sp = split_consumer_credit(w, dates)
    scope = w[SCOPE].reindex(dates)
    est = sp["is_estimated"]
    classes = {
        "home_backed": (w[MORT].reindex(dates), w[HOME_VALUE].reindex(dates), False),
        "vehicle_backed": (sp["auto"], w[DURABLES].reindex(dates), False),
        "uncollateralized": (sp["revolving"] + sp["student"], None, True),
        "other_nonrevolving": (sp["other_nonrevolving"], None, True),
    }
    rows = []
    for cls, (debt, coll, imputed) in classes.items():
        df = pd.DataFrame({"date": dates, "collateral_class": cls, "debt_musd": debt.values})
        df["collateral_value_musd"] = coll.values if coll is not None else np.nan
        df["coverage_ratio"] = (coll / debt.where(debt > 0)).values if coll is not None else np.nan
        df["share_of_debt"] = (debt / scope).values
        df["is_estimated"] = est.values if imputed else False
        rows.append(df)
    return pd.concat(rows, ignore_index=True)[COLUMNS["mart.collateral_coverage"]]


def metric_frame(debt: pd.DataFrame, pub: pd.DataFrame, coll: pd.DataFrame) -> pd.DataFrame:
    m = {"public_share": pub.set_index("date")["public_share"]}
    by_bucket = debt.groupby(["date", "risk_bucket"])["share_of_total"].sum().unstack()
    for b in config.risk_buckets():
        m[f"share:{b}"] = by_bucket[b]
    c = coll.set_index(["date", "collateral_class"])
    for cls in config.collateral_classes():
        m[f"share:{cls}"] = c.xs(cls, level="collateral_class")["share_of_debt"]
    for cls in ("home_backed", "vehicle_backed"):
        m[f"coverage:{cls}"] = c.xs(cls, level="collateral_class")["coverage_ratio"]
    return pd.DataFrame(m)


def build_crisis_event_window(metrics: pd.DataFrame, dim_crisis: pd.DataFrame) -> pd.DataFrame:
    idx = metrics.index
    pos = pd.Series(np.arange(len(idx)), index=idx)
    rows = []
    for c in dim_crisis.itertuples():
        t0 = pd.Timestamp(c.start_q)
        if t0 not in pos:
            continue
        p0 = pos[t0]
        for metric in metrics.columns:
            s = metrics[metric]
            v0 = s.iloc[p0]
            if pd.isna(v0):
                continue
            for k in range(config.WINDOW_MIN, config.WINDOW_MAX + 1):
                p = p0 + k
                if 0 <= p < len(idx) and pd.notna(s.iloc[p]):
                    rows.append((c.crisis_id, metric, k, idx[p], s.iloc[p], v0, s.iloc[p] - v0))
    return pd.DataFrame(rows, columns=COLUMNS["mart.crisis_event_window"])


def build_nyfed_by_type(fact: pd.DataFrame) -> pd.DataFrame:
    ny = fact[fact.series_id.str.startswith("NYFED_HHDC.")].copy()
    if ny.empty:
        return pd.DataFrame(columns=COLUMNS["mart.nyfed_by_type"])
    parts = ny.series_id.str.split(".", expand=True)
    ny["metric"], ny["loan_type"] = parts[1], parts[2]
    p = ny.pivot_table(index=["date", "loan_type"], columns="metric", values="value").reset_index()
    p = p.rename(columns={"balance": "balance_busd", "transition90": "transition_serious_pct"})
    for c in ("balance_busd", "transition_serious_pct"):
        if c not in p:
            p[c] = np.nan
    return p[COLUMNS["mart.nyfed_by_type"]].sort_values(["date", "loan_type"]).reset_index(drop=True)


# ----------------------------------------------------------------------------- orchestration
def _round(tables: dict[str, pd.DataFrame]) -> None:
    for name, df in tables.items():
        for col in df.columns:
            if df[col].dtype.kind != "f":
                continue
            dp = MUSD_DP if (col.endswith("_musd") or col.endswith("_busd")) else RATIO_DP
            if name == "core.fact_quarterly":
                continue  # keep source values untouched
            df[col] = df[col].round(dp)


def build_all(raw: pd.DataFrame | None = None) -> tuple[dict[str, pd.DataFrame], dict]:
    raw = load_raw() if raw is None else raw
    fact = build_fact_quarterly(raw)
    w = wide(fact)
    dates = mart_dates(w)
    holders = holder_amounts(w, dates)
    debt = build_debt_by_risk_holder(w, dates)
    pub = build_public_share(holders, w, dates)
    coll = build_collateral_coverage(w, dates)
    dim_crisis = build_dim_crisis()
    tables = {
        "core.dim_series": build_dim_series(fact),
        "core.dim_risk_bucket": build_dim_risk_bucket(),
        "core.dim_crisis": dim_crisis,
        "core.fact_quarterly": fact,
        "mart.debt_by_risk_holder": debt,
        "mart.public_share": pub,
        "mart.collateral_coverage": coll,
        "mart.crisis_event_window": build_crisis_event_window(metric_frame(debt, pub, coll), dim_crisis),
        "mart.nyfed_by_type": build_nyfed_by_type(fact),
    }
    _round(tables)
    _, _, cpi_base = _deflators(w, dates)
    split = split_consumer_credit(w, dates)
    meta = {
        "mart_start": str(dates.min().date()), "mart_end": str(dates.max().date()),
        "cpi_base_quarter": str(pd.Period(cpi_base, "Q")),
        "student_loans_reported_from": str(pd.Period(split["student_first"].iloc[0], "Q")),
        "vintages": {s: str(g.max().date()) for s, g in raw.groupby("source")["vintage"]},
    }
    return tables, meta


def write_out(tables: dict[str, pd.DataFrame], meta: dict) -> None:
    import json
    config.OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_csv(config.OUT_DIR / f"{name}.csv", index=False)
    (config.OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    log.info("transform: wrote %d tables to %s (%s)", len(tables), config.OUT_DIR,
             ", ".join(f"{k}={len(v)}" for k, v in tables.items()))


def read_out() -> dict[str, pd.DataFrame]:
    tables = {}
    for name, cols in COLUMNS.items():
        path = config.OUT_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"{path} missing - run `hhdebt transform` first")
        df = pd.read_csv(path)
        for c in ("date", "start_q", "end_q", "vintage"):
            if c in df:
                df[c] = pd.to_datetime(df[c])
        tables[name] = df[cols]
    return tables


def run() -> dict[str, pd.DataFrame]:
    tables, meta = build_all()
    write_out(tables, meta)
    return tables
