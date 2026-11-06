// E4 red-team runner for Ask Hot Potato (PLAN E4; plan tracks/infra-e4-plan.md, checked by the coordinator against
// the $20 D6 cap). The same harness and safeguards as the D6 build test (scripts/ask-buildtest.ts):
//
//   npx tsx scripts/ask-redteam.ts --pass P1 --fake                                            # offline, no spend
//   npx tsx scripts/ask-redteam.ts --pass P1 --live --confirm-spend --approval <commit> [--out evals/e4_redteam/run-...]
//
//  * the catalogue must match the SHA-256 frozen in evals/e4_redteam/frozen.json (a changed catalogue is refused);
//  * P1 = the 60 attacks, budget $3.00; P2 = the 60 + 20 held-out paraphrases, budget $4.00;
//  * --live: --confirm-spend, --approval <commit with her d6-spend row>, output inside evals/e4_redteam; the D6 ledger
//    counts evals/d6_ask and evals/e4_redteam against the $20 cap; pre-call guard; 10% checkpoint; append-only;
//  * data: the committed snapshot only (loadEnv), never the live mart.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import { parse } from "yaml";
import { d6SpendSoFar, E4_ROOT, LEDGER_ROOTS, makeClient, run } from "./ask-buildtest";

export const PASS_BUDGET_USD: Record<string, number> = { P1: 3.0, P2: 4.0 };
export const CATALOGUE = path.join(E4_ROOT, "attacks.yaml");
const FROZEN = path.join(E4_ROOT, "frozen.json");

export type Attack = { id: string; family: string; expect: string; prompt: string };
export function catalogueHash(file = CATALOGUE): string {
  return createHash("sha256").update(readFileSync(file)).digest("hex");
}

export function loadCatalogue(file = CATALOGUE, frozen = FROZEN): { attacks: Attack[]; heldout: Attack[]; sha256: string } {
  const sha256 = catalogueHash(file);
  const want = JSON.parse(readFileSync(frozen, "utf8")).sha256;
  if (sha256 !== want) throw new Error(`refusing: ${path.basename(file)} sha256 ${sha256.slice(0, 12)} != frozen ${String(want).slice(0, 12)}`);
  const y = parse(readFileSync(file, "utf8"));
  const ids = [...y.attacks, ...y.heldout].map((a: Attack) => a.id);
  if (new Set(ids).size !== ids.length) throw new Error("duplicate attack ids");
  return { attacks: y.attacks, heldout: y.heldout, sha256 };
}

export function passQuestions(pass: string, cat: { attacks: Attack[]; heldout: Attack[] }) {
  if (!(pass in PASS_BUDGET_USD)) throw new Error("--pass must be P1 or P2");
  const qs = pass === "P1" ? cat.attacks : [...cat.attacks, ...cat.heldout];
  return qs.map((a) => ({ id: a.id, question: a.prompt, gold: { ...a } }));
}

async function main() {
  const args = process.argv.slice(2);
  const pass = args[args.indexOf("--pass") + 1];
  if (!args.includes("--pass")) throw new Error("--pass P1|P2 is required");
  const cat = loadCatalogue();
  const questions = passQuestions(pass, cat);
  const live = args.includes("--live");
  const date = new Date().toISOString().slice(0, 10);
  const outDir = args.includes("--out") ? path.resolve(args[args.indexOf("--out") + 1])
    : path.join(E4_ROOT, `run-${live ? "" : "fake-"}${pass}-${date}`);
  const made = await makeClient(args, outDir, E4_ROOT);
  const carried = made.live ? d6SpendSoFar(LEDGER_ROOTS, outDir) : 0;
  const summary = await run(made.client, outDir, carried, made.approval, questions, {
    budget: PASS_BUDGET_USD[pass], check: () => null, label: `E4 red-team ${pass}; flags and hand labels follow (scripts/redteam-score.ts)`,
    extra: { pass, catalogue_sha256: cat.sha256, data: "snapshot (lib/ask/env.ts loadEnv)" } });
  console.log(JSON.stringify(summary, null, 1));
}

if (process.argv[1] && process.argv[1].endsWith("ask-redteam.ts")) main().catch((e) => { console.error(e.message); process.exit(1); });
