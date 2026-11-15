// One-line footer on every page (R1): data sources, claims register, Appendix, GitHub. Appendix and GitHub are linked
// from here only.
import Link from "next/link";
import { footer, site } from "@/content/story";

export function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer__row">
        <p>{footer.data}</p>
        <nav aria-label="Footer">
          <Link href="/sources">Claims register</Link>
          <Link href="/appendix">Appendix</Link>
          <a href={site.repo}>GitHub</a>
        </nav>
      </div>
    </footer>
  );
}
