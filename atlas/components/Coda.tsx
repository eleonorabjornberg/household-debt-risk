"use client";

import { useMemo, useState } from "react";
import { fmtPct, fmtTrillions, nearestIndex, sumReal } from "@/lib/format";
import type { Series } from "@/lib/types";
import { coda, PILE_LONG, site } from "@/content/story";

export default function Coda({ series }: { series: Series }) {
  const firstYear = Number(series.dates[0].slice(0, 4)) + 1;
  const lastYear = Number(series.dates[series.dates.length - 1].slice(0, 4));
  const years = useMemo(() => Array.from({ length: lastYear - firstYear + 1 }, (_, i) => firstYear + i), [firstYear, lastYear]);
  const [year, setYear] = useState(2008);

  const q = nearestIndex(series.dates, `${year}-12-31`);
  const cells = series.real[q];
  const total = sumReal(cells);
  const share = series.publicShare[q];
  const holders = cells.map((c, b) => ({ b, v: c[0] + c[1] })).sort((a, b) => b.v - a.v);
  const decades = years.filter((y) => y % 10 === 0 || y === lastYear);

  return (
    <section className="coda" aria-labelledby="coda-title">
      <div className="coda__inner">
        <h2 id="coda-title">{coda.title}</h2>
        <p className="coda__lede">{coda.lede}</p>
        <label className="coda__pick">
          <span>Year</span>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>

        <figure className="receipt">
          <p className="receipt__year">{year === lastYear ? `${year} (latest)` : year}</p>
          <p className="receipt__big">{fmtPct(share)}</p>
          <p className="receipt__what">of US household debt held by the public sector</p>
          <dl>
            <div><dt>Public</dt><dd>{fmtTrillions(total * share)}</dd></div>
            <div><dt>Total</dt><dd>{fmtTrillions(total)}</dd></div>
            <div><dt>Largest holder</dt><dd>{PILE_LONG[holders[0].b]}</dd></div>
          </dl>
          <div className="receipt__bar" aria-hidden>
            <span style={{ width: `${share * 100}%` }} />
          </div>
          <figcaption>2026 dollars. Federal Reserve Z.1.</figcaption>
        </figure>
        <p>
          <a className="button" href={`/api/og?year=${year}`} download={`hot-potato-${year}.png`}>
            Download {year} as an image
          </a>
        </p>

        <details className="table">
          <summary>The numbers by decade</summary>
          <div className="table__scroll">
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

        <h2>{coda.sourcesTitle}</h2>
        <ul className="sources">
          {coda.sources.map((s) => <li key={s}>{s}</li>)}
        </ul>
        <p className="coda__more">
          The full analysis, with methods, caveats and the crisis-by-crisis test, is at{" "}
          <a href={site.original}>Who Holds the Debt?</a>{" "}
          {series.cpiBase ? `CPI base: ${series.cpiBase}. ` : ""}
          Data loaded from {series.source === "supabase" ? "Supabase" : "the pipeline's snapshot"}.
        </p>
      </div>
    </section>
  );
}
