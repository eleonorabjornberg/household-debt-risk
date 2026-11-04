"""Records real tool calls over stdio (snapshot backend) into examples/transcripts.md.
Run: uv run python examples/record_transcripts.py"""
import json, os, sys
from pathlib import Path
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CALLS = [
    ("Public share, 2026Q2", "public_share", {"start": "2026Q2", "end": "2026Q2"}),
    ("Risk buckets, 2007Q4", "holdings_by_bucket", {"quarter": "2007Q4"}),
    ("Risk buckets, 2011Q4", "holdings_by_bucket", {"quarter": "2011Q4"}),
    ("Claim lookup", "lookup_claim", {"text_or_id": "public_share_2026q2"}),
    ("Refusal 1: auto loans held by banks (holder x type)", "check_answerable", {"question": "How much of auto loans are held by banks?"}),
    ("Refusal 2: a forecast", "check_answerable", {"question": "Forecast the public share for 2028"}),
    ("Refusal 3: a quarter outside coverage (tool-level)", "public_share", {"start": "2027Q1", "end": "2027Q4"}),
    ("Refusal 4: state split", "check_answerable", {"question": "Household debt by state"}),
    ("Refusal 5: borrower-level", "check_answerable", {"question": "Which borrowers have the highest loan-level delinquency?"}),
]

def payload(res):
    sc = getattr(res, "structuredContent", None)
    return sc.get("result", sc) if sc else json.loads(res.content[0].text)

def trim(o):
    # keep transcripts readable: only truncate long caveat prose, never numbers
    return o

async def main():
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL_READONLY"}
    params = StdioServerParameters(command=sys.executable, args=["-m", "household_credit_mcp.server"], env=env)
    out = ["# Recorded tool calls", "",
           "Real calls made through an MCP stdio client against the snapshot backend (`web/public/data`, "
           "Z.1 vintage 2026-09-11). Output is verbatim JSON from the server. Regenerate with "
           "`uv run python examples/record_transcripts.py`.", ""]
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for title, tool, args in CALLS:
                res = payload(await s.call_tool(tool, args))
                out += [f"## {title}", "", f"`{tool}({json.dumps(args)})`", "", "```json",
                        json.dumps(res, indent=2), "```", ""]
    Path(__file__).with_name("transcripts.md").write_text("\n".join(out))

anyio.run(main)
