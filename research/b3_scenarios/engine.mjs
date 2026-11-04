// PLAN task B3: browser version of the scenario engine (same logic as engine.py; see METHOD.md).
// Dependency-free ES module. Checked against the Python core on fixtures/cases.json by test_engine.mjs.

export const CLASSES = ["mortgage", "student_federal", "consumer_other"];

export function validate(exposures, classes, transfer) {
  for (const e of exposures) {
    if (!CLASSES.includes(e.class) || !["public", "private"].includes(e.side)) throw new Error(`bad exposure ${JSON.stringify(e)}`);
    if (!(e.balance >= 0 && Number.isFinite(e.balance))) throw new Error(`negative or non-finite balance ${JSON.stringify(e)}`);
  }
  for (const [c, p] of Object.entries(classes)) {
    if (!CLASSES.includes(c)) throw new Error(`unknown class ${c}`);
    if (!(p.pd >= 0 && p.pd <= 1 && p.lgd >= 0 && p.lgd <= 1)) throw new Error(`pd/lgd outside [0,1] for ${c}`);
    const w = p.timing ?? [1.0];
    if (w.some((x) => x < 0) || Math.abs(w.reduce((a, b) => a + b, 0) - 1) > 1e-12) throw new Error(`timing for ${c} must be non-negative and sum to 1`);
  }
  if (transfer) {
    const share = transfer.share ?? 0, cap = transfer.cap_musd ?? 0;
    if (!(share >= 0 && share <= 1) || cap < 0) throw new Error("transfer share must be in [0,1] and cap >= 0");
  }
}

export function run(exposures, classes, transfer = null) {
  validate(exposures, classes, transfer);
  const n = Math.max(1, ...Object.values(classes).map((p) => (p.timing ?? [1.0]).length));
  const pub = new Array(n).fill(0), priv = new Array(n).fill(0), gsePub = new Array(n).fill(0);
  for (const e of exposures) {
    const p = classes[e.class];
    if (!p) continue;
    const loss = e.balance * p.pd * p.lgd;
    (p.timing ?? [1.0]).forEach((w, q) => {
      if (e.side === "public") {
        pub[q] += loss * w;
        if (e.transfer_eligible) gsePub[q] += loss * w;
      } else {
        priv[q] += loss * w;
      }
    });
  }
  const moved = new Array(n).fill(0);
  if (transfer && (transfer.share ?? 0) > 0 && (transfer.cap_musd ?? 0) > 0) {
    let room = transfer.cap_musd;
    for (let q = 0; q < n; q++) {
      const m = Math.min(gsePub[q] * transfer.share, room);
      moved[q] = m; room -= m; pub[q] -= m; priv[q] += m;
    }
  }
  const total = pub.map((a, i) => a + priv[i]);
  const s = (v) => v.reduce((a, b) => a + b, 0);
  return { public: pub, private: priv, total, transferred: moved,
           sum: { public: s(pub), private: s(priv), total: s(total), transferred: s(moved) } };
}
