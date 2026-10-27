"use client";
// Tableau Embedding API v3 (<tableau-viz>) with Connected Apps auth.
// Renders `fallback` (the native chart) on the server, while loading, and if anything fails,
// so the page never depends on Tableau being reachable.
import { useEffect, useState, type ReactNode } from "react";

let scriptPromise: Promise<void> | null = null;

function loadEmbeddingApi(serverUrl: string): Promise<void> {
  if (typeof window !== "undefined" && window.customElements?.get("tableau-viz")) return Promise.resolve();
  if (!scriptPromise) {
    scriptPromise = new Promise<void>((resolve, reject) => {
      const s = document.createElement("script");
      s.type = "module";
      s.src = `${serverUrl}/javascripts/api/tableau.embedding.3.latest.min.js`;
      s.onload = () => resolve();
      s.onerror = () => {
        scriptPromise = null;
        s.remove();
        reject(new Error("Could not load the Tableau Embedding API"));
      };
      document.head.appendChild(s);
    });
  }
  return scriptPromise;
}

interface Props {
  serverUrl: string;
  /** Full view URL, e.g. https://pod.online.tableau.com/t/site/views/WhoHoldsTheDebt/Ratchet */
  src: string;
  title: string;
  height?: number;
  fallback: ReactNode;
}

type State = { status: "loading" } | { status: "ready"; token: string } | { status: "error"; message: string };

export function TableauViz({ serverUrl, src, title, height = 680, fallback }: Props) {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [res] = await Promise.all([fetch("/api/tableau-token", { cache: "no-store" }), loadEmbeddingApi(serverUrl)]);
        if (!res.ok) throw new Error(`Token request failed (${res.status})`);
        const { token } = (await res.json()) as { token: string };
        if (!cancelled) setState({ status: "ready", token });
      } catch (err) {
        if (!cancelled) setState({ status: "error", message: (err as Error).message });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [serverUrl]);

  if (state.status === "ready") {
    return (
      <div className="tableau" style={{ minHeight: height }}>
        <tableau-viz src={src} token={state.token} toolbar="bottom" hide-tabs width="100%" height={`${height}px`} aria-label={title} />
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
