// One short "Claude draft" banner for every page (site review 2026-11-11). Authorship rule: Claude's text stays
// labelled until Eleonora approves the page.
export function DraftBanner({ testId, plural = false }: { testId: string; plural?: boolean }) {
  return (
    <div className="pg-banner" role="note" data-testid={testId}>
      <p style={{ margin: 0 }}>
        <strong>{plural ? "Claude drafts" : "Claude draft"}</strong>
        <span>for Eleonora&apos;s review</span>
      </p>
    </div>
  );
}
