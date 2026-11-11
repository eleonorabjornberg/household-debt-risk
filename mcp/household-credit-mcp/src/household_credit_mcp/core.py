"""Tool logic. Every function returns a plain dict envelope; nothing here invents numbers."""
from __future__ import annotations

import csv
import json
import re
from functools import lru_cache
from typing import Any

import yaml

from .backends import repo_file

Z1_UNITS = "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)"
LIMITS_URL = "/methods#limits"


@lru_cache(maxsize=1)
def _shared_limits() -> dict[str, str]:
    """Shared limit texts from claims/limits.json (one source, also behind the site and the Ask API), as 'title: body'."""
    with open(repo_file("claims", "limits.json"), encoding="utf-8") as f:
        return {x["id"]: f"{x['title']}: {x['body']}" for x in json.load(f)}


def shared(*ids: str) -> list[str]:
    texts = _shared_limits()
    return [texts[i] for i in ids]


COMMON_Z1 = shared("z1-levels-nsa", "holding-not-bearing", "mortgage-holders-apportioned", "out-of-scope-liabilities")
PUBLIC_BUCKETS = ["federal_direct", "gse_agency", "state_local"]
TOOLS = {  # nearest-answerable pointers
    "public_share": "public_share(start, end, measure)",
    "holdings": "holdings_by_bucket(quarter)",
    "nyfed": "nyfed_by_type(start, end)",
    "coverage": "collateral_coverage(start, end)",
}


# ------------------------------------------------------------------ envelope helpers
def ok(backend, tool: str, data: Any, *, units: dict | str, series_ids: list[str], source: str,
       limits: list[str], extra: dict | None = None) -> dict:
    v = backend.vintages()
    out = {
        "ok": True, "tool": tool, "backend": backend.name,
        "source": source,
        "vintage": {"source_vintage": v.get(source if source in v else "z1"), "all": v},
        "units": units, "series_ids": series_ids, "limits": limits, "limits_url": LIMITS_URL, "data": data,
    }
    if getattr(backend, "note", None):
        out["backend_note"] = backend.note
    if extra:
        out.update(extra)
    return out


def refusal(backend, tool: str, code: str, reason: str, nearest: list[dict]) -> dict:
    return {"ok": False, "refused": True, "tool": tool, "backend": backend.name if backend else None,
            "reason_code": code, "reason": reason, "nearest_answerable": nearest,
            "note": "No number was returned: the data cannot answer this question."}


# ------------------------------------------------------------------ quarters
_Q = re.compile(r"^\s*(\d{4})\s*-?\s*Q([1-4])\s*$", re.I)
_QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}


def parse_quarter(s: str) -> str | None:
    """'2026Q2' or '2026-06-30' -> '2026-06-30'; None if not a quarter-end."""
    if not isinstance(s, str):
        return None
    m = _Q.match(s)
    if m:
        return f"{m[1]}-{_QEND[int(m[2])]}"
    if re.fullmatch(r"\d{4}-(03-31|06-30|09-30|12-31)", s.strip()):
        return s.strip()
    return None


def label(d: str) -> str:
    return f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"


def _resolve_range(backend, tool, start, end, lo, hi, alt_tool):
    """Return (start_date, end_date, None) or (None, None, refusal)."""
    e = parse_quarter(end) if end else hi
    s = parse_quarter(start) if start else e
    if s is None or e is None:
        return None, None, refusal(backend, tool, "bad_quarter",
                                   "Quarters must look like 2026Q2 (quarterly data only).",
                                   [{"tool": alt_tool, "args": {"start": label(hi), "end": label(hi)}}])
    if s > e:
        return None, None, refusal(backend, tool, "bad_range", "start is after end.",
                                   [{"tool": alt_tool, "args": {"start": label(e), "end": label(e)}}])
    if s > hi or e > hi:
        return None, None, refusal(
            backend, tool, "future_or_unpublished",
            f"Latest quarter in the data is {label(hi)}. Later quarters are future or unpublished values; "
            "this server reports published history only and does not forecast.",
            [{"tool": alt_tool, "args": {"start": label(min(s, hi)), "end": label(hi)}}])
    if s < lo or e < lo:
        return None, None, refusal(
            backend, tool, "before_coverage", f"Earliest quarter in the data for this table is {label(lo)}.",
            [{"tool": alt_tool, "args": {"start": label(lo), "end": label(min(max(e, lo), hi))}}])
    return s, e, None


