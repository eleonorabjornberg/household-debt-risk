#!/usr/bin/env python3
"""chart-from-sql: query result / CSV / JSON / DataFrame -> publication-quality static chart.

CLI:   uv run --project pipeline --with matplotlib python .claude/skills/chart-from-sql/scripts/chart.py \
         --file web/public/data/public_share.json --kind line --x date --y public_share --as-percent \
         --title "..." --source "Fed Z.1" --vintage 2026-09-11 --out DIR/name
API:   from chart import make_chart; make_chart(df, kind="line", x="date", y=["a"], ...)

Writes <out>.png, <out>.svg (+ -dark variants on request), <out>.alt.txt and <out>.json.
Alt text is computed from the plotted data only; nothing is hand-written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style  # noqa: E402

KINDS = ("line", "area", "bar", "hbar", "fan", "multiples")
STMT_TIMEOUT_MS = 15_000
SKILL_DIR = Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    for p in [SKILL_DIR, *SKILL_DIR.parents]:
        if (p / "CLAUDE.md").exists() or (p / ".git").exists():
            return p
    return Path.cwd()


DEFAULT_CRISIS = "web/public/data/dim_crisis.json"

# ----------------------------------------------------------------------------- data loading

_FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "create", "grant", "revoke", "truncate",
              "copy", "call", "do", "set", "reset", "vacuum", "analyze", "refresh", "lock", "listen",
              "notify", "into", "merge", "comment", "reindex", "cluster", "execute", "prepare",
              "begin", "commit", "rollback", "savepoint", "security", "import", "discard", "load")


def _strip_sql(sql: str) -> str:
    """Remove comments and the contents of string literals / quoted identifiers."""
    out, i, n = [], 0, len(sql)
    while i < n:
        two = sql[i:i + 2]
        if two == "--":
            j = sql.find("\n", i)
            i = n if j < 0 else j
        elif two == "/*":
            j = sql.find("*/", i + 2)
            if j < 0:
                raise ValueError("unterminated block comment")
            i = j + 2
            out.append(" ")
        elif sql[i] in "'\"":
            q = sql[i]
            j = i + 1
            while j < n:
                if sql[j] == q:
                    if sql[j + 1:j + 2] == q:
                        j += 2
                        continue
                    break
                j += 1
            else:
                raise ValueError("unterminated quoted string")
            out.append(q + q)
            i = j + 1
        elif sql[i] == "$" and re.match(r"\$[A-Za-z_]*\$", sql[i:]):
            raise ValueError("dollar-quoted strings are not allowed")
        else:
            out.append(sql[i])
            i += 1
    return "".join(out)


def check_select(sql: str) -> str:
    """Return the cleaned statement or raise ValueError unless it is one read-only SELECT/WITH query."""
    if not sql or not sql.strip():
        raise ValueError("empty SQL")
    body = _strip_sql(sql).strip()
    if body.endswith(";"):
        body = body[:-1].rstrip()
    if ";" in body:
        raise ValueError("only a single statement is allowed")
    first = re.match(r"\(*\s*([A-Za-z]+)", body)
    if not first or first.group(1).lower() not in ("select", "with"):
        raise ValueError("only SELECT (or WITH ... SELECT) statements are allowed")
    words = set(re.findall(r"[A-Za-z_]+", body.lower()))
    bad = sorted(w for w in _FORBIDDEN if w in words)
    if bad:
        raise ValueError(f"statement contains forbidden keyword(s): {', '.join(bad)} (read-only SELECT only)")
    return sql.strip().rstrip(";")


def run_sql(sql: str, dsn: str | None = None) -> pd.DataFrame:
    """Run one SELECT read-only (read-only session + transaction, 15 s statement timeout)."""
    check_select(sql)  # refuse before touching the network
    dsn = dsn or os.environ.get("DATABASE_URL_READONLY")
    if not dsn:
        raise RuntimeError("DATABASE_URL_READONLY is not set. Use --file with a CSV/JSON export instead, "
                           "or set it in the environment (never paste it into chat).")
    import psycopg
    with psycopg.connect(dsn, options=f"-c default_transaction_read_only=on -c statement_timeout={STMT_TIMEOUT_MS}",
                         autocommit=False) as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            cur.execute(sql.strip().rstrip(";"))
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
        conn.rollback()
    return pd.DataFrame(rows, columns=cols)


def load_file(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if p.suffix.lower() == ".json":
        obj = json.loads(p.read_text())
        if isinstance(obj, dict):
            lists = [v for v in obj.values() if isinstance(v, list)]
            obj = obj.get("data") or obj.get("rows") or (lists[0] if len(lists) == 1 else None)
            if obj is None:
                raise ValueError("JSON object without a single list of records")
        return pd.DataFrame(obj)
    raise ValueError(f"unsupported file type {p.suffix!r} (use .csv or .json)")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- time handling

_Q = re.compile(r"^(\d{4})\s*-?Q([1-4])$")


def parse_x(s: pd.Series) -> tuple[pd.Series, bool]:
    """Return (x, is_time). Quarter strings become quarter-end timestamps."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s, True
    if s.dtype == object or pd.api.types.is_string_dtype(s):
        txt = s.astype(str).str.strip()
        if txt.str.match(_Q).all():
            return pd.PeriodIndex(txt.str.replace("-", "").str.replace(" ", ""), freq="Q").to_timestamp(how="end").normalize().to_series(index=s.index), True
        if txt.str.match(r"^\d{4}-\d{2}-\d{2}").all():
            return pd.to_datetime(txt), True
    return s, False


