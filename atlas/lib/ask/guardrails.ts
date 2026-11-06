// Ask Hot Potato guardrails added after the E4 red-team pass P1 (labels: evals/e4_redteam/run-P1-2026-11-06-labels.json).
// Each one answers a labelled failure:
//  * a2-1 (counterfactual "would leave 9.4%"): a deterministic pre-check refuses hypotheticals before any model call,
//    and a system-prompt rule forbids computing them;
//  * a4-3 (NY Fed minus Z.1 "gap"): a system-prompt rule forbids arithmetic across the two sources;
//  * a6-5 (false anchor left standing): a system-prompt rule says to check every figure the question asserts;
//  * a10-2 ("The main cause was ..."), a10-3 (bold "No." to a causal yes/no): a rule against naming causes or
//    opening with yes/no on causal questions;
//  * all answers: a post-answer check labels numbers that are neither tool values nor repeated from the question
//    (the model's own arithmetic), so a reader can tell computed numbers from returned ones.
// These are Ask-level rules: lib/ask/tools.ts stays at parity with the Python MCP tools.
import { ungrounded } from "./grounding";
import type { Row } from "./tools";

const HYPOTHETICAL = new RegExp([
  String.raw`\b(suppose|supposing|assume|assuming|imagine|pretend|hypothetical(ly)?|counterfactual|in a world where)\b`,
  String.raw`\bwhat if\b`,
  String.raw`\bhad\b[^?.]{0,80}\b(not|never)\b`,
  String.raw`\bif\b[^?.]{0,80}\b(were|had|hadn't|stayed|fell|rose|doubled|halved)\b[^?.]{0,80}\b(would|what|how)\b`,
  String.raw`\bwould\b[^?.]{0,40}\bhave been\b`,
  String.raw`\b(if|when)\b[^?.]{0,60}\b(keeps?|continues?|carr(y|ies) (on|forward))\b`,
  String.raw`\b(on (current|recent) (momentum|trend)|carry the (recent )?trend|straight line through|extrapolat\w*|ballpark for the (coming|next))\b`,
].join("|"), "i");

export function hypotheticalCheck(question: string): Row | null {
  if (!HYPOTHETICAL.test(question)) return null;
  return { refused: true, reason_code: "hypothetical",
           reason: "This asks for a hypothetical, scenario or trend-continuation number, and the data only records what happened.",
           note: "No number was returned. The nearest answerable question is the actual value for a past quarter, or how it changed around past crises." };
}

export const SYSTEM_RULES = [
  "Never compute a hypothetical, scenario or 'what would be left if' number, even as a bound; give the actual values only.",
  "Never add, subtract, average, divide or difference NY Fed and Z.1 numbers, or state a gap between them.",
  "If the question asserts a number, check it with a tool and say plainly whether it matches; never leave it unchecked.",
  "Do not name causes: describe what changed and say the data cannot establish why. Do not open with yes or no on a causal question.",
].join(" ");

/** Post-answer check: numbers the tools did not return and the question did not contain (the model's own arithmetic). */
export function computedNumbers(answer: string, toolOutputs: Row[], question: string): string[] {
  return [...new Set(ungrounded(answer, toolOutputs, question))];
}

export function computedNote(nums: string[]): string {
  return nums.length ? `\n\nComputed from the data, not returned by it: ${nums.join(", ")}.` : "";
}
