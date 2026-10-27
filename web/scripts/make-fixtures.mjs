// Generates FAKE development fixtures in web/fixtures/ that match the mart schema
// (supabase/migrations/20261027000000_init.sql). The shapes are real; the numbers are not.
// Curves are hand-shaped to resemble the story so the charts are meaningful in development,
// but every value here is synthetic. Real data arrives as web/public/data/<table>.json.
//
//   node scripts/make-fixtures.mjs
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "fixtures");
mkdirSync(OUT, { recursive: true });

// ---- quarter helpers -------------------------------------------------------
const qEnd = (y, q) => {
  const m = q * 3;
  const d = new Date(Date.UTC(y, m, 0));
  return d.toISOString().slice(0, 10);
};
const quarters = [];
for (let y = 1952; y <= 2026; y++) {
  for (let q = 1; q <= 4; q++) {
    if (y === 1952 && q < 4) continue;
    if (y === 2026 && q > 2) continue;
    quarters.push({ y, q, t: y + (q - 1) / 4, date: qEnd(y, q) });
  }
}

// piecewise-linear interpolation over [t, value] knots
const interp = (knots) => (t) => {
  if (t <= knots[0][0]) return knots[0][1];
  for (let i = 1; i < knots.length; i++) {
    const [t1, v1] = knots[i];
    const [t0, v0] = knots[i - 1];
    if (t <= t1) return v0 + ((v1 - v0) * (t - t0)) / (t1 - t0);
  }
  return knots[knots.length - 1][1];
};
// deterministic wiggle so lines don't look ruler-straight
const wiggle = (t, amp, seed = 1) => amp * Math.sin(t * 2.1 * seed) * Math.cos(t * 0.7 + seed);
const r = (x, d = 6) => Number(x.toFixed(d));

// ---- headline shapes (synthetic) -------------------------------------------
const publicShare = interp([
  [1952.75, 0.03], [1965, 0.05], [1973.75, 0.068], [1977.75, 0.107], [1981.5, 0.145],
  [1985.5, 0.225], [1990.5, 0.328], [1994.5, 0.402], [2001, 0.396], [2005, 0.36],
  [2007.75, 0.355], [2011.75, 0.48], [2016, 0.53], [2020, 0.545], [2026.25, 0.56],
]);
const scopeTotal = (t) =>
  Math.exp(interp([
    [1952.75, Math.log(30000)], [1970, Math.log(450000)], [1980, Math.log(1400000)],
    [1990, Math.log(3500000)], [2000, Math.log(6900000)], [2007.75, Math.log(13800000)],
    [2012.5, Math.log(12900000)], [2020, Math.log(15500000)], [2026, Math.log(18900000)],
    [2026.25, Math.log(18820000)],
  ])(t));
// within public: federal direct, state & local, rest GSE
const fedDirectOfTotal = interp([[1952.75, 0.012], [1975, 0.01], [1995, 0.012], [2009, 0.03], [2013, 0.07], [2020, 0.085], [2026.25, 0.08]]);
const stateLocalOfTotal = interp([[1952.75, 0.004], [1980, 0.01], [1990, 0.012], [2026.25, 0.006]]);
// within private: private securitization, nonbank, rest banks
const privSecOfTotal = interp([[1952.75, 0], [1984, 0.002], [1995, 0.04], [2001, 0.06], [2006.5, 0.15], [2009, 0.09], [2013, 0.04], [2026.25, 0.03]]);
const nonbankOfTotal = interp([[1952.75, 0.27], [1970, 0.2], [1990, 0.1], [2007, 0.07], [2026.25, 0.06]]);
// consumer-credit fraction of each bucket's holdings
const ccFrac = {
  federal_direct: interp([[1952.75, 0.05], [1990, 0.3], [2010, 0.85], [2026.25, 0.92]]),
  gse_agency: interp([[1952.75, 0], [1975, 0.02], [2004, 0.01], [2005, 0], [2026.25, 0]]),
  state_local: () => 0,
  banks_credit_unions: interp([[1952.75, 0.25], [1990, 0.3], [2026.25, 0.35]]),
  private_securitization: interp([[1984, 0.3], [2000, 0.4], [2006, 0.2], [2026.25, 0.35]]),
  nonbank_other: interp([[1952.75, 0.25], [1990, 0.45], [2026.25, 0.6]]),
};
const cpi = interp([[1952.75, 26.7], [1970, 38.8], [1980, 82.4], [1990, 130.7], [2000, 172.2], [2010, 218], [2020, 258], [2026.25, 325]]);
const dpi = interp([[1959, 340000], [1970, 740000], [1980, 2000000], [1990, 4300000], [2000, 7400000], [2010, 11300000], [2020, 17500000], [2026.25, 22800000]]);
const cpiLatest = cpi(2026.25);

