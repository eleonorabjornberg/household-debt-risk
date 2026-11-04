#!/usr/bin/env python3
"""Write the "what moved" note comparing two Fed Z.1 vintages (PLAN task 0.8).

    uv run --project pipeline python .claude/skills/z1-release-update/scripts/what_moved.py \
        --prev PREV.zip --curr CURR.zip [--results validation/results.json] [--out PATH]

Reads two zips (the long FRB_Z1_csv.zip or the per-table z1_csv_files.zip), recomputes the public share
the same way validation/run.py does, and writes a markdown note. Default output:
data/releases/<vintage>/what_moved.md (data/ is gitignored). It never edits any number or data file other
than its own output. It does not import hhdebt; it loads validation/zparse.py by file path.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[4]
FIRST_Q = pd.Timestamp("1952-03-31")  # same start as validation/run.py
THR_PP = 0.05       # revision threshold, public share, percentage points
THR_MUSD = 1000.0   # revision threshold, scope total or public $, $ millions
TOP_N = 10


def load_zparse(root: Path = ROOT):
    spec = importlib.util.spec_from_file_location("zparse", root / "validation" / "zparse.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------------------------
def load_catalog(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text())


def catalog_parts(cat: dict):
    rows = [s for s in cat["series"] if s["source"] == "z1"]
    public = {k for k, v in cat["risk_buckets"].items() if v["public"]}
    mh = [s for s in rows if s["role"] == "mortgage_holder"]
    ch = [s for s in rows if s["role"] == "cc_holder"]
    ids = sorted({s["id"] for s in rows if s["role"] in ("mortgage_holder", "cc_holder", "total")}
                 | {"FL893065105", "FL153165105", "FL153166000", "FL154104015"})
    return mh, ch, public, ids


def zip_vintage(path: Path) -> datetime:
    """Timestamp of Z1.csv inside the long zip, else the newest member of a per-table zip."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "Z1.csv" in names:
            return datetime(*z.getinfo("Z1.csv").date_time)
        return max(datetime(*i.date_time) for i in z.infolist() if not i.is_dir())


def load_vintage(zp, path: Path, ids) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        long_fmt = "Z1.csv" in z.namelist()
    if long_fmt:
        ser = zp.load_z1_zip(path, ids)
    else:
        ser, _conflicts = zp.load_table_zip(path, ids)
    df = pd.DataFrame(ser).sort_index()
    df.index = pd.to_datetime(df.index)
    if "FL154104015" not in df.columns:
        df["FL154104015"] = df["FL153165105"] + df["FL153166000"]
    return df


def compute(df: pd.DataFrame, mh, ch, public) -> pd.DataFrame:
    """scope, public $ and share, plus $ by risk bucket ('b_<bucket>'). Same method as validation/run.py."""
    out = pd.DataFrame(index=df.index)
    out["scope"] = df["FL154104015"]
    ratio = df["FL153165105"] / df["FL893065105"]
    parts: dict[str, list] = {}
    for s in mh:
        parts.setdefault(s["risk_bucket"], []).append(df[s["id"]] * ratio)
    for s in ch:
        parts.setdefault(s["risk_bucket"], []).append(df[s["id"]])
    for b, lst in parts.items():
        out["b_" + b] = pd.concat(lst, axis=1).sum(axis=1, min_count=len(lst))
    pub_cols = ["b_" + b for b in parts if b in public]
    out["public"] = out[pub_cols].sum(axis=1, min_count=len(pub_cols))
    out["share"] = out["public"] / out["scope"]
    return out


# ---------------------------------------------------------------------------------------------
# formatting (as on the site: one decimal for %, two for $T)
# ---------------------------------------------------------------------------------------------
def qlabel(ts) -> str:
    ts = pd.Timestamp(ts)
    return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"


def fpct(x) -> str:
    return "n/a" if pd.isna(x) else f"{x * 100:.1f}%"


def ftn(musd) -> str:
    return "n/a" if pd.isna(musd) else f"${musd / 1e6:.2f}T"


def fpp(x) -> str:
    if pd.isna(x):
        return "n/a"
    v = round(x * 100, 1)
    return "0.0 pp" if v == 0 else f"{v:+.1f} pp"


