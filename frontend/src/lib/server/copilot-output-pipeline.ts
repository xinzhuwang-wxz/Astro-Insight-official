import { mergeCopilotAndAstroEvents } from "./copilot-store-merge";

export function processIncomingAstroEvent(
  state: unknown[],
  event: unknown
) {
  return mergeCopilotAndAstroEvents(state, event);
}