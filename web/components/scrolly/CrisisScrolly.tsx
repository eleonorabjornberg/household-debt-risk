"use client";
// "Crisis by crisis" scroll-through: a sticky Ratchet chart beside one step card per crisis.
//
// When a step crosses the trigger line the chart zooms to t0 − 2y … t0 + 4y and the crisis band is
// emphasised. With Tableau configured (and a wide screen) the sticky chart is the published
// Ratchet dashboard, driven through lib/tableauControl.ts; otherwise, or if Tableau fails, it is
// the native RatchetChart with the same zoom, highlight, legend and side card.
import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import type { Crisis, CrisisStep, RatchetData } from "@/lib/shape";
import type { RiskBucket } from "@/lib/types";
import { pct, pts, quarterLabel, quarterToYear } from "@/lib/format";
import { CRISIS_FOCUS_EVENT, crisisStepId } from "@/lib/crisisFocus";
import {
  createRatchetController,
  loadEmbeddingApi,
  logOnce,
  whenInteractive,
  type HolderSelection,
  type RatchetController,
} from "@/lib/tableauControl";
import { RatchetChart } from "@/components/charts/RatchetChart";

export interface ScrollyCopy {
  intro: string;
  legendLabel: string;
  legendHint: string;
  reset: string;
  caption: string;
  cardSince: string;
  cardBegan: string;
  cardClose: string;
  nativeNote: string;
  stepCta: string;
}

interface Props {
  steps: CrisisStep[];
  data: RatchetData;
  crises: Crisis[];
  /** Tableau embed for the Ratchet view, or null for the native chart only. */
  embed: { scriptUrl: string; src: string; needsToken: boolean } | null;
  title: string;
  copy: ScrollyCopy;
  holderNotes: Record<string, string>;
}

const WIDE = "(min-width: 769px)";
const REDUCED = "(prefers-reduced-motion: reduce)";
// Embed height. The dashboard uses automatic sizing, so it fills the column width at this height.
const VIZ_H = 640;

function useMediaQuery(query: string, serverValue: boolean) {
  return useSyncExternalStore(
    (cb) => {
      const m = window.matchMedia(query);
      m.addEventListener("change", cb);
      return () => m.removeEventListener("change", cb);
    },
    () => window.matchMedia(query).matches,
    () => serverValue,
  );
}

/** Index of `iso` in sorted `dates`, or of the nearest earlier date. */
function indexAtOrBefore(dates: string[], iso: string): number {
  let best = -1;
  for (let i = 0; i < dates.length && dates[i] <= iso; i++) best = i;
  return best;
}

type Load = "off" | "loading" | "mounted" | "failed";

