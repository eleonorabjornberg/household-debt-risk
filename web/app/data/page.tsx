import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Metadata } from "next";
import { cacheLife } from "next/cache";
import dict from "@/lib/opendata.json";
import { getSnapshotMeta } from "@/lib/data";

const V1 = "/downloads/v1";

interface IndexFile { vintages: { id: string; path: string; vintages: Record<string, string>; files: { table: string }[] }[] }

/** public/downloads/v1/index.json, written by scripts/make-downloads.mjs before the build. */
async function getArchive(): Promise<IndexFile["vintages"]> {
  "use cache";
  cacheLife("days");
  try {
    const idx = JSON.parse(await readFile(path.join(process.cwd(), "public", "downloads", "v1", "index.json"), "utf8")) as IndexFile;
    return idx.vintages ?? [];
  } catch {
    return [];
  }
}

export const metadata: Metadata = {
  title: "Data",
  description: "Download the derived tables behind Who Holds the Debt? as CSV or JSON, with a data dictionary and licence notes.",
};

interface Column { name: string; type: string; unit?: string; desc: string }
interface Table {
  name: string; title: string; grain: string; licence: string; redistribute: boolean; pending?: string; link?: string;
  sources: string[]; validation: string; columns: Column[];
}
interface Licence { name: string; url: string; attribution?: string; source_identifier?: string; applies_to: string }
interface Dictionary {
  units: Record<string, string>; licences: Record<string, Licence>; tables: Table[];
  third_party_not_redistributed: { series: string; name: string; why: string; link: string }[];
}

// PLAN F4. Files are written to public/downloads/v1 by scripts/make-downloads.mjs before every build, from
// the same snapshots the charts use and the archived releases in opendata/archive. The dictionary is
// opendata/dictionary.json (copied to lib/).
export default async function DataPage() {
  const d = dict as Dictionary;
  const [meta, archive] = await Promise.all([getSnapshotMeta(), getArchive()]);
  const cc = d.licences["cc-by-4.0"];
  return (
    <main>
      <header className="page-head wrap">
        <div className="col">
          <p className="kicker">Data</p>
          <h1>Download the data</h1>
          <p>
            The quarterly tables behind every chart on this site, as CSV or JSON, with a data dictionary. Derived data are
            under {cc.name}; New York Fed figures keep the New York Fed&apos;s own terms; the code is MIT. Copyrighted
            third-party series are linked, not redistributed. Every past data release stays downloadable.
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
            <a href={`${V1}/latest/dictionary.json`}>dictionary.json</a> (all tables, columns, units and licences) ·{" "}
            <a href={`${V1}/latest/LICENSE-DATA.md`}>LICENSE-DATA.md</a> ·{" "}
            <a href={`${V1}/index.json`}>index.json</a> (every release and file). Paths under <code className="code">{V1}/</code>{" "}
            are stable: names and columns change only with a new version.
          </p>
          {archive.length > 0 && (
            <p>
              Past releases:{" "}
              {archive.map((v, i) => (
                <span key={v.id}>
                  {i > 0 ? " · " : ""}
                  <a href={`${V1}/${v.path}dictionary.json`}>Z.1 {v.vintages.z1 ?? v.id}</a>
                </span>
              ))}{" "}
              (same file names under <code className="code">{V1}/vintages/&lt;release&gt;/</code>).
            </p>
          )}
          <p>Units: {Object.entries(d.units).map(([k, v]) => `${k} = ${v}`).join("; ")}.</p>
          {d.tables.map((t) => (
            <article key={t.name} id={t.name} className="catalog">
              <h3>{t.title}</h3>
              <p>
                <code className="code">{t.name}</code> · {t.grain} · {d.licences[t.licence].name}
              </p>
              {t.redistribute ? (
                <p>
                  <a href={`${V1}/latest/${t.name}.csv`} download>CSV</a> · <a href={`${V1}/latest/${t.name}.json`} download>JSON</a>
                  {d.licences[t.licence].source_identifier && (
                    <>
                      {" "}· <a href={`${V1}/latest/NOTICE-nyfed.txt`}>NOTICE</a>. {d.licences[t.licence].attribution}{" "}
                      {d.licences[t.licence].source_identifier}.
                    </>
                  )}
                </p>
              ) : (
                <p>
                  Not redistributed here: get it from <a href={t.link}>the source</a>.
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
