# household-credit-mcp

Read-only MCP server over the household-debt-risk warehouse: who holds America's household mortgage and consumer credit (Fed Z.1) and how NY Fed CCP delinquency splits by loan type. Built to back "Ask Hot Potato" (D6), the question-to-SQL benchmark (E1) and the Cowork plugin (D7).

Every result carries values, units, series IDs, source vintage, the backend used, and caveats. Questions the data cannot answer return a structured refusal (`ok: false, refused: true, reason_code, reason, nearest_answerable`) with no numbers.

## Tools

| Tool | What |
|---|---|
| `list_series(role?, source?)`, `describe_series(id)` | Series catalog |
| `public_share(start?, end?, measure)` | Public share, `total` / `mortgage` / `consumer_credit` |
| `holdings_by_bucket(quarter?)` | Six risk buckets, $ and share |
| `crisis_windows(crisis_id?, metric?)` | Crisis event windows |
| `collateral_coverage(start?, end?)` | Collateral value / debt by class |
| `nyfed_by_type(start?, end?)` | NY Fed CCP (not Z.1) by loan type |
| `lookup_claim(text_or_id)` | `claims/register.csv` with validation status |
| `data_coverage()` | What the data can and cannot answer |
| `check_answerable(question)` | Pre-check; refuses holder-by-type, forecasts, borrower-level, geography, monthly, out-of-range |

Quarters are written `2026Q2`. Tools also refuse future and pre-coverage quarters rather than clamping.

## Backends

* Snapshot (default): `web/public/data/*.json` plus `meta.json` (vintages). Used when `DATABASE_URL_READONLY` is unset. Override the folder with `HOUSEHOLD_CREDIT_SNAPSHOT_DIR`.
* Postgres: set `DATABASE_URL_READONLY` (the `research_reader` login). The server sets the transaction read-only, `statement_timeout` 15 s, and runs only the parameterised SELECTs in `backends.ALLOWED_SQL`; no SQL ever comes from the client. `research_reader` cannot read raw/core vintages, so vintages still come from `meta.json` and the result says so.
* Unreachable database: the server probes the database once, at the first tool call. If it cannot connect (an unresolvable host, a refused connection or a timeout, as with the Supabase pooler from this project's cloud sandbox), it answers from the snapshots, with `backend: snapshot` and a `backend_note` giving the reason. Set `HOUSEHOLD_CREDIT_REQUIRE_DB=1` to fail instead. Tests: `tests/test_fallback.py`.

`lookup_claim` and the series catalog always read the repository files (`claims/register.csv`, `pipeline/series_catalog.yaml`), on either backend.

## Install (Claude Code)

```bash
cd mcp/household-credit-mcp && uv sync
claude mcp add household-credit -- uv --directory /ABS/PATH/household-debt-risk/mcp/household-credit-mcp run household-credit-mcp
# live database instead of snapshots: the URL stays in your environment, never in chat
claude mcp add household-credit -e DATABASE_URL_READONLY="$DATABASE_URL_READONLY" -- uv --directory /ABS/PATH/household-debt-risk/mcp/household-credit-mcp run household-credit-mcp
```

`.mcp.json` snippet:

```json
{
  "mcpServers": {
    "household-credit": {
      "command": "uv",
      "args": ["--directory", "/ABS/PATH/household-debt-risk/mcp/household-credit-mcp", "run", "household-credit-mcp"]
    }
  }
}
```

Not published to PyPI or any registry (needs approval). The server locates the repo by its path, so install from a checkout.

## Tests

```bash
uv run pytest        # snapshot backend, refusals, DB guard, stdio protocol smoke, C2/C3 cross-check
```

The live-DB test runs only when `DATABASE_URL_READONLY` is set and reachable, otherwise it skips.

`examples/transcripts.md` holds recorded real calls (`uv run python examples/record_transcripts.py`).
