"use client";
import { useMemo } from "react";
import type { NyfedData } from "@/lib/shape";
import { LOAN_ORDER } from "@/lib/shape";
import { quarterLabel, quarterToYear } from "@/lib/format";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { DataTable, SLOT } from "./parts";

// Federal student-loan payment pause: 2020 Q1 (March 2020) to 2023 Q3 (payments resumed Oct 2023).
const PAUSE = { x0: 2020, x1: 2023.75 };

export function PaymentPriority({ data, labels, title }: { data: NyfedData; labels: Record<string, string>; title: string }) {
  const x = useMemo(() => data.dates.map(quarterToYear), [data.dates]);
  const xLabels = useMemo(() => data.dates.map(quarterLabel), [data.dates]);
  const types = LOAN_ORDER.filter((k) => data.transition[k].some((v) => v !== null));

  const hi = Math.max(1, ...types.flatMap((k) => data.transition[k].filter((v): v is number => v !== null)));
  const domain: [number, number] = [0, Math.ceil(hi / 5) * 5];

  // Order panels by average transition rate, highest first: who stops paying first.
  const ordered = [...types].sort((a, b) => avg(data.transition[b]) - avg(data.transition[a]));

  const rows = data.dates
    .map((d, i) => ({ d, i }))
    .filter(({ d }) => d.slice(5, 7) === "12" || d === data.dates[data.dates.length - 1])
    .map(({ d, i }) => [quarterLabel(d), ...ordered.map((k) => fmt(data.transition[k][i]))]);

  return (
    <div className="chart">
      <ol className="multiples multiples--three" aria-label={title}>
        {ordered.map((k) => {
          const series = [
            ...types.filter((o) => o !== k).map((o) => ({ key: o, label: labels[o] ?? o, color: "var(--muted-line)", values: data.transition[o], muted: true })),
            { key: k, label: labels[k] ?? k, color: SLOT[0], values: data.transition[k] },
          ];
          const last = [...data.transition[k]].reverse().find((v) => v !== null) ?? null;
          return (
            <li key={k} className="multiples__panel">
              <div className="multiples__head">
                <span className="multiples__name">{labels[k] ?? k}</span>
                <span className="multiples__delta">{fmt(last)}</span>
              </div>
              <div className="multiples__sub">Average {fmt(avg(data.transition[k]))} since {data.dates[0]?.slice(0, 4)}</div>
              <TimeSeriesChart
                compact
                x={x}
                xLabels={xLabels}
                series={series}
                mode="line"
                title={`${labels[k] ?? k}: share of balances moving into serious delinquency`}
                desc={`Latest ${fmt(last)} in ${xLabels[xLabels.length - 1]}. Other loan types shown in gray for comparison.`}
                yFormat={(v) => `${v}%`}
                valueFormat={(v) => `${v.toFixed(1)}%`}
                yDomain={domain}
                bands={k === "student" ? [{ ...PAUSE }] : []}
                xTicks={[2005, 2015, 2025]}
              />
            </li>
          );
        })}
      </ol>
      <DataTable
        caption={`${title}, fourth quarter of each year (percent of balance, annualized)`}
        columns={["Quarter", ...ordered.map((k) => labels[k] ?? k)]}
        rows={rows}
      />
    </div>
  );
}

function avg(vals: (number | null)[]) {
  const v = vals.filter((x): x is number => x !== null);
  return v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0;
}
function fmt(v: number | null) {
  return v === null ? "–" : `${v.toFixed(1)}%`;
}
