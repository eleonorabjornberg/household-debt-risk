# Job 2, after: the household-credit MCP server (in the plugin's .mcp.json), tool `public_share`

Call: `public_share(start="2026Q2", end="2026Q2", measure="mortgage")`, made over stdio JSON-RPC with the command in `.mcp.json`, from the repo root, using the snapshot backend (`DATABASE_URL_READONLY` unset).

Note: when this example was recorded, with `DATABASE_URL_READONLY` set and the database host unreachable (as in this cloud sandbox), the same call returned an error (`failed to resolve host ...`). That was fixed the same night: the server now falls back to the snapshots and adds a `backend_note` (`mcp/household-credit-mcp/tests/test_fallback.py`).

```json
{
  "ok": true,
  "tool": "public_share",
  "backend": "snapshot",
  "source": "z1",
  "vintage": {
    "source_vintage": "2026-09-11",
    "all": {
      "fred": "2026-10-27",
      "nyfed": "2026-10-27",
      "z1": "2026-09-11",
      "snapshot_generated_at": "2026-10-27T22:13:44+00:00",
      "source": "meta.json (database export)"
    }
  },
  "units": {
    "public_share": "fraction 0-1 (display as %)",
    "public_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "scope_total_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "measure": "mortgage"
  },
  "series_ids": [
    "FL153165105",
    "FL893065105",
    "FL313065105",
    "FL403065105",
    "FL413065105",
    "FL213065103"
  ],
  "caveats": [
    "Z.1 levels are end-of-quarter and not seasonally adjusted.",
    "Holding is not a guarantee: a public holder owning a loan is not the same as the public guaranteeing it, and a private holder may be protected by a guarantee.",
    "Mortgage holders are reported for ALL 1-4 family mortgages (incl. business borrowers) and apportioned to households by each holder's share; this is a method, not a published Z.1 holder split for households.",
    "Scope = household and nonprofit 1-4 family mortgages + consumer credit (FL154104015), about 87% of total household liabilities; it excludes HELOCs-as-separate-line, business debt and other liabilities.",
    "Public = federal government (direct) + GSEs & agency pools + state & local governments. Dollars are nominal.",
    "fed_mbs_musd (Fed MBS, WSHOMCB) is a QE overlay already inside agency pools; never add it."
  ],
  "data": [
    {
      "quarter": "2026Q2",
      "date": "2026-06-30",
      "public_share": 0.6555413006,
      "public_share_display": "65.6%"
    }
  ]
}
```