const BUCKETS = ["federal_direct", "gse_agency", "state_local", "banks_credit_unions", "private_securitization", "nonbank_other"];

const debt = [];
const pub = [];
const bucketShareByDate = new Map();
for (const { t, date } of quarters) {
  const total = scopeTotal(t);
  const ps = Math.min(0.9, Math.max(0.01, publicShare(t) + wiggle(t, 0.003)));
  const fed = fedDirectOfTotal(t);
  const sl = stateLocalOfTotal(t);
  const gse = Math.max(0.005, ps - fed - sl);
  const priv = 1 - ps;
  const ps2 = privSecOfTotal(t);
  const nb = nonbankOfTotal(t);
  const banks = Math.max(0.05, priv - ps2 - nb);
  const shares = { federal_direct: fed, gse_agency: gse, state_local: sl, banks_credit_unions: banks, private_securitization: ps2, nonbank_other: nb };
  const norm = Object.values(shares).reduce((a, b) => a + b, 0);
  let pubM = 0, pubCc = 0, mortT = 0, ccT = 0;
  const rows = [];
  for (const b of BUCKETS) {
    const amt = (shares[b] / norm) * total;
    const cc = amt * ccFrac[b](t);
    const mort = amt - cc;
    for (const [debt_type, v] of [["mortgage", mort], ["consumer_credit", cc]]) {
      rows.push({
        date, risk_bucket: b, debt_type,
        nominal_musd: r(v, 1),
        real_musd: r(v * (cpiLatest / cpi(t)), 1),
        share_of_total: r(v / total),
        pct_of_dpi: t >= 1959 ? r(v / dpi(t)) : null,
      });
    }
    if (b === "federal_direct" || b === "gse_agency" || b === "state_local") { pubM += mort; pubCc += cc; }
    mortT += mort; ccT += cc;
  }
  debt.push(...rows);
  bucketShareByDate.set(date, Object.fromEntries(BUCKETS.map((b) => [b, shares[b] / norm])));
  const fedMbs = t >= 2009 ? interp([[2009, 900000], [2014.75, 1750000], [2019.75, 1400000], [2022.25, 2700000], [2026.25, 2050000]])(t) : null;
  pub.push({
    date,
    scope_total_musd: r(total, 1),
    public_musd: r(pubM + pubCc, 1),
    public_share: r((pubM + pubCc) / total),
    public_share_mortgage: r(pubM / mortT),
    public_share_cc: r(pubCc / ccT),
    fed_mbs_musd: fedMbs === null ? null : r(fedMbs, 1),
    fed_mbs_share_of_scope: fedMbs === null ? null : r(fedMbs / total),
  });
}

