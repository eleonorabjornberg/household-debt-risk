// All reader-facing copy for the site lives here, so it can be revised from analysis/findings.md
// without touching components.
//
// Conventions
// - Analysis numbers are hard-coded in `facts` below, sourced from analysis/results.json (and
//   findings.md). Update them there when the analysis is re-run; the copy reads from `facts`.
// - `{token}` placeholders are filled from the live mart data at render time (see `tokens` in
//   app/page.tsx). Use them only for labels that must track the charts ({latestQuarter},
//   {firstQuarter}, {firstYear}, {latestYear}, {publicShareLatest}, {nyQuarter}, {nyTotal},
//   {nyMortgageChangeAbs}).
// - Never put a NY Fed credit-report figure next to a Z.1 figure without saying which is which.
//   They measure different things and disagree in 2026Q2 (see `nyFedVsZ1`).
// - `// TODO(findings)` marks claims still to be checked against analysis/findings.md.
// - Crisis notes are keyed by the calendar year of the crisis start quarter (core.dim_crisis.start_q).

/** Analysis results (Z.1 unless stated). Source: analysis/results.json, vintage Z.1 2026-09-11. */
export const facts = {
  latestQuarter: "2026 Q2",
  publicShareFirst: "3.2%", // 1952Q1
  publicShareLatest: "56.4%", // 2026Q2
  publicLatest: "$10.77T",
  scopeLatest: "$19.10T",
  publicSharePeak: "58.6%",
  publicSharePeakQ: "2021 Q1",
  gse1980s: "+18.8 pts", // GSE & agency pools, 1979Q4–1989Q4
  public1980s: "+19.0 pts",
  placeboP: "0.30", // crisis windows vs random 16-quarter windows
  crisesAboveMedian: "5 of 11",
  gfcFrom: "36.1%", // 2007Q4
  gfcTo: "49.2%", // 2011Q4
  gfcDelta: "+13.1 pts",
  gfcPercentile: "98th",
  gfcPrivateShrinkPct: "24.6%",
  gfcPrivateShrink: "$2.07T",
  gfcPrivateLabelShare: "12.5 pts",
  gfcPublicGrowPct: "29%",
  gfcPublicGrow: "$1.40T",
  dotcomFrom: "40.6%",
  dotcomTo: "36.8%",
  dotcomDelta: "−3.8 pts",
  preGfcDecline: "−5.0 pts", // 1999Q4–2007Q4
  covidDelta: "+1.0 pts",
  shocksMax: "less than 1 point",
  publicBookHome: "85%",
  studentInPublicBook2007: "2.4%",
  studentInPublicBookNow: "14.9%",
  publicShareOfStudent: "86%",
  publicShareOfUncoll: "51%",
  publicShareOfUncoll2007: "7%",
  mortgagesOfScope: "73%",
  homeCoverage: "3.56×",
  homeCushion: "72%",
  homeCoverageLow: "1.85×",
  homeCoverageLowQ: "2012 Q1",
  uncollShare: "16.6%",
  fedMbsPeak: "16.4%",
  fedMbsPeakQ: "2022 Q1",
  fedMbsPeakUsd: "$2.72T",
  fedMbsNow: "10.3%",
  debtToIncomeNow: "80%",
  debtToIncome2007: "124%",
  // NY Fed Household Debt and Credit Report (credit-report sample), 2026Q2
  nyTotal: "$18.77T",
  nyMortgageChange: "−$74B",
  // Z.1, 2026Q2, not seasonally adjusted
  z1MortgageChange: "+$150B",
  z1ScopeChange: "+$198B",
};

export const site = {
  title: "Who Holds the Debt?",
  description:
    "Most US household debt now sits on public balance sheets. Seventy years of data show crises didn't put it there. One did.",
  byline: "A data essay on US household debt, 1952–2026",
};

