import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // lib/data.ts falls back to these JSON snapshots at build and revalidation time.
  outputFileTracingIncludes: {
    "/": ["./public/data/**/*.json"],
    // /methods (moved from web/, site-visible (b)) reads meta.json and the series via lib/data.ts on revalidation.
    "/methods": ["./public/data/**/*.json"],
    // /dashboard (F7) reads the snapshots and content/findings.md.
    "/dashboard": ["./public/data/**/*.json", "./content/findings.md"],
    // /research/[slug] reads its copied write-up (content/research, scripts/sync-research.mjs).
    "/research/[slug]": ["./content/research/*.md"],
    // Ask Hot Potato's route reads the snapshots and the exported catalog and register at request time.
    "/api/ask": ["./public/data/**/*.json", "./lib/ask/catalog.json", "./lib/ask/register.json"],
  },
  // F7 (docket 54): Findings merged into the Dashboard tab; old links land on the findings section.
  async redirects() {
    return [{ source: "/findings", destination: "/dashboard#findings", permanent: false }];
  },
};

export default nextConfig;
