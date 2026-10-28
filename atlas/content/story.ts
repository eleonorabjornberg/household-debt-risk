// All copy for the page. Step bodies may use tokens filled from the data at that step's quarter:
//   {share}  public share, e.g. 36.1%
//   {total}  total household mortgage + consumer credit in 2026 dollars, e.g. $19.1T
//   {public} the public part of it, e.g. $10.8T
// Fixed historical claims come from analysis/findings.md.

export const site = {
  title: "Hot Potato",
  kicker: "Who holds America's household debt, 1952–2026",
  description:
    "Watch $19 trillion of US household debt move between banks, private investors and the public sector, one $50 billion dot at a time.",
  original: "https://household-debt-risk-web.vercel.app",
};

export const PILE_NAMES = [
  "Federal govt",
  "GSEs & agency",
  "State & local",
  "Banks & CUs",
  "Private-label",
  "Other lenders",
];

export const PILE_LONG = [
  "Federal government (direct loans, mostly student loans)",
  "Fannie Mae, Freddie Mac and agency MBS pools",
  "State and local governments",
  "Banks and credit unions",
  "Private securitization and mortgage REITs",
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
      "These dots are American households' mortgages (solid) and consumer loans (rings), in 2026 dollars. Each one sits with whoever holds the loan, because whoever holds it takes the loss if it goes bad. In 1952 nearly all of it was with banks and finance companies. The public side held {share}.",
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
    title: "The private-label boom pulls the other way",
    body:
      "Wall Street securitization grows fast enough to take market share from the agencies. From the 2001 recession to 2006 the public share falls to {share}, while the private-label pile swells to about $4.6T in today's dollars.",
  },
  {
    date: "2007-12-31",
    kicker: "December 2007",
    title: "The Great Recession begins",
    body:
      "Total debt is {total}. The public sector holds {share} of it. Keep an eye on the private-label pile.",
  },
  {
    date: "2011-12-31",
    kicker: "2007–2011",
    title: "The hot potato",
    body:
      "In four years the private-label pile loses almost two-thirds, from $4.5T to $1.7T. Banks shrink too. The agencies and the federal government keep growing. The public share jumps from 36.1% to {share}, a rise bigger than 98% of all four-year windows. It is the one crisis that ratcheted risk onto the public, and it never went back.",
  },
  {
    date: "2021-12-31",
    kicker: "2020–2021",
    title: "COVID barely moves the dots",
    body:
      "The sharpest jump in unemployment since the 1930s, and the share goes from 55.2% to {share} in two years. Across all eleven recessions, the shift after a crisis looks like any other period's. 2007–11 is the exception, not the rule.",
  },
  {
    date: "2026-06-30",
    kicker: "Today",
    title: "Most of it is public now",
    body:
      "{public} of {total}, or {share}, sits with the public sector. It mostly got there slowly. One crisis made it permanent.",
  },
  {
    date: "2026-06-30",
    kicker: "Your turn",
    title: "Explore it yourself",
    body:
      "Drag the timeline or press play. Switch to Shares to see only the mix, with a fixed 1,000 dots. Hover over a pile, or tap it, to see its numbers.",
  },
];

export const coda = {
  title: "Pick a year",
  lede: "Any year since 1952 on one card. Download it as an image to share.",
  sourcesTitle: "About the data",
  sources: [
    "Federal Reserve Z.1 Financial Accounts: holders of 1–4 family mortgages and consumer credit. Mortgage holders are apportioned to the household sector.",
    "Converted to 2026 dollars with CPI. The public share is computed in nominal dollars.",
    "“Public” means the federal government, GSEs and agency pools, and state and local governments. Mortgages in GSE and agency pools count as public.",
    "Dots are rounded with the largest-remainder method, so each quarter's dots match its total to within one dot. Between quarters only the difference moves.",
  ],
};
