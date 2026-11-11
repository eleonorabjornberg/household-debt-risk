"use client";
// Filter the /sources list by the page a number appears on (review list P1, 2026-11-11).
// Works on the rendered list by register id, so the shared SourcesList copy stays untouched.
import { useEffect, useState } from "react";
import { claims } from "@/components/claims/SourceRef";

const PAGES: { label: string; files: string[] }[] = [
  { label: "Home", files: ["atlas/app/page.tsx", "atlas/content/story.ts", "atlas/components/Experience.tsx"] },
  { label: "Dashboard", files: ["atlas/components/dashboard/"] },
  { label: "Methods", files: ["atlas/content/methods.ts", "atlas/app/methods/"] },
  { label: "How it was built", files: ["atlas/content/build.ts", "atlas/app/how-it-was-built/"] },
];

export function pagesFor(locations: string[]): string[] {
  return PAGES.filter((p) => locations.some((l) => p.files.some((f) => l.startsWith(f)))).map((p) => p.label);
}

export function SourcesFilter() {
  const [page, setPage] = useState("All");
  useEffect(() => {
    for (const c of claims) {
      const el = document.getElementById(c.id);
      if (el) el.hidden = page !== "All" && !pagesFor(c.locations).includes(page);
    }
  }, [page]);
  const options = ["All", ...PAGES.map((p) => p.label).filter((l) => claims.some((c) => pagesFor(c.locations).includes(l)))];
  return (
    <div className="sources-filter" role="group" aria-label="Filter by page">
      <span>Show numbers on:</span>
      {options.map((o) => (
        <button key={o} type="button" aria-pressed={page === o} onClick={() => setPage(o)}>{o}</button>
      ))}
    </div>
  );
}
