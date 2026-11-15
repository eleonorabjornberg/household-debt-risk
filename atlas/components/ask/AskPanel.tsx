"use client";
// Ask Hot Potato panel (PLAN D6; restyled in R1, 2026-11-15). Shows the answer and, under it (closed by default),
// every tool call it used, with series IDs and the data vintage. Example chips fill the box; they do not send.
import { useId, useRef, useState } from "react";
import { Markdown } from "@/components/Markdown";
import { parseMarkdown } from "@/lib/markdown";

type Source = { tool: string; args: Record<string, unknown>; ok: boolean; refused?: boolean; series_ids: string[];
                vintage: string | null; source: string | null };
type Result = { answer?: string; refused?: boolean; sources?: Source[]; error?: string };

export default function AskPanel({ examples = [], disabledMessage }: { examples?: { label: string; question: string }[]; disabledMessage?: string }) {
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
  const box = useRef<HTMLTextAreaElement>(null);
  const id = useId();
  // The model answers in Markdown (bold, lists). Render it as React elements: no raw HTML, only safe links.
  const answerBlocks = res?.answer ? parseMarkdown(res.answer) : [];
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setRes(null);
    try {
      const r = await fetch("/api/ask", { method: "POST", headers: { "content-type": "application/json" },
                                          body: JSON.stringify({ question: q }) });
      setRes(await r.json());
    } catch {
      setRes({ error: "Could not reach the server." });
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="ask">
      <form className="ask__card" onSubmit={submit}>
        <label htmlFor={`${id}-q`} className="ask__label sr-only">Your question</label>
        <textarea id={`${id}-q`} ref={box} value={q} maxLength={500} rows={3} onChange={(e) => setQ(e.target.value)}
                  disabled={!!disabledMessage} />
        {examples.length > 0 && (
          <div className="ask__chips" role="group" aria-label="Example questions">
            {examples.map((x) => (
              <button key={x.label} type="button" className="chip chip--q" disabled={!!disabledMessage} title={x.question}
                      onClick={() => { setQ(x.question); box.current?.focus(); }}>
                {x.label}
              </button>
            ))}
          </div>
        )}
        <div className="ask__actions">
          <button type="submit" className="btn btn--ask" disabled={busy || !q.trim() || !!disabledMessage}>
            {busy ? "Thinking…" : "Ask"}
          </button>
          {disabledMessage && <p role="status" className="ask__off">{disabledMessage}</p>}
        </div>
      </form>
      {res?.error && <p role="alert" className="ask__error"><strong>Something went wrong.</strong> {res.error}</p>}
      {res?.answer && (
        <div className={`ask__answer${res.refused ? " is-refused" : ""}`} aria-live="polite">
          <div className="ask__md"><Markdown blocks={answerBlocks} /></div>
          {!!res.sources?.length && (
            <details>
              <summary>Query and sources</summary>
              <ul>
                {res.sources.map((s, i) => (
                  <li key={i}>
                    <code>{s.tool}({JSON.stringify(s.args)})</code>
                    {s.refused ? " refused" : ""}
                    {s.source ? ` · ${s.source === "nyfed" ? "NY Fed CCP" : "Fed Z.1"}` : ""}
                    {s.vintage ? ` · vintage ${s.vintage}` : ""}
                    {s.series_ids?.length ? ` · ${s.series_ids.slice(0, 6).join(", ")}${s.series_ids.length > 6 ? ", …" : ""}` : ""}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
