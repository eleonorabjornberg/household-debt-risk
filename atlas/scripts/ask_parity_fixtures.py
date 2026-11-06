"""Parity fixtures for the Ask Hot Potato tool port (atlas/lib/ask/tools.ts, PLAN D6).

    uv run --project mcp/household-credit-mcp python atlas/scripts/ask_parity_fixtures.py

Runs the Python MCP tools (household_credit_mcp.core, snapshot backend) on a fixed list of calls and writes
atlas/lib/ask/parity.fixtures.json. parity.test.ts runs the same calls through the TypeScript port and compares.
Regenerate after changing core.py, the catalog, the register or the snapshots.
"""
import json
import os
import sys
from pathlib import Path

for k in ("DATABASE_URL_READONLY", "DATABASE_URL"):
    os.environ.pop(k, None)
from household_credit_mcp import core  # noqa: E402
from household_credit_mcp.backends import SnapshotBackend  # noqa: E402

CALLS = [
    ("public_share", {}), ("public_share", {"start": "2007Q4", "end": "2011Q4"}),
    ("public_share", {"start": "1951Q4", "end": "1952Q4", "measure": "mortgage"}),
    ("public_share", {"end": "2026Q2", "measure": "consumer_credit"}), ("public_share", {"measure": "bogus"}),
    ("public_share", {"start": "1900Q1", "end": "2030Q4"}), ("public_share", {"start": "2027Q1"}),
    ("public_share", {"start": "1940Q1", "end": "1950Q4"}), ("public_share", {"start": "2026-06-30"}),
    ("public_share", {"start": "2011Q4", "end": "2007Q4"}), ("public_share", {"start": "May 2020"}),
    ("holdings_by_bucket", {}), ("holdings_by_bucket", {"quarter": "2007Q4"}), ("holdings_by_bucket", {"quarter": "1951Q4"}),
    ("holdings_by_bucket", {"quarter": "2030Q1"}), ("holdings_by_bucket", {"quarter": "1900Q1"}), ("holdings_by_bucket", {"quarter": "x"}),
    ("crisis_windows", {}), ("crisis_windows", {"crisis_id": "gfc_2007"}),
    ("crisis_windows", {"crisis_id": "covid_2020", "metric": "coverage:home_backed"}),
    ("crisis_windows", {"metric": "share:gse_agency"}), ("crisis_windows", {"crisis_id": "nope"}),
    ("crisis_windows", {"metric": "nope"}),
    ("collateral_coverage", {}), ("collateral_coverage", {"start": "2005Q4", "end": "2006Q2"}),
    ("collateral_coverage", {"start": "2030Q1"}),
    ("nyfed_by_type", {}), ("nyfed_by_type", {"start": "2003Q1", "end": "2003Q4"}), ("nyfed_by_type", {"start": "1999Q4"}),
    ("lookup_claim", {"text_or_id": "public_share_2026q2"}), ("lookup_claim", {"text_or_id": "public share 2011Q4"}),
    ("lookup_claim", {"text_or_id": "gfc jump"}), ("lookup_claim", {"text_or_id": ""}),
    ("lookup_claim", {"text_or_id": "zzzz qqqq"}),
    ("data_coverage", {}),
    ("list_series", {}), ("list_series", {"role": "mortgage_holder"}), ("list_series", {"source": "nyfed"}),
    ("describe_series", {"id": "FL153166400"}), ("describe_series", {"id": "fl155111005"}), ("describe_series", {"id": "XYZ"}),
] + [("check_answerable", {"question": q}) for q in [
    "What was the public share in 2026Q2?", "What will the public share be in 2027Q4?",
    "How many auto loans did banks hold in 2026Q2?", "Which state had the highest debt?",
    "What was the median credit score of borrowers?", "What was the public share on 15 May 2026, monthly?",
    "What was the public share in 1945?", "What was the NY Fed balance in 2031?",
    "Delinquency of loans held by banks", "Delinquency by loan type held by banks",
    "Will mortgages rise next year?", "public share by 2030", "Credit card debt held by credit unions",
]]

def main() -> None:
    be = SnapshotBackend()
    out = []
    for tool, args in CALLS:
        fn = getattr(core, tool)
        out.append({"tool": tool, "args": args, "output": fn(be, **args)})
    dst = Path(__file__).resolve().parents[1] / "lib" / "ask" / "parity.fixtures.json"
    dst.write_text(json.dumps(out, default=str) + "\n")
    print(f"{len(out)} parity fixtures -> {dst}")

if __name__ == "__main__":
    sys.exit(main())
