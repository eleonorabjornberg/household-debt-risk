#!/usr/bin/env python3
"""claim-check: trace every number in a sentence, paragraph or file to claims/register.csv and recompute it.

    uv run --project pipeline python .claude/skills/claim-check/scripts/claim_check.py "text"
    ... claim_check.py --file README.md --line 10
    ... claim_check.py --file README.md            # whole file
    ... add --json for machine output

Read-only: never edits the register, validation/results.json, analysis files or copy.
Exit 0: no MISMATCH and no UNTRACED (AMBIGUOUS / NOT RECOMPUTABLE are printed but do not fail); 1: any
MISMATCH or UNTRACED; 2: usage error.

Number tokens, normalisation and register parsing are reused from claims/check_register.py.

Verdicts per token
  MATCH            register display, register value and an independent recompute all agree at the token's precision
  MISMATCH         register value or recompute rounds (ROUND_HALF_UP) to something other than the token
  UNTRACED         no register row prints this token
  AMBIGUOUS        several rows print this token and no `locations` entry pins the file:line
  NOT RECOMPUTABLE a row exists but no recompute path could be run (reason given); never guessed

Recompute paths, in order (first that yields a number wins; paths that cannot run are listed in the reason)
  1. validation/results.json check named in the row's check_id: number parsed from the check's `observed`.
  2. a results.json key in `computation`: `analysis/results.json a.b.c`, `a[2007Q4].c` (list element whose first
     value is 2007Q4), `-> results.json k` under research/<task>/, and `results.json key: expr` (+ - * / over
     that object's numeric fields).
  3. a committed CSV (`X.csv col (KEY)`, `X.csv (KEY col)`, `X.csv col KEY`, `X.csv col max`) or a JSON list of
     records (`sum(col) where k='v' and date='D'`, `min|max col for date >= D`, `sum of col for date D in X.json`).
Source numbers keep their printed decimals, so each recompute is an interval (value +/- half a unit in the last
digit); a token is MATCH if it is reachable inside that interval and says so when it is an edge case.
Units: shares stored as fractions are compared as percent for `%` tokens; usd_tn/usd_bn convert between $T/$B/$M;
results.json numbers are taken as exact (JSON drops trailing zeros); CSV and check numbers as printed. Sources named *musd / *busd / *usd_bn are converted to the row's unit. Signs are not verified (the register
normalisation drops them); a sign that disagrees with the register value is only noted.
"""
from __future__ import annotations

