// "Claude draft" banner (CLAUDE.md authorship rule; Eleonora's banners-56, 2026-11-13).
// Stays on a page until she approves that page or replaces its text with her own.
export function DraftBanner({ testId = "draft-banner" }: { testId?: string }) {
  return (
    <div className="banner wrap" role="note" data-testid={testId}>
      <p className="banner__inner col-wide">
        <strong>Claude draft</strong>
        <span>This page and its text were drafted by Claude for Eleonora to review and rewrite. It is not her text yet.</span>
      </p>
    </div>
  );
}
