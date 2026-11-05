"""E1 gold answers, path 2: rebuild the tables the E1 questions read from the RAW sources, then compare.

Called by run.py (checks E1-<question id>). Like the rest of the validation suite it does not import `hhdebt`
and does not read the pipeline's staging or the database. Inputs:
  * the raw Z.1 frame run.py already parsed from FRB_Z1_csv.zip (series IDs and bucket membership from
    pipeline/series_catalog.yaml, as run.py does);
  * the raw NY Fed workbook HHD_C_Report_<yq>.xlsx, parsed here by sheet title (the pipeline locates sheets
    through the table of contents);
  * definitions only: crisis start quarters from the snapshot's dim_crisis.json (a project definition, not data).

For each answerable question in evals/e1_sql_benchmark/questions.yaml without an existing register row, the
question's check is evaluated on these rebuilt tables and on the snapshot the MCP server serves
(evals/e1_sql_benchmark/spec.py, a shared evaluator). PASS when the two agree to a tenth of the question's
scoring tolerance (exactly, for counts) and name the same quarter. The rebuilt value is reported as
`observed`; build_register.py writes it into the register row.

Rebuilt definitions (from the methodology notes, re-implemented, not imported):
  public_share         = run.compute(): public mortgage holders apportioned by FL153165105 / FL893065105
  debt_by_risk_holder  mortgage: bucket's holders / FL893065105 * FL153165105; consumer credit: bucket's
                       holders as reported; share_of_total = nominal / FL154104015
  collateral_coverage  home_backed FL153165105 vs FL155035015; vehicle_backed FL153166400 vs FL155111005;
                       uncollateralized FL153166100 + FL153166220 and other_nonrevolving FL153166205 ONLY from
                       the first quarter with student loans reported (earlier rows are imputed in the pipeline
                       and are not rebuilt here, so a question touching them cannot PASS)
  crisis_event_window  offsets -8..+16 around each crisis start, on the metrics above
  nyfed_by_type        balance (trillions x 1000 = $B) and new-seriously-delinquent share by loan type
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
QUESTIONS = ROOT / "evals" / "e1_sql_benchmark" / "questions.yaml"
SNAP = ROOT / "web" / "public" / "data"
NYFED_XLSX = ROOT / "data" / "validation" / "nyfed" / "HHD_C_Report_2026Q2.xlsx"
NYFED_URL = "https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/HHD_C_Report_2026Q2.xlsx"
FIRST_DATE = pd.Timestamp("1951-12-31")  # first quarter of the quarterly Z.1 record the snapshot starts at

sys.path.insert(0, str(ROOT / "evals" / "e1_sql_benchmark"))
import spec  # noqa: E402

BAL_COLS = {"mortgage": "mortgage", "he revolving": "heloc", "auto loan": "auto", "credit card": "credit_card",
            "student loan": "student", "other": "other"}
TRANS_COLS = {"mortgage": "mortgage", "heloc": "heloc", "auto": "auto", "cc": "credit_card",
              "student loan": "student", "other": "other"}


def _d(ts) -> str:
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- Z.1 tables
def z1_tables(df: pd.DataFrame, cat: dict, groups: dict, res: pd.DataFrame) -> dict[str, list[dict]]:
    idx = df.index[(df.index >= FIRST_DATE) & df["FL154104015"].notna()]
    df, res = df.loc[idx], res.loc[idx]
    scope, mort, all_mort = df["FL154104015"], df["FL153165105"], df["FL893065105"]

    ps = [{"date": _d(t), "scope_total_musd": r.scope, "public_musd": r.public, "public_share": r.share,
           "public_share_mortgage": r.share_mort, "public_share_cc": r.share_cc} for t, r in res.iterrows()]

    buckets = list(cat["risk_buckets"])
    dbh, bucket_share = [], {}
    for b in buckets:
        m_ids = [s["id"] for s in groups["mort_holders"] if s["risk_bucket"] == b]
        c_ids = [s["id"] for s in groups["cc_holders"] if s["risk_bucket"] == b]
        m = df[m_ids].fillna(0).sum(axis=1) / all_mort * mort if m_ids else pd.Series(0.0, index=idx)
        c = df[c_ids].fillna(0).sum(axis=1) if c_ids else pd.Series(0.0, index=idx)
        bucket_share[b] = (m + c) / scope
        for kind, s in (("mortgage", m), ("consumer_credit", c)):
            dbh += [{"date": _d(t), "risk_bucket": b, "debt_type": kind, "nominal_musd": v, "share_of_total": v / scope[t]}
                    for t, v in s.items()]

    student = df["FL153166220"].fillna(0)
    first_student = student[student > 0].index.min()
    reported = idx >= first_student
    classes = {
        "home_backed": (mort, df["FL155035015"], np.ones(len(idx), bool)),
        "vehicle_backed": (df["FL153166400"], df["FL155111005"], np.ones(len(idx), bool)),
        "uncollateralized": (df["FL153166100"].fillna(0) + student, None, reported),
        "other_nonrevolving": (df["FL153166205"].fillna(0), None, reported),
    }
    cc_rows, class_share, coverage = [], {}, {}
    for cls, (debt, coll, keep) in classes.items():
        debt = debt.where(keep)
        class_share[cls] = debt / scope
        if coll is not None:
            coverage[cls] = coll / debt.where(debt > 0)
        for t in idx:
            if pd.isna(debt[t]):
                continue
            cc_rows.append({"date": _d(t), "collateral_class": cls, "debt_musd": debt[t],
                            "collateral_value_musd": None if coll is None else coll[t],
                            "coverage_ratio": None if coll is None else coverage[cls][t],
                            "share_of_debt": class_share[cls][t]})

    metrics = {"public_share": res["share"]}
    metrics.update({f"share:{b}": s for b, s in bucket_share.items()})
    metrics.update({f"share:{c}": s for c, s in class_share.items()})
    metrics.update({f"coverage:{c}": s for c, s in coverage.items()})
    pos = {t: i for i, t in enumerate(idx)}
    cew = []
    for c in json.loads((SNAP / "dim_crisis.json").read_text()):
        t0 = pd.Timestamp(c["start_q"])
        if t0 not in pos:
            continue
        for name, s in metrics.items():
            v0 = s[t0]
            for off in range(-8, 17):
                i = pos[t0] + off
                if 0 <= i < len(idx) and not pd.isna(s.iloc[i]):
                    cew.append({"crisis_id": c["crisis_id"], "metric": name, "q_offset": off, "date": _d(idx[i]),
                                "value": s.iloc[i], "value_at_t0": v0,
                                "delta_from_t0": None if pd.isna(v0) else s.iloc[i] - v0})

    dim_rb = [{"risk_bucket": k, "is_public": bool(v["public"])} for k, v in cat["risk_buckets"].items()]
    return {"public_share": ps, "debt_by_risk_holder": dbh, "collateral_coverage": cc_rows,
            "crisis_event_window": cew, "dim_risk_bucket": dim_rb}


# ---------------------------------------------------------------- NY Fed workbook
def _qdate(label) -> str | None:
    m = re.fullmatch(r"\s*(\d{2}):?\s*Q([1-4])\s*", str(label))
    if not m:
        return None
    y, qn = 2000 + int(m.group(1)), int(m.group(2))
    return _d(pd.Timestamp(year=y, month=3 * qn, day=1) + pd.offsets.MonthEnd(0))


def _sheet_by_title(wb, title_re: str):
    for ws in wb.worksheets:
        for row in ws.iter_rows(min_row=1, max_row=3, values_only=True):
            if any(isinstance(c, str) and re.search(title_re, c, re.I) for c in row):
                return ws
    raise LookupError(f"no sheet titled /{title_re}/")


def _read_table(ws, colmap: dict, mult: float) -> dict[tuple[str, str], float]:
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows) if sum(isinstance(c, str) and c.strip().lower() in colmap for c in r) >= 4)
    hdr = rows[hdr_i]
    out = {}
    for r in rows[hdr_i + 1:]:
        d = _qdate(r[0]) if r and r[0] is not None else None
        if not d:
            continue
        for j, h in enumerate(hdr):
            key = h.strip().lower() if isinstance(h, str) else None
            if key in colmap and j < len(r) and isinstance(r[j], (int, float)):
                out[(d, colmap[key])] = float(r[j]) * mult
    return out


def nyfed_table(path: Path) -> list[dict]:
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    bal = _read_table(_sheet_by_title(wb, r"^total debt balance and its composition"), BAL_COLS, 1000.0)
    tr = _read_table(_sheet_by_title(wb, r"^new seriously delinquent\*? balances by loan type"), TRANS_COLS, 1.0)
    keys = sorted(set(bal) | set(tr))
    return [{"date": d, "loan_type": lt, "balance_busd": bal.get((d, lt)), "transition_serious_pct": tr.get((d, lt))}
            for d, lt in keys]


def ensure_nyfed(path: Path = NYFED_XLSX) -> Path | None:
    if path.exists():
        return path
    try:
        import requests
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {NYFED_URL} ...", file=sys.stderr)
        r = requests.get(NYFED_URL, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
        return path
    except Exception as e:  # no workbook -> NY Fed questions are NOT RUN, never PASS
        print(f"NY Fed workbook unavailable: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------- checks
def _fmt(v) -> str:
    return "-" if v is None else f"{v:.10g}"


def run_checks(df, cat, groups, res, Check, nyfed_path: Path | None = None, questions: Path = QUESTIONS) -> list:
    doc = yaml.safe_load(questions.read_text())
    qs = [q for q in doc["questions"] + doc.get("retired", []) if not q.get("refuse") and not q.get("register")]
    # retired questions (2026-11-05) stay checked so their register rows remain valid until they are removed
    raw = z1_tables(df, cat, groups, res)
    nyfed_path = nyfed_path or ensure_nyfed()
    if nyfed_path:
        raw["nyfed_by_type"] = nyfed_table(nyfed_path)
    snap = spec.load_snapshot()
    out = []
    for q in qs:
        cid, desc = f"E1-{q['id']}", f"E1 gold {q['id']} ({q['family']}/{q['difficulty']}): raw vs snapshot"
        bound = q["tolerance"] / 10
        try:
            s_val, s_q = spec.evaluate(q["check"], snap)
        except Exception as e:
            out.append(Check(cid, desc, "snapshot value", f"{type(e).__name__}: {e}", f"{bound:g}", "FAIL", "snapshot"))
            continue
        try:
            r_val, r_q = spec.evaluate(q["check"], raw)
        except KeyError as e:
            status = "NOT RUN" if "nyfed_by_type" in str(e) and not nyfed_path else "FAIL"
            out.append(Check(cid, desc, _fmt(s_val), f"raw: {type(e).__name__}: {e}", f"{bound:g}", status,
                             "raw rebuild could not evaluate this check"))
            continue
        ok = math.isclose(r_val, s_val, abs_tol=bound if bound else 1e-9) and r_q == s_q
        note = f"quarter {r_q}" if r_q else ""
        if r_q != s_q:
            note = f"quarter raw {r_q} vs snapshot {s_q}"
        out.append(Check(cid, desc, _fmt(s_val), _fmt(r_val), f"{bound:g}", "PASS" if ok else "FAIL", note))
    return out
