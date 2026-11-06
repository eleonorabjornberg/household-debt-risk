// Ask Hot Potato (PLAN D6): one reader question -> a short answer with its sources, via Sonnet 5.5 and the ported
// household-credit tools (lib/ask/tools.ts). Eleonora's choices (PLAN 0e0dd6c): Sonnet; preview limits in
// lib/ask/limits.ts. Every answer carries the tool calls (query), series IDs and vintage it used.
import type Anthropic from "@anthropic-ai/sdk";
import { computedNote, computedNumbers, hypotheticalCheck, SYSTEM_RULES } from "./guardrails";
import { Limiter } from "./limits";
import { TOOLS, check_answerable, type Env, type Row } from "./tools";

export const MODEL = "claude-sonnet-5-5";
export const MAX_TURNS = 4;
export const MAX_TOKENS = 2048;
export const MAX_QUESTION_CHARS = 500;
// Live prices, USD per million tokens (platform.claude.com pricing page, checked 2026-11-05).
export const PRICE = { input: 2.0, output: 10.0, cache_read: 0.1, cache_write: 2.5 };
// Pre-call worst case: 30k fresh input tokens written to cache + MAX_TOKENS of output.
export const WORST_CALL_USD = (30_000 * PRICE.cache_write + MAX_TOKENS * PRICE.output) / 1e6;

export const SYSTEM = [
  "You answer questions about who holds US household mortgage and consumer credit, using only the tools provided",
  "(read-only data from the Federal Reserve's Z.1 Financial Accounts and the New York Fed Consumer Credit Panel).",
  "Quote only numbers returned by tools, with their quarter and units. Never estimate, extrapolate or forecast:",
  "if the data cannot answer, say so plainly and suggest the nearest question it can answer.",
  "Keep the NY Fed and Z.1 apart (different definitions). Say when a number is a share (0-1 shown as %).",
  "Answer in at most 120 words, in plain English, for a general reader. Do not list your tool calls; the page shows them.",
  SYSTEM_RULES, // E4 P1 guardrails (lib/ask/guardrails.ts)
].join(" ");

const Q = { type: "string", description: "Quarter like 2026Q2" };
export const TOOL_DEFS: Anthropic.Tool[] = [
  { name: "public_share", description: "Public holders' share of household 1-4 family mortgages + consumer credit, quarterly (Z.1). Quarters like 2026Q2; default is the latest quarter. measure: total | mortgage | consumer_credit. Public = federal + GSE/agency pools + state & local.",
    input_schema: { type: "object", properties: { start: Q, end: Q, measure: { type: "string", enum: ["total", "mortgage", "consumer_credit"] } } } },
  { name: "holdings_by_bucket", description: "The six risk buckets for one quarter (e.g. 2007Q4): nominal $ millions and share of scope, with mortgage/consumer split. Default is the latest quarter.",
    input_schema: { type: "object", properties: { quarter: Q } } },
  { name: "crisis_windows", description: "Crisis event windows (-8..+16 quarters). Lists crises with the metric at t0 and changes after 4/8/16 quarters (percentage points for shares). metric examples: public_share, share:gse_agency, coverage:home_backed.",
    input_schema: { type: "object", properties: { crisis_id: { type: "string" }, metric: { type: "string" } } } },
  { name: "collateral_coverage", description: "Collateral value / debt by collateral class (home-backed, vehicle-backed, uncollateralized, other), quarterly. Default is the latest quarter.",
    input_schema: { type: "object", properties: { start: Q, end: Q } } },
  { name: "nyfed_by_type", description: "NY FED Consumer Credit Panel (NOT Z.1): balances and serious-delinquency transitions by loan type (mortgage, heloc, auto, credit_card, student, other), 2003Q1+.",
    input_schema: { type: "object", properties: { start: Q, end: Q } } },
  { name: "lookup_claim", description: "Find registered claims (the project's published numbers) by claim id or words, with validation status (PASS / UNVERIFIED / ESTIMATE).",
    input_schema: { type: "object", properties: { text_or_id: { type: "string" } }, required: ["text_or_id"] } },
  { name: "data_coverage", description: "What the data can and cannot answer, with covered quarters.",
    input_schema: { type: "object", properties: {} } },
];

export type Source = { tool: string; args: Row; ok: boolean; refused?: boolean; series_ids: string[];
                       vintage: string | null; source: string | null };
export type Answer = { answer: string; refused: boolean; reason_code?: string; sources: Source[];
                       usage: Row[]; cost_usd: number; truncated: boolean; computed_numbers?: string[] };

export function callCost(u: Row): number {
  return ((u.input_tokens ?? 0) * PRICE.input + (u.output_tokens ?? 0) * PRICE.output +
          (u.cache_read_input_tokens ?? 0) * PRICE.cache_read +
          (u.cache_creation_input_tokens ?? 0) * PRICE.cache_write) / 1e6;
}

