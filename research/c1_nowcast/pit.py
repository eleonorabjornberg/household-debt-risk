#!/usr/bin/env python3
"""PLAN task C1, data plumbing: point-in-time (as-of) panel and release-lag table for the nowcast inputs.

    uv run --project pipeline python research/c1_nowcast/pit.py            # fetch vintages, write tables
    uv run --project pipeline python research/c1_nowcast/pit.py --asof 2024-05-01   # print one as-of panel

No evaluation is computed here: the indicator set, vintage rule, benchmarks and metrics are Eleonora's
choice (tracks/markets.md, "Questions for Eleonora"). This file only answers "what was public on day t?".

Point-in-time rule. ALFRED returns, for every observation date, each value it has ever had with the
interval [realtime_start, realtime_end] during which that value was current. The value known on
day t is the row with realtime_start <= t <= realtime_end. An observation whose first realtime_start is
after t did not exist yet on day t and is absent from the as-of panel (never filled, never a default).

Outputs (next to this file): release_lags.csv (per input: first and median publication lag in days
after the end of the reference period, number of vintages, first vintage), z1_calendar.csv (Z.1
release dates as recorded by ALFRED), inputs_coverage.csv. Raw ALFRED JSON is cached in data/fred/.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "common"))
import fred  # noqa: E402

FREQ_OFFSET = {"W": "W", "M": "M", "Q": "Q"}


def load_inputs() -> list[dict]:
    return yaml.safe_load((HERE / "inputs.yaml").read_text())["inputs"]


def period_end(dates: pd.Series, freq: str) -> pd.Series:
    """End of the reference period of each observation date (FRED dates mark the period start, except
    weekly H.8 / H.4.1 series, whose date is the Wednesday or week-ending day itself)."""
    if freq == "W":
        return dates
    return dates.dt.to_period(freq).dt.end_time.dt.normalize()


def as_of(v: pd.DataFrame, t) -> pd.Series:
    """Values of one series as they were known at the END of day t (Timestamp or ISO date).

    Same-day rule: a value published on day t (realtime_start == t) is included, so a nowcast "at t"
    means after that day's releases. Use t - 1 day for a nowcast made before the day's releases.
    """
    t = pd.Timestamp(t)
    known = v[(v["realtime_start"] <= t) & (v["realtime_end"] >= t)]
    s = known.set_index("date")["value"].sort_index()
    assert not s.index.duplicated().any(), "two values current on the same day for one date"
    return s


def first_release(v: pd.DataFrame) -> pd.DataFrame:
    """First published value of each observation and the day it was published.

    For dates already in ALFRED's first vintage this is the first value ALFRED holds, not the true
    first release (which predates ALFRED); callers that need true first releases must drop them,
    as release_lags and revision_size do. NaN values ('.') count as published.
    """
    f = v.sort_values("realtime_start").groupby("date", as_index=False).nth(0)
    return f[["date", "realtime_start", "value"]].rename(columns={"realtime_start": "published"})


def release_lags(v: pd.DataFrame, freq: str, since: str | None = None) -> dict:
    """Publication lag (days after the reference period ends) of each observation's first release.

    Only observations first published after ALFRED's first vintage count: earlier observations all
    carry that first vintage date as their 'release', which would overstate the lag.
    """
    f = first_release(v)
    first_vintage = v["realtime_start"].min()
    f = f[f["published"] > first_vintage]
    # Count only observations that were the newest date in the vintage that first carried them;
    # ALFRED also back-fills old dates when a series' history is extended, which is not a release lag.
    newest = v.groupby("realtime_start")["date"].max()
    f = f[f["date"].values == newest.reindex(f["published"]).values]
    if since:
        f = f[f["published"] >= pd.Timestamp(since)]
    lag = (f["published"] - period_end(f["date"], freq)).dt.days
    return {
        "n_obs": int(len(lag)),
        "lag_days_min": int(lag.min()) if len(lag) else None,
        "lag_days_median": float(lag.median()) if len(lag) else None,
        "lag_days_max": int(lag.max()) if len(lag) else None,
    }


def revision_size(v: pd.DataFrame) -> float | None:
    """Median absolute revision, first release to current value, as a share of the current value, over
    observations first released after ALFRED's first vintage (older history is mostly never revised)."""
    f = first_release(v)
    f = f[f["published"] > v["realtime_start"].min()].set_index("date")["value"]  # released inside ALFRED's window
    cur = v[v["realtime_end"] >= v["realtime_end"].max()].set_index("date")["value"]
    j = pd.concat([f, cur], axis=1, keys=["first", "cur"]).dropna()
    j = j[j["cur"] != 0]
    return float(((j["first"] - j["cur"]).abs() / j["cur"].abs()).median()) if len(j) else None


