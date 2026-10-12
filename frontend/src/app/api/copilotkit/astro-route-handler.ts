import { proxyAstroStream } from "./astro-proxy";

/**
 * Candidate route implementation.
 *
 * Keeps the existing CopilotKit route untouched until the installed
 * protocol is verified.
 */
export async function POST(request: Request) {
  const body = await request.json();
  const response = await proxyAstroStream(body);

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
    },
  });
}