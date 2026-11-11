import type { Metadata } from "next";
import { DraftBanner } from "@/components/pages/DraftBanner";
import { PotatoPerson } from "@/components/Potato";
import { Suspense } from "react";
import exposures from "@/lib/b3/exposures.json";
import { ScenarioTool } from "@/components/scenarios/ScenarioTool";
import dfast from "@/lib/b3/preset_dfast2026.json";
import replay from "@/lib/b3/preset_replay_2008_2012.json";

// Horizons and years come from the preset files, not from the copy (editor mkt-e28).
const stressQ = dfast.presets.dfast2026_proxy.classes.mortgage.timing.length;
const replayQ = replay.presets.replay_2008_2012_proxy.classes.mortgage.timing.length;
const stressYear = dfast.source.match(/\b(20\d\d) Supervisory Stress Test/)?.[1] ?? "";
const replayYears = (() => {
  const m = replay.source.match(/(\d{4})Q\d-(\d{4})Q\d/);
  return m ? `${m[1]}–${m[2].slice(2)}` : "";
})();

// PLAN B3, moved from web/ into Hot Potato (site-visible (b), 2026-11-07). Linked from the top bar.
export const metadata: Metadata = {
  title: "Scenarios · Hot Potato",
  description: "Try a loss scenario on today's household debt and see how the losses split between public and private books.",
};

export default function ScenariosPage() {
  return (
    <main className="pg">
      <DraftBanner testId="b3-draft-banner" />
      <header>
        <div className="pg-col">
          <p className="tag">Scenarios</p>
          <h1>If loans go bad, which lenders’ books record the losses?</h1>
          <p className="pg-lede">Pick a scenario and see whose books take the losses. Fed Z.1 balances as of {exposures.as_of}.</p>
          <div className="sc-sides" aria-label="Who counts as public, who as private">
            <figure>
              <PotatoPerson potatoes={6} tone="public" width={84} />
              <figcaption><strong>Public</strong> Federal government, Fannie Mae, Freddie Mac, agency pools, state and local.</figcaption>
            </figure>
            <figure>
              <PotatoPerson potatoes={4} tone="private" pose="sweat" width={84} />
              <figcaption><strong>Private</strong> Banks, finance companies, private securitization.</figcaption>
            </figure>
          </div>
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
          <h2>Before you quote a number</h2>
          <ul className="sc-caveats">
            <li><strong>Who holds is not who bears.</strong> Insurance, credit-risk transfer and guarantees move some risk.</li>
            <li><strong>The presets are proxies.</strong> Bank loss rates ({stressYear} stress test, {replayYears} replay; {stressQ} and {replayQ} quarters) applied to every holder.</li>
            <li><strong>Known biases.</strong> The replay likely overstates the public share; some stress-test choices push it up, others down.</li>
            <li><strong>Federal student loans</strong> are left out of the main presets, which lowers the public share.</li>
            <li><strong>Today’s balances, today’s dollars.</strong> Not a forecast of defaults.</li>
          </ul>
          <p><a href="/research/b3">Method, biases and checks →</a></p>
        </div>
      </section>
    </main>
  );
}
