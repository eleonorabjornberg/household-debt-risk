import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Ask Hot Potato: the Anthropic client body, the tool arguments and the E1 gold file are untyped JSON at an API
  // boundary; these files read them as `any` on purpose (2026-11-15, after CI showed the rule failing the atlas job).
  {
    files: ["lib/ask/**", "scripts/ask-buildtest.ts"],
    rules: { "@typescript-eslint/no-explicit-any": "off" },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
