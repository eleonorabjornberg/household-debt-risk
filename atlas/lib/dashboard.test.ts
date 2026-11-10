import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { LOAN_TYPES, computeTiles, holderMix, loanPanel, move, shiftQuarter } from "./dashboard";

const DATA = path.join(__dirname, "..", "public", "data");
const read = (f: string) => JSON.parse(readFileSync(path.join(DATA, f), "utf8"));
const share = read("public_share.json");
const coverage = read("collateral_coverage.json");
const nyfed = read("nyfed_by_type.json");

describe("shiftQuarter", () => {
  it("steps quarter ends across years", () => {
    expect(shiftQuarter("2026-06-30", -1)).toBe("2026-03-31");
    expect(shiftQuarter("2026-03-31", -1)).toBe("2025-12-31");
    expect(shiftQuarter("2026-06-30", -4)).toBe("2025-06-30");
    expect(shiftQuarter("2025-12-31", 1)).toBe("2026-03-31");
  });
});

describe("move", () => {
  it("takes the latest value and its quarter and year changes", () => {
    const m = move([
      { date: "2025-06-30", v: 1 }, { date: "2026-03-31", v: 3 }, { date: "2026-06-30", v: 4 }, { date: "2026-09-30", v: null },
    ]);
    expect(m).toEqual({ date: "2026-06-30", value: 4, dq: 1, dy: 3 });
  });
  it("returns null changes when the earlier quarter is missing", () => {
    expect(move([{ date: "2026-06-30", v: 2 }])).toMatchObject({ dq: null, dy: null });
  });
});

// Each dashboard number must equal the value recorded in claims/register.csv.
const REGISTER = path.join(__dirname, "..", "..", "claims", "register.csv");
function registerValues(): Map<string, number> {
  const out = new Map<string, number>();
  for (const line of readFileSync(REGISTER, "utf8").split("\n")) {
    const m = /^(dash_[a-z_]+|scope_usd_2026q2|public_share_2026q2|home_coverage_2026q2),/.exec(line);
    if (!m) continue;
    // value is the 4th field; claims and displays here contain no quoted commas before it except the claim text
    const fields = line.match(/("([^"]|"")*"|[^,]*)(,|$)/g)!.map((f) => f.replace(/,$/, "").replace(/^"|"$/g, ""));
    out.set(m[1], Number(fields[3]));
  }
  return out;
}

describe("dashboard tiles match the claims register", () => {
  const t = computeTiles({ share, coverage, nyfed });
  const reg = registerValues();
  it("is dated 2026Q2", () => expect(t.scope.date).toBe("2026-06-30"));
  it("scope and public share", () => {
    expect(t.scope.dy! / 1e3).toBeCloseTo(reg.get("dash_scope_dy")!, 2);
    expect(t.publicShare.dq! * 100).toBeCloseTo(reg.get("dash_public_share_dq")!, 3);
    expect(t.publicShare.dy! * 100).toBeCloseTo(reg.get("dash_public_share_dy")!, 3);
  });
  it("home coverage", () => {
    expect(t.homeCoverage.dq!).toBeCloseTo(reg.get("dash_home_cov_dq")!, 3);
    expect(t.homeCoverage.dy!).toBeCloseTo(reg.get("dash_home_cov_dy")!, 3);
  });
  it.each(LOAN_TYPES)("serious-delinquency transitions: %s", (lt) => {
    const m = t.transitions[lt];
    expect(m.value).toBeCloseTo(reg.get(`dash_trans_${lt}`)!, 3);
    expect(m.dq!).toBeCloseTo(reg.get(`dash_trans_${lt}_dq`)!, 3);
    expect(m.dy!).toBeCloseTo(reg.get(`dash_trans_${lt}_dy`)!, 3);
  });
});

describe("panels", () => {
  it("holder mix splits into mortgage and consumer credit that sum within all", () => {
    const mix = holderMix(read("debt_by_risk_holder.json"), read("dim_risk_bucket.json"));
    const last = mix.dates.length - 1;
    const sum = (v: number[][]) => v.reduce((a, b) => a + b[last], 0);
    expect(sum(mix.values.mortgage) + sum(mix.values.consumer_credit)).toBeLessThanOrEqual(sum(mix.values.all) + 1e-6);
    expect(mix.buckets.some((b) => b.isPublic)).toBe(true);
  });
  it("loan panel has every type on a shared date axis", () => {
    const p = loanPanel(nyfed);
    for (const lt of LOAN_TYPES) expect(p.transition[lt]).toHaveLength(p.dates.length);
  });
});
