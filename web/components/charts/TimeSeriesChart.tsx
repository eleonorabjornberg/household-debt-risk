"use client";
// One hand-rolled SVG chart used for every native figure: stacked areas, lines and small multiples.
// Follows the dataviz mark specs: 2px lines, hairline solid grid, 2px surface gaps between stacked
// fills, >=8px end dots with a surface ring, crosshair + tooltip on hover, and keyboard stepping.
import { useCallback, useId, useMemo, useState, type KeyboardEvent, type PointerEvent } from "react";
import { niceMax, niceTicks, useWidth } from "./useWidth";

export interface Series {
  key: string;
  label: string;
  color: string;
  values: (number | null)[];
  /** Drawn in gray behind the highlighted series and left out of the tooltip. */
  muted?: boolean;
}

export interface Band {
  x0: number;
  x1: number;
  label?: string;
  /** "rule" draws a single vertical line at x0 (policy shocks). */
  kind?: "band" | "rule";
}

export interface TimeSeriesChartProps {
  x: number[];
  /** Tooltip heading for each index, e.g. "2007 Q4". */
  xLabels: string[];
  series: Series[];
  mode: "line" | "stack";
  title: string;
  desc: string;
  yFormat: (v: number) => string;
  /** Tooltip value format; defaults to yFormat. */
  valueFormat?: (v: number) => string;
  yDomain?: [number, number];
  yTickCount?: number;
  xTicks?: number[];
  xTickFormat?: (v: number) => string;
  bands?: Band[];
  /** In stack mode: draw a heavy rule above the first N series (the public/private line). */
  boundaryAfter?: number;
  boundaryLabel?: (value: number) => string;
  /** Total line in the tooltip (stack mode). */
  totalLabel?: string;
  height?: number;
  compact?: boolean;
  zeroLine?: boolean;
  /** Label the last value of the first highlighted series at the right edge. */
  endLabel?: boolean;
  /** Vertical rule at this x (e.g. t = 0 in crisis windows). */
  markerX?: number;
}

const SURFACE = "var(--surface)";

function bisect(xs: number[], x: number): number {
  let lo = 0;
  let hi = xs.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (xs[mid] < x) lo = mid;
    else hi = mid;
  }
  return Math.abs(xs[lo] - x) <= Math.abs(xs[hi] - x) ? lo : hi;
}

