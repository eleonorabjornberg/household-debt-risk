// Copy for /how-it-was-built. Keep it factual: every tool and connector listed here was actually used.

export const build = {
  lede:
    "This project was built in a single working session by one person and Claude Code, Anthropic's coding agent, working in a cloud environment. The person made the editorial and account decisions; Claude researched the angle, wrote the code, ran the analysis and operated the services through connectors. This page lists what was used and who did what.",

  flow: [
    { step: "Sources", text: "Federal Reserve Z.1 Financial Accounts (bulk CSV), FRED and the New York Fed Household Debt and Credit report." },
    { step: "Pipeline", text: "A Python package (hhdebt, managed with uv) downloads the sources, checks that every holder adds up to its published total, and builds the analysis tables. More than 40 automated tests." },
    { step: "Warehouse", text: "Supabase Postgres in three layers: raw (every vintage), core (latest values) and mart (analysis-ready). The website reads mart through Supabase's API with a read-only public key." },
    { step: "Refresh", text: "A GitHub Actions workflow re-runs the pipeline after each quarterly Z.1 release, reloads Supabase and runs the tests." },
    { step: "Analysis", text: "A Python notebook tested the original thesis with placebo windows. The thesis failed, and the story was rewritten around what the data showed." },
    { step: "Tableau", text: "A script generates the Tableau workbook; it is published to Tableau Public and embedded here with Tableau's Embedding API, which lets the page zoom and highlight the chart as you read." },
    { step: "Website", text: "Next.js on Vercel. Every chart has a built-in version, so the page works even when Tableau is unavailable." },
  ],

  stack: [
    { name: "GitHub", body: "Source code, history and the quarterly refresh workflow (GitHub Actions)." },
    { name: "Supabase", body: "Hosted Postgres database and its REST API. Row-level security keeps the raw and core layers private." },
    { name: "Vercel", body: "Builds and hosts this site, and redeploys on every push to the main branch." },
    { name: "Tableau Public", body: "Hosts the interactive dashboard embedded in the story." },
    { name: "Google Sheets (planned)", body: "Will feed Tableau Public with current data pulled from this site, so the dashboard refreshes without being republished. Until then, the dashboard is republished by hand after each quarterly update." },
    { name: "Python, pandas, uv, pytest", body: "Data pipeline, analysis and tests." },
    { name: "Next.js, React, TypeScript", body: "The story site. Charts are hand-drawn SVG." },
  ],

  connectorsLede:
    "Claude reaches outside services through connectors: authorised links to the person's own accounts. These are the ones this project used, and what they were used for.",
  connectors: [
    { name: "GitHub", body: "Attached the repository to the session, pushed every commit and triggered the data-refresh workflow." },
    { name: "Supabase", body: "Created the database project, applied the schema migrations, ran Supabase's security checks and read the public API key for the site." },
    { name: "Google Drive and Google Sheets", body: "Created the spreadsheet that will relay data to Tableau Public." },
    { name: "Vercel", body: "Looked up the account. The connector had no access to the personal account, so the Vercel project itself was created in the dashboard by hand." },
    { name: "Web search and fetch", body: "Background research on household debt, and downloads of the Fed, FRED and NY Fed data." },
  ],
  notConnected:
    "Tableau has no connector or publishing API for Tableau Public, so the workbook is opened and saved to Tableau Public in the desktop app by hand.",

  agentsLede:
    "The larger pieces were built by several Claude agents working in parallel, each owning one folder. The main session wrote the shared contract between them, reviewed each result, checked the numbers against each other and made the commits.",
  agents: [
    { name: "Pipeline agent", body: "Data extraction, the warehouse load, tests and the refresh workflow." },
    { name: "Analysis agent", body: "The thesis test, the findings write-up and the Tableau specifications." },
    { name: "Website agent", body: "This site, its charts and the Tableau integration." },
    { name: "Workbook agent", body: "The script that generates the Tableau workbook, and the beginner's guide." },
  ],

  human: [
    "Chose the topic, the angle and the tools, and approved each plan.",
    "Created the GitHub repository and the Vercel project, and set the site's environment variables.",
    "Added the database connection as a GitHub secret, so the password never passed through the chat.",
    "Opened the workbook in Tableau, fixed the stacking order and published it to Tableau Public.",
    "Reviewed the live site and asked for layout and wording changes.",
  ],
};
