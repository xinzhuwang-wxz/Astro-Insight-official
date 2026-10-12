/**
 * Bridge between existing Copilot output storage and Astro events.
 *
 * This intentionally does not delete the existing output store.
 */
export function appendAstroEvent(
  current: unknown[],
  event: unknown
) {
  return [...current, event];
}