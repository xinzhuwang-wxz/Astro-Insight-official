import { adaptAstroOutput } from "./copilot-astro-adapter";

export function appendAstroOutput(
  current: unknown[],
  incoming: unknown
) {
  return [
    ...current,
    adaptAstroOutput(incoming),
  ];
}