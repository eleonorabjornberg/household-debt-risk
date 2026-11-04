import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // lib/data.ts reads JSON from disk at runtime (ISR revalidation), so ship those files with the
  // server bundle.
  outputFileTracingIncludes: {
    "/": ["./public/data/**/*.json", "./fixtures/**/*.json"],
    "/methods": ["./public/data/**/*.json", "./fixtures/**/*.json"],
    "/data": ["./public/data/**/*.json", "./public/downloads/v1/index.json"],
  },
};

export default nextConfig;
