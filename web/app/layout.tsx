import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Newsreader, Public_Sans } from "next/font/google";
import { site } from "@/content/story";
import "./globals.css";
import "./claims.css";

const newsreader = Newsreader({
  subsets: ["latin"],
  variable: "--font-newsreader",
  style: ["normal", "italic"],
  axes: ["opsz"],
  display: "swap",
});
const publicSans = Public_Sans({ subsets: ["latin"], variable: "--font-public-sans", display: "swap" });

export const metadata: Metadata = {
  title: { default: site.title, template: `%s · ${site.title}` },
  description: site.description,
  openGraph: { title: site.title, description: site.description, type: "article" },
};

export const viewport: Viewport = {
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f7f8f9" },
    { media: "(prefers-color-scheme: dark)", color: "#101215" },
  ],
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${newsreader.variable} ${publicSans.variable}`}>
      <body>
        <header className="masthead">
          <div className="wrap">
            <div className="masthead__inner col-wide">
              <Link href="/" className="masthead__name">{site.title}</Link>
              <nav className="masthead__nav" aria-label="Site">
                <Link href="/#ratchet">Story</Link>
                <Link href="/methods">Methods</Link>
                <Link href="/how-it-was-built">How it was built</Link>
                <Link href="/data">Data</Link>
                <Link href="/sources">Sources</Link>
              </nav>
            </div>
          </div>
        </header>
        {children}
        <footer className="footer">
          <div className="wrap">
            <div className="footer__inner col-wide">
              <span>{site.byline}</span>
              <span>
                Data: Federal Reserve Z.1, FRED, NY Fed Consumer Credit Panel. <Link href="/methods">Methods and caveats</Link>
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
