import type { Metadata } from "next";
import dict from "@/lib/opendata.json";
import { getSnapshotMeta } from "@/lib/data";

export const metadata: Metadata = {
  title: "Data",
  description: "Download the derived tables behind Who Holds the Debt? as CSV or JSON, with a data dictionary and licence notes.",
};

interface Column { name: string; type: string; unit?: string; desc: string }
interface Table {
  name: string; title: string; grain: string; licence: string; redistribute: boolean; pending?: string; link?: string;
  sources: string[]; validation: string; columns: Column[];
}
interface Licence { name: string; url: string; attribution?: string; applies_to: string }
interface Dictionary {
  units: Record<string, string>; licences: Record<string, Licence>; tables: Table[];
  third_party_not_redistributed: { series: string; name: string; why: string; link: string }[];
}

// PLAN F4. Files are written to public/downloads by scripts/make-downloads.mjs before every build, from
// the same snapshots the charts use. The dictionary is opendata/dictionary.json (copied to lib/).
export default async function DataPage() {
  const d = dict as Dictionary;
  const meta = await getSnapshotMeta();
  const cc = d.licences["cc-by-4.0"];
  return (
    <main>
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">Data</p>
          <h1>Download the data</h1>
          <p>
            The quarterly tables behind every chart on this site, as CSV or JSON, with a data dictionary. Derived data are
            under {cc.name}; the code is MIT. Third-party series are linked, not redistributed.
          </p>
        </div>
      </header>

      <section className="mblock wrap" aria-labelledby="files">
        <div className="col">
          <h2 id="files">Files</h2>
          {meta?.vintages && (
            <p>
              Source vintages: {Object.entries(meta.vintages).map(([k, v]) => `${k.toUpperCase()} ${v}`).join(" · ")}.
              {meta.cpi_base_quarter ? ` Real dollars are in prices of ${meta.cpi_base_quarter}.` : ""}
            </p>
          )}
          <p>
            <a href="/downloads/dictionary.json">dictionary.json</a> (all tables, columns, units and licences) ·{" "}
            <a href="/downloads/LICENSE-DATA.md">LICENSE-DATA.md</a>
          </p>
          <p>Units: {Object.entries(d.units).map(([k, v]) => `${k} = ${v}`).join("; ")}.</p>
          {d.tables.map((t) => (
            <article key={t.name} id={t.name} className="catalog">
              <h3>{t.title}</h3>
              <p>
                <code className="code">{t.name}</code> · {t.grain} · {d.licences[t.licence].name}
              </p>
              {t.redistribute ? (
                <p>
                  <a href={`/downloads/${t.name}.csv`} download>CSV</a> · <a href={`/downloads/${t.name}.json`} download>JSON</a>
                </p>
              ) : (
                <p>
                  Not redistributed here: get it from <a href={t.link}>the source</a>.{t.pending ? ` ${t.pending}` : ""}
                </p>
              )}
              <p>Sources: {t.sources.join("; ")}. {t.validation}</p>
              <div className="tablewrap">
                <table>
                  <caption className="sr-only">Columns of {t.name}</caption>
                  <thead>
                    <tr><th scope="col">Column</th><th scope="col">Type</th><th scope="col">Unit</th><th scope="col">Meaning</th></tr>
                  </thead>
                  <tbody>
                    {t.columns.map((c) => (
                      <tr key={c.name}>
                        <th scope="row"><code className="code">{c.name}</code></th>
                        <td>{c.type}</td>
                        <td>{c.unit ?? ""}</td>
                        <td className="desc">{c.desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="mblock wrap" aria-labelledby="licences">
        <div className="col">
          <h2 id="licences">Licences and attribution</h2>
          <dl className="caveats">
            {Object.entries(d.licences).map(([k, l]) => (
              <div key={k}>
                <dt><a href={l.url}>{l.name}</a></dt>
                <dd>{l.applies_to}{l.attribution ? ` Attribution: ${l.attribution}` : ""}</dd>
              </div>
            ))}
            {d.third_party_not_redistributed.map((x) => (
              <div key={x.series}>
                <dt>Not redistributed: <a href={x.link}>{x.name}</a></dt>
                <dd>{x.why}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>
    </main>
  );
}
