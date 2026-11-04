# Audit and Phase 0 session prompts, 3-4 Nov 2026

Source session: `session_01GDxCQ42apfBERQ1Fw4qyjV`. These are the person's own typed prompts, in order (oldest first, UTC). Each prompt is followed by the commits made after it and before the next prompt.

### 2026-11-03T23:20:13Z

> I'm submitting this project (Hot Potato: Who Holds America's Household Debt, live at household-debt-risk.vercel.app) to the ieNYC × DataCamp "Be a Master in Claude" challenge. Deadline: 12 Nov 2026, 23:59 ET. The project counts for 50% of the ranking.
>
> ## Brief requirements
> Formats, any can be combined:
> - Data analysis: raw files/database → validated dashboard → recommendation
> - Agent skill or subagent: a SKILL.md that automates a recurring analytical task, with examples of it triggering
> Deliverables:
> 1. A 2–3 page write-up: problem, approach, how I used Claude, results and limits
> 2. The artifacts as a GitHub link: code, skill files, prompts, notebooks/dashboard
> 3. A 3–5 minute demo video
>
> ## Plan: primary format is Data analysis, plus one Skill
>
> Work in this order. Stop after step 1 and show me the plan before building anything.
>
> 1. Audit (read-only). Map the repo: data sources (Fed Z.1, FRED, NY Fed), the ingest pipeline, the PostgreSQL schema, the Next.js/Canvas frontend. List what already exists against each brief requirement and what is missing. Also look for evidence of how Claude was used in the build: git log (Co-Authored-By lines), CLAUDE.md, prompt files, commit messages. Summarize what you find; I need it for the "how I used Claude" section.
>
> 2. Validation. Add a reproducible check script (e.g. `validation/` with a single entry point) that:
>    - reconciles our sector totals to the published Z.1 aggregates for selected quarters
>    - recomputes the headline figures from source (public share 3.2% → 56.4%; the 2007–11 jump never reversed)
>    - flags gaps, series breaks and definition changes
>    Output a short pass/fail report I can screenshot for the write-up. Do not change the headline numbers silently; if a check fails, tell me.
>
> 3. Recommendation. Draft a "So what" section, in the app and in the write-up: what the shift of household credit risk onto the public balance sheet implies for taxpayers, for policy and for mortgage default risk. Keep it evidence-bound and mark the limits: correlation vs. cause, guarantee vs. ownership, data revisions.
>
> 4. Skill. Create `.claude/skills/z1-release-update/SKILL.md`: when a new Fed Z.1 release comes out,

Commits: none

### 2026-11-03T23:20:47Z

> MCP server: a small server over your Postgres database, so Claude can answer questions like “who held auto-loan risk in 1990?” straight from your data. That makes a good live moment in the demo.

Commits: none

### 2026-11-03T23:24:39Z