export const hero = {
  kicker: "US household debt, 1952–2026",
  headline: "Most US household debt now sits on public balance sheets. Crises didn't put it there. One did.",
  dek: `In 1952 the federal government, the housing agencies and state and local governments held ${facts.publicShareFirst} of what American households owed on their homes and consumer loans. By ${facts.latestQuarter} they held ${facts.publicShareLatest}: ${facts.publicLatest} of ${facts.scopeLatest}. The obvious story is that every crisis pushed more risk onto taxpayers. The data mostly say otherwise. The climb was a slow build-out of Fannie Mae, Freddie Mac and the agency pools. The one real exception is 2007.`,
  statLabel: "of US household mortgage and consumer debt is held on public balance sheets",
  statNote: "Public share of household 1–4 family mortgages and consumer credit, {firstQuarter} to {latestQuarter}. Fed Z.1 Financial Accounts.",
  sparkTitle: "Public share of household debt, {firstYear}–{latestYear}",
  facts: [
    { label: "Public share, 1952 Q1", value: facts.publicShareFirst },
    { label: `All-time high, ${facts.publicSharePeakQ}`, value: facts.publicSharePeak },
    { label: "Change over 2007–11, the one real ratchet", value: facts.gfcDelta },
    { label: `Publicly held, ${facts.latestQuarter}`, value: `${facts.publicLatest} of ${facts.scopeLatest}` },
  ],
  factsSource: "Fed Z.1 Financial Accounts, household mortgages and consumer credit.",
};

/** The quarter's news hook. NY Fed credit-report data, always attributed and explained. */
export const nyFedVsZ1 = {
  title: "This quarter's headline, and why this essay doesn't use it",
  body: [
    `The New York Fed's credit-report data show household debt falling in the second quarter of 2026 for the first time since 2020, to ${facts.nyTotal}, with mortgage balances down ${facts.nyMortgageChange.replace("−", "")}.`,
    `The Fed's Financial Accounts (Z.1), which every other number here comes from, show the opposite for the same quarter: mortgages up ${facts.z1MortgageChange.replace("+", "")} and in-scope household debt up ${facts.z1ScopeChange.replace("+", "")}, before seasonal adjustment.`,
    "They measure different things. The New York Fed series comes from a 5% sample of individual credit reports. Z.1 is built from lenders' balance sheets and counts nonprofits as households. Neither is wrong; a single quarter's direction is not something to build a story on.",
  ],
};

export interface Chapter {
  id: string;
  number: string;
  title: string;
  lede: string;
  body: string[];
  figure: { title: string; caption: string; source: string };
  aside?: { title: string; body: string };
}

export const ratchet: Chapter = {
  id: "ratchet",
  number: "1",
  title: "The Ratchet",
  lede: "The public share of household debt rose for seventy years. Mostly, it rose in ordinary times.",
  body: [
    `Start in 1952. Banks, savings institutions, life insurers and households selling their own homes on credit held nearly all US home mortgages and consumer loans. Public holders, meaning the federal government, the housing agencies and state and local governments, had ${facts.publicShareFirst}.`,
    `The share climbed for the next three decades, and fastest when nothing was going wrong. Ginnie Mae issued the first mortgage-backed security in 1970 and Freddie Mac was chartered the same year. Through the 1980s, thrifts and banks sold or swapped their mortgages into agency pools. The GSEs and agency pools added ${facts.gse1980s} of household debt in that decade alone.`,
    `The share fell in the early 2000s, by ${facts.preGfcDecline.replace("−", "")} between 1999 and 2007, as Wall Street's private-label securities took market share. Then the financial crisis reversed all of that and more. The public share went from ${facts.gfcFrom} at the end of 2007 to ${facts.gfcTo} four years later and never came back down. It peaked at ${facts.publicSharePeak} in ${facts.publicSharePeakQ} and is ${facts.publicShareLatest} today.`,
    "Read the chart from the bottom up. The bands below the dark line are public: federal lending (mostly student loans), Fannie Mae, Freddie Mac and the Ginnie Mae pools, and state and local housing agencies. Everything above it is private. Switch to real dollars to see the scale, or split mortgages from consumer credit.",
  ],
  figure: {
    title: "Who bears the credit risk on household debt",
    caption:
      "Share of household 1–4 family mortgages and consumer credit by the type of institution that holds it (agency and GSE mortgage pools count as holders). Public holders (federal government, GSEs and agency pools, state and local governments) are stacked at the bottom; the top edge of that block is the public share.",
    source: "Fed Z.1 Financial Accounts, tables L.218 and L.222 (holders apportioned to the household liability). NBER recession dates.",
  },
  aside: {
    title: "What counts as public",
    body:
      "A loan is public here when a government entity or a government-sponsored enterprise holds it, directly or through an agency or GSE mortgage pool. Fannie Mae and Freddie Mac have been in federal conservatorship since September 2008, so their credit risk is, in practice, the taxpayer's. Holding a loan is not always the same as bearing its risk; the Methods page explains where the two differ.",
  },
};

