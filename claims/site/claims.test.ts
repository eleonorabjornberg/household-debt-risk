// GENERATED COPY: edit claims/site/claims.test.ts in the repo root, not the copy in a site.
// Unit tests for the F1 matcher (claims-core.ts) and the committed lib/claims.json.
import { describe, expect, it } from "vitest";
import data from "./claims.json";
import { makeMatcher, type Claim, type ClaimsFile } from "./claims-core";

const claim = (id: string, display: string[], anchors: string[], exact: string[] = []): Claim => ({
  id, claim: "", display, value: "", unit: "", period: "", locations: [], computation: "", series: [],
  vintage: "", validation: "UNVERIFIED", checkId: "", notes: "", register: "", anchors, exact,
});

const m = makeMatcher([
  claim("seven", ["7%"], ["up from this in 2007"]),
  claim("gfc", ["+13.1 points", "13.1 points", "13 points"], ["The public share rose"]),
  claim("p", ["p ≈ 0.30", "0.30"], [], ["p ≈ 0.30"]),
]);
const ids = (text: string, ctx?: string) =>
  m.segment(text, ctx).flatMap((s) => (typeof s === "string" ? [] : [`${s.id}:${s.text}`]));

describe("claims-core", () => {
  it("links a number only where an anchor from its cited line appears", () => {
    expect(ids("51% now, up from this in 2007: 7%")).toEqual(["seven:7%"]);
    expect(ids("Somewhere else, 7% means something else")).toEqual([]);
  });
  it("respects digit boundaries", () => {
    expect(ids("up from this in 2007: 17% and 7.5% and 7%")).toEqual(["seven:7%"]);
  });
  it("prefers the longest spelling and never overlaps", () => {
    expect(ids("The public share rose 13.1 points, not 13 points.")).toEqual(["gfc:13.1 points", "gfc:13 points"]);
  });
  it("links a short stat literal rendered on its own", () => {
    expect(ids("p ≈ 0.30")).toEqual(["p:p ≈ 0.30"]);
    expect(ids("costs 0.30 dollars")).toEqual([]);
  });
  it("uses context (a label) for eligibility but links only inside the text", () => {
    expect(ids("+13.1 points", "The public share rose")).toEqual(["gfc:+13.1 points"]);
  });
  it("returns the text unchanged when nothing matches", () => {
    expect(m.segment("nothing here")).toEqual(["nothing here"]);
  });
});

describe("lib/claims.json", () => {
  const file = data as ClaimsFile;
  it("has unique ids, display spellings and a validation status", () => {
    expect(new Set(file.claims.map((c) => c.id)).size).toBe(file.claims.length);
    for (const c of file.claims) {
      expect(c.display.length, c.id).toBeGreaterThan(0);
      expect(["PASS", "FAIL", "UNVERIFIED", "ESTIMATE", "STALE", "DEFINITION"], c.id).toContain(c.validation);
      expect(c.locations.every((l) => l.startsWith(`${file.site}/`)), c.id).toBe(true);
    }
  });
  it("has no display spelling shared by two claims on this site", () => {
    const seen = new Map<string, string>();
    for (const c of file.claims)
      for (const d of c.display) {
        expect(seen.get(d) ?? c.id, `"${d}" in ${c.id} and ${seen.get(d)}`).toBe(c.id);
        seen.set(d, c.id);
      }
  });
});
