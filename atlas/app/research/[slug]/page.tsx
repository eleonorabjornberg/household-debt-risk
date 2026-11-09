import type { Metadata } from "next";
import Link from "next/link";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { notFound } from "next/navigation";
import { parseMarkdown, plain } from "@/lib/markdown";
import { Markdown } from "@/components/Markdown";
import { research } from "@/content/research";

// One research write-up, research/<task>/README.md as it stands (copied to content/research/<slug>.md by
// scripts/sync-research.mjs, which only rewrites relative links). Like /findings, rendered without raw HTML.
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
  const ids = research.filter((r) => r.slug === slug).map((r) => r.id);
  return (
    <main className="pg">
      <p className="pg-caption"><Link href="/research">← All research</Link> · Write-up for {ids.join(", ")}</p>
      <article className="pg-col findings research-doc">
        <Markdown blocks={parseMarkdown(src)} />
      </article>
    </main>
  );
}
