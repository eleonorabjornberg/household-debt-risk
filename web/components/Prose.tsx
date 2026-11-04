import { Sourced } from "@/components/claims/SourceRef";

export function Prose({ paragraphs }: { paragraphs: string[] }) {
  return (
    <div className="prose">
      {paragraphs.map((p, i) => (
        <p key={i}><Sourced text={p} /></p>
      ))}
    </div>
  );
}
