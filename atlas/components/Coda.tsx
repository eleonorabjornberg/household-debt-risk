import { fmtPct, fmtTrillions, nearestIndex, sumReal } from "@/lib/format";
import { BUCKETS, type Series } from "@/lib/types";
import { coda, meaning, PILE_LONG, site } from "@/content/story";

export default function Coda({ series }: { series: Series }) {
  const firstYear = Number(series.dates[0].slice(0, 4)) + 1;
  const lastYear = Number(series.dates[series.dates.length - 1].slice(0, 4));
  const decades: number[] = [];
  for (let y = firstYear; y <= lastYear; y++) if (y % 10 === 0 || y === lastYear) decades.push(y);

  const latest = series.dates.length - 1;
  const fill = (text: string) =>
    text
      .replaceAll("{share}", fmtPct(series.publicShare[latest]))
      .replaceAll("{pls}", fmtTrillions(series.real[latest][BUCKETS.indexOf("private_securitization")].reduce((a, b) => a + b, 0)));

  return (
    <section className="coda" aria-labelledby="coda-title">
      <div className="coda__inner">
        <h2 id="coda-title">{meaning.title}</h2>
        <ol className="meaning">
          {meaning.points.map((p) => (
            <li key={p.title}>
              <span className="meaning__n">{fill(p.stat)}</span>
              <h3>{p.title}</h3>
              <p>{fill(p.body)}</p>
            </li>
          ))}
        </ol>

        <h2>{coda.sourcesTitle}</h2>
        <ul className="sources">
          {coda.sources.map((s) => <li key={s}>{s}</li>)}
        </ul>

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

        <p className="coda__more">
          The code, the data pipeline and the full analysis (methods, caveats and the crisis-by-crisis test) are on{" "}
          <a href={site.repo}>GitHub</a>.{" "}
          {series.cpiBase ? `CPI base: ${series.cpiBase}. ` : ""}
          Data loaded from {series.source === "supabase" ? "Supabase" : "the pipeline's snapshot"}.
        </p>
      </div>
    </section>
  );
}