> Replace both previous scope updates with this one. Assume unlimited time: no deadline cuts, no "if there's time". My target is quantitative research and AI systems for financial markets, so frame everything that way. Keep the original steps 1–5 (audit, validation, recommendation, z1-release-update skill, submission package) as the foundation.
>
> The question every component serves: who holds America's household credit risk, how is it priced, and where is it going? The aim is a research platform at working-paper standard, with an AI research system that keeps it current and audits itself.
>
> ## Start: PLAN.md
> Rewrite PLAN.md with the phases below: tasks, dependencies, acceptance criteria and status. Keep it updated so any fresh session can resume from it. Show me the plan and wait for approval.
>
> ## Phase A: Core analysis
> A1. Breakdown of the 2007–11 jump by loan type and holder (GSE conservatorship, 2010 student-loan takeover, FHA/Ginnie Mae).
> A2. Net vs. gross public exposure: subtract the risk the GSEs sold back through credit-risk-transfer deals (since 2013).
> A3. Full history: extend the series back before 1952 from historical sources; document the New Deal origins (HOLC 1933, FHA 1934, Fannie 1938) and every later policy step, verified against primary sources.
> A4. Structural breaks: treat legislation as candidate breaks and test them formally (Bai-Perron, Chow). Report which breaks the data confirms.
> A5. Distribution: geographic (NY Fed Consumer Credit Panel, county level) and by income/wealth (Fed Distributional Financial Accounts): who borrows vs. who carries the risk.
> A6. Hidden subsidy: CBO-style fair-value estimate of the subsidy embedded in government-held household credit risk.
> A7. Causal evidence: event studies and synthetic control around the 2008 conservatorship and the 2010 student-loan takeover.
> A8. International comparison: US vs. Canada (CMHC), Denmark (covered bonds), UK, Germany.
>
> ## Phase B: Markets and pricing
> B1. Market-implied credit risk: mortgage-rate spread over Treasuries, agency vs. private-label pricing. Did the shift onto the public balance sheet compress the price of household credit risk?
> B2. CRT spreads as the market's price for the risk the GSEs hand back; link to A2.
> B3. Scenario engine: parameterized stress model (default rate, loss severity, recovery path) splitting losses public vs. private, interactive in the app.
> B4. Scenarios for policy regimes: GSEs released from conservatorship, student-loan reform, recession. Look up the current status of these debates; don't assume.
> Data rule for all phases: check availability first. If a series is paywalled (Bloomberg, ICE, etc.), say so and propose a free proxy. Never fabricate data.
>
> ## Phase C: Forecasting
> C1. Nowcast the public share between quarterly Z.1 releases using higher-frequency data (monthly/weekly series).
> C2. Forecast model with purged rolling-origin validation, leakage tests, prediction intervals and naive/AR benchmarks, mirroring the validation discipline of my repo-market-model project.
> C3. Report forecast accuracy honestly, including where the model fails.
>
> ## Phase D: AI research system (cover all four challenge formats)
> Skills (.claude/skills/):
> - z1-release-update: new release → reload → validate → "what moved" note
> - claim-check: trace any number to its query, series and vintage; flag mismatches
> - chart-from-sql: query → publication-quality chart in the project's style
> - research-memo: findings → 2-page memo for a named market audience
> Subagents (.claude/agents/), each with a clear role and logged output:
> - analyst (runs queries), skeptic (tries to break every claim: revisions, definition changes, double counting, vintages), quant-reviewer (checks methods: leakage, overfitting, bad tests), editor (style and sourcing rules)
> - debate log of every challenge and its resolution in claims/review-log.md
> MCP server: household-credit-mcp covering Z.1, FRED, NY Fed CCP and CBO data. Built to publish: tests, docs, install instructions.
> Anthropic API app: "Ask Hot Potato" on the live site. Tool use against the database; every answer cites the query behind it; it refuses forecasts it can't support.
> Cowork plugin: package the skills, subagents and MCP as a "Fed Data Desk" plugin for a research team, with before/after outputs.
>
> ## Phase E: Evaluation
> E1. Question-to-SQL benchmark: ~100 questions with verified answers, scored for Haiku vs. Sonnet vs. Opus on accuracy, cost and latency.
> E2. Planted-error test: insert deliberate errors and measure the skeptic's and quant-reviewer's catch rate and misses.
> E3. Regression suite: rerun E1–E2 whenever prompts or models change; chart results over time.
> E4. Red-team "Ask Hot Potato": try to get misleading answers or unsupported forecasts; document guardrails and failures.
>
> ## Phase F: Reproducibility, living site, publication
> F1. Source register: every published number links to query, series, vintage and validation status (claims/register.csv), surfaced in the app.
> F2. `make all` (ingest → validation → models → build) and a GitHub Action running validation and evals on every push, with badges in the README.
> F3. Scheduled updates after each Z.1 release; Claude drafts release notes, I approve before publishing.
> F4. Open data: downloads, a public API, accessible chart descriptions.
> F5. Building with Claude log: models per task, token cost, errors Claude made and how they were caught. Start logging now.
> F6. Outputs: the challenge write-up (2–3 pages) and 4-minute demo script, plus a working-paper draft (SSRN format) and a short op-ed.
>
> ## Rules
> - Stop for my approval after PLAN.md and after each phase.
> - Never present an unverified number as fact; label estimates.
> - Don't touch the production Vercel deployment without asking.
> - Commit after each task with clear messages.
> - Token discipline: excerpts over whole files, no data dumps in chat, cheaper models or subagents for routine work, the main model for analysis and review. Suggest /clear or a new session at phase boundaries.
> - Any steps I must run myself: exact copy-pasteable commands.

