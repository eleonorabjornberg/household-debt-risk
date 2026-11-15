// "About the data" and the decade table, moved from the home page to /methods in R1 (2026-11-15).
import { fmtPct, fmtTrillions, nearestIndex, sumReal } from "@/lib/format";
import type { Series } from "@/lib/types";
import { coda, PILE_LONG } from "@/content/story";
import { Sourced } from "../claims/SourceRef";

export function DataNotes({ series }: { series: Series }) {
  const firstYear = Number(series.dates[0].slice(0, 4)) + 1;
  const lastYear = Number(series.dates[series.dates.length - 1].slice(0, 4));
  const decades: number[] = [];
  for (let y = firstYear; y <= lastYear; y++) if (y % 10 === 0 || y === lastYear) decades.push(y);
  return (
    <section className="pg-section" aria-labelledby="about-data">
      <div className="pg-col">
        <h2 id="about-data">{coda.sourcesTitle}</h2>
        <ul>
          {coda.sources.map((s) => <li key={s}><Sourced text={s} /></li>)}
        </ul>
        <details className="table">
          <summary>The numbers by decade</summary>
          <div className="tablewrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Year</th>
                  <th scope="col">Public share</th>
                  <th scope="col">Total</th>
                  {PILE_LONG.map((l) => <th key={l} scope="col">{l}</th>)}
                </tr>
              </thead>
              <tbody>
                {decades.map((y) => {
                  const i = nearestIndex(series.dates, `${y}-12-31`);
                  const c = series.real[i];
                  return (
                    <tr key={y}>
                      <th scope="row">{y}</th>
                      <td>{fmtPct(series.publicShare[i])}</td>
                      <td>{fmtTrillions(sumReal(c))}</td>
                      {c.map((cell, b) => <td key={b}>{fmtTrillions(cell[0] + cell[1])}</td>)}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </details>
        <p className="pg-caption">
          {series.cpiBase ? `CPI base: ${series.cpiBase}. ` : ""}
          Data loaded from {series.source === "supabase" ? "Supabase" : "the pipeline's snapshot"}.
        </p>
      </div>
    </section>
  );
}
