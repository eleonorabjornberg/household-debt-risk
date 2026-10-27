// Issues a short-lived Tableau Connected Apps (direct trust) JWT for the Embedding API v3.
// The secret never leaves the server; the browser only receives a token valid for 5 minutes
// that can do nothing but embed views as TABLEAU_EMBED_USER.
import { randomUUID } from "node:crypto";
import { SignJWT } from "jose";
import { connection } from "next/server";
import { missingTableauEnv } from "@/lib/tableau";

const TOKEN_TTL_SECONDS = 5 * 60; // Tableau allows at most 10 minutes.

export async function GET() {
  await connection(); // never prerender: every request gets a fresh token

  const missing = missingTableauEnv();
  if (missing.length > 0) {
    return Response.json(
      {
        error: "Tableau embedding is not configured on this deployment.",
        missing,
        hint: "Set these environment variables (see web/.env.example) and redeploy. The site falls back to its built-in charts meanwhile.",
      },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }

  const clientId = process.env.TABLEAU_CONNECTED_APP_CLIENT_ID!;
  const secretId = process.env.TABLEAU_CONNECTED_APP_SECRET_ID!;
  const secret = new TextEncoder().encode(process.env.TABLEAU_CONNECTED_APP_SECRET_VALUE!);

  const token = await new SignJWT({ scp: ["tableau:views:embed"] })
    .setProtectedHeader({ alg: "HS256", typ: "JWT", kid: secretId, iss: clientId })
    .setIssuer(clientId)
    .setAudience("tableau")
    .setSubject(process.env.TABLEAU_EMBED_USER!)
    .setJti(randomUUID())
    .setIssuedAt()
    .setExpirationTime(`${TOKEN_TTL_SECONDS}s`)
    .sign(secret);

  return Response.json({ token, expiresIn: TOKEN_TTL_SECONDS }, { headers: { "Cache-Control": "no-store" } });
}
