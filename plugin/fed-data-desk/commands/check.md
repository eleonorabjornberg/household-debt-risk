---
description: Trace every number in a sentence or file line to the claims register and recompute it (claim-check)
argument-hint: "<sentence>" | <file> [line]
---
Use the `claim-check` skill on: $ARGUMENTS

If the argument is a file path (optionally followed by a line number), run the script with `--file` (and `--line`). Otherwise pass the text. Report per number: token, register row, verdict, one line of evidence; MISMATCH and UNTRACED first; end with the SUMMARY line. Never edit the register or the copy.
