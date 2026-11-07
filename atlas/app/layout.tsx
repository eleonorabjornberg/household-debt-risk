import type { Metadata, Viewport } from "next";
import { Fraunces, Space_Grotesk } from "next/font/google";
import { site } from "@/content/story";
import "./globals.css";
import "./claims.css";
import "./pages.css";
import { TopBar } from "@/components/TopBar";

const fraunces = Fraunces({ subsets: ["latin"], variable: "--font-display", axes: ["opsz", "SOFT", "WONK"], style: ["normal", "italic"], display: "swap" });
const grotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-text", display: "swap" });

export const metadata: Metadata = {
  title: `${site.title}: ${site.kicker}`,
  description: site.description,
  openGraph: {
    title: site.title,
    description: site.description,
    type: "article",
  },
};

export const viewport: Viewport = {
  // One deliberate light theme, in light and dark system modes alike.
  themeColor: "#ffffff",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${grotesk.variable}`}>
      <body>
        <TopBar />
        {children}
      </body>
    </html>
  );
}