import argparse
import ast
import csv
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def _load_check_register(root: Path):
    spec = importlib.util.spec_from_file_location("check_register", root / "claims" / "check_register.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("check_register", mod)
    spec.loader.exec_module(mod)
    return mod


CR = _load_check_register(ROOT)
TOKEN_RE, normalize = CR.TOKEN_RE, CR.normalize
SIGNS = "+-−–"


# ------------------------------------------------------------------ intervals
@dataclass(frozen=True)
class Iv:
    lo: Decimal
    hi: Decimal

    @staticmethod
    def exact(v) -> "Iv":
        v = Decimal(v)
        return Iv(v, v)

    @staticmethod
    def printed(text: str) -> "Iv":
        """A number as printed: +/- half a unit in its last digit."""
        d = Decimal(text.replace(",", ""))
        h = Decimal(5).scaleb(d.as_tuple().exponent - 1)
        return Iv(d - h, d + h)

    def _c(self, o):
        return o if isinstance(o, Iv) else Iv.exact(o)

    def __add__(self, o):
        o = self._c(o); return Iv(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = self._c(o); return Iv(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = self._c(o); c = [a * b for a in (self.lo, self.hi) for b in (o.lo, o.hi)]; return Iv(min(c), max(c))

    def __truediv__(self, o):
        o = self._c(o)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("interval contains 0")
        c = [a / b for a in (self.lo, self.hi) for b in (o.lo, o.hi)]; return Iv(min(c), max(c))

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def scale(self, f) -> "Iv":
        return self * Iv.exact(f)

    @property
    def mid(self) -> Decimal:
        return (self.lo + self.hi) / 2


def round_hu(v: Decimal, places: int) -> Decimal:
    return v.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


# ------------------------------------------------------------------ tokens
@dataclass
class Tok:
    text: str
    line: int
    kind: str          # pct pp x th money pval dec nofm
    number: Decimal | None
    places: int
    money: str = ""    # T B M or $ (bare dollars)
    sign: str = ""


def parse_token(m: re.Match, line: str, lineno: int) -> Tok:
    text = m.group(0).strip()
    start = m.start()
    sign = line[start - 1] if start > 0 and line[start - 1] in SIGNS else ""
    sign = {"−": "-", "–": "-"}.get(sign, sign)
    g = m.lastgroup
    if g == "nofm":
        return Tok(text, lineno, "nofm", None, 0, sign=sign)
    if g == "pval":
        n = re.search(r"\d*\.\d+", text).group(0)
        return Tok(text, lineno, "pval", Decimal(n), len(n.split(".")[1]), sign=sign)
    n = re.search(r"\d[\d,]*(?:\.\d+)?", text).group(0)
    places = len(n.split(".")[1]) if "." in n else 0
    val = Decimal(n.replace(",", ""))
    if g == "money":
        suf = text[text.index(n) + len(n):].strip().lower()
        money = {"t": "T", "trillion": "T", "b": "B", "billion": "B", "m": "M", "million": "M"}.get(suf, "$")
        return Tok(text, lineno, "money", val, places, money, sign)
    if g == "unit":
        suf = text[text.index(n) + len(n):].strip().lower()
        kind = "pct" if suf == "%" else "pp" if suf in ("pp", "pts", "point", "points") else "x" if suf in ("×", "x") else "th"
        return Tok(text, lineno, kind, val, places, sign=sign)
    return Tok(text, lineno, "dec", val, places, sign=sign)


def tokens_in_line(line: str, lineno: int) -> list[Tok]:
    return [parse_token(m, line, lineno) for m in TOKEN_RE.finditer(line)]


def row_to_token_units(unit: str, tok: Tok, v):
    """Convert a value in a register row's unit into the units the token is printed in; None if unsupported."""
    k = tok.kind
    if k == "pct":
        return v * 100 if unit in ("share", "pvalue") else None
    if k == "pp":
        return v if unit == "pp" else None
    if k == "x":
        return v if unit == "ratio" else None
    if k == "th":
        return v if unit == "pct_rank" else None
    if k in ("pval", "dec"):
        return v if unit in ("pvalue", "ratio", "share", "pp", "count") else None
    if k == "money":
        tbl = {("usd_tn", "T"): 1, ("usd_tn", "B"): 1000, ("usd_tn", "M"): 10**6,
               ("usd_bn", "T"): Decimal("0.001"), ("usd_bn", "B"): 1, ("usd_bn", "M"): 1000}
        f = tbl.get((unit, tok.money))
        return None if f is None else v * f
    return None


# ------------------------------------------------------------------ context
@dataclass
class Ctx:
    root: Path = ROOT
    register: Path | None = None
    results: Path | None = None
    rows: list = field(default_factory=list)
    checks: dict = field(default_factory=dict)
    _cache: dict = field(default_factory=dict)

    def __post_init__(self):
        self.register = self.register or self.root / "claims" / "register.csv"
        self.results = self.results or self.root / "validation" / "results.json"
        _, self.rows, _ = CR.load_register(self.register)
        if self.results.is_file():
            self.checks = {c["id"]: c for c in json.loads(self.results.read_text())["checks"]}
        for r in self.rows:
            r["_norms"] = CR.register_tokens([r.get("display", "")])
            r["_locs"] = {x.strip() for x in r.get("locations", "").split(";") if x.strip()}

    def json_file(self, rel: str):
        p = self.root / rel
        if rel not in self._cache:
            self._cache[rel] = json.loads(p.read_text(), parse_float=Decimal) if p.is_file() else None
        return self._cache[rel]


class NoPath(Exception):
    """A recompute path exists in the computation text but cannot be run."""


# ------------------------------------------------------------------ source-unit handling
def unit_scale(hint_name: str, row_unit: str):
    """Factor from a source column/key's unit (guessed only from its name) to the row's unit."""
    n = hint_name.lower()
    if row_unit in ("usd_tn", "usd_bn"):
        src = "m" if "musd" in n else "b" if ("busd" in n or "usd_bn" in n) else None
        if src is None:
            return Decimal(1)
        return {("m", "usd_tn"): Decimal("1e-6"), ("m", "usd_bn"): Decimal("1e-3"),
                ("b", "usd_tn"): Decimal("1e-3"), ("b", "usd_bn"): Decimal(1)}[(src, row_unit)]
    if row_unit == "share" and n.endswith("_pct"):
        return Decimal("0.01")
    if row_unit == "pct_rank" and "percentile" in n:
        return Decimal(100)   # fractions (0.982) -> 98.2; applied only when |v| <= 1
    return Decimal(1)


def apply_unit(iv: Iv, name: str, row_unit: str) -> Iv:
    f = unit_scale(name, row_unit)
    if row_unit == "pct_rank" and f == 100 and abs(iv.mid) > 1:
        f = Decimal(1)
    return iv.scale(f)


# ------------------------------------------------------------------ path 1: validation check
OBS_RE = re.compile(r"(?<![\w.])([+\-−])?(\$)?(\d[\d,]*(?:\.\d+)?)\s?(%|pp\b|pts\b|T\b|B\b|M\b|×|x\b)?")


CONF_LEVEL_RE = re.compile(r"\s*(?:\w+\s+)?(?:interval|CI\b|confidence|credible)", re.I)
PVAL_OBS_RE = re.compile(r"\bp\s*(?:=|≈|<|>|<=|>=)\s*(0?\.\d+|[01](?:\.\d+)?)\b")


def parse_observed(obs: str):
    out = []
    for m in OBS_RE.finditer(obs):
        sign, dollar, num, suf = m.groups()
        if suf in ("T", "B", "M") and not dollar:
            continue
        if dollar:
            kind = suf if suf in ("T", "B", "M") else None
        else:
            kind = {"%": "pct", "pp": "pp", "pts": "pp", "×": "x", "x": "x"}.get(suf)
        if kind is None:
            continue
        out.append((kind, num, m.start(), m.end()))
    return out


def obs_to_row_unit(kind: str, iv: Iv, unit: str):
    if unit in ("share", "pvalue") and kind == "pct":
        return iv.scale(Decimal("0.01"))
    if unit == "pp" and kind == "pp":
        return iv
    if unit == "ratio" and kind == "x":
        return iv
    f = {("usd_tn", "T"): 1, ("usd_tn", "B"): Decimal("1e-3"), ("usd_tn", "M"): Decimal("1e-6"),
         ("usd_bn", "T"): 1000, ("usd_bn", "B"): 1, ("usd_bn", "M"): Decimal("1e-3")}.get((unit, kind))
    return None if f is None else iv.scale(f)


def from_check(row, ctx: Ctx):
    cid = row["check_id"].strip()
    chk = ctx.checks.get(cid)
    if chk is None:
        raise NoPath(f"check {cid} not in validation/results.json")
    obs = chk.get("observed", "")
    cands = []
    for kind, num, s, e in parse_observed(obs):
        if kind == "pct" and CONF_LEVEL_RE.match(obs, e):
            continue  # "MC 99% interval", "95% CI": a confidence level, never the value
        iv = obs_to_row_unit(kind, Iv.printed(num), row["unit"])
        if iv is not None:
            cands.append((iv, s, e, num, kind))
    if row["unit"] == "pvalue":
        for m in PVAL_OBS_RE.finditer(obs):
            cands.append((Iv.printed(m.group(1)), m.start(1), m.end(1), m.group(1), "pval"))
        cands.sort(key=lambda c: c[1])
    if not cands:
        raise NoPath(f"check {cid} observed {obs!r} has no number in a unit comparable to {row['unit']}")
    how = "the only comparable number"
    if len(cands) > 1:
        quarters = re.findall(r"\d{4}Q[1-4]", chk.get("description", ""))
        of = re.fullmatch(r"\s*(.+?)\s+of\s+(.+?)\s*", obs)
        if len(quarters) == len(cands) and row["period"] in quarters:
            idx = quarters.index(row["period"]); cands = [cands[idx]]
            how = f"number #{idx + 1}, paired with period {row['period']} in the check description"
        elif of and len(cands) == 2 and re.search(r"\bscope\b|\btotal", row["claim"].lower()):
            cands = [cands[1]]; how = "second number of 'A of B' (row claim says scope/total)"
        elif of and len(cands) == 2 and "scope" not in row["claim"].lower():
            cands = [cands[0]]; how = "first number of 'A of B'"
        else:
            cands = [cands[0]]; how = "first comparable number of the check's observed"
    iv, s, e, num, kind = cands[0]
    return iv, f"validation check {cid} ({chk['status']}) observed {obs!r}: {how} = {num} ({kind})"


# ------------------------------------------------------------------ path 2: results.json key
RESULTS_RE = re.compile(r"(?P<pre>[\w./-]*?)results\.json:?\s+(?P<key>[A-Za-z_][\w.\[\]]*)(?:\s*:\s*(?P<expr>[^;(=]+))?")


def results_file(m: re.Match, computation: str) -> str:
    pre = m.group("pre")
    if pre:
        return pre + "results.json"
    r = re.search(r"(research/[\w-]+)/", computation)
    return (r.group(1) + "/" if r else "analysis/") + "results.json"


def walk(obj, key: str):
    for part in re.findall(r"[^.\[\]]+|\[[^\]]*\]", key):
        if part.startswith("["):
            sel = part[1:-1]
            if not isinstance(obj, list):
                raise NoPath(f"{key}: [{sel}] applied to a non-list")
            hit = [x for x in obj if isinstance(x, dict) and str(next(iter(x.values()))) == sel]
            if len(hit) != 1:
                raise NoPath(f"{key}: no unique list element with first value {sel}")
            obj = hit[0]
        else:
            if not isinstance(obj, dict) or part not in obj:
                raise NoPath(f"key {part!r} not found")
            obj = obj[part]
    return obj


def eval_expr(expr: str, env: dict) -> Iv:
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.BinOp):
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Add): return a + b
            if isinstance(n.op, ast.Sub): return a - b
            if isinstance(n.op, ast.Mult): return a * b
            if isinstance(n.op, ast.Div): return a / b
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub): return -ev(n.operand)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return Iv.exact(Decimal(str(n.value)))
        if isinstance(n, ast.Name):
            if n.id not in env or isinstance(env[n.id], (dict, list, str, bool)) or env[n.id] is None:
                raise NoPath(f"name {n.id!r} is not a numeric field")
            return Iv.exact(env[n.id])
        raise NoPath("unsupported expression")
    try:
        return ev(ast.parse(expr.strip(), mode="eval"))
    except SyntaxError:
        raise NoPath(f"cannot parse expression {expr.strip()!r}")
    except ZeroDivisionError:
        raise NoPath("division by an interval containing zero")


