"use client";
// /dashboard (PLAN F7, docket 54, 2026-11-10): Core tiles and panels for a market reader.
// Every number on a tile is wrapped in a ClaimRef to its claims/register.csv row (dash_* and the
// headline rows); lib/dashboard.test.ts checks the computed values against the register.
import { useMemo, useState } from "react";
import { PotatoPerson } from "@/components/Potato";
import { ClaimRef } from "@/components/claims/SourceRef";
import { TimeSeriesChart } from "@/components/pages/charts/TimeSeriesChart";
import { DataTable, Legend, Segmented } from "@/components/pages/charts/parts";
import { fmtQuarter } from "@/lib/format";
import { pct, usdFromMillions } from "@/lib/pages-format";
import { LOAN_LABEL, LOAN_TYPES, type HolderMix, type LoanPanel, type LoanType, type Move, type Tiles } from "@/lib/dashboard";

type LoanFilter = "all" | LoanType;
type Range = "all" | "2000" | "10y" | "5y";
type Units = "share" | "usd";

const BUCKET_COLORS = ["#1d4ed8", "#3b82f6", "#93c5fd", "#c2410c", "#f97316", "#fdba74"];
const LOAN_COLORS: Record<LoanType, string> = {
  mortgage: "#1d4ed8", heloc: "#0891b2", auto: "#7c3aed", credit_card: "#e5267a", student: "#c2410c", other: "#525252",
};

// Display spellings shared with the register rows (each register location points at a line using one of these).
const sign = (v: number) => (v > 0 ? "+" : v < 0 ? "−" : "");
export const fmtUsdDelta = (musd: number) => `${sign(musd)}${usdFromMillions(Math.abs(musd), 0)}`;
export const fmtPp = (share: number) => `${sign(share)}${Math.abs(share * 100).toFixed(1)} pp`;
export const fmtUsd = (musd: number) => usdFromMillions(musd, 2);
export const fmtTimes = (r: number) => `${r.toFixed(2)}×`;
export const fmtTimesDelta = (r: number) => `${sign(r)}${Math.abs(r).toFixed(2)}×`;
export const fmtRate = (p: number) => `${p.toFixed(2)}%`;
export const fmtRateDelta = (p: number) => `${sign(p)}${Math.abs(p).toFixed(2)} pp`;

const yearOf = (d: string) => Number(d.slice(0, 4)) + (Number(d.slice(5, 7)) - 1.5) / 12;

function startFor(range: Range, last: string): string {
  const y = Number(last.slice(0, 4));
  if (range === "2000") return "2000-01-01";
  if (range === "10y") return `${y - 10}${last.slice(4)}`;
  if (range === "5y") return `${y - 5}${last.slice(4)}`;
  return "0000";
}

function Delta({ id, children, v }: { id: string; children: string; v: number | null }) {
  if (v === null) return <span className="dash-delta">n/a</span>;
  return (
    <span className={`dash-delta ${v > 0 ? "up" : v < 0 ? "down" : ""}`}>
      <ClaimRef id={id}>{children}</ClaimRef>
    </span>
  );
}

function Tile({ label, value, dq, dy, note }: { label: string; value: React.ReactNode; dq: React.ReactNode; dy: React.ReactNode; note: React.ReactNode }) {
  return (
    <div className="dash-tile">
      <p className="dash-tile__label">{label}</p>
      <p className="dash-tile__value">{value}</p>
      <dl className="dash-tile__moves">
        <div><dt>on the quarter</dt><dd>{dq}</dd></div>
        <div><dt>on the year</dt><dd>{dy}</dd></div>
      </dl>
      <p className="dash-tile__note">{note}</p>
    </div>
  );
}