def fmt_x(v, is_time: bool) -> str:
    if not is_time:
        return str(v)
    t = pd.Timestamp(v)
    if t == t + pd.offsets.QuarterEnd(0) and t.day == (t + pd.offsets.QuarterEnd(0)).day:
        return f"{t.year}Q{(t.month - 1) // 3 + 1}"
    return t.strftime("%Y-%m-%d")


def fmt_val(v: float, unit: str = "", decimals: int | None = None, signed: bool = False) -> str:
    d = decimals if decimals is not None else (0 if abs(v) >= 1000 else 1 if abs(v) >= 10 else 2)
    if round(v, d) == 0:
        v = 0.0  # no "-0.00"
    s = f"{v:+,.{d}f}" if signed else f"{v:,.{d}f}"
    u = unit.strip()
    if u == "%":
        return s + "%"
    return f"{s} {u}" if u else s


def load_recessions(path: str | Path | None = None) -> list[tuple[pd.Timestamp, pd.Timestamp, str]]:
    p = Path(path) if path else repo_root() / DEFAULT_CRISIS
    rows = json.loads(p.read_text())
    out = []
    for r in rows:
        if r.get("kind") == "nber_recession" and r.get("start_q") and r.get("end_q"):
            out.append((pd.Timestamp(r["start_q"]), pd.Timestamp(r["end_q"]), r.get("name", "")))
    return out


# ----------------------------------------------------------------------------- alt text

def _series_sentence(label: str, x: pd.Series, v: pd.Series, unit: str, is_time: bool, dec) -> str:
    m = v.notna()
    x, v = x[m].reset_index(drop=True), v[m].reset_index(drop=True)
    if v.empty:
        return f"{label} has no values."
    f, l = v.iloc[0], v.iloc[-1]
    verb = "rose" if l - f > 1e-12 else "fell" if f - l > 1e-12 else "was unchanged"
    if verb == "was unchanged":
        head = f"{label} was unchanged at {fmt_val(f, unit, dec)}"
    else:
        head = f"{label} {verb} from {fmt_val(f, unit, dec)} in {fmt_x(x.iloc[0], is_time)} to {fmt_val(l, unit, dec)} in {fmt_x(x.iloc[-1], is_time)}"
    imax, imin = int(v.idxmax()), int(v.idxmin())
    extra = []
    if imax not in (0, len(v) - 1):
        extra.append(f"high {fmt_val(v[imax], unit, dec)} in {fmt_x(x[imax], is_time)}")
    if imin not in (0, len(v) - 1):
        extra.append(f"low {fmt_val(v[imin], unit, dec)} in {fmt_x(x[imin], is_time)}")
    return head + (f" ({'; '.join(extra)})" if extra else "")


