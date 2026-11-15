import type { Metadata } from "next";
import { notFound } from "next/navigation";
import AskPanel from "@/components/ask/AskPanel";
import { PotatoPerson } from "@/components/Potato";
import { deploymentGate } from "@/lib/ask/gate";
import { ask } from "@/content/story";

// /ask: Ask Hot Potato (PLAN D6; R1 layout, 2026-11-15). A magenta colour block like Built with Claude's blue one
// (Eleonora: "a more fun layout"). Renders only where the route may run.
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Ask · Hot Potato",
  description: "Ask the project's Fed data a question in plain English.",
};

export default function AskPage() {
  const g = deploymentGate();
  if (!g.ok && g.status === 404) notFound();
  return (
    <main className="band band--ask band--page ask-page">
      <div className="wrap ask-layout">
        <div className="ask-layout__intro">
          <h1 className="page-h">{ask.title}</h1>
          <p className="band__lede">{ask.intro}</p>
          <div className="ask-cast" aria-hidden="true">
            <PotatoPerson potatoes={3} pose="toss" ink="var(--sun)" width={110} />
            <PotatoPerson potatoes={5} pose="sweat" ink="var(--paper)" width={92} />
          </div>
        </div>
        <AskPanel examples={ask.examples} disabledMessage={g.ok ? undefined : g.message} />
      </div>
    </main>
  );
}
