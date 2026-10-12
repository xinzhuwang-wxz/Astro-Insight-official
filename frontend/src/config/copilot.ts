import { ASTRO_BACKEND } from "@/config/backend";

export const COPILOT_RUNTIME_URL =
  process.env.NEXT_PUBLIC_COPILOT_RUNTIME_URL ||
  `${ASTRO_BACKEND}/query/stream`;

export const ASTRO_STREAM_URL =
  process.env.NEXT_PUBLIC_ASTRO_STREAM_URL ||
  `${ASTRO_BACKEND}/query/stream`;
