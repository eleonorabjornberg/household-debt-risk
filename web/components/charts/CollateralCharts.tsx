"use client";
import { useMemo } from "react";
import type { CollateralData, Crisis } from "@/lib/shape";
import { COLLATERAL_ORDER } from "@/lib/shape";
import { pct, quarterLabel, quarterToYear, ratio } from "@/lib/format";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { crisisBands, DataTable, Legend } from "./parts";

export function CollateralCharts({
  data, crises, labels, title,
}: { data: CollateralData; crises: Crisis[]; labels: Record<string, string>; title: string }) {
  const x = useMemo(() => data.dates.map(quarterToYear), [data.dates]);
  const xLabels = useMemo(() => data.dates.map(quarterLabel), [data.dates]);
  const bands = useMemo(() => crisisBands(crises, false), [crises]);

  const shareSeries = COLLATERAL_ORDER.map((k) => ({ key: k, label: labels[k] ?? k, color: `var(--c-${k})`, values: data.share[k] }));
  const covSeries = COLLATERAL_ORDER.filter((k) => data.coverage[k].some((v) => v !== null)).map((k) => ({
    key: k,
    label: labels[k] ?? k,
    color: `var(--c-${k})`,
    values: data.coverage[k],
  }));

  const rows = data.dates
    .map((d, i) => ({ d, i }))
    .filter(({ d }) => d.slice(5, 7) === "12" || d === data.dates[data.dates.length - 1])
    .map(({ d, i }) => [
      quarterLabel(d),
      ...COLLATERAL_ORDER.map((k) => pct(data.share[k][i])),
      ...covSeries.map((s) => ratio(s.values[i])),
    ]);

  return (
    <div className="chart">
      <Legend items={shareSeries.map((s) => ({ key: s.key, label: s.label, color: s.color }))} />
      <div className="chart__pair">
        <div className="chart__pane">
          <h4 className="chart__panetitle">Share of household debt</h4>
          <TimeSeriesChart
            x={x}
            xLabels={xLabels}
            series={shareSeries}
            mode="stack"
            title="Share of household debt by collateral"
            desc={`Stacked area of household mortgages and consumer credit by what backs them, ${xLabels[0]} to ${xLabels[xLabels.length - 1]}.`}
            yFormat={(v) => pct(v, 0)}
            valueFormat={(v) => pct(v, 1)}
            yDomain={[0, 1]}
            bands={bands}
            height={300}
          />
        </div>
        <div className="chart__pane">
          <h4 className="chart__panetitle">Collateral value ÷ debt</h4>
          <TimeSeriesChart
            x={x}
            xLabels={xLabels}
            series={covSeries}
            mode="line"
            title="Collateral coverage ratio"
            desc="Market value of owner-occupied real estate divided by home mortgages, and the value of consumer durables divided by auto loans."
            yFormat={(v) => `${v}×`}
            valueFormat={(v) => ratio(v)}
            bands={bands}
            height={300}
          />
        </div>
      </div>
      {data.estimatedThrough && (
        <p className="chart__footnote">The split of consumer credit by type is estimated through {quarterLabel(data.estimatedThrough)}.</p>
      )}
      <DataTable
        caption={`${title}, fourth quarter of each year`}
        columns={["Quarter", ...COLLATERAL_ORDER.map((k) => `${labels[k] ?? k} share`), ...covSeries.map((s) => `${s.label} coverage`)]}
        rows={rows}
      />
    </div>
  );
}
