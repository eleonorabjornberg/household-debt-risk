"use client";
// The top bar on every Hot Potato page (site-visible (b), 2026-11-07: one site with the pages moved from web/).
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/research", label: "Research" },
  { href: "/scenarios", label: "Scenarios" },
  { href: "/how-it-was-built", label: "How it was built" },
  { href: "/methods", label: "Methods" },
  { href: "/sources", label: "Sources" },
];

export function TopBar() {
  const path = usePathname();
  return (
    <nav className="topbar" aria-label="Site">
      <Link href="/" className="topbar__brand" aria-current={path === "/" ? "page" : undefined}>Hot Potato</Link>
      <div className="topbar__nav">
        {LINKS.map((l) => (
          <Link key={l.href} href={l.href} aria-current={path === l.href || path.startsWith(`${l.href}/`) ? "page" : undefined}>{l.label}</Link>
        ))}
      </div>
    </nav>
  );
}
