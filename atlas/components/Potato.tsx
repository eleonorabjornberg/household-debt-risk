// Hand-drawn hot-potato figures (Eleonora's idea, 2026-11-11: "little drawings of people holding amounts of hot
// potatoes" to make the site less dense). Plain SVG, solid fills and ink outlines, no gradients.
// Sizing rule (site review): a potato count is either derived from a published, registered value by the caller,
// or the figure is decorative (aria-hidden) and makes no quantitative claim.

type Tone = "public" | "private" | "neutral";
const BODY: Record<Tone, string> = { public: "var(--public)", private: "var(--private)", neutral: "var(--muted)" };
const POTATO = "#c98a3d";
const SPECK = "#7a4f1c";

/** One potato at (x, y), slightly rotated, with optional steam ("hot"). */
export function PotatoShape({ x, y, r = 9, rot = 0, hot = false }: { x: number; y: number; r?: number; rot?: number; hot?: boolean }) {
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot})`}>
      {hot && (
        <path d={`M${-r * 0.4} ${-r * 1.1} q-3 -5 0 -9 q3 -4 0 -8 M${r * 0.4} ${-r * 1.1} q-3 -5 0 -9`}
          fill="none" stroke="var(--accent)" strokeWidth={1.6} strokeLinecap="round" />
      )}
      <path d={`M${-r} 0 C${-r} ${-r * 0.8} ${-r * 0.2} ${-r * 0.75} ${r * 0.3} ${-r * 0.7} C${r * 1.1} ${-r * 0.65} ${r * 1.15} ${r * 0.1} ${r * 0.9} ${r * 0.45} C${r * 0.6} ${r * 0.85} ${-r * 0.7} ${r * 0.8} ${-r} 0 Z`}
        fill={POTATO} stroke="var(--ink)" strokeWidth={1.8} strokeLinejoin="round" />
      <circle cx={-r * 0.35} cy={-r * 0.15} r={1.1} fill={SPECK} />
      <circle cx={r * 0.3} cy={r * 0.2} r={1.1} fill={SPECK} />
      <circle cx={r * 0.45} cy={-r * 0.3} r={0.9} fill={SPECK} />
    </g>
  );
}

/** Positions for n potatoes stacked as a pile, bottom row widest, centred on x = 0, bottom at y = 0. */
function pile(n: number, r: number) {
  const out: { x: number; y: number; rot: number }[] = [];
  let row = 0;
  let left = n;
  let width = Math.max(1, Math.ceil(Math.sqrt(n * 2)));
  while (left > 0) {
    const k = Math.min(width, left);
    for (let i = 0; i < k; i++) {
      out.push({ x: (i - (k - 1) / 2) * r * 1.9, y: -row * r * 1.45, rot: ((i * 37 + row * 23) % 50) - 25 });
    }
    left -= k;
    row += 1;
    width = Math.max(1, width - 1);
  }
  return out;
}

/**
 * A person holding a pile of potatoes overhead-ish in both arms.
 * pose "hold": arms around a pile; "toss": one arm up, a potato flying off to the right; "sweat": holding, with sweat drops.
 */
export function PotatoPerson({
  potatoes, tone = "neutral", pose = "hold", label, width = 120, hot = true,
}: { potatoes: number; tone?: Tone; pose?: "hold" | "toss" | "sweat"; label?: string; width?: number; hot?: boolean }) {
  const r = 9;
  const spots = pile(Math.max(0, Math.round(potatoes)), r);
  const pileH = spots.length ? -Math.min(...spots.map((s) => s.y)) + r * 2 : 0;
  // Figure geometry: feet at y = 0, head above; pile held at chest height (y = -62), growing upward.
  const H = 120 + pileH;
  const vb = `-60 ${-H} 120 ${H + (label ? 22 : 6)}`;
  return (
    <svg viewBox={vb} width={width} role={label ? "img" : undefined} aria-hidden={label ? undefined : true}
      aria-label={label} className="potato-person" style={{ overflow: "visible" }}>
      {label && <title>{`${label} holders`}</title>}
      {label && <desc>{`${label} holders carry ${potatoes} of 10 potatoes: their share of household debt, to the nearest tenth.`}</desc>}
      {/* legs */}
      <path d="M-8 -34 L-14 -2 M8 -34 L14 -2" stroke="var(--ink)" strokeWidth={3} strokeLinecap="round" fill="none" />
      {/* body */}
      <path d="M-15 -36 Q-17 -64 -10 -70 L10 -70 Q17 -64 15 -36 Z" fill={BODY[tone]} stroke="var(--ink)" strokeWidth={2.2} strokeLinejoin="round" />
      {/* head */}
      <circle cx={0} cy={-84} r={12} fill="var(--paper)" stroke="var(--ink)" strokeWidth={2.2} />
      <circle cx={-4} cy={-86} r={1.4} fill="var(--ink)" />
      <circle cx={4} cy={-86} r={1.4} fill="var(--ink)" />
      <path d={pose === "toss" ? "M-4 -79 q4 3 8 0" : "M-4 -78 q4 -3 8 0"} stroke="var(--ink)" strokeWidth={1.6} fill="none" strokeLinecap="round" />
      {pose === "sweat" && (
        <path d="M16 -92 q3 5 0 7 q-3 -2 0 -7 Z M20 -80 q2.5 4 0 6 q-2.5 -2 0 -6 Z" fill="#8ec5ff" stroke="var(--ink)" strokeWidth={1} />
      )}
      {/* arms and pile */}
      {pose === "toss" ? (
        <>
          <path d="M-12 -64 Q-26 -80 -16 -102 M12 -64 Q30 -76 38 -98" stroke="var(--ink)" strokeWidth={3} strokeLinecap="round" fill="none" />
          <path d="M40 -104 Q60 -130 80 -112" stroke="var(--ink)" strokeWidth={1.4} strokeDasharray="3 4" fill="none" />
          <PotatoShape x={84} y={-104} r={r} rot={30} hot={hot} />
          <g transform={`translate(-16 ${-102 - r})`}>
            {spots.map((s, i) => <PotatoShape key={i} x={s.x * 0.6} y={s.y} r={r} rot={s.rot} hot={hot && i === spots.length - 1} />)}
          </g>
        </>
      ) : (
        <>
          <path d="M-13 -64 Q-30 -70 -22 -98 M13 -64 Q30 -70 22 -98" stroke="var(--ink)" strokeWidth={3} strokeLinecap="round" fill="none" />
          <g transform={`translate(0 ${-100 - r * 0.6})`}>
            {spots.map((s, i) => <PotatoShape key={i} x={s.x} y={s.y} r={r} rot={s.rot} hot={hot && i === spots.length - 1} />)}
          </g>
        </>
      )}
      {label && (
        <text x={0} y={16} textAnchor="middle" fontSize={12} fontWeight={700} fill="var(--ink)">{label}</text>
      )}
    </svg>
  );
}
