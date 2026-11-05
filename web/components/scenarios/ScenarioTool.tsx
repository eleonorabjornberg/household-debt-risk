"use client";
// PLAN B3: the scenario engine in the browser. Runs lib/b3/engine.mjs, a byte-for-byte copy of
// research/b3_scenarios/engine.mjs, which is checked against the Python core (lib/b3/*.test.ts and
// research/b3_scenarios/test_browser.mjs). Every figure shown is computed here from the synced inputs.
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { run, type Classes, type Exposure, type LoanClass, type Result, type Transfer } from "@/lib/b3/engine.mjs";
import exposuresFile from "@/lib/b3/exposures.json";
import casesFile from "@/lib/b3/cases.json";
import dfast from "@/lib/b3/preset_dfast2026.json";
import replay from "@/lib/b3/preset_replay_2008_2012.json";
import { TimeSeriesChart } from "@/components/charts/TimeSeriesChart";
import { DataTable, Legend, Segmented } from "@/components/charts/parts";
import { pct, usdFromMillions } from "@/lib/format";
import styles from "./scenarios.module.css";

const CLASS_LABEL: Record<LoanClass, string> = {
  mortgage: "Mortgages",
  student_federal: "Federal student loans",
  consumer_other: "Other consumer credit",
};
const CLASS_ORDER: LoanClass[] = ["mortgage", "student_federal", "consumer_other"];

interface PresetDef { classes: Classes; note?: string }
const PRESETS: { key: string; label: string; source: string; proxy: string; def: PresetDef }[] = [
  { key: "dfast2026_proxy", label: "Stress test 2026 (proxy)", source: dfast.source, proxy: dfast.label,
    def: dfast.presets.dfast2026_proxy as PresetDef },
  { key: "dfast2026_proxy_with_student", label: "Stress test 2026 + federal student loans (weak proxy)", source: dfast.source,
    proxy: dfast.label, def: dfast.presets.dfast2026_proxy_with_student as PresetDef },
  { key: "replay_2008_2012_proxy", label: "2008–12 replay (proxy)", source: replay.source, proxy: replay.label,
    def: replay.presets.replay_2008_2012_proxy as PresetDef },
];

interface Custom { on: boolean; pdPct: number; lgdPct: number; quarters: number }
type CustomMap = Record<LoanClass, Custom>;

function customFrom(classes: Classes): CustomMap {
  const out = {} as CustomMap;
  for (const c of CLASS_ORDER) {
    const p = classes[c];
    out[c] = p ? { on: true, pdPct: +(p.pd * 100).toFixed(4), lgdPct: +(p.lgd * 100).toFixed(4), quarters: (p.timing ?? [1]).length }
               : { on: false, pdPct: 0, lgdPct: 100, quarters: 1 };
  }
  return out;
}

function classesFrom(custom: CustomMap): Classes {
  const out: Classes = {};
  for (const c of CLASS_ORDER) {
    const v = custom[c];
    if (!v.on) continue;
    const n = Math.max(1, Math.min(40, Math.round(v.quarters)));
    out[c] = { pd: v.pdPct / 100, lgd: v.lgdPct / 100, timing: new Array(n).fill(1 / n) };
  }
  return out;
}

interface Case { name: string; exposures: Exposure[]; classes: Classes; transfer: Transfer | null }

export function ScenarioTool() {
  const params = useSearchParams();
  const testCase = (casesFile as unknown as Case[]).find((c) => c.name === params.get("case")) ?? null;
  return testCase ? <Tool key={testCase.name} testCase={testCase} /> : <Tool testCase={null} />;
}