# ------------------------------------------------------------------ catalog
@lru_cache(maxsize=1)
def catalog() -> dict:
    return yaml.safe_load(repo_file("pipeline", "series_catalog.yaml").read_text())


def _series_row(s: dict) -> dict:
    cat = catalog()
    row = dict(s)
    row["units"] = {"z1": Z1_UNITS, "fred": "see FRED series page (context series; frequency varies)",
                    "nyfed": "USD billions / % as published by the NY Fed (CCP)"}[s["source"]]
    if s.get("risk_bucket"):
        row["risk_bucket_label"] = cat["risk_buckets"][s["risk_bucket"]]["label"]
        row["is_public_holder"] = cat["risk_buckets"][s["risk_bucket"]]["public"]
    return row


def list_series(backend, role: str | None = None, source: str | None = None) -> dict:
    rows = [s for s in catalog()["series"]
            if (role is None or s["role"] == role) and (source is None or s["source"] == source)]
    data = [{"id": s["id"], "source": s["source"], "role": s["role"], "desc": s["desc"],
             "risk_bucket": s.get("risk_bucket"), "debt_type": s.get("debt_type")} for s in rows]
    roles = sorted({s["role"] for s in catalog()["series"]})
    return ok(backend, "list_series", data, units="n/a (catalog listing)", series_ids=[s["id"] for s in rows],
              source="z1", limits=[f"Available roles: {', '.join(roles)}.",
                                    "Catalog is pipeline/series_catalog.yaml; it lists what is loaded, not every Z.1 series."])


def describe_series(backend, id: str) -> dict:
    sid = (id or "").strip().upper()
    hit = next((s for s in catalog()["series"] if s["id"].upper() == sid), None)
    if not hit:
        return refusal(backend, "describe_series", "unknown_series",
                       f"{id!r} is not in the series catalog (the data holds only catalogued series).",
                       [{"tool": "list_series", "args": {}}])
    lim = []
    if hit["role"] == "mortgage_holder":
        lim.append("Holder of ALL 1-4 family mortgages (asset side); apportioned to households in the mart.")
    if hit["role"] == "cc_holder":
        lim.append("Holder of consumer credit (asset side); one dimension only, not split by loan type.")
    if hit["role"] == "cc_type":
        lim.append("Loan type (liability side); Z.1 does not split these by holder.")
    if hit["id"] == "FL155111005":
        lim.extend(shared("durables-proxy") + ["The proxy series is FL155111005."])
    if hit["source"] == "fred":
        lim.append("Context series; not part of the holder shares.")
    return ok(backend, "describe_series", _series_row(hit), units=_series_row(hit)["units"],
              series_ids=[hit["id"]], source=hit["source"], limits=lim or ["See catalog header for methods."])


# ------------------------------------------------------------------ data tools
def _pct(x): return None if x is None else f"{x * 100:.1f}%"
def _tn(m): return None if m is None else f"${m / 1e6:.2f}T"


def _ids(buckets=None, roles=("mortgage_holder", "cc_holder")):
    return [s["id"] for s in catalog()["series"]
            if s["role"] in roles and (buckets is None or s.get("risk_bucket") in buckets)]


def public_share(backend, start=None, end=None, measure="total") -> dict:
    tool = "public_share"
    if measure not in ("total", "mortgage", "consumer_credit"):
        return refusal(backend, tool, "bad_measure", "measure must be total, mortgage or consumer_credit.",
                       [{"tool": tool, "args": {"measure": "total"}}])
    lo, hi = backend.mart_range()
    s, e, r = _resolve_range(backend, tool, start, end, lo, hi, tool)
    if r:
        return r
    key = {"total": "public_share", "mortgage": "public_share_mortgage", "consumer_credit": "public_share_cc"}[measure]
    rows = []
    for x in backend.public_share(s, e):
        row = {"quarter": label(x["date"]), "date": x["date"], "public_share": x[key],
               "public_share_display": _pct(x[key])}
        if measure == "total":
            row.update(public_musd=x["public_musd"], public_usd_display=_tn(x["public_musd"]),
                       scope_total_musd=x["scope_total_musd"], scope_usd_display=_tn(x["scope_total_musd"]),
                       fed_mbs_musd=x["fed_mbs_musd"])
        rows.append(row)
    ids = {"total": ["FL154104015", "FL153165105", "FL153166000"] + _ids(PUBLIC_BUCKETS),
           "mortgage": ["FL153165105", "FL893065105"] + _ids(PUBLIC_BUCKETS, ("mortgage_holder",)),
           "consumer_credit": ["FL153166000"] + _ids(PUBLIC_BUCKETS, ("cc_holder",))}[measure]
    lim = COMMON_Z1 + ["Public = federal government (direct) + GSEs & agency pools + state & local governments. "
                       "Dollars are nominal.",
                       "fed_mbs_musd is Fed MBS (WSHOMCB)."] + shared("fed-mbs-rate-risk")
    return ok(backend, tool, rows, source="z1", series_ids=ids, limits=lim,
              units={"public_share": "fraction 0-1 (display as %)", "public_musd": Z1_UNITS,
                     "scope_total_musd": Z1_UNITS, "measure": measure})


