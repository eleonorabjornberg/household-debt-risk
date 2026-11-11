"use client";
// The top bar on every Hot Potato page (site-visible (b), 2026-11-07: one site with the pages moved from web/).
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS: { href: string; label: string; also?: string[] }[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/research", label: "Research" },
  { href: "/scenarios", label: "Scenarios" },
  { href: "/how-it-was-built", label: "How it was built" },
  // Methods and Sources share one entry (review list P2, 2026-11-11); both routes stay, and each page links to the other.
  { href: "/methods", label: "Methods & sources", also: ["/sources"] },
];

export function TopBar() {
  const path = usePathname();
  return (
    <nav className="topbar" aria-label="Site">
      <Link href="/" className="topbar__brand" aria-current={path === "/" ? "page" : undefined}>Hot Potato</Link>
      <div className="topbar__nav">
        {LINKS.map((l) => (
          <Link key={l.href} href={l.href} aria-current={[l.href, ...(l.also ?? [])].some((h) => path === h || path.startsWith(`${h}/`)) ? "page" : undefined}>{l.label}</Link>
        ))}
      </div>
    </nav>
  );
}
