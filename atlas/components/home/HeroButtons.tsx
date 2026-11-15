"use client";
// Hero buttons (R1): "Play the story" scrolls to the explorer and starts it from 1952.
import Link from "next/link";
import { hero } from "@/content/story";
import { PLAY_EVENT } from "../Experience";

export function HeroButtons() {
  return (
    <div className="hero__buttons">
      <a
        href="#explore"
        className="btn btn--home btn--icon-play"
        onClick={(e) => {
          e.preventDefault();
          const el = document.getElementById("explore");
          el?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
          window.dispatchEvent(new Event(PLAY_EVENT));
        }}
      >
        {hero.buttons.play}
      </a>
      <a href="#ask" className="btn btn--ask">{hero.buttons.ask}</a>
      <Link href="/how-it-was-built" className="btn btn--build">{hero.buttons.build}</Link>
    </div>
  );
}