def holdings_by_bucket(backend, quarter=None) -> dict:
    tool = "holdings_by_bucket"
    lo, hi = backend.mart_range()
    d = parse_quarter(quarter) if quarter else hi
    if d is None:
        return refusal(backend, tool, "bad_quarter", "quarter must look like 2026Q2.",
                       [{"tool": tool, "args": {"quarter": label(hi)}}])
    if d > hi:
        return refusal(backend, tool, "future_or_unpublished",
                       f"Latest quarter in the data is {label(hi)}; this server does not forecast.",
                       [{"tool": tool, "args": {"quarter": label(hi)}}])
    if d < lo:
        return refusal(backend, tool, "before_coverage", f"Earliest quarter is {label(lo)}.",
                       [{"tool": tool, "args": {"quarter": label(lo)}}])
    rows = backend.holdings(d)
    if not rows:
        return refusal(backend, tool, "no_data", f"No holdings rows for {label(d)}.",
                       [{"tool": tool, "args": {"quarter": label(hi)}}])
    dims = {b["risk_bucket"]: b for b in backend.risk_buckets()}
    cat = catalog()
    agg: dict[str, dict] = {}
    for r in rows:
        a = agg.setdefault(r["risk_bucket"], {"mortgage_musd": 0.0, "consumer_credit_musd": 0.0,
                                              "nominal_musd": 0.0, "real_musd": 0.0, "share_of_scope": 0.0})
        a[f"{r['debt_type']}_musd"] += r["nominal_musd"]
        a["nominal_musd"] += r["nominal_musd"]
        a["real_musd"] += r["real_musd"] or 0.0
        a["share_of_scope"] += r["share_of_total"]
    data = []
    for b in sorted(agg, key=lambda k: dims[k]["sort_order"]):
        a = {k: round(v, 3) if k != "share_of_scope" else v for k, v in agg[b].items()}
        data.append({"risk_bucket": b, "label": dims[b]["label"], "is_public": dims[b]["is_public"],
                     **a, "share_display": _pct(a["share_of_scope"]), "usd_display": _tn(a["nominal_musd"]),
                     "series_ids": [s["id"] for s in cat["series"]
                                    if s.get("risk_bucket") == b and s["role"] in ("mortgage_holder", "cc_holder")]})
    total = sum(x["nominal_musd"] for x in data)
    pub = sum(x["nominal_musd"] for x in data if x["is_public"])
    summary = {"quarter": label(d), "scope_total_musd": round(total, 3), "scope_usd_display": _tn(total),
               "public_musd": round(pub, 3), "public_share": pub / total, "public_share_display": _pct(pub / total)}
    return ok(backend, tool, data, source="z1",
              series_ids=["FL154104015", "FL153165105", "FL153166000"] + _ids(),
              units={"nominal_musd": Z1_UNITS, "real_musd": "USD millions, constant dollars of the latest CPI "
                     "quarter (CPIAUCSL, FRED); an estimate",
                     "share_of_scope": "fraction 0-1 of mortgages + consumer credit"},
              limits=COMMON_Z1 + ["Six risk buckets are this project's grouping of Z.1 holder sectors (catalog).",
                                   "real_musd uses a CPI deflator and is not a published Z.1 number."],
              extra={"summary": summary})


