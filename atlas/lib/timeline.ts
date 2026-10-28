// Turns quarterly holder totals into dots with stable identities.
//
// Each quarter, the 12 cells (6 holders x 2 debt types) are apportioned into whole dots by the
// largest-remainder method. Between quarters only the difference moves: within each debt type,
// holders with too many dots hand their newest dots to holders with too few, so the number of
// moving dots is the minimum possible. Any remaining surplus dies; any remaining deficit is born.
import { BUCKETS, DEBT_TYPES } from "./types";

export type Lens = "dollars" | "shares";

/** $50B in real (2026) dollars, expressed in $ millions. */
export const DOLLAR_UNIT_MUSD = 50_000;
export const SHARE_DOTS = 1000;

export interface Timeline {
  lens: Lens;
  nDots: number;
  /** debt type index per dot id */
  dotType: Uint8Array;
  /** per quarter: holder index per dot id, -1 when the dot doesn't exist that quarter */
  frames: Int8Array[];
  /** per quarter: slot (0 = pile centre) of each dot within its holder's pile */
  slots: Int16Array[];
  /** per quarter: dots per holder */
  counts: number[][];
  /** max dots any holder ever has (sizes the piles) */
  maxCounts: number[];
}

/** Largest-remainder apportionment of `total` whole units in proportion to `values`. */
export function apportion(values: number[], total: number): number[] {
  const sum = values.reduce((a, b) => a + b, 0);
  if (sum <= 0 || total <= 0) return values.map(() => 0);
  const quotas = values.map((v) => (v / sum) * total);
  const out = quotas.map(Math.floor);
  let left = total - out.reduce((a, b) => a + b, 0);
  const order = quotas.map((q, i) => [q - Math.floor(q), i] as const).sort((a, b) => b[0] - a[0] || a[1] - b[1]);
  for (let k = 0; left > 0; k++, left--) out[order[k % order.length][1]] += 1;
  return out;
}

/** Target dots per [holder][type] for one quarter. */
export function targetCounts(cells: number[][], lens: Lens): number[][] {
  const flat = cells.flat();
  const sum = flat.reduce((a, b) => a + b, 0);
  const total = lens === "shares" ? SHARE_DOTS : Math.round(sum / DOLLAR_UNIT_MUSD);
  const a = apportion(flat, total);
  return cells.map((row, b) => row.map((_, t) => a[b * row.length + t]));
}

export function buildTimeline(real: number[][][], lens: Lens): Timeline {
  const nB = BUCKETS.length;
  const nT = DEBT_TYPES.length;
  // members[b] = dot ids in arrival order (oldest first); arrival order sets the slot.
  const members: number[][] = Array.from({ length: nB }, () => []);
  const types: number[] = [];
  const snapshots: { members: number[][] }[] = [];

  for (const cells of real) {
    const target = targetCounts(cells, lens);
    for (let t = 0; t < nT; t++) {
      const free: number[] = [];
      for (let b = 0; b < nB; b++) {
        let have = members[b].filter((id) => types[id] === t).length;
        // Surplus: release this type's newest dots.
        for (let i = members[b].length - 1; i >= 0 && have > target[b][t]; i--) {
          if (types[members[b][i]] === t) {
            free.push(members[b][i]);
            members[b].splice(i, 1);
            have--;
          }
        }
      }
      for (let b = 0; b < nB; b++) {
        let have = members[b].filter((id) => types[id] === t).length;
        while (have < target[b][t]) {
          let id = free.shift();
          if (id === undefined) {
            id = types.length;
            types.push(t);
          }
          members[b].push(id);
          have++;
        }
      }
      // Anything still in `free` dies this quarter.
    }
    snapshots.push({ members: members.map((m) => m.slice()) });
  }

  const nDots = types.length;
  const frames: Int8Array[] = [];
  const slots: Int16Array[] = [];
  const counts: number[][] = [];
  const maxCounts = new Array(nB).fill(0);
  for (const s of snapshots) {
    const f = new Int8Array(nDots).fill(-1);
    const sl = new Int16Array(nDots).fill(-1);
    s.members.forEach((ids, b) => {
      ids.forEach((id, k) => {
        f[id] = b;
        sl[id] = k;
      });
      maxCounts[b] = Math.max(maxCounts[b], ids.length);
    });
    frames.push(f);
    slots.push(sl);
    counts.push(s.members.map((m) => m.length));
  }
  return { lens, nDots, dotType: Uint8Array.from(types), frames, slots, counts, maxCounts };
}