def from_results_key(row, ctx: Ctx):
    comp = row["computation"]
    if re.search(r"\bderived\b|\brecompute\b", comp):
        raise NoPath("computation is a derived expression, not a single results.json key")
    m = RESULTS_RE.search(comp)
    if not m:
        raise NoPath("no results.json key in computation")
    rel = results_file(m, comp)
    data = ctx.json_file(rel)
    if data is None:
        raise NoPath(f"{rel} not found")
    key, expr = m.group("key"), m.group("expr")
    node = walk(data, key)
    if expr and expr.strip():
        if not isinstance(node, dict):
            raise NoPath(f"{key} is not an object to evaluate {expr.strip()!r} against")
        iv = eval_expr(expr, node)
        return apply_unit(iv, key, row["unit"]), f"{rel} {key}: {expr.strip()}"
    if isinstance(node, bool) or not isinstance(node, (Decimal, int)):
        raise NoPath(f"{rel} {key} is {type(node).__name__}, not a number")
    iv = Iv.exact(node)   # JSON drops trailing zeros, so its precision is unknown: treated as exact
    return apply_unit(iv, key, row["unit"]), f"{rel} {key} = {node}"


# ------------------------------------------------------------------ path 3: CSV / JSON
CSV_RE = re.compile(r"(?P<file>(?:[\w./-]+/)?[\w-]+\.csv)\b(?P<rest>[^;]*)")


