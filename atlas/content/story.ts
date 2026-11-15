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

// Home hero copy (Eleonora's approved copy, R1, 2026-11-15). The lede's numbers are wired in app/page.tsx.
export const hero = {
  forLine: "For analysts who price household credit, and for anyone who wants to see where the risk went.",
  buttons: { play: "Play the story", ask: "Ask a question", build: "How it was built" },
};

// The explorer's five chapters (Eleonora's approved copy, R1, 2026-11-15): date, button, title, caption.
export interface Chapter {
  date: string;
  button: string;
  title: string;
  caption: string;
}

export const chapters: Chapter[] = [
  {
    date: "1952-03-31",
    button: "1952",
    title: "Every dot is $50 billion of debt",
    caption: "Each dot sits with whoever holds the loan and takes the loss. The public side holds {share}.",
  },
  {
    date: "1989-12-31",
    button: "1980s",
    title: "No crisis required",
    caption: "Banks sell mortgages into Fannie Mae, Freddie Mac and Ginnie Mae pools. Public share: {share}.",
  },
  {
    date: "2006-12-31",
    button: "2001–06",
    title: "Wall Street pulls the other way",
    caption: "Private securitization takes share from the agencies. The public share falls to {share}.",
  },
  {
    date: "2011-12-31",
    button: "2007–11",
    title: "The hot potato",
    caption:
      "The private pile drops from $4.5T to $1.7T. The public share jumps from 36.1% to {share}. It never came back.",
  },
  {
    date: "2026-06-30",
    button: "Today",
    title: "Most of it is public now",
    caption: "{public} of {total}, or {share}, sits with the public sector.",
  },
];

// "What it means" (Eleonora's approved copy, R1). Tokens: {share} latest public share. `pile` is the holder each
// card is about, so its rule and stat wear that holder's ink. Every number has a row in claims/register.csv.
export const meaning = {
  title: "What it means",
  points: [
    {
      stat: "{share}",
      pile: 1,
      title: "Taxpayers are the backstop",
      body: "A holder loses only what the collateral fails to cover, and homes are worth 3.56x the mortgages against them.",
    },
    {
      stat: "13.1 pp",
      pile: 4,
      title: "One crisis moved the risk for good",
      body: "Across eleven recessions, only 2007–11 moved the share for good.",
    },
    {
      stat: "51%",
      pile: 0,
      title: "The public book is going unsecured",
      body: "The public sector holds 51% of debt with no collateral, up from 7% in 2007.",
    },
  ],
};

// Ask Hot Potato (Eleonora's approved copy, R1). Example questions come from the answerable E1 set
// (evals/e1_sql_benchmark/questions.yaml q116, q146, q162; none is in the E3 holdout).
export const ask = {
  title: "Ask Hot Potato",
  intro:
    "Ask in plain English. Claude queries the project's Fed data and shows its query and the data vintage under every answer. No forecasts. Five questions a day.",
  // label: the chip text; question: what the chip puts in the box (the E1 wording).
  examples: [
    { label: "Banks' share, 2026Q2", question: "What share of household mortgages and consumer credit did banks and credit unions hold in 2026Q2?" },
    { label: "Home collateral coverage, 2026Q2", question: "What was the home-backed collateral coverage ratio (collateral value / debt) in 2026Q2?" },
    { label: "Student-loan delinquency, 2026Q2", question: "What percentage of student loan balances transitioned into serious delinquency (90+) in 2026Q2, per the NY Fed?" },
  ],
};

// Footer (Eleonora's approved copy, R1).
export const footer = {
  data: "Data: Federal Reserve Z.1 and FRED. Every number links to its row in the claims register.",
};

// "About the data" (moved to /methods in R1).
export const coda = {
  sourcesTitle: "About the data",
  sources: [
    "Converted to 2026Q3 dollars with CPI (base: the 2026Q3 average of CPIAUCSL). The public share is computed in nominal dollars.",
    "Dots are rounded with the largest-remainder method, so each quarter's dots match its total to within one dot. Between quarters only the difference moves.",
  ],
};
