import type { Metadata } from "next";
import { PotatoPerson } from "@/components/Potato";
import { Suspense } from "react";
import Link from "next/link";
import exposures from "@/lib/b3/exposures.json";
import { ScenarioTool } from "@/components/scenarios/ScenarioTool";


// PLAN B3, moved from web/ into Hot Potato (site-visible (b), 2026-11-07). Linked from the top bar.
export const metadata: Metadata = {
  title: "Scenarios · Hot Potato",
  description: "Try a loss scenario on today's household debt and see how the losses split between public and private books.",
};

export default function ScenariosPage() {
  return (
    <main className="pg">
      <header>
        <div className="pg-col">
          <p className="tag">Scenarios</p>
          <h1>If loans go bad, which lenders’ books record the losses?</h1>
          <p className="pg-lede">Pick a scenario and see whose books take the losses. Fed Z.1 balances as of {exposures.as_of}.</p>
          <div className="sc-sides" aria-label="Who counts as public, who as private">
            <figure>
              <PotatoPerson potatoes={6} tone="public" width={84} />
              <figcaption><strong>Public</strong></figcaption>
            </figure>
            <figure>
              <PotatoPerson potatoes={4} tone="private" pose="sweat" width={84} />
              <figcaption><strong>Private</strong></figcaption>
            </figure>
          </div>
          <p className="pg-caption"><a href="/methods#scope">Who counts as public and who as private →</a></p>
        </div>
      </header>
      <section style={{ marginTop: 32 }}>
        <div>
          <Suspense fallback={<p>Loading the scenario tool…</p>}>
            <ScenarioTool />
          </Suspense>
        </div>
      </section>
      <section className="pg-section">
        <div>
          <p><a href="/methods#limits">Limits of these estimates →</a> · <Link href="/research/b3">Method and checks →</Link></p>
        </div>
      </section>
    </main>
  );
}
