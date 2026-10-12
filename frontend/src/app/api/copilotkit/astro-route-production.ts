import { proxyAstroStream } from "./astro-proxy";
import { sseHeaders, runtimeError } from "./astro-runtime-utils";

export async function handleAstroCopilotRequest(request: Request) {
  try {
    const body = await request.json();
    const response = await proxyAstroStream(body);

    return new Response(response.body, {
      status: response.status,
      headers: sseHeaders(),
    });
  } catch (error) {
    return runtimeError(
      error instanceof Error ? error.message : "Unknown runtime error"
    );
  }
}