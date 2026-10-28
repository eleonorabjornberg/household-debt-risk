"use client";

// The canvas. Owns the animation loop: it walks its own playhead one quarter at a time toward
// `target` (so a long jump replays the history instead of teleporting), and springs each dot to
// its slot in the current quarter's pile. React only passes props; everything per-frame lives
// in refs so scrolling never re-renders the canvas.
import { useEffect, useRef } from "react";
import { computeLayout, slotPosition, type Layout } from "@/lib/layout";
import type { Timeline } from "@/lib/timeline";

export interface PileLabel {
  name: string;
  value: string;
}

interface Props {
  timeline: Timeline;
  target: number;
  reducedMotion: boolean;
  labels: (frame: number) => PileLabel[];
  onFrame: (frame: number) => void;
  onHover: (hit: { pile: number; x: number; y: number } | null) => void;
  ariaLabel: string;
}

const STIFFNESS = 70;
const DAMPING = 13;
const MAX_STAGGER = 0.45;

interface Theme {
  piles: string[];
  ink: string;
  muted: string;
  rule: string;
  font: string;
}

function readTheme(el: HTMLElement): Theme {
  const cs = getComputedStyle(el);
  const v = (name: string) => cs.getPropertyValue(name).trim();
  return {
    piles: [0, 1, 2, 3, 4, 5].map((i) => v(`--pile-${i}`) || "#888"),
    ink: v("--ink") || "#eee",
    muted: v("--muted") || "#999",
    rule: v("--rule") || "#444",
    font: cs.fontFamily || "sans-serif",
  };
}

