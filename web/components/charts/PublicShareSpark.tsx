"use client";
import { useMemo } from "react";
import type { Crisis, PublicSeries } from "@/lib/shape";
import { pct, quarterLabel, quarterToYear } from "@/lib/format";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { crisisBands, SLOT } from "./parts";

export function PublicShareSpark({ data, crises, title }: { data: PublicSeries; crises: Crisis[]; title: string }) {
  const x = useMemo(() => data.dates.map(quarterToYear), [data.dates]);
  const xLabels = useMemo(() => data.dates.map(quarterLabel), [data.dates]);
  const bands = useMemo(() => crisisBands(crises, false), [crises]);
  const first = data.share[0];
  const last = data.share[data.share.length - 1];
  const decades = [];
  for (let y = Math.ceil(x[0] / 20) * 20; y <= x[x.length - 1]; y += 20) decades.push(y);
  return (
    <TimeSeriesChart
      x={x}
      xLabels={xLabels}
      series={[{ key: "public", label: "Public share", color: SLOT[0], values: data.share }]}
      mode="line"
      title={title}
      desc={`Line rising in steps from ${pct(first, 0)} in ${xLabels[0]} to ${pct(last, 1)} in ${xLabels[xLabels.length - 1]}. Shaded bands are recessions.`}
      yFormat={(v) => pct(v, 0)}
      valueFormat={(v) => pct(v, 1)}
      yDomain={[0, Math.max(0.6, Math.ceil(Math.max(...data.share) * 10) / 10)]}
      yTickCount={3}
      xTicks={decades}
      bands={bands}
      height={170}
      endLabel
    />
  );
}
