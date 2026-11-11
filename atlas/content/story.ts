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
      "Solid dots are mortgages, rings are consumer loans. Each sits with whoever holds the loan and takes the loss. In 1952 the public side held {share}.",
  },
  {
    date: "1979-12-31",
    kicker: "1950s–1970s",
    title: "The public side starts to fill",
    body:
      "Fannie Mae, Freddie Mac and Ginnie Mae start pooling mortgages. By 1979 the public share is {share}.",
  },
  {
    date: "1989-12-31",
    kicker: "1980s",
    title: "No crisis required",
    body:
      "Banks sell mortgages into agency pools: about 19 points in one decade, no rescue needed. Public share: {share}.",
  },
  {
    date: "2006-12-31",
    kicker: "2001–2006",
    title: "The private securitization boom pulls the other way",
    body:
      "Wall Street securitization takes share from the agencies. The public share falls to {share}; the private pile swells to about $4.6T.",
  },
  {
    date: "2007-12-31",
    kicker: "December 2007",
    title: "The Great Recession begins",
    body:
      "Total debt is {total}. The public sector holds {share}. Watch the private pile.",
  },
  {
    date: "2011-12-31",
    kicker: "2007–2011",
    title: "The hot potato",
    body:
      "The private pile drops from $4.5T to $1.7T. The public share jumps from 36.1% to {share}, bigger than 98% of four-year windows. It never came back.",
  },
  {
    date: "2023-12-31",
    kicker: "2020–2023",
    title: "COVID barely moves the dots",
    body:
      "The sharpest jump in unemployment since the 1930s moves the share from 55.2% to {share}: about one point.",
  },
  {
    date: "2026-06-30",
    kicker: "Today",
    title: "Most of it is public now",
    body:
      "{public} of {total}, or {share}, sits with the public sector. Most of the shift was gradual; one crisis made it permanent.",
  },
  {
    date: "2026-06-30",
    kicker: "Your turn",
    title: "Explore it yourself",
    body:
      "Drag the timeline or press play. Tap a pile for its numbers.",
  },
];

// "What does this mean?" Tokens: {share} latest public share, {pls} private securitization and REITs, incl. card ABS
// in the latest quarter. Every number has a row in claims/register.csv (analysis/recommendation.md, 0.7).
export const meaning = {
  title: "What does this mean?",
  points: [
    {
      stat: "{share}",
      title: "Taxpayers are the backstop; collateral takes the first loss",
      body: "A holder loses only what the collateral fails to cover, and homes are worth 3.56× the mortgages against them.",
    },
    {
      stat: "13.1 pp",
      title: "Crises rarely move the risk",
      body: "Across eleven recessions, only 2007–11 moved the share for good: 13.1 points.",
    },
    {
      stat: "51%",
      title: "The public book is going unsecured",
      body: "The public sector holds 51% of debt with no collateral, up from 7% in 2007. Losses depend on collection.",
    },
    {
      stat: "2025",
      title: "What to watch",
      body: "Student-loan collections restarted in 2025: the first test of the unsecured public book.",
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