def csv_path(name: str, comp: str, ctx: Ctx) -> Path:
    if "/" in name:
        return ctx.root / name
    r = re.search(r"(research/[\w-]+)/", comp)
    return ctx.root / (r.group(1) if r else "") / name


def from_csv(row, ctx: Ctx, m: re.Match):
    path = csv_path(m.group("file"), row["computation"], ctx)
    if not path.is_file():
        raise NoPath(f"{path.relative_to(ctx.root) if path.is_relative_to(ctx.root) else path} not found")
    with path.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        header, rows = rd.fieldnames, list(rd)
    keycols = header[:2] if header[:2] == ["from", "to"] else header[:1]
    words = re.findall(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)?", m.group("rest").replace(",", " "))
    cols = [w for w in dict.fromkeys(words) if w in header and w not in keycols]
    if len(cols) != 1:
        raise NoPath(f"{path.name}: cannot identify one value column in {m.group('rest').strip()!r}")
    col = cols[0]
    if "max" in words or "min" in words:
        fn = max if "max" in words else min
        vals = [r[col] for r in rows if re.fullmatch(r"-?\d+(\.\d+)?", r[col] or "")]
        if not vals:
            raise NoPath(f"{path.name}: column {col} has no numbers")
        pick = fn(vals, key=Decimal)
        what = f"{path.name} {'max' if fn is max else 'min'}({col}) = {pick}"
    else:
        hit = []
        for w in words:
            parts = w.split("-")
            for r in rows:
                if len(keycols) == 1 and r[keycols[0]] == w:
                    hit.append(r)
                elif len(keycols) == 2 and len(parts) == 2 and [r[keycols[0]], r[keycols[1]]] == parts:
                    hit.append(r)
        if len(hit) != 1:
            raise NoPath(f"{path.name}: {len(hit)} rows match a key in {m.group('rest').strip()!r}")
        pick = hit[0][col]
        if not re.fullmatch(r"-?\d+(\.\d+)?", pick or ""):
            raise NoPath(f"{path.name}: {col} is empty or non-numeric for that row")
        what = f"{path.name} [{'/'.join(hit[0][k] for k in keycols)}] {col} = {pick}"
    return apply_unit(Iv.printed(pick), col, row["unit"]), what


