"use client";

import { useEffect, useState } from "react";
import { fetchLLMConfig, testSavedLLMConnection, updateLLMConfig, validateLLMConfig } from "@/api/settings";
import { Button } from "@/components/ui/button";
import type { LLMApiFormat } from "@/models/llm";

// Tailwind 的 preflight 会把 button/input 的默认外观清掉（透明背景、无边框），
// 所以这里必须显式给样式，否则 Save 之类的按钮会渲染成一行纯文本。
const fieldClass =
  "w-full rounded-md border border-white/15 bg-white/5 px-3 py-2 text-sm text-white placeholder-white/40 outline-none transition [color-scheme:dark] focus:border-blue-400/60 focus:ring-1 focus:ring-blue-400/40";

const labelClass = "mb-1.5 block text-sm font-medium text-white/80";

export default function LLMSettingsPanel() {
  const [provider, setProvider] = useState("openai");
  const [apiFormat, setApiFormat] = useState<LLMApiFormat>("auto");
  const [model, setModel] = useState("gpt-4o-mini");
  const [baseUrl, setBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [hasStoredKey, setHasStoredKey] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchLLMConfig()
      .then((config) => {
        if (config.provider) setProvider(config.provider);
        if (config.api_format) setApiFormat(config.api_format);
        if (config.model) setModel(config.model);
        if (config.base_url) setBaseUrl(config.base_url);
        setHasStoredKey(Boolean(config.has_api_key));
      })
      .catch(() => {
        // The backend may not be running yet; the form remains editable.
      });
  }, []);

  const payload = () => ({
    provider,
    api_format: apiFormat,
    model,
    base_url: baseUrl,
    api_key: apiKey,
  });

  async function validate() {
    setStatus("Validating...");
    try {
      const result = (await validateLLMConfig(payload())) as {
        api_format?: string;
        runtime_dependency_installed?: boolean;
      };
      setStatus(
        `Protocol: ${result.api_format ?? apiFormat}; dependency: ${
          result.runtime_dependency_installed ? "ready" : "install required"
        }`,
      );
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Validation failed");
    }
  }

  async function testConnection() {
    setStatus("Testing API...");
    try {
      const result = await testSavedLLMConnection();
      setStatus(`API OK (${result.api_format}): ${result.response}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "API test failed");
    }
  }

  async function save() {
    setStatus("Saving...");
    try {
      await updateLLMConfig(payload());
      if (apiKey) setHasStoredKey(true);
      setApiKey("");
      setStatus("Saved");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Save failed");
    }
  }

  return (
    <div className="max-w-xl space-y-4">
      <div>
        <label className={labelClass} htmlFor="llm-provider">
          Provider
        </label>
        <input
          id="llm-provider"
          className={fieldClass}
          value={provider}
          onChange={(event) => setProvider(event.target.value)}
          placeholder="openai / claude / deepseek / custom"
        />
      </div>

      <div>
        <label className={labelClass} htmlFor="llm-api-format">
          API Format
        </label>
        <select
          id="llm-api-format"
          className={fieldClass}
          value={apiFormat}
          onChange={(event) => setApiFormat(event.target.value as LLMApiFormat)}
        >
          <option value="auto">Auto-detect API format</option>
          <option value="openai">OpenAI-compatible (Chat Completions)</option>
          <option value="anthropic">Anthropic-native (Messages API)</option>
        </select>
      </div>

      <div>
        <label className={labelClass} htmlFor="llm-model">
          Model
        </label>
        <input
          id="llm-model"
          className={fieldClass}
          value={model}
          onChange={(event) => setModel(event.target.value)}
          placeholder="Model"
        />
      </div>

      <div>
        <label className={labelClass} htmlFor="llm-base-url">
          Base URL
        </label>
        <input
          id="llm-base-url"
          className={fieldClass}
          value={baseUrl}
          onChange={(event) => setBaseUrl(event.target.value)}
          placeholder={
            apiFormat === "anthropic"
              ? "Base URL, e.g. https://api.anthropic.com"
              : "Base URL, e.g. https://api.openai.com/v1"
          }
        />
      </div>

      <div>
        <label className={labelClass} htmlFor="llm-api-key">
          API Key
          {hasStoredKey && (
            <span className="ml-2 rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs font-normal text-emerald-300">
              已保存
            </span>
          )}
        </label>
        <input
          id="llm-api-key"
          className={fieldClass}
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
          placeholder={hasStoredKey ? "留空则保留已保存的 key" : "API Key"}
          type="password"
          autoComplete="off"
        />
      </div>

      <div className="flex flex-wrap gap-2 pt-2">
        <Button type="button" variant="outline" onClick={validate}>
          Validate
        </Button>
        <Button type="button" onClick={save}>
          Save
        </Button>
        <Button type="button" variant="outline" onClick={testConnection}>
          Test API
        </Button>
      </div>

      {status && (
        <div className="rounded-md border border-white/15 bg-white/5 px-3 py-2 text-sm text-white/80">
          {status}
        </div>
      )}
    </div>
  );
}
