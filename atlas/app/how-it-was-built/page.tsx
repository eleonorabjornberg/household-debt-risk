import type { Metadata } from "next";
import { build, REPO_TREE } from "@/content/build";
import { BuildSchema } from "@/components/pages/BuildSchema";
import { BuildTiles } from "@/components/home/BuildBand";
import { PotatoPerson } from "@/components/Potato";
import { ClaimRef } from "@/components/claims/SourceRef";

// Built with Claude (R1, 2026-11-15): tiles, the two-loop diagram, the E1 table with the two eval notes, and what
// Eleonora did. Copy in content/build.ts (lede and tiles approved by Eleonora in R1).
export const metadata: Metadata = {
  title: "Built with Claude · Hot Potato",
  description: "The Claude skills, subagents, MCP server, API, hooks and plugin behind Hot Potato.",
};

export default function HowItWasBuiltPage() {
  return (
    <main className="build-page">
      <section className="band band--build band--page" aria-labelledby="build-title">
        <div className="wrap">
          <h1 id="build-title" className="page-h">Built with Claude</h1>
          <p className="band__lede">{build.lede}</p>
          <BuildTiles />
        </div>
      </section>

      <section className="band" aria-labelledby="schema">
        <div className="wrap">
          <h2 id="schema">How it works</h2>
          <BuildSchema workflow={build.schema.workflow} build={build.schema.build} />
        </div>
      </section>

      <section className="band band--tight" aria-labelledby="evals">
        <div className="wrap">
          <h2 id="evals">Testing the tools</h2>
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
          <ul className="build-notes">
            {build.evals.notes.map((n) => <li key={n}>{n}</li>)}
          </ul>
          <p><a href={`${REPO_TREE}/evals`}>Pre-registrations, runs and results →</a></p>
        </div>
      </section>

      <section className="band band--tight" aria-labelledby="human">
        <div className="wrap">
          <h2 id="human">What Eleonora did</h2>
          <div className="build-human">
            <PotatoPerson potatoes={1} tone="neutral" width={72} />
            <ul className="build-notes">
              {build.human.map((h) => <li key={h}>{h}</li>)}
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