function Tool({ testCase }: { testCase: Case | null }) {
  const [mode, setMode] = useState<string>(testCase ? "custom" : PRESETS[0].key);
  const [custom, setCustom] = useState<CustomMap>(() => customFrom(testCase ? testCase.classes : PRESETS[0].def.classes));
  const [transferOn, setTransferOn] = useState(Boolean(testCase?.transfer));
  const [sharePct, setSharePct] = useState(testCase?.transfer ? testCase.transfer.share * 100 : 0);
  const [capB, setCapB] = useState(testCase?.transfer ? testCase.transfer.cap_musd / 1000 : 0);

  const exposures = testCase ? testCase.exposures : (exposuresFile.exposures as Exposure[]);
  const preset = PRESETS.find((p) => p.key === mode) ?? null;
  // A fixed test case keeps its own timing vectors; the form's even timing applies once an input is edited.
  const [caseUntouched, setCaseUntouched] = useState(Boolean(testCase));
  const classes = preset ? preset.def.classes : caseUntouched && testCase ? testCase.classes : classesFrom(custom);
  const transfer: Transfer | null = transferOn ? { share: sharePct / 100, cap_musd: capB * 1000 } : null;

  let out: { result: Result | null; error: string | null };
  try {
    out = { result: run(exposures, classes, transfer), error: null };
  } catch (e) {
    out = { result: null, error: e instanceof Error ? e.message : String(e) };
  }

  // What the form shows: the preset's values, the untouched test case's, or the user's own.
  const shown: CustomMap = preset ? customFrom(preset.def.classes) : caseUntouched && testCase ? customFrom(testCase.classes) : custom;
  const edit = (c: LoanClass, patch: Partial<Custom>) => {
    setCustom({ ...shown, [c]: { ...shown[c], ...patch } });
    setMode("custom");
    setCaseUntouched(false);
  };

  const r = out.result;
  const n = r ? r.total.length : 0;
  const x = Array.from({ length: n }, (_, i) => i + 1);
  const xLabels = x.map((q) => `Quarter ${q}`);
  const shareOfLosses = r && r.sum.total > 0 ? r.sum.public / r.sum.total : null;
  // like for like (skeptic mkt-s55): balances of the loan classes this scenario covers only
  const inScope = exposures.filter((e) => e.class in classes);
  const publicBalance = inScope.filter((e) => e.side === "public").reduce((a, e) => a + e.balance, 0);
  const allBalance = inScope.reduce((a, e) => a + e.balance, 0);
  const leftOut = CLASS_ORDER.filter((c) => !(c in classes)).map((c) => CLASS_LABEL[c].toLowerCase());

  return (
    <div className={styles.tool}>
      <Segmented
        id="b3-preset"
        label="Scenario"
        value={mode}
        options={[...PRESETS.map((p) => ({ value: p.key, label: p.label })), { value: "custom", label: "Your own" }]}
        onChange={(v) => { if (v === "custom") setCustom(shown); setCaseUntouched(false); setMode(v); }}
      />
      {testCase && <p className={styles.note} data-testid="b3-case">Test case “{testCase.name}”: synthetic balances from the engine’s fixed cases replace the Z.1 balances described above. Nothing shown here is Z.1 data.</p>}
      {preset && (
        <p className={styles.note} data-testid="b3-preset-note">
          <strong>{preset.proxy}.</strong> {preset.def.note ? `${preset.def.note[0].toUpperCase()}${preset.def.note.slice(1)}. ` : ""}Source: {preset.source}.
        </p>
      )}

      <fieldset className={styles.fields}>
        <legend>Loss assumptions by loan class{preset ? " (from the preset; edit any to make your own)" : ""}</legend>
        <div className={styles.grid} role="table">
          <div role="row" className={styles.head}>
            <span role="columnheader">Loan class</span>
            <span role="columnheader">{preset ? "Loss rate, % (as default rate)" : "Default rate, %"}</span>
            <span role="columnheader">Loss given default, %</span>
            <span role="columnheader">Spread over quarters</span>
          </div>
          {CLASS_ORDER.map((c) => {
            const v = shown[c];
            return (
              <div role="row" key={c} className={styles.row}>
                <label role="cell" className={styles.cls}>
                  <input type="checkbox" checked={v.on} data-testid={`b3-on-${c}`}
                         onChange={(e) => edit(c, { on: e.target.checked })} /> {CLASS_LABEL[c]}
                </label>
                <input role="cell" type="number" min={0} max={100} step="any" value={v.pdPct} disabled={!v.on}
                       aria-label={`${CLASS_LABEL[c]}: default rate, percent`} data-testid={`b3-pd-${c}`}
                       onChange={(e) => edit(c, { pdPct: Number(e.target.value) })} />
                <input role="cell" type="number" min={0} max={100} step="any" value={v.lgdPct} disabled={!v.on}
                       aria-label={`${CLASS_LABEL[c]}: loss given default, percent`} data-testid={`b3-lgd-${c}`}
                       onChange={(e) => edit(c, { lgdPct: Number(e.target.value) })} />
                <input role="cell" type="number" min={1} max={40} step={1} value={v.quarters} disabled={!v.on || Boolean(preset)}
                       aria-label={`${CLASS_LABEL[c]}: number of quarters`} data-testid={`b3-q-${c}`}
                       onChange={(e) => edit(c, { quarters: Number(e.target.value) })} />
              </div>
            );
          })}
        </div>
        <p className={styles.hint}>
          {preset ? "Presets give a loss rate directly, entered here as a default rate with 100% loss given default, and keep their own quarter-by-quarter timing. " : "Your own scenario spreads each class’s losses evenly over its quarters. "}
          The default rate is cumulative over the whole horizon.
        </p>
      </fieldset>

      <fieldset className={styles.fields}>
        <legend>
          <label><input type="checkbox" checked={transferOn} data-testid="b3-transfer-on"
                        onChange={(e) => setTransferOn(e.target.checked)} /> Pass part of the losses on GSE and agency-pool mortgages to private investors</label>
        </legend>
        <p className={styles.hint}>
          Stands for credit-risk transfer and mortgage insurance: a share of the losses on mortgages held by the GSEs and in
          agency pools moves from the public to the private side, up to a cap. That group also includes Ginnie Mae (FHA and
          VA) pools, whose cover works differently, so a large share with no cap overstates what transfer can move. Off by
          default; the presets apply no transfer.
        </p>
        <div className={styles.pair}>
          <label>Share moved, % <input type="number" min={0} max={100} step="any" value={sharePct} disabled={!transferOn}
                                        data-testid="b3-share" onChange={(e) => setSharePct(Number(e.target.value))} /></label>
          <label>Cap, $ billions <input type="number" min={0} step="any" value={capB} disabled={!transferOn}
                                         data-testid="b3-cap" onChange={(e) => setCapB(Number(e.target.value))} /></label>
        </div>
      </fieldset>

      {out.error && <p className={styles.error} role="alert" data-testid="b3-error">These inputs are not valid: {out.error}</p>}
      {r && (
        <>
          <dl className={styles.totals} aria-live="polite">
            <div><dt>Total losses</dt><dd data-testid="b3-total">{usdFromMillions(r.sum.total)}</dd></div>
            <div><dt>Held on public books</dt><dd data-testid="b3-public">{usdFromMillions(r.sum.public)}</dd></div>
            <div><dt>Held on private books</dt><dd data-testid="b3-private">{usdFromMillions(r.sum.private)}</dd></div>
            <div><dt>Public share of losses</dt><dd data-testid="b3-share-losses">{pct(shareOfLosses, 0)}</dd></div>
            <div><dt>Public share of balances{leftOut.length ? `, without ${leftOut.join(" and ")}` : ""}</dt><dd data-testid="b3-share-balances">{pct(allBalance > 0 ? publicBalance / allBalance : null, 0)}</dd></div>
            {transferOn && <div><dt>Moved by transfer</dt><dd data-testid="b3-transferred">{usdFromMillions(r.sum.transferred)}</dd></div>}
          </dl>
          {n > 0 && r.sum.total > 0 && (
            <figure className={`figure chart ${styles.figure}`}>
              <Legend items={[{ key: "public", label: "Public books", color: "var(--b-federal_direct)" },
                              { key: "private", label: "Private books", color: "var(--b-banks_credit_unions)" }]} />
              <TimeSeriesChart
                x={x}
                xLabels={xLabels}
                series={[{ key: "public", label: "Public books", color: "var(--b-federal_direct)", values: r.public },
                         { key: "private", label: "Private books", color: "var(--b-banks_credit_unions)", values: r.private }]}
                mode="stack"
                boundaryAfter={1}
                title="Losses by quarter, public and private books"
                desc={`Stacked areas over ${n} quarters: losses on public books below, private books above. Total ${usdFromMillions(r.sum.total)}, of which public ${usdFromMillions(r.sum.public)}.`}
                yFormat={(v) => usdFromMillions(v, 0)}
                valueFormat={(v) => usdFromMillions(v)}
                xTicks={x.filter((q) => n <= 12 || q % 4 === 1)}
                xTickFormat={(v) => `Q${v}`}
                totalLabel="Total"
                height={240}
              />
              <DataTable
                caption="Losses by quarter"
                columns={["Quarter", "Public books", "Private books", "Total", ...(transferOn ? ["Moved by transfer"] : [])]}
                rows={x.map((q, i) => [`Q${q}`, usdFromMillions(r.public[i]), usdFromMillions(r.private[i]), usdFromMillions(r.total[i]),
                                       ...(transferOn ? [usdFromMillions(r.transferred[i])] : [])])}
                note="Figures in dollars of today's balances; a quarter is one step of the scenario, not a calendar date."
              />
            </figure>
          )}
        </>
      )}
      <pre hidden data-testid="b3-result">{JSON.stringify({ classes, transfer, result: r, error: out.error })}</pre>
    </div>
  );
}
