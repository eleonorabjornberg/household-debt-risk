import { fixtureBanner } from "@/content/story";

export function FixtureBanner() {
  return (
    <div className="banner wrap" role="note">
      <p className="banner__inner col-wide">
        <strong>Fixture data</strong>
        <span>{fixtureBanner}</span>
      </p>
    </div>
  );
}