def load_vintages(inputs) -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    """ALFRED vintages for every input, dollar series rescaled to millions per the units then current
    (G.19 vintages switched from billions to millions on 2025-02-07, Z.1 series on FRED on 2026-01-09;
    see sources.md)."""
    vint, rescaled = {}, {}
    for i in inputs:
        v, n = fred.to_millions(fred.vintages(i["id"]), fred.units_history(i["id"]))
        vint[i["id"]], rescaled[i["id"]] = v, n
    return vint, rescaled


def panel(t, inputs=None, vint=None) -> dict[str, pd.Series]:
    """As-of panel at day t: {input id: series as known on t}. Series not yet in ALFRED on t are absent."""
    inputs = inputs or load_inputs()
    out = {}
    for inp in inputs:
        if inp.get("alfred") is False:
            continue
        v = vint[inp["id"]] if vint else load_vintages([inp])[0][inp["id"]]
        s = as_of(v, t)
        if len(s):
            out[inp["id"]] = s
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--asof", help="print the as-of panel for this day (last 3 observations per input)")
    a = ap.parse_args(argv)
    inputs = [i for i in load_inputs() if i.get("alfred", True)]
    vint, rescaled = load_vintages(inputs)

    if a.asof:
        for k, s in panel(a.asof, inputs, vint).items():
            print(k, s.dropna().tail(3).to_dict())
        return 0

    rows = []
    for inp in inputs:
        v = vint[inp["id"]]
        lag = release_lags(v, inp["freq"])
        rows.append({
            "id": inp["id"], "release": inp["release"], "freq": inp["freq"], "role": inp["role"],
            "first_vintage": v["realtime_start"].min().date().isoformat(),
            "n_vintages": int(v["realtime_start"].nunique()),
            "first_obs": v["date"].min().date().isoformat(),
            **lag,
            "median_abs_revision_share": revision_size(v),
            "rows_rescaled_to_millions": rescaled[inp["id"]],
            "units_label_current": fred.units_history(inp["id"])["units"].iloc[-1],  # values above are in millions
        })
    lags = pd.DataFrame(rows)
    # Checks: lags are non-negative and no observation was published before its period ended
    # (weekly H.8 dates are week-ending Wednesdays; a negative lag would mean a wrong period convention).
    assert (lags["lag_days_min"].dropna() >= 0).all(), lags[["id", "lag_days_min"]]
    lags.to_csv(HERE / "release_lags.csv", index=False, float_format="%.4g")

    # Z.1 release calendar, as ALFRED records it (vintage dates of a Z.1 level series)
    z = sorted(set(vint["BOGZ1FL413065105Q"]["realtime_start"]) | set(vint["HMLBSHNO"]["realtime_start"]))
    zc = pd.DataFrame({"z1_release": [d.date().isoformat() for d in z]})
    hh = first_release(vint["HMLBSHNO"])
    zc["latest_quarter_published"] = [
        str(hh[hh["published"] <= d]["date"].max().to_period("Q")) if (hh["published"] <= d).any() else ""
        for d in z]
    zc.to_csv(HERE / "z1_calendar.csv", index=False)
    print(lags.to_string(index=False))
    print(f"{len(zc)} Z.1 releases in ALFRED, {zc.z1_release.iloc[0]} to {zc.z1_release.iloc[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
