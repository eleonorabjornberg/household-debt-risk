import type { ReactNode } from "react";
import { tableauNote } from "@/content/story";
import { tableauConfig, tableauViewUrl } from "@/lib/tableau";
import { TableauViz } from "./TableauViz";

interface Props {
  id: string;
  label: string;
  title: string;
  caption: string;
  source: string;
  /** Tableau view path, e.g. "WhoHoldsTheDebt/Ratchet". Omit for native-only figures. */
  tableauView?: string;
  children: ReactNode;
}

/** A numbered figure: native chart, swapped for the Tableau view when Tableau is configured. */
export function Figure({ id, label, title, caption, source, tableauView, children }: Props) {
  const cfg = tableauView ? tableauConfig() : null;
  return (
    <figure className="figure" id={id} aria-labelledby={`${id}-title`}>
      <header className="figure__head">
        <p className="figure__label">{label}</p>
        <h3 className="figure__title" id={`${id}-title`}>{title}</h3>
        <p className="figure__caption">{caption}</p>
      </header>
      {cfg && tableauView ? (
        <TableauViz serverUrl={cfg.serverUrl} src={tableauViewUrl(cfg, tableauView)} title={title} fallback={children} />
      ) : (
        <>
          {children}
          {tableauView && <p className="figure__soon">{tableauNote}</p>}
        </>
      )}
      <p className="figure__source">
        <span>Source</span> {source}
      </p>
    </figure>
  );
}
