// A small, typed wrapper around the parts of the Tableau Embedding API v3 the site drives.
// The names it uses are fixed by tableau/INTEGRATION_CONTRACT.md.
//
// Every call is fail-soft: an error (e.g. the `Active crisis` parameter is missing from an older
// published workbook) is logged once per kind and ignored, so the page never breaks.

// ---------------------------------------------------------------- contract names
export const RATCHET_MAIN = "Ratchet – main"; // en dash (U+2013)
export const RATCHET_PUBLIC = "Public share";
export const FIELD_DATE = "Date";
export const FIELD_BUCKET = "Bucket label";
export const PARAM_ACTIVE_CRISIS = "Active crisis";
export const PARAM_NONE = "none";

// ---------------------------------------------------------------- API types (the subset we use)
export interface TableauDataValue {
  value: unknown;
  formattedValue: string;
}
export interface TableauColumn {
  fieldName: string;
  index: number;
}
export interface TableauDataTable {
  columns: TableauColumn[];
  data: TableauDataValue[][];
}
export interface TableauMarksCollection {
  data: TableauDataTable[];
}
export interface TableauFilter {
  fieldName: string;
  filterType: string;
  minValue?: TableauDataValue;
  maxValue?: TableauDataValue;
}
export interface TableauParameter {
  name: string;
  currentValue: TableauDataValue;
}
export type SelectionUpdateType = "select-replace" | "select-add" | "select-remove";
export interface TableauWorksheet {
  name: string;
  sheetType: "worksheet";
  applyRangeFilterAsync(fieldName: string, range: { min?: Date | number; max?: Date | number }): Promise<string>;
  clearFilterAsync(fieldName: string): Promise<string>;
  getFiltersAsync(): Promise<TableauFilter[]>;
  selectMarksByValueAsync(
    selections: { fieldName: string; value: (string | number)[] }[],
    updateType: SelectionUpdateType,
  ): Promise<void>;
  clearSelectedMarksAsync(): Promise<void>;
  getSelectedMarksAsync(): Promise<TableauMarksCollection>;
}
export interface TableauDashboard {
  name: string;
  sheetType: "dashboard";
  worksheets: TableauWorksheet[];
}
export interface TableauWorkbook {
  activeSheet: TableauDashboard | TableauWorksheet;
  getParametersAsync(): Promise<TableauParameter[]>;
  changeParameterValueAsync(name: string, value: string | number | boolean | Date): Promise<TableauParameter>;
}
/** The <tableau-viz> element once it is interactive. */
export interface TableauVizElement extends HTMLElement {
  workbook: TableauWorkbook;
}

// Embedding API v3 event names (TableauEventType).
export const EVT_FIRST_INTERACTIVE = "firstinteractive";
export const EVT_LOAD_ERROR = "vizloaderror";
export const EVT_MARK_SELECTION = "markselectionchanged";

// ---------------------------------------------------------------- script loader
const scriptPromises = new Map<string, Promise<void>>();

/** Loads the Embedding API module once per URL and resolves when <tableau-viz> is defined. */
export function loadEmbeddingApi(scriptUrl: string): Promise<void> {
  if (typeof window !== "undefined" && window.customElements?.get("tableau-viz")) return Promise.resolve();
  let p = scriptPromises.get(scriptUrl);
  if (!p) {
    p = new Promise<void>((resolve, reject) => {
      const s = document.createElement("script");
      s.type = "module";
      s.src = scriptUrl;
      s.onload = () => resolve();
      s.onerror = () => {
        scriptPromises.delete(scriptUrl);
        s.remove();
        reject(new Error("Could not load the Tableau Embedding API"));
      };
      document.head.appendChild(s);
    });
    scriptPromises.set(scriptUrl, p);
  }
  // A loaded module that never defines the element is a failure too.
  return p.then(() =>
    Promise.race([
      window.customElements.whenDefined("tableau-viz").then(() => undefined),
      new Promise<void>((_, reject) => setTimeout(() => reject(new Error("Tableau Embedding API did not initialise")), 10000)),
    ]),
  );
}

// ---------------------------------------------------------------- helpers
const logged = new Set<string>();
/** Log a failed call once per key, then stay quiet. */
export function logOnce(key: string, err: unknown) {
  if (logged.has(key)) return;
  logged.add(key);
  console.warn(`[tableau] ${key} failed; continuing without it.`, err instanceof Error ? err.message : err);
}