type Client = { messages: { create: (body: any) => Promise<any> } };

export async function ask(question: string, deps: { client: Client; env: Env; limiter: Limiter }): Promise<Answer> {
  const q = (question ?? "").trim();
  if (!q) return { answer: "Please ask a question.", refused: true, reason_code: "empty", sources: [], usage: [], cost_usd: 0, truncated: false };
  if (q.length > MAX_QUESTION_CHARS)
    return { answer: `Please keep questions under ${MAX_QUESTION_CHARS} characters.`, refused: true, reason_code: "too_long",
             sources: [], usage: [], cost_usd: 0, truncated: false };
  // Deterministic pre-check (the ported check_answerable): forecasts, borrower-level, geography, holder x type,
  // sub-quarterly and out-of-coverage years are refused before any model call, with the nearest answerable tool.
  const pre = check_answerable(deps.env, { question: q });
  if (pre.refused)
    return { answer: `${pre.reason} ${pre.note}`, refused: true, reason_code: pre.reason_code,
             sources: [{ tool: "check_answerable", args: { question: q }, ok: false, refused: true, series_ids: [], vintage: null, source: null }],
             usage: [], cost_usd: 0, truncated: false };
  // E4 guardrail: hypotheticals, scenarios and trend continuations are refused before any model call.
  const hyp = hypotheticalCheck(q);
  if (hyp)
    return { answer: `${hyp.reason} ${hyp.note}`, refused: true, reason_code: hyp.reason_code,
             sources: [{ tool: "hypothetical_check", args: { question: q }, ok: false, refused: true, series_ids: [], vintage: null, source: null }],
             usage: [], cost_usd: 0, truncated: false };

  const messages: Row[] = [{ role: "user", content: q }];
  const sources: Source[] = [];
  const outputs: Row[] = [];
  const usage: Row[] = [];
  let cost = 0, text = "", stop: string | null = null;
  for (let turn = 1; turn <= MAX_TURNS; turn++) {
    await deps.limiter.guard(WORST_CALL_USD); // throws LimitError at the daily stop
    const resp = await deps.client.messages.create({
      model: MODEL, max_tokens: MAX_TOKENS, output_config: { effort: "medium" },
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      tools: TOOL_DEFS, messages, cache_control: { type: "ephemeral" },
    });
    const u = { input_tokens: resp.usage?.input_tokens ?? 0, output_tokens: resp.usage?.output_tokens ?? 0,
                cache_read_input_tokens: resp.usage?.cache_read_input_tokens ?? 0,
                cache_creation_input_tokens: resp.usage?.cache_creation_input_tokens ?? 0 };
    const c = callCost(u);
    cost += c;
    usage.push({ turn, served_model: resp.model ?? null, ...u, cost_usd: c }); // the model that actually answered
    await deps.limiter.record(c);
    stop = resp.stop_reason;
    const blocks: Row[] = resp.content ?? [];
    const t = blocks.filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
    if (t) text = t;
    const uses = blocks.filter((b) => b.type === "tool_use");
    if (stop !== "tool_use" || !uses.length) break;
    messages.push({ role: "assistant", content: blocks });
    const results = uses.map((b) => {
      const fn = TOOLS[b.name];
      let out: Row;
      try { out = fn ? fn(deps.env, b.input ?? {}) : { ok: false, refused: true, reason: `unknown tool ${b.name}` }; }
      catch (e) { out = { ok: false, error: String(e) }; }
      outputs.push(out);
      sources.push({ tool: b.name, args: b.input ?? {}, ok: !!out.ok, refused: !!out.refused,
                     series_ids: out.series_ids ?? [], vintage: out.vintage?.source_vintage ?? null, source: out.source ?? null });
      return { type: "tool_result", tool_use_id: b.id, content: JSON.stringify(out), is_error: !out.ok && !out.refused };
    });
    messages.push({ role: "user", content: results });
  }
  const truncated = stop === "tool_use";
  if (stop === "refusal")
    return { answer: "The model declined to answer this question.", refused: true, reason_code: "model_refusal", sources, usage, cost_usd: cost, truncated };
  if (!text || truncated)
    return { answer: "I couldn't finish answering within this preview's step limit. Try a narrower question (one quarter, one measure).",
             refused: true, reason_code: "turn_limit", sources, usage, cost_usd: cost, truncated };
  // E4 guardrail: label the model's own arithmetic (numbers no tool returned and the question did not contain).
  const computed = computedNumbers(text, outputs, q);
  return { answer: text + computedNote(computed), refused: false, sources, usage, cost_usd: cost, truncated, computed_numbers: computed };
}
