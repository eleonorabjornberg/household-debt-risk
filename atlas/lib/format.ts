export function sumReal(cells: number[][]): number {
  let s = 0;
  for (const row of cells) for (const v of row) s += v;
  return s;
}

/** $ millions -> "$4.5T" (or "$820B" below a trillion). */
export function fmtTrillions(musd: number): string {
  if (musd >= 1e6) return `$${(musd / 1e6).toFixed(musd >= 1e7 ? 1 : 2)}T`;
  return `$${Math.round(musd / 1e3)}B`;
}

export function fmtPct(x: number): string {
  return Number.isFinite(x) ? `${(x * 100).toFixed(1)}%` : "–";
}

/** "2008-12-31" -> "2008 Q4" */
export function fmtQuarter(date: string): string {
  const m = Number(date.slice(5, 7));
  return `${date.slice(0, 4)} Q${Math.ceil(m / 3)}`;
}

/** Index of the quarter at or just before `date` (dates are sorted ISO strings). */
export function nearestIndex(dates: string[], date: string): number {
  let lo = 0;
  for (let i = 0; i < dates.length; i++) if (dates[i] <= date) lo = i;
  return lo;
}
