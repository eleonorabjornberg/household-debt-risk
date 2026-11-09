// Renders lib/markdown.ts blocks as React elements (no dangerouslySetInnerHTML).
import type { Block, Inline, ListBlock } from "@/lib/markdown";

function Inl({ c }: { c: Inline[] }) {
  return (
    <>
      {c.map((x, i) => {
        switch (x.t) {
          case "text": return <span key={i}>{x.v}</span>;
          case "code": return <code key={i}>{x.v}</code>;
          case "strong": return <strong key={i}><Inl c={x.c} /></strong>;
          case "em": return <em key={i}><Inl c={x.c} /></em>;
          case "link": {
            const safe = /^(https?:\/\/|\/|#)/.test(x.href);
            return safe ? <a key={i} href={x.href}><Inl c={x.c} /></a> : <span key={i}><Inl c={x.c} /></span>;
          }
        }
      })}
    </>
  );
}

/** Inline Markdown on its own (the /research index renders PLAN quotes with it). */
export function MarkdownInline({ c }: { c: Inline[] }) {
  return <Inl c={c} />;
}

function List({ b }: { b: ListBlock }) {
  const items = b.items.map((it, i) => (
    <li key={i}>
      <Inl c={it.body} />
      {it.children.map((ch, j) => <List key={j} b={ch} />)}
    </li>
  ));
  return b.ordered ? <ol start={b.start}>{items}</ol> : <ul>{items}</ul>;
}

export function Markdown({ blocks }: { blocks: Block[] }) {
  return (
    <>
      {blocks.map((b, i) => {
        switch (b.t) {
          case "heading": {
            const H = (b.level <= 1 ? "h1" : b.level === 2 ? "h2" : "h3") as "h1" | "h2" | "h3";
            return <H key={i} id={b.id}><Inl c={b.c} /></H>;
          }
          case "para": return <p key={i}><Inl c={b.c} /></p>;
          case "list": return <List key={i} b={b} />;
          case "table":
            return (
              <div key={i} className="tablewrap">
                <table>
                  <thead><tr>{b.head.map((h, j) => <th key={j} scope="col"><Inl c={h} /></th>)}</tr></thead>
                  <tbody>{b.rows.map((r, j) => <tr key={j}>{r.map((c, k) => <td key={k}><Inl c={c} /></td>)}</tr>)}</tbody>
                </table>
              </div>
            );
          case "fence":
            return <pre key={i} className="md-fence"><code>{b.text}</code></pre>;
          case "quote":
            return <blockquote key={i} className="md-quote"><Markdown blocks={b.blocks} /></blockquote>;
        }
      })}
    </>
  );
}
