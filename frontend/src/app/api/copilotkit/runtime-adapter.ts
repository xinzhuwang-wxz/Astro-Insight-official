/**
 * Runtime normalization boundary.
 *
 * Keeps Copilot protocol handling separate from Astro backend streaming.
 * The actual route handler can use this adapter once the exact protocol
 * payload is confirmed.
 */
export function normalizeAstroRequest(body: unknown) {
  return {
    input: body,
  };
}

export function normalizeAstroResponse(payload: unknown) {
  return payload;
}