/** Resolves when the viz fires `firstinteractive`; rejects on `vizloaderror` or after `timeoutMs`. */
export function whenInteractive(el: HTMLElement, timeoutMs = 30000): Promise<TableauVizElement> {
  return new Promise((resolve, reject) => {
    const done = (fn: () => void) => {
      clearTimeout(timer);
      el.removeEventListener(EVT_FIRST_INTERACTIVE, onOk);
      el.removeEventListener(EVT_LOAD_ERROR, onErr);
      fn();
    };
    const onOk = () => done(() => resolve(el as TableauVizElement));
    const onErr = () => done(() => reject(new Error("The Tableau view failed to load")));
    // A missing Tableau Public view loads a "Where's the viz?" page without firing vizloaderror.
    const timer = setTimeout(() => done(() => reject(new Error("The Tableau view never became interactive"))), timeoutMs);
    el.addEventListener(EVT_FIRST_INTERACTIVE, onOk);
    el.addEventListener(EVT_LOAD_ERROR, onErr);
  });
}

/** Tableau date values come back as "2007-10-01 00:00:00" (quarter start) or a Date; return the quarter-end ISO date. */
export function toQuarterEnd(v: unknown): string | null {
  let y: number;
  let m: number;
  if (v instanceof Date) {
    y = v.getUTCFullYear();
    m = v.getUTCMonth() + 1;
  } else if (typeof v === "string") {
    const hit = /^(\d{4})-(\d{2})/.exec(v);
    if (!hit) return null;
    y = Number(hit[1]);
    m = Number(hit[2]);
  } else return null;
  const qEndMonth = Math.ceil(m / 3) * 3;
  const lastDay = new Date(Date.UTC(y, qEndMonth, 0)).getUTCDate();
  return `${y}-${String(qEndMonth).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;
}

/** ISO date -> UTC Date (Tableau compares range filters on dates). */
export function isoToUtc(iso: string): Date {
  return new Date(Date.UTC(Number(iso.slice(0, 4)), Number(iso.slice(5, 7)) - 1, Number(iso.slice(8, 10))));
}

/** Shift an ISO quarter-end date by whole years (keeps the quarter end). */
export function shiftYears(iso: string, years: number): string {
  const y = Number(iso.slice(0, 4)) + years;
  return `${y}${iso.slice(4)}`;
}

// ---------------------------------------------------------------- controller
export interface CrisisTarget {
  id: string;
  /** ISO dates for the Date range filter (t0 − 2y, t0 + 4y). */
  min: string;
  max: string;
}

export interface HolderSelection {
  label: string;
  /** Quarter-end ISO dates of the selected marks, sorted. */
  dates: string[];
}

export interface RatchetController {
  readonly hasActiveCrisisParam: boolean;
  /** Zoom + highlight a crisis, or reset with null. Latest call wins; calls never overlap. */
  focusCrisis(target: CrisisTarget | null, opts?: { immediate?: boolean }): void;
  /** Select a holder's marks on `Ratchet – main`, or clear the selection with null. */
  selectHolder(label: string | null): Promise<void>;
  /** Subscribe to selection changes made in Tableau (or by selectHolder). */
  onSelection(cb: (sel: HolderSelection | null) => void): () => void;
  dispose(): void;
  readonly worksheets: { main: TableauWorksheet | null; publicShare: TableauWorksheet | null };
}

const sameTarget = (a: CrisisTarget | null, b: CrisisTarget | null) =>
  a === b || (!!a && !!b && a.id === b.id && a.min === b.min && a.max === b.max);

/**
 * Wraps an interactive <tableau-viz> showing the Ratchet dashboard.
 * Call after `whenInteractive(el)` has resolved.
 */
export async function createRatchetController(viz: TableauVizElement, debounceMs = 180): Promise<RatchetController> {
  const workbook = viz.workbook;
  const sheet = workbook.activeSheet;
  const sheets: TableauWorksheet[] = sheet.sheetType === "dashboard" ? sheet.worksheets : [sheet];
  const main = sheets.find((w) => w.name === RATCHET_MAIN) ?? null;
  const publicShare = sheets.find((w) => w.name === RATCHET_PUBLIC) ?? null;
  if (!main) logOnce(`worksheet "${RATCHET_MAIN}" lookup`, new Error(`found: ${sheets.map((w) => w.name).join(", ")}`));
  const filterSheets = [main, publicShare].filter((w): w is TableauWorksheet => !!w);

  // Check the parameter once, so an older published workbook doesn't get a failing call per scroll step.
  let hasParam = false;
  try {
    const params = await workbook.getParametersAsync();
    hasParam = params.some((p) => p.name === PARAM_ACTIVE_CRISIS);
    if (!hasParam) logOnce(`parameter "${PARAM_ACTIVE_CRISIS}"`, new Error("not in the published workbook yet"));
  } catch (err) {
    logOnce("getParametersAsync", err);
  }

  // ---- serialised, latest-wins crisis focus
  let applied: CrisisTarget | null = null;
  let pending: { t: CrisisTarget | null } | null = null;
  let running = false;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let disposed = false;

  async function apply(t: CrisisTarget | null) {
    const calls: Promise<unknown>[] = [];
    if (hasParam) {
      calls.push(
        workbook.changeParameterValueAsync(PARAM_ACTIVE_CRISIS, t ? t.id : PARAM_NONE).catch((e) => logOnce("changeParameterValueAsync", e)),
      );
    }
    for (const w of filterSheets) {
      calls.push(
        (t
          ? w.applyRangeFilterAsync(FIELD_DATE, { min: isoToUtc(t.min), max: isoToUtc(t.max) })
          : // Verified on Tableau Public: after this, getFiltersAsync() still lists the Date filter,
            // but as a range spanning the full domain (1951 Q4–2026 Q2), i.e. nothing is filtered.
            w.clearFilterAsync(FIELD_DATE)
        ).catch((e) => logOnce(`${t ? "applyRangeFilterAsync" : "clearFilterAsync"} on ${w.name}`, e)),
      );
    }
    await Promise.all(calls);
  }

  async function drain() {
    if (running) return;
    running = true;
    try {
      while (pending && !disposed) {
        const { t } = pending;
        pending = null;
        if (sameTarget(t, applied)) continue;
        await apply(t);
        applied = t;
      }
    } finally {
      running = false;
    }
  }

  // ---- selection events
  const listeners = new Set<(sel: HolderSelection | null) => void>();
  let selSeq = 0;
  async function readSelection() {
    if (!main) return;
    const seq = ++selSeq;
    let sel: HolderSelection | null = null;
    try {
      const marks = await main.getSelectedMarksAsync();
      const labels = new Map<string, Set<string>>();
      for (const table of marks.data) {
        const bi = table.columns.findIndex((c) => c.fieldName === FIELD_BUCKET);
        // The date column is named e.g. "QUARTER(Date)" or "Date".
        const di = table.columns.findIndex((c) => c.fieldName === FIELD_DATE || c.fieldName.includes(`(${FIELD_DATE})`));
        if (bi < 0) continue;
        for (const row of table.data) {
          const label = String(row[bi]?.value ?? row[bi]?.formattedValue ?? "");
          if (!label) continue;
          if (!labels.has(label)) labels.set(label, new Set());
          const d = di >= 0 ? toQuarterEnd(row[di]?.value) : null;
          if (d) labels.get(label)!.add(d);
        }
      }
      // One holder per card: the one with the most selected marks.
      const best = [...labels.entries()].sort((a, b) => b[1].size - a[1].size)[0];
      if (best) sel = { label: best[0], dates: [...best[1]].sort() };
    } catch (err) {
      logOnce("getSelectedMarksAsync", err);
    }
    if (seq !== selSeq || disposed) return; // a newer event superseded this read
    listeners.forEach((cb) => cb(sel));
  }
  const onMarks = () => void readSelection();
  viz.addEventListener(EVT_MARK_SELECTION, onMarks);

  return {
    hasActiveCrisisParam: hasParam,
    worksheets: { main, publicShare },
    focusCrisis(target, opts) {
      pending = { t: target };
      clearTimeout(timer);
      if (opts?.immediate) void drain();
      else timer = setTimeout(() => void drain(), debounceMs);
    },
    async selectHolder(label) {
      if (!main) return;
      try {
        if (label) await main.selectMarksByValueAsync([{ fieldName: FIELD_BUCKET, value: [label] }], "select-replace");
        else await main.clearSelectedMarksAsync();
      } catch (err) {
        logOnce(label ? "selectMarksByValueAsync" : "clearSelectedMarksAsync", err);
      }
    },
    onSelection(cb) {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    dispose() {
      disposed = true;
      clearTimeout(timer);
      viz.removeEventListener(EVT_MARK_SELECTION, onMarks);
      listeners.clear();
    },
  };
}
