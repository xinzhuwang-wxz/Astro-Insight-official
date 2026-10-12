import { COPILOT_RUNTIME_URL } from "@/config/copilot";

/**
 * Copilot runtime boundary.
 *
 * The desktop/static build talks directly to the FastAPI SSE endpoint instead
 * of depending on a Next.js POST Route Handler, which is incompatible with
 * `output: "export"`.
 */
export function getAstroRuntimeConfig() {
  return { runtimeUrl: COPILOT_RUNTIME_URL };
}