def json_records(comp: str, ctx: Ctx):
    m = re.search(r"((?:[\w./-]+/)?[\w-]+\.json)\b", comp)
    if not m:
        raise NoPath("no json file named")
    data = ctx.json_file(m.group(1))
    if not isinstance(data, list):
        raise NoPath(f"{m.group(1)} not found or not a list of records")
    return m.group(1), data


def from_json(row, ctx: Ctx):
    comp = row["computation"]
    a = re.search(r"\b(sum|min|max)\((\w+)\)\s+where\s+(?P<w>[^()]+)", comp)
    b = re.search(r"\b(min|max)\s+(\w+)\s+for\s+date\s*(>=)\s*(\d{4}-\d{2}-\d{2})", comp)
    c = re.search(r"\bsum of (\w+) for date (\d{4}-\d{2}-\d{2}) in\b", comp)
    if a:
        agg, col = a.group(1), a.group(2)
        conds = [(k, "=", v) for k, _, v in re.findall(r"(\w+)\s*(=)\s*'([^']*)'", a.group("w"))]
    elif b:
        agg, col, conds = b.group(1), b.group(2), [("date", ">=", b.group(4))]
    elif c:
        agg, col, conds = "sum", c.group(1), [("date", "=", c.group(2))]
    else:
        raise NoPath("no JSON aggregation pattern in computation")
    rel, recs = json_records(comp, ctx)

    def keep(r):
        for k, op, v in conds:
            if k not in r or (r[k] != v if op == "=" else not str(r[k]) >= v):
                return False
        return True

    vals = [r[col] for r in recs if keep(r) and isinstance(r.get(col), (int, Decimal))]
    if not vals:
        raise NoPath(f"{rel}: no records with numeric {col} under {conds}")
    v = {"sum": sum, "min": min, "max": max}[agg](vals)
    return apply_unit(Iv.exact(Decimal(v)), col, row["unit"]), f"{rel} {agg}({col}) where {conds} = {v}"