export const crisisByCrisis: Chapter & {
  notes: Record<string, { label: string; text: string }>;
  metricLabels: Record<string, string>;
} = {
  id: "crises",
  number: "2",
  title: "Crisis by crisis",
  lede: "Line every recession up on the quarter it began. Only one stands out.",
  body: [
    "Each panel starts two years before a crisis and runs four years past it. The line shows how far the public share moved, in percentage points, from the quarter the crisis began.",
    `If crises ratcheted risk onto public balance sheets, these windows should show bigger gains than any other four-year stretch. They don't. Compared with every other 16-quarter window since 1952, recession windows are statistically indistinguishable (p ≈ ${facts.placeboP} in a placebo test), and only ${facts.crisesAboveMedian} recessions beat the median window. The big gains of the 1970s and 1980s happened inside recessions and outside them alike, because the agencies were growing the whole time.`,
    `The financial crisis is the exception. The public share rose ${facts.gfcDelta.replace("+", "")} from the end of 2007, from ${facts.gfcFrom} to ${facts.gfcTo}, which puts it in the ${facts.gfcPercentile} percentile of all four-year windows since 1952. About half of that was private lenders pulling back rather than the public sector expanding: private holdings shrank ${facts.gfcPrivateShrinkPct} (${facts.gfcPrivateShrink}) and private-label securities lost ${facts.gfcPrivateLabelShare} of share, while public holdings grew ${facts.gfcPublicGrowPct} (${facts.gfcPublicGrow}).`,
    `2001 went the other way, ${facts.dotcomDelta.replace(" pts", " points")}, during the private-label boom. The 2020 recession added about one point. The CARES Act forbearance, the 2023 student-loan restart and the 2025 return of collections each moved the share by ${facts.shocksMax}.`,
  ],
  figure: {
    title: "Change in the public share around each crisis",
    caption:
      "Percentage-point change from the quarter each crisis began (t = 0), two years before to four years after. Same scale in every panel. Policy shocks have shorter windows because they are recent.",
    source: "mart.crisis_event_window, built from Fed Z.1 and NBER business-cycle dates. Placebo test: analysis/notebook.py.",
  },
  notes: {
    "1953": { label: "1953–54", text: "Post-Korean War recession. Banks, thrifts and insurers hold almost everything." },
    "1957": { label: "1957–58", text: "FHA and VA insurance grow, but the loans stay on private books." },
    "1960": { label: "1960–61", text: "The public share falls slightly." },
    "1969": { label: "1969–70", text: "Ginnie Mae issues the first mortgage-backed security in 1970; Freddie Mac is chartered the same year." },
    "1973": { label: "1973–75", text: "Inflation squeezes thrifts and agency pools keep growing, as they did before the recession." },
    "1980": { label: "1980", text: "A large gain, but the 1980s build-out was just as fast outside recessions." },
    "1981": { label: "1981–82", text: "High rates break the savings-and-loan model; thrifts swap mortgages into agency securities." },
    "1990": { label: "1990–91", text: "The savings-and-loan cleanup. Agency pools become the default home for new mortgages." },
    "2001": { label: "2001", text: "The share falls 3.8 points as private-label securitization booms." },
    "2007": { label: "2007–09", text: "The one real ratchet: +13.1 points, half of it private lenders retreating. It never reversed." },
    "2019": { label: "2020", text: "About one point. Rates fall to zero and refinancing flows through the agencies." },
    "2020": { label: "CARES Act", text: "Mortgage forbearance and the student-loan pause. Less than half a point since." },
    "2023": { label: "2023 restart", text: "Student-loan payments resume. A policy shock with almost no effect on the share." },
    "2025": { label: "2025 collections", text: "Collections on defaulted student loans resume. The share is slightly lower since." },
  },
  metricLabels: {
    public_share: "Public share",
    "share:gse_agency": "GSE & agency pools",
    "share:federal_direct": "Federal direct",
    "share:state_local": "State & local",
    "share:banks_credit_unions": "Banks & credit unions",
    "share:private_securitization": "Private securitization",
    "share:nonbank_other": "Finance companies & other",
    "share:home_backed": "Home-backed debt",
    "share:vehicle_backed": "Vehicle-backed debt",
    "share:uncollateralized": "Uncollateralized debt",
    "share:other_nonrevolving": "Other non-revolving debt",
    "coverage:home_backed": "Home collateral coverage",
    "coverage:vehicle_backed": "Vehicle collateral coverage (durables proxy)",
  },
};

