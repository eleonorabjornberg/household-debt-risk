import type { Metadata } from "next";
import { readFile } from "node:fs/promises";
import path from "node:path";
import catalog from "@/content/series_catalog.json";
import { methods } from "@/content/methods";
import { getSeries } from "@/lib/data";
import { Sourced } from "@/components/claims/SourceRef";

// Moved from web/app/methods (site-visible (b), 2026-11-07: one site). Copy in content/methods.ts.
// Statically built and refreshed daily, like the home page.
export const revalidate = 86400;

export const metadata: Metadata = {
  title: "Methods · Hot Potato",
  description: "Data lineage, the series catalog and caveats behind Hot Potato.",
};

interface SnapshotMeta { cpi_base_quarter?: string; vintages?: Record<string, string> }

/** public/data/meta.json, copied from the pipeline's snapshots by scripts/copy-data.mjs (optional). */
async function getSnapshotMeta(): Promise<SnapshotMeta | null> {
  try {
    const parsed = JSON.parse(await readFile(path.join(process.cwd(), "public", "data", "meta.json"), "utf8"));
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as SnapshotMeta) : null;
  } catch {
    return null;
  }
}

/** "2007-12-31" -> "2007 Q4" (as web/lib/format.ts) */
function quarterLabel(iso: string): string {
  return `${iso.slice(0, 4)} Q${Math.ceil(Number(iso.slice(5, 7)) / 3)}`;
}

const supabaseConfigured = () =>
  Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY));

interface CatalogSeries {
  id: string;
  source: string;
  role: string;
  desc: string;
  debt_type?: string;
  risk_bucket?: string;
  collateral_class?: string;
}
interface Catalog {
  risk_buckets: Record<string, { label: string; public: boolean }>;
  collateral_classes: Record<string, { label: string; collateral_series: string | null }>;
  series: CatalogSeries[];
}

const ROLE_LABELS: Record<string, string> = {
  total: "Totals and identities",
  cc_type: "Consumer credit by type",
  collateral: "Collateral values",
  mortgage_holder: "1–4 family mortgage holders",
  cc_holder: "Consumer credit holders",
  overlay: "Overlay (never summed)",
  context: "Context",
  nyfed: "NY Fed Household Debt and Credit",
};

export default async function MethodsPage() {
  const cat = catalog as Catalog;
  const [series, meta] = await Promise.all([getSeries(), getSnapshotMeta()]);
  const latest = series.dates.at(-1);
  const roles = [...new Set(cat.series.map((s) => s.role))];
  const sourceSummary = series.source === "supabase" ? "Supabase (live mart schema)" : "Pipeline snapshot (public/data)";

  return (
    <main className="pg">
      <header className="pg-col">
        <p className="tag">Methods</p>
        <h1>How this was made</h1>
        <p className="pg-lede"><Sourced text={methods.lede} /></p>
      </header>

      <section className="pg-section" aria-labelledby="lineage">
        <div className="pg-col">
          <h2 id="lineage">Data lineage</h2>
          <ol className="lineage">
            {methods.lineage.map((l) => (
              <li key={l.step}>
                <strong>{["raw", "core", "mart"].includes(l.step) ? <code>{l.step}</code> : l.step}</strong>
                <span><Sourced text={l.text} /></span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="scope">
        <div className="pg-col">
          <h2 id="scope">Scope and definitions</h2>
          <div>
            {methods.scope.map((p, i) => <p key={i}><Sourced text={p} /></p>)}
          </div>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="caveats">
        <div className="pg-col">
          <h2 id="caveats">Caveats</h2>
          <dl className="caveats">
            {methods.caveats.map((c) => (
              <div key={c.title}>
                <dt><Sourced text={c.title} /></dt>
                <dd><Sourced text={c.body} context={c.title} /></dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="catalog">
        <div>
          <div className="pg-col">
            <h2 id="catalog">Series catalog</h2>
            <p className="pg-caption">{methods.catalogIntro}</p>
          </div>
          <div className="catalog">
            <h3>Risk buckets</h3>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr><th scope="col">Bucket</th><th scope="col">Label</th><th scope="col">Public</th></tr>
                </thead>
                <tbody>
                  {Object.entries(cat.risk_buckets).map(([k, v]) => (
                    <tr key={k}>
                      <td><code className="code">{k}</code></td>
                      <td>{v.label}</td>
                      <td><span className={`pill${v.public ? " pill--public" : ""}`}>{v.public ? "Public" : "Private"}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3>Collateral classes</h3>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr><th scope="col">Class</th><th scope="col">Label</th><th scope="col">Collateral series</th></tr>
                </thead>
                <tbody>
                  {Object.entries(cat.collateral_classes).map(([k, v]) => (
                    <tr key={k}>
                      <td><code className="code">{k}</code></td>
                      <td>{v.label}</td>
                      <td>{v.collateral_series ? <code className="code">{v.collateral_series}</code> : "None"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {roles.map((role) => (
              <div key={role}>
                <h3>{ROLE_LABELS[role] ?? role}</h3>
                <div className="tablewrap">
                  <table>
                    <thead>
                      <tr>
                        <th scope="col">Series</th>
                        <th scope="col">Source</th>
                        <th scope="col">Description</th>
                        <th scope="col">Bucket / class</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cat.series.filter((s) => s.role === role).map((s) => (
                        <tr key={s.id}>
                          <td><code className="code">{s.id}</code></td>
                          <td>{s.source === "z1" ? "Fed Z.1" : s.source === "fred" ? "FRED" : "NY Fed"}</td>
                          <td className="desc">{s.desc}</td>
                          <td>{s.risk_bucket ?? s.collateral_class ?? s.debt_type ?? ""}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="pg-section" aria-labelledby="build">
        <div className="pg-col">
          <h2 id="build">This build</h2>
          <dl className="status">
            <div><dt>Data source</dt><dd>{sourceSummary}</dd></div>
            <div><dt>Latest quarter</dt><dd>{latest ? quarterLabel(latest) : "–"}</dd></div>
            {meta?.vintages?.z1 && <div><dt>Z.1 release (vintage)</dt><dd>{meta.vintages.z1}</dd></div>}
            {meta?.vintages?.nyfed && <div><dt>NY Fed data retrieved</dt><dd>{meta.vintages.nyfed}</dd></div>}
            {meta?.cpi_base_quarter && <div><dt>Real dollars in prices of</dt><dd>{meta.cpi_base_quarter}</dd></div>}
            <div><dt>Supabase</dt><dd>{supabaseConfigured() ? "Configured" : "Not configured"}</dd></div>
          </dl>
          <p className="pg-caption" style={{ marginTop: "1rem" }}>
            Tables read by Hot Potato: debt_by_risk_holder, public_share, dim_crisis.
          </p>
        </div>
      </section>
    </main>
  );
}
