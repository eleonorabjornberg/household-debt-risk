"use client";
import { useMemo, useState } from "react";
import type { Crisis, RatchetData } from "@/lib/shape";
import { pct, quarterLabel, quarterToYear, usdFromMillions } from "@/lib/format";
import { TimeSeriesChart } from "./TimeSeriesChart";
import { crisisBands, DataTable, Legend, Segmented } from "./parts";

type DebtView = "all" | "mortgage" | "consumer_credit";
type Measure = "share" | "real";

export function RatchetChart({ data, crises, title }: { data: RatchetData; crises: Crisis[]; title: string }) {
  const [debt, setDebt] = useState<DebtView>("all");
  const [measure, setMeasure] = useState<Measure>("share");

  const x = useMemo(() => data.dates.map(quarterToYear), [data.dates]);
  const xLabels = useMemo(() => data.dates.map(quarterLabel), [data.dates]);
  const bands = useMemo(() => crisisBands(crises), [crises]);
  const nPublic = data.buckets.filter((b) => b.isPublic).length;

  const series = useMemo(() => {
    const types = debt === "all" ? (["mortgage", "consumer_credit"] as const) : ([debt] as const);
    const raw = data.buckets.map((b) =>
      data.dates.map((_, i) =>
        types.reduce((s, t) => {
          const v = measure === "real" ? (data.real[t][b.key][i] ?? data.nominal[t][b.key][i]) : data.nominal[t][b.key][i];
          return s + (v ?? 0);
        }, 0),
      ),
    );
    const totals = data.dates.map((_, i) => raw.reduce((s, r) => s + r[i], 0));
    return data.buckets.map((b, k) => ({
      key: b.key,
      label: b.label,
      color: `var(--b-${b.key})`,
      values: measure === "share" ? raw[k].map((v, i) => (totals[i] ? v / totals[i] : 0)) : raw[k],
    }));
  }, [data, debt, measure]);

  const fmt = measure === "share" ? (v: number) => pct(v, 0) : (v: number) => usdFromMillions(v, 0);
  const valueFmt = measure === "share" ? (v: number) => pct(v, 1) : (v: number) => usdFromMillions(v, 2);
  const debtName = debt === "all" ? "household mortgages and consumer credit" : debt === "mortgage" ? "household 1–4 family mortgages" : "consumer credit";

  const tableRows = data.dates
    .map((d, i) => ({ d, i }))
    .filter(({ d }) => d.slice(5, 7) === "12" || d === data.dates[data.dates.length - 1])
    .map(({ d, i }) => [
      quarterLabel(d),
      valueFmt(series.slice(0, nPublic).reduce((s, se) => s + (se.values[i] ?? 0), 0)),
      ...series.map((s) => valueFmt(s.values[i] ?? 0)),
    ]);

  return (
    <div className="chart">
      <div className="chart__controls">
        <Segmented
          id="ratchet-debt"
          label="Debt"
          value={debt}
          onChange={setDebt}
          options={[
            { value: "all", label: "All" },
            { value: "mortgage", label: "Mortgages" },
            { value: "consumer_credit", label: "Consumer credit" },
          ]}
        />
        <Segmented
          id="ratchet-measure"
          label="Measure"
          value={measure}
          onChange={setMeasure}
          options={[
            { value: "share", label: "Share" },
            { value: "real", label: "Real dollars" },
          ]}
        />
      </div>
      <div className="legend-groups">
        <Legend label="Public" items={series.slice(0, nPublic).map((s) => ({ key: s.key, label: s.label, color: s.color }))} />
        <Legend label="Private" items={series.slice(nPublic).map((s) => ({ key: s.key, label: s.label, color: s.color }))} />
      </div>
      <TimeSeriesChart
        x={x}
        xLabels={xLabels}
        series={series}
        mode="stack"
        title={title}
        desc={`Stacked area of ${debtName} by holder type, ${xLabels[0]} to ${xLabels[xLabels.length - 1]}, as ${measure === "share" ? "a share of the total" : "inflation-adjusted dollars"}. The dark line separates public holders below from private holders above. Shaded bands are recessions.`}
        yFormat={fmt}
        valueFormat={valueFmt}
        yDomain={measure === "share" ? [0, 1] : undefined}
        bands={bands}
        boundaryAfter={nPublic}
        boundaryLabel={(v) => (measure === "share" ? `Public ${pct(v, 0)}` : usdFromMillions(v, 1))}
        totalLabel="Public total"
      />
      <DataTable
        caption={`Holders of ${debtName}, fourth quarter of each year (${measure === "share" ? "share of total" : "real USD"})`}
        columns={["Quarter", "Public total", ...series.map((s) => s.label)]}
        rows={tableRows}
      />
    </div>
  );
}
