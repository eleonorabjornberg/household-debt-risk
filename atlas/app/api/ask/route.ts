// POST /api/ask {question} -> {answer, refused, reason_code, sources}. Ask Hot Potato (PLAN D6).
// Gated to preview deployments and local dev (lib/ask/gate.ts); limits in lib/ask/limits.ts; store and data source in
// lib/ask/runtime.ts; loop in lib/ask/agent.ts.
import { createHash } from "node:crypto";
import Anthropic from "@anthropic-ai/sdk";
import { ask } from "@/lib/ask/agent";
import { deploymentGate } from "@/lib/ask/gate";
import { Limiter, LimitError, utcDay } from "@/lib/ask/limits";
import { askEnv, askStore } from "@/lib/ask/runtime";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const gate = deploymentGate();
  if (!gate.ok) return Response.json({ error: gate.message }, { status: gate.status });
  let question = "";
  try { question = String((await request.json())?.question ?? ""); }
  catch { return Response.json({ error: "Send JSON: {\"question\": \"...\"}" }, { status: 400 }); }

  const ip = (request.headers.get("x-forwarded-for") ?? "local").split(",")[0].trim();
  const salt = process.env.ASK_VISITOR_SALT ?? "local-dev";
  const visitor = createHash("sha256").update(`${salt}|${ip}|${utcDay(new Date())}`).digest("hex").slice(0, 32);
  // Fail closed: no limit store or no data means no model call.
  let limiter: Limiter, env;
  try {
    limiter = new Limiter(await askStore());
    await limiter.admitVisitor(visitor);
    env = await askEnv();
  } catch (e) {
    if (e instanceof LimitError) return Response.json({ error: e.message, code: e.code }, { status: 429 });
    console.log(JSON.stringify({ ask_unavailable: e instanceof Error ? e.name : "error" }));
    return Response.json({ error: "Ask Hot Potato is unavailable right now." }, { status: 503 });
  }
  try {
    const client = new Anthropic({ apiKey: process.env.HHDEBT_ANTHROPIC_API_KEY, baseURL: "https://api.anthropic.com" });
    const a = await ask(question, { client, env, limiter });
    // Server log: cost and outcome only (never the key, a header or the visitor's IP).
    console.log(JSON.stringify({ ask: { refused: a.refused, reason: a.reason_code ?? null, tools: a.sources.map((s) => s.tool),
                                        backend: env.backend ?? "snapshot", cost_usd: Number(a.cost_usd.toFixed(6)),
                                        truncated: a.truncated } }));
    return Response.json({ answer: a.answer, refused: a.refused, reason_code: a.reason_code ?? null, sources: a.sources,
                           backend: env.backend ?? "snapshot" });
  } catch (e) {
    if (e instanceof LimitError) return Response.json({ error: e.message, code: e.code }, { status: 429 });
    console.log(JSON.stringify({ ask_error: e instanceof Error ? e.name : "error" }));
    return Response.json({ error: "Something went wrong answering that question." }, { status: 502 });
  }
}
