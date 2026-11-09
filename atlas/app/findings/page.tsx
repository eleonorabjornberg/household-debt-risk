import type { Metadata } from "next";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { parseMarkdown } from "@/lib/markdown";
import { Markdown } from "@/components/Markdown";

// Docket 48 site-findings (b), 2026-11-08: analysis/findings.md as it stands, unedited.
// content/findings.md is copied from analysis/findings.md by scripts/sync-findings.mjs before every build.
export const metadata: Metadata = {
  title: "Findings · Hot Potato",
  description: "The analysis findings behind Hot Potato, as written in analysis/findings.md.",
};

export default async function FindingsPage() {
  const src = await readFile(path.join(process.cwd(), "content", "findings.md"), "utf8");
  return (
    <main className="pg">
      <article className="pg-col findings">
        <Markdown blocks={parseMarkdown(src)} />
      </article>
    </main>
  );
}
