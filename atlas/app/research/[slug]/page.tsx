import type { Metadata } from "next";
import Link from "next/link";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import { parseInline, parseMarkdown, plain } from "@/lib/markdown";
import { Markdown, MarkdownInline } from "@/components/Markdown";
import { research } from "@/content/research";

// One research write-up, research/<task>/README.md as it stands (copied to content/research/<slug>.md by
// scripts/sync-research.mjs, which only rewrites relative links). Like the findings on /dashboard, rendered without raw HTML.
const SLUGS = [...new Set(research.map((r) => r.slug).filter((s): s is string => Boolean(s)))];

export const dynamicParams = false;
export function generateStaticParams() {
  return SLUGS.map((slug) => ({ slug }));
}

async function load(slug: string) {
  if (!SLUGS.includes(slug)) return null;
  return readFile(path.join(process.cwd(), "content", "research", `${slug}.md`), "utf8");
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const src = await load(slug);
  const h1 = src ? parseMarkdown(src).find((b) => b.t === "heading") : undefined;
  return { title: `${h1 && h1.t === "heading" ? plain(h1.c) : "Research"} · Hot Potato` };
}

export default async function ResearchPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const src = await load(slug);
  if (!src) notFound();
  const entries = research.filter((r) => r.slug === slug);
  const ids = entries.map((r) => r.id);
  return (
    <main className="pg">
      <p className="pg-caption"><Link href="/research">← All research</Link> · Write-up for {ids.join(", ")}</p>
      {/* "In short" box (review list P1, 2026-11-11): the task's question and the one-line method from the
          /research index, so the box adds no new text and no new numbers. */}
      <aside className="in-short" aria-label="In short">
        <p className="tag">In short</p>
        <ul>
          {entries.map((r) => (
            <li key={r.id}><strong>{r.id}.</strong> <MarkdownInline c={parseInline(r.question)} /></li>
          ))}
          {entries.map((r) => <li key={`${r.id}-m`}>{r.method}</li>)}
          <li>The full write-up follows.</li>
        </ul>
      </aside>
      <article className="pg-col findings research-doc">
        <Markdown blocks={parseMarkdown(src)} />
      </article>
    </main>
  );
}
