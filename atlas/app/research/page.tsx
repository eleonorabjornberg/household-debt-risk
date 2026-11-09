import type { Metadata } from "next";
import Link from "next/link";
import { research } from "@/content/research";
import { parseInline } from "@/lib/markdown";
import { MarkdownInline } from "@/components/Markdown";

export const metadata: Metadata = {
  title: "Research · Hot Potato",
  description: "Every research task behind Hot Potato: the question, the method, its status and the full write-up.",
};

export default function ResearchIndex() {
  return (
    <main className="pg">
      <header className="pg-col">
        <p className="tag">Research</p>
        <h1>The quantitative work behind the site</h1>
        <p className="pg-lede">
          One entry per research task: the question it set out to answer, the method in one line, its status as recorded
          in the project plan, and the full write-up. Inconclusive and failed results are listed with the rest.
        </p>
        <p className="pg-caption">
          Questions and statuses are quoted from the project plan. The one-line methods are Claude’s summaries. Each
          write-up is shown as it stands in the repository, including its own “Claude draft” banner.
        </p>
      </header>
      <ol className="research-list">
        {research.map((r) => (
          <li key={r.id} className="research-item" data-testid={`research-${r.id}`}>
            <h2><span className="tag">{r.id}</span></h2>
            <dl>
              <div><dt>Question</dt><dd><MarkdownInline c={parseInline(r.question)} /></dd></div>
              <div><dt>Method</dt><dd>{r.method}</dd></div>
              <div>
                <dt>Status{r.statusRow ? ` (plan, ${r.statusRow} row)` : ""}</dt>
                <dd>
                  {r.status.join("; ")}
                  {r.blocked && <>: <MarkdownInline c={parseInline(r.blocked)} /></>}
                </dd>
              </div>
            </dl>
            <p className="research-links">
              {r.slug ? <Link href={`/research/${r.slug}`}>Read the write-up</Link> : <span>No write-up: the task is blocked.</span>}
              {r.extra && <> · <Link href={r.extra.href}>{r.extra.label}</Link></>}
            </p>
          </li>
        ))}
      </ol>
    </main>
  );
}
