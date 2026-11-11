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
    "Public means federal government, GSEs and agency pools, and state and local governments.",
    "Crisis test: no detectable rise in the public share after recession peaks (placebo p ≈ 0.30, low power).",
  ],
  caveats: [
    { title: "Holding is not bearing", body: "Bank-held FFEL, FHA and VA loans count as private, so public risk is understated; GSE risk transfer pushes the other way." },
    { title: "About 13% of liabilities are out of scope", body: "Mainly nonprofit commercial mortgages and other loans." },
    { title: "Student loans before 2006 are imputed", body: "A linear ramp from 1965, flagged as estimated. Without it, uncollateralized debt jumps from 7.6% to 11.5% in 2006 Q1." },
    { title: "Durables proxy", body: "Vehicle collateral is proxied by all consumer durables, so auto coverage is overstated." },
    { title: "Buy-now-pay-later is missing", body: "Mostly unreported to credit bureaus and absent from Z.1." },
    { title: "2010 accounting break", body: "FAS 166 and 167 moved agency pools onto GSE balance sheets. The public share is unaffected." },
    { title: "Fed MBS is rate risk", body: "It sits inside agency pools and is never added on top; the agencies keep the credit risk." },
    { title: "NY Fed and Z.1 can disagree", body: "NY Fed: a 5% sample of credit files, mortgages down $74B in 2026 Q2. Z.1: lenders' balance sheets, up $150B before seasonal adjustment." },
    { title: "Student-loan delinquency", body: "Defaulted loans returned to credit reports in May 2025; the jump is partly re-reporting." },
    { title: "Z.1 revises history", body: "Every vintage is kept; this site shows the latest." },
  ],
  catalogIntro: "Every series the pipeline loads, from pipeline/series_catalog.yaml.",
};
