"""MCP protocol-level smoke test: spawn the server over stdio and call two tools."""
import json
import os
import sys
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _payload(res):
    if getattr(res, "structuredContent", None):
        sc = res.structuredContent
        return sc.get("result", sc)
    return json.loads(res.content[0].text)


def test_stdio_smoke():
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL_READONLY"}
    params = StdioServerParameters(command=sys.executable, args=["-m", "household_credit_mcp.server"], env=env)

    async def run():
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                names = {t.name for t in (await s.list_tools()).tools}
                assert {"public_share", "holdings_by_bucket", "lookup_claim", "check_answerable", "data_coverage",
                        "crisis_windows", "collateral_coverage", "nyfed_by_type", "list_series", "describe_series",
                        "list_research", "get_research_writeup"} <= names
                a = _payload(await s.call_tool("public_share", {"start": "2026Q2", "end": "2026Q2"}))
                assert a["ok"] and a["backend"] == "snapshot" and a["data"][0]["public_share_display"] == "56.4%"
                b = _payload(await s.call_tool("check_answerable", {"question": "auto loans held by banks"}))
                assert b["refused"] and b["reason_code"] == "holder_by_type_not_available"
                c = _payload(await s.call_tool("get_research_writeup", {"task": "A3"}))
                assert c["ok"] and c["data"]["slug"] == "a3" and c["data"]["markdown"].startswith("# A3")

    anyio.run(run)
