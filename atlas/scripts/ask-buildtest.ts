// D6 (PLAN task "Ask Hot Potato") paid build test. Developer testing under Eleonora's d6-spend: a $20 cap for
// building D6 and the E4 red-team, separate from E1 (PLAN 0e0dd6c). Same safeguards as E1.
//
//   npx tsx scripts/ask-buildtest.ts --fake                         # offline, fake client, no spend
//   npx tsx scripts/ask-buildtest.ts --live --confirm-spend --approval <commit> [--out evals/d6_ask/run-...]  # spends money
//
// Safeguards:
//  * --live refuses unless PLAN.md at the approval commit has her d6-spend row (dated, "| Eleonora |", "(d6-spend",
//    "cap $20") and that commit is an ancestor of HEAD;
//  * a ledger of every D6 run directory's logged spend (evals/d6_ask/run-*/calls.jsonl, live runs only) counts
//    against the $20 cap; a pre-call guard stops before any call could reach it;
//  * this run's own budget is RUN_BUDGET_USD; the pre-call guard also stops before it could be reached;
//  * a 10% checkpoint projects this run's total and stops if the projection exceeds RUN_BUDGET_USD;
//  * results are append-only: an output directory that already holds a run is refused.
// The key is read from HHDEBT_ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL is ignored (base URL passed explicitly), and
// nothing here prints or writes the key or any header.
import { execFileSync } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { ask, WORST_CALL_USD } from "../lib/ask/agent";
import { loadEnv } from "../lib/ask/env";
import { Limiter, LimitError, MemoryStore } from "../lib/ask/limits";

export const D6_CAP_USD = 20;
export const RUN_BUDGET_USD = 2;
export const CHECKPOINT = 0.1;
const ROOT = path.join(__dirname, "..", "..");
export const OUT_ROOT = path.join(ROOT, "evals", "d6_ask");
// E4 red-team runs count against the same $20 D6 cap (PLAN 2026-11-06 d6-spend: "building D6 and the E4 red-team").
export const E4_ROOT = path.join(ROOT, "evals", "e4_redteam");
export const LEDGER_ROOTS = [OUT_ROOT, E4_ROOT];
const SPEND_ROW = /\(d6-spend\b[^)]*\)[^|]*cap \$20/i;

export function d6SpendSoFar(roots: string | string[] = LEDGER_ROOTS, exclude?: string): number {
  let total = 0;
  for (const root of Array.isArray(roots) ? roots : [roots]) {
  if (!existsSync(root)) continue;
  for (const d of readdirSync(root).filter((x) => x.startsWith("run-") && !x.includes("fake")).sort()) {
    if (exclude && path.resolve(root, d) === path.resolve(exclude)) continue;
    const f = path.join(root, d, "calls.jsonl");
    if (!existsSync(f)) continue;
    for (const l of readFileSync(f, "utf8").split("\n")) if (l.trim()) total += JSON.parse(l).cost_usd ?? 0;
  }
  }
  return total;
}

export function spendRow(plan: string): string | null {
  const rows = plan.split("\n").filter((l) => /^\| 20\d\d-\d\d-\d\d \|/.test(l) && l.trimEnd().endsWith("| Eleonora |") && SPEND_ROW.test(l));
  return rows.length ? rows[rows.length - 1] : null;
}

export function checkApproval(commit: string): string {
  const git = (...a: string[]) => execFileSync("git", a, { cwd: ROOT, encoding: "utf8" });
  try { git("merge-base", "--is-ancestor", commit, "HEAD"); }
  catch { throw new Error(`refusing: ${commit} is not an ancestor of HEAD`); }
  const row = spendRow(git("show", `${commit}:PLAN.md`));
  if (!row) throw new Error(`refusing: no Eleonora d6-spend row (cap $20) in PLAN.md at ${commit}`);
  return row;
}