// ---- collateral --------------------------------------------------------------
const collShare = {
  vehicle_backed: interp([[1952.75, 0.12], [1980, 0.1], [2000, 0.08], [2026.25, 0.09]]),
  uncollateralized: interp([[1952.75, 0.02], [1968, 0.03], [1980, 0.06], [2000, 0.09], [2010, 0.13], [2026.25, 0.15]]),
  other_nonrevolving: interp([[1952.75, 0.12], [1980, 0.08], [2000, 0.05], [2026.25, 0.03]]),
};
const homeCoverage = interp([[1952.75, 3.6], [1970, 3.0], [1980, 3.2], [1990, 2.4], [2000, 2.3], [2006, 2.1], [2011.75, 1.55], [2019, 2.3], [2022.5, 2.9], [2026.25, 2.75]]);
const durablesCoverage = interp([[1952.75, 4.5], [1980, 4.2], [2000, 3.6], [2026.25, 2.9]]);
const coll = [];
const collByDate = new Map();
for (const { t, date } of quarters) {
  const total = scopeTotal(t);
  const v = collShare.vehicle_backed(t), u = collShare.uncollateralized(t), o = collShare.other_nonrevolving(t);
  const h = 1 - v - u - o;
  const est = t < 1968;
  const entries = { home_backed: h, vehicle_backed: v, uncollateralized: u, other_nonrevolving: o };
  collByDate.set(date, entries);
  for (const [k, s] of Object.entries(entries)) {
    const d = s * total;
    const cov = k === "home_backed" ? homeCoverage(t) + wiggle(t, 0.04, 2) : k === "vehicle_backed" ? durablesCoverage(t) : null;
    coll.push({
      collateral_class: k, date,
      debt_musd: r(d, 1),
      collateral_value_musd: cov === null ? null : r(cov * d, 1),
      coverage_ratio: cov === null ? null : r(cov, 4),
      share_of_debt: r(s),
      is_estimated: k !== "home_backed" && est,
    });
  }
}

// ---- dims ---------------------------------------------------------------------
const dimRisk = [
  { risk_bucket: "federal_direct", label: "Federal government (direct)", is_public: true, sort_order: 1 },
  { risk_bucket: "gse_agency", label: "GSEs & agency pools", is_public: true, sort_order: 2 },
  { risk_bucket: "state_local", label: "State & local governments", is_public: true, sort_order: 3 },
  { risk_bucket: "banks_credit_unions", label: "Banks & credit unions", is_public: false, sort_order: 4 },
  { risk_bucket: "private_securitization", label: "Private securitization & mortgage REITs", is_public: false, sort_order: 5 },
  { risk_bucket: "nonbank_other", label: "Finance companies & other private", is_public: false, sort_order: 6 },
];
const dimCrisis = [
  { crisis_id: "recession_1969", name: "1969–70 recession", kind: "nber_recession", start_q: "1969-12-31", end_q: "1970-12-31", notes: "FIXTURE" },
  { crisis_id: "stagflation_1973", name: "1973–75 stagflation", kind: "nber_recession", start_q: "1973-12-31", end_q: "1975-03-31", notes: "FIXTURE" },
  { crisis_id: "double_dip_1980", name: "1980 recession", kind: "nber_recession", start_q: "1980-03-31", end_q: "1980-09-30", notes: "FIXTURE" },
  { crisis_id: "double_dip_1981", name: "1981–82 recession", kind: "nber_recession", start_q: "1981-09-30", end_q: "1982-12-31", notes: "FIXTURE" },
  { crisis_id: "recession_1990", name: "1990–91 recession", kind: "nber_recession", start_q: "1990-09-30", end_q: "1991-03-31", notes: "FIXTURE" },
  { crisis_id: "recession_2001", name: "2001 recession", kind: "nber_recession", start_q: "2001-03-31", end_q: "2001-12-31", notes: "FIXTURE" },
  { crisis_id: "gfc_2007", name: "Great Recession", kind: "nber_recession", start_q: "2007-12-31", end_q: "2009-06-30", notes: "FIXTURE" },
  { crisis_id: "covid_2020", name: "Covid recession", kind: "nber_recession", start_q: "2019-12-31", end_q: "2020-06-30", notes: "FIXTURE" },
  { crisis_id: "student_restart_2023", name: "Student-loan restart", kind: "policy_shock", start_q: "2023-09-30", end_q: null, notes: "FIXTURE" },
];

