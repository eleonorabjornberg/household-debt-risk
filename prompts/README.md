# Prompt archive

This folder keeps a record of the prompts typed in Claude Code cloud sessions for this project.

- **One dated file per session.** `2026-10-27_build-session.md` holds the typed prompts from session `session_01GDxCQ7VknqvF4GHqeAt7mG` (27 to 29 Oct 2026). Each prompt has a UTC timestamp heading and is quoted in full.
- **Audit and Phase 0 session.** `2026-11-03_audit-and-phase0.md` holds the typed prompts from session `session_01GDxCQ42apfBERQ1Fw4qyjV` (3 to 4 Nov 2026, 19 prompts). Under each prompt, a `Commits:` line lists the commits made after it and before the next prompt.
- **Coordinator session.** `2026-11-04_coordinator-session.md` holds the typed prompts from session `session_01GDxCQ4PEo3YCh72CZhKaU4` (4 Nov 2026, 00:04 to 04:29 UTC, 28 prompts). Prompts marked `<!-- unsure: ... -->` are kept as typed but may be launch text, a slash command or reply-form text.
- **Prompts are verbatim.** Wording, line breaks and pasted text are kept as typed. Only the person's own messages are included. Tool output, subagent reports, peer-session messages and system notices are left out.
- **Secrets are redacted.** Passwords, tokens, API keys and connection strings are replaced with `[REDACTED]`. If you find an unredacted secret here, remove it and rotate the credential.
- **Agent and skill prompts are not duplicated here.** Prompts that define agents or skills live with their definitions in `.claude/` and are referenced from there, not copied into this folder.