/** One-line descriptions of each holder type, for the linked side card in "Crisis by crisis".
 *  Keyed by risk_bucket; mirrors the series mapping in pipeline/series_catalog.yaml. */
export const holderNotes: Record<string, string> = {
  federal_direct: "Loans the federal government holds itself: mostly direct student loans, plus a few mortgages.",
  gse_agency: "Fannie Mae, Freddie Mac and the agency and GSE mortgage pools (Ginnie Mae included), plus Sallie Mae until 2004.",
  state_local: "State and local governments, mainly their housing finance agencies.",
  banks_credit_unions: "Commercial banks, savings institutions and credit unions, lending from their own balance sheets.",
  private_securitization: "Private-label asset-backed securities and mortgage REITs: the risk sold on to investors without a public guarantee.",
  nonbank_other: "Finance companies, life insurers, pension funds, retailers and households who sell homes on credit.",
};

/** Copy for the scroll-driven walk through each crisis (chapter 2). */
export const crisisScrolly = {
  label: "Crisis walk-through",
  title: "Who held household debt around each crisis",
  intro: "Scroll through each crisis. The chart zooms to two years before and four years after it began.",
  legendLabel: "Highlight a holder",
  legendHint: "Select a holder to highlight it in the chart and see its share.",
  reset: "Show all years",
  caption: "Public share",
  cardSince: "since",
  cardBegan: "began",
  cardClose: "Clear",
  stepCta: "Show in the chart",
};

export const collateral: Chapter & { classLabels: Record<string, string> } = {
  id: "collateral",
  number: "3",
  title: "What the debt bought",
  lede: "Household debt as a whole is still mostly backed by houses. The public sector's newest debt is backed by nothing.",
  body: [
    "A mortgage is backed by a house, which usually gains value. An auto loan is backed by a car, which loses value from the day it leaves the lot. A credit card balance or a student loan is backed only by the borrower's future income.",
    `Household debt has not drifted away from houses. Mortgages are ${facts.mortgagesOfScope} of the debt in scope, and the cushion behind them is unusually thick: owner-occupied real estate is worth ${facts.homeCoverage} the mortgages against it, a ${facts.homeCushion} equity cushion. Outside 2022–26, coverage has not been that high since 1960. The low point was ${facts.homeCoverageLow} in ${facts.homeCoverageLowQ}, after the housing crash.`,
    `The change is inside the public book. It is still about ${facts.publicBookHome} home-backed, but student loans went from ${facts.studentInPublicBook2007} of it at the end of 2007 to ${facts.studentInPublicBookNow} now. The public sector holds ${facts.publicShareOfStudent} of student loans and ${facts.publicShareOfUncoll} of all household debt with no collateral, up from ${facts.publicShareOfUncoll2007} in 2007. That is where the two lenses meet: the debt the government took on most recently is the debt with nothing behind it.`,
  ],
  figure: {
    title: "What household debt is backed by",
    caption:
      "Share of household mortgages and consumer credit by the collateral behind it, and the coverage ratio: market value of the homes divided by the mortgage debt they back.",
    source: "Fed Z.1: FL153165105, FL153166100/220/400/205 (debt); FL155035015, FL155111005 (collateral).",
  },
  classLabels: {
    home_backed: "Home-backed",
    vehicle_backed: "Vehicle-backed",
    uncollateralized: "No collateral",
    other_nonrevolving: "Other non-revolving",
  },
};

