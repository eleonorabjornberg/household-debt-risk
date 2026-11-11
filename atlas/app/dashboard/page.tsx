import type { Metadata } from "next";
import { DraftBanner } from "@/components/pages/DraftBanner";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { Markdown } from "@/components/Markdown";
import { computeTiles, holderMix, loanPanel } from "@/lib/dashboard";
import { parseMarkdown, plain } from "@/lib/markdown";

// PLAN F7, docket 54 (Eleonora, 2026-11-10): a Dashboard tab for a market reader, merged with Findings.
// Core tiles and panels on top, computed from the mart snapshots in public/data (the vintage the register
// cites); below them analysis/findings.md, shown whole and unedited (docket 48), folded closed by default
// (site review 2026-11-11: too much text on first view).
// /findings redirects here (next.config.ts).
export const metadata: Metadata = {
  title: "Dashboard · Hot Potato",
  description: "Household debt now: who holds it, how much collateral backs it, and where delinquency is moving, with the full findings folded below.",
};

async function json<T>(name: string): Promise<T> {
  return JSON.parse(await readFile(path.join(process.cwd(), "public", "data", `${name}.json`), "utf8")) as T;
}

export default async function DashboardPage() {
  const [share, coverage, nyfed, holders, dim, src] = await Promise.all([
    json<Parameters<typeof computeTiles>[0]["share"]>("public_share"),
    json<Parameters<typeof computeTiles>[0]["coverage"]>("collateral_coverage"),
    json<Parameters<typeof computeTiles>[0]["nyfed"]>("nyfed_by_type"),
    json<Parameters<typeof holderMix>[0]>("debt_by_risk_holder"),
    json<Parameters<typeof holderMix>[1]>("dim_risk_bucket"),
    readFile(path.join(process.cwd(), "content", "findings.md"), "utf8"),
  ]);
  const tiles = computeTiles({ share, coverage, nyfed });
  const blocks = parseMarkdown(src);
  const contents = blocks.flatMap((b) => (b.t === "heading" && b.level === 2 ? [{ id: b.id, text: plain(b.c) }] : []));

  return (
    <main className="pg">
      <DraftBanner testId="dash-draft-banner" />
      <header>
        <div className="pg-col">
          <p className="tag">Dashboard</p>
          <h1>Household debt now</h1>
          <p className="pg-lede">Four numbers to watch each quarter.</p>
        </div>
      </header>
      <Dashboard tiles={tiles} mix={holderMix(holders, dim)} loans={loanPanel(nyfed)} />
      <details className="pg-col findings-fold" id="findings">
        <summary>The full findings ({contents.length} sections)</summary>
        <nav aria-label="Findings contents">
          <ol className="dash-toc">
            {contents.map((c) => <li key={c.id}><a href={`#${c.id}`}>{c.text}</a></li>)}
          </ol>
        </nav>
        <article className="findings">
          <Markdown blocks={blocks} />
        </article>
      </details>
    </main>
  );
}
