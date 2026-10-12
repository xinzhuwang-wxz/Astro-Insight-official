/**
 * Boundary between UI components and Astro backend.
 *
 * Keeping this separate allows us to switch between:
 * - CopilotKit runtime protocol
 * - direct LangGraph streaming
 * without rewriting components.
 */

import { ASTRO_BACKEND } from "@/config/backend";

export async function sendAstroQuery(query: string) {
  return fetch(`${ASTRO_BACKEND}/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "text/event-stream",
    },
    body: JSON.stringify({ query }),
  });
}