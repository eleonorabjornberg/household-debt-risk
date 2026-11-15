import Link from "next/link";
import type { Metadata } from "next";
import { DraftBanner } from "@/components/pages/DraftBanner";

// /appendix (R1, 2026-11-15): the documentation pages, one line and one link each. The routes themselves are unchanged
// and keep their own draft banners. This page's lines are a Claude draft.
export const metadata: Metadata = {
  title: "Appendix · Hot Potato",
  description: "The dashboard, scenarios, research, methods and sources behind Hot Potato.",
};

const PAGES = [
  { href: "/dashboard", name: "Dashboard", line: "The latest quarter at a glance, with the full findings below." },
  { href: "/scenarios", name: "Scenarios", line: "Set default and loss rates and see who takes the losses." },
  { href: "/research", name: "Research", line: "The write-ups behind the story, one question each." },
  { href: "/methods", name: "Methods", line: "Data lineage, scope, limits and the series catalog." },
  { href: "/sources", name: "Sources", line: "Every number on the site with its query, series, vintage and check." },
];

export default function AppendixPage() {
  return (
    <main className="pg">
      <DraftBanner testId="appendix-draft-banner" />
      <header className="pg-col">
        <p className="tag">Appendix</p>
        <h1>Appendix</h1>
      </header>
      <ul className="appendix">
        {PAGES.map((p) => (
          <li key={p.href}>
            <Link href={p.href}>{p.name}</Link>
            <span>{p.line}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