export function TimeSeriesChart(props: TimeSeriesChartProps) {
  const {
    x, xLabels, series, mode, title, desc, yFormat, valueFormat = yFormat, bands = [], compact = false,
    zeroLine = false, endLabel = false, boundaryAfter, boundaryLabel, totalLabel, markerX,
  } = props;
  const uid = useId();
  const [wrapRef, width] = useWidth<HTMLDivElement>(compact ? 280 : 720);
  const [hover, setHover] = useState<number | null>(null);

  const narrow = width < 520;
  const height = props.height ?? (compact ? 150 : Math.round(Math.max(260, Math.min(440, width * 0.56))));
  const hasRightLabel = (endLabel || boundaryLabel) && !compact;
  // Reserve right margin for the end label from its actual text (~7.2px per char at 12px bold).
  const rightText = !hasRightLabel
    ? ""
    : boundaryLabel && boundaryAfter
      ? boundaryLabel(series.slice(0, boundaryAfter).reduce((s, se) => s + (se.values[x.length - 1] ?? 0), 0))
      : (() => {
          const s0 = series.find((s) => !s.muted);
          const v = s0 ? [...s0.values].reverse().find((v) => v !== null) : null;
          return v === null || v === undefined ? "" : valueFormat(v);
        })();
  const m = {
    top: compact ? 8 : bands.some((b) => b.label) && !narrow ? 26 : 12,
    right: hasRightLabel ? Math.ceil(rightText.length * 7.2) + 14 : compact ? 14 : 12,
    bottom: compact ? 20 : 26,
    left: compact ? 38 : 44,
  };
  const iw = Math.max(10, width - m.left - m.right);
  const ih = Math.max(10, height - m.top - m.bottom);

  // ---- stack / y-domain --------------------------------------------------------
  const stacked = useMemo(() => {
    if (mode !== "stack") return null;
    const lower: number[][] = [];
    const upper: number[][] = [];
    const acc = new Array(x.length).fill(0);
    for (const s of series) {
      lower.push([...acc]);
      for (let i = 0; i < x.length; i++) acc[i] += s.values[i] ?? 0;
      upper.push([...acc]);
    }
    return { lower, upper, total: acc as number[] };
  }, [mode, series, x.length]);

  const [y0, y1] = useMemo<[number, number]>(() => {
    if (props.yDomain) return props.yDomain;
    if (stacked) return [0, niceMax(Math.max(...stacked.total), props.yTickCount ?? 4)];
    let lo = Infinity;
    let hi = -Infinity;
    for (const s of series) for (const v of s.values) if (v !== null && Number.isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    if (!Number.isFinite(lo)) return [0, 1];
    if (lo > 0) lo = 0;
    return [lo, hi];
  }, [props.yDomain, props.yTickCount, stacked, series]);

  const yTicks = useMemo(() => niceTicks(y0, y1, props.yTickCount ?? (compact ? 3 : 4)), [y0, y1, props.yTickCount, compact]);
  const yMin = Math.min(y0, yTicks[0]);
  const yMax = Math.max(y1, yTicks[yTicks.length - 1]);

  const xMin = x[0];
  const xMax = x[x.length - 1];
  const sx = useCallback((v: number) => m.left + ((v - xMin) / (xMax - xMin || 1)) * iw, [m.left, xMin, xMax, iw]);
  const sy = useCallback((v: number) => m.top + ih - ((v - yMin) / (yMax - yMin || 1)) * ih, [m.top, ih, yMin, yMax]);

  const xTicks = useMemo(() => {
    if (props.xTicks) return props.xTicks;
    const span = xMax - xMin;
    const target = compact ? 3 : narrow ? 4 : 8;
    const step = [1, 2, 5, 10, 20, 25, 50].find((s) => span / s <= target) ?? 50;
    const out: number[] = [];
    for (let v = Math.ceil(xMin / step) * step; v <= xMax; v += step) out.push(v);
    return out;
  }, [props.xTicks, xMin, xMax, compact, narrow]);
  const xTickFormat = props.xTickFormat ?? ((v: number) => String(Math.round(v)));

  // ---- paths --------------------------------------------------------------------
  const linePath = (vals: (number | null)[]) => {
    let d = "";
    let pen = false;
    vals.forEach((v, i) => {
      if (v === null || !Number.isFinite(v)) { pen = false; return; }
      d += `${pen ? "L" : "M"}${sx(x[i]).toFixed(1)},${sy(v).toFixed(1)}`;
      pen = true;
    });
    return d;
  };
  const areaPath = (lo: number[], up: number[]) => {
    let d = "";
    for (let i = 0; i < x.length; i++) d += `${i ? "L" : "M"}${sx(x[i]).toFixed(1)},${sy(up[i]).toFixed(1)}`;
    for (let i = x.length - 1; i >= 0; i--) d += `L${sx(x[i]).toFixed(1)},${sy(lo[i]).toFixed(1)}`;
    return d + "Z";
  };

  // ---- interaction ----------------------------------------------------------------
  const onMove = (e: PointerEvent<SVGRectElement>) => {
    const rect = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * width;
    const xv = xMin + ((px - m.left) / iw) * (xMax - xMin);
    setHover(bisect(x, xv));
  };
  const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
    const step = e.shiftKey ? 4 : 1;
    if (e.key === "ArrowRight") { setHover((h) => Math.min(x.length - 1, (h ?? -1) + step)); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { setHover((h) => Math.max(0, (h ?? x.length) - step)); e.preventDefault(); }
    else if (e.key === "Home") { setHover(0); e.preventDefault(); }
    else if (e.key === "End") { setHover(x.length - 1); e.preventDefault(); }
    else if (e.key === "Escape") setHover(null);
  };

  const highlighted = series.filter((s) => !s.muted);
  const last = x.length - 1;
  const lastValueOf = (s: Series) => {
    for (let i = s.values.length - 1; i >= 0; i--) if (s.values[i] !== null) return { i, v: s.values[i] as number };
    return null;
  };

  const bandEls = (fill: string, rule: string) =>
    bands.map((b, i) =>
      b.kind === "rule" ? (
        <line key={`b${i}`} x1={sx(b.x0)} x2={sx(b.x0)} y1={m.top} y2={m.top + ih} stroke={rule} strokeWidth={1} />
      ) : (
        <rect
          key={`b${i}`}
          x={sx(Math.max(b.x0, xMin))}
          y={m.top}
          width={Math.max(2, sx(Math.min(b.x1, xMax)) - sx(Math.max(b.x0, xMin)))}
          height={ih}
          fill={fill}
        />
      ),
    );

  // crisis band labels, skipping ones that would collide
  const bandLabels: { x: number; text: string }[] = [];
  if (!compact && !narrow) {
    let lastX = -Infinity;
    for (const b of bands) {
      if (!b.label) continue;
      const bx = sx(b.x0);
      if (bx - lastX < 34 || bx < m.left || bx > width - m.right) continue;
      bandLabels.push({ x: bx, text: b.label });
      lastX = bx;
    }
  }

  const tooltipRows =
    hover === null
      ? []
      : (mode === "stack" ? [...highlighted].reverse() : highlighted).map((s) => ({ s, v: s.values[hover] }));
  const hoverX = hover === null ? 0 : sx(x[hover]);
  const tipLeft = hoverX > width / 2;

  const titleId = `${uid}-t`;
  const descId = `${uid}-d`;

  return (
    <div
      ref={wrapRef}
      className={`tsc${compact ? " tsc--compact" : ""}`}
      tabIndex={0}
      onKeyDown={onKey}
      onBlur={() => setHover(null)}
      aria-label={`${title}. Interactive chart: use the left and right arrow keys to read values.`}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-labelledby={`${titleId} ${descId}`}
        className="tsc__svg"
      >
        <title id={titleId}>{title}</title>
        <desc id={descId}>{desc}</desc>

        {mode === "line" && bandEls("var(--band)", "var(--muted)")}
        {bandLabels.map((l, i) => (
          <text key={i} x={l.x} y={m.top - 9} className="tsc__bandlabel" fill="var(--muted)">
            {l.text}
          </text>
        ))}

        {/* grid + y axis */}
        {yTicks.map((t) => (
          <g key={t}>
            <line x1={m.left} x2={m.left + iw} y1={sy(t)} y2={sy(t)} stroke={t === 0 && zeroLine ? "var(--axis)" : "var(--grid)"} strokeWidth={1} />
            <text x={m.left - 6} y={sy(t)} dy="0.32em" textAnchor="end" className="tsc__tick" fill="var(--muted)">
              {yFormat(t)}
            </text>
          </g>
        ))}
        {/* x axis */}
        <line x1={m.left} x2={m.left + iw} y1={m.top + ih} y2={m.top + ih} stroke="var(--axis)" strokeWidth={1} />
        {xTicks.map((t) => (
          <text key={t} x={sx(t)} y={m.top + ih + (compact ? 14 : 18)} textAnchor="middle" className="tsc__tick" fill="var(--muted)">
            {xTickFormat(t)}
          </text>
        ))}
        {markerX !== undefined && (
          <line x1={sx(markerX)} x2={sx(markerX)} y1={m.top} y2={m.top + ih} stroke="var(--ink-2)" strokeWidth={1} />
        )}

        {/* data */}
        {stacked &&
          series.map((s, k) => (
            <path
              key={s.key}
              d={areaPath(stacked.lower[k], stacked.upper[k])}
              fill={s.color}
              fillOpacity={0.8}
              stroke={SURFACE}
              strokeWidth={1.5}
              strokeLinejoin="round"
            />
          ))}
        {stacked && bandEls("var(--band-over)", "var(--band-over-rule)")}
        {stacked && boundaryAfter !== undefined && boundaryAfter > 0 && (
          <path d={linePath(stacked.upper[boundaryAfter - 1])} fill="none" stroke="var(--ink)" strokeWidth={2} strokeLinejoin="round" />
        )}
        {stacked && boundaryAfter !== undefined && boundaryLabel && !compact && (
          <text
            x={sx(x[last]) + 6}
            y={sy(stacked.upper[boundaryAfter - 1][last])}
            dy="0.32em"
            className="tsc__endlabel"
            fill="var(--ink)"
          >
            {boundaryLabel(stacked.upper[boundaryAfter - 1][last])}
          </text>
        )}

        {mode === "line" &&
          [...series.filter((s) => s.muted), ...highlighted].map((s) => (
            <path
              key={s.key}
              d={linePath(s.values)}
              fill="none"
              stroke={s.muted ? "var(--muted-line)" : s.color}
              strokeWidth={s.muted ? 1.25 : 2}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          ))}
        {mode === "line" &&
          highlighted.map((s) => {
            const lv = lastValueOf(s);
            if (!lv) return null;
            return <circle key={s.key} cx={sx(x[lv.i])} cy={sy(lv.v)} r={compact ? 3.5 : 4} fill={s.color} stroke={SURFACE} strokeWidth={2} />;
          })}
        {mode === "line" && endLabel && !compact && highlighted[0] && (() => {
          const lv = lastValueOf(highlighted[0]);
          return lv ? (
            <text x={sx(x[lv.i]) + 8} y={sy(lv.v)} dy="0.32em" className="tsc__endlabel" fill="var(--ink)">
              {valueFormat(lv.v)}
            </text>
          ) : null;
        })()}

        {/* hover */}
        {hover !== null && (
          <g pointerEvents="none">
            <line x1={hoverX} x2={hoverX} y1={m.top} y2={m.top + ih} stroke="var(--ink-2)" strokeWidth={1} />
            {mode === "line" &&
              highlighted.map((s) =>
                s.values[hover] === null ? null : (
                  <circle key={s.key} cx={hoverX} cy={sy(s.values[hover] as number)} r={4} fill={s.color} stroke={SURFACE} strokeWidth={2} />
                ),
              )}
          </g>
        )}
        <rect
          x={m.left}
          y={m.top}
          width={iw}
          height={ih}
          fill="transparent"
          onPointerMove={onMove}
          onPointerDown={onMove}
          onPointerLeave={() => setHover(null)}
          style={{ touchAction: "pan-y" }}
        />
      </svg>

      {hover !== null && (
        <div
          className="tsc__tip"
          role="status"
          aria-live="polite"
          style={{
            top: m.top + 4,
            ...(tipLeft ? { right: width - hoverX + 10 } : { left: hoverX + 10 }),
          }}
        >
          <div className="tsc__tiphead">{xLabels[hover]}</div>
          {tooltipRows.map(({ s, v }) => (
            <div key={s.key} className="tsc__tiprow">
              <span className="tsc__key" style={{ background: s.color }} aria-hidden="true" />
              <span className="tsc__tiplabel">{s.label}</span>
              <span className="tsc__tipval">{v === null || v === undefined ? "–" : valueFormat(v)}</span>
            </div>
          ))}
          {stacked && totalLabel && (
            <div className="tsc__tiprow tsc__tiprow--total">
              <span className="tsc__key" aria-hidden="true" />
              <span className="tsc__tiplabel">{totalLabel}</span>
              <span className="tsc__tipval">
                {valueFormat(
                  boundaryAfter ? stacked.upper[boundaryAfter - 1][hover] : stacked.total[hover],
                )}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
