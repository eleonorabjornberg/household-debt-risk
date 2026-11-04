#!/usr/bin/env python3
"""E2: plant catalogued errors into copies of project write-ups, and write the hidden key (PLAN E2).

    uv run --project pipeline python evals/e2_planted_errors/plant.py \
        --data research/a1_gfc_decomposition/README.md analysis/findings.md \
        --method research/c1_nowcast/README.md \
        --planted 12 --errors-per-doc 3 --controls 4 --seed 20261104 --out evals/e2_planted_errors/run-<id>

Writes into --out:
  docs/doc-<hex>.md   the variants reviewers see (planted and control copies, neutral names, shuffled)
  manifest.json       the variant names only (what reviewers may be told)
  key.json            HIDDEN: per variant, its source, whether it is a control, and every planted error
                      (line in the variant, category, agent, original and planted text)
  key.sha256          SHA-256 of key.json; commit it before any reviewer runs, so the key cannot change

Data documents get data errors (skeptic) and method documents get method errors (quant-reviewer), as in
the pre-registration. Deterministic for a given seed and inputs. Refuses to run unless
docs/decisions/e2-prereg.md says it is frozen, except with --rehearsal (output marked as such and kept
out of results).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREREG = ROOT / "docs" / "decisions" / "e2-prereg.md"


def load_catalogue(path: Path = HERE / "catalogue.yaml") -> list[dict]:
    return yaml.safe_load(path.read_text())["errors"]


def eligible_lines(lines: list[str]) -> list[int]:
    """Prose lines only: not headings, tables, fences, blockquote banners or blank lines."""
    out, fence = [], False
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s or s.startswith(("#", "|", ">", "<!--")):
            continue
        out.append(i)
    return out


def _fill(repl: str, m: re.Match) -> str:
    """Expand {bump} (next digit, never the same) and {bumpyear} in a replacement."""
    if "{bump}" in repl:
        repl = repl.replace("{bump}", str((int(m.group(2)) + 1) % 10))
    if "{bumpyear}" in repl:
        repl = repl.replace("{bumpyear}", str((int(m.group(2)) + 1) % 10))
    return m.expand(repl)


def apply_error(lines: list[str], idx: int, err: dict) -> tuple[int, str, str] | None:
    """Plant `err` at line idx. Returns (line index of the error, original, planted) or None."""
    line = lines[idx]
    if not re.search(err["eligible"], line):
        return None
    if err["kind"] == "replace":
        m = re.search(err["find"], line)
        if not m:
            return None
        new = line[: m.start()] + _fill(err["repl"], m) + line[m.end():]
        if new == line:
            return None
        lines[idx] = new
        return idx, line, new
    if err["kind"] == "insert":
        lines.insert(idx + 1, err["text"])
        return idx + 1, "", err["text"]
    raise ValueError(f"unknown kind {err['kind']}")


def plant_doc(text: str, errors: list[dict], k: int, rng: random.Random) -> tuple[str, list[dict]]:
    lines = text.split("\n")
    planted: list[dict] = []
    used_lines: set[int] = set()
    pool = errors[:]
    rng.shuffle(pool)
    for err in pool:
        if len(planted) == k:
            break
        cands = [i for i in eligible_lines(lines) if i not in used_lines and re.search(err["eligible"], lines[i])]
        rng.shuffle(cands)
        for idx in cands:
            res = apply_error(lines, idx, err)
            if res is None:
                continue
            at, orig, new = res
            if err["kind"] == "insert":  # every recorded line at or after the insertion moves down one
                for p in planted:
                    if p["line"] - 1 >= at:
                        p["line"] += 1
                used_lines = {u + 1 if u >= at else u for u in used_lines}
            used_lines.update({at, at - 1, at + 1})
            planted.append({"category": err["id"], "agent": err["agent"], "kind": err["kind"], "line": at + 1,
                            "original": orig, "planted": new, "fix": err["fix"]})
            break
    return "\n".join(lines), planted


def is_frozen(prereg: Path = PREREG) -> bool:
    return prereg.exists() and re.search(r"^Status:\s*\**frozen", prereg.read_text(), re.M | re.I) is not None


def run(data: list[Path], method: list[Path], planted: int, k: int, controls: int, seed: int, out: Path,
        rehearsal: bool = False) -> dict:
    if not rehearsal and not is_frozen():
        raise SystemExit("docs/decisions/e2-prereg.md is not frozen: E2 may not be run (use --rehearsal for a dry run)")
    cat = load_catalogue()
    rng = random.Random(seed)
    sources = [(p, "skeptic") for p in data] + [(p, "quant-reviewer") for p in method]
    if not sources:
        raise SystemExit("no documents")
    jobs = [("planted", sources[i % len(sources)]) for i in range(planted)] + \
           [("control", sources[i % len(sources)]) for i in range(controls)]
    rng.shuffle(jobs)
    (out / "docs").mkdir(parents=True, exist_ok=True)
    key = {"seed": seed, "rehearsal": rehearsal, "errors_per_doc": k, "variants": []}
    try:
        key["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                              text=True).stdout.strip()
    except OSError:
        key["source_commit"] = None
    names = []
    for role, (src, agent) in jobs:
        name = f"doc-{rng.getrandbits(32):08x}.md"
        text = src.read_text(encoding="utf-8")
        errs: list[dict] = []
        if role == "planted":
            text, errs = plant_doc(text, [e for e in cat if e["agent"] == agent], k, rng)
            if len(errs) < k:
                print(f"warning: only {len(errs)} of {k} errors fit in {src}", file=sys.stderr)
        (out / "docs" / name).write_text(text, encoding="utf-8")
        names.append(name)
        key["variants"].append({"doc": name, "source": str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src),
                                "control": role == "control", "agent": agent, "errors": errs})
    (out / "manifest.json").write_text(json.dumps({"docs": sorted(names)}, indent=1) + "\n")
    raw = json.dumps(key, indent=1, ensure_ascii=False).encode() + b"\n"
    (out / "key.json").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    (out / "key.sha256").write_text(f"{digest}  key.json\n")
    return {"digest": digest, "variants": len(names), "errors": sum(len(v["errors"]) for v in key["variants"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", nargs="*", type=Path, default=[])
    ap.add_argument("--method", nargs="*", type=Path, default=[])
    ap.add_argument("--planted", type=int, required=True)
    ap.add_argument("--errors-per-doc", type=int, default=3)
    ap.add_argument("--controls", type=int, default=0)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rehearsal", action="store_true", help="dry run before the freeze; never a result")
    a = ap.parse_args(argv)
    r = run([p.resolve() for p in a.data], [p.resolve() for p in a.method], a.planted, a.errors_per_doc,
            a.controls, a.seed, a.out, a.rehearsal)
    print(f"{r['variants']} variants, {r['errors']} planted errors; key.sha256 {r['digest']}")
    print("Commit key.sha256 now, before any reviewer runs. Do not show key.json to reviewers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
