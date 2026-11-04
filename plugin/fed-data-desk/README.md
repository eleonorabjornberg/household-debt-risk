# Fed Data Desk (PLAN D7)

A Claude Code plugin that packages the household-debt-risk project's research tooling for a team working
in a clone of the repository.

| Component | What |
|---|---|
| Skills | `claim-check`, `research-memo`, `z1-release-update`, `chart-from-sql`, `source-provenance`, `preregister` |
| Commands | `/fed-data-desk:check`, `/fed-data-desk:memo`, `/fed-data-desk:release-check`, `/fed-data-desk:review` |
| Subagents | `skeptic`, `quant-reviewer`, `editor`, `analyst`, `register-keeper`, `prompt-archivist` |
| MCP | `household-credit` (read-only; snapshot backend, or the `research_reader` database when `DATABASE_URL_READONLY` is set) |

## Install
Run from the root of a clone of the repository, with `uv` installed:
```bash
claude plugin marketplace add ./plugin
claude plugin install fed-data-desk@household-debt-risk
```
Tested 2026-11-04 with Claude Code 2.1.318 in a throwaway config directory:
- `claude plugin validate` passes, with one warning: no icon;
- the install succeeded;
- `claude plugin details` lists 10 skills (6 skills plus 4 commands), 6 agents and 1 MCP server, at about 2.3k always-on tokens;
- the MCP command answers `initialize` and `tools/list` (10 tools).

The skills, agents and MCP server read repository files (`claims/register.csv`, `validation/`, `mcp/`), so the
plugin works only inside a clone, started from its root. No secrets are in the plugin; the database URL, if any,
stays in your environment.

## Source of truth
`.claude/skills/` and `.claude/agents/` hold the originals. `python3 plugin/sync.py` refreshes the copies here, and
`python3 plugin/sync.py --check` (in `make ci-static`) fails if they are stale.

## Before and after: three routine jobs
`examples/before/` shows the manual route; `examples/after/` shows the output of the script or tool the plugin
wires in, run directly on 2026-11-04 (a Claude session through the plugin would call the same scripts).
1. **Trace a number** (`/check`): grep and hand lookup vs claim-check's per-number MATCH with the recompute.
2. **Answer a data question** (MCP `public_share`): a bare fraction from a JSON file vs a value with series IDs,
   vintage, units and the holder-vs-guarantee caveats.
3. **Check for a new Z.1 release** (`/release-check`): HTTP headers compared by eye vs the detect verdict, and the
   "what moved" note a release produces (rehearsal of 2026-06 → 2026-09).

Memo drafting (`/memo`) is shown by the three logged memos in `skills/research-memo/examples/`.
