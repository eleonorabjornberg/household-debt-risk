import { SHARED_LIMITS } from "@/lib/ask/shared-limits.generated";
// Limits live in claims/limits.json (one place for the site, the Ask API and the MCP; Eleonora, 2026-11-11).
// Copy for /methods, moved from web/content/story.ts (Eleonora's site-visible (b), 2026-11-07: one site).
// Cut to short form on 2026-11-11 (Eleonora: "10 times too much text"; review list P1).
// Numbers in this file are scanned by claims/check_register.py; each has a register row located here.

export const methods = {
  title: "Methods",
  lede: "Where the numbers come from, and what they leave out.",
  lineage: [
    { step: "Sources", text: "Fed Z.1, FRED and the NY Fed Household Debt and Credit report." },
    { step: "raw", text: "Every release, kept with its vintage date." },
    { step: "core", text: "The latest vintage of each series." },
    { step: "mart", text: "Analysis tables: holders, public share, collateral, crises, delinquency." },
    { step: "Site", text: "Reads the mart tables directly." },
  ],
  scope: [
    "Home mortgages on 1–4 family properties plus consumer credit: about 87% of household liabilities. The Fed's household sector includes nonprofits.",
    "Holder amounts are apportioned from Z.1 holder shares; the 17 mortgage holders and 9 consumer-credit holders sum exactly to their totals.",
    "Public means the federal government, GSEs and agency pools (the mortgages in those pools included), and state and local governments. Private means banks and credit unions, private securitization and REITs, and finance companies and other lenders.",
    "Crisis test: no detectable rise in the public share after recession peaks (placebo p ≈ 0.30, low power).",
  ],
  limits: SHARED_LIMITS,
  catalogIntro: "Every series the pipeline loads, from pipeline/series_catalog.yaml.",
};
