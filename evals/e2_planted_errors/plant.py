#!/usr/bin/env python3
"""E2: plant catalogued errors into copies of project write-ups, and write the hidden key (PLAN E2).

The frozen E2 command (docs/decisions/e2-prereg.md, CHOICE-11 (a)):

    uv run --project pipeline python evals/e2_planted_errors/plant.py \
        --data research/a1_gfc_decomposition/README.md research/a2_net_exposure/README.md \
               analysis/findings.md .claude/skills/research-memo/examples/bank_treasury.md \
        --method research/c1_nowcast/README.md research/c1_nowcast/EVALUATION.md research/c2_forecast/SPECS.md \
        --planted-data 4 --planted-method 3 --controls-data 1 --controls-method 1 \
        --errors-per-doc 2 --seed 20261104 --stratified --out evals/e2_planted_errors/run-<id>

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
import itertools
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


def plant_doc(text: str, errors: list[dict], k: int, rng: random.Random,
              ordered: bool = False) -> tuple[str, list[dict]]:
    """Plant up to k of `errors`. ordered=True tries them in the given order (stratified mode)."""
    lines = text.split("\n")
    planted: list[dict] = []
    used_lines: set[int] = set()
    pool = errors[:]
    if not ordered:
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


def stratify(docs: list[str], cats: list[dict], k: int, rng: random.Random) -> list[list[dict]]:
    """CHOICE-10 (b): assign categories to the planted documents of one agent so that every category is
    planted the same number of times (len(docs) * k / len(cats), which must be a whole number), no
    document gets a category twice, and all k fit the document together. Seeded backtracking search,
    so deterministic for a seed."""
    if not docs:
        return []
    total = len(docs) * k
    if total % len(cats):
        raise SystemExit(f"stratified: {total} errors do not split evenly over {len(cats)} categories")
    quota = {c["id"]: total // len(cats) for c in cats}
    by_id = {c["id"]: c for c in cats}
    fits = [{c["id"] for c in cats if plant_doc(d, [c], 1, random.Random(0))[1]} for d in docs]
    combos = []
    for i, d in enumerate(docs):
        ids = sorted(fits[i])
        cs = [list(t) for t in itertools.combinations(ids, k)]
        rng.shuffle(cs)
        combos.append(cs)
    joint: dict[tuple[int, tuple], bool] = {}

    def ok(i: int, combo: list[str]) -> bool:
        key = (i, tuple(combo))
        if key not in joint:
            joint[key] = len(plant_doc(docs[i], [by_id[c] for c in combo], k, random.Random(0), ordered=True)[1]) == k
        return joint[key]

    out: list[list[str]] = []

    def go(i: int) -> bool:
        if i == len(docs):
            return all(v == 0 for v in quota.values())
        left = len(docs) - i - 1
        for combo in combos[i]:
            if any(quota[c] == 0 for c in combo) or not ok(i, combo):
                continue
            for c in combo:
                quota[c] -= 1
            # prune: what remains must still fit in the documents left
            if sum(quota.values()) == left * k and all(
                    quota[c] <= sum(c in fits[j] for j in range(i + 1, len(docs))) for c in quota) and go(i + 1):
                out.insert(0, combo)
                return True
            for c in combo:
                quota[c] += 1
        return False

    if not go(0):
        raise SystemExit("stratified: no assignment fits every document; change the document set")
    return [[by_id[c] for c in combo] for combo in out]


def is_frozen(prereg: Path | None = None) -> bool:
    prereg = prereg or PREREG
    return prereg.exists() and re.search(r"^Status:\s*\**frozen", prereg.read_text(), re.M | re.I) is not None


def run(data: list[Path], method: list[Path], planted: int | dict, k: int, controls: int | dict, seed: int, out: Path,
        rehearsal: bool = False, stratified: bool = False) -> dict:
    if not rehearsal and not is_frozen():
        raise SystemExit("docs/decisions/e2-prereg.md is not frozen: E2 may not be run (use --rehearsal for a dry run)")
    cat = load_catalogue()
    rng = random.Random(seed)
    sources = [(p, "skeptic") for p in data] + [(p, "quant-reviewer") for p in method]
    if not sources:
        raise SystemExit("no documents")
    if isinstance(planted, dict) or isinstance(controls, dict):
        # counts per agent (CHOICE-11): each agent cycles over its own documents
        planted = planted if isinstance(planted, dict) else {}
        controls = controls if isinstance(controls, dict) else {}
        per = {"skeptic": [s_ for s_ in sources if s_[1] == "skeptic"],
               "quant-reviewer": [s_ for s_ in sources if s_[1] == "quant-reviewer"]}
        jobs = []
        for role, counts in (("planted", planted), ("control", controls)):
            for agent, n in counts.items():
                if n and not per[agent]:
                    raise SystemExit(f"no {agent} documents for {n} {role} copies")
                jobs += [(role, per[agent][i % len(per[agent])]) for i in range(n)]
    else:
        jobs = [("planted", sources[i % len(sources)]) for i in range(planted)] + \
               [("control", sources[i % len(sources)]) for i in range(controls)]
    rng.shuffle(jobs)
    (out / "docs").mkdir(parents=True, exist_ok=True)
    key = {"seed": seed, "rehearsal": rehearsal, "stratified": stratified, "errors_per_doc": k, "variants": []}
    plan: dict[int, list[dict]] = {}
    if stratified:
        for agent in ("skeptic", "quant-reviewer"):
            idx = [i for i, (role, (_, a)) in enumerate(jobs) if role == "planted" and a == agent]
            groups = stratify([jobs[i][1][0].read_text(encoding="utf-8") for i in idx],
                              [e for e in cat if e["agent"] == agent], k, rng)
            plan.update(zip(idx, groups))
    try:
        key["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                              text=True).stdout.strip()
    except OSError:
        key["source_commit"] = None
    names = []
    for j, (role, (src, agent)) in enumerate(jobs):
        name = f"doc-{rng.getrandbits(32):08x}.md"
        text = src.read_text(encoding="utf-8")
        errs: list[dict] = []
        if role == "planted":
            if stratified:
                text, errs = plant_doc(text, plan[j], k, rng, ordered=True)
            else:
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
    ap.add_argument("--planted", type=int, help="planted copies, cycling over all sources (pre-CHOICE-11)")
    ap.add_argument("--planted-data", type=int, help="planted copies of data documents (skeptic)")
    ap.add_argument("--planted-method", type=int, help="planted copies of method documents (quant-reviewer)")
    ap.add_argument("--controls-data", type=int, help="control copies of data documents")
    ap.add_argument("--controls-method", type=int, help="control copies of method documents")
    ap.add_argument("--errors-per-doc", type=int, default=3)
    ap.add_argument("--controls", type=int, default=0)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stratified", action="store_true",
                    help="CHOICE-10 (b): every category of an agent planted the same number of times")
    ap.add_argument("--rehearsal", action="store_true", help="dry run before the freeze; never a result")
    a = ap.parse_args(argv)
    per_agent = any(v is not None for v in (a.planted_data, a.planted_method, a.controls_data, a.controls_method))
    if per_agent == (a.planted is not None):
        ap.error("give either --planted (and --controls) or the per-agent counts, not both")
    if per_agent:
        planted = {"skeptic": a.planted_data or 0, "quant-reviewer": a.planted_method or 0}
        controls = {"skeptic": a.controls_data or 0, "quant-reviewer": a.controls_method or 0}
    else:
        planted, controls = a.planted, a.controls
    r = run([p.resolve() for p in a.data], [p.resolve() for p in a.method], planted, a.errors_per_doc,
            controls, a.seed, a.out, a.rehearsal, a.stratified)
    print(f"{r['variants']} variants, {r['errors']} planted errors; key.sha256 {r['digest']}")
    print("Commit key.sha256 now, before any reviewer runs. Do not show key.json to reviewers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
