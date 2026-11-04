#!/usr/bin/env bash
# Fast checks that must pass before any commit: the claims register and the offline test suites.
# Used by the Claude Code PreToolUse hook (pre_commit.sh) and by the git hook in .githooks/pre-commit.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
fail=0
out=$(uv run -q --project pipeline python claims/check_register.py 2>&1) || { echo "claims/check_register.py failed:"; echo "$out" | grep -v UV_NATIVE | tail -20; fail=1; }
out=$(uv run -q --project pipeline pytest -q claims research validation/test_run.py .claude/skills/z1-release-update/tests 2>&1) || { echo "pytest failed:"; echo "$out" | grep -v UV_NATIVE | tail -20; fail=1; }
exit $fail
