// Where the six piles sit on the canvas. Each pile is a sunflower (phyllotaxis) disc whose area
// grows with its dot count; the layout reserves room for the largest the pile ever gets.
export const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

export interface Layout {
  centers: { x: number; y: number }[];
  /** phyllotaxis spacing: slot k sits at radius spacing * sqrt(k + 0.5) */
  spacing: number;
  dotRadius: number;
  /** reserved radius per pile (at its largest) */
  maxRadius: number[];
  /** y of each pile's label baseline */
  labelY: number[];
  /** public/private divider: vertical (x) in one row, horizontal (y) in two rows */
  dividerX: number | null;
  dividerY: number | null;
  rows: 1 | 2;
  /** label font size */
  fontSize: number;
}

const LABEL_SPACE = 44;

/** Solve spacing so a row of piles (widths 2*s*sqrt(max), with a floor) fills `avail` px. */
function solveRow(maxes: number[], avail: number, minPile: number): number {
  let fixed = new Set<number>();
  let s = 0;
  for (let pass = 0; pass < 4; pass++) {
    const free = maxes.map((m, i) => (fixed.has(i) ? 0 : 2 * Math.sqrt(Math.max(m, 1))));
    const room = avail - fixed.size * minPile;
    s = room / Math.max(1e-6, free.reduce((a, b) => a + b, 0));
    const next = new Set(maxes.map((m, i) => [2 * s * Math.sqrt(Math.max(m, 1)), i] as const).filter(([w]) => w < minPile).map(([, i]) => i));
    if (next.size === fixed.size && [...next].every((i) => fixed.has(i))) break;
    fixed = next;
  }
  return s;
}

function placeRow(maxes: number[], s: number, gaps: number[], cy: number, minPile: number) {
  const out: { x: number; y: number; r: number }[] = [];
  let x = 0;
  maxes.forEach((m, i) => {
    const r = s * Math.sqrt(Math.max(m, 1));
    const w = Math.max(2 * r, minPile);
    out.push({ x: x + w / 2, y: cy, r });
    x += w + (i < maxes.length - 1 ? gaps[i] : 0);
  });
  return { piles: out, width: x };
}

/** `publicCount` = how many piles (in order) are public. */
export function computeLayout(width: number, height: number, maxCounts: number[], publicCount = 3): Layout {
  const pad = Math.max(12, Math.min(32, width * 0.03));
  const narrow = width < 500;
  const gap = narrow ? 8 : 22;
  const divider = 64;
  const minPile = narrow ? 76 : 92;
  const fontSize = narrow ? 11 : 12;
  const pub = maxCounts.slice(0, publicCount);
  const priv = maxCounts.slice(publicCount);
  const sq = (xs: number[]) => Math.sqrt(Math.max(...xs, 1));

  // Option A: one row, public | private.
  const availA = width - 2 * pad - (maxCounts.length - 2) * gap - divider;
  const sA = Math.max(0, Math.min(solveRow(maxCounts, availA, minPile), (height - 2 * pad - LABEL_SPACE) / (2 * sq(maxCounts))));
  // Option B: public row on top, private row below.
  const availB = (n: number) => width - 2 * pad - (n - 1) * gap;
  const midGap = 28;
  const sB = Math.max(0, Math.min(
    solveRow(pub, availB(pub.length), minPile),
    solveRow(priv, availB(priv.length), minPile),
    (height - 2 * pad - 2 * LABEL_SPACE - midGap) / (2 * (sq(pub) + sq(priv))),
  ));
  const rows: 1 | 2 = sB > sA * 1.15 || width < 720 ? 2 : 1;

  let piles: { x: number; y: number; r: number }[];
  let s: number;
  let dividerX: number | null = null;
  let dividerY: number | null = null;
  let labelY: number[];
  if (rows === 1) {
    s = sA;
    const gaps = maxCounts.map((_, i) => (i === publicCount - 1 ? divider : gap));
    const row = placeRow(maxCounts, s, gaps, 0, minPile);
    const offset = (width - row.width) / 2;
    const cy = pad + (height - 2 * pad - LABEL_SPACE) / 2;
    piles = row.piles.map((p) => ({ ...p, x: p.x + offset, y: cy }));
    const lastPub = piles[publicCount - 1];
    dividerX = lastPub.x + Math.max(lastPub.r, minPile / 2) + divider / 2;
    const tallest = Math.max(...piles.map((p) => p.r));
    labelY = piles.map((p) => p.y + tallest + 18);
  } else {
    s = sB;
    const rPub = s * sq(pub);
    const rPriv = s * sq(priv);
    const used = 2 * rPub + LABEL_SPACE + midGap + 2 * rPriv + LABEL_SPACE;
    const top = pad + Math.max(0, (height - 2 * pad - used) / 2);
    const yPub = top + rPub;
    const yPriv = top + 2 * rPub + LABEL_SPACE + midGap + rPriv;
    const rowOf = (maxes: number[], cy: number) => {
      const r = placeRow(maxes, s, maxes.map(() => gap), cy, minPile);
      const offset = (width - r.width) / 2;
      return r.piles.map((p) => ({ ...p, x: p.x + offset }));
    };
    piles = [...rowOf(pub, yPub), ...rowOf(priv, yPriv)];
    dividerY = top + 2 * rPub + LABEL_SPACE + midGap / 2;
    labelY = piles.map((p, i) => p.y + (i < publicCount ? rPub : rPriv) + 18);
  }

  return {
    centers: piles.map(({ x, y }) => ({ x, y })),
    spacing: s,
    dotRadius: Math.max(0.8, s * 0.78),
    maxRadius: piles.map((p) => p.r),
    labelY,
    dividerX,
    dividerY,
    rows,
    fontSize,
  };
}

/** Position of slot k in a pile centred on (cx, cy). */
export function slotPosition(cx: number, cy: number, k: number, spacing: number): [number, number] {
  const r = spacing * Math.sqrt(k + 0.5);
  const a = k * GOLDEN_ANGLE;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}
