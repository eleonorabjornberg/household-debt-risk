"""Copy the project's skills and subagents into the Fed Data Desk plugin (PLAN D7).

    python3 plugin/sync.py           # refresh plugin/fed-data-desk/skills and agents from .claude/
    python3 plugin/sync.py --check   # exit 1 if the plugin copies are stale (CI)

.claude/skills and .claude/agents stay the source of truth; the plugin carries copies so it can be
installed on its own (claude plugin marketplace add ./plugin). Caches and test fixtures' __pycache__ are
left out. Stdlib only.
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "plugin" / "fed-data-desk"
SKILLS = ["claim-check", "research-memo", "z1-release-update", "chart-from-sql", "source-provenance", "preregister"]
AGENTS = ["skeptic", "quant-reviewer", "editor", "analyst", "register-keeper", "prompt-archivist"]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def pairs():
    for s in SKILLS:
        yield ROOT / ".claude" / "skills" / s, DST / "skills" / s
    for a in AGENTS:
        yield ROOT / ".claude" / "agents" / f"{a}.md", DST / "agents" / f"{a}.md"


def same_tree(a: Path, b: Path) -> bool:
    if a.is_file():
        return b.is_file() and filecmp.cmp(a, b, shallow=False)
    if not b.is_dir():
        return False
    c = filecmp.dircmp(a, b, ignore=["__pycache__", ".pytest_cache"])
    if c.left_only or c.right_only or c.diff_files or c.funny_files:
        return False
    return all(same_tree(a / d, b / d) for d in c.common_dirs)


def main(argv: list[str]) -> int:
    stale = [str(d.relative_to(ROOT)) for s, d in pairs() if not same_tree(s, d)]
    if "--check" in argv:
        if stale:
            print("stale plugin copies (run python3 plugin/sync.py):\n  " + "\n  ".join(stale))
            return 1
        print("plugin copies up to date")
        return 0
    for s, d in pairs():
        if d.exists():
            shutil.rmtree(d) if d.is_dir() else d.unlink()
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(s, d, ignore=IGNORE) if s.is_dir() else shutil.copy2(s, d)
    print(f"plugin: {len(SKILLS)} skills, {len(AGENTS)} agents copied ({len(stale)} were stale)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
