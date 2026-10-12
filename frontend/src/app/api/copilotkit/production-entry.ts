import { handleAstroCopilotRequest } from "./astro-route-production";

/**
 * Production Copilot entry point.
 * The existing framework route can delegate here.
 */
export async function POST(request: Request) {
  return handleAstroCopilotRequest(request);
}