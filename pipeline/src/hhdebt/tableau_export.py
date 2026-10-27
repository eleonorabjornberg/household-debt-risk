"""Write flat, pre-joined CSVs to tableau/data/ for Tableau Public (which cannot connect to Postgres).

One file per dashboard, so the workbook needs no joins or relationships:
  ratchet.csv           debt_by_risk_holder + dim_risk_bucket + public_share (date x bucket x debt_type)
  crisis_windows.csv    crisis_event_window + dim_crisis
  collateral.csv        collateral_coverage + a readable class label
  payment_priority.csv  nyfed_by_type + labels + stress index vs each type's 2003-06 average
  crises.csv            dim_crisis (crisis bands)
Source: the database when DATABASE_URL is set, else data/out (same rule as export-snapshot).
"""
from __future__ import annotations

import logging

import pandas as pd

from . import config, export, transform

log = logging.getLogger(__name__)
TABLEAU_DATA_DIR = config.REPO_ROOT / "tableau" / "data"

COLLATERAL_LABELS = {"home_backed": "Home-backed", "vehicle_backed": "Vehicle-backed",
                     "uncollateralized": "No collateral", "other_nonrevolving": "Other non-revolving"}
LOAN_TYPES = {  # loan_type -> (label, collateral class)
    "mortgage": ("Mortgage", "home_backed"), "heloc": ("HELOC", "home_backed"),
    "auto": ("Auto", "vehicle_backed"), "credit_card": ("Credit card", "uncollateralized"),
    "student": ("Student loan", "uncollateralized"), "other": ("Other", "other_nonrevolving"),
}

# Column order of each output file; tests and tableau/build_workbook.py rely on these names.
COLUMNS = {
    "ratchet": ["date", "risk_bucket", "bucket_label", "is_public", "sort_order", "debt_type",
                "nominal_musd", "real_musd", "share_of_total", "public_share", "fed_mbs_share_of_scope"],
    "crisis_windows": ["crisis_id", "crisis_name", "kind", "start_q", "metric", "q_offset", "date",
                       "value", "value_at_t0", "delta_from_t0"],
    "collateral": ["date", "collateral_class", "class_label", "debt_musd", "collateral_value_musd",
                   "coverage_ratio", "share_of_debt", "is_estimated"],
    "payment_priority": ["date", "loan_type", "loan_label", "collateral_class", "balance_busd",
                         "transition_serious_pct", "baseline_2003_06_pct", "stress_index"],
    "crises": ["crisis_id", "name", "kind", "start_q", "end_q", "notes"],
}


def _tables(source: str) -> dict[str, pd.DataFrame]:
    use_db = source == "db" or (source == "auto" and config.database_url())
    if not use_db:
        return transform.read_out()
    out = {}
    for name, rows in export._rows_from_db().items():
        df = pd.DataFrame(rows, columns=transform.COLUMNS[name])
        for c in ("date", "start_q", "end_q"):
            if c in df:
                df[c] = pd.to_datetime(df[c])
        out[name] = df
    return out


def build(t: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    buckets = t["core.dim_risk_bucket"].rename(columns={"label": "bucket_label"})
    share = t["mart.public_share"][["date", "public_share", "fed_mbs_share_of_scope"]]
    ratchet = (t["mart.debt_by_risk_holder"].merge(buckets, on="risk_bucket", how="left")
               .merge(share, on="date", how="left")
               .sort_values(["date", "sort_order", "debt_type"]))

    crises = t["core.dim_crisis"].sort_values("start_q")
    windows = (t["mart.crisis_event_window"]
               .merge(crises[["crisis_id", "name", "kind", "start_q"]].rename(columns={"name": "crisis_name"}),
                      on="crisis_id", how="left")
               .sort_values(["start_q", "metric", "q_offset"]))

    coll = t["mart.collateral_coverage"].assign(
        class_label=lambda d: d.collateral_class.map(COLLATERAL_LABELS)).sort_values(["date", "collateral_class"])

    ny = t["mart.nyfed_by_type"].copy()
    ny["loan_label"] = ny.loan_type.map(lambda k: LOAN_TYPES[k][0])
    ny["collateral_class"] = ny.loan_type.map(lambda k: LOAN_TYPES[k][1])
    base = (ny[ny.date.dt.year <= 2006].groupby("loan_type").transition_serious_pct.mean()
            .rename("baseline_2003_06_pct"))
    ny = ny.merge(base, on="loan_type", how="left")
    ny["stress_index"] = ny.transition_serious_pct / ny.baseline_2003_06_pct
    ny = ny.sort_values(["date", "loan_type"])

    frames = {"ratchet": ratchet, "crisis_windows": windows, "collateral": coll,
              "payment_priority": ny, "crises": crises}
    return {k: df[COLUMNS[k]].reset_index(drop=True) for k, df in frames.items()}


def run(source: str = "auto") -> dict[str, pd.DataFrame]:
    out = build(_tables(source))
    TABLEAU_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in out.items():
        path = TABLEAU_DATA_DIR / f"{name}.csv"
        df.to_csv(path, index=False, date_format="%Y-%m-%d", float_format="%.10g")
        log.info("export-tableau: %s (%d rows) -> %s", name, len(df), path)
    return out
