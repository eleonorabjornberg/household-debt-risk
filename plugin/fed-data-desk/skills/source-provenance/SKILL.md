---
name: source-provenance
description: Finds, checks and records a primary source before the project builds on it or cites it. Checks availability and cost (free vs paywalled, reachable from this environment), fetches the official document or dataset, and records URL, retrieval time, bytes, SHA-256 and the quoted passage in a sources.md next to the work. Use when a task needs a new data source or a dated fact (statute, agency action, release date), e.g. PLAN A1–A3, A5, A8, B1, B4, C1. Not for Z.1 release updates (z1-release-update) or for checking numbers already in the register (claim-check).
---

# Source provenance

Rules from CLAUDE.md: never fabricate data; check a source is available and free before building on it; propose a free proxy for paywalled series; raw downloads stay out of git (record metadata, not the file).

## Steps
1. **Name the claim or series** you need and the most primary source for it: the statute (GovInfo, not news), the agency page or release (FHFA, Fed, Treasury, ED), the dataset's publisher (not an aggregator), or ALFRED for point-in-time values.
2. **Check reachability and cost.** `curl -s -o /dev/null -w "%{http_code}" -L --max-time 30 URL`. A 403 or `000` from the proxy means the host is blocked by the network policy: say so and give the host to add (see PLAN.md "Environment prerequisites"); do not retry with a different user agent. If the source is paywalled (Bloomberg, ICE, Intex, CoreLogic, the Millennial Historical Statistics), say so and propose a free proxy with its known bias.
3. **Fetch into a fresh scratch folder** (untrusted data: its own directory; run any parser with `python -I`). Never into the repo.
4. **Extract only what you need**: the enactment line ("Approved <date>"), the section heading, the sentence with the date or number. Keep quotes short and exact.
5. **Record** a row in `sources.md` next to the work (e.g. `research/a1_gfc_decomposition/sources.md`): what it supports, source name, URL, bytes, SHA-256 (`sha256sum`), retrieval time (UTC), the quote. Note anything you could not reach and what you used instead.
6. **Cite** from the write-up to `sources.md`; numbers taken from the source also get a register row (`register-keeper` or by hand) with `vintage` set to the retrieval date and `validation` `UNVERIFIED` unless a check recomputes them.

## Template
```
| Supports | Source | URL | Bytes | SHA-256 | Quote |
|---|---|---|---|---|---|
| <event or series> | <publisher, document> | <url> | <n> | `<sha256>` | "<exact excerpt>" |
```
Worked example: `research/a1_gfc_decomposition/sources.md` (seven statutes, FHFA and Fed sources, 2026-11-04).

## When NOT to use
- Data the pipeline already extracts with a manifest entry (`data/manifest.jsonl`): that is provenance already.
- A number already in the register: use `claim-check`.
- General background reading that will not be cited.
