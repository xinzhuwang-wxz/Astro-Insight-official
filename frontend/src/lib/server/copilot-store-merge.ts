import { appendAstroOutput } from "./astro-output-store";

export function mergeCopilotAndAstroEvents(
  current: unknown[],
  event: unknown
) {
  return appendAstroOutput(current, event);
}