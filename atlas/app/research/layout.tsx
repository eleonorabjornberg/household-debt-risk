// /research (Eleonora, 2026-11-09): the project's quantitative write-ups on the live site, labelled as Claude drafts.
export default function ResearchLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <div className="pg research-banner-wrap">
        <div className="pg-banner" role="note" data-testid="research-draft-banner">
          <p style={{ margin: 0 }}>
            <strong>Claude drafts</strong>
            The research write-ups in this section were drafted by Claude for Eleonora to review and rewrite. They are
            not her text.
          </p>
        </div>
      </div>
      {children}
    </>
  );
}