/** Cheap deterministic hash in [0, 1). */
function hash01(n: number): number {
  const x = Math.sin(n * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}

export default function DotStage({ timeline, target, reducedMotion, labels, onFrame, onHover, ariaLabel }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const props = useRef({ timeline, target, reducedMotion, labels, onFrame, onHover });
  const wakeRef = useRef<() => void>(() => {});

  useEffect(() => {
    props.current = { timeline, target, reducedMotion, labels, onFrame, onHover };
    wakeRef.current();
  });

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const tl = timeline;
    const n = tl.nDots;
    const x = new Float32Array(n);
    const y = new Float32Array(n);
    const vx = new Float32Array(n);
    const vy = new Float32Array(n);
    const alpha = new Float32Array(n);
    const delay = new Float32Array(n);
    const pile = new Int8Array(n).fill(-1); // pile the dot is heading to (or -1 when dying)
    const shown = new Int8Array(n).fill(-1); // pile whose colour it wears
    const tx = new Float32Array(n);
    const ty = new Float32Array(n);

    let width = 0;
    let height = 0;
    let dpr = 1;
    let layout: Layout | null = null;
    let theme = readTheme(canvas);
    let playhead = Math.max(0, Math.min(tl.frames.length - 1, props.current.target));
    let frame = -1;
    let raf = 0;
    let last = 0;
    let hoverPile = -1;

    function setTargets(snap: boolean) {
      if (!layout) return;
      const f = tl.frames[frame];
      const sl = tl.slots[frame];
      for (let id = 0; id < n; id++) {
        const b = f[id];
        if (b >= 0) {
          const c = layout.centers[b];
          const [px, py] = slotPosition(c.x, c.y, sl[id], layout.spacing);
          tx[id] = px;
          ty[id] = py;
          if (alpha[id] <= 0.01 && pile[id] < 0) {
            // Born: appear in place.
            x[id] = px;
            y[id] = py;
            vx[id] = vy[id] = 0;
            shown[id] = b;
          } else if (pile[id] !== b && pile[id] >= 0 && !snap) {
            delay[id] = hash01(id + frame * 7.13) * MAX_STAGGER;
          }
        }
        pile[id] = b;
        if (snap) {
          if (b >= 0) {
            x[id] = tx[id];
            y[id] = ty[id];
            vx[id] = vy[id] = 0;
            shown[id] = b;
            alpha[id] = 1;
          } else alpha[id] = 0;
          delay[id] = 0;
        }
      }
    }

    function goTo(f: number, snap: boolean) {
      if (f === frame) return;
      frame = f;
      setTargets(snap);
      props.current.onFrame(f);
    }

    function resize() {
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(2, window.devicePixelRatio || 1);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      layout = computeLayout(width, height, tl.maxCounts);
      if (frame < 0) {
        // First layout: place every dot, then let them fade in (unless motion is reduced).
        frame = Math.round(playhead);
        setTargets(true);
        if (!props.current.reducedMotion) alpha.fill(0);
        props.current.onFrame(frame);
      } else setTargets(false);
      draw();
      wake();
    }

    function step(dt: number): boolean {
      const { target: T, reducedMotion: rm } = props.current;
      let busy = false;
      if (rm) {
        playhead = T;
        goTo(T, true);
      } else if (playhead !== T) {
        const dist = T - playhead;
        const speed = Math.min(60, Math.max(7, Math.abs(dist) * 2.5)); // quarters per second
        const move = Math.sign(dist) * Math.min(Math.abs(dist), speed * dt);
        playhead += move;
        goTo(Math.round(playhead), false);
        busy = true;
      }
      for (let id = 0; id < n; id++) {
        const alive = pile[id] >= 0;
        const goal = alive ? 1 : 0;
        if (alpha[id] !== goal) {
          alpha[id] = goal > alpha[id] ? Math.min(1, alpha[id] + dt * 3) : Math.max(0, alpha[id] - dt * 2.5);
          busy = true;
        }
        if (!alive) continue;
        if (delay[id] > 0) {
          delay[id] -= dt;
          busy = true;
          continue;
        }
        shown[id] = pile[id];
        const ax = STIFFNESS * (tx[id] - x[id]) - DAMPING * vx[id];
        const ay = STIFFNESS * (ty[id] - y[id]) - DAMPING * vy[id];
        vx[id] += ax * dt;
        vy[id] += ay * dt;
        x[id] += vx[id] * dt;
        y[id] += vy[id] * dt;
        if (Math.abs(tx[id] - x[id]) > 0.05 || Math.abs(ty[id] - y[id]) > 0.05 || Math.abs(vx[id]) + Math.abs(vy[id]) > 0.1) busy = true;
        else {
          x[id] = tx[id];
          y[id] = ty[id];
          vx[id] = vy[id] = 0;
        }
      }
      return busy;
    }

    function draw() {
      if (!layout) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      const r = layout.dotRadius;

      // Public | private divider.
      ctx.font = `700 11px ${theme.font}`;
      ctx.letterSpacing = "0.12em";
      ctx.fillStyle = theme.ink;
      ctx.lineWidth = 2;
      if (layout.dividerX !== null) {
        ctx.strokeStyle = theme.rule;
        ctx.setLineDash([8, 6]);
        ctx.beginPath();
        ctx.moveTo(layout.dividerX, 16);
        ctx.lineTo(layout.dividerX, height - 16);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.textAlign = "right";
        ctx.fillText("← PUBLIC", layout.dividerX - 12, 24);
        ctx.textAlign = "left";
        ctx.fillText("PRIVATE →", layout.dividerX + 12, 24);
      } else if (layout.dividerY !== null) {
        ctx.strokeStyle = theme.rule;
        ctx.setLineDash([8, 6]);
        ctx.beginPath();
        ctx.moveTo(12, layout.dividerY);
        ctx.lineTo(width - 12, layout.dividerY);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.textAlign = "left";
        ctx.fillText("↑ PUBLIC", 12, layout.dividerY - 8);
        ctx.fillText("↓ PRIVATE", 12, layout.dividerY + 18);
      }
      ctx.letterSpacing = "0px";

      // Hover halo.
      if (hoverPile >= 0 && frame >= 0) {
        const c = layout.centers[hoverPile];
        const rr = layout.spacing * Math.sqrt(tl.counts[frame][hoverPile] + 0.5) + r + 6;
        ctx.strokeStyle = theme.ink;
        ctx.globalAlpha = 1;
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.arc(c.x, c.y, rr, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Overprint like riso ink where dots and streaks cross.
      ctx.globalCompositeOperation = "multiply";

      // Motion streaks for dots in flight.
      ctx.lineCap = "round";
      for (let id = 0; id < n; id++) {
        if (alpha[id] <= 0 || shown[id] < 0) continue;
        const sp = Math.abs(vx[id]) + Math.abs(vy[id]);
        if (sp < 60) continue;
        ctx.strokeStyle = theme.piles[shown[id]];
        ctx.globalAlpha = 0.28 * alpha[id];
        ctx.lineWidth = r * 1.4;
        ctx.beginPath();
        ctx.moveTo(x[id], y[id]);
        ctx.lineTo(x[id] - vx[id] * 0.07, y[id] - vy[id] * 0.07);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // Dots, batched by colour and type. Fading dots are drawn one by one.
      for (let b = 0; b < theme.piles.length; b++) {
        ctx.fillStyle = theme.piles[b];
        ctx.strokeStyle = theme.piles[b];
        ctx.beginPath();
        for (let id = 0; id < n; id++) {
          if (shown[id] !== b || alpha[id] < 1 || tl.dotType[id] !== 0) continue;
          ctx.moveTo(x[id] + r, y[id]);
          ctx.arc(x[id], y[id], r, 0, Math.PI * 2);
        }
        ctx.fill();
        ctx.lineWidth = Math.max(0.8, r * 0.42);
        const rr = r - ctx.lineWidth / 2;
        ctx.beginPath();
        for (let id = 0; id < n; id++) {
          if (shown[id] !== b || alpha[id] < 1 || tl.dotType[id] !== 1) continue;
          ctx.moveTo(x[id] + rr, y[id]);
          ctx.arc(x[id], y[id], rr, 0, Math.PI * 2);
        }
        ctx.stroke();
      }
      for (let id = 0; id < n; id++) {
        if (alpha[id] <= 0 || alpha[id] >= 1 || shown[id] < 0) continue;
        ctx.globalAlpha = alpha[id];
        const scale = 0.5 + 0.5 * alpha[id];
        ctx.fillStyle = ctx.strokeStyle = theme.piles[shown[id]];
        ctx.beginPath();
        if (tl.dotType[id] === 0) {
          ctx.arc(x[id], y[id], r * scale, 0, Math.PI * 2);
          ctx.fill();
        } else {
          ctx.lineWidth = Math.max(0.8, r * 0.42);
          ctx.arc(x[id], y[id], (r - ctx.lineWidth / 2) * scale, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = "source-over";

      // Labels under each pile, with an ink swatch.
      if (frame >= 0) {
        const lines = props.current.labels(frame);
        ctx.textAlign = "center";
        lines.forEach((l, i) => {
          const c = layout!.centers[i];
          ctx.font = `700 ${layout!.fontSize}px ${theme.font}`;
          const w = ctx.measureText(l.name).width;
          const sw = layout!.fontSize - 2;
          if (layout!.fontSize >= 12) {
            ctx.fillStyle = theme.piles[i];
            ctx.fillRect(c.x - w / 2 - sw - 5, layout!.labelY[i] - sw, sw, sw);
          }
          ctx.fillStyle = theme.ink;
          ctx.fillText(l.name, c.x, layout!.labelY[i]);
          ctx.fillStyle = theme.muted;
          ctx.font = `400 ${layout!.fontSize}px ${theme.font}`;
          ctx.fillText(l.value, c.x, layout!.labelY[i] + layout!.fontSize + 4);
        });
      }
    }

    function loop(now: number) {
      const dt = Math.min(0.05, last ? (now - last) / 1000 : 1 / 60);
      last = now;
      const busy = step(dt);
      draw();
      raf = busy ? requestAnimationFrame(loop) : 0;
      if (!busy) last = 0;
    }

    function wake() {
      if (!raf) raf = requestAnimationFrame(loop);
    }
    wakeRef.current = wake;

    function hitTest(ev: PointerEvent) {
      if (!layout || frame < 0) return;
      const rect = canvas.getBoundingClientRect();
      const px = ev.clientX - rect.left;
      const py = ev.clientY - rect.top;
      let hit = -1;
      layout.centers.forEach((c, i) => {
        const rr = Math.max(26, layout!.spacing * Math.sqrt(tl.counts[frame][i] + 0.5) + 10);
        if (Math.hypot(px - c.x, py - c.y) <= rr) hit = i;
      });
      if (hit !== hoverPile) {
        hoverPile = hit;
        draw();
      }
      props.current.onHover(hit >= 0 ? { pile: hit, x: px, y: py } : null);
    }
    function leave() {
      hoverPile = -1;
      draw();
      props.current.onHover(null);
    }

    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const retheme = () => {
      theme = readTheme(canvas);
      draw();
    };
    mq.addEventListener("change", retheme);
    canvas.addEventListener("pointermove", hitTest);
    canvas.addEventListener("pointerdown", hitTest);
    canvas.addEventListener("pointerleave", leave);
    document.fonts?.ready.then(retheme);
    resize();
    wake();

    return () => {
      cancelAnimationFrame(raf);
      raf = 0;
      wakeRef.current = () => {};
      ro.disconnect();
      mq.removeEventListener("change", retheme);
      canvas.removeEventListener("pointermove", hitTest);
      canvas.removeEventListener("pointerdown", hitTest);
      canvas.removeEventListener("pointerleave", leave);
    };
  }, [timeline]);

  return <canvas ref={canvasRef} className="stage__canvas" role="img" aria-label={ariaLabel} />;
}