def recompute(row, ctx: Ctx):
    """Return (Iv in row unit, description) or raise NoPath with every reason collected."""
    if row["unit"] == "date":
        raise NoPath("date rows have no numeric recompute")
    reasons = []
    comp = row["computation"]
    attempts = []
    if row["check_id"].strip():
        attempts.append(lambda: from_check(row, ctx))
    attempts.append(lambda: from_results_key(row, ctx))
    for m in CSV_RE.finditer(comp):
        attempts.append(lambda m=m: from_csv(row, ctx, m))
    if ".json" in comp:
        attempts.append(lambda: from_json(row, ctx))
    for fn in attempts:
        try:
            return fn()
        except NoPath as e:
            reasons.append(str(e))
    if not row["check_id"].strip() and not reasons:
        reasons.append("no recompute path")
    raise NoPath("; ".join(dict.fromkeys(reasons)) or "no recompute path")


# ------------------------------------------------------------------ verdicts
def fmt(v: Decimal, places: int = 4) -> str:
    return f"{v.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP):f}"


def judge(tok: Tok, row, ctx: Ctx) -> dict:
    """Verdict for one token against one register row."""
    res = {"claim_id": row["claim_id"], "register_display": row["display"], "value": row["value"], "unit": row["unit"],
           "period": row["period"], "computation": row["computation"], "series_ids": row["series_ids"],
           "vintage": row["vintage"], "validation": row["validation"], "check_id": row["check_id"],
           "recompute": None, "notes": []}
    if tok.kind == "nofm":
        res["verdict"], res["notes"] = "NOT RECOMPUTABLE", ["'n of m' counts are compared by hand"]
        return res
    try:
        reg = Decimal(row["value"])
    except Exception:
        res["verdict"], res["notes"] = "NOT RECOMPUTABLE", [f"register value {row['value']!r} is not numeric"]
        return res
    reg_t = row_to_token_units(row["unit"], tok, reg)
    reg_iv = Iv.printed(row["value"].strip())   # `value` is unrounded where known; a short value is read as +/- half its last digit
    if reg_t is None:
        res["verdict"] = "NOT RECOMPUTABLE"
        res["notes"] = [f"unit {row['unit']} cannot be compared with a {tok.kind} token {tok.text!r}"]
        return res
    problems = []
    if tok.sign and reg != 0 and ((reg < 0) != (tok.sign == "-")):
        res["notes"].append(f"printed sign {tok.sign!r} differs from the register value's sign (signs are not verified)")
    shown = tok.number
    rl, rh = (abs(x) for x in sorted((row_to_token_units(row["unit"], tok, reg_iv.lo), row_to_token_units(row["unit"], tok, reg_iv.hi))))
    rl, rh = min(rl, rh), max(rl, rh)
    reg_r = round_hu(abs(reg_t), tok.places)
    res["register_at_display"] = f"{reg_r:f}"
    if not round_hu(rl, tok.places) <= shown <= round_hu(rh, tok.places):
        problems.append(f"register value {row['value']} {row['unit']} = {fmt(abs(reg_t), 4)} in token units, rounds to {reg_r} not {shown} "
                        f"(off by {abs(reg_r - shown)})")
    elif reg_r != shown:
        res["notes"].append(f"edge case: register value {row['value']} is itself rounded; it rounds to {reg_r} but {shown} is within its precision")
    try:
        iv, how = recompute(row, ctx)
    except NoPath as e:
        res["recompute"] = {"status": "none", "reason": str(e)}
        res["verdict"] = "MISMATCH" if problems else "NOT RECOMPUTABLE"
        res["notes"] = problems + res["notes"] + ([] if problems else [f"no recompute: {e}"])
        return res
    lo, hi = row_to_token_units(row["unit"], tok, iv.lo), row_to_token_units(row["unit"], tok, iv.hi)
    lo, hi = abs(min(lo, hi)), abs(max(lo, hi))
    rlo, rhi = round_hu(lo, tok.places), round_hu(hi, tok.places)
    mid = abs(row_to_token_units(row["unit"], tok, iv.mid))
    res["recompute"] = {"status": "ok", "how": how, "value_token_units": fmt(mid, max(tok.places + 2, 4)),
                        "rounded_range": [f"{rlo:f}", f"{rhi:f}"]}
    if rlo <= shown <= rhi:
        if rlo != rhi:
            res["notes"].append(f"edge case: the source is printed to fewer digits than the token, so it cannot settle the last digit "
                                f"(rounds to {rlo}..{rhi}); the register value decides")
    else:
        problems.append(f"recompute {fmt(mid, max(tok.places + 2, 4))} rounds to {rlo if shown > rhi else rhi} not {shown} "
                        f"(off by {min(abs(shown - rlo), abs(shown - rhi))})")
    res["verdict"] = "MISMATCH" if problems else "MATCH"
    res["notes"] = problems + res["notes"]
    return res


