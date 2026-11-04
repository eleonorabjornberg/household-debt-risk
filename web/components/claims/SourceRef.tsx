// GENERATED COPY: edit claims/site/SourceRef.tsx in the repo root, not the copy in a site.
// Source popovers for registered numbers (PLAN F1). Works in Server and Client Components: no state,
// the popover opens on hover and keyboard focus with CSS (app/claims.css), and the number links to
// its row on /sources, so it also works without JavaScript and on touch screens.
import { Fragment, useId, type ReactNode } from "react";
import data from "@/lib/claims.json";
import { makeMatcher, STATUS_TEXT, type ClaimsFile } from "@/lib/claims-core";

const file = data as ClaimsFile;
export const claims = file.claims;
export const matcher = makeMatcher(claims);
export const SOURCES_PATH = "/sources";
const MAX_SERIES = 4;

export function ClaimRef({ id, children }: { id: string; children: ReactNode }) {
  const tip = useId();
  const c = matcher.byId.get(id);
  if (!c) {
    if (process.env.NODE_ENV !== "production") throw new Error(`ClaimRef: no register row "${id}"`);
    return <>{children}</>;
  }
  const extra = c.series.length - MAX_SERIES;
  return (
    <span className="claim">
      <a className="claim__num" href={`${SOURCES_PATH}#${c.id}`} aria-describedby={tip} data-claim={c.id}>
        {children}
      </a>
      <span className="claim__tip" role="tooltip" id={tip}>
        <span className={`claim__status claim__status--${c.validation.toLowerCase()}`}>
          {c.validation}
          {c.checkId ? ` · check ${c.checkId}` : ""}
        </span>
        <span className="claim__text">{c.claim}</span>
        <span className="claim__row"><b>Period</b> {c.period}</span>
        <span className="claim__row"><b>Vintage</b> {c.vintage}</span>
        {c.series.length > 0 && (
          <span className="claim__row">
            <b>Series</b> {c.series.slice(0, MAX_SERIES).join(", ")}
            {extra > 0 ? ` and ${extra} more` : ""}
          </span>
        )}
        <span className="claim__row"><b>Computed by</b> <code>{c.computation}</code></span>
        <span className="claim__more">{STATUS_TEXT[c.validation] ?? c.validation}. Click for the full register row.</span>
      </span>
    </span>
  );
}

/** Renders `text`, linking every registered number in it. `context` is nearby copy (a label). */
export function Sourced({ text, context }: { text: string; context?: string }) {
  return (
    <>
      {matcher.segment(text, context).map((s, i) =>
        typeof s === "string" ? (
          <Fragment key={i}>{s}</Fragment>
        ) : (
          <ClaimRef key={i} id={s.id}>{s.text}</ClaimRef>
        ),
      )}
    </>
  );
}
