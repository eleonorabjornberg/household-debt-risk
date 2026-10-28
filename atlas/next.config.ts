import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // lib/data.ts falls back to these JSON snapshots at build and revalidation time.
  outputFileTracingIncludes: {
    "/": ["./public/data/**/*.json"],
    "/api/og": ["./public/data/**/*.json"],
  },
};

export default nextConfig;