Commits: none

### 2026-11-03T23:25:51Z

> Clone the repository eleonorabjornberg/repo-market-model into this session.

Commits: none

### 2026-11-03T23:26:10Z

> Tell me what you need for the environment

Commits: none

### 2026-11-03T23:28:59Z

> Why are you saving anything locally? Where am I supposed to find the variables?

Commits: none

### 2026-11-03T23:29:32Z

> Where am i supposed to find them?

Commits: none

### 2026-11-03T23:29:46Z

> Let's start a fresh repo and project for this

Commits: none

### 2026-11-03T23:30:31Z

> I'm worried that you're still using tableau

Commits: none

### 2026-11-03T23:30:49Z

> Otherwise i'm happy to keep using this repo.

Commits: none

### 2026-11-03T23:44:54Z

> Don't worry about the demo yet, let me handle that. We're just going to build the product.

Commits: none

### 2026-11-03T23:45:42Z

> Kill any reference to the challenge. Just make sure the structure suits the required submission

Commits: 96372fd Add PLAN.md and start the Building-with-Claude log

### 2026-11-03T23:46:22Z

> <!-- reply 3 -->
> > Will you register for the Freddie Mac and Fannie Mae data accounts yourself if their credit-risk-transfer deal data needs a login?
>
> I will
>
> <!-- reply -->
> > Which market audiences should the research memos target?
>
> Financial institutions
>
> <!-- reply -->
> > Which licence do you want for the open data and code?
>
> Probably mit, unless you have a better idea
>
>
> I approve the plan.

Commits: none

### 2026-11-03T23:48:47Z

> Use subagents where you can, let's make this process as efficient as possible

Commits: none

### 2026-11-03T23:50:52Z

> <!-- reply 1 -->
> > One decision for you: should I apply the 0.2 migration to the production Supabase database? That removes tableau_reader there. I can apply it through the Supabase connector, or you can run it yourself in the SQL editor. Either way, afterwards you set the password, so it never goes through the chat:
>
> Go ahead

Commits: 63a4c0f Remove Tableau; add research_reader role and CLAUDE.md (task 0.1, 0.2)

### 2026-11-03T23:53:31Z

<!-- unsure: pasted web page text in a desktop-app message; may be a paste rather than typed prose -->
> For the fred 
>
> * 
>
> * [Release Calendar](https://fred.stlouisfed.org/releases/calendar)
> * Tools
> * [News](https://news.research.stlouisfed.org/category/fred-announcements/)
> * [Blog](https://fredblog.stlouisfed.org/)
> * About
>
> API Key
> Describe the application or program you intend to write:

Commits: a553a0e Add prompt archive for the 27-29 Oct build session (task 0.10); e0359ba Log Phase 0 subagent runs and errors; mark 0.5 and 0.8 in progress; 0db9a0a Add validation suite (task 0.3); b6de1e6 Record provenance for every raw download (task 0.4)

### 2026-11-03T23:59:05Z

> <!-- reply 1 -->
> > 0.2 read-only role: done and live in production. research_reader exists with read-only sessions and a 15-second statement timeout, and tableau_reader is gone. The site’s public read access is unchanged. Supabase’s security check shows only two notices, both on tables that are private on purpose. Two steps are yours:
> > In the Supabase SQL editor, run:
> > Add DATABASE_URL_READONLY to the environment settings. It’s the Session pooler string from Supabase → Connect, with the user research_reader.ldckwcqucdnwarysqmgj.
>
> i don't understand this at all

Commits: 6de6ee1 Add z1-release-update skill (task 0.8)

### 2026-11-04T00:03:37Z

> I'm going to start a new session with the new environment. Give me the prompt

Commits: none

### 2026-11-04T00:10:52Z

> yes, fix them, the other session is running

Commits: b44cfde Fix two stale numbers in published copy