function TransitionRows({ moves, only }: { moves: Record<LoanType, Move>; only: LoanType[] }) {
  return (
    <table className="dash-mini">
      <thead><tr><th scope="col">Loan type</th><th scope="col">Rate</th><th scope="col">Qtr</th><th scope="col">Year</th></tr></thead>
      <tbody>
        {only.map((t) => {
          const m = moves[t];
          return (
            <tr key={t}>
              <th scope="row">{LOAN_LABEL[t]}</th>
              <td><ClaimRef id={`dash_trans_${t}`}>{fmtRate(m.value)}</ClaimRef></td>
              <td><Delta id={`dash_trans_${t}_dq`} v={m.dq}>{fmtRateDelta(m.dq ?? 0)}</Delta></td>
              <td><Delta id={`dash_trans_${t}_dy`} v={m.dy}>{fmtRateDelta(m.dy ?? 0)}</Delta></td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function Dashboard({ tiles, mix, loans }: { tiles: Tiles; mix: HolderMix; loans: LoanPanel }) {
  const [loan, setLoan] = useState<LoanFilter>("all");
  const [range, setRange] = useState<Range>("10y");
  const [units, setUnits] = useState<Units>("share");
  const { scope, publicShare: ps, homeCoverage: hc } = tiles;
  const asOf = fmtQuarter(scope.date);

  const debtView = loan === "all" ? "all" : loan === "mortgage" || loan === "heloc" ? "mortgage" : "consumer_credit";
  const debtLabel = { all: "mortgages and consumer credit", mortgage: "mortgages", consumer_credit: "consumer credit" }[debtView];

  const holder = useMemo(() => {
    const from = startFor(range, mix.dates[mix.dates.length - 1]);
    const idx = mix.dates.map((d, i) => [d, i] as const).filter(([d]) => d >= from).map(([, i]) => i);
    const raw = mix.values[debtView];
    const totals = idx.map((q) => raw.reduce((s, b) => s + b[q], 0));
    const series = mix.buckets.map((b, bi) => ({
      key: b.key, label: b.label, color: BUCKET_COLORS[bi % BUCKET_COLORS.length],
      values: idx.map((q, k) => (units === "share" ? (totals[k] ? raw[bi][q] / totals[k] : null) : raw[bi][q])),
    }));
    const pub = idx.map((q, k) => (totals[k] ? mix.buckets.reduce((s, b, bi) => s + (b.isPublic ? raw[bi][q] : 0), 0) / totals[k] : null));
    return { dates: idx.map((q) => mix.dates[q]), series, totals, pub };
  }, [mix, range, debtView, units]);

  const loanView = useMemo(() => {
    const from = startFor(range, loans.dates[loans.dates.length - 1]);
    const idx = loans.dates.map((d, i) => [d, i] as const).filter(([d]) => d >= from).map(([, i]) => i);
    const series = (k: "transition" | "balance") => LOAN_TYPES.map((t) => ({
      key: t, label: LOAN_LABEL[t], color: LOAN_COLORS[t],
      values: idx.map((q) => loans[k][t][q]), muted: loan !== "all" && loan !== t,
    }));
    return { dates: idx.map((q) => loans.dates[q]), transition: series("transition"), balance: series("balance") };
  }, [loans, range, loan]);

  const ticks = (dates: string[]) => {
    const years = [...new Set(dates.map((d) => Number(d.slice(0, 4))))];
    const step = years.length > 40 ? 10 : years.length > 15 ? 5 : years.length > 7 ? 2 : 1;
    return years.filter((y) => y % step === 0).map((y) => y + 0.125);
  };
  const lastPub = holder.pub[holder.pub.length - 1];
  const firstPub = holder.pub[0];
  const focus = loan === "all" ? null : loan;

  return (
    <div className="dash">
      <div className="dash-filters" role="group" aria-label="Dashboard filters">
        <Segmented id="dash-loan" label="Loan type" value={loan} onChange={setLoan}
          options={[{ value: "all", label: "All" }, ...LOAN_TYPES.map((t) => ({ value: t, label: LOAN_LABEL[t] }))]} />
        <Segmented id="dash-range" label="Date range" value={range} onChange={setRange}
          options={[{ value: "all", label: "Full history" }, { value: "2000", label: "Since 2000" }, { value: "10y", label: "10 years" }, { value: "5y", label: "5 years" }]} />
      </div>

      <section className="dash-tiles" aria-label={`Headline numbers, ${asOf}`}>
        <Tile label="Household debt in scope"
          value={<ClaimRef id="scope_usd_2026q2">{fmtUsd(scope.value)}</ClaimRef>}
          dq={<Delta id="z1_scope_change" v={scope.dq}>{fmtUsdDelta(scope.dq ?? 0)}</Delta>}
          dy={<Delta id="dash_scope_dy" v={scope.dy}>{fmtUsdDelta(scope.dy ?? 0)}</Delta>}
          note="Mortgages plus consumer credit. Fed Z.1, nominal." />
        <Tile label="Public share"
          value={<ClaimRef id="public_share_2026q2">{pct(ps.value, 1)}</ClaimRef>}
          dq={<Delta id="dash_public_share_dq" v={ps.dq}>{fmtPp(ps.dq ?? 0)}</Delta>}
          dy={<Delta id="dash_public_share_dy" v={ps.dy}>{fmtPp(ps.dy ?? 0)}</Delta>}
          note={<a href="/methods#scope">Who counts as public</a>} />
        <Tile label="Home collateral coverage"
          value={<ClaimRef id="home_coverage_2026q2">{fmtTimes(hc.value)}</ClaimRef>}
          dq={<Delta id="dash_home_cov_dq" v={hc.dq}>{fmtTimesDelta(hc.dq ?? 0)}</Delta>}
          dy={<Delta id="dash_home_cov_dy" v={hc.dy}>{fmtTimesDelta(hc.dy ?? 0)}</Delta>}
          note="Home value ÷ mortgage debt. Higher is more cushion." />
        <div className="dash-tile dash-tile--wide">
          <p className="dash-tile__label">Into serious delinquency (90+ days), % of balance, annualized</p>
          <TransitionRows moves={tiles.transitions} only={focus ? [focus] : [...LOAN_TYPES]} />
          <p className="dash-tile__note">
            NY Fed, {fmtQuarter(tiles.transitions.mortgage.date)}, pp. <a href="/methods#limits">Limits</a>.
          </p>
        </div>
      </section>
      <p className="pg-caption">Data as of {asOf}. Click a number for its source and register row.</p>

      <section className="pg-section dash-panel" aria-labelledby="dash-holders">
        <h2 id="dash-holders">Who holds the {debtLabel}</h2>
        <p className="pg-caption">
          Public share of {debtLabel}: {pct(firstPub, 1)} in {fmtQuarter(holder.dates[0])}, {pct(lastPub, 1)} in{" "}
          {fmtQuarter(holder.dates[holder.dates.length - 1])}.
          {loan !== "all" && " Holders shown for its category (mortgages or consumer credit)."}
        </p>
        <div className="holder-cast" role="img"
          aria-label={`Each holder drawn holding potatoes, one potato for about 5% of ${debtLabel} in ${fmtQuarter(mix.dates[mix.dates.length - 1])}.`}>
          {mix.buckets.map((b, bi) => {
            const raw = mix.values[debtView];
            const q = mix.dates.length - 1;
            const tot = raw.reduce((t, x) => t + x[q], 0);
            const n = tot ? Math.round((raw[bi][q] / tot) * 20) : 0;
            return (
              <figure key={b.key}>
                <PotatoPerson potatoes={n} tone={b.isPublic ? "public" : "private"} width={70} hot={n > 0} />
                <figcaption>{b.label}</figcaption>
              </figure>
            );
          })}
        </div>
        <p className="pg-caption">One potato ≈ 5% of the total, latest quarter.</p>
        <Segmented id="dash-units" label="Show" value={units} onChange={setUnits}
          options={[{ value: "share", label: "Share of total" }, { value: "usd", label: "Dollars" }]} />
        <div className="chart">
          <Legend items={holder.series.map((s) => ({ key: s.key, label: s.label, color: s.color }))} label="Public (blue) · private (orange)" />
          <TimeSeriesChart
            x={holder.dates.map(yearOf)}
            xLabels={holder.dates.map(fmtQuarter)}
            series={holder.series}
            mode="stack"
            boundaryAfter={mix.buckets.filter((b) => b.isPublic).length}
            boundaryLabel={(v) => (units === "share" ? `public ${pct(v, 1)}` : `public ${usdFromMillions(v)}`)}
            title={`Holders of household ${debtLabel}, by quarter`}
            desc={`Stacked areas by holder from ${fmtQuarter(holder.dates[0])} to ${fmtQuarter(holder.dates[holder.dates.length - 1])}: three public holders at the bottom, three private holders above, separated by a heavy line. The public share went from ${pct(firstPub, 1)} to ${pct(lastPub, 1)}.`}
            yFormat={(v) => (units === "share" ? pct(v, 0) : usdFromMillions(v, 0))}
            valueFormat={(v) => (units === "share" ? pct(v, 1) : usdFromMillions(v))}
            yDomain={units === "share" ? [0, 1] : undefined}
            xTicks={ticks(holder.dates)}
            xTickFormat={(v) => String(Math.floor(v))}
            totalLabel="Total"
            height={300}
          />
          <DataTable
            caption={`Holders of household ${debtLabel} (nominal $ millions)`}
            columns={["Quarter", ...mix.buckets.map((b) => b.label), "Public share"]}
            rows={holder.dates.slice(-8).map((d, k0) => {
              const k = holder.dates.length - Math.min(8, holder.dates.length) + k0;
              const qi = mix.dates.indexOf(d);
              return [fmtQuarter(d), ...mix.buckets.map((_, bi) => usdFromMillions(mix.values[debtView][bi][qi])), pct(holder.pub[k], 1)];
            })}
            note="Last eight quarters. Fed Z.1, nominal."
          />
        </div>
      </section>

      <section className="pg-section dash-panel" aria-labelledby="dash-loans">
        <h2 id="dash-loans">Delinquency and balances by loan type</h2>
        <p className="pg-caption">
          NY Fed, from 2003. {focus ? `${LOAN_LABEL[focus]} highlighted.` : "Pick a loan type to highlight it."}
        </p>
        <div className="dash-two">
          <div className="chart">
            <TimeSeriesChart
              x={loanView.dates.map(yearOf)}
              xLabels={loanView.dates.map(fmtQuarter)}
              series={loanView.transition}
              mode="line"
              title="Balance moving into 90+ days delinquent, % annualized"
              desc={`Lines for six loan types from ${fmtQuarter(loanView.dates[0])} to ${fmtQuarter(loanView.dates[loanView.dates.length - 1])}. Latest: ${LOAN_TYPES.map((t) => `${LOAN_LABEL[t]} ${fmtRate(tiles.transitions[t].value)}`).join(", ")}.`}
              yFormat={(v) => `${v.toFixed(0)}%`}
              valueFormat={(v) => `${v.toFixed(2)}%`}
              xTicks={ticks(loanView.dates)}
              xTickFormat={(v) => String(Math.floor(v))}
              height={260}
              compact
            />
          </div>
          <div className="chart">
            <TimeSeriesChart
              x={loanView.dates.map(yearOf)}
              xLabels={loanView.dates.map(fmtQuarter)}
              series={loanView.balance}
              mode="line"
              title="Balance outstanding, $ billions"
              desc={`Balances for six loan types from ${fmtQuarter(loanView.dates[0])} to ${fmtQuarter(loanView.dates[loanView.dates.length - 1])}, NY Fed, nominal dollars. Mortgages are by far the largest.`}
              yFormat={(v) => usdFromMillions(v * 1000, 0)}
              valueFormat={(v) => usdFromMillions(v * 1000)}
              xTicks={ticks(loanView.dates)}
              xTickFormat={(v) => String(Math.floor(v))}
              height={260}
              compact
            />
          </div>
        </div>
        <Legend items={LOAN_TYPES.map((t) => ({ key: t, label: LOAN_LABEL[t], color: LOAN_COLORS[t] }))} label="Loan type" />
      </section>
    </div>
  );
}
