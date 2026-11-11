import type { Metadata } from "next";
import { DraftBanner } from "@/components/pages/DraftBanner";
import { build } from "@/content/build";
import { Sourced } from "@/components/claims/SourceRef";
import { BuildSchema } from "@/components/pages/BuildSchema";
import { PotatoPerson } from "@/components/Potato";

// Moved from web/app/how-it-was-built (site-visible (b), 2026-11-07: one site). Copy in content/build.ts.
export const metadata: Metadata = {
  title: "How it was built · Hot Potato",
  description: "The sessions, tools, connectors and division of work behind Hot Potato.",
};

const REPO = "https://github.com/eleonorabjornberg/household-debt-risk/tree/main";

export default function HowItWasBuiltPage() {
  return (
    <main className="pg">
      <DraftBanner testId="build-draft-banner" />
      <header className="pg-col">
        <p className="tag">How it was built</p>
        <h1>Built with Claude Code</h1>
        <p className="pg-lede">{build.lede}</p>
      </header>

      <section aria-label="Claude capabilities used" className="build-tiles">
        {build.tiles.map((t) => (
          <a key={t.name} className="build-tile" href={`${REPO}/${t.href}`}>
            <strong>{t.name}</strong>
            <span>{t.body}</span>
          </a>
        ))}
      </section>

      <section className="pg-section" aria-labelledby="schema">
        <div className="pg-col">
          <h2 id="schema">How it works</h2>
          <p>{build.schema.lede}</p>
          <BuildSchema workflow={build.schema.workflow} build={build.schema.build} />
        </div>
      </section>

      <section className="pg-section" aria-labelledby="flow">
        <div className="pg-col">
          <h2 id="flow">From the Fed to this page</h2>
          <ol className="build-steps">
            {build.flow.map((f) => (
              <li key={f.step}><strong>{f.step}</strong> <Sourced text={f.text} /></li>
            ))}
          </ol>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="stack">
        <div className="pg-col">
          <h2 id="stack">Tools</h2>
          <div className="build-tiles build-tiles--small">
            {build.stack.map((t) => (
              <div key={t.name} className="build-tile"><strong>{t.name}</strong><span>{t.body}</span></div>
            ))}
          </div>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="human">
        <div className="pg-col">
          <h2 id="human">What Eleonora did</h2>
          <div className="build-cast" aria-hidden="true">
            <figure><PotatoPerson potatoes={1} tone="public" width={84} /><figcaption>Eleonora decides</figcaption></figure>
            <figure><PotatoPerson potatoes={3} tone="private" pose="toss" width={120} /><figcaption>Claude builds</figcaption></figure>
            <figure><PotatoPerson potatoes={2} tone="neutral" pose="sweat" width={84} /><figcaption>Subagents object</figcaption></figure>
          </div>
          <ul className="build-steps">
            {build.human.map((h) => <li key={h}>{h}</li>)}
          </ul>
        </div>
      </section>
    </main>
  );
}
