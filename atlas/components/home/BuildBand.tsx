// "Built with Claude" band on the home page (R1): the six capability tiles from content/build.ts, each linking to its
// folder in the repository, and one link to /how-it-was-built.
import Link from "next/link";
import { build, REPO_TREE } from "@/content/build";

export function BuildTiles() {
  return (
    <ul className="tiles">
      {build.tiles.map((t) => (
        <li key={t.name}>
          <a className="tile" href={`${REPO_TREE}/${t.href}`}>
            <strong>{t.name}</strong>
            <span>{t.body}</span>
          </a>
        </li>
      ))}
    </ul>
  );
}

export function BuildBand() {
  return (
    <section className="band band--build" aria-labelledby="build-h">
      <div className="wrap">
        <h2 id="build-h">Built with Claude</h2>
        <BuildTiles />
        <p className="band__more"><Link href="/how-it-was-built">How it was built →</Link></p>
      </div>
    </section>
  );
}
