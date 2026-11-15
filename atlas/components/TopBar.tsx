"use client";
// The top bar on every Hot Potato page. R1 (2026-11-15): three items only; the documentation pages are linked from
// /appendix, and /appendix and GitHub from the footer.
import Link from "next/link";
import { usePathname } from "next/navigation";

// Each link wears the colour of the page it opens (Eleonora, 2026-11-15).
const LINKS: { href: string; label: string; tone: string }[] = [
  { href: "/ask", label: "Ask", tone: "ask" },
  { href: "/how-it-was-built", label: "Built with Claude", tone: "build" },
];

export function TopBar() {
  const path = usePathname();
  return (
    <nav className="topbar" aria-label="Site">
      <div className="wrap topbar__row">
        <Link href="/" className="topbar__brand" aria-current={path === "/" ? "page" : undefined}>Hot Potato</Link>
        <div className="topbar__nav">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className={`nav--${l.tone}`} aria-current={path === l.href || path.startsWith(`${l.href}/`) ? "page" : undefined}>{l.label}</Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
