import { storeEnv } from "./limits";
// Where Ask Hot Potato may run (PLAN D6): Vercel preview (her d6-preview, PLAN 0e0dd6c) and, since her
// production OK of 2026-11-15, Vercel production; plus local development. On every deployment it stays off
// until the enable flag, the API key and the shared limit store are all set in the Vercel project settings.
export type Gate = { ok: true } | { ok: false; status: number; message: string };

export function deploymentGate(env: Record<string, string | undefined> = process.env): Gate {
  const onVercel = !!env.VERCEL;
  if (onVercel && env.VERCEL_ENV !== "preview" && env.VERCEL_ENV !== "production")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (!onVercel && env.NODE_ENV === "production" && env.ASK_ALLOW_LOCAL_PROD !== "1")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (env.NEXT_PUBLIC_ASK_ENABLED !== "1")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (!env.HHDEBT_ANTHROPIC_API_KEY)
    return { ok: false, status: 503, message: "Ask Hot Potato is not configured (no API key)." };
  // The shared limit store (Vercel KV / Upstash Redis, her d6-store (a)) is required on Vercel; she adds it.
  if (onVercel && !storeEnv(env))
    return { ok: false, status: 503, message: "Ask Hot Potato is not configured (no shared limit store)." };
  return { ok: true };
}
