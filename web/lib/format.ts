/** "2007-12-31" -> "2007 Q4" */
export function quarterLabel(iso: string): string {
  const y = iso.slice(0, 4);
  const m = Number(iso.slice(5, 7));
  return `${y} Q${Math.ceil(m / 3)}`;
}

/** "2007-12-31" -> 2007.75 (start of quarter, for x scales) */
export function quarterToYear(iso: string): number {
  const y = Number(iso.slice(0, 4));
  const m = Number(iso.slice(5, 7));
  return y + (Math.ceil(m / 3) - 1) / 4;
}

/** 0.3554 -> "35.5%" */
export function pct(x: number | null | undefined, digits = 1): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return "–";
  return `${(x * 100).toFixed(digits)}%`;
}

/** percentage-point delta: 0.128 -> "+12.8 pts" */
export function pts(x: number | null | undefined, digits = 1): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return "–";
  const v = x * 100;
  const s = v > 0 ? "+" : v < 0 ? "−" : "±";
  return `${s}${Math.abs(v).toFixed(digits)} pts`;
}

/** USD millions -> "$18.8T" / "$412B" / "$950M" */
export function usdFromMillions(musd: number | null | undefined, digits = 1): string {
  if (musd === null || musd === undefined || !Number.isFinite(musd)) return "–";
  const abs = Math.abs(musd);
  const sign = musd < 0 ? "−" : "";
  if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(digits)}T`;
  if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(abs >= 1e5 ? 0 : digits)}B`;
  return `${sign}$${abs.toFixed(0)}M`;
}

/** USD billions -> "$18.77T" / "$74B" */
export function usdFromBillions(busd: number | null | undefined, digits = 2): string {
  if (busd === null || busd === undefined || !Number.isFinite(busd)) return "–";
  const abs = Math.abs(busd);
  const sign = busd < 0 ? "−" : "";
  if (abs >= 1000) return `${sign}$${(abs / 1000).toFixed(digits)}T`;
  return `${sign}$${abs.toFixed(0)}B`;
}

export function ratio(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return "–";
  return `${x.toFixed(digits)}×`;
}

/** Fill `{token}` placeholders in copy. Unknown tokens are left visible so they get noticed. */
export function fill(text: string, tokens: Record<string, string>): string {
  return text.replace(/\{(\w+)\}/g, (m, k: string) => (k in tokens ? tokens[k] : m));
}
