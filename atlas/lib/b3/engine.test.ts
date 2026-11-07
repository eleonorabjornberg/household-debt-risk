// The engine the page runs reproduces the Python core on every fixed case (research/b3_scenarios/fixtures/cases.json)
// and on both presets (results_*.json written by the Python core).
import { describe, expect, it } from "vitest";
import { run, type Classes, type Exposure, type Transfer } from "./engine.mjs";
import cases from "./cases.json";
import exposures from "./exposures.json";
import dfast from "./preset_dfast2026.json";
import replay from "./preset_replay_2008_2012.json";
import rDfast from "./results_dfast2026.json";
import rReplay from "./results_replay_2008_2012.json";

const close = (a: number, b: number) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
const ex = exposures.exposures as Exposure[];

describe("fixed cases", () => {
  for (const c of cases as unknown as { name: string; exposures: Exposure[]; classes: Classes; transfer: Transfer | null;
                                         expected: Record<string, number[]> & { sum: Record<string, number> } }[]) {
    it(c.name, () => {
      const got = run(c.exposures, c.classes, c.transfer);
      for (const k of ["public", "private", "total", "transferred"] as const) {
        expect(got[k].length).toBe(c.expected[k].length);
        got[k].forEach((v, i) => expect(close(v, c.expected[k][i])).toBe(true));
        expect(close(got.sum[k], c.expected.sum[k])).toBe(true);
      }
      got.total.forEach((t, i) => expect(close(t, got.public[i] + got.private[i])).toBe(true));
    });
  }
  it("refuses invalid input", () => {
    expect(() => run(ex, { mortgage: { pd: 1.2, lgd: 0.3 } })).toThrow();
    expect(() => run(ex, { mortgage: { pd: 0.1, lgd: 0.3, timing: [0.5, 0.4] } })).toThrow();
  });
});

describe("presets", () => {
  const presets = { ...dfast.presets, ...replay.presets } as Record<string, { classes: Classes }>;
  const expected = { ...rDfast, ...rReplay } as unknown as Record<string, { public_musd: number; private_musd: number; total_musd: number }>;
  for (const name of Object.keys(presets)) {
    it(name, () => {
      const got = run(ex, presets[name].classes);
      expect(close(got.sum.public, expected[name].public_musd)).toBe(true);
      expect(close(got.sum.private, expected[name].private_musd)).toBe(true);
      expect(close(got.sum.total, expected[name].total_musd)).toBe(true);
    });
  }
});