def crisis_windows(backend, crisis_id=None, metric="public_share") -> dict:
    tool = "crisis_windows"
    crises = {c["crisis_id"]: c for c in backend.crises()}
    if crisis_id and crisis_id not in crises:
        return refusal(backend, tool, "unknown_crisis", f"{crisis_id!r} is not in dim_crisis.",
                       [{"tool": tool, "args": {}, "crisis_ids": sorted(crises)}])
    rows = backend.crisis_window(metric, crisis_id)
    if not rows:
        return refusal(backend, tool, "unknown_metric",
                       f"No event-window rows for metric {metric!r}. Examples: public_share, share:gse_agency, "
                       "share:uncollateralized, coverage:home_backed.", [{"tool": tool, "args": {"metric": "public_share"}}])
    ratio = metric.startswith("coverage:")
    by: dict[str, dict[int, dict]] = {}
    for r in rows:
        by.setdefault(r["crisis_id"], {})[r["q_offset"]] = r
    data = []
    for cid, offs in by.items():
        t0 = offs.get(0)
        c = crises[cid]
        row = {"crisis_id": cid, "name": c["name"], "kind": c["kind"], "start_q": c["start_q"], "end_q": c["end_q"],
               "notes": c["notes"], "t0_quarter": label(t0["date"]) if t0 else None,
               "value_at_t0": t0["value"] if t0 else None,
               "max_offset_available": max(offs), "min_offset_available": min(offs)}
        for k in (4, 8, 16):
            o = offs.get(k)
            row[f"delta_q{k}"] = None if o is None else (o["delta_from_t0"] if ratio else o["delta_from_t0"] * 100)
        data.append(row)
    return ok(backend, tool, data, source="z1", series_ids=["FL154104015"] + _ids(),
              units={"value_at_t0": "ratio (collateral/debt)" if ratio else "fraction 0-1",
                     "delta_qN": "change vs t0, in ratio units" if ratio else "percentage points vs t0 (computed here as delta*100)",
                     "window": "q_offset -8..+16 quarters around t0 (crisis start quarter)"},
              limits=COMMON_Z1 + ["Event windows are descriptive; a change after a crisis start is not shown to be caused by it.",
                                   "Recent crises have truncated windows (see max_offset_available); missing deltas are null, not zero."],
              extra={"metric": metric})


def collateral_coverage(backend, start=None, end=None) -> dict:
    tool = "collateral_coverage"
    lo, hi = backend.mart_range()
    s, e, r = _resolve_range(backend, tool, start, end, lo, hi, tool)
    if r:
        return r
    cl = {c: v["label"] for c, v in catalog()["collateral_classes"].items()}
    data = [{"quarter": label(x["date"]), "date": x["date"], "collateral_class": x["collateral_class"],
             "label": cl.get(x["collateral_class"]), "debt_musd": x["debt_musd"],
             "collateral_value_musd": x["collateral_value_musd"], "coverage_ratio": x["coverage_ratio"],
             "share_of_scope": x["share_of_debt"], "is_estimated": x["is_estimated"]}
            for x in backend.coverage(s, e)]
    return ok(backend, tool, data, source="z1",
              series_ids=["FL153165105", "FL153166100", "FL153166220", "FL153166400", "FL153166205", "FL155035015", "FL155111005"],
              units={"debt_musd": Z1_UNITS, "collateral_value_musd": Z1_UNITS,
                     "coverage_ratio": "aggregate collateral value / aggregate debt (a ratio, not per-loan LTV)",
                     "share_of_scope": "fraction 0-1"},
              limits=COMMON_Z1 + [
                  "Coverage is a sector-level aggregate; it says nothing about any individual borrower's equity.",
                  *shared("durables-proxy"), "The durables series is FL155111005.",
                  "Uncollateralized and other non-revolving classes have no collateral value (null ratio).",
                  "Rows with is_estimated=true use an imputed loan-type split (early years); treat as estimates."])


def nyfed_by_type(backend, start=None, end=None) -> dict:
    tool = "nyfed_by_type"
    lo, hi = backend.nyfed_range()
    s, e, r = _resolve_range(backend, tool, start, end, lo, hi, tool)
    if r:
        return r
    data = [{"quarter": label(x["date"]), "date": x["date"], "loan_type": x["loan_type"],
             "balance_busd": x["balance_busd"], "transition_into_serious_delinquency_pct": x["transition_serious_pct"]}
            for x in backend.nyfed(s, e)]
    return ok(backend, tool, data, source="nyfed", series_ids=["NYFED_HHDC"],
              units={"balance_busd": "USD billions as published", "transition_into_serious_delinquency_pct":
                     "% of balance newly 90+ days delinquent, annualized, as published"},
              limits=["SOURCE IS THE NEW YORK FED CONSUMER CREDIT PANEL (credit bureau data), NOT FEDERAL RESERVE Z.1.",
                       "Balances use a different definition from Z.1 and do not reconcile to Z.1 totals; do not mix them.",
                       "This table splits by loan TYPE only. It has no holder dimension, so it cannot say who holds the debt.",
                       "Student-loan delinquency transition is null in early years (not reported).",
                       "Not seasonally adjusted as loaded; transition rates are annualized as published."])


