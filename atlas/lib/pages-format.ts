// Formatters used by the pages moved from web/ (site-visible (b), 2026-11-07); same as web/lib/format.ts.

export function pct(x: number | null | undefined, digits = 1): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return "–";
  return `${(x * 100).toFixed(digits)}%`;
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
