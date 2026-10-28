import { Figure } from "@/components/Figure";
import { FixtureBanner } from "@/components/FixtureBanner";
import { Prose } from "@/components/Prose";
import { CollateralCharts } from "@/components/charts/CollateralCharts";
import { CrisisMultiples } from "@/components/charts/CrisisMultiples";
import { PaymentPriority } from "@/components/charts/PaymentPriority";
import { PublicShareSpark } from "@/components/charts/PublicShareSpark";
import { RatchetChart } from "@/components/charts/RatchetChart";
import { CrisisScrolly } from "@/components/scrolly/CrisisScrolly";
import {
  collateral, crisisByCrisis, crisisScrolly, hero, holderNotes, now, nyFedVsZ1, paymentPriority, ratchet, type Chapter,
} from "@/content/story";
import { getStoryData, overallSource } from "@/lib/data";
import { fill, pct, quarterLabel, usdFromBillions } from "@/lib/format";
import { collateralData, crises, crisisSteps, crisisWindows, headline, nyfedData, publicSeries, ratchetData } from "@/lib/shape";
import { scrollyTableauEnabled, TABLEAU_VIEWS, tableauEmbedFor } from "@/lib/tableau";

export default async function Home() {
  const data = await getStoryData();
  const h = headline(data);
  const crisisList = crises(data);
  const ratchetRows = ratchetData(data);
  const scrollyEmbed = scrollyTableauEnabled() ? tableauEmbedFor(TABLEAU_VIEWS.scrolly) : null;

  const tokens: Record<string, string> = {
    latestQuarter: quarterLabel(h.latestDate),
    firstQuarter: quarterLabel(h.firstDate),
    latestYear: h.latestDate.slice(0, 4),
    firstYear: h.firstDate.slice(0, 4),
    publicShareLatest: pct(h.publicShareLatest, 0),
    publicShareFirst: pct(h.publicShareFirst, 0),
    publicShare2007: pct(h.publicShare2007, 1),
    publicShare2011: pct(h.publicShare2011, 0),
    nyQuarter: h.nyLatestDate ? quarterLabel(h.nyLatestDate) : "–",
    nyTotal: usdFromBillions(h.nyTotal),
    nyMortgageChange: usdFromBillions(h.nyMortgageChange),
    nyMortgageChangeAbs: h.nyMortgageChange === null ? "–" : usdFromBillions(Math.abs(h.nyMortgageChange)),
    shareFederalDirect: pct(h.shareFederalDirect, 0),
    shareGse: pct(h.shareGse, 0),
    shareUncollateralized: pct(h.shareUncollateralized, 0),
    fedMbsShareLatest: pct(h.fedMbsShareLatest, 0),
  };
  const f = (s: string) => fill(s, tokens);
  const chapters = [ratchet, crisisByCrisis, collateral, paymentPriority, now];

  return (
    <main>
      {overallSource(data.sources) === "fixture" && <FixtureBanner />}

      <header className="hero wrap">
        <div className="col-wide">
          <p className="kicker">{f(hero.kicker)}</p>
          <h1 className="hero__headline">{f(hero.headline)}</h1>
          <div className="hero__grid">
            <div>
              <p className="hero__dek">{f(hero.dek)}</p>
              <dl className="hero__facts">
                {hero.facts.map((x) => (
                  <div key={x.label}>
                    <dt>{x.label}</dt>
                    <dd>{x.value}</dd>
                  </div>
                ))}
              </dl>
              <p className="hero__factsource">{hero.factsSource}</p>
            </div>
            <div className="stat">
              <p className="stat__value">{pct(h.publicShareLatest, 1)}</p>
              <p className="stat__label">{hero.statLabel}</p>
              <div className="stat__chart">
                <p className="stat__charttitle">{f(hero.sparkTitle)}</p>
                <PublicShareSpark data={publicSeries(data)} crises={crisisList} title={f(hero.sparkTitle)} />
                <p className="stat__note">{f(hero.statNote)}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <aside className="hook wrap" aria-labelledby="hook-title">
        <div className="col-wide hook__inner">
          <p className="hook__label">NY Fed credit-report data · {tokens.nyQuarter}</p>
          <div className="hook__body">
            <h2 className="hook__title" id="hook-title">{nyFedVsZ1.title}</h2>
            {nyFedVsZ1.body.map((p, i) => <p key={i}>{p}</p>)}
          </div>
        </div>
      </aside>

      <nav className="toc wrap" aria-label="Chapters">
        <ol className="col-wide">
          {chapters.map((c) => (
            <li key={c.id}>
              <a href={`#${c.id}`}>
                <span>{c.number}</span>
                {c.title}
              </a>
            </li>
          ))}
        </ol>
      </nav>

      <ChapterSection chapter={ratchet} f={f}>
        <Figure id="fig-ratchet" label="Figure 1" tableauView={TABLEAU_VIEWS.ratchet} {...ratchet.figure}>
          <RatchetChart data={ratchetRows} crises={crisisList} title={ratchet.figure.title} />
        </Figure>
      </ChapterSection>

      <ChapterSection chapter={crisisByCrisis} f={f}>
        <section className="figure scrolly-figure" id="crisis-walkthrough" aria-labelledby="crisis-walkthrough-title">
          <header className="figure__head">
            <p className="figure__label">{crisisScrolly.label}</p>
            <h3 className="figure__title" id="crisis-walkthrough-title">{crisisScrolly.title}</h3>
            <p className="figure__caption">{crisisScrolly.intro}</p>
          </header>
          <CrisisScrolly
            steps={crisisSteps(data, crisisByCrisis.notes)}
            data={ratchetRows}
            crises={crisisList}
            embed={scrollyEmbed ? { scriptUrl: scrollyEmbed.scriptUrl, src: scrollyEmbed.src, needsToken: scrollyEmbed.needsToken } : null}
            title={crisisScrolly.title}
            copy={crisisScrolly}
            holderNotes={holderNotes}
          />
          <p className="figure__source">
            <span>Source</span> {ratchet.figure.source}
          </p>
        </section>
        <Figure id="fig-crises" label="Figure 2" tableauView={TABLEAU_VIEWS.crises} tableauHeight={1350} {...crisisByCrisis.figure}>
          <CrisisMultiples
            data={crisisWindows(data)}
            metricLabels={crisisByCrisis.metricLabels}
            notes={crisisByCrisis.notes}
            title={crisisByCrisis.figure.title}
          />
        </Figure>
      </ChapterSection>

      <ChapterSection chapter={collateral} f={f}>
        <Figure id="fig-collateral" label="Figure 3" tableauView={TABLEAU_VIEWS.collateral} {...collateral.figure}>
          <CollateralCharts data={collateralData(data)} crises={crisisList} labels={collateral.classLabels} title={collateral.figure.title} />
        </Figure>
      </ChapterSection>

      <ChapterSection chapter={paymentPriority} f={f}>
        <Figure id="fig-priority" label="Figure 4" tableauView={TABLEAU_VIEWS.priority} {...paymentPriority.figure}>
          <PaymentPriority data={nyfedData(data)} labels={paymentPriority.loanLabels} title={paymentPriority.figure.title} />
          <p className="chart__footnote">{paymentPriority.studentNote}</p>
        </Figure>
      </ChapterSection>

      <section className="chapter wrap" id={now.id} aria-labelledby={`${now.id}-title`}>
        <div className="col">
          <ChapterHead chapter={now} />
          <Prose paragraphs={now.body.map(f)} />
        </div>
        <div className="col-wide">
          <dl className="tiles">
            {now.tiles.map((t) => (
              <div key={t.label} className="tile">
                <dt className="tile__label">{t.label}</dt>
                <dd className="tile__value">{t.value}</dd>
              </div>
            ))}
          </dl>
          <p className="figure__source">
            <span>Source</span> {now.tilesSource}
          </p>
        </div>
      </section>
    </main>
  );
}

function ChapterHead({ chapter }: { chapter: Pick<Chapter, "id" | "number" | "title" | "lede"> }) {
  return (
    <header className="chapter__head">
      <p className="chapter__num">Chapter {chapter.number}</p>
      <h2 className="chapter__title" id={`${chapter.id}-title`}>{chapter.title}</h2>
      <p className="chapter__lede">{chapter.lede}</p>
    </header>
  );
}

function ChapterSection({ chapter, f, children }: { chapter: Chapter; f: (s: string) => string; children: React.ReactNode }) {
  return (
    <section className="chapter wrap" id={chapter.id} aria-labelledby={`${chapter.id}-title`}>
      <div className="col">
        <ChapterHead chapter={chapter} />
        <Prose paragraphs={chapter.body.map(f)} />
        {chapter.aside && (
          <aside className="aside">
            <h3>{chapter.aside.title}</h3>
            <p>{chapter.aside.body}</p>
          </aside>
        )}
      </div>
      {children}
    </section>
  );
}
