// Copy for /methods, moved from web/content/story.ts (Eleonora's site-visible (b), 2026-11-07: one site).
// Numbers in this file are scanned by claims/check_register.py; each has a register row located here.

export const methods = {
  title: "Methods",
  lede: "Where the numbers come from, how they are combined, and what they leave out.",
  lineage: [
    { step: "Sources", text: "Fed Z.1 Financial Accounts (quarterly CSV), FRED (CPI, disposable income, unemployment, Case-Shiller, Fed MBS holdings) and the NY Fed Household Debt and Credit report." },
    { step: "raw", text: "Every observation from every release is kept with its vintage date, because the Fed revises history each quarter." },
    { step: "core", text: "The latest vintage of each series, joined to dimensions for series, risk bucket and crisis." },
    { step: "mart", text: "Analysis-ready tables: debt by risk holder, public share, collateral coverage, crisis windows and NY Fed delinquency by loan type." },
    { step: "Outputs", text: "This site reads the mart tables directly, so the numbers match the warehouse." },
  ],
  scope: [
    "The unit is the household sector as the Fed defines it, which includes nonprofit organizations. Scope is home mortgages on 1–4 family properties plus consumer credit (Z.1 series FL154104015). That is about 87% of household liabilities; the remaining 13% is excluded.",
    "Z.1 reports who holds all 1–4 family mortgages, including those owed by businesses. We take each holder's share of that total and apply it to the household liability, so holder amounts are apportioned rather than reported. The 17 mortgage holders sum exactly to the all-sector total, and the 9 consumer-credit holders sum exactly to household consumer credit.",
    "Public means federal government, GSEs and agency pools, and state and local governments. Everything else is private.",
    "The crisis test compares the 16-quarter change in the public share after each NBER recession peak with the change over every other 16-quarter window, and with randomly placed and circularly shifted sets of dates (a placebo test). Result: no detectable excess after a crisis (p ≈ 0.30, low power).",
  ],
  caveats: [
    { title: "Holding a loan is not always bearing its risk", body: "Buckets are assigned by who holds the loan, which is not always who loses if it defaults. Bank-held FFEL student loans were federally guaranteed, and FHA and VA mortgages are government-insured even when a bank holds them, so the public share understates public credit risk. GSE credit-risk transfer deals push the other way, selling some of Fannie Mae's and Freddie Mac's credit risk to private investors." },
    { title: "Households include nonprofits", body: "The Fed's household sector bundles in nonprofit organizations. Their share of mortgage and consumer debt is small but not zero, and Z.1 does not report it separately for these series." },
    { title: "About 13% of liabilities are out of scope", body: "Commercial mortgages owed by nonprofits, deferred and unpaid life insurance premiums and other loans are excluded. The public share is a share of mortgages plus consumer credit, not of all household liabilities." },
    { title: "Consumer credit types are partly estimated", body: "Z.1 splits out revolving credit from 1968 and student loans only from 2006 Q1. Before 2006 student loans sit inside \"other non-revolving\"; the pipeline imputes them with a linear ramp from 1965 and flags those quarters as estimated, which removes a break that would otherwise make uncollateralized debt jump from 7.6% to 11.5% in 2006 Q1." },
    { title: "The durables proxy", body: "Z.1 has no series for the value of the vehicles that secure auto loans. We use the current-cost value of all consumer durable goods, which includes furniture and appliances, so vehicle coverage is overstated." },
    { title: "Buy-now-pay-later is missing", body: "BNPL loans are mostly not reported to credit bureaus or captured in Z.1 consumer credit. This 'phantom debt' is not in any figure here." },
    { title: "The 2010 accounting break", body: "FAS 166 and 167 moved most GSE-guaranteed pools onto Fannie Mae's and Freddie Mac's balance sheets in 2010. Holdings shift from agency pools to the GSEs that year. Both are in the same public bucket, so the public share is unaffected, but the split between them has a break." },
    { title: "Fed MBS is rate risk, not credit risk", body: "The Fed's agency MBS holdings are a subset of the agency pools, so they sit inside the public share and are never added to it. The Fed bears interest-rate risk on them; the credit risk stays with Fannie Mae, Freddie Mac and Ginnie Mae." },
    { title: "NY Fed and Z.1 can disagree", body: "Delinquency and the 2026 Q2 news hook come from the New York Fed's credit-report sample (a 5% sample of credit files). Everything else comes from Z.1, built from lenders' balance sheets. In 2026 Q2 the NY Fed shows mortgage balances down $74B; Z.1 shows them up $150B, before seasonal adjustment." },
    { title: "Student-loan delinquency is distorted", body: "After the 2020–2023 pause, defaulted federal student loans returned to credit reports when collections resumed in May 2025. The jump in delinquency transitions reflects re-reporting as much as new missed payments." },
    { title: "Z.1 revises history", body: "Each quarterly Z.1 release can revise past quarters. The pipeline keeps every vintage; this site shows the latest. The release used for this build is listed at the bottom of this page; later releases may shift numbers slightly." },
  ],
  catalogIntro: "Every series the pipeline loads, from pipeline/series_catalog.yaml.",
};