def ftn_d(musd) -> str:
    if pd.isna(musd):
        return "n/a"
    v = round(musd / 1e6, 2)
    return "$0.00T" if v == 0 else f"{'+' if v > 0 else '-'}${abs(v):.2f}T"


def fmm(musd) -> str:
    return "n/a" if pd.isna(musd) else f"{musd:+,.0f}"


def back(idx, ts, n):
    """The quarter n steps before ts in idx, or None."""
    pos = idx.get_loc(ts)
    return idx[pos - n] if pos >= n else None


# ---------------------------------------------------------------------------------------------
# note
# ---------------------------------------------------------------------------------------------
def revisions_table(res_prev, res_cur, thr_pp, thr_musd, top_n):
    valid_prev = res_prev.dropna(subset=["share"]).index
    common = res_cur.dropna(subset=["share"]).index.intersection(valid_prev)
    common = common[common >= FIRST_Q]
    d = pd.DataFrame({
        "share_prev": res_prev.loc[common, "share"], "share_cur": res_cur.loc[common, "share"],
        "d_share": res_cur.loc[common, "share"] - res_prev.loc[common, "share"],
        "d_scope": res_cur.loc[common, "scope"] - res_prev.loc[common, "scope"],
        "d_public": res_cur.loc[common, "public"] - res_prev.loc[common, "public"],
    })
    d["score"] = pd.concat([d["d_share"].abs() * 100 / thr_pp, d["d_scope"].abs() / thr_musd,
                            d["d_public"].abs() / thr_musd], axis=1).max(axis=1)
    over = d[d["score"] >= 1.0].sort_values("score", ascending=False)
    return d, over.head(top_n), len(over)


