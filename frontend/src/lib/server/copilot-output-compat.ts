import { processIncomingAstroEvent } from "./copilot-output-pipeline";

export function updateCopilotOutput(
  state: unknown[],
  incoming: unknown
) {
  return processIncomingAstroEvent(state, incoming);
}