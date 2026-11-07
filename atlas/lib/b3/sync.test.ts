// The copies in lib/b3/ must match research/b3_scenarios/ byte for byte (PLAN B3: the browser runs the checked engine).
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import manifest from "./manifest.json";

const here = join(__dirname);
const research = join(here, "..", "..", "..", "research", "b3_scenarios");
const sha = (p: string) => createHash("sha256").update(readFileSync(p)).digest("hex");

describe("lib/b3 copies", () => {
  for (const [file, m] of Object.entries(manifest as Record<string, { source: string; sha256: string }>)) {
    it(`${file} matches its manifest hash`, () => expect(sha(join(here, file))).toBe(m.sha256));
    it.skipIf(!existsSync(research))(`${file} matches ${m.source}`, () => {
      expect(sha(join(here, file))).toBe(sha(join(here, "..", "..", "..", m.source)));
    });
  }
});
