import { loadLLMSettings, saveLLMSettings, testLLMConnection, validateLLMSettings } from "@/api/astro";
import type { LLMApiFormat } from "@/models/llm";

export type LLMConfig = {
  provider: string;
  api_format?: LLMApiFormat;
  model: string;
  base_url?: string;
  api_key?: string;
};

export async function updateLLMConfig(config: LLMConfig) {
  return saveLLMSettings(config);
}

export async function validateLLMConfig(config: LLMConfig) {
  return validateLLMSettings(config);
}

export async function fetchLLMConfig() {
  return loadLLMSettings();
}

export async function testSavedLLMConnection() {
  return testLLMConnection();
}
