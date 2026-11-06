// Where Ask Hot Potato may run (PLAN D6, Eleonora's d6-preview, PLAN 0e0dd6c): Vercel PREVIEW deployments and
// local development only. Production is refused until she approves it separately.
export type Gate = { ok: true } | { ok: false; status: number; message: string };

export function deploymentGate(env: Record<string, string | undefined> = process.env): Gate {
  const onVercel = !!env.VERCEL;
  if (onVercel && env.VERCEL_ENV !== "preview")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (!onVercel && env.NODE_ENV === "production" && env.ASK_ALLOW_LOCAL_PROD !== "1")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (env.NEXT_PUBLIC_ASK_ENABLED !== "1")
    return { ok: false, status: 404, message: "Ask Hot Potato is not enabled on this deployment." };
  if (!env.HHDEBT_ANTHROPIC_API_KEY)
    return { ok: false, status: 503, message: "Ask Hot Potato is not configured (no API key)." };
  // A durable limit store is required on Vercel (her open question 1); until one is wired in, refuse there.
  if (onVercel && !env.ASK_LIMIT_STORE)
    return { ok: false, status: 503, message: "Ask Hot Potato is not configured (no shared limit store)." };
  return { ok: true };
}
