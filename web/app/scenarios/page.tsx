import type { Metadata } from "next";
import { Suspense } from "react";
import exposures from "@/lib/b3/exposures.json";
import { ScenarioTool } from "@/components/scenarios/ScenarioTool";

// PLAN B3. Reachable by URL only until Eleonora reviews it (no nav link; the coordinator holds the proposed one).
export const metadata: Metadata = {
  title: "Scenarios",
  description: "Try a loss scenario on today's household debt and see how the losses split between public and private books.",
};

export default function ScenariosPage() {
  return (
    <main>
      <div className="banner wrap" role="note" data-testid="b3-draft-banner">
        <p className="banner__inner col-wide">
          <strong>Claude draft</strong>
          <span>This page and its text were drafted by Claude for Eleonora to review and rewrite. It is not her text yet.</span>
        </p>
      </div>
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">Scenarios</p>
          <h1>If loans go bad, whose books take the loss?</h1>
          <p>
            Pick a scenario, or set your own default rates and loss severities. The tool applies them to the household debt
            outstanding in the latest Financial Accounts (Z.1, data as of {exposures.as_of}, released {exposures.z1_release}) and
            splits the losses by who holds each loan: the federal government, the GSEs and agency pools, and state and local
            governments on the public side; banks, finance companies and private securitization on the private side.
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
              credit-risk transfer and federal guarantees on privately held loans move some of the risk elsewhere; the optional
              transfer above covers only the first two, and only on GSE mortgages.
            </li>
            <li>
              <strong>The presets are proxies.</strong> They apply bank loss rates (the Fed’s stress-test projections, or banks’
              realised charge-offs in 2008–12) to every holder, including the GSEs and federal books, whose losses would differ.
              The stress-test presets cover nine quarters and the replay twenty, so they differ in horizon as well as severity.
            </li>
            <li>
              <strong>Known biases in the presets</strong> (details in the method notes): the replay applies the
              banks’ 2008–12 losses, which included loans the GSEs did not guarantee, so its public share of losses is probably
              an upper bound. In the stress-test presets, using the first-lien rate for all mortgages understates the junior
              liens that banks mostly hold, which pushes the public share up; federally guaranteed student loans held by private
              lenders count as private, which pushes it down. No preset applies credit-risk transfer or mortgage insurance.
            </li>
            <li>
              <strong>Federal student loans</strong> have no bank loss series. They are left out of the main presets; one
              variant gives them a weak proxy rate.
            </li>
            <li>
              <strong>Today’s balances.</strong> Every scenario is applied to current balances. Nothing here forecasts defaults.
            </li>
          </ul>
          <p>
            Method, sources and checks: <code>research/b3_scenarios/</code> in the project repository. The engine on this page is
            the same code that is tested there against the Python version, case by case.
          </p>
        </div>
      </section>
    </main>
  );
}
