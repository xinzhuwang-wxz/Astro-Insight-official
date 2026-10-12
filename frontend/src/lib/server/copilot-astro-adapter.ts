import { createAstroEvent } from "./astro-events";

export function adaptAstroOutput(raw: unknown) {
  return createAstroEvent(raw);
}