import { updateCopilotOutput } from "./copilot-output-compat";

export function handleProductionEvent(
  state: unknown[],
  event: unknown
) {
  return updateCopilotOutput(state, event);
}