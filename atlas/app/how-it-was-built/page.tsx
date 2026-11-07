import type { Metadata } from "next";
import { build } from "@/content/build";
import { Sourced } from "@/components/claims/SourceRef";

// Moved from web/app/how-it-was-built (site-visible (b), 2026-11-07: one site). Copy in content/build.ts.
export const metadata: Metadata = {
  title: "How it was built · Hot Potato",
  description: "The stack, the connectors and the division of work behind Hot Potato.",
};

function DefinitionList({ items }: { items: { name: string; body: string }[] }) {
  return (
    <dl className="caveats">
      {items.map((i) => (
        <div key={i.name}>
          <dt>{i.name}</dt>
          <dd>{i.body}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function HowItWasBuiltPage() {
  return (
    <main className="pg">
      <header className="pg-col">
        <p className="tag">How it was built</p>
        <h1>Built with Claude Code</h1>
        <p className="pg-lede"><Sourced text={build.lede} /></p>
      </header>

      <section className="pg-section" aria-labelledby="flow">
        <div className="pg-col">
          <h2 id="flow">From the Fed to this page</h2>
          <ol className="lineage">
            {build.flow.map((f) => (
              <li key={f.step}>
                <strong>{f.step}</strong>
                <span><Sourced text={f.text} /></span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="stack">
        <div className="pg-col">
          <h2 id="stack">Tools and services</h2>
          <DefinitionList items={build.stack} />
        </div>
      </section>

      <section className="pg-section" aria-labelledby="connectors">
        <div className="pg-col">
          <h2 id="connectors">Connectors used</h2>
          <p>{build.connectorsLede}</p>
          <DefinitionList items={build.connectors} />
        </div>
      </section>

      <section className="pg-section" aria-labelledby="agents">
        <div className="pg-col">
          <h2 id="agents">Parallel agents</h2>
          <p>{build.agentsLede}</p>
          <DefinitionList items={build.agents} />
        </div>
      </section>

      <section className="pg-section" aria-labelledby="human">
        <div className="pg-col">
          <h2 id="human">What the person did</h2>
          <ol className="lineage">
            {build.human.map((h, i) => (
              <li key={h}>
                <strong>{i + 1}</strong>
                <span>{h}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </main>
  );
}