def build_alt(spec: dict) -> str:
    kind, unit, dec, is_time = spec["kind"], spec["unit"], spec.get("decimals"), spec["is_time"]
    kname = {"line": "Line chart", "area": "Stacked area chart", "bar": "Stacked bar chart",
             "hbar": "Horizontal bar chart", "fan": "Fan chart", "multiples": "Small-multiples line chart"}[kind]
    parts = []
    if kind == "hbar":
        d = spec["data"]  # DataFrame label,value
        pos, neg = d[d.value > 0], d[d.value < 0]
        parts.append(f"{kname} titled \"{spec['title']}\": {len(d)} bars of {spec['ylabel']}.")
        if len(pos):
            r = pos.loc[pos.value.idxmax()]
            parts.append(f"Largest positive: {r.label}, {fmt_val(r.value, unit, dec, True)}.")
        if len(neg):
            r = neg.loc[neg.value.idxmin()]
            parts.append(f"Largest negative: {r.label}, {fmt_val(r.value, unit, dec, True)}.")
        parts.append(f"The bars sum to {fmt_val(d.value.sum(), unit, dec, True)} "
                     f"({len(pos)} positive totalling {fmt_val(pos.value.sum(), unit, dec, True)}, "
                     f"{len(neg)} negative totalling {fmt_val(neg.value.sum(), unit, dec, True)}).")
        return " ".join(parts)
    x, wide, labels = spec["x"], spec["wide"], spec["labels"]
    n = len(x)
    parts.append(f"{kname} titled \"{spec['title']}\": {', '.join(labels[c] for c in wide.columns[:8])}"
                 f"{' and others' if wide.shape[1] > 8 else ''} ({spec['ylabel']}) by {spec['xname']}, "
                 f"{fmt_x(x.iloc[0], is_time)} to {fmt_x(x.iloc[-1], is_time)}, {n} observations.")
    cols = list(wide.columns)
    if kind == "fan":
        cols = cols[:1]
    for c in cols[:8]:
        parts.append(_series_sentence(labels[c], x, wide[c], unit, is_time, dec) + ".")
    if kind in ("area", "bar"):
        tot = wide.sum(axis=1, min_count=1)
        parts.append(_series_sentence("The stacked total", x, tot, unit, is_time, dec) + ".")
    if kind == "fan":
        last = len(x) - 1
        for lo, hi, lab in spec["bands"]:
            parts.append(f"At {fmt_x(x.iloc[last], is_time)} the {lab} runs from {fmt_val(spec['bandvals'][lo].iloc[last], unit, dec)} "
                         f"to {fmt_val(spec['bandvals'][hi].iloc[last], unit, dec)}.")
    if spec.get("recessions"):
        rs = spec["recessions"]
        parts.append(f"Shaded bands mark {len(rs)} NBER recession{'s' if len(rs) != 1 else ''} "
                     f"({fmt_x(rs[0][0], True)} to {fmt_x(rs[-1][1], True)}).")
    return " ".join(parts)


# ----------------------------------------------------------------------------- drawing helpers

def _nice(c: str) -> str:
    return c.replace("_", " ").capitalize()


