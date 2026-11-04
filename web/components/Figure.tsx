import type { ReactNode } from "react";
import { Sourced } from "@/components/claims/SourceRef";

interface Props {
  id: string;
  label: string;
  title: string;
  caption: string;
  source: string;
  children: ReactNode;
}

/** A numbered figure: a native SVG chart with its caption and source. */
export function Figure({ id, label, title, caption, source, children }: Props) {
  return (
    <figure className="figure" id={id} aria-labelledby={`${id}-title`}>
      <header className="figure__head">
        <p className="figure__label">{label}</p>
        <h3 className="figure__title" id={`${id}-title`}>{title}</h3>
        <p className="figure__caption"><Sourced text={caption} /></p>
      </header>
      {children}
      <p className="figure__source">
        <span>Source</span> {source}
      </p>
    </figure>
  );
}
