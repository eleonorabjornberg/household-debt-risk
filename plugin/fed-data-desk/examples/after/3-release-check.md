# Job 3, after: `/fed-data-desk:release-check` (z1-release-update skill)

Step 1, detect (live, 2026-11-04):
```
Nothing new. live: 64219006 bytes, Last-Modified 2026-09-11 16:00 GMT; repo: 64219006 bytes, Z1.csv dated 2026-09-11, meta.json vintages.z1 2026-09-11
previous zip (keep as comparison vintage): data/raw/z1/83b8eded0bc7f9b7_FRB_Z1_csv.zip
```

Nothing is new today, so the skill stops here. For what a release produces, here is the start of the "what moved" note (step 5) from a rehearsal of the 2026-06 → 2026-09 release, generated 2026-11-04 with the Fed's archived per-table zip as the previous vintage:

```markdown
# What moved: 2026-06-10 to 2026-09-11

Previous vintage: 2026-06-10 (latest quarter 2026Q1). Current vintage: 2026-09-11 (latest quarter 2026Q2). Scope is 1-4 family mortgages plus consumer credit of households and nonprofits; public = federal, GSE and agency pools, state and local holders. Computed from the raw Z.1 files; figures are not edited.

## New quarters

2026Q2

## Headline, 2026Q2

| Measure | Level | q/q | y/y |
|---|---|---|---|
| Public share of scope | 56.4% | -0.2 pp | -0.2 pp |
| Public debt | $10.77T | +$0.07T | +$0.26T |
| Scope total | $19.10T | +$0.20T | +$0.53T |

q/q is against 2026Q1, y/y against 2025Q2, both as published in the current vintage (so they include revisions).

## Risk buckets, share of scope, 2026Q2

| Bucket | Share | q/q | y/y |
|---|---|---|---|
| federal_direct | 8.8% | -0.1 pp | +0.1 pp |
| gse_agency | 47.0% | -0.1 pp | -0.3 pp |
| state_local | 0.6% | 0.0 pp | 0.0 pp |
| banks_credit_unions | 33.6% | +0.2 pp | +0.1 pp |
| private_securitization | 3.6% | +0.1 pp | +0.4 pp |
| nonbank_other | 6.4% | -0.1 pp | -0.2 pp |

## Revisions to history
```
