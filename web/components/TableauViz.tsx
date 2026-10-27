"use client";
// Tableau Embedding API v3 (<tableau-viz>), for Tableau Public (no token) or Tableau Cloud
// (Connected Apps JWT from /api/tableau-token).
// Renders `fallback` (the native chart) on the server, while loading, and if anything fails
// (script won't load, token request fails, the viz fires a load error, or it never becomes
// interactive), so the page never
// depends on Tableau being reachable.
import { useEffect, useRef, useState, type ReactNode } from "react";
import { loadEmbeddingApi } from "@/lib/tableauControl";

interface Props {
  /** Embedding API v3 module URL. */
  scriptUrl: string;
  /** Full view URL, e.g. https://public.tableau.com/views/WhoHoldsTheDebt/Ratchet */
  src: string;
  /** Cloud: fetch a Connected Apps token first. Public: no token. */
  needsToken: boolean;
  title: string;
  height?: number;
  fallback: ReactNode;
}

type State = { status: "loading" } | { status: "ready"; token?: string } | { status: "error"; message: string };

// Embedding API v3 event names (TableauEventType).
const VIZ_LOAD_ERROR = "vizloaderror";
const FIRST_INTERACTIVE = "firstinteractive";
// A missing Tableau Public view loads a "Where's the viz?" page without firing vizloaderror,
// so a view that isn't interactive within this time is treated as failed.
const INTERACTIVE_TIMEOUT_MS = 30000;

export function TableauViz({ scriptUrl, src, needsToken, title, height = 680, fallback }: Props) {
  const [state, setState] = useState<State>({ status: "loading" });
  const vizRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (needsToken) {
          const [res] = await Promise.all([fetch("/api/tableau-token", { cache: "no-store" }), loadEmbeddingApi(scriptUrl)]);
          if (!res.ok) throw new Error(`Token request failed (${res.status})`);
          const { token } = (await res.json()) as { token: string };
          if (!cancelled) setState({ status: "ready", token });
        } else {
          await loadEmbeddingApi(scriptUrl);
          if (!cancelled) setState({ status: "ready" });
        }
      } catch (err) {
        if (!cancelled) setState({ status: "error", message: (err as Error).message });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [scriptUrl, needsToken]);

  const ready = state.status === "ready";
  useEffect(() => {
    const el = vizRef.current;
    if (!ready || !el) return;
    const onError = () => setState({ status: "error", message: "The Tableau view failed to load" });
    const timer = setTimeout(onError, INTERACTIVE_TIMEOUT_MS);
    const onInteractive = () => clearTimeout(timer);
    el.addEventListener(VIZ_LOAD_ERROR, onError);
    el.addEventListener(FIRST_INTERACTIVE, onInteractive);
    return () => {
      clearTimeout(timer);
      el.removeEventListener(VIZ_LOAD_ERROR, onError);
      el.removeEventListener(FIRST_INTERACTIVE, onInteractive);
    };
  }, [ready]);

  if (state.status === "ready") {
    return (
      <div className="tableau" style={{ minHeight: height }}>
        <tableau-viz
          ref={vizRef}
          src={src}
          {...(state.token ? { token: state.token } : {})}
          toolbar="bottom"
          hide-tabs
          width="100%"
          height={`${height}px`}
          aria-label={title}
        />
      </div>
    );
  }
  return (
    <>
      {fallback}
      {state.status === "error" && (
        <p className="figure__soon">The interactive Tableau version could not load, so the built-in chart is shown instead.</p>
      )}
    </>
  );
}
