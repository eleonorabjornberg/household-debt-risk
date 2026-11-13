import type { Metadata } from "next";
import { Suspense } from "react";
import exposures from "@/lib/b3/exposures.json";
import { ScenarioTool } from "@/components/scenarios/ScenarioTool";
import dfast from "@/lib/b3/preset_dfast2026.json";
import replay from "@/lib/b3/preset_replay_2008_2012.json";
import { DraftBanner } from "@/components/DraftBanner";

// Horizons and years come from the preset files, not from the copy (editor mkt-e28).
const stressQ = dfast.presets.dfast2026_proxy.classes.mortgage.timing.length;
const replayQ = replay.presets.replay_2008_2012_proxy.classes.mortgage.timing.length;
const stressYear = dfast.source.match(/\b(20\d\d) Supervisory Stress Test/)?.[1] ?? "";
const replayYears = (() => {
  const m = replay.source.match(/(\d{4})Q\d-(\d{4})Q\d/);
  return m ? `${m[1]}–${m[2].slice(2)}` : "";
})();

// PLAN B3. Reachable by URL only until Eleonora reviews it (no nav link; the coordinator holds the proposed one).
export const metadata: Metadata = {
  title: "Scenarios",
  description: "Try a loss scenario on today's household debt and see how the losses split between public and private books.",
};

export default function ScenariosPage() {
  return (
    <main>
      <DraftBanner testId="b3-draft-banner" />
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">Scenarios</p>
          <h1>If loans go bad, which lenders’ books record the losses?</h1>
          <p>
            Pick a scenario, or set your own default rates and loss severities. The tool applies them to the household debt
            outstanding in the Federal Reserve’s latest Financial Accounts of the United States (the “Z.1” release; data as of{" "}
            {exposures.as_of}, released {exposures.z1_release}) and splits the losses by who holds each loan. Public side: the
            federal government, the government-sponsored enterprises Fannie Mae and Freddie Mac (the GSEs) and the mortgage
            pools guaranteed by them and by Ginnie Mae (agency pools), and state and local governments. Private side: banks,
            finance companies and private securitization (loans packaged into bonds without a government guarantee).
          </p>
        </div>
      </header>
      <section className="wrap">
        <div className="col-wide">
          <Suspense fallback={<p>Loading the scenario tool…</p>}>
            <ScenarioTool />
          </Suspense>
        </div>
      </section>
      <section className="wrap" style={{ marginTop: "clamp(2.5rem, 5vw, 3.5rem)" }}>
        <div className="col">
          <h2>Read this before quoting a number</h2>
          <ul>
            <li>
              <strong>Who holds is not who bears.</strong> Losses are assigned to whoever holds the loan. Mortgage insurance,
              credit-risk transfer (deals in which the GSEs pay private investors to absorb part of their mortgage losses) and
              federal guarantees on privately held loans move some of the risk elsewhere. The optional transfer above stands for
              the first two, and only on mortgages held by the GSEs and in agency pools.
            </li>
            <li>
              <strong>The presets are proxies</strong>, that is, stand-ins: loss rates measured for banks, applied to every
              holder, including the GSEs and federal books, whose losses would differ. The stress-test presets use the Fed’s
              {" "}{stressYear} stress test: projected losses for the largest banks in a hypothetical severe recession (the
              “severely adverse” scenario). That is a test, not a forecast. The replay uses the share of their loans that banks
              actually wrote off, net of recoveries, quarter by quarter in {replayYears}. The stress-test presets cover {stressQ}
              {" "}quarters and the replay {replayQ}, so they differ in length as well as severity.
            </li>
            <li>
              <strong>Known biases in the presets</strong> (details in the method notes). The replay applies the banks’ losses
              of {replayYears}, which included loans the GSEs did not guarantee, so its public share of losses is probably an
              upper bound. Its cumulative rate adds up the quarterly write-off rates and applies the total to today’s balances,
              an approximation. In the stress-test presets, using the first-lien rate for all mortgages understates losses on
              second mortgages and home-equity lines, which banks mostly hold; that pushes the public share up. Federally
              guaranteed student loans held by private lenders count as private, which pushes it down. No preset applies
              credit-risk transfer or mortgage insurance.
            </li>
            <li>
              <strong>Federal student loans</strong> have no bank loss series, so the main presets leave them out. The federal
              government holds them, so leaving them out lowers the public share of losses. One variant gives them the stress
              test’s rate for other consumer loans, a weak stand-in.
            </li>
            <li>
              <strong>Today’s balances, today’s dollars.</strong> Every scenario is applied to current balances, in dollars
              that are neither discounted nor adjusted for inflation. Nothing here forecasts defaults.
            </li>
          </ul>
          <p>
            Method, sources and checks are in the folder <code>research/b3_scenarios/</code> of the project’s code repository.
            The engine on this page is a copy of the code tested there; on fixed test cases it matches the Python version up to
            computer rounding.
          </p>
        </div>
      </section>
    </main>
  );
}
