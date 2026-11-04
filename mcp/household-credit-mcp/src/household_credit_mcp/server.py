"""FastMCP server: read-only tools over the household-debt-risk warehouse (stdio)."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import core
from .backends import get_backend

mcp = FastMCP("household-credit-mcp", instructions=(
    "Read-only data about who holds US household mortgage + consumer credit (Fed Z.1) and NY Fed CCP delinquency "
    "by type. Quote only numbers returned by tools, with their vintage and caveats. If a tool returns refused=true, "
    "say so and offer the nearest_answerable alternative; never fill the gap with an estimate."))

_backend = None


def backend():
    global _backend
    if _backend is None:
        _backend = get_backend()
    return _backend


@mcp.tool()
def list_series(role: str | None = None, source: str | None = None) -> dict:
    """List catalogued series (id, source, role, description). Filter by role (e.g. mortgage_holder, cc_type) or source (z1, fred, nyfed)."""
    return core.list_series(backend(), role, source)


@mcp.tool()
def describe_series(id: str) -> dict:
    """Describe one catalogued series by ID (e.g. FL153166400): role, risk bucket, units, caveats."""
    return core.describe_series(backend(), id)


@mcp.tool()
def public_share(start: str | None = None, end: str | None = None, measure: str = "total") -> dict:
    """Public holders' share of household 1-4 family mortgages + consumer credit, quarterly (Z.1). Quarters like 2026Q2; default is the latest quarter. measure: total | mortgage | consumer_credit. Public = federal + GSE/agency pools + state & local."""
    return core.public_share(backend(), start, end, measure)


@mcp.tool()
def holdings_by_bucket(quarter: str | None = None) -> dict:
    """The six risk buckets for one quarter (e.g. 2007Q4): nominal $ millions and share of scope, with mortgage/consumer split. Default is the latest quarter."""
    return core.holdings_by_bucket(backend(), quarter)


@mcp.tool()
def crisis_windows(crisis_id: str | None = None, metric: str = "public_share") -> dict:
    """Crisis event windows (-8..+16 quarters). Lists crises with the metric at t0 and changes after 4/8/16 quarters (percentage points for shares). metric examples: public_share, share:gse_agency, coverage:home_backed."""
    return core.crisis_windows(backend(), crisis_id, metric)


@mcp.tool()
def collateral_coverage(start: str | None = None, end: str | None = None) -> dict:
    """Collateral value / debt by collateral class (home-backed, vehicle-backed, uncollateralized, other), quarterly. Default is the latest quarter."""
    return core.collateral_coverage(backend(), start, end)


@mcp.tool()
def nyfed_by_type(start: str | None = None, end: str | None = None) -> dict:
    """NY FED Consumer Credit Panel (NOT Z.1): balances and serious-delinquency transitions by loan type (mortgage, heloc, auto, credit_card, student, other), 2003Q1+."""
    return core.nyfed_by_type(backend(), start, end)


@mcp.tool()
def lookup_claim(text_or_id: str) -> dict:
    """Find registered claims in claims/register.csv by claim id or words, with validation status (PASS / UNVERIFIED / ESTIMATE)."""
    return core.lookup_claim(backend(), text_or_id)


@mcp.tool()
def data_coverage() -> dict:
    """What the data can and cannot answer, with covered quarters."""
    return core.data_coverage(backend())


@mcp.tool()
def check_answerable(question: str) -> dict:
    """Pre-check a natural-language question. Returns a structured refusal (reason + nearest answerable tool) for questions the data cannot answer: holder-by-type splits, forecasts, borrower-level, geography, out-of-range quarters."""
    return core.check_answerable(backend(), question)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
