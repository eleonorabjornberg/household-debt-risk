import Experience from "@/components/Experience";
import { getSeries } from "@/lib/data";
import { fmtPct } from "@/lib/format";
import { site } from "@/content/story";
import { ClaimRef } from "@/components/claims/SourceRef";

// Statically built, refreshed daily (the pipeline updates Supabase quarterly).
export const revalidate = 86400;

export default async function Page() {
  const series = await getSeries();
  const last = series.dates.length - 1;
  return (
    <main>
      <header className="hero">
        <span className="hero__disc hero__disc--c" aria-hidden />
        <div className="hero__inner">
          <p className="hero__kicker tag">{site.kicker}</p>
          <h1 aria-label={site.title}>
            <span className="riso-2" aria-hidden>Hot</span>
            <span className="riso" aria-hidden>Potato</span>
          </h1>
          <p className="hero__lede">
            In 1952 the public sector held <b className="old"><ClaimRef id="public_share_1952q1">{fmtPct(series.publicShare[1])}</ClaimRef></b> of American household
            debt. Today it holds <b className="pub"><ClaimRef id="public_share_2026q2">{fmtPct(series.publicShare[last])}</ClaimRef></b>. Watch it change hands, one{" "}
            <ClaimRef id="atlas_dot_unit">$50 billion</ClaimRef> dot at a time.
          </p>
          <p className="hero__cue" aria-hidden>Scroll ↓</p>
        </div>
      </header>
      <Experience series={series} />
    </main>
  );
}
