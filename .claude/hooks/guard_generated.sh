#!/usr/bin/env bash
# Claude Code PreToolUse hook (Edit|Write|NotebookEdit): results.json files are generated outputs.
# Hand edits are blocked; regenerate them with the script that writes them.
f=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // ""')
case "$f" in
  */results.json|results.json)
    echo "Blocked: $f is generated, never edited by hand (CLAUDE.md: no number is changed silently)." >&2
    echo "Regenerate it instead: validation/results.json <- validation/run.py; analysis/results.json <- analysis/notebook.py; research/<task>/results.json <- that folder's script." >&2
    exit 2 ;;
esac
exit 0
