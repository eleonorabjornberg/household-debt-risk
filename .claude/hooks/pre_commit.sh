#!/usr/bin/env bash
# Claude Code PreToolUse hook (Bash): before a `git commit`, run .claude/hooks/checks.sh.
# Exit 2 blocks the commit and shows the failure to Claude.
cmd=$(jq -r '.tool_input.command // ""')
echo "$cmd" | grep -qE '(^|[;&|(]|[[:space:]])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit\b' || exit 0
if ! out=$("${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/checks.sh" 2>&1); then
  echo "Commit blocked: fix these before committing." >&2
  echo "$out" >&2
  exit 2
fi
exit 0