/** 30 build-test questions from the E1 set: never the 20 held-out ones; 20 answerable (every 3rd by id) + 10 unanswerable. */
export function buildQuestions(): { id: string; question: string; gold: any }[] {
  const gold = JSON.parse(readFileSync(path.join(ROOT, "evals", "e1_sql_benchmark", "gold.json"), "utf8")).questions as any[];
  const held = gold.filter((q) => !q.holdout).sort((a, b) => a.id.localeCompare(b.id));
  const ans = held.filter((q) => q.gold !== "refuse").filter((_, i) => i % 3 === 0).slice(0, 20);
  const un = held.filter((q) => q.gold === "refuse").slice(0, 10);
  return [...ans, ...un].map((q) => ({ id: q.id, question: q.question, gold: q }));
}

/** Rough build-test check, NOT an evaluation: does the prose answer contain the gold value (or refuse when it should)? */
export function roughCheck(answer: string, refused: boolean, gold: any): boolean {
  if (gold.gold === "refuse") return refused || !/\d/.test(answer.replace(/\b(19|20)\d\d(Q[1-4])?\b/g, ""));
  const nums = [...answer.replace(/,/g, "").matchAll(/-?\d+(\.\d+)?/g)].map((m) => Number(m[0]));
  const g = Number(gold.gold), tol = Number(gold.tolerance);
  const cands = gold.unit === "share" ? nums.map((n) => n / 100).concat(nums) : nums;
  return cands.some((n) => Math.abs(n - g) <= Math.max(tol, Math.abs(g) * 0.005));
}

export class D6Limiter extends Limiter {
  constructor(private carried: number, private runSpent: () => number, private budget = RUN_BUDGET_USD) { super(new MemoryStore()); }
  async guard(worst: number): Promise<void> {
    if (this.carried + this.runSpent() + worst >= D6_CAP_USD)
      throw new LimitError("app_daily_budget", `pre-call guard: D6 spend $${(this.carried + this.runSpent()).toFixed(4)} + worst $${worst.toFixed(4)} would reach the $${D6_CAP_USD} cap`);
    if (this.runSpent() + worst >= this.budget)
      throw new LimitError("app_daily_budget", `pre-call guard: this run's $${this.runSpent().toFixed(4)} + worst $${worst.toFixed(4)} would reach its $${this.budget} budget`);
  }
}

export type RunOpts = { budget?: number; check?: (answer: string, refused: boolean, gold: any) => boolean | null; label?: string;
                        extra?: Record<string, unknown> };
export async function run(client: any, outDir: string, carried: number, approval: string | null, questions = buildQuestions(),
                          opts: RunOpts = {}) {
  const budget = opts.budget ?? RUN_BUDGET_USD, check = opts.check ?? roughCheck;
  if (existsSync(path.join(outDir, "calls.jsonl"))) throw new Error(`refusing: ${outDir} already holds a run`);
  mkdirSync(outDir, { recursive: true });
  const env = await loadEnv(path.join(ROOT, "atlas"));
  let spent = 0, done = 0, stop: string | null = null, okCount = 0;
  const limiter = new D6Limiter(carried, () => spent, budget);
  const log = (rec: object) => appendFileSync(path.join(outDir, "calls.jsonl"), JSON.stringify({ ...rec, ts: new Date().toISOString() }) + "\n");
  for (const q of questions) {
    try {
      const a = await ask(q.question, { client, env, limiter });
      spent += a.cost_usd;
      const ok = check(a.answer, a.refused, q.gold);
      okCount += ok ? 1 : 0;
      log({ qid: q.id, family: q.gold.family, refused: a.refused, reason_code: a.reason_code ?? null, answer: a.answer,
            sources: a.sources, usage: a.usage, cost_usd: Number(a.cost_usd.toFixed(6)), truncated: a.truncated, rough_ok: ok });
      done++;
      if (done === Math.max(1, Math.floor(questions.length * CHECKPOINT))) {
        const proj = (spent / done) * questions.length;
        log({ checkpoint: done, of: questions.length, spent_usd: Number(spent.toFixed(6)), projected_usd: Number(proj.toFixed(4)) });
        if (proj > budget) { stop = `checkpoint: projected $${proj.toFixed(2)} > run budget $${budget}`; break; }
      }
    } catch (e) {
      stop = e instanceof Error ? e.message : String(e);
      break;
    }
  }
  const summary = { approval, questions: questions.length, done, spent_usd: Number(spent.toFixed(6)),
                    d6_spend_total_usd: Number((carried + spent).toFixed(6)), d6_cap_usd: D6_CAP_USD, run_budget_usd: budget,
                    worst_call_usd: WORST_CALL_USD, rough_ok: okCount, stop, label: opts.label ?? "build test, not an evaluation",
                    ...(opts.extra ?? {}) };
  writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 1) + "\n");
  return summary;
}

