"use client";

// The explorer (R1, 2026-11-15): five chapter buttons and Play drive the potato stage; the scrubber sets the quarter
// directly. The canvas reports the quarter it shows; the readout follows. Chapter captions are Eleonora's approved copy.
import { useCallback, useEffect, useMemo, useState } from "react";
import DotStage, { type PileLabel } from "./DotStage";
import { buildTimeline, DOLLAR_UNIT_MUSD, SHARE_DOTS, type Lens } from "@/lib/timeline";
import { fmtPct, fmtQuarter, fmtTrillions, nearestIndex, sumReal } from "@/lib/format";
import type { Series } from "@/lib/types";
import { chapters, PILE_LONG, PILE_NAMES } from "@/content/story";
import { Sourced } from "./claims/SourceRef";

function useReducedMotion(): boolean {
  const [rm, setRm] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setRm(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
  return rm;
}

/** Legend key: the stage's potato, filled (mortgage) or outlined (consumer credit), in navy. */
function LegendPotato({ filled }: { filled: boolean }) {
  return (
    <svg className="legend__potato" viewBox="-12 -10 25 20" width={18} height={14} aria-hidden>
      <path d="M-10 0 C-10 -8 -2 -7.5 3 -7 C11 -6.5 11.5 1 9 4.5 C6 8.5 -7 8 -10 0 Z"
        fill={filled ? "var(--ink)" : "var(--paper)"} stroke="var(--ink)" strokeWidth={filled ? 1.5 : 3} strokeLinejoin="round" />
    </svg>
  );
}

/** Window event the hero's "Play the story" button sends. */
export const PLAY_EVENT = "hotpotato:play";

export default function Experience({ series }: { series: Series }) {
  const last = series.dates.length - 1;
  const [lens, setLens] = useState<Lens>("dollars");
  const chapterIndex = useMemo(() => chapters.map((c) => nearestIndex(series.dates, c.date)), [series.dates]);
  const [target, setTarget] = useState(() => chapterIndex[0]);
  const [frame, setFrame] = useState(target);
  const [playing, setPlaying] = useState(false);
  const [hover, setHover] = useState<{ pile: number; x: number; y: number } | null>(null);
  const reducedMotion = useReducedMotion();

  const dollars = useMemo(() => buildTimeline(series.real, "dollars"), [series.real]);
  const shares = useMemo(() => (lens === "shares" ? buildTimeline(series.real, "shares") : null), [lens, series.real]);
  const timeline = lens === "shares" && shares ? shares : dollars;

  // Play: advance one quarter every 90 ms, from the start if the story has ended.
  useEffect(() => {
    if (!playing) return;
    const id = window.setInterval(() => {
      setTarget((t) => {
        if (t >= last) {
          setPlaying(false);
          return t;
        }
        return t + 1;
      });
    }, 90);
    return () => window.clearInterval(id);
  }, [playing, last]);

  const play = useCallback(() => {
    setTarget((t) => (t >= last ? 0 : t));
    setPlaying(true);
  }, [last]);

  // The hero's "Play the story" button.
  useEffect(() => {
    const onPlay = () => {
      setTarget(0);
      setPlaying(true);
    };
    window.addEventListener(PLAY_EVENT, onPlay);
    return () => window.removeEventListener(PLAY_EVENT, onPlay);
  }, []);

  // Arrow keys step through quarters when the stage is on screen and focus isn't in a form control.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      const stage = document.getElementById("stage");
      if (!stage) return;
      const r = stage.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      e.preventDefault();
      setPlaying(false);
      setTarget((t) => Math.max(0, Math.min(last, t + (e.key === "ArrowRight" ? 1 : -1))));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [last]);

  const labels = useCallback(
    (f: number): PileLabel[] => {
      const cells = series.real[f];
      const total = sumReal(cells);
      return PILE_NAMES.map((name, b) => {
        const v = cells[b][0] + cells[b][1];
        return {
          name,
          value: lens === "dollars" ? `${fmtTrillions(v)} · ${fmtPct(v / total)}` : fmtPct(v / total),
        };
      });
    },
    [series.real, lens],
  );

  const date = series.dates[frame];
  const total = sumReal(series.real[frame]);
  const share = series.publicShare[frame];
  const recession = series.recessions.find((r) => date >= r.start && date <= r.end) ?? null;
  const settled = frame === target;
  // The chapter on screen: the last one whose quarter the stage has reached.
  let active = 0;
  chapterIndex.forEach((q, i) => {
    if (frame >= q) active = i;
  });

  const fill = (body: string, q: number) => {
    const t = sumReal(series.real[q]);
    const s = series.publicShare[q];
    return body
      .replaceAll("{share}", fmtPct(s))
      .replaceAll("{total}", fmtTrillions(t))
      .replaceAll("{public}", fmtTrillions(t * s));
  };

  const tip = hover && (() => {
    const b = hover.pile;
    const cells = series.real[frame];
    const v = cells[b][0] + cells[b][1];
    const prevQ = Math.max(0, frame - 4);
    const prev = series.real[prevQ];
    const shareNow = v / total;
    const sharePrev = (prev[b][0] + prev[b][1]) / sumReal(prev);
    const delta = (shareNow - sharePrev) * 100;
    return (
      <div className="tip" style={{ left: `clamp(130px, ${hover.x}px, calc(100% - 130px))`, top: hover.y, borderTopColor: `var(--pile-${b})` }} role="status">
        <strong>{PILE_LONG[b]}</strong>
        <span>{fmtTrillions(v)} in 2026Q3 dollars · {lens === "dollars" ? Math.round(v / DOLLAR_UNIT_MUSD) : Math.round(shareNow * SHARE_DOTS)} potatoes</span>
        <span>{fmtPct(shareNow)} of all household debt</span>
        <span>
          {delta >= 0 ? "+" : "−"}
          {Math.abs(delta).toFixed(1)} pts vs a year earlier
        </span>
        <span className="tip__sub">Mortgages {fmtTrillions(cells[b][0])} · consumer {fmtTrillions(cells[b][1])}</span>
      </div>
    );
  })();

  const ticks = series.recessions.map((r) => ({
    ...r,
    left: (nearestIndex(series.dates, r.start) / last) * 100,
    width: Math.max(0.4, ((nearestIndex(series.dates, r.end) - nearestIndex(series.dates, r.start)) / last) * 100),
  }));

  // Public share over time, drawn as a filled sparkline behind the scrubber.
  const spark = useMemo(
    () => `M0 1 ${series.publicShare.map((v, i) => `L${i} ${(1 - (Number.isFinite(v) ? v : 0) / 0.7).toFixed(4)}`).join(" ")} L${last} 1 Z`,
    [series.publicShare, last],
  );

  return (
    <section id="explore" className="band band--explore" aria-label="Explorer">
      <div className="wrap">
        <div className="chapters" role="group" aria-label="Chapters">
          <button
            type="button"
            className="btn btn--play"
            onClick={() => (playing ? setPlaying(false) : play())}
            aria-label={playing ? "Pause" : "Play the story"}
          >
            <span aria-hidden>{playing ? "❚❚" : "▶"}</span> {playing ? "Pause" : "Play"}
          </button>
          {chapters.map((c, i) => (
            <button
              key={c.button}
              type="button"
              className="chip"
              aria-pressed={i === active}
              onClick={() => {
                setPlaying(false);
                setTarget(chapterIndex[i]);
              }}
            >
              {c.button}
            </button>
          ))}
        </div>

        <div id="stage" className="explorer" data-recession={recession ? "" : undefined}>
          <div className="readout">
            <div className="readout__when">
              <span className="readout__year">{fmtQuarter(date)}</span>
              <span className={`readout__badge${recession ? " is-on" : ""}`} aria-hidden={!recession}>
                {recession ? recession.name : " "}
              </span>
            </div>
            {/* All five captions are in the page (and its prerendered HTML, so every number keeps its register link);
                only the active chapter's is shown. */}
            <div className="readout__caption" aria-live="polite">
              {chapters.map((c, i) => (
                <div key={c.button} hidden={i !== active}>
                  <h3><Sourced text={c.title} /></h3>
                  <p><Sourced text={fill(c.caption, chapterIndex[i])} /></p>
                </div>
              ))}
            </div>
            <div className="split">
              <div className="split__labels">
                <span className="split__pub-label">
                  <b className="hi">{fmtPct(share)}</b> public
                </span>
                <span className="split__priv-label">
                  private <b>{fmtPct(1 - share)}</b>
                </span>
              </div>
              <div className="split__bar" aria-hidden>
                <span className="split__pub" style={{ width: `${share * 100}%` }} />
                <span className="split__priv" />
              </div>
            </div>
            <div className="readout__row">
              <div className="readout__total">
                <span className="readout__mid">{fmtTrillions(total)}</span>
                <span className="readout__label">total debt, 2026 $</span>
              </div>
              <div className="lens" role="group" aria-label="Lens">
                <button type="button" aria-pressed={lens === "dollars"} onClick={() => setLens("dollars")}>Dollars</button>
                <button type="button" aria-pressed={lens === "shares"} onClick={() => setLens("shares")}>Shares</button>
              </div>
            </div>
          </div>

          <div className="explorer__main">
            <div className="stage__plot">
              <DotStage
                timeline={timeline}
                target={target}
                reducedMotion={reducedMotion}
                labels={labels}
                onFrame={setFrame}
                onHover={setHover}
                ariaLabel={`Potato chart of US household debt by holder, ${fmtQuarter(date)}. ${fmtPct(share)} is held by the public sector.`}
              />
              {tip}
            </div>

            <div className="legend">
              <span><LegendPotato filled /> Mortgage</span>
              <span><LegendPotato filled={false} /> Consumer credit</span>
              <span><Sourced text={lens === "dollars" ? "1 potato = $50B (2026 $)" : "1 potato = 0.1% of all debt"} /></span>
            </div>

            <div className="scrub">
              <div className="scrub__track">
                <svg className="scrub__spark" viewBox={`0 0 ${last} 1`} preserveAspectRatio="none" aria-hidden>
                  <path d={spark} />
                </svg>
                {ticks.map((t) => (
                  <span key={t.id} className="scrub__band" style={{ left: `${t.left}%`, width: `${t.width}%` }} title={t.name} />
                ))}
                <input
                  type="range"
                  min={0}
                  max={last}
                  value={target}
                  aria-label="Quarter"
                  aria-valuetext={fmtQuarter(series.dates[target])}
                  onChange={(e) => {
                    setPlaying(false);
                    setTarget(Number(e.target.value));
                  }}
                />
              </div>
              <span className="scrub__ends" aria-hidden>
                {series.dates[0].slice(0, 4)}–{series.dates[last].slice(0, 4)}
              </span>
            </div>
          </div>

          <p className="sr-only" aria-live="polite">
            {settled ? `${fmtQuarter(date)}: ${fmtPct(share)} public, ${fmtTrillions(total)} in total.` : ""}
          </p>
        </div>
      </div>
    </section>
  );
}