# ------------------------------------------------------------------ claims
@lru_cache(maxsize=1)
def _claims() -> list[dict]:
    with open(repo_file("claims", "register.csv"), newline="") as f:
        return list(csv.DictReader(f))


def lookup_claim(backend, text_or_id: str, limit: int = 5) -> dict:
    q = (text_or_id or "").strip().lower()
    if not q:
        return refusal(backend, "lookup_claim", "empty_query", "Give a claim id or some words.", [])
    claims = _claims()
    exact = [c for c in claims if c["claim_id"].lower() == q]
    if exact:
        hits = exact
    else:
        toks = set(re.findall(r"[a-z0-9.%$]+", q))
        scored = []
        for c in claims:
            hay = " ".join([c["claim_id"], c["claim"], c["display"], c["period"]]).lower()
            hay_t = set(re.findall(r"[a-z0-9.%$]+", hay)) | set(c["claim_id"].lower().split("_"))
            sc = len(toks & hay_t)
            if sc:
                scored.append((sc, c))
        scored.sort(key=lambda t: -t[0])
        hits = [c for _, c in scored[:limit]]
    if not hits:
        return refusal(backend, "lookup_claim", "no_matching_claim",
                       "No row in claims/register.csv matches. Unregistered numbers are not published numbers.",
                       [{"tool": "data_coverage", "args": {}}])
    data = [{"claim_id": c["claim_id"], "claim": c["claim"], "display": c["display"], "value": c["value"],
             "unit": c["unit"], "period": c["period"], "check_id": c["check_id"], "series_ids": c["series_ids"].split(),
             "vintage": c["vintage"], "validation": c["validation"], "computation": c["computation"],
             "notes": c["notes"], "quotable_as_verified": c["validation"] == "PASS"} for c in hits]
    return ok(backend, "lookup_claim", data, units="as stated per claim", series_ids=sorted({s for d in data for s in d["series_ids"]}),
              source="z1", limits=[
                  "Source is claims/register.csv (read from the repository, not the database).",
                  "Only validation=PASS rows are verified. UNVERIFIED rows are registered but not yet checked; "
                  "ESTIMATE rows are labelled estimates. Do not present non-PASS rows as fact.",
                  "Vintage shown is each claim's own vintage."])


# ------------------------------------------------------------------ coverage & refusals
def data_coverage(backend) -> dict:
    lo, hi = backend.mart_range()
    nlo, nhi = backend.nyfed_range()
    cat = catalog()
    data = {
        "can_answer": [
            f"Public vs private share of household 1-4 family mortgages + consumer credit, quarterly {label(lo)}-{label(hi)} (Z.1).",
            f"Holdings by six risk buckets, in dollars and share of scope, {label(lo)}-{label(hi)}; mortgages and consumer credit combined or separate, but not split by loan type within a holder.",
            "Collateral coverage (collateral value / debt) by collateral class.",
            "Crisis event windows (-8..+16 quarters) for 14 recessions/shocks.",
            f"NY Fed CCP balances and serious-delinquency transitions by loan type, {label(nlo)}-{label(nhi)} (a different source from Z.1).",
            "Registered, validated claims (claims/register.csv).",
        ],
        "cannot_answer": [
            "Consumer credit by holder AND loan type together (Z.1 gives holders or types, never the cross), e.g. auto loans held by banks.",
            "Anything outside the covered quarters, and any forecast or future value.",
            "Loan-level or borrower-level questions (individual loans, credit scores, who owes what).",
            "Geographic splits (state, county, zip, metro): the data is national.",
            "Monthly, weekly or daily household-debt values (quarterly only).",
            "Delinquency by holder (the NY Fed table has types, not holders).",
            "Guarantee or credit-risk exposure: the data shows who holds debt, not who bears the loss.",
        ],
        "coverage": {"mart_quarters": [label(lo), label(hi)], "nyfed_quarters": [label(nlo), label(nhi)],
                     "student_loans_reported_from": backend_meta(backend).get("student_loans_reported_from"),
                     "risk_buckets": {k: v["label"] for k, v in cat["risk_buckets"].items()},
                     "series_in_catalog": len(cat["series"])},
    }
    return ok(backend, "data_coverage", data, units="n/a", series_ids=[], source="z1",
              limits=["Coverage dates come from the backend in use; vintages are in the vintage field."])


