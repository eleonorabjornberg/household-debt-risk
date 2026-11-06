// /ask: Ask Hot Potato (PLAN D6). Renders only where the route may run (preview deployments, local dev).
import { notFound } from "next/navigation";
import AskPanel from "@/components/ask/AskPanel";
import { deploymentGate } from "@/lib/ask/gate";

export const dynamic = "force-dynamic";

export default function AskPage() {
  const g = deploymentGate();
  if (!g.ok && g.status === 404) notFound();
  return (
    <main className="ask-page">
      <AskPanel />
      {!g.ok && <p role="status">{g.message}</p>}
    </main>
  );
}
