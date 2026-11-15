import Experience from "@/components/Experience";
import { getSeries } from "@/lib/data";
import { fmtPct } from "@/lib/format";
import { ask, hero, site } from "@/content/story";
import { ClaimRef } from "@/components/claims/SourceRef";
import { HeroButtons } from "@/components/home/HeroButtons";
import { Meaning } from "@/components/home/Meaning";
import { BuildBand } from "@/components/home/BuildBand";
import AskPanel from "@/components/ask/AskPanel";
import { deploymentGate } from "@/lib/ask/gate";

// Statically built, refreshed daily (the pipeline updates Supabase quarterly).
export const revalidate = 86400;

// Home (R1, 2026-11-15): hero, explorer, what it means, Ask, built with Claude. Copy is Eleonora's approved copy.
export default async function Page() {
  const series = await getSeries();
  const last = series.dates.length - 1;
  const gate = deploymentGate();
  return (
    <main>
      <header className="band hero">
        <span className="hero__disc hero__disc--a" aria-hidden />
        <span className="hero__disc hero__disc--b" aria-hidden />
        <span className="hero__disc hero__disc--c" aria-hidden />
        <div className="wrap hero__inner">
          <p className="tag">{site.kicker}</p>
          <h1 aria-label={site.title}>
            <span className="riso-2" aria-hidden>Hot</span>{" "}
            <span className="riso" aria-hidden>Potato</span>
          </h1>
          <p className="hero__lede">
            When a household loan goes bad, whoever holds it takes the loss. In 1952 the public sector held{" "}
            <ClaimRef id="public_share_1952q1">{fmtPct(series.publicShare[1])}</ClaimRef> of American household debt. Today it
            holds <b className="hi"><ClaimRef id="public_share_2026q2">{fmtPct(series.publicShare[last])}</ClaimRef></b>.
            Watch <ClaimRef id="scope_usd_2026q2_atlas_headline">$19 trillion</ClaimRef> change hands, or ask the data a question.
          </p>
          <p className="hero__for">{hero.forLine}</p>
          <HeroButtons />
        </div>
      </header>

      <Experience series={series} />

      <Meaning latestShare={series.publicShare[last]} />

      <section id="ask" className="band band--ask" aria-labelledby="ask-h">
        <div className="wrap wrap--narrow">
          <h2 id="ask-h">{ask.title}</h2>
          <p className="band__lede">{ask.intro}</p>
          <AskPanel examples={ask.examples} disabledMessage={gate.ok ? undefined : gate.message} />
        </div>
      </section>

      <BuildBand />
    </main>
  );
}