def backend_meta(backend):
    b = getattr(backend, "meta", None) or getattr(getattr(backend, "_snap", None), "meta", None)
    return b or {}


_CC_TYPE = r"(auto|car|vehicle|student|credit[ -]?card|card|revolving)"
_HOLDER = r"(held by|holder|holders|owned by|banks?\b|credit unions?|finance compan|gses?|fannie|freddie|federal government|abs\b|securiti[sz]|who holds|which (sector|institution))"
RULES = [
    ("forecast", r"forecast|predict|projection|project(ed)? (to|for)|will (be|rise|fall|reach)|next (quarter|year)|going to|in 20(2[7-9]|[3-9]\d)(?!\d)|by 20(2[7-9]|[3-9]\d)(?!\d)|future|expect",
     "Forecasts and future values are not available; the server only reports published history.",
     [{"tool": "public_share", "args": {"measure": "total"}}, {"tool": "crisis_windows", "args": {}}]),
    ("loan_or_borrower_level", r"borrower|loan[- ]level|individual|credit score|fico|my (loan|mortgage|debt)|which (people|households|families)|per household|per capita|income group|race|age group|zip",
     "The data is aggregate sector totals. There is no loan-level or borrower-level information.",
     [{"tool": "holdings_by_bucket", "args": {}}, {"tool": "nyfed_by_type", "args": {}}]),
    ("geography", r"by state|per state|each state|state[- ]level|statewide|counties|county|metro|\bmsa\b|city|cities|region|california|texas|florida|new york (city|state)|rural|urban",
     "The data is national. There are no state, county or regional splits.",
     [{"tool": "public_share", "args": {"measure": "total"}}]),
    ("frequency", r"monthly|weekly|daily|month[- ]by[- ]month",
     "Household-debt holdings are quarterly (end of quarter).",
     [{"tool": "public_share", "args": {}}]),
]


def check_answerable(backend, question: str) -> dict:
    """Heuristic pre-check. A pass is not a guarantee; a refusal is definitive for these patterns."""
    tool = "check_answerable"
    qs = (question or "").lower()
    lo, hi = backend.mart_range()
    holder_x_type = re.search(_CC_TYPE, qs) and re.search(_HOLDER, qs)
    delinq_holder = re.search(r"delinquen|default|90\+", qs) and re.search(_HOLDER, qs) and not re.search(r"loan type|by type", qs)
    if holder_x_type or delinq_holder:
        why = ("Z.1 reports consumer credit by holder OR by loan type, never both together, so the number cannot be "
               "read from the data." if holder_x_type else
               "Delinquency is available by loan type (NY Fed CCP) but not by holder.")
        return refusal(backend, tool, "holder_by_type_not_available", why, [
            {"tool": "holdings_by_bucket", "args": {}, "gives": "consumer credit by holder (all types combined)"},
            {"tool": "collateral_coverage", "args": {}, "gives": "consumer credit by type (all holders combined)"},
            {"tool": "nyfed_by_type", "args": {}, "gives": "NY Fed balances/delinquency by type (not Z.1)"}])
    for code, pat, reason, alt in RULES:
        if re.search(pat, qs):
            return refusal(backend, tool, code, reason, alt)
    for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b(?:\s*q[1-4])?", qs):
        y = int(y)
        if y < int(lo[:4]):
            return refusal(backend, tool, "before_coverage", f"Data starts in {label(lo)}.",
                           [{"tool": "public_share", "args": {"start": label(lo), "end": label(lo)}}])
        if y > int(hi[:4]):
            return refusal(backend, tool, "future_or_unpublished",
                           f"Latest quarter is {label(hi)}.", [{"tool": "public_share", "args": {"end": label(hi)}}])
    return ok(backend, tool, {"answerable": True, "note": "No refusal pattern matched. Use the data tools; they "
                              "still refuse out-of-coverage quarters."}, units="n/a", series_ids=[], source="z1",
              limits=["Heuristic check only."])