export function CrisisScrolly({ steps, data, crises, embed, title, copy, holderNotes }: Props) {
  const isWide = useMediaQuery(WIDE, true);
  const reduced = useMediaQuery(REDUCED, false);

  const [active, setActive] = useState<string | null>(null);
  const [focusBucket, setFocusBucket] = useState<RiskBucket | null>(null);
  const [tabSel, setTabSel] = useState<HolderSelection | null>(null);
  const [load, setLoad] = useState<Load>("off");
  const [token, setToken] = useState<string | undefined>();
  const [ready, setReady] = useState(false);

  const rootRef = useRef<HTMLDivElement>(null);
  const vizRef = useRef<HTMLElement | null>(null);
  const ctlRef = useRef<RatchetController | null>(null);
  const activeRef = useRef<string | null>(null);
  const immediateRef = useRef(false);
  const lockUntil = useRef(0);
  const startedRef = useRef(false);

  const stepById = useMemo(() => new Map(steps.map((s) => [s.id, s])), [steps]);
  const activeStep = active ? stepById.get(active) ?? null : null;
  const tableauOn = ready && load === "mounted";

  // ---- data derived from the site's own tables (never from Tableau)
  const holder = useMemo(() => {
    const n = data.dates.length;
    const totals = new Array<number>(n).fill(0);
    const sums = data.buckets.map((b) =>
      data.dates.map((_, i) => (data.nominal.mortgage[b.key][i] ?? 0) + (data.nominal.consumer_credit[b.key][i] ?? 0)),
    );
    sums.forEach((row) => row.forEach((v, i) => (totals[i] += v)));
    const share = Object.fromEntries(
      data.buckets.map((b, k) => [b.key, sums[k].map((v, i) => (totals[i] ? v / totals[i] : 0))]),
    ) as Record<RiskBucket, number[]>;
    const publicShare = data.dates.map((_, i) =>
      data.buckets.filter((b) => b.isPublic).reduce((s, b) => s + share[b.key][i], 0),
    );
    return { share, publicShare };
  }, [data]);
  const keyByLabel = useMemo(() => new Map(data.buckets.map((b) => [b.label, b.key])), [data.buckets]);
  const latest = data.dates[data.dates.length - 1];

  // ---- mark the active step (ref mirror for observers)
  useEffect(() => {
    activeRef.current = active;
  }, [active]);

  // ---- lazy-load Tableau when the section comes near, on wide screens only
  const startTableau = useCallback(async () => {
    if (!embed || startedRef.current) return;
    startedRef.current = true;
    setLoad("loading");
    try {
      if (embed.needsToken) {
        const [res] = await Promise.all([fetch("/api/tableau-token", { cache: "no-store" }), loadEmbeddingApi(embed.scriptUrl)]);
        if (!res.ok) throw new Error(`Token request failed (${res.status})`);
        setToken(((await res.json()) as { token: string }).token);
      } else {
        await loadEmbeddingApi(embed.scriptUrl);
      }
      setLoad("mounted");
    } catch (err) {
      logOnce("Embedding API load (scroll-through)", err);
      setLoad("failed");
    }
  }, [embed]);

  useEffect(() => {
    const el = rootRef.current;
    if (!embed || !el) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting) && window.matchMedia(WIDE).matches) {
          io.disconnect();
          void startTableau();
        }
      },
      { rootMargin: "1200px 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [embed, startTableau]);

  // ---- once <tableau-viz> is in the DOM: wait for firstinteractive, then build the controller
  const mounted = load === "mounted";
  useEffect(() => {
    const el = vizRef.current;
    if (!mounted || !el) return;
    let cancelled = false;
    whenInteractive(el)
      .then((viz) => createRatchetController(viz))
      .then((ctl) => {
        if (cancelled) return ctl.dispose();
        ctlRef.current = ctl;
        setReady(true);
      })
      .catch((err) => {
        if (cancelled) return;
        logOnce("Ratchet embed (scroll-through)", err);
        setLoad("failed");
      });
    return () => {
      cancelled = true;
      ctlRef.current?.dispose();
      ctlRef.current = null;
    };
  }, [mounted]);

  // ---- drive Tableau from the active step (debounced + serialised inside the controller)
  useEffect(() => {
    const ctl = ctlRef.current;
    if (!tableauOn || !ctl) return;
    const s = active ? stepById.get(active) : null;
    ctl.focusCrisis(s ? { id: s.id, min: s.min, max: s.max } : null, { immediate: immediateRef.current });
    immediateRef.current = false;
  }, [active, tableauOn, stepById]);

  // ---- Tableau → site: selected marks drive the side card
  useEffect(() => {
    const ctl = ctlRef.current;
    if (!tableauOn || !ctl) return;
    return ctl.onSelection((sel) => {
      setTabSel(sel);
      setFocusBucket(sel ? keyByLabel.get(sel.label) ?? null : null);
    });
  }, [tableauOn, keyByLabel]);

  // ---- scroll trigger: a 1px line at 50% of the viewport (72% on phones, under the sticky chart)
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const els = [...root.querySelectorAll<HTMLElement>("[data-step]")];
    let io: IntersectionObserver | null = null;
    const build = () => {
      io?.disconnect();
      const h = window.innerHeight;
      const top = Math.round(h * (isWide ? 0.5 : 0.72));
      io = new IntersectionObserver(
        (entries) => {
          if (performance.now() < lockUntil.current) return;
          for (const e of entries) {
            const el = e.target as HTMLElement;
            const id = el.dataset.step!;
            const idx = Number(el.dataset.index);
            if (e.isIntersecting) {
              setActive(id);
            } else if (activeRef.current === id) {
              const lineY = e.rootBounds ? e.rootBounds.top : top;
              const below = e.boundingClientRect.top > lineY;
              // Scrolled back above the first step, or past the last: leave the chapter state.
              if ((idx === 0 && below) || (idx === els.length - 1 && !below)) setActive(null);
            }
          }
        },
        { rootMargin: `-${top}px 0px -${Math.max(0, h - top - 1)}px 0px`, threshold: 0 },
      );
      els.forEach((el) => io!.observe(el));
    };
    build();
    // The whole section out of view also resets.
    const outer = new IntersectionObserver((entries) => {
      if (entries.every((e) => !e.isIntersecting)) setActive(null);
    });
    outer.observe(root);
    let t: ReturnType<typeof setTimeout> | undefined;
    const onResize = () => {
      clearTimeout(t);
      t = setTimeout(build, 200);
    };
    window.addEventListener("resize", onResize);
    return () => {
      clearTimeout(t);
      window.removeEventListener("resize", onResize);
      io?.disconnect();
      outer.disconnect();
    };
  }, [isWide]);

  // ---- Figure 2 panels (and anything else) can ask for a crisis
  const goTo = useCallback(
    (id: string, scroll: boolean) => {
      const el = document.getElementById(crisisStepId(id));
      if (!el || !stepById.has(id)) return false;
      lockUntil.current = performance.now() + (scroll ? (reduced ? 200 : 1400) : 400);
      immediateRef.current = true;
      setActive(id);
      if (scroll) {
        el.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
        el.focus({ preventScroll: true });
      }
      return true;
    },
    [reduced, stepById],
  );
  useEffect(() => {
    const onFocus = (ev: Event) => {
      const id = (ev as CustomEvent<{ id: string }>).detail?.id;
      if (id && goTo(id, true)) ev.preventDefault();
    };
    window.addEventListener(CRISIS_FOCUS_EVENT, onFocus);
    return () => window.removeEventListener(CRISIS_FOCUS_EVENT, onFocus);
  }, [goTo]);

  const reset = () => {
    lockUntil.current = performance.now() + 400;
    immediateRef.current = true;
    setActive(null);
  };

  // ---- site → Tableau: legend
  const onHolder = (key: RiskBucket) => {
    const next = focusBucket === key ? null : key;
    setFocusBucket(next);
    const ctl = ctlRef.current;
    if (tableauOn && ctl) void ctl.selectHolder(next ? data.buckets.find((b) => b.key === next)!.label : null);
  };
  const clearHolder = () => {
    setFocusBucket(null);
    setTabSel(null);
    const ctl = ctlRef.current;
    if (tableauOn && ctl) void ctl.selectHolder(null);
  };

  // ---- side card (values from the site's data)
  const windowEnd = activeStep ? (activeStep.max < latest ? activeStep.max : latest) : latest;
  const card = (() => {
    let key: RiskBucket | null = null;
    let date = windowEnd;
    if (tableauOn) {
      if (!tabSel) return null;
      key = keyByLabel.get(tabSel.label) ?? null;
      if (tabSel.dates.length) date = tabSel.dates[tabSel.dates.length - 1];
    } else key = focusBucket;
    if (!key) return null;
    const i = indexAtOrBefore(data.dates, date);
    if (i < 0) return null;
    const d = data.dates[i];
    const share = holder.share[key][i];
    const prev = [...crises].filter((c) => c.start < d).pop() ?? null;
    const j = prev ? indexAtOrBefore(data.dates, prev.start) : -1;
    const delta = j >= 0 ? share - holder.share[key][j] : null;
    const meta = data.buckets.find((b) => b.key === key)!;
    return { key, label: meta.label, isPublic: meta.isPublic, date: d, share, prev, delta, note: holderNotes[key] ?? "" };
  })();

  // ---- caption
  const caption = (() => {
    if (activeStep) {
      const delta = activeStep.shareStart !== null && activeStep.shareEnd !== null ? activeStep.shareEnd - activeStep.shareStart : null;
      return {
        name: activeStep.name,
        detail: `${copy.caption} ${pct(activeStep.shareStart, 1)} → ${pct(activeStep.shareEnd, 1)} (${pts(delta)}), ${quarterLabel(activeStep.start)}–${activeStep.endDate ? quarterLabel(activeStep.endDate) : "–"}`,
      };
    }
    const n = data.dates.length - 1;
    return {
      name: `${data.dates[0].slice(0, 4)}–${latest.slice(0, 4)}`,
      detail: `${copy.caption} ${pct(holder.publicShare[0], 1)} → ${pct(holder.publicShare[n], 1)}`,
    };
  })();

  const xDomain: [number, number] | undefined = activeStep
    ? [quarterToYear(activeStep.start) - 2, quarterToYear(activeStep.start) + 4]
    : undefined;
  const showNative = !tableauOn;
  const nPublic = data.buckets.filter((b) => b.isPublic).length;

  return (
    <div className={`scrolly${tableauOn ? " scrolly--tableau" : ""}`} ref={rootRef}>
      <div className="scrolly__panel">
        <div className="scrolly__viz">
          <div className={`scrolly__caption${tableauOn ? " is-overlay" : ""}`} aria-live="polite" aria-atomic="true">
            <strong>{caption.name}</strong> <span>{caption.detail}</span>
            {activeStep && (
              <button type="button" className="scrolly__reset" onClick={reset}>
                {copy.reset}
              </button>
            )}
          </div>
          {mounted && (
            <div
              className={`scrolly__tableau${tableauOn ? "" : " is-loading"}`}
              style={{ height: VIZ_H }}
              aria-hidden={tableauOn ? undefined : true}
            >
              <tableau-viz
                ref={vizRef}
                src={embed!.src}
                {...(token ? { token } : {})}
                toolbar="hidden"
                hide-tabs
                width="100%"
                height={`${VIZ_H}px`}
                aria-label={`${title} (interactive Tableau view)`}
                style={{ display: "block" }}
              />
            </div>
          )}
          {showNative && (
            <RatchetChart
              data={data}
              crises={crises}
              title={title}
              xDomain={xDomain}
              activeCrisis={active}
              focusBucket={focusBucket}
              chrome={false}
            />
          )}
          {embed && !isWide && <p className="figure__soon">{copy.nativeNote}</p>}
          {load === "failed" && (
            <p className="figure__soon">The interactive Tableau version could not load, so the built-in chart is shown instead.</p>
          )}
        </div>

        <div className="holderlegend" role="group" aria-label={copy.legendLabel}>
          {[data.buckets.slice(0, nPublic), data.buckets.slice(nPublic)].map((group, g) => (
            <div key={g} className="holderlegend__group">
              <span className="legend__group">{g === 0 ? "Public" : "Private"}</span>
              {group.map((b) => (
                <button
                  key={b.key}
                  type="button"
                  className="holderlegend__btn"
                  aria-pressed={focusBucket === b.key}
                  data-bucket={b.key}
                  onClick={() => onHolder(b.key)}
                >
                  <span className="legend__swatch" style={{ background: `var(--b-${b.key})` }} aria-hidden="true" />
                  {b.label}
                </button>
              ))}
            </div>
          ))}
          <p className="holderlegend__hint">{copy.legendHint}</p>
        </div>

        <div className="scrolly__cardslot" aria-live="polite">
          {card && (
            <section className="holdercard" aria-label={`${card.label}: details`} data-testid="holder-card">
              <div className="holdercard__head">
                <span className="legend__swatch" style={{ background: `var(--b-${card.key})` }} aria-hidden="true" />
                <h4 className="holdercard__title">{card.label}</h4>
                <button type="button" className="holdercard__close" onClick={clearHolder} aria-label={`${copy.cardClose}: ${card.label}`}>
                  {copy.cardClose}
                </button>
              </div>
              <p className="holdercard__value">
                <strong>{pct(card.share, 1)}</strong> of household debt in {quarterLabel(card.date)}
                {card.isPublic ? " (public)" : " (private)"}
              </p>
              {card.prev && (
                <p className="holdercard__delta">
                  <strong>{pts(card.delta)}</strong> {copy.cardSince} the {card.prev.name} {copy.cardBegan} ({quarterLabel(card.prev.start)})
                </p>
              )}
              <p className="holdercard__note">{card.note}</p>
            </section>
          )}
        </div>
      </div>

      <ol className="scrolly__steps" aria-label="Crises, one step each">
        {steps.map((s, i) => {
          const delta = s.shareStart !== null && s.shareEnd !== null ? s.shareEnd - s.shareStart : null;
          const on = active === s.id;
          return (
            <li
              key={s.id}
              id={crisisStepId(s.id)}
              data-step={s.id}
              data-index={i}
              tabIndex={-1}
              className={`scrolly__step${on ? " is-active" : ""}`}
              aria-current={on ? "step" : undefined}
            >
              <p className="scrolly__kicker">
                {s.label} · {s.kind === "policy_shock" ? "Policy shock" : "NBER recession"}
              </p>
              <h3 className="scrolly__name">{s.name}</h3>
              <p className="scrolly__move">
                Public share <strong>{pts(delta)}</strong>: {pct(s.shareStart, 1)} in {quarterLabel(s.start)}
                {s.endDate ? ` → ${pct(s.shareEnd, 1)} in ${quarterLabel(s.endDate)}` : ""}
              </p>
              {s.note && <p className="scrolly__note">{s.note}</p>}
              <button type="button" className="scrolly__show" aria-pressed={on} onClick={() => goTo(s.id, false)}>
                {copy.stepCta}
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
