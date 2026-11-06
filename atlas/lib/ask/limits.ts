// Ask Hot Potato (PLAN D6) limits, Eleonora's d6-preview (PLAN 0e0dd6c): 5 questions per visitor per UTC day and a
// $2/day hard stop for the whole app, enforced here, server-side, before any model call. Both need a store shared
// across serverless instances; which one is her open question. MemoryStore is for tests and local dev ONLY.

export interface Store {
  /** Add `by` to the number at `key` (creating it at 0), expire it after `ttlSeconds`, return the new value. */
  add(key: string, by: number, ttlSeconds: number): Promise<number>;
  get(key: string): Promise<number>;
}

export class MemoryStore implements Store {
  private m = new Map<string, number>();
  async add(key: string, by: number): Promise<number> {
    const v = (this.m.get(key) ?? 0) + by;
    this.m.set(key, v);
    return v;
  }
  async get(key: string): Promise<number> {
    return this.m.get(key) ?? 0;
  }
}

export const QUESTIONS_PER_VISITOR_PER_DAY = 5;
export const APP_USD_PER_DAY = 2.0;
const DAY_TTL = 2 * 24 * 3600;

export class LimitError extends Error {
  constructor(public code: "visitor_daily_limit" | "app_daily_budget", message: string) { super(message); }
}

export const utcDay = (now: Date) => now.toISOString().slice(0, 10);

export class Limiter {
  constructor(private store: Store, private now: () => Date = () => new Date()) {}

  private key(kind: string, extra = "") { return `ask:${kind}:${utcDay(this.now())}${extra ? ":" + extra : ""}`; }

  /** Count one question for this visitor; refuse the 6th and later in a UTC day. Call once per question. */
  async admitVisitor(visitorHash: string): Promise<number> {
    const n = await this.store.add(this.key("visitor", visitorHash), 1, DAY_TTL);
    if (n > QUESTIONS_PER_VISITOR_PER_DAY)
      throw new LimitError("visitor_daily_limit",
        `This preview allows ${QUESTIONS_PER_VISITOR_PER_DAY} questions per visitor per day. Please come back tomorrow (UTC).`);
    return n;
  }

  async spentToday(): Promise<number> { return this.store.get(this.key("usd")); }

  /** Pre-call guard: refuse if the day's spend plus the worst case of the next call would reach the daily stop. */
  async guard(worstCaseUsd: number): Promise<void> {
    const spent = await this.spentToday();
    if (spent + worstCaseUsd >= APP_USD_PER_DAY)
      throw new LimitError("app_daily_budget",
        "Ask Hot Potato has reached its daily budget for this preview. Please try again tomorrow (UTC).");
  }

  /** Record a call's measured cost (logged usage x price). */
  async record(usd: number): Promise<number> { return this.store.add(this.key("usd"), usd, DAY_TTL); }
}
