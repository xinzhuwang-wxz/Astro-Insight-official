# Astro Insight — API-format compatibility build

This source package combines the latest readable backend/frontend branches from the project and adds a shared LLM runtime that can use either:

- OpenAI-compatible Chat Completions APIs (`api_format=openai`)
- Anthropic-native Messages APIs (`api_format=anthropic`)
- automatic protocol selection (`api_format=auto`)

No production API key is bundled in this package.

## 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn api_service.main:app --host 0.0.0.0 --port 8000
```

The API can start in `degraded` mode before an LLM key is configured. Useful endpoints:

- `GET /health`
- `GET /api/settings/llm`
- `POST /api/settings/llm/validate` — local config validation; no model request
- `POST /api/settings/llm/test` — one real model request after a key is saved
- `POST /query/stream` — SSE agent stream

### OpenAI-compatible example

```json
{
  "provider": "openai",
  "api_format": "openai",
  "model": "gpt-4o-mini",
  "base_url": "https://api.openai.com/v1",
  "api_key": "YOUR_KEY"
}
```

The same protocol mode can be used for OpenAI-compatible providers such as compatible gateways, DeepSeek-style endpoints, or local OpenAI-compatible servers by changing provider/model/base URL.

### Anthropic-native example

```json
{
  "provider": "anthropic",
  "api_format": "anthropic",
  "model": "YOUR_CLAUDE_MODEL",
  "base_url": "https://api.anthropic.com",
  "api_key": "YOUR_KEY"
}
```

For Anthropic mode, enter the SDK base URL rather than the final `/v1/messages` endpoint. The backend also normalizes a pasted terminal `/v1` or `/v1/messages`.

## 2. Frontend

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm build
```

For local development, `.env.example` defaults to `http://127.0.0.1:8000`. For production, copy values from `.env.production.example` and point `NEXT_PUBLIC_ASTRO_BACKEND_URL` at the deployed backend.

The settings panel supports provider, API format, model, base URL, API key, local validation, save, and a real API connectivity test. Persisted API keys are not returned to the browser after saving.

## 3. Tauri

The Tauri config now invokes the frontend from the `frontend/` subdirectory and reads the static export from `frontend/dist`.

```bash
# from repository root, after Rust/Tauri prerequisites are installed
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend tauri build
```

The Copilot runtime is configured to call the FastAPI stream endpoint directly, so the static Next export no longer depends on a POST Route Handler.

## 4. Before production release

Fill the real API settings, use **Validate**, then **Save**, then **Test API**. After that, run the real frontend build and Tauri/Rust build in the production machine. See `VALIDATION_REPORT.md` for exactly what was and was not verified in the current environment.