/** The client for a run: the offline fake, or (with every safeguard) the live API. Shared with ask-redteam.ts. */
export async function makeClient(args: string[], outDir: string, ledgerRoot: string): Promise<{ client: any; approval: string | null; live: boolean }> {
  const live = args.includes("--live"), fake = args.includes("--fake");
  if (live === fake) throw new Error("pass exactly one of --fake or --live");
  if (!live) return { client: fakeClient(), approval: null, live };
  // Added 2026-11-06 after an accidental live run: spending needs an explicit flag, and live output must go
  // where the D6 ledger (d6SpendSoFar) can see it.
  if (!args.includes("--confirm-spend")) throw new Error("refusing: --live also needs --confirm-spend");
  if (!path.resolve(outDir).startsWith(ledgerRoot + path.sep))
    throw new Error(`refusing: live output must be inside ${ledgerRoot} so the D6 spend ledger counts it`);
  const commit = args[args.indexOf("--approval") + 1];
  if (!args.includes("--approval") || !commit) throw new Error("refusing: --live needs --approval <commit>");
  const approval = checkApproval(commit);
  const key = process.env.HHDEBT_ANTHROPIC_API_KEY;
  if (!key) throw new Error("HHDEBT_ANTHROPIC_API_KEY is not set");
  delete process.env.ANTHROPIC_BASE_URL;
  delete process.env.ANTHROPIC_AUTH_TOKEN;
  const { default: Anthropic } = await import("@anthropic-ai/sdk");
  return { client: new Anthropic({ apiKey: key, baseURL: "https://api.anthropic.com" }), approval, live };
}

export function fakeClient() {
  return { messages: { create: async (body: any) => (body.messages.length === 1
    ? { model: "fake", usage: { input_tokens: 100, output_tokens: 80, cache_read_input_tokens: 2000, cache_creation_input_tokens: 0 }, stop_reason: "tool_use",
        content: [{ type: "tool_use", id: "t1", name: "data_coverage", input: {} }] }
    : { model: "fake", usage: { input_tokens: 100, output_tokens: 120, cache_read_input_tokens: 4000, cache_creation_input_tokens: 0 }, stop_reason: "end_turn",
        content: [{ type: "text", text: "Fake answer." }] }) } };
}

async function main() {
  const args = process.argv.slice(2);
  const date = new Date().toISOString().slice(0, 10);
  const outArg = args[args.indexOf("--out") + 1];
  const outDir = args.includes("--out") ? path.resolve(outArg) : path.join(OUT_ROOT, `run-${args.includes("--live") ? "" : "fake-"}${date}`);
  const { client, approval, live } = await makeClient(args, outDir, OUT_ROOT);
  const carried = live ? d6SpendSoFar(LEDGER_ROOTS, outDir) : 0;
  console.log(JSON.stringify(await run(client, outDir, carried, approval), null, 1));
}

if (process.argv[1] && process.argv[1].endsWith("ask-buildtest.ts")) main().catch((e) => { console.error(e.message); process.exit(1); });
