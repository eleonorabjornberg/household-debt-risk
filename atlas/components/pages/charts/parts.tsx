"use client";
import type { ReactNode } from "react";

// Copied from web/components/charts/parts.tsx for the pages moved into Hot Potato (site-visible (b), 2026-11-07).
// The crisis-band helpers are left out: no moved page uses them.

export function Legend({ items, label }: { items: { key: string; label: string; color: string }[]; label?: string }) {
  return (
    <div className="legend" role="list" aria-label={label ?? "Legend"}>
      {label && <span className="legend__group">{label}</span>}
      {items.map((it) => (
        <span key={it.key} className="legend__item" role="listitem">
          <span className="legend__swatch" style={{ background: it.color }} aria-hidden="true" />
          {it.label}
        </span>
      ))}
    </div>
  );
}

export function Segmented<T extends string>({
  label, value, options, onChange, id,
}: { label: string; value: T; options: { value: T; label: string }[]; onChange: (v: T) => void; id: string }) {
  return (
    <div className="segmented" role="radiogroup" aria-labelledby={`${id}-label`}>
      <span className="segmented__label" id={`${id}-label`}>{label}</span>
      <div className={options.length > 3 ? "segmented__opts segmented__opts--grid" : "segmented__opts"}>
        {options.map((o) => (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={value === o.value}
            className="segmented__opt"
            onClick={() => onChange(o.value)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function DataTable({ caption, columns, rows, note }: { caption: string; columns: string[]; rows: ReactNode[][]; note?: string }) {
  return (
    <details className="datatable">
      <summary>Show the data as a table</summary>
      <div className="tablewrap">
        <table>
          <caption>{caption}</caption>
          <thead>
            <tr>{columns.map((c, i) => <th key={i} scope="col">{c}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                {r.map((c, j) => (j === 0 ? <th key={j} scope="row">{c}</th> : <td key={j}>{c}</td>))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {note && <p className="datatable__note">{note}</p>}
    </details>
  );
}
