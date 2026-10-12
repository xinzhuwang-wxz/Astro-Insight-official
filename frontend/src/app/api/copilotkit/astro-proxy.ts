import { ASTRO_BACKEND } from "@/config/backend";

export async function proxyAstroStream(body: unknown) {
  return fetch(`${ASTRO_BACKEND}/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "text/event-stream",
    },
    body: JSON.stringify(body),
  });
}