export const paymentPriority: Chapter & { loanLabels: Record<string, string>; studentNote: string } = {
  id: "priority",
  number: "4",
  title: "Who stops paying first",
  lede: "When money runs short, households keep the house and the car and let the cards go.",
  body: [
    "Credit-report data from the New York Fed, available from 2003, show the order in which households fall behind. Each quarter the series reports what share of each loan type moved into serious delinquency, 90 days or more past due. These are NY Fed figures, not Z.1.",
    "Card balances go bad first and most often, in good years and bad. Mortgages are the last thing people stop paying, except in 2009 and 2010, when the housing crash left many owners deep underwater. Auto loans sit in between, because a car is how people get to work.",
    "Student loans are the outlier, and the reason is policy. During the payment pause, from March 2020 to September 2023, almost no federal student loans were reported delinquent. When collections and credit reporting of defaulted loans resumed in May 2025, loans that had been in default for years reappeared on credit reports at once.",
  ],
  figure: {
    title: "Share of balances moving into serious delinquency, by loan type",
    caption:
      "Percent of balance transitioning into 90+ days delinquent, annualized, as published by the NY Fed, one panel per loan type. Student-loan rates sit near zero from 2020 to early 2025 because of the federal payment pause, then jump as defaulted loans were reported again.",
    source: "Federal Reserve Bank of New York, Household Debt and Credit Report (Consumer Credit Panel / Equifax).",
  },
  loanLabels: {
    mortgage: "Mortgage",
    heloc: "Home equity line",
    auto: "Auto loan",
    credit_card: "Credit card",
    student: "Student loan",
    other: "Other",
  },
  studentNote:
    // TODO(findings): add the size of the re-reporting effect if findings.md quantifies it.
    "The 2025 jump in student-loan delinquency mostly reflects defaulted loans returning to credit reports after the pause, not a sudden wave of new missed payments.",
};

export const now = {
  id: "now",
  number: "5",
  title: "Now",
  lede: "The public sector holds most household debt. That is mostly the legacy of a slow build-out and one crash, and it changes what the next downturn looks like.",
  body: [
    `In ${facts.latestQuarter} public holders had ${facts.publicLatest} of ${facts.scopeLatest} in household mortgages and consumer credit, ${facts.publicShareLatest}. That is a little below the ${facts.publicSharePeak} peak of ${facts.publicSharePeakQ}, and the share has barely moved through the pandemic, the student-loan restart or the return of collections.`,
    `Households are also less stretched than before the last crash. Mortgage and consumer debt is about ${facts.debtToIncomeNow} of disposable income, against ${facts.debtToIncome2007} at the end of 2007, and home equity is unusually high.`,
    `At its peak the Fed owned about one dollar in six of all household mortgage and consumer debt, as a bondholder exposed to interest rates, not as a lender exposed to defaults. Its agency mortgage-backed securities reached ${facts.fedMbsPeak} of the debt in scope in ${facts.fedMbsPeakQ} (${facts.fedMbsPeakUsd}) and are ${facts.fedMbsNow} now. Those holdings sit inside the public share, not on top of it: the credit risk stays with Fannie Mae, Freddie Mac and Ginnie Mae.`,
    "When private lenders held most of the risk, a downturn meant bank failures and credit crunches. With the public sector holding most of it, the next one is more likely to show up as losses on federal balance sheets, fights over forbearance and forgiveness, and pressure on the Fed to keep mortgage markets working.",
  ],
  tiles: [
    { value: facts.publicShareLatest, label: `Public share of household debt, ${facts.latestQuarter}` },
    { value: facts.gfcDelta, label: "Public share gain over 2007–11, the only crisis that moved it" },
    { value: facts.publicShareOfUncoll, label: `Of debt with no collateral now held publicly (${facts.publicShareOfUncoll2007} in 2007)` },
    { value: facts.fedMbsNow, label: `Held by the Fed as MBS (peak ${facts.fedMbsPeak}, ${facts.fedMbsPeakQ})` },
  ],
  tilesSource: "Fed Z.1 Financial Accounts; Fed MBS from FRED (WSHOMCB), quarter-end.",
};

export const fixtureBanner =
  "Development preview. Charts on this page use synthetic fixture data, not the Fed series. Numbers in the text may not match them.";

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
    "The crisis test compares the 16-quarter change in the public share after each NBER recession peak with the change over every other 16-quarter window, and with randomly placed and circularly shifted sets of dates (a placebo test).",
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
