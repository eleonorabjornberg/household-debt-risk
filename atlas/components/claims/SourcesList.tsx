// GENERATED COPY: edit claims/site/SourcesList.tsx in the repo root, not the copy in a site.
// The /sources page body: one entry per register row with a location on this site (PLAN F1).
import { claims } from "./SourceRef";
import { STATUS_TEXT } from "@/lib/claims-core";

const REPO = "https://github.com/eleonorabjornberg/household-debt-risk/blob/main";

export function SourcesList() {
  const counts = claims.reduce<Record<string, number>>((m, c) => ({ ...m, [c.validation]: (m[c.validation] ?? 0) + 1 }), {});
  return (
    <div className="sources">
      <p className="sources__summary">
        {claims.length} published numbers.{" "}
        {Object.entries(counts)
          .sort()
          .map(([k, n]) => `${n} ${k}`)
          .join(" · ")}
        .
      </p>
      <dl className="sources__legend">
        {Object.entries(STATUS_TEXT).map(([k, v]) => (
          <div key={k}>
            <dt className={`claim__status claim__status--${k.toLowerCase()}`}>{k}</dt>
            <dd>{v}.</dd>
          </div>
        ))}
      </dl>
      <ol className="sources__list">
        {claims.map((c) => (
          <li key={c.id} id={c.id} className="sources__item">
            <p className="sources__head">
              <span className="sources__display">{c.display.join(" · ")}</span>
              <span className={`claim__status claim__status--${c.validation.toLowerCase()}`}>
                {c.validation}
                {c.checkId ? ` · check ${c.checkId}` : ""}
              </span>
            </p>
            <p className="sources__claim">{c.claim}</p>
            <dl className="sources__fields">
              <div><dt>Register id</dt><dd><code>{c.id}</code></dd></div>
              <div><dt>Value</dt><dd>{c.value} ({c.unit})</dd></div>
              <div><dt>Period</dt><dd>{c.period}</dd></div>
              <div><dt>Vintage</dt><dd>{c.vintage}</dd></div>
              <div><dt>Computed by</dt><dd><code>{c.computation}</code></dd></div>
              <div><dt>Series</dt><dd>{c.series.length ? c.series.join(" ") : "n/a"}</dd></div>
              {c.notes && <div><dt>Notes</dt><dd>{c.notes}</dd></div>}
              <div>
                <dt>Printed at</dt>
                <dd>{c.locations.join(", ")}</dd>
              </div>
              <div>
                <dt>Register</dt>
                <dd><a href={`${REPO}/${c.register}`}>{c.register}</a></dd>
              </div>
            </dl>
          </li>
        ))}
      </ol>
    </div>
  );
}