def build_note(res_prev, res_cur, prev_label, cur_label, results=None, thr_pp=THR_PP, thr_musd=THR_MUSD,
               top_n=TOP_N) -> str:
    cur = res_cur.dropna(subset=["share"])
    prev = res_prev.dropna(subset=["share"])
    last = cur.index[-1]
    new_q = [t for t in cur.index if t not in prev.index and t > prev.index[-1]]
    L = [f"# What moved: {prev_label} to {cur_label}", "",
         f"Previous vintage: {prev_label} (latest quarter {qlabel(prev.index[-1])}). "
         f"Current vintage: {cur_label} (latest quarter {qlabel(last)}). "
         "Scope is 1-4 family mortgages plus consumer credit of households and nonprofits; "
         "public = federal, GSE and agency pools, state and local holders. "
         "Computed from the raw Z.1 files; figures are not edited.", ""]

    L += ["## New quarters", ""]
    L.append(", ".join(qlabel(t) for t in new_q) if new_q else "None: the current vintage ends in the same quarter as the previous one.")
    L.append("")

    # headline
    L += [f"## Headline, {qlabel(last)}", "",
          "| Measure | Level | q/q | y/y |", "|---|---|---|---|"]
    q1, y1 = back(cur.index, last, 1), back(cur.index, last, 4)

    def delta(col, fmt):
        return [fmt(cur.loc[last, col] - cur.loc[b, col]) if b is not None else "n/a" for b in (q1, y1)]
    L.append("| Public share of scope | " + fpct(cur.loc[last, "share"]) + " | " + " | ".join(delta("share", fpp)) + " |")
    L.append("| Public debt | " + ftn(cur.loc[last, "public"]) + " | " + " | ".join(delta("public", ftn_d)) + " |")
    L.append("| Scope total | " + ftn(cur.loc[last, "scope"]) + " | " + " | ".join(delta("scope", ftn_d)) + " |")
    L.append("")
    if q1 is not None:
        L.append(f"q/q is against {qlabel(q1)}" + (f", y/y against {qlabel(y1)}" if y1 is not None else "") +
                 ", both as published in the current vintage (so they include revisions).")
        L.append("")

    # buckets
    bcols = [c for c in cur.columns if c.startswith("b_")]
    L += [f"## Risk buckets, share of scope, {qlabel(last)}", "",
          "| Bucket | Share | q/q | y/y |", "|---|---|---|---|"]
    for c in bcols:
        sh = cur[c] / cur["scope"]
        row = [fpct(sh[last])]
        for b in (q1, y1):
            row.append(fpp(sh[last] - sh[b]) if b is not None else "n/a")
        L.append(f"| {c[2:]} | " + " | ".join(row) + " |")
    L.append("")

    # revisions
    d, top, n_over = revisions_table(res_prev, res_cur, thr_pp, thr_musd, top_n)
    L += ["## Revisions to history", "",
          f"{len(d)} quarters are in both vintages ({qlabel(d.index[0])} to {qlabel(d.index[-1])}). "
          f"{n_over} moved by at least {thr_pp} pp of public share or ${thr_musd:,.0f}M of scope or public debt. "
          f"The {min(top_n, n_over)} largest, ranked by the biggest move relative to those thresholds:", ""]
    if n_over:
        L += ["| Quarter | Share prev | Share now | Change | Scope change ($M) | Public change ($M) |", "|---|---|---|---|---|---|"]
        for t, r in top.iterrows():
            L.append(f"| {qlabel(t)} | {r.share_prev * 100:.2f}% | {r.share_cur * 100:.2f}% | {r.d_share * 100:+.2f} pp | "
                     f"{fmm(r.d_scope)} | {fmm(r.d_public)} |")
    else:
        L.append("No quarter crosses the thresholds.")
    L.append("")
    L.append(f"Largest absolute share revision: {d['d_share'].abs().max() * 100:.3f} pp "
             f"in {qlabel(d['d_share'].abs().idxmax())}. (Revision table uses two decimals so small moves are visible.)")
    L.append("")

    # validation
    L += ["## Validation flags", ""]
    if results is None:
        L.append("No validation results supplied (pass `--results validation/results.json`). Run validation before using this note.")
    else:
        meta, checks = results.get("meta", {}), results.get("checks", [])
        if meta.get("latest") and meta["latest"] != qlabel(last):
            L.append(f"WARNING: results.json is for {meta['latest']}, not {qlabel(last)}; re-run validation.")
            L.append("")
        s = results.get("summary", {})
        L.append("Summary: " + ", ".join(f"{v} {k}" for k, v in s.items()) + ".")
        L.append("")
        bad = [c for c in checks if c["status"] != "PASS"]
        if bad:
            L += ["| Check | Status | Observed |", "|---|---|---|"]
            for c in bad:
                L.append(f"| {c['id']} {c['description']} | {c['status']} | {c['observed']} |")
            L.append("")
        else:
            L += ["All checks PASS.", ""]
        cutoff = back(cur.index, last, 4)
        jumps = [j for j in results.get("unexplained_jumps", []) if pd.Timestamp(j["date"]) >= (cutoff or last)]
        total = len(results.get("unexplained_jumps", []))
        L.append(f"Unexplained component-share jumps (E8): {total} in the whole history, {len(jumps)} in the last five quarters"
                 + (":" if jumps else "."))
        for j in jumps:
            L.append(f"- {j['series']} {j['quarter']}: {j['delta_pp']:+.1f} pp (robust z {j['robust_z']:.1f})")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prev", type=Path, required=True, help="previous vintage zip (long or per-table)")
    ap.add_argument("--curr", type=Path, required=True, help="current vintage zip (long or per-table)")
    ap.add_argument("--results", type=Path, default=None, help="validation/results.json of the current run")
    ap.add_argument("--out", type=Path, default=None, help="default data/releases/<vintage>/what_moved.md")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--thr-pp", type=float, default=THR_PP)
    ap.add_argument("--thr-musd", type=float, default=THR_MUSD)
    ap.add_argument("--top", type=int, default=TOP_N)
    a = ap.parse_args(argv)

    zp = load_zparse(a.root)
    mh, ch, public, ids = catalog_parts(load_catalog(a.root / "pipeline" / "series_catalog.yaml"))
    v_prev, v_cur = zip_vintage(a.prev), zip_vintage(a.curr)
    res_prev = compute(load_vintage(zp, a.prev, ids), mh, ch, public)
    res_cur = compute(load_vintage(zp, a.curr, ids), mh, ch, public)
    results = json.loads(a.results.read_text()) if a.results and a.results.exists() else None
    note = build_note(res_prev, res_cur, v_prev.date().isoformat(), v_cur.date().isoformat(), results,
                      a.thr_pp, a.thr_musd, a.top)
    out = a.out or a.root / "data" / "releases" / v_cur.date().isoformat() / "what_moved.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(note)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
