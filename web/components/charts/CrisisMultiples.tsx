"use client";
import { useId, useMemo, useState } from "react";
import type { CrisisWindows } from "@/lib/shape";
import { pts, quarterLabel } from "@/lib/format";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { DataTable, SLOT } from "./parts";

interface Props {
  data: CrisisWindows;
  metricLabels: Record<string, string>;
  notes: Record<string, { label: string; text: string }>;
  title: string;
}

const isCoverage = (m: string) => m.startsWith("coverage:");

export function CrisisMultiples({ data, metricLabels, notes, title }: Props) {
  const selectId = useId();
  const metrics = data.metrics.length ? data.metrics : ["public_share"];
  const [metric, setMetric] = useState(metrics.includes("public_share") ? "public_share" : metrics[0]);

  const { panels, domain } = useMemo(() => {
    // Shares may arrive as 0-1 or 0-100; normalise to fractions so deltas print as points.
    const all = data.crises.flatMap((c) => (data.values[c.id]?.[metric] ?? []).filter((v): v is number => v !== null));
    const scale = !isCoverage(metric) && all.some((v) => Math.abs(v) > 1.5) ? 0.01 : 1;
    const panels = data.crises.map((c) => {
      const vals = data.values[c.id]?.[metric] ?? new Array(25).fill(null);
      const v0 = vals[8];
      const deltas = vals.map((v) => (v === null || v0 === null ? null : (v - v0) * scale));
      const end = [...deltas].reverse().find((d) => d !== null) ?? null;
      return { crisis: c, deltas, end };
    });
    const flat = panels.flatMap((p) => p.deltas.filter((d): d is number => d !== null));
    const lo = Math.min(0, ...flat);
    const hi = Math.max(0, ...flat);
    const pad = (hi - lo) * 0.08 || 0.01;
    return { panels, domain: [lo - pad, hi + pad] as [number, number] };
  }, [data, metric]);

  const fmt = isCoverage(metric)
    ? (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(1)}×`
    : (v: number) => (v === 0 ? "0" : `${v > 0 ? "+" : "−"}${Math.abs(v * 100).toFixed(0)}`);
  const fmtLong = isCoverage(metric)
    ? (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(2)}×`
    : (v: number) => pts(v, 1);
  const noteFor = (start: string) => notes[start.slice(0, 4)];
  const x = data.offsets;
  const xLabels = x.map((o) => (o === 0 ? "Crisis begins (t = 0)" : `${o > 0 ? "+" : "−"}${Math.abs(o)} quarters`));

  return (
    <div className="chart">
      <div className="chart__controls">
        <label className="select" htmlFor={selectId}>
          <span className="segmented__label">Metric</span>
          <select id={selectId} value={metric} onChange={(e) => setMetric(e.target.value)}>
            {metrics.map((m) => (
              <option key={m} value={m}>{metricLabels[m] ?? m}</option>
            ))}
          </select>
        </label>
      </div>
      <ol className="multiples" aria-label={title}>
        {panels.map(({ crisis, deltas, end }) => {
          const note = noteFor(crisis.start);
          const startLabel = quarterLabel(crisis.start);
          return (
            <li key={crisis.id} className="multiples__panel">
              <div className="multiples__head">
                <span className="multiples__name">{crisis.name}</span>
                <span className={`multiples__delta${end !== null && end < 0 ? " is-down" : ""}`}>
                  {end === null ? "–" : fmtLong(end)}
                </span>
              </div>
              <div className="multiples__sub">
                {startLabel}
                {crisis.kind === "policy_shock" ? " · policy shock" : ""}
              </div>
              <TimeSeriesChart
                compact
                x={x}
                xLabels={xLabels}
                mode="line"
                series={[{ key: crisis.id, label: metricLabels[metric] ?? metric, color: SLOT[0], values: deltas }]}
                title={`${crisis.name}: change in ${metricLabels[metric] ?? metric}`}
                desc={`Change from ${startLabel}, two years before to four years after. Ends at ${end === null ? "no data" : fmtLong(end)}.`}
                yFormat={fmt}
                valueFormat={fmtLong}
                yDomain={domain}
                xTicks={[-8, 0, 8, 16]}
                xTickFormat={(v) => (v === 0 ? "t0" : `${v > 0 ? "+" : "−"}${Math.abs(v) / 4}y`)}
                zeroLine
                markerX={0}
              />
              {note && <p className="multiples__note">{note.text}</p>}
            </li>
          );
        })}
      </ol>
      <DataTable
        caption={`Change in ${metricLabels[metric] ?? metric} from the quarter each crisis began`}
        columns={["Crisis", "Start", "−2 years", "+1 year", "+2 years", "+4 years"]}
        rows={panels.map(({ crisis, deltas }) => [
          crisis.name,
          quarterLabel(crisis.start),
          ...[0, 12, 16, 24].map((i) => (deltas[i] === null ? "–" : fmtLong(deltas[i] as number))),
        ])}
      />
    </div>
  );
}
