#!/usr/bin/env python3
"""E1 cost pilot: 10 verified questions x 3 models x 1 tool-use loop, with hard spend stops.

    # offline rehearsal, fake client, no network, no key:
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/pilot.py --fake
    # live (spends money; approved for the pilot only, cap $2.98):
    uv run --project mcp/household-credit-mcp --with anthropic python evals/e1_sql_benchmark/pilot.py --live

Approval: Eleonora, 2026-11-04 (PLAN.md b7f1158): E1 pilot only, hard cap $2.98. The pilot does not approve the
full E1 build-out. Pilot accuracy is not an E1 result.

Key handling: the key is read from HHDEBT_ANTHROPIC_API_KEY and passed to the client; ANTHROPIC_BASE_URL and
ANTHROPIC_AUTH_TOKEN are removed from this process's environment and base_url is set to the first-party API.
Nothing here prints, logs or writes the key or any request header; calls.jsonl holds usage, latency and text only.

Tools: the household-credit MCP tools, called in-process on the snapshot backend (DATABASE_URL_READONLY and
DATABASE_URL are dropped before import, so production is never queried).

Hard stops (checked after every call, plus a pre-call guard so no single call can cross the cap):
  1. running dollar total (logged usage x live prices) reaches CAP_USD;
  2. any model's mean cost per loop so far (loops started) exceeds 1.5x its per-loop assumption.
On a stop the triggering call is written to stop.json and the run ends.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

CAP_USD = 2.98
MAX_TURNS = 4
MAX_TOKENS = 4096
EFFORT = "medium"  # same for all three models (Opus 5.5 and Haiku 5.5 default to medium; Sonnet 5.5 to high)
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]  # cheapest first, so a stop leaves data for all

# Live prices, USD per million tokens, checked 2026-11-04 on platform.claude.com/docs/en/about-claude/pricing.md.
# Sonnet 5.5 cache read is $0.10 (the 2026-10-06 cached table said $0.20). Haiku: prompts up to 100K tokens.
PRICES = {
    "claude-opus-5-5":   {"input": 4.00, "output": 20.00, "cache_read": 0.20, "cache_write": 5.00},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10, "cache_write": 2.50},
    "claude-haiku-5-5":  {"input": 0.10, "output": 0.50,  "cache_read": 0.01, "cache_write": 0.125},
}
# Per-loop assumptions (tracks/infra.md "Cost estimates", Sonnet recomputed with the live cache-read price).
ASSUMED_PER_LOOP = {"claude-opus-5-5": 0.129, "claude-sonnet-5-5": 0.0645, "claude-haiku-5-5": 0.0033}
OVERRUN = 1.5
GUARD_INPUT_TOKENS = 40_000  # pre-call guard: assume the next call could bill this much uncached input + MAX_TOKENS

SYSTEM = (
    "You answer questions about who holds US household mortgage and consumer credit, using only the tools "
    "provided (read-only data from the Fed's Z.1 Financial Accounts and the NY Fed Consumer Credit Panel). "
    "Quote only numbers returned by tools. If the data cannot answer, say so; never estimate.\n\n"
    "End your reply with exactly these lines:\n"
    "ANSWER: <one number, with its unit, e.g. 12.3% or 0.123 or 4.56 trillion or 1.2 pp>\n"
    "QUARTER: <quarter like 2007Q4 if the question asks which quarter, else none>"
)


# ---------------------------------------------------------------- cost and stops

def usage_dict(usage) -> dict:
    get = (lambda k: usage.get(k)) if isinstance(usage, dict) else (lambda k: getattr(usage, k, None))
    return {k: int(get(k) or 0) for k in
            ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}


def call_cost(model: str, u: dict) -> float:
    p = PRICES[model]
    return (u["input_tokens"] * p["input"] + u["output_tokens"] * p["output"]
            + u["cache_read_input_tokens"] * p["cache_read"]
            + u["cache_creation_input_tokens"] * p["cache_write"]) / 1e6


class Stop(Exception):
    pass


@dataclass
class Budget:
    cap: float = CAP_USD
    total: float = 0.0
    by_model: dict = field(default_factory=dict)  # model -> [cost, loops started]

    def start_loop(self, model: str) -> None:
        self.by_model.setdefault(model, [0.0, 0])[1] += 1

    def guard(self, model: str) -> None:
        p = PRICES[model]
        worst = (GUARD_INPUT_TOKENS * p["cache_write"] + MAX_TOKENS * p["output"]) / 1e6
        if self.total + worst >= self.cap:
            raise Stop(f"pre-call guard: total ${self.total:.4f} + worst-case next {model} call ${worst:.4f} "
                       f">= cap ${self.cap:.2f}")

    def add(self, model: str, cost: float) -> None:
        self.total += cost
        self.by_model.setdefault(model, [0.0, 1])[0] += cost
        if self.total >= self.cap:
            raise Stop(f"cap: running total ${self.total:.4f} >= ${self.cap:.2f}")
        spent, loops = self.by_model[model]
        mean = spent / loops
        if mean > OVERRUN * ASSUMED_PER_LOOP[model]:
            raise Stop(f"overrun: {model} mean ${mean:.4f}/loop over {loops} loop(s) > "
                       f"{OVERRUN}x assumption ${ASSUMED_PER_LOOP[model]}")


# ---------------------------------------------------------------- scoring (rule fixed in pilot_questions.yaml)

NUM = r"[-+]?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?"


def parse_answer(text: str) -> tuple[float | None, str, str | None]:
    """Return (number, unit text, quarter) from the ANSWER/QUARTER lines (last occurrence)."""
    ans = re.findall(r"ANSWER:\s*(.+)", text or "")
    qtr = re.findall(r"QUARTER:\s*(\d{4})\s*-?\s*Q([1-4])", text or "", flags=re.I)
    quarter = f"{qtr[-1][0]}Q{qtr[-1][1]}" if qtr else None
    if not ans:
        return None, "", quarter
    m = re.search(NUM, ans[-1])
    if not m:
        return None, ans[-1].strip(), quarter
    return float(m.group(0).replace(",", "")), ans[-1][m.end():].strip().lower(), quarter


def to_unit(value: float, unit_text: str, unit: str) -> float:
    """Read the model's number in its stated unit, converted to the question's unit."""
    u = unit_text
    if unit == "share":
        return value / 100 if u.startswith("%") or "percent" in u else value
    if unit == "usd_tn":
        if u.startswith(("trillion", "tn", "t ")) or u == "t":
            return value
        if u.startswith(("billion", "bn", "b ")) or u == "b":
            return value / 1e3
        if u.startswith(("million", "mn", "m ")) or u == "m":
            return value / 1e6
        return value
    return value  # pp


def score(answer_text: str, gold: dict) -> dict:
    value, unit_text, quarter = parse_answer(answer_text)
    if value is None:
        return {"correct": False, "parsed": None, "unit_text": unit_text, "quarter": quarter, "why": "no number"}
    v = to_unit(value, unit_text, gold["unit"])
    ok = abs(v - gold["gold"]) <= gold["tolerance"]
    why = None if ok else f"|{v:.6g} - {gold['gold']:.6g}| > {gold['tolerance']}"
    if gold.get("quarter") and quarter != gold["quarter"]:
        ok, why = False, f"quarter {quarter} != {gold['quarter']}"
    return {"correct": ok, "parsed": v, "unit_text": unit_text, "quarter": quarter, "why": why}


# ---------------------------------------------------------------- the loop

def block_dicts(content) -> list[dict]:
    return [b if isinstance(b, dict) else b.model_dump(exclude_none=True) for b in content]


def run_loop(client, model: str, q: dict, tools: list[dict], call_tool, budget: Budget, log) -> dict:
    budget.start_loop(model)
    messages = [{"role": "user", "content": q["question"]}]
    system = [{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}]
    loop_cost, final_text, stop_reason = 0.0, "", None
    for turn in range(1, MAX_TURNS + 1):
        budget.guard(model)
        t0 = time.monotonic()
        err = None
        try:
            resp = client.messages.create(
                model=model, max_tokens=MAX_TOKENS, system=system, tools=tools, messages=messages,
                output_config={"effort": EFFORT}, cache_control={"type": "ephemeral"})
        except Exception as e:  # logged and counted as an unanswered loop; no spend recorded for a failed call
            err = f"{type(e).__name__}: {str(e)[:300]}"
            resp = None
        latency = round(time.monotonic() - t0, 3)
        if resp is None:
            log({"qid": q["id"], "model": model, "turn": turn, "error": err, "latency_s": latency})
            break
        u = usage_dict(resp.usage)
        cost = call_cost(model, u)
        loop_cost += cost
        stop_reason = resp.stop_reason
        content = block_dicts(resp.content)
        text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
        tool_uses = [b for b in content if b.get("type") == "tool_use"]
        log({"qid": q["id"], "model": model, "turn": turn, "usage": u, "cost_usd": round(cost, 6),
             "latency_s": latency, "stop_reason": stop_reason, "text": text,
             "tool_calls": [{"name": b["name"], "input": b["input"]} for b in tool_uses]})
        budget.add(model, cost)  # may raise Stop; the call is already logged
        final_text = text or final_text
        if stop_reason != "tool_use" or not tool_uses:
            break
        messages.append({"role": "assistant", "content": content})
        results = []
        for b in tool_uses:
            try:
                out, is_err = json.dumps(call_tool(b["name"], b["input"]), default=str), False
            except Exception as e:
                out, is_err = f"{type(e).__name__}: {e}", True
            results.append({"type": "tool_result", "tool_use_id": b["id"], "content": out, "is_error": is_err})
        messages.append({"role": "user", "content": results})
    return {"loop_cost": loop_cost, "final_text": final_text, "stop_reason": stop_reason, "turns": turn}


# ---------------------------------------------------------------- tools and clients

def mcp_tools():
    """Tool definitions and an in-process caller for the household-credit MCP server, snapshot backend."""
    for k in ("DATABASE_URL_READONLY", "DATABASE_URL"):
        os.environ.pop(k, None)
    import asyncio

    from household_credit_mcp import server
    defs = asyncio.run(server.mcp.list_tools())
    tools = [{"name": t.name, "description": t.description or "", "input_schema": t.inputSchema} for t in defs]
    fns = {t["name"]: getattr(server, t["name"]) for t in tools}
    if type(server.backend()).__name__ != "SnapshotBackend":
        raise SystemExit("refusing to run: MCP backend is not the snapshot backend")
    return tools, (lambda name, args: fns[name](**args))


def live_client():
    key = os.environ.get("HHDEBT_ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("HHDEBT_ANTHROPIC_API_KEY is not set")
    for k in ("ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
        os.environ.pop(k, None)
    import anthropic
    return anthropic.Anthropic(api_key=key, base_url="https://api.anthropic.com", max_retries=2)


class FakeClient:
    """Offline stand-in: one tool call, then an answer. Usage per call is configurable for stop tests."""

    def __init__(self, usage: dict | None = None, answer: str = "ANSWER: 56.38%\nQUARTER: none"):
        self.usage = usage or {"input_tokens": 3000, "output_tokens": 400,
                               "cache_read_input_tokens": 6000, "cache_creation_input_tokens": 0}
        self.answer, self.calls = answer, 0
        self.messages = self

    def create(self, **kw):
        self.calls += 1
        assert "api_key" not in kw and "headers" not in kw
        first = len(kw["messages"]) == 1
        content = ([{"type": "tool_use", "id": f"t{self.calls}", "name": "public_share", "input": {}}] if first
                   else [{"type": "text", "text": self.answer}])
        return type("R", (), {"usage": dict(self.usage), "stop_reason": "tool_use" if first else "end_turn",
                              "content": content})()


# ---------------------------------------------------------------- main

def run(client, tools, call_tool, outdir: Path, budget: Budget | None = None, models=MODELS) -> dict:
    questions = yaml.safe_load((HERE / "pilot_questions.yaml").read_text())["questions"]
    gold = {g["id"]: g for g in json.loads((HERE / "pilot_gold.json").read_text())}
    if not all(g["ok"] for g in gold.values()) or len(gold) != len(questions):
        raise SystemExit("pilot_gold.json is not 10/10 verified; run verify.py first")
    outdir.mkdir(parents=True, exist_ok=True)
    budget = budget or Budget()
    calls = (outdir / "calls.jsonl").open("w")
    results, stop = [], None

    def log(rec):
        rec["ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        calls.write(json.dumps(rec) + "\n")
        calls.flush()

    try:
        for q in questions:
            for model in models:
                loop = run_loop(client, model, q, tools, call_tool, budget, log)
                s = score(loop["final_text"], gold[q["id"]])
                results.append({"qid": q["id"], "model": model, **{k: v for k, v in loop.items() if k != "final_text"},
                                **s, "gold": gold[q["id"]]["gold"]})
    except Stop as e:
        stop = {"reason": str(e), "at": json.loads((outdir / "calls.jsonl").read_text().splitlines()[-1])
                if (outdir / "calls.jsonl").stat().st_size else None}
    finally:
        calls.close()
    summary = {"cap_usd": budget.cap, "total_usd": round(budget.total, 6), "stop": stop, "per_model": {}}
    for m, (spent, loops) in budget.by_model.items():
        rs = [r for r in results if r["model"] == m]
        summary["per_model"][m] = {
            "loops_started": loops, "loops_scored": len(rs), "spent_usd": round(spent, 6),
            "mean_per_loop_usd": round(spent / loops, 6) if loops else None,
            "assumed_per_loop_usd": ASSUMED_PER_LOOP[m],
            "pilot_correct": sum(r["correct"] for r in rs)}
    (outdir / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    (outdir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fake", action="store_true", help="offline rehearsal with a fake client")
    g.add_argument("--live", action="store_true", help="real API calls (spends money)")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    tools, call_tool = mcp_tools()
    date = datetime.now(timezone.utc).date().isoformat()
    out = a.out or (HERE / (f"pilot-{date}" if a.live else f"pilot-fake-{date}"))
    client = live_client() if a.live else FakeClient()
    summary = run(client, tools, call_tool, out)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
