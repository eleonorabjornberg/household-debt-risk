import type { Metadata } from "next";
import Link from "next/link";
import { SourcesList } from "@/components/claims/SourcesList";
import { SourcesFilter } from "@/components/SourcesFilter";

export const metadata: Metadata = {
  title: "Sources · Hot Potato",
  description: "Every number on Hot Potato, with its computation, series, vintage and validation status.",
};

// PLAN F1: the claims register rows behind every number on the page. Hover a number for its row;
// clicking it lands here. Rows come from claims/register.csv via lib/claims.json.
// Header in the .pg pattern and the one-line intro: review list P1, 2026-11-11.
export default function SourcesPage() {
  return (
    <main className="pg">
      <header className="pg-col">
        <p className="tag">Sources</p>
        <h1>Where every number comes from</h1>
        <p className="pg-lede">Every number, its computation and its check.</p>
        <p className="pg-caption">How the data was built: <Link href="/methods">Methods</Link>.</p>
      </header>
      <SourcesFilter />
      <SourcesList />
    </main>
  );
}
