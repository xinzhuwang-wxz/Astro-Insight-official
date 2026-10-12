import { handleAstroCopilotRequest } from "./astro-route-production";

export async function POST(request: Request) {
  return handleAstroCopilotRequest(request);
}