// ---- crisis windows (long format) --------------------------------------------------
const dateIdx = new Map(quarters.map((q, i) => [q.date, i]));
const metricValue = (metric, date) => {
  if (metric === "public_share") return pub[dateIdx.get(date)].public_share;
  const [kind, key] = metric.split(":");
  if (kind === "share" && bucketShareByDate.get(date)[key] !== undefined) return bucketShareByDate.get(date)[key];
  if (kind === "share") return collByDate.get(date)[key];
  if (kind === "coverage") return coll.find((c) => c.date === date && c.collateral_class === key).coverage_ratio;
  throw new Error(metric);
};
const METRICS = ["public_share", "share:gse_agency", "share:federal_direct", "share:banks_credit_unions", "share:private_securitization", "share:uncollateralized", "coverage:home_backed"];
const windows = [];
for (const c of dimCrisis) {
  const i0 = dateIdx.get(c.start_q);
  for (const metric of METRICS) {
    const v0 = metricValue(metric, c.start_q);
    for (let k = -8; k <= 16; k++) {
      const q = quarters[i0 + k];
      if (!q) continue;
      const v = metricValue(metric, q.date);
      windows.push({ crisis_id: c.crisis_id, metric, q_offset: k, date: q.date, value: r(v), value_at_t0: r(v0), delta_from_t0: r(v - v0) });
    }
  }
}

// ---- NY Fed (2003+) ---------------------------------------------------------------
const ny = [];
const nyBal = {
  mortgage: interp([[2003, 4900], [2008.5, 9300], [2013, 7900], [2020, 9800], [2023, 12000], [2026, 13140], [2026.25, 13066]]),
  heloc: interp([[2003, 240], [2009, 714], [2021.25, 322], [2026.25, 420]]),
  auto: interp([[2003, 640], [2008, 810], [2010, 700], [2020, 1350], [2026.25, 1680]]),
  credit_card: interp([[2003, 690], [2008.75, 866], [2013, 660], [2020, 820], [2021, 770], [2026.25, 1210]]),
  student: interp([[2003, 240], [2010, 760], [2020, 1540], [2026.25, 1650]]),
  other: interp([[2003, 470], [2008, 410], [2013, 310], [2026.25, 550]]),
};
const nyTr = {
  mortgage: interp([[2003, 1.0], [2006, 1.0], [2009.75, 8.9], [2013, 2.5], [2016, 1.0], [2021, 0.4], [2026.25, 1.2]]),
  heloc: interp([[2003, 0.6], [2009.5, 4.5], [2015, 1.5], [2021, 0.3], [2026.25, 0.8]]),
  auto: interp([[2003, 2.6], [2009.25, 5.3], [2012, 3.2], [2019, 4.9], [2021, 3.0], [2026.25, 5.2]]),
  credit_card: interp([[2003, 9.5], [2005, 7.5], [2010, 13.7], [2016, 7.0], [2019, 8.4], [2021.25, 4.2], [2026.25, 7.3]]),
  student: interp([[2003, 9.0], [2012, 11.8], [2019, 9.4], [2020.25, 9.0], [2020.5, 0.9], [2025, 0.8], [2025.25, 8.5], [2025.75, 14.3], [2026.25, 13.9]]),
  other: interp([[2003, 6.0], [2010, 7.5], [2016, 4.5], [2021, 2.8], [2026.25, 4.8]]),
};
for (const { t, date } of quarters) {
  if (t < 2003) continue;
  for (const k of Object.keys(nyBal)) {
    ny.push({ date, loan_type: k, balance_busd: r(nyBal[k](t), 0), transition_serious_pct: r(Math.max(0.1, nyTr[k](t) + wiggle(t, 0.15, 3)), 2) });
  }
}

const write = (name, rows) => writeFileSync(join(OUT, `${name}.json`), JSON.stringify(rows) + "\n");
write("debt_by_risk_holder", debt);
write("public_share", pub);
write("collateral_coverage", coll);
write("crisis_event_window", windows);
write("nyfed_by_type", ny);
write("dim_crisis", dimCrisis);
write("dim_risk_bucket", dimRisk);
console.log(`fixtures: ${quarters.length} quarters, ${debt.length} debt rows, ${windows.length} window rows, ${ny.length} nyfed rows -> ${OUT}`);
