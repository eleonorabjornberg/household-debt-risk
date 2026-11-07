// All copy for the page. Step bodies may use tokens filled from the data at that step's quarter:
//   {share}  public share, e.g. 36.1%
//   {total}  total household mortgage + consumer credit in 2026Q3 dollars, e.g. $19.2T
//   {public} the public part of it, e.g. $10.8T
// Fixed historical claims come from analysis/findings.md.

export const site = {
  title: "Hot Potato",
  kicker: "Who holds America's household debt?",
  description:
    "Watch $19 trillion of US household debt move between banks, private investors and the public sector, one $50 billion dot at a time.",
  repo: "https://github.com/eleonorabjornberg/household-debt-risk",
};

export const PILE_NAMES = [
  "Federal govt",
  "GSEs & agency",
  "State & local",
  "Banks & CUs",
  "Private sec. & REITs",
  "Other lenders",
];

export const PILE_LONG = [
  "Federal government (direct loans, mostly student loans)",
  "Fannie Mae, Freddie Mac and agency MBS pools",
  "State and local governments",
  "Banks and credit unions",
  "Private securitization and REITs, incl. card ABS",
  "Finance companies and other private lenders",
];

export interface Step {
  date: string;
  kicker: string;
  title: string;
  body: string;
}

export const steps: Step[] = [
  {
    date: "1952-03-31",
    kicker: "1952",
    title: "Every dot is $50 billion of debt",
    body:
      "These dots are American households' mortgages (solid) and consumer loans (rings), in 2026Q3 dollars. Each one sits with whoever holds the loan, because whoever holds it takes the loss if it goes bad. In 1952 nearly all of it was with banks and finance companies. The public side held {share}.",
  },
  {
    date: "1979-12-31",
    kicker: "1950s–1970s",
    title: "The public side starts to fill",
    body:
      "Fannie Mae, Freddie Mac and Ginnie Mae begin buying and pooling mortgages, and dots start to cross the line. Debt keeps growing on both sides. By 1979 the public share is {share}.",
  },
  {
    date: "1989-12-31",
    kicker: "1980s",
    title: "No crisis required",
    body:
      "The 1980s alone add about 19 points as banks sell their mortgages into agency pools. It's the biggest shift in the whole record, and it is slow and structural: the build-out of the GSEs, not a rescue. Public share: {share}.",
  },
  {
    date: "2006-12-31",
    kicker: "2001–2006",
    title: "The private securitization boom pulls the other way",
    body:
      "Wall Street securitization grows fast enough to take market share from the agencies. From the 2001 recession to 2006 the public share falls to {share}, while the pile of private securitization and REITs, incl. card ABS, swells to about $4.6T in 2026Q3 dollars.",
  },
  {
    date: "2007-12-31",
    kicker: "December 2007",
    title: "The Great Recession begins",
    body:
      "Total debt is {total}. The public sector holds {share} of it. Keep an eye on the private securitization and REITs pile.",
  },
  {
    date: "2011-12-31",
    kicker: "2007–2011",
    title: "The hot potato",
    body:
      "In four years the private securitization and REITs pile, incl. card ABS, loses almost two-thirds, from $4.5T to $1.7T. Banks shrink too. The agencies and the federal government keep growing. The public share jumps from 36.1% to {share}, a rise bigger than 98% of all four-year windows. It is the one crisis that moved the share for good, and a little over half of the jump came from private lenders shrinking, not from Fannie Mae and Freddie Mac growing.",
  },
  {
    date: "2023-12-31",
    kicker: "2020–2023",
    title: "COVID barely moves the dots",
    body:
      "The sharpest jump in unemployment since the 1930s, and four years after the 2019 peak the share has gone from 55.2% to {share}, about one point. Across all eleven recessions, the shift after a crisis looks like any other period's. 2007–11 is the exception, not the rule.",
  },
  {
    date: "2026-06-30",
    kicker: "Today",
    title: "Most of it is public now",
    body:
      "{public} of {total} in 2026Q3 dollars, or {share}, sits with the public sector. It mostly got there slowly. One crisis made it permanent.",
  },
  {
    date: "2026-06-30",
    kicker: "Your turn",
    title: "Explore it yourself",
    body:
      "Drag the timeline or press play. Switch to Shares to see only the mix, with a fixed 1,000 dots. Hover over a pile, or tap it, to see its numbers.",
  },
];

// "What does this mean?" Tokens: {share} latest public share, {pls} private securitization and REITs, incl. card ABS
// in the latest quarter. Every number has a row in claims/register.csv (analysis/recommendation.md, 0.7).
export const meaning = {
  title: "What does this mean?",
  points: [
    {
      stat: "{share}",
      title: "Taxpayers are the backstop, not the first loss",
      body: "The public sector holds most household debt, but holding a loan is not the same as losing on it. Most of the public book is mortgages, and in aggregate homes are worth 3.56× the mortgages against them. Borrowers' equity, private mortgage insurance and the GSEs' risk-transfer deals stand in front of the taxpayer; this site does not measure how much they absorb. Fannie Mae and Freddie Mac have been in federal conservatorship since 2008.",
    },
    {
      stat: "p ≈ 0.30",
      title: "Crises rarely move the risk",
      body: "Across eleven recessions, a placebo test finds no detectable excess in the shift after a crisis (p ≈ 0.30, low power), against random sets of start quarters drawn from all 282 overlapping 16-quarter windows, 1952Q1–2022Q2. 2007–11 is the exception: it added 13.1 points, about half of it from private lenders pulling back, and the share has not fallen below its end-2011 level since. Private securitization and REITs, incl. card ABS, went from $4.6T in 2006 to {pls} today, in 2026Q3 dollars.",
    },
    {
      stat: "86%",
      title: "The public book is going unsecured",
      body: "The public sector holds 86% of student loans and 51% of household debt with no collateral, up from 7% in 2007. Part of that is relabelling: before 2010 most student loans held by banks already carried a federal guarantee. The debt can't be repossessed, but it is hard to discharge and can be collected from wages and tax refunds, so losses depend on collection, not collateral.",
    },
    {
      stat: "2025",
      title: "What to watch",
      body: "Releasing Fannie Mae and Freddie Mac from conservatorship would change who stands behind the biggest pile, not which pile it is in: this site counts them as public either way. Student-loan collections restarted in 2025, the first real test of the unsecured public book.",
    },
  ],
};

export const coda = {
  sourcesTitle: "About the data",
  sources: [
    "Federal Reserve Z.1 Financial Accounts: holders of 1–4 family mortgages and consumer credit. Mortgage holders are apportioned to the household sector.",
    "Converted to 2026Q3 dollars with CPI (base: the 2026Q3 average of CPIAUCSL). The public share is computed in nominal dollars.",
    "“Public” means the federal government, GSEs and agency pools, and state and local governments. Mortgages in GSE and agency pools count as public.",
    "Dots are rounded with the largest-remainder method, so each quarter's dots match its total to within one dot. Between quarters only the difference moves.",
  ],
};
