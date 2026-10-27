// Server-side helpers that decide how (and whether) each figure embeds its Tableau view.
//
// Two modes:
//   - Tableau Public: NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE is set. Views load from public.tableau.com
//     with no token. Only the sheets listed in NEXT_PUBLIC_TABLEAU_VIEWS are embedded.
//   - Tableau Cloud (Connected Apps): the Public profile is unset and all TABLEAU_REQUIRED_ENV are set.
//     Every view is embedded, with a short-lived JWT from /api/tableau-token.
// With neither, every figure shows its native chart.

export const TABLEAU_PUBLIC_ORIGIN = "https://public.tableau.com";

export const TABLEAU_REQUIRED_ENV = [
  "TABLEAU_SERVER_URL",
  "TABLEAU_CONNECTED_APP_CLIENT_ID",
  "TABLEAU_CONNECTED_APP_SECRET_ID",
  "TABLEAU_CONNECTED_APP_SECRET_VALUE",
  "TABLEAU_EMBED_USER",
] as const;

/** "<Workbook>/<Sheet>" as it appears in a views URL. */
export const TABLEAU_VIEWS = {
  ratchet: "WhoHoldsTheDebt/Ratchet",
  crises: "WhoHoldsTheDebt/CrisisSmallMultiples",
  collateral: "WhoHoldsTheDebt/Collateral",
  priority: "WhoHoldsTheDebt/PaymentPriority",
} as const;

export function missingTableauEnv(): string[] {
  return TABLEAU_REQUIRED_ENV.filter((k) => !process.env[k]?.trim());
}

/** Tableau Public profile name, or null when Public mode is off. */
export function tableauPublicProfile(): string | null {
  return process.env.NEXT_PUBLIC_TABLEAU_PUBLIC_PROFILE?.trim() || null;
}

/** Sheet names listed in NEXT_PUBLIC_TABLEAU_VIEWS (Public mode opt-in). Empty when unset. */
export function publishedPublicSheets(): Set<string> {
  return new Set(
    (process.env.NEXT_PUBLIC_TABLEAU_VIEWS ?? "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
  );
}

/**
 * The "Crisis by crisis" scroll-through drives the Ratchet view only when NEXT_PUBLIC_TABLEAU_SCROLLY=1.
 * Otherwise it uses the native chart, even when the views are configured (the published dashboard
 * must use automatic sizing to fit the scroll-through column). Figure 1's embed is unaffected.
 */
export function scrollyTableauEnabled(): boolean {
  return process.env.NEXT_PUBLIC_TABLEAU_SCROLLY?.trim() === "1";
}

/** Cloud (Connected Apps) settings, or null when Cloud isn't configured. */
export function tableauConfig(): { serverUrl: string; site: string } | null {
  if (missingTableauEnv().length > 0) return null;
  return {
    serverUrl: process.env.TABLEAU_SERVER_URL!.trim().replace(/\/+$/, ""),
    site: process.env.TABLEAU_SITE?.trim() ?? "",
  };
}

export type TableauMode = "public" | "cloud" | null;

export function tableauMode(): TableauMode {
  if (tableauPublicProfile()) return "public";
  if (tableauConfig()) return "cloud";
  return null;
}

/** e.g. https://pod.online.tableau.com/t/mysite/views/WhoHoldsTheDebt/Ratchet */
export function tableauViewUrl(cfg: { serverUrl: string; site: string }, view: string): string {
  return `${cfg.serverUrl}${cfg.site ? `/t/${encodeURIComponent(cfg.site)}` : ""}/views/${view}`;
}

function splitView(view: string): { workbook: string; sheet: string } {
  const i = view.lastIndexOf("/");
  return { workbook: view.slice(0, i), sheet: view.slice(i + 1) };
}

/** Everything the client needs to embed one view. */
export interface TableauEmbed {
  mode: "public" | "cloud";
  /** Embedding API v3 module URL. */
  scriptUrl: string;
  /** Full view URL for <tableau-viz src>. */
  src: string;
  /** Cloud only: fetch a Connected Apps JWT from /api/tableau-token. */
  needsToken: boolean;
  /** Public only: the view's page on the author's Tableau Public profile. */
  openUrl?: string;
}

const scriptPath = "/javascripts/api/tableau.embedding.3.latest.min.js";

/** How to embed `view`, or null to show the native chart. */
export function tableauEmbedFor(view: string): TableauEmbed | null {
  const profile = tableauPublicProfile();
  if (profile) {
    const { workbook, sheet } = splitView(view);
    if (!publishedPublicSheets().has(sheet)) return null; // not published yet: no broken iframe
    return {
      mode: "public",
      scriptUrl: `${TABLEAU_PUBLIC_ORIGIN}${scriptPath}`,
      src: `${TABLEAU_PUBLIC_ORIGIN}/views/${view}`,
      needsToken: false,
      openUrl: `${TABLEAU_PUBLIC_ORIGIN}/app/profile/${encodeURIComponent(profile)}/viz/${workbook}/${sheet}`,
    };
  }
  const cfg = tableauConfig();
  if (cfg) {
    return { mode: "cloud", scriptUrl: `${cfg.serverUrl}${scriptPath}`, src: tableauViewUrl(cfg, view), needsToken: true };
  }
  return null;
}

/** One-line status for the /methods page. */
export function tableauStatus(): string {
  const mode = tableauMode();
  if (mode === "public") {
    const sheets = [...publishedPublicSheets()];
    return `Tableau Public (${tableauPublicProfile()}): ${sheets.length ? sheets.join(", ") : "no views listed yet (native charts)"}`;
  }
  if (mode === "cloud") return "Tableau Cloud (Connected Apps)";
  return "Not configured (native charts)";
}
