import type { Metadata } from "next";
import { SourcesList } from "@/components/claims/SourcesList";

export const metadata: Metadata = {
  title: "Sources",
  description: "Every number on this site, with its computation, series, vintage and validation status.",
};

// PLAN F1: the claims register rows behind every number on the site. Hover a number on any page for
// its row; clicking it lands here. Rows come from claims/register.csv via lib/claims.json.
export default function SourcesPage() {
  return (
    <main>
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">Sources</p>
          <h1>Where every number comes from</h1>
          <p>
            Each number on this site has a row in the project&apos;s claims register: what is claimed, how it was
            computed, which series and data vintage it uses, and whether an independent check recomputes it.
          </p>
        </div>
      </header>
      <section className="mblock wrap">
        <div className="col">
          <SourcesList />
        </div>
      </section>
    </main>
  );
}
