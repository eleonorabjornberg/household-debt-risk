import type { Metadata, Viewport } from "next";
import { Fraunces, Space_Grotesk } from "next/font/google";
import { site } from "@/content/story";
import "./globals.css";

const fraunces = Fraunces({ subsets: ["latin"], variable: "--font-display", axes: ["opsz", "SOFT", "WONK"], style: ["normal", "italic"], display: "swap" });
const grotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-text", display: "swap" });

const host = process.env.VERCEL_PROJECT_PRODUCTION_URL;

export const metadata: Metadata = {
  metadataBase: new URL(host ? `https://${host}` : "http://localhost:3000"),
  title: `${site.title}: ${site.kicker}`,
  description: site.description,
  openGraph: {
    title: site.title,
    description: site.description,
    type: "article",
    images: [{ url: "/api/og", width: 1200, height: 630 }],
  },
  twitter: { card: "summary_large_image" },
};

export const viewport: Viewport = {
  // One deliberate print-on-paper theme, in light and dark system modes alike.
  themeColor: "#f3ecdc",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${grotesk.variable}`}>
      <body>{children}</body>
    </html>
  );
}
