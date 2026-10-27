// Lets Figure 2 (CrisisMultiples) ask the "Crisis by crisis" scroll-through to show a crisis.
// The scroll-through listens for the event and calls preventDefault() when it handled it, so a
// panel link falls back to plain #anchor navigation when nothing is listening.

export const CRISIS_FOCUS_EVENT = "hhd:crisis-focus";

export const crisisStepId = (crisisId: string) => `crisis-step-${crisisId}`;

/** Returns true when a listener handled the request. */
export function requestCrisisFocus(crisisId: string): boolean {
  const ev = new CustomEvent<{ id: string }>(CRISIS_FOCUS_EVENT, { detail: { id: crisisId }, cancelable: true });
  return !window.dispatchEvent(ev);
}
