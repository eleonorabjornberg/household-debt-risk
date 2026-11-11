import { DraftBanner } from "@/components/pages/DraftBanner";
// /research (Eleonora, 2026-11-09): the project's quantitative write-ups on the live site, labelled as Claude drafts.
export default function ResearchLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <div className="pg research-banner-wrap">
        <DraftBanner testId="research-draft-banner" plural />
      </div>
      {children}
    </>
  );
}