def check_line(line: str, lineno: int, ctx: Ctx, rel: str | None):
    items = []
    for tok in tokens_in_line(line, lineno):
        n = normalize(tok.text)
        rows = [r for r in ctx.rows if n in r["_norms"]]
        out = {"token": tok.text, "line": lineno, "rows": []}
        if rel and len(rows) > 1:
            pinned = [r for r in rows if f"{rel}:{lineno}" in r["_locs"]]
            if pinned:
                rows = pinned
                out["note"] = f"{len(pinned)} row(s) pinned by locations {rel}:{lineno}"
        if not rows:
            out["verdict"] = "UNTRACED"
            out["related"] = related(tok, line, ctx)
        elif len(rows) > 1:
            out["verdict"] = "AMBIGUOUS"
            out["rows"] = [{"claim_id": r["claim_id"], "claim": r["claim"], "value": r["value"], "unit": r["unit"],
                            "period": r["period"], "locations": r["locations"]} for r in rows]
            out["ask"] = "Several rows print this token; which claim is meant?"
        else:
            j = judge(tok, rows[0], ctx)
            out["verdict"], out["rows"] = j["verdict"], [j]
        items.append(out)
    return items


def related(tok: Tok, line: str, ctx: Ctx):
    """Rows in the same unit family whose period is named in the line: leads for a human, NOT matches."""
    periods = set(re.findall(r"\d{4}Q[1-4]", line))
    out = []
    for r in ctx.rows:
        if r["period"] in periods and row_to_token_units(r["unit"], tok, Decimal(1)) is not None:
            out.append({"claim_id": r["claim_id"], "display": r["display"], "period": r["period"]})
    return out[:4]


