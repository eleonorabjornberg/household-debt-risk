import type { Metadata } from "next";
import { DraftBanner } from "@/components/pages/DraftBanner";
import { build } from "@/content/build";
import { BuildSchema } from "@/components/pages/BuildSchema";
import { PotatoPerson } from "@/components/Potato";
import { ClaimRef } from "@/components/claims/SourceRef";

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
          <p className="pg-caption"><a href="/methods#lineage">Each data step in detail: Methods →</a></p>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="evals">
        <div className="pg-col">
          <h2 id="evals">Testing the tools</h2>
          <p>{build.evals.lede}</p>
          <table className="pg-table">
            <caption>{build.evals.e1.caption}</caption>
            <thead><tr><th scope="col">Model</th><th scope="col">Answerable questions</th><th scope="col">Correct refusals</th></tr></thead>
            <tbody>
              {build.evals.e1.rows.map((r) => (
                <tr key={r.model}>
                  <th scope="row">{r.model}</th>
                  <td><ClaimRef id={r.answer.id}>{r.answer.text}</ClaimRef></td>
                  <td><ClaimRef id={r.refuse.id}>{r.refuse.text}</ClaimRef></td>
                </tr>
              ))}
            </tbody>
          </table>
          <ul className="build-steps">
            {build.evals.notes.map((n) => <li key={n}>{n}</li>)}
          </ul>
          <p className="pg-caption"><a href={`${REPO}/evals`}>Pre-registrations, runs and results →</a></p>
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
