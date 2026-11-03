import type { Metadata } from "next";
import { build } from "@/content/build";

export const metadata: Metadata = {
  title: "How it was built",
  description: "The stack, the connectors and the division of work behind Who Holds the Debt?",
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
    <main>
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">How it was built</p>
          <h1>Built with Claude Code</h1>
          <p>{build.lede}</p>
        </div>
      </header>

      <section className="mblock wrap" aria-labelledby="flow">
        <div className="col">
          <h2 id="flow">From the Fed to this page</h2>
          <ol className="lineage">
            {build.flow.map((f) => (
              <li key={f.step}>
                <strong>{f.step}</strong>
                <span>{f.text}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mblock wrap" aria-labelledby="stack">
        <div className="col">
          <h2 id="stack">Tools and services</h2>
          <DefinitionList items={build.stack} />
        </div>
      </section>

      <section className="mblock wrap" aria-labelledby="connectors">
        <div className="col">
          <h2 id="connectors">Connectors used</h2>
          <div className="prose"><p>{build.connectorsLede}</p></div>
          <DefinitionList items={build.connectors} />
        </div>
      </section>

      <section className="mblock wrap" aria-labelledby="agents">
        <div className="col">
          <h2 id="agents">Parallel agents</h2>
          <div className="prose"><p>{build.agentsLede}</p></div>
          <DefinitionList items={build.agents} />
        </div>
      </section>

      <section className="mblock wrap" aria-labelledby="human">
        <div className="col">
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
