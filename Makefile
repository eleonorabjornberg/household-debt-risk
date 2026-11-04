# One-command reproduction (PLAN F2):  make all
#
#   ingest    download Z.1 / FRED / NY Fed, transform, export web/public/data snapshots
#             (loads the database only with LOAD=1 and DATABASE_URL set)
#   validate  independent recomputation of the headline numbers (validation/REPORT.md, results.json)
#   models    analysis notebook and every research/<task>/ script that writes results.json
#   build     source-register copies, then test and build atlas/ and web/
#   check     claims register, offline test suites, F1 link coverage, reproduction check
#
# Needs: uv, node >= 20.9, network to federalreserve.gov, fred.stlouisfed.org, newyorkfed.org.
# FRED_API_KEY is optional (ALFRED vintages). Nothing here touches production unless LOAD=1.
# `make ci` is the offline subset GitHub Actions runs on every push.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
UV ?= uv
PY := $(UV) run -q --project pipeline python
DATA := data
Z1_ZIP := $(DATA)/z1/FRB_Z1_csv.zip
Z1_CSV := $(DATA)/z1/Z1.csv
SITES := web atlas
LOAD ?= 0

.PHONY: test-db ci-static all ingest validate models build check ci test site-test site-build site-copies f1-links repro clean-data help

all: ingest validate models build check  ## everything, from a fresh clone

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

# ---------------------------------------------------------------- ingest
# Without LOAD=1, DATABASE_URL is dropped so snapshots come from this run's data/out, never the database.
ingest:  ## pipeline: extract -> transform [-> load] -> export snapshots
	cd pipeline && $(UV) sync -q && \
	  if [ "$(LOAD)" = "1" ]; then $(UV) run hhdebt run --export; else env -u DATABASE_URL $(UV) run hhdebt run --no-load --export; fi

$(Z1_ZIP):
	cd pipeline && $(UV) run hhdebt extract --sources z1

$(Z1_CSV): $(Z1_ZIP)
	unzip -o -q -d $(DATA)/z1 $(Z1_ZIP) Z1.csv && touch $@

# ---------------------------------------------------------------- validate
validate: $(Z1_ZIP)  ## validation suite (exit 1 on any FAIL)
	$(PY) validation/run.py --z1-zip $(Z1_ZIP)

# ---------------------------------------------------------------- models
models: $(Z1_CSV) $(Z1_ZIP)  ## analysis notebook + research scripts
	cd analysis && rm -f .cache/z1_extract.csv && \
	  Z1_CSV=$(abspath $(Z1_CSV)) $(UV) run -q --with pandas --with matplotlib --with numpy python -I notebook.py >/dev/null
	@for s in research/*/decompose.py research/*/run.py; do \
	  [ -f "$$s" ] || continue; echo "models: $$s"; $(PY) "$$s" --z1-zip $(Z1_ZIP); done

# ---------------------------------------------------------------- build
site-copies:  ## refresh lib/claims.json and the shared F1 files in each site
	node claims/site/sync.mjs

site-test:
	@for s in $(SITES); do (cd $$s && npm ci --no-audit --no-fund --silent && npm test --silent); done

site-build:
	@for s in $(SITES); do (cd $$s && npm run build --silent); done

build: site-copies site-test site-build  ## test and build both sites

# ---------------------------------------------------------------- check
# Offline: the database URLs are dropped so database tests skip (test-db runs them).
OFFLINE := env -u DATABASE_URL -u DATABASE_URL_READONLY
test:  ## offline Python suites (pipeline, claims, validation, research, skills, MCP)
	cd pipeline && $(OFFLINE) $(UV) run -q pytest -q
	$(OFFLINE) $(PY) -m pytest -q claims research validation/test_run.py .claude/skills/z1-release-update/tests
	cd mcp/household-credit-mcp && $(OFFLINE) $(UV) run -q pytest -q

test-db:  ## database tests (needs DATABASE_URL / DATABASE_URL_READONLY and a reachable host)
	cd pipeline && $(UV) run -q pytest -q tests/test_snapshot_and_db.py

f1-links:  ## after build: every register row is a link (F1), every chart has a text description (F4)
	@for s in $(SITES); do node claims/site/check_html.mjs --site $$s; node tools/check_chart_text.mjs --site $$s; done

repro:  ## regenerated results match the committed ones
	python3 tools/repro_check.py

check: test f1-links repro  ## after a full run
	$(PY) claims/check_register.py
	node claims/site/sync.mjs --check

# What CI runs on every push: no network, no secrets, no money.
ci: ci-static test site-test site-build f1-links

ci-static:  ## register check and stale-copy check (before any build rewrites the copies)
	$(PY) claims/check_register.py
	node claims/site/sync.mjs --check
	node web/scripts/make-downloads.mjs --check

clean-data:  ## remove downloaded data (data/ is gitignored)
	rm -rf $(DATA) analysis/.cache
