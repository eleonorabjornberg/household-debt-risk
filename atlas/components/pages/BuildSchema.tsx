// Schema of the workflow and build process on /how-it-was-built (2026-11-11). Plain HTML boxes and arrows, not a chart,
// so it wraps to a single column on a phone. Flat colours only: no gradients (Eleonora, gradients-55 (a)).
import { Sourced } from "@/components/claims/SourceRef";

type Step = { who: string; name: string; body: string };
type Lane = { title: string; loop: string; steps: Step[] };

const whoClass: Record<string, string> = {
  Eleonora: "schema-who-human",
  Claude: "schema-who-claude",
  Gate: "schema-who-gate",
  Data: "schema-who-data",
  Code: "schema-who-claude",
};

function SchemaLane({ lane, id }: { lane: Lane; id: string }) {
  return (
    <figure className="schema" aria-labelledby={id}>
      <figcaption id={id} className="schema-title">{lane.title}</figcaption>
      <ol className="schema-steps">
        {lane.steps.map((s) => (
          <li key={s.name} className={`schema-step ${whoClass[s.who] ?? ""}`}>
            <span className="schema-who">{s.who}</span>
            <strong className="schema-name">{s.name}</strong>
          </li>
        ))}
      </ol>
      {/* Step details folded (R1: the page stays under 250 words); open for what each step does. */}
      <details className="schema-more">
        <summary>What each step does</summary>
        <dl>
          {lane.steps.map((s) => (
            <div key={s.name}><dt>{s.name}</dt><dd><Sourced text={s.body} /></dd></div>
          ))}
        </dl>
      </details>
      <p className="schema-loop">
        <span aria-hidden="true">↺ </span>
        {lane.loop}
      </p>
    </figure>
  );
}

export function BuildSchema({ workflow, build }: { workflow: Lane; build: Lane }) {
  return (
    <div className="schema-wrap" data-testid="build-schema">
      <SchemaLane lane={workflow} id="schema-workflow" />
      <SchemaLane lane={build} id="schema-build" />
    </div>
  );
}
