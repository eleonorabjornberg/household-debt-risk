"use client";
// Ask Hot Potato panel (PLAN D6, preview only). Shows the answer and, under it, every tool call it used,
// with series IDs and the data vintage.
import { useState } from "react";

type Source = { tool: string; args: Record<string, unknown>; ok: boolean; refused?: boolean; series_ids: string[];
                vintage: string | null; source: string | null };
type Result = { answer?: string; refused?: boolean; sources?: Source[]; error?: string };

export default function AskPanel() {
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
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
    <section className="ask" aria-labelledby="ask-h">
      <h2 id="ask-h">Ask Hot Potato</h2>
      <p className="ask__note">Preview. Answers come only from the project&apos;s Z.1 and NY Fed data, with the query and data
        vintage shown. No forecasts. Five questions per visitor per day.</p>
      <form onSubmit={submit}>
        <label htmlFor="ask-q" className="ask__label">Your question</label>
        <textarea id="ask-q" value={q} maxLength={500} rows={3} onChange={(e) => setQ(e.target.value)}
                  placeholder="What share of household mortgages and consumer credit did public holders hold in 2007Q4?" />
        <button type="submit" disabled={busy || !q.trim()}>{busy ? "Thinking…" : "Ask"}</button>
      </form>
      {res?.error && <p role="alert" className="ask__error">{res.error}</p>}
      {res?.answer && (
        <div className="ask__answer" aria-live="polite">
          <p>{res.answer}</p>
          {!!res.sources?.length && (
            <details open>
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
    </section>
  );
}
