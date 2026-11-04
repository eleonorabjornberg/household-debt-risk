import type { Metadata } from "next";
import Link from "next/link";
import { SourcesList } from "@/components/claims/SourcesList";

export const metadata: Metadata = {
  title: "Sources · Hot Potato",
  description: "Every number on Hot Potato, with its computation, series, vintage and validation status.",
};

// PLAN F1: the claims register rows behind every number on the page. Hover a number for its row;
// clicking it lands here. Rows come from claims/register.csv via lib/claims.json.
export default function SourcesPage() {
  return (
    <main className="sources-page">
      <p><Link href="/">← Hot Potato</Link></p>
      <h1>Where every number comes from</h1>
      <p>
        Each number on Hot Potato has a row in the project&apos;s claims register: what is claimed, how it was computed,
        which series and data vintage it uses, and whether an independent check recomputes it.
      </p>
      <SourcesList />
    </main>
  );
}
