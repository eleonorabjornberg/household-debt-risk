#!/usr/bin/env python3
"""Validate claims/register.csv and scan published copy for numbers with no register row.

Run from anywhere:

    uv run --project pipeline python claims/check_register.py

Part 1, the register itself (errors):
  * header is exactly SCHEMA, in order
  * claim_id is a unique slug
  * required fields are non-empty; value parses as a number (unit "date" may hold an ISO date)
  * validation is one of STATUSES
  * validation PASS/FAIL  -> check_id is set, exists in validation/results.json, and that check's
    own status agrees (PASS row needs a PASS check, FAIL row a FAIL check)
  * any other validation  -> check_id is empty
  * every location is `path:line`, the file exists and the line is in range

Part 2, the scan (errors): every number-like token in SCAN_FILES must equal a token found in some
row's `display` (after normalisation), unless it is allowlisted. In LINE_CITED_FILES (analysis/findings.md) the row must also cite
that file:line in its `locations`. Unmatched tokens are printed as
file:line.

What counts as a number-like token (TOKEN_RE, first alternative that matches wins):
  money     $12, $10.77T, $50 billion, $681B            \\$\\d[\\d,]*(\\.\\d+)?\\s?(T|B|M|trillion|billion|million)?
  p-value   p ≈ 0.30, p = .05, p < 0.01                  p\\s?[≈=<]\\s?\\d*\\.\\d+
  n of m    5 of 11                                      \\d+ of \\d+
  unit      56.4%, +13.1 pp, 13.1 pts, 3 points, 3.56×,  \\d[\\d,]*(\\.\\d+)?\\s?(%|pp|pts|point(s)|×|x|th)
            98th
  decimal   0.30 (a bare decimal with no unit)           \\d+\\.\\d+
Not tokens, by design: years, "2026Q2", series IDs, figure numbers and bare integers ("1,000 dots"
is registered by hand but not scanned for).

Normalisation (so that spelling variants of one claim compare equal): lower-case; drop spaces and
thousands commas; unify minus signs; drop a leading sign; pts/point/points -> pp; × -> x;
trillion -> T; billion -> B; million -> M. "+13.1 pts", "13.1 pp" and "13.1 points" are the same
token; "56.4%" and "56%" are not.

Which lines are scanned: the whole file, except in .md files fenced code blocks and `inline code`, and in
.ts files whole-line comments and trailing ` // ...` comments (comments are not published copy).

Exit status 0 when both parts are clean, 1 otherwise.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "claims" / "register.csv"
# Parallel tracks add rows in claims/tracks/<track>.csv (same schema); the coordinator moves them into
# register.csv when it merges the track, so tracks never edit the shared register.
TRACK_REGISTERS = ROOT / "claims" / "tracks"
VALIDATION_RESULTS = ROOT / "validation" / "results.json"

SCHEMA = [
    "claim_id", "claim", "display", "value", "unit", "period", "locations",
    "computation", "series_ids", "vintage", "validation", "check_id", "notes",
]
STATUSES = {"PASS", "FAIL", "UNVERIFIED", "ESTIMATE", "STALE", "DEFINITION"}  # DEFINITION: design setting, not a data claim
REQUIRED = ["claim_id", "claim", "display", "value", "unit", "period", "locations",
            "computation", "vintage", "validation"]

# Files whose published copy is scanned for unregistered numbers.
SCAN_FILES = ["README.md", "atlas/content/story.ts", "atlas/content/methods.ts", "atlas/content/build.ts",
              "web/content/story.ts", "analysis/recommendation.md", "analysis/findings.md"] + sorted(
    str(p.relative_to(ROOT)) for p in (ROOT / "research").glob("*/README.md"))  # every research write-up

# Non-claims. Each entry: file (exact path), pattern (regex matched with fullmatch against the
# normalised token), reason. Keep this short; prefer registering a row.
ALLOWLIST = [
    {"file": "README.md", "pattern": r"20th", "reason": "day of month in the refresh-workflow schedule (the 20th of Mar/Jun/Sep/Dec)"},
    {"file": "README.md", "pattern": r"(?:20)?4\.0", "reason": "CC BY 4.0 licence name in the data-licence badge (and its URL-encoded form)"},
]

TOKEN_RE = re.compile(
    r"""
    (?P<money>\$\d[\d,]*(?:\.\d+)?\s?(?:trillion|billion|million|T|B|M)?(?![A-Za-z]))
  | (?P<pval>\bp\s?[≈=<]\s?\d*\.\d+)
  | (?P<nofm>\b\d+\s+of\s+\d+\b)
  | (?P<unit>(?<![\w.])\d[\d,]*(?:\.\d+)?\s?(?:%|pp\b|pts\b|points?\b|×|x\b|th\b))
  | (?P<dec>(?<![\w.$])\d+\.\d+(?![\d%\w]))
    """,
    re.VERBOSE,
)

TEMPLATE_RE = re.compile(r"\{\w+\}|\$\{facts\.|facts\.\w+|fmt\w*\(|pct\(")
LOC_RE = re.compile(r"^(?P<path>[^:]+):(?P<line>\d+)$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")
VINTAGE_RE = re.compile(r"^(?:n/a|[a-z0-9]+:\d{4}-\d{2}-\d{2}(?: [a-z0-9]+:\d{4}-\d{2}-\d{2})*)$")


# ------------------------------------------------------------------ token matching
def normalize(token: str) -> str:
    t = token.strip().lower().replace("−", "-").replace("–", "-")
    t = t.replace(",", "")
    t = re.sub(r"\s+", "", t)
    t = t.lstrip("+-")
    t = t.replace("×", "x")
    t = re.sub(r"(trillion)$", "t", t)
    t = re.sub(r"(billion)$", "b", t)
    t = re.sub(r"(million)$", "m", t)
    t = re.sub(r"(pts|points|point)$", "pp", t)
    t = re.sub(r"^p([≈=<])0?(?=\.)", r"p\1", t)  # p≈.30 == p≈0.30 -> "p≈.30"
    t = re.sub(r"^p([≈=<])0\.", r"p\1.", t)
    return t


def extract_tokens(line: str) -> list[str]:
    """Number-like tokens in one line of text (raw spelling, unnormalised)."""
    return [m.group(0).strip() for m in TOKEN_RE.finditer(line)]


def register_tokens(displays: list[str]) -> set[str]:
    """Normalised token set covered by a list of `display` cells (variants split on ' | ')."""
    out: set[str] = set()
    for cell in displays:
        for variant in cell.split(" | "):
            for tok in extract_tokens(variant):
                out.add(normalize(tok))
            out.add(normalize(variant))  # whole-variant match, e.g. a bare "0.30"
    return out


def is_allowlisted(rel_path: str, token: str, allowlist=ALLOWLIST) -> bool:
    n = normalize(token)
    return any(a["file"] == rel_path and re.fullmatch(a["pattern"], n) for a in allowlist)


def publishable_lines(rel_path: str, text: str):
    """Yield (lineno, text) for lines that are published copy (see module docstring)."""
    in_fence = False
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw
        if rel_path.endswith(".md"):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = re.sub(r"`[^`]*`", "", line)
        elif rel_path.endswith((".ts", ".tsx")):
            s = line.lstrip()
            if s.startswith(("//", "*", "/*")) or s.startswith("import "):
                continue
            line = re.sub(r"\s//\s.*$", "", line)
        yield i, line


def scan_text(rel_path: str, text: str, covered: set[str], allowlist=ALLOWLIST):
    """Return [(lineno, token)] for tokens with no register match."""
    bad = []
    for i, line in publishable_lines(rel_path, text):
        for tok in extract_tokens(line):
            if normalize(tok) in covered or is_allowlisted(rel_path, tok, allowlist):
                continue
            bad.append((i, tok))
    return bad


# ------------------------------------------------------------------ register validation
def load_register(path: Path = REGISTER):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [dict(zip(header, r)) | {"_line": n, "_file": path.name} for n, r in enumerate(reader, 2) if any(c.strip() for c in r)]
        widths = [len(r) for r in csv.reader(path.open(newline="", encoding="utf-8"))]
    return header, rows, widths


def validate_register(root: Path = ROOT, register: Path = REGISTER, results_path: Path = VALIDATION_RESULTS,
                      track_dir: Path | None = None):
    errors: list[str] = []
    track_dir = TRACK_REGISTERS if track_dir is None and register == REGISTER else track_dir
    files = [register] + (sorted(track_dir.glob("*.csv")) if track_dir and track_dir.is_dir() else [])
    rows = []
    for f in files:
        header, frows, widths = load_register(f)
        if header != SCHEMA:
            errors.append(f"{f.name} header mismatch.\n  expected {SCHEMA}\n  found    {header}")
            return errors, rows + frows
        for n, w in enumerate(widths, 1):
            if w and w != len(SCHEMA):
                errors.append(f"{f.name} line {n}: {w} columns, expected {len(SCHEMA)}")
        rows += frows

    checks: dict[str, str] = {}
    if results_path.exists():
        checks = {c["id"]: c["status"] for c in json.loads(results_path.read_text())["checks"]}
    else:
        errors.append(f"{results_path} not found (needed to verify check_id)")

    seen: set[str] = set()
    for r in rows:
        tag = f"{r.get('_file', 'register.csv')}:{r['_line']} [{r.get('claim_id', '?')}]"
        for col in REQUIRED:
            if not (r.get(col) or "").strip():
                errors.append(f"{tag}: empty required field {col}")
        cid = r.get("claim_id", "")
        if not SLUG_RE.match(cid):
            errors.append(f"{tag}: claim_id is not a slug ([a-z0-9_])")
        if cid in seen:
            errors.append(f"{tag}: duplicate claim_id")
        seen.add(cid)

        if r["unit"] == "date":
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["value"]):
                errors.append(f"{tag}: unit=date needs an ISO date value, got {r['value']!r}")
        else:
            try:
                float(r["value"])
            except ValueError:
                errors.append(f"{tag}: value {r['value']!r} is not numeric")

        if not VINTAGE_RE.match(r["vintage"]):
            errors.append(f"{tag}: vintage {r['vintage']!r} must look like 'z1:2026-09-11' (space-separated) or 'n/a'")

        v, check_id = r["validation"], r["check_id"].strip()
        if v not in STATUSES:
            errors.append(f"{tag}: validation {v!r} not in {sorted(STATUSES)}")
        elif v in ("PASS", "FAIL"):
            if not check_id:
                errors.append(f"{tag}: validation={v} needs a check_id")
            elif check_id not in checks:
                errors.append(f"{tag}: check_id {check_id} is not in validation/results.json")
            elif checks[check_id] != v:
                errors.append(f"{tag}: row says {v} but validation/results.json says {check_id} is {checks[check_id]}")
        elif check_id:
            errors.append(f"{tag}: check_id must be empty unless validation is PASS/FAIL")

        for loc in [x.strip() for x in r["locations"].split(";") if x.strip()]:
            m = LOC_RE.match(loc)
            if not m:
                errors.append(f"{tag}: location {loc!r} is not path:line")
                continue
            p = root / m["path"]
            if not p.is_file():
                errors.append(f"{tag}: location file {m['path']} does not exist")
                continue
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            n_lines = len(lines)
            if not 1 <= int(m["line"]) <= n_lines:
                errors.append(f"{tag}: {loc} is outside the file ({n_lines} lines)")
                continue
            # The line must show the number (any display spelling) or the template that renders it.
            # Catches locations that drift when lines are inserted above them.
            text = lines[int(m["line"]) - 1]
            spellings = [d.strip() for d in r.get("display", "").split("|") if d.strip()]
            if not any(d in text for d in spellings) and not TEMPLATE_RE.search(text):
                errors.append(f"{tag}: {loc} does not show {r.get('display')!r} (line drifted?): {text.strip()[:80]!r}")
    return errors, rows


# Files where a token counts as registered only if a row cites that exact file:line (Eleonora, docket 51
# findings-scan (a), 2026-11-09): a matching display on some other row is not enough there.
LINE_CITED_FILES = {"analysis/findings.md"}


def cited_tokens(rows, rel: str) -> dict[int, set[str]]:
    """line -> normalised tokens of the rows whose locations cite rel:line."""
    out: dict[int, set[str]] = {}
    for r in rows:
        for loc in r.get("locations", "").split(";"):
            m = LOC_RE.match(loc.strip())
            if m and m["path"] == rel:
                out.setdefault(int(m["line"]), set()).update(register_tokens([r.get("display", "")]))
    return out


def scan_files(rows, root: Path = ROOT, scan_files_=SCAN_FILES, allowlist=ALLOWLIST, line_cited=LINE_CITED_FILES):
    covered = register_tokens([r["display"] for r in rows])
    out = []
    for rel in scan_files_:
        p = root / rel
        if not p.is_file():
            out.append((rel, 0, "<file missing>"))
            continue
        text = p.read_text(encoding="utf-8")
        if rel in line_cited:
            by_line = cited_tokens(rows, rel)
            for i, line in publishable_lines(rel, text):
                for tok in extract_tokens(line):
                    if normalize(tok) not in by_line.get(i, set()) and not is_allowlisted(rel, tok, allowlist):
                        out.append((rel, i, tok))
            continue
        for line, tok in scan_text(rel, text, covered, allowlist):
            out.append((rel, line, tok))
    return out


def main() -> int:
    errors, rows = validate_register()
    for e in errors:
        print("REGISTER ERROR:", e)
    unmatched = scan_files(rows)
    for rel, line, tok in unmatched:
        print(f"UNREGISTERED: {rel}:{line}  {tok!r}")
    status = {}
    for r in rows:
        status[r["validation"]] = status.get(r["validation"], 0) + 1
    print(f"{len(rows)} rows; " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())))
    if errors or unmatched:
        print(f"FAILED: {len(errors)} register error(s), {len(unmatched)} unregistered token(s)")
        return 1
    print("OK: register valid; every number-like token in " + ", ".join(SCAN_FILES) + " has a register row")
    return 0


if __name__ == "__main__":
    sys.exit(main())
