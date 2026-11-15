// "What it means" (R1): three cards, each with its stat, a potato figure, a title and one sentence. Each card's rule,
// stat and figure wear the ink of the holder it is about. Figures are decorative.
import { fmtPct } from "@/lib/format";
import { meaning } from "@/content/story";
import { ClaimRef, Sourced } from "../claims/SourceRef";
import { PotatoPerson } from "../Potato";

// The register row behind each card's stat (the stat is wrapped explicitly, the sentence through <Sourced>).
const STAT_CLAIM = ["public_share_2026q2", "gfc_jump_pp", "public_share_of_uncoll_2026q2"];
const FIGURE: { potatoes: number; pose: "hold" | "toss" | "sweat" }[] = [
  { potatoes: 6, pose: "sweat" },
  { potatoes: 3, pose: "toss" },
  { potatoes: 5, pose: "hold" },
];

export function Meaning({ latestShare }: { latestShare: number }) {
  return (
    <section className="band band--meaning" aria-labelledby="meaning-h">
      <div className="wrap">
        <h2 id="meaning-h">{meaning.title}</h2>
        <ol className="cards">
          {meaning.points.map((p, i) => (
            <li key={p.title} className="card" style={{ "--holder": `var(--pile-${p.pile})` } as React.CSSProperties}>
              <div className="card__top">
                <span className={`card__stat${i === 0 ? " hi" : ""}`}>
                  <ClaimRef id={STAT_CLAIM[i]}>{p.stat === "{share}" ? fmtPct(latestShare) : p.stat}</ClaimRef>
                </span>
                <PotatoPerson potatoes={FIGURE[i].potatoes} pose={FIGURE[i].pose} ink={`var(--pile-${p.pile})`} width={84} />
              </div>
              <h3>{p.title}</h3>
              <p><Sourced text={p.body} /></p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
