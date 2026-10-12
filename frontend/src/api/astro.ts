import { ASTRO_BACKEND } from "@/config/backend";
import type { LLMApiFormat } from "@/models/llm";

export type LLMSettingsPayload = {
  provider: string;
  api_format?: LLMApiFormat;
  model: string;
  base_url?: string;
  api_key?: string;
};

async function readJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  let payload: unknown = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload && "detail" in payload
        ? String((payload as { detail?: unknown }).detail)
        : String(payload || response.statusText);
    throw new Error(`Backend ${response.status}: ${detail}`);
  }
  return payload as T;
}

export async function saveLLMSettings(config: LLMSettingsPayload) {
  const response = await fetch(`${ASTRO_BACKEND}/api/settings/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  return readJson(response);
}

export async function validateLLMSettings(config: LLMSettingsPayload) {
  const response = await fetch(`${ASTRO_BACKEND}/api/settings/llm/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  return readJson(response);
}

export async function testLLMConnection() {
  const response = await fetch(`${ASTRO_BACKEND}/api/settings/llm/test`, {
    method: "POST",
  });
  return readJson<{
    success: boolean;
    provider: string;
    api_format: string;
    model: string;
    response: string;
  }>(response);
}

export async function loadLLMSettings() {
  const response = await fetch(`${ASTRO_BACKEND}/api/settings/llm`);
  return readJson<LLMSettingsPayload & { has_api_key?: boolean }>(response);
}

export async function loadUsage() {
  const response = await fetch(`${ASTRO_BACKEND}/api/usage`);
  return readJson(response);
}
