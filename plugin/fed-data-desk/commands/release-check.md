---
description: Check for a new Fed Z.1 release and, if there is one, run the release update up to the approval gates (z1-release-update)
---
Use the `z1-release-update` skill. Start with step 1 (detect). If nothing is new, say so with the numbers the script printed and stop. Otherwise run the steps in order and stop at every **ASK** gate; never load the database, commit, push or deploy without an explicit yes.
