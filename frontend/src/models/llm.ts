export type LLMApiFormat = "auto" | "openai" | "anthropic";

export type LLMProvider = {
  provider: string;
  api_format: LLMApiFormat;
  model: string;
  base_url?: string;
  api_key?: string;
  has_api_key?: boolean;
};

export const defaultLLMProvider: LLMProvider = {
  provider: "openai",
  api_format: "auto",
  model: "gpt-4o-mini",
};
