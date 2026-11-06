// Ask Hot Potato may run on preview deployments and in local dev only (her d6-preview; production needs her OK).
import { describe, expect, it } from "vitest";
import { deploymentGate } from "./gate";

const READY = { NEXT_PUBLIC_ASK_ENABLED: "1", HHDEBT_ANTHROPIC_API_KEY: "test-not-a-key",
                KV_REST_API_URL: "https://example.invalid", KV_REST_API_TOKEN: "test-not-a-token" } as Record<string, string | undefined>;

describe("deploymentGate", () => {
  it("refuses Vercel production even when everything else is configured", () => {
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "production", ...READY })).toMatchObject({ ok: false, status: 404 });
  });
  it("refuses a preview without a shared limit store, and without a key", () => {
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "preview", ...READY, KV_REST_API_URL: undefined }))
      .toMatchObject({ ok: false, status: 503 });
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "preview", ...READY, HHDEBT_ANTHROPIC_API_KEY: undefined }))
      .toMatchObject({ ok: false, status: 503 });
  });
  it("refuses when the preview flag is off", () => {
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "preview", ...READY, NEXT_PUBLIC_ASK_ENABLED: undefined }))
      .toMatchObject({ ok: false, status: 404 });
  });
  it("allows a configured preview and local development", () => {
    expect(deploymentGate({ VERCEL: "1", VERCEL_ENV: "preview", ...READY })).toEqual({ ok: true });
    expect(deploymentGate({ NODE_ENV: "development", ...READY, KV_REST_API_URL: undefined })).toEqual({ ok: true });
  });
  it("refuses a local production build unless explicitly allowed", () => {
    expect(deploymentGate({ NODE_ENV: "production", ...READY })).toMatchObject({ ok: false, status: 404 });
  });
});
