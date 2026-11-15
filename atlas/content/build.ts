// Copy for /how-it-was-built, moved from web/content/build.ts (site-visible (b), 2026-11-07: one site). Keep it factual:
// every session, tool and connector listed here was actually used; sources are docs/building-with-claude.md and PLAN.md.
// Rewritten 2026-11-10 after Eleonora flagged the old copy as factually incorrect; a Claude draft in her register per her
// voice-53 (a), shown under a draft banner until she approves it.

// Cut to about a fifth on 2026-11-11 after Eleonora said the site had "10 times too much text" (site review).

export const build = {
  lede:
    "Eleonora designed and decided; Claude Code built, checked and drafted, across one coordinator and three track sessions.",

  // The four Claude capabilities the challenge judges, each linked to where it lives in the repository.
  tiles: [
    { name: "Skills", body: "claim-check, preregister, research-memo, chart-from-sql and more", href: ".claude/skills" },
    { name: "Subagents", body: "skeptic, quant-reviewer, editor, register-keeper, analyst", href: ".claude/agents" },
    { name: "MCP", body: "Own household-credit server, plus GitHub, Supabase, Vercel and FRED", href: "mcp" },
    { name: "API", body: "Ask Hot Potato, and model benchmarks run under spend caps", href: "evals" },
    { name: "Hooks", body: "Pre-commit register check and tests; hand edits to generated results blocked", href: ".claude/hooks" },
    { name: "Plugin", body: "Fed Data Desk: the skills, subagents and MCP server packaged for reuse", href: "plugin/fed-data-desk" },
  ],

  // E1 rates, each linked to its row in claims/tracks/infra.csv (ClaimRef in the page, by id).
  evals: {
    lede: "The tools were tested against pre-registrations written before any result existed.",
    e1: {
      caption: "E1, question to SQL (2026-11-05): share correct, three runs per question.",
      rows: [
        { model: "Opus", answer: { id: "e1_h1_opus_rate", text: "91.7%" }, refuse: { id: "e1_h3_opus_rate", text: "91.7%" } },
        { model: "Sonnet", answer: { id: "e1_h1_sonnet_rate", text: "96.1%" }, refuse: { id: "e1_h3_sonnet_rate", text: "68.3%" } },
        { model: "Haiku", answer: { id: "e1_h1_haiku_rate", text: "92.8%" }, refuse: { id: "e1_h3_haiku_rate", text: "40.0%" } },
      ],
    },
    notes: [
      "E2, planted errors: the skeptic and quant-reviewer subagents caught every planted error in the rerun. A plain baseline also found every planted data error, so the test cannot separate the prompts from the model.",
      "E4, red team: attacks on Ask Hot Potato before and after its guardrails; no secret or system-prompt text leaked.",
    ],
  },

  stack: [
    { name: "GitHub", body: "Code, history, CI and the quarterly refresh." },
    { name: "Supabase", body: "Postgres warehouse; read-only research login." },
    { name: "Vercel", body: "Hosting, with a preview for every branch." },
    { name: "Python and Next.js", body: "Pipeline, analysis and this site: Canvas dots, hand-drawn SVG." },
    { name: "Claude.ai artifacts", body: "Decision docket and review queue for Eleonora." },
  ],

  schema: {
    lede: "Two loops: how a task reaches Eleonora's sign-off, and how data reaches this page.",
    workflow: {
      title: "Workflow",
      loop: "Her answers go back into the plan.",
      steps: [
        { who: "Eleonora", name: "Plan", body: "Sets phases, tasks and acceptance criteria." },
        { who: "Claude", name: "Coordinator", body: "Assigns tasks, merges branches, keeps the log." },
        { who: "Claude", name: "Tracks", body: "Markets, analysis, infrastructure, one branch each." },
        { who: "Claude", name: "Review", body: "Subagents raise objections; tracks answer each." },
        { who: "Gate", name: "Checks", body: "Register check and tests block bad commits." },
        { who: "Eleonora", name: "Decide", body: "Rules on cards; her choices are recorded as hers." },
      ],
    },
    build: {
      title: "Build",
      loop: "Each Z.1 release reruns the chain as a pull request.",
      steps: [
        { who: "Data", name: "Sources", body: "Z.1, FRED, NY Fed, each checked free first." },
        { who: "Code", name: "Pipeline", body: "Python package hhdebt: extract, transform, load, export. More than 600 automated tests across the repository." },
        { who: "Data", name: "Warehouse", body: "Raw, core, mart." },
        { who: "Code", name: "Analysis", body: "Pre-registered; every number registered." },
        { who: "Gate", name: "Preview", body: "Every branch builds a preview." },
        { who: "Eleonora", name: "Production", body: "Live only after her OK." },
      ],
    },
  },

  human: [
    "Chose the topic, angle and research design.",
    "Decided every open question and spend cap.",
    "Caught errors Claude missed.",
    "Approved every production release.",
  ],
};
