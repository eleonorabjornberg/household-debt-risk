import type { Metadata } from "next";
import Link from "next/link";
import { research } from "@/content/research";
import { parseInline } from "@/lib/markdown";
import { MarkdownInline } from "@/components/Markdown";

export const metadata: Metadata = {
  title: "Research · Hot Potato",
  description: "Every research task behind Hot Potato: the question, the method and the write-up.",
};

export default function ResearchIndex() {
  return (
    <main className="pg">
      <header className="pg-col">
        <p className="tag">Research</p>
        <h1>The quantitative work behind the site</h1>
        <p className="pg-lede">Each question, its method and the write-up, failed and inconclusive ones included.</p>
        <p className="pg-caption">Methods are Claude’s one-line summaries. Write-ups keep their “Claude draft” banners.</p>
      </header>
      <ol className="research-list">
        {research.map((r) => (
          <li key={r.id} className="research-item" data-testid={`research-${r.id}`}>
            <h2><span className="tag">{r.id}</span></h2>
            <dl>
              <div><dt>Question</dt><dd><MarkdownInline c={parseInline(r.question)} /></dd></div>
              <div><dt>Method</dt><dd>{r.method}</dd></div>
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
