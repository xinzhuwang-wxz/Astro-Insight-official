import { getAstroRuntimeConfig } from "@/lib/copilot-provider-adapter";

export function getCopilotRuntimeUrl() {
  return getAstroRuntimeConfig().runtimeUrl;
}

/**
 * Central runtime decision point.
 * Core providers should consume this instead of hardcoded URLs.
 */