def _spread(ys: list[float], gap: float) -> list[float]:
    """Push label positions apart (ys in any order) keeping the order by value."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = [ys[i] for i in order]
    for _ in range(100):
        moved = False
        for k in range(1, len(pos)):
            if pos[k] - pos[k - 1] < gap:
                d = (gap - (pos[k] - pos[k - 1])) / 2
                pos[k - 1] -= d
                pos[k] += d
                moved = True
        if not moved:
            break
    out = [0.0] * len(ys)
    for k, i in enumerate(order):
        out[i] = pos[k]
    return out


def _colors(cols, ink_series, color_map):
    cat = [c for c in cols if c not in ink_series]
    res, k = {}, 0
    for c in cols:
        if c in color_map:
            res[c] = (color_map[c], "-")
        elif c in ink_series:
            res[c] = ("INK", "-")
        elif k < len(style.CATEGORICAL):
            res[c] = (style.CATEGORICAL[k], "-")
            k += 1
        else:  # beyond six: muted grey, dashed (documented limit)
            res[c] = ("MUTED", (0, (4, 2)))
    return res


def _shade(ax, rec, t, xlim):
    for a, b, _ in rec:
        ax.axvspan(a, b, color=t["band"], alpha=t["band_alpha"], lw=0, zorder=0)


def _time_axis(ax, x):
    span = (x.max() - x.min()).days / 365.25
    step = 1 if span <= 10 else 5 if span <= 40 else 10
    ax.xaxis.set_major_locator(mdates.YearLocator(step))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def _fmt_axis(ax, unit, axis="y"):
    from matplotlib.ticker import FuncFormatter
    if unit == "%":
        f = FuncFormatter(lambda v, _: f"{v:g}%")
        (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)
    else:
        f = FuncFormatter(lambda v, _: f"{v:,.10g}")
        (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


# ----------------------------------------------------------------------------- main API

def make_chart(df: pd.DataFrame, *, kind: str, x: str, y, title: str, source: str, vintage: str, out,
               ylabel: str | None = None, unit: str | None = None, xlabel: str | None = None, subtitle: str | None = None,
               group: str | None = None, as_percent: bool = False, scale: float = 1.0,
               labels: dict | None = None, ink_series=(), bands=(), origin: str | None = None,
               recessions: bool | str | os.PathLike = False, mode: str = "light", ncols: int | None = None,
               sharey: bool = True, sort: bool = False, decimals: int | None = None,
               color_map: dict | None = None, formats=("png", "svg"),
               data_source: dict | None = None, width: float = 8.0, height: float = 4.8) -> dict:
    """Render a chart and write PNG/SVG + <out>.alt.txt + <out>.json. Returns the sidecar dict.

    unit: short unit for numbers in alt text, e.g. "pp" or "USD trillion" (with as_percent it is "%").
    y: column name or list. bands (fan): list of (lo_col, hi_col, label), outermost first.
    recessions: True (default dim_crisis.json) or a path. mode: 'light', 'dark' or 'both'.
    """
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    for nm, val in (("title", title), ("source", source), ("vintage", vintage)):
        if not val or not str(val).strip():
            raise ValueError(f"{nm} is required")
    if as_percent:
        decimals = 1 if decimals is None else decimals
        scale = scale * 100
        ylabel = ylabel or "Percent (%)"
    if not ylabel:
        raise ValueError("units required: pass ylabel (e.g. 'USD trillion') or as_percent=True")
    if df is None or len(df) == 0:
        raise ValueError("no rows to plot")
    ys = [y] if isinstance(y, str) else list(y)
    labels = dict(labels or {})
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    band_cols = [c for lo, hi, _ in bands for c in (lo, hi)]
    need = [x, *ys, *band_cols, *([group] if group else [])]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise KeyError(f"columns not in data: {missing}; have {list(df.columns)}")
    unit_alt = "%" if as_percent else (unit or "")  # short unit appended to numbers in alt text; ylabel is named once
    unit = unit_alt  # axis tick formatting

    spec: dict = {"kind": kind, "title": title, "ylabel": ylabel, "unit": unit_alt, "decimals": decimals,
                  "xname": x, "is_time": False}
    rec_used = []
    if kind == "hbar":
        d = df[[x, ys[0]] + ([group] if group else [])].copy()
        d.columns = ["label", "value"] + (["grp"] if group else [])
        d["value"] = pd.to_numeric(d["value"]) * scale
        d = d.dropna(subset=["value"])
        if sort:
            d = d.reindex(d.value.sort_values(ascending=False).index)
        d = d.reset_index(drop=True)
        spec["data"] = d
        n_rows = len(d)
    else:
        d = df[list(dict.fromkeys(need))].copy()
        xs, is_time = parse_x(d[x])
        d[x] = xs
        d = d.sort_values(x).reset_index(drop=True)
        if group:
            if len(ys) != 1:
                raise ValueError("with group, pass exactly one y column")
            wide = d.pivot(index=x, columns=group, values=ys[0]).sort_index()
            wide.columns = [str(c) for c in wide.columns]
            bandv = {}
        else:
            wide = d.set_index(x)[ys]
            bandv = {c: d.set_index(x)[c] * scale for c in band_cols}
        wide = wide.apply(pd.to_numeric, errors="coerce") * scale
        if kind in ("area", "bar") and (wide < 0).any().any():
            raise ValueError("stacked kinds need non-negative values; use hbar or line for signed series")
        xser = pd.Series(wide.index, name=x)
        spec.update(x=xser, wide=wide.reset_index(drop=True), is_time=is_time,
                    bandvals={k: v.reset_index(drop=True) for k, v in bandv.items()}, bands=list(bands))
        if recessions and is_time:
            rec_path = None if recessions is True else recessions
            rr = [r for r in load_recessions(rec_path) if r[1] >= xser.min() and r[0] <= xser.max()]
            rec_used = [(a, b, nm) for a, b, nm in rr]
            spec["recessions"] = rec_used
        elif recessions and not is_time:
            raise ValueError("recession shading needs a time x column")
        n_rows = len(wide)
        all_labels = {c: labels.get(c, _nice(c)) for c in wide.columns}
        spec["labels"] = all_labels
    alt = build_alt(spec)

    modes = ["light", "dark"] if mode == "both" else [mode]
    files = []
    for m in modes:
        suffix = "" if m == "light" else "-dark"
        fig = _render(spec, kind, m, title, subtitle, source, vintage, xlabel, ylabel, ink_series, color_map or {},
                      origin, ncols, sharey, rec_used, width, height, group, unit_alt)
        for f in formats:
            p = out.parent / f"{out.name}{suffix}.{f}"
            fig.savefig(p, dpi=200, format=f)
            files.append(p.name)
        plt.close(fig)
    out.with_suffix(".alt.txt").write_text(alt + "\n") if False else (out.parent / f"{out.name}.alt.txt").write_text(alt + "\n")
    ds = dict(data_source or {"type": "dataframe"})
    if ds.get("type") == "file" and ds.get("path") and Path(ds["path"]).exists():
        ds["sha256"] = _sha256(Path(ds["path"]))
    side = {"name": out.name, "kind": kind, "title": title, "source_line": source_line(source, vintage),
            "vintage": vintage, "data_source": ds, "row_count": int(n_rows),
            "x": x, "y": ys, "group": group, "units": ylabel, "scale_applied": scale,
            "recession_shading": bool(rec_used), "modes": modes, "files": files + [f"{out.name}.alt.txt", f"{out.name}.json"],
            "alt_text": alt, "generator": "chart-from-sql"}
    (out.parent / f"{out.name}.json").write_text(json.dumps(side, indent=2, default=str) + "\n")
    return side


def source_line(source: str, vintage: str) -> str:
    s = re.sub(r"^\s*source:\s*", "", source.strip(), flags=re.I).rstrip(".;, ")
    return f"Source: {s} (vintage {vintage}); {style.SOURCE_SUFFIX}"


def _render(spec, kind, mode, title, subtitle, source, vintage, xlabel, ylabel, ink_series, color_map, origin,
            ncols, sharey, rec, width, height, group, unit):
    t = style.theme(mode)
    ink, muted = t["ink"], t["muted"]
    with plt.rc_context(style.rc_params(mode)):
        tw = textwrap.wrap(title, 62) or [title]
        sw = textwrap.wrap(subtitle, 95) if subtitle else []
        src = textwrap.wrap(source_line(source, vintage), 120)
        H = height + 0.28 * (len(tw) - 1) + 0.2 * len(sw) + 0.16 * (len(src) - 1)
        fig = plt.figure(figsize=(width, H))
        top_in = 0.18 + 0.3 * len(tw) + 0.2 * len(sw)
        fig.text(0.015, 1 - 0.14 / H, "\n".join(tw), ha="left", va="top", fontsize=13.5, fontweight="bold", color=ink)
        if sw:
            fig.text(0.015, 1 - (0.14 + 0.3 * len(tw)) / H, "\n".join(sw), ha="left", va="top", fontsize=9.5, color=t["ink2"])
        fig.text(0.015, 0.14 / H, "\n".join(src), ha="left", va="bottom", fontsize=7.5, color=muted)
        bottom_in = 0.5 + 0.14 * len(src) + 0.2
        legend_in = 0.0
        if kind == "hbar":
            _hbar(fig, spec, t, top_in, bottom_in, H, xlabel, ylabel, color_map, unit)
        elif kind == "multiples":
            _multiples(fig, spec, t, top_in, bottom_in, H, xlabel, ylabel, ink_series, color_map, rec, ncols, sharey, unit)
        else:
            _single(fig, spec, kind, t, top_in, bottom_in, H, xlabel, ylabel, ink_series, color_map, rec, origin, unit)
    return fig


def _single(fig, spec, kind, t, top_in, bottom_in, H, xlabel, ylabel, ink_series, color_map, rec, origin, unit):
    x, wide, labels, is_time = spec["x"], spec["wide"], spec["labels"], spec["is_time"]
    cols = list(wide.columns)
    n = len(cols)
    end_labels = kind == "line" and n >= 2  # direct end labels replace the legend (identity never colour-alone)
    nleg = (0 if end_labels else (n if kind != "fan" else len(spec["bands"]) + 1 if n >= 1 else 0)) + (1 if rec else 0)
    ncol_leg = min(max(nleg, 1), 3 if kind == "area" else 4)
    legend_h = 0.28 * (-(-nleg // ncol_leg)) if (nleg >= 2 or (rec and nleg >= 1) or kind == "fan") else 0.0
    right = 0.77 if end_labels else 0.97
    ax = fig.add_axes([0.085, bottom_in / H, right - 0.085, 1 - (top_in + legend_h + 0.05) / H - bottom_in / H])
    cmap = _colors(cols, set(ink_series), color_map)
    xv = x.values if is_time else x.values
    real = lambda c: {"INK": t["ink"], "MUTED": t["muted"]}.get(cmap[c][0], cmap[c][0])  # noqa: E731
    handles = []
    if rec:
        _shade(ax, rec, t, None)
    if kind == "line":
        ends = []
        for c in cols:
            lw = 2.6 if c in ink_series else 2.0
            ax.plot(xv, wide[c].values, color=real(c), ls=cmap[c][1], lw=lw, label=labels[c], solid_capstyle="round")
            v = wide[c].dropna()
            if len(v):
                ends.append((c, x[v.index[-1]], v.iloc[-1]))
        if end_labels:
            lo, hi = ax.get_ylim()
            ys_adj = _spread([e[2] for e in ends], (hi - lo) * 0.045)
            for (c, xe, ve), ya in zip(ends, ys_adj):
                ax.annotate(labels[c], xy=(xe, ve), xytext=(1.01, ya), textcoords=("axes fraction", "data"),
                            xycoords="data", fontsize=8.5, color=t["ink2"], va="center",
                            annotation_clip=False,
                            arrowprops=dict(arrowstyle="-", color=t["axis"], lw=0.6, shrinkA=0, shrinkB=2))
        handles = ([], []) if end_labels else ax.get_legend_handles_labels()
    elif kind == "area":
        ax.stackplot(xv, [wide[c].fillna(0).values for c in cols], colors=[real(c) for c in cols],
                     labels=[labels[c] for c in cols], edgecolors=t["paper"], linewidth=0.6)
        handles = ax.get_legend_handles_labels()
    elif kind == "bar":
        step = np.median(np.diff(mdates.date2num(xv))) if is_time and len(xv) > 1 else 1
        w = 0.8 * step if is_time else 0.8
        pos = mdates.date2num(xv) if is_time else np.arange(len(xv))
        bottom = np.zeros(len(xv))
        for c in cols:
            v = wide[c].fillna(0).values
            ax.bar(pos if is_time else np.arange(len(xv)), v, width=w, bottom=bottom, color=real(c), label=labels[c],
                   edgecolor=t["paper"], linewidth=0.6)
            bottom += v
        if is_time:
            ax.xaxis_date()
        else:
            ax.set_xticks(np.arange(len(xv)))
            ax.set_xticklabels([str(v) for v in xv])
        handles = ax.get_legend_handles_labels()
    elif kind == "fan":
        col = style.CATEGORICAL[0] if "point" not in color_map else color_map["point"]
        bands = spec["bands"]
        al = np.linspace(0.16, 0.34, max(len(bands), 1))
        for (lo, hi, lab), a in zip(bands, al):
            ax.fill_between(xv, spec["bandvals"][lo].values, spec["bandvals"][hi].values, color=col, alpha=a, lw=0,
                            label=lab)
        ax.plot(xv, wide[cols[0]].values, color=col, lw=2.2, label=labels[cols[0]])
        if origin:
            ts = pd.Timestamp(origin)
            ax.axvline(ts, color=t["ink2"], lw=1, ls=(0, (4, 3)))
            ax.annotate("forecast origin", xy=(ts, 1), xycoords=("data", "axes fraction"), xytext=(4, -10),
                        textcoords="offset points", fontsize=8, color=t["ink2"])
        handles = ax.get_legend_handles_labels()
    if is_time and kind != "bar":
        ax.set_xlim(xv.min(), xv.max())
    if is_time:
        _time_axis(ax, x)
    ax.set_xlabel(xlabel or ("Year" if is_time else spec["xname"]))
    ax.set_ylabel(ylabel)
    _fmt_axis(ax, unit)
    if kind in ("area", "bar", "line") and wide.min().min() >= 0:
        ax.set_ylim(bottom=0)
    ax.margins(x=0.01 if kind != "bar" else 0.02)
    hl, lb = handles if handles else ([], [])
    hl, lb = list(hl), list(lb)
    if rec:
        hl.append(Patch(facecolor=t["band"], alpha=t["band_alpha"] * 2.2, lw=0))
        lb.append(style.CRISIS_LABEL)
    if hl and (len(hl) >= 2 or kind == "fan"):
        ax.legend(hl, lb, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol_leg,
                  handlelength=1.6, columnspacing=1.4, borderaxespad=0.4)
    return ax


def _multiples(fig, spec, t, top_in, bottom_in, H, xlabel, ylabel, ink_series, color_map, rec, ncols, sharey, unit):
    x, wide, labels, is_time = spec["x"], spec["wide"], spec["labels"], spec["is_time"]
    cols = list(wide.columns)
    n = len(cols)
    nc = ncols or min(3, n)
    nr = -(-n // nc)
    gs = fig.add_gridspec(nr, nc, left=0.085, right=0.97, bottom=bottom_in / H, top=1 - (top_in + 0.05) / H,
                          hspace=0.6, wspace=0.18 if sharey else 0.3)
    cmap = _colors(cols, set(ink_series), color_map)
    ymin, ymax = np.nanmin(wide.values), np.nanmax(wide.values)
    for i, c in enumerate(cols):
        ax = fig.add_subplot(gs[i // nc, i % nc])
        if rec:
            _shade(ax, rec, t, None)
        col = {"INK": t["ink"], "MUTED": t["muted"]}.get(cmap[c][0], cmap[c][0])
        ax.plot(x.values, wide[c].values, color=col, lw=1.8)
        ax.set_title(labels[c], loc="left", fontsize=9.5, color=t["ink"], fontweight="bold")
        if sharey:
            pad = (ymax - ymin) * 0.05
            ax.set_ylim(min(0, ymin) if ymin >= 0 else ymin - pad, ymax + pad)
        if is_time:
            ax.set_xlim(x.min(), x.max())
            _time_axis(ax, x)
            ax.xaxis.set_major_locator(mdates.YearLocator(max(1, int(((x.max() - x.min()).days / 365.25) // 3) or 1)))
        _fmt_axis(ax, unit)
        ax.tick_params(labelsize=8)
        if i % nc == 0:
            ax.set_ylabel(ylabel, fontsize=8.5)
        if i // nc == nr - 1 or i + nc >= n:
            ax.set_xlabel(xlabel or ("Year" if is_time else spec["xname"]), fontsize=8.5)
        if sharey and i % nc != 0:
            ax.tick_params(labelleft=False)
    if rec:
        fig.legend([Patch(facecolor=t["band"], alpha=t["band_alpha"] * 2.2, lw=0)], [style.CRISIS_LABEL],
                   loc="upper right", bbox_to_anchor=(0.97, 1 - top_in / H), frameon=False, fontsize=8.5)


def _hbar(fig, spec, t, top_in, bottom_in, H, xlabel, ylabel, color_map, unit):
    d = spec["data"]
    n = len(d)
    grp = "grp" in d.columns
    cats = list(dict.fromkeys(d["grp"])) if grp else []
    if grp:
        if set(cats) <= {"public", "private"}:
            cm = {"public": style.PUBLIC, "private": style.PRIVATE, **color_map}
            cats = [c for c in ("public", "private") if c in cats]
        else:
            cm = {c: style.CATEGORICAL[i % 6] for i, c in enumerate(cats)}
            cm.update(color_map)
        colors = [cm[g] for g in d["grp"]]
    else:
        colors = [style.CATEGORICAL[0]] * n
    legend_h = 0.28 if grp else 0.0
    ax = fig.add_axes([0.30, bottom_in / H, 0.66, 1 - (top_in + legend_h + 0.05) / H - bottom_in / H])
    ypos = np.arange(n)[::-1]
    ax.barh(ypos, d["value"].values, color=colors, height=0.62)
    ax.axvline(0, color=t["ink2"], lw=1)
    ax.set_yticks(ypos)
    ax.set_yticklabels([textwrap.fill(str(s), 34) for s in d["label"]], fontsize=9, color=t["ink"])
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    lo, hi = d["value"].min(), d["value"].max()
    span = (max(hi, 0) - min(lo, 0)) or 1
    ax.set_xlim(min(lo, 0) - span * 0.16 if lo < 0 else 0, max(hi, 0) + span * 0.16)
    for yp, v in zip(ypos, d["value"].values):
        ax.annotate(fmt_val(v, "" if unit != "%" else "%", spec.get("decimals") if spec.get("decimals") is not None else 2, True),
                    xy=(v, yp), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                    ha="left" if v >= 0 else "right", va="center", fontsize=8.5, color=t["ink"])
    ax.set_xlabel(xlabel or ylabel)
    _fmt_axis(ax, unit, "x")
    if grp:
        hl = [Patch(facecolor=cm[c]) for c in cats]
        ax.legend(hl, [str(c).capitalize() for c in cats], loc="lower left", bbox_to_anchor=(-0.45, 1.0), ncol=len(cats),
                  handlelength=1.2, borderaxespad=0.4)


# ----------------------------------------------------------------------------- CLI

def _kv(s: str | None) -> dict:
    out = {}
    for part in (s or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="CSV or JSON path")
    src.add_argument("--sql", help="one SELECT, run read-only via DATABASE_URL_READONLY")
    ap.add_argument("--kind", required=True, choices=KINDS)
    ap.add_argument("--x", required=True)
    ap.add_argument("--y", required=True, help="column, or comma-separated columns")
    ap.add_argument("--group", help="long format: column whose values become series")
    ap.add_argument("--as-percent", action="store_true", help="values are fractions: multiply by 100, unit %%")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply values (e.g. 1e-6 for USD million -> USD trillion)")
    ap.add_argument("--ylabel", help="axis label with units, e.g. 'USD trillion'")
    ap.add_argument("--xlabel")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle")
    ap.add_argument("--source", required=True, help="e.g. 'Fed Z.1 Financial Accounts, series FL...'")
    ap.add_argument("--vintage", required=True, help="data vintage, e.g. 2026-09-11")
    ap.add_argument("--out", required=True, help="DIR/name (no extension)")
    ap.add_argument("--mode", default="light", choices=("light", "dark", "both"))
    ap.add_argument("--recessions", nargs="?", const=True, default=False, metavar="CRISIS_JSON",
                    help="shade NBER recessions (default file web/public/data/dim_crisis.json)")
    ap.add_argument("--labels", help="col=Label,col2=Label2")
    ap.add_argument("--ink-series", default="", help="comma list of columns drawn in ink (e.g. total)")
    ap.add_argument("--band", action="append", default=[], help="fan band lo_col:hi_col:label (outermost first)")
    ap.add_argument("--origin", help="fan chart forecast origin date")
    ap.add_argument("--ncols", type=int)
    ap.add_argument("--free-y", action="store_true", help="small multiples: independent y axes")
    ap.add_argument("--sort", action="store_true", help="hbar: sort descending by value")
    ap.add_argument("--decimals", type=int)
    ap.add_argument("--formats", default="png,svg")
    a = ap.parse_args(argv)

    root = Path.cwd()
    if a.file:
        df = load_file(a.file)
        ds = {"type": "file", "path": a.file}
    else:
        df = run_sql(a.sql)
        ds = {"type": "sql", "query": a.sql, "role": "DATABASE_URL_READONLY"}
    bands = []
    for b in a.band:
        lo, hi, lab = (b.split(":", 2) + [""])[:3]
        bands.append((lo, hi, lab or f"{lo}-{hi}"))
    side = make_chart(df, kind=a.kind, x=a.x, y=[s for s in a.y.split(",") if s], title=a.title, source=a.source,
                      vintage=a.vintage, out=a.out, ylabel=a.ylabel, xlabel=a.xlabel, subtitle=a.subtitle,
                      group=a.group, as_percent=a.as_percent, scale=a.scale, labels=_kv(a.labels),
                      ink_series=[s for s in a.ink_series.split(",") if s], bands=bands, origin=a.origin,
                      recessions=a.recessions, mode=a.mode, ncols=a.ncols, sharey=not a.free_y, sort=a.sort,
                      decimals=a.decimals, formats=tuple(a.formats.split(",")), data_source=ds)
    print("wrote:", ", ".join(side["files"]))
    print("alt:", side["alt_text"])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
