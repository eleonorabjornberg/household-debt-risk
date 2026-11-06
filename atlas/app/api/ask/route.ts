// POST /api/ask {question} -> {answer, refused, reason_code, sources}. Ask Hot Potato (PLAN D6).
// Gated to preview deployments and local dev (lib/ask/gate.ts); limits in lib/ask/limits.ts; loop in lib/ask/agent.ts.
import { createHash } from "node:crypto";
import Anthropic from "@anthropic-ai/sdk";
import { ask } from "@/lib/ask/agent";
import { loadEnv } from "@/lib/ask/env";
import { deploymentGate } from "@/lib/ask/gate";
import { Limiter, LimitError, MemoryStore, utcDay, type Store } from "@/lib/ask/limits";

export const runtime = "nodejs";

let devStore: Store | null = null;
function store(): Store {
  // Local development only: an in-memory store (deploymentGate refuses Vercel until a shared store is configured).
  return (devStore ??= new MemoryStore());
}

export async function POST(request: Request) {
  const gate = deploymentGate();
  if (!gate.ok) return Response.json({ error: gate.message }, { status: gate.status });
  let question = "";
  try { question = String((await request.json())?.question ?? ""); }
  catch { return Response.json({ error: "Send JSON: {\"question\": \"...\"}" }, { status: 400 }); }

  const ip = (request.headers.get("x-forwarded-for") ?? "local").split(",")[0].trim();
  const salt = process.env.ASK_VISITOR_SALT ?? "local-dev";
  const visitor = createHash("sha256").update(`${salt}|${ip}|${utcDay(new Date())}`).digest("hex").slice(0, 32);
  const limiter = new Limiter(store());
  try {
    await limiter.admitVisitor(visitor);
    const client = new Anthropic({ apiKey: process.env.HHDEBT_ANTHROPIC_API_KEY, baseURL: "https://api.anthropic.com" });
    const a = await ask(question, { client, env: await loadEnv(), limiter });
    // Server log: cost and outcome only (never the key, a header or the visitor's IP).
    console.log(JSON.stringify({ ask: { refused: a.refused, reason: a.reason_code ?? null, tools: a.sources.map((s) => s.tool),
                                        cost_usd: Number(a.cost_usd.toFixed(6)), truncated: a.truncated } }));
    return Response.json({ answer: a.answer, refused: a.refused, reason_code: a.reason_code ?? null, sources: a.sources });
  } catch (e) {
    if (e instanceof LimitError) return Response.json({ error: e.message, code: e.code }, { status: 429 });
    console.log(JSON.stringify({ ask_error: e instanceof Error ? e.name : "error" }));
    return Response.json({ error: "Something went wrong answering that question." }, { status: 502 });
  }
}
