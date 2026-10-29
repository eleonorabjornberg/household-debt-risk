import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { apportion, buildTimeline, DOLLAR_UNIT_MUSD, SHARE_DOTS } from "./timeline";
import { computeLayout } from "./layout";
import { BUCKETS, DEBT_TYPES, type DebtByRiskHolderRow } from "./types";

function loadReal(): number[][][] {
  const rows: DebtByRiskHolderRow[] = JSON.parse(
    readFileSync(path.join(__dirname, "..", "..", "web", "public", "data", "debt_by_risk_holder.json"), "utf8"),
  );
  const dates = [...new Set(rows.map((r) => r.date))].sort();
  const q = new Map(dates.map((d, i) => [d, i]));
  const real = dates.map(() => BUCKETS.map(() => DEBT_TYPES.map(() => 0)));
  for (const r of rows) real[q.get(r.date)!][BUCKETS.indexOf(r.risk_bucket)][DEBT_TYPES.indexOf(r.debt_type)] += r.real_musd ?? 0;
  return real;
}

const real = loadReal();

describe("apportion", () => {
  it("hands out exactly the total", () => {
    expect(apportion([1, 1, 1], 10).reduce((a, b) => a + b)).toBe(10);
    expect(apportion([0.5, 0.25, 0.25], 4)).toEqual([2, 1, 1]);
    expect(apportion([0, 0], 5)).toEqual([0, 0]);
  });
});

describe("dollars lens", () => {
  const tl = buildTimeline(real, "dollars");
  it("each quarter's dots match its real total to within one dot", () => {
    real.forEach((cells, q) => {
      const total = cells.flat().reduce((a, b) => a + b, 0);
      const alive = tl.counts[q].reduce((a, b) => a + b, 0);
      expect(Math.abs(alive - total / DOLLAR_UNIT_MUSD)).toBeLessThanOrEqual(1);
    });
  });
  it("frames agree with counts and slots are dense", () => {
    tl.frames.forEach((f, q) => {
      BUCKETS.forEach((_, b) => {
        const ids = [...f.keys()].filter((id) => f[id] === b);
        expect(ids.length).toBe(tl.counts[q][b]);
        expect(ids.map((id) => tl.slots[q][id]).sort((x, y) => x - y)).toEqual(ids.map((_, k) => k));
      });
    });
  });
  it("moves the minimum number of dots between quarters", () => {
    for (let q = 1; q < tl.frames.length; q++) {
      const prev = tl.frames[q - 1];
      const cur = tl.frames[q];
      let moved = 0;
      for (let id = 0; id < tl.nDots; id++) if (prev[id] >= 0 && cur[id] >= 0 && prev[id] !== cur[id]) moved++;
      let minimum = 0;
      for (let t = 0; t < DEBT_TYPES.length; t++) {
        let surplus = 0;
        let deficit = 0;
        for (let b = 0; b < BUCKETS.length; b++) {
          const count = (f: Int8Array) => [...f.keys()].filter((id) => f[id] === b && tl.dotType[id] === t).length;
          const d = count(cur) - count(prev);
          if (d > 0) deficit += d;
          else surplus -= d;
        }
        minimum += Math.min(surplus, deficit);
      }
      expect(moved).toBe(minimum);
    }
  });
  it("the Great Recession moves dots from private securitization to the public side", () => {
    const q0 = (2007 - 1951) * 4; // the data starts in 1951Q4, so this is 2007Q4
    const q1 = q0 + 16; // 2011Q4
    const ps = BUCKETS.indexOf("private_securitization");
    expect(tl.counts[q1][ps]).toBeLessThan(tl.counts[q0][ps] * 0.5);
  });
});

describe("shares lens", () => {
  const tl = buildTimeline(real, "shares");
  it("always has exactly 1,000 dots", () => {
    tl.counts.forEach((c) => expect(c.reduce((a, b) => a + b, 0)).toBe(SHARE_DOTS));
  });
});

describe("layout", () => {
  const tl = buildTimeline(real, "dollars");
  for (const [w, h] of [[1280, 760], [375, 520], [358, 300], [350, 240]]) {
    it(`fits ${w}x${h} without overlapping piles`, () => {
      const l = computeLayout(w, h, tl.maxCounts);
      for (let i = 0; i < l.centers.length; i++) {
        const c = l.centers[i];
        expect(c.x - l.maxRadius[i]).toBeGreaterThanOrEqual(0);
        expect(c.x + l.maxRadius[i]).toBeLessThanOrEqual(w);
        expect(c.y - l.maxRadius[i]).toBeGreaterThanOrEqual(0);
        expect(l.labelY[i]).toBeLessThanOrEqual(h);
        for (let j = i + 1; j < l.centers.length; j++) {
          const d = Math.hypot(c.x - l.centers[j].x, c.y - l.centers[j].y);
          expect(d).toBeGreaterThan(l.maxRadius[i] + l.maxRadius[j]);
        }
      }
    });
  }
});
