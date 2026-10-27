// Server-only helpers for Tableau Connected Apps embedding.

export const TABLEAU_REQUIRED_ENV = [
  "TABLEAU_SERVER_URL",
  "TABLEAU_CONNECTED_APP_CLIENT_ID",
  "TABLEAU_CONNECTED_APP_SECRET_ID",
  "TABLEAU_CONNECTED_APP_SECRET_VALUE",
  "TABLEAU_EMBED_USER",
] as const;

export const TABLEAU_VIEWS = {
  ratchet: "WhoHoldsTheDebt/Ratchet",
  crises: "WhoHoldsTheDebt/CrisisSmallMultiples",
  collateral: "WhoHoldsTheDebt/Collateral",
  priority: "WhoHoldsTheDebt/PaymentPriority",
} as const;

export function missingTableauEnv(): string[] {
  return TABLEAU_REQUIRED_ENV.filter((k) => !process.env[k]?.trim());
}

/** Public (non-secret) embed settings, or null when Tableau isn't configured. */
export function tableauConfig(): { serverUrl: string; site: string } | null {
  if (missingTableauEnv().length > 0) return null;
  return {
    serverUrl: process.env.TABLEAU_SERVER_URL!.replace(/\/+$/, ""),
    site: process.env.TABLEAU_SITE?.trim() ?? "",
  };
}

/** e.g. https://pod.online.tableau.com/t/mysite/views/WhoHoldsTheDebt/Ratchet */
export function tableauViewUrl(cfg: { serverUrl: string; site: string }, view: string): string {
  return `${cfg.serverUrl}${cfg.site ? `/t/${encodeURIComponent(cfg.site)}` : ""}/views/${view}`;
}