def source_lines(args, ctx: Ctx):
    """Yield (lineno, text, relpath|None)."""
    if args.text is not None:
        yield 1, args.text, None
        return
    p = Path(args.file)
    p = p if p.is_absolute() else Path.cwd() / p
    if not p.is_file():
        p = ctx.root / args.file
    if not p.is_file():
        raise FileNotFoundError(args.file)
    try:
        rel = p.resolve().relative_to(ctx.root.resolve()).as_posix()
    except ValueError:
        rel = None
    text = p.read_text(encoding="utf-8", errors="replace")
    pub = dict(CR.publishable_lines(rel or p.name, text))
    if args.line:
        raw = text.splitlines()
        if not 1 <= args.line <= len(raw):
            raise FileNotFoundError(f"{args.file} has {len(raw)} lines")
        yield args.line, pub.get(args.line, ""), rel
        return
    for n, t in pub.items():
        yield n, t, rel


COUNTED = ("MATCH", "MISMATCH", "UNTRACED", "AMBIGUOUS", "NOT RECOMPUTABLE")


def render(items, summary) -> str:
    out = []
    for i, it in enumerate(items, 1):
        out.append(f"[{i}] {it['token']!r} (line {it['line']}) -> {it['verdict']}")
        if it.get("note"):
            out.append(f"    {it['note']}")
        if it["verdict"] == "UNTRACED":
            out.append("    no register row prints this token")
            for r in it.get("related", []):
                out.append(f"    related, not a match: {r['claim_id']} prints {r['display']!r} ({r['period']})")
        elif it["verdict"] == "AMBIGUOUS":
            for r in it["rows"]:
                out.append(f"    candidate {r['claim_id']}: {r['claim']} value={r['value']} {r['unit']} {r['period']} at {r['locations']}")
            out.append(f"    {it['ask']}")
        else:
            for r in it["rows"]:
                out.append(f"    register {r['claim_id']}: value={r['value']} {r['unit']}, period {r['period']}, vintage {r['vintage']}, "
                           f"validation {r['validation']}{' (' + r['check_id'] + ')' if r['check_id'] else ''}")
                out.append(f"    series {r['series_ids'] or '-'}; computation: {r['computation'][:160]}")
                rc = r["recompute"]
                if rc and rc["status"] == "ok":
                    out.append(f"    recompute: {rc['how']} -> {rc['value_token_units']} in token units, rounds to {'..'.join(dict.fromkeys(rc['rounded_range']))}")
                elif rc:
                    out.append(f"    recompute: none ({rc['reason'][:200]})")
                for n in r["notes"]:
                    out.append(f"    - {n}")
    out.append("SUMMARY " + ", ".join(f"{k} {summary.get(k, 0)}" for k in COUNTED) + f" (of {len(items)} numbers)")
    return "\n".join(out)


def run(args, ctx: Ctx):
    items = []
    for n, text, rel in source_lines(args, ctx):
        items += check_line(text, n, ctx, rel)
    summary = {}
    for it in items:
        summary[it["verdict"]] = summary.get(it["verdict"], 0) + 1
    return items, summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Trace numbers in text to claims/register.csv and recompute them (read-only).")
    ap.add_argument("text", nargs="?", help="sentence or paragraph to check")
    ap.add_argument("--file", help="file to check (whole file, or one line with --line)")
    ap.add_argument("--line", type=int, help="1-based line in --file")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if (args.text is None) == (args.file is None) or (args.line and not args.file):
        print("usage: give either TEXT or --file PATH [--line N]", file=sys.stderr)
        return 2
    try:
        ctx = Ctx(root=args.root)
        items, summary = run(args, ctx)
    except (FileNotFoundError, OSError, KeyError, StopIteration) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"summary": summary, "items": items}, indent=2, default=str))
    else:
        print(render(items, summary) if items else "no numbers found")
    return 1 if summary.get("MISMATCH") or summary.get("UNTRACED") else 0


if __name__ == "__main__":
    sys.exit(main())
