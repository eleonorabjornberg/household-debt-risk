import Experience from "@/components/Experience";
import { getSeries } from "@/lib/data";
import { fmtPct } from "@/lib/format";
import { site } from "@/content/story";

// Statically built, refreshed daily (the pipeline updates Supabase quarterly).
export const revalidate = 86400;

export default async function Page() {
  const series = await getSeries();
  const last = series.dates.length - 1;
  return (
    <main>
      <header className="hero">
        <p className="hero__kicker">{site.kicker}</p>
        <h1>
          Hot <em>Potato</em>
        </h1>
        <p className="hero__lede">
          In 1952 the public sector held {fmtPct(series.publicShare[1])} of American household debt. Today it holds{" "}
          {fmtPct(series.publicShare[last])}. Watch it change hands, one $50 billion dot at a time.
        </p>
        <p className="hero__cue" aria-hidden>Scroll ↓</p>
      </header>
      <Experience series={series} />
    </main>
  );
}
