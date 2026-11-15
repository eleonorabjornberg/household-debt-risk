// The /research index (Eleonora, 2026-11-09: "Make sure our quantitative work is visible there as well").
// question: the task's description in PLAN.md, verbatim. status: verbatim fragments of the task's PLAN.md status cell
// (statusRow names the row when it is another task's). method: one line, a Claude draft, with no figures.
// lib/research.test.ts checks the question and every status fragment against PLAN.md, and the slugs against
// scripts/sync-research.mjs. The write-ups themselves are research/<task>/README.md; the site shows a short version (whole
// sections cut, links aside; Eleonora 2026-11-11), the MCP server and the Ask API return them in full (get_research_writeup).

export interface ResearchEntry {
  id: string;
  /** /research/<slug>, rendered from content/research/<slug>.md; null when there is no write-up */
  slug: string | null;
  /** another page for the same task (B3: the scenario tool) */
  extra?: { href: string; label: string };
  question: string;
  method: string;
  status: string[];
  statusRow?: string;
  /** why there is no write-up */
  blocked?: string;
}

export const research: ResearchEntry[] = [
  { id: "A1", slug: "a1",
    question: "**Decompose the 2007–11 jump** by loan type × holder: GSE conservatorship (Sept 2008), FHA/Ginnie Mae expansion, the 2010 student-loan takeover (SAFRA ended new FFEL loans)",
    method: "An exact decomposition of the change in the public share by loan type and holder, with a Shapley split between public growth and private retreat.",
    status: ["done"] },
  { id: "A2", slug: "a2",
    question: "**Net vs gross public exposure**: subtract risk sold back through CRT (STACR, CAS) and mortgage insurance",
    method: "The risk the GSEs pass back through credit-risk transfer and mortgage insurance, taken from their 10-K filings, subtracted from what they hold.",
    status: ["done: Freddie Mac part and Fannie Mae part", "accepted by Eleonora 2026-11-04"] },
  { id: "A3", slug: "a3",
    question: "**Full history before 1952**: Z.1 annual 1945–51; earlier from historical sources. Document HOLC (1933), FHA (1934), Fannie Mae (1938) and every later policy step",
    method: "Z.1 annual levels before 1952 joined to Historical Statistics of the United States for earlier years, with each policy date checked against its primary source.",
    status: ["done", "accepted by Eleonora 2026-11-04"] },
  { id: "A4", slug: "a4",
    question: "**Structural breaks**: legislation dates as candidate breaks; Bai-Perron (unknown breaks) and Chow (known dates)",
    method: "Break tests on the public share, run to a pre-registration frozen before the code first touched the series.",
    status: ["done", "accepted by Eleonora 2026-11-04"] },
  { id: "A5", slug: "a5",
    question: "**Distribution**: geographic and by income/wealth; who borrows vs who carries the risk",
    method: "Who borrows (by income, wealth and state) set beside who holds the loans, with a labeled estimate linking the two.",
    status: ["done", "accepted by Eleonora 2026-11-04"] },
  { id: "A6", slug: null,
    question: "**Hidden subsidy**: CBO-style fair-value estimate of the subsidy in government-held household credit risk",
    method: "Would replicate the Congressional Budget Office's fair-value estimates.",
    status: ["blocked"],
    blocked: "CBO replication: `cbo.gov` returns 403" },
  { id: "A7", slug: "a7",
    question: "**Causal evidence**: event studies and synthetic control around the 2008 conservatorship and the 2010 student-loan takeover",
    method: "Event studies and synthetic control, run to a pre-registration and its addenda, all committed before any data was fetched.",
    status: ["done: accepted by Eleonora 2026-11-04", "family of four kept"] },
  { id: "A8", slug: "a8",
    question: "**International comparison**: US vs Canada (CMHC), Denmark (covered bonds), UK, Germany",
    method: "Two measures per country, who holds the loans and who bears the risk, with every figure that cannot be computed recorded as missing.",
    status: ["done, partial by design", "accepted by Eleonora 2026-11-04"] },
  { id: "B1", slug: "b1",
    question: "**Market-implied credit risk**: mortgage-rate spread over Treasuries; agency vs private-label. Did the shift compress the price of household credit risk?",
    method: "Mortgage-rate spreads against the public share, with the specification fixed before any result and later checks marked post hoc.",
    status: ["done, inconclusive", "accepted by Eleonora 2026-11-04"] },
  { id: "B2", slug: "b2",
    question: "**CRT spreads** as the market's price for the risk the GSEs hand back; link to A2",
    method: "FHFA's deal-level credit costs (2013–16), the GSEs' 10-K costs (2017–23) and Freddie Mac's tranche spreads from 2017, each set against a baseline expected loss.",
    status: ["done (all parts approved as Claude drafts)"] },
  { id: "B3", slug: "b3", extra: { href: "/scenarios", label: "Try the scenario tool" },
    question: "**Scenario engine**: default rate, loss severity, recovery path → losses split public vs private; interactive in the app",
    method: "A loss engine applied to today's balances by holder, with proxy presets from the Fed's stress test and the 2008–12 bank write-offs; the same engine runs in the browser.",
    status: ["done", "/scenarios live"] },
  { id: "B4", slug: "b4",
    question: "**Policy-regime scenarios**: GSEs released from conservatorship, student-loan reform, recession",
    method: "Policy cases mapped onto the B3 engine, with each debate's status looked up from primary sources.",
    status: ["done", "recession and GSE ranges accepted", "no loss-engine change"] },
  { id: "C1", slug: "c1",
    question: "**Nowcast** the public share between Z.1 releases from higher-frequency data",
    method: "A point-in-time panel of the inputs public at each nowcast instant, scored against benchmarks on a development sample, then once on a sealed holdout.",
    status: ["done", "holdout run once 2026-11-05"] },
  { id: "C1b", slug: "joint-holdout",
    question: "A second, pre-registered C1 run that adds Freddie Mac's and Ginnie Mae's monthly data.",
    method: "Built and frozen before the holdout, then scored once in the joint holdout with C1 and C2.",
    status: ["done", "holdout run once 2026-11-05 with C1/C1b"], statusRow: "C2" },
  { id: "C2", slug: "joint-holdout",
    question: "**Forecast model** with purged rolling-origin validation, leakage tests, prediction intervals, naive/AR benchmarks, mirroring `repo-market-model`",
    method: "Forecasts frozen under a scoring protocol before the holdout was opened, then scored once against naive and AR benchmarks.",
    status: ["done", "holdout run once 2026-11-05 with C1/C1b", "results feed C3"] },
  { id: "C3", slug: "c3",
    question: "**Honest accuracy report**, including where the model fails",
    method: "Every frozen specification, abandoned ones included, scored against its benchmarks, with the largest errors and the failing regimes listed.",
    status: ["done", "accuracy report built 2026-11-05", "reviewed and accepted"] },
  { id: "Joint holdout", slug: "joint-holdout",
    question: "The single, gated run of the sealed holdout for the C2 forecast and the C1 and C1b nowcasts.",
    method: "One run under the frozen protocols; its results are reported as they came out.",
    status: ["done", "write-up research/joint_holdout accepted"], statusRow: "C1" },
];
