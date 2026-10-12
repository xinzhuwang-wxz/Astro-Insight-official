# Production bring-up checklist

1. Install backend requirements in a clean virtual environment.
2. Start the backend and confirm `GET /health` returns HTTP 200 (`ok` or expected pre-key `degraded`).
3. Start the frontend, open LLM settings, choose `openai`, `anthropic`, or `auto`, then save the real model/base URL/key.
4. Run **Validate** first; it does not spend tokens. Run **Test API** next; it makes one minimal real request.
5. Exercise one normal `/query/stream` conversation and one tool-using agent path.
6. Run `pnpm --dir frontend build` and fix any environment-specific Next dependency/build issue.
7. Run `cargo check --manifest-path src-tauri/Cargo.toml`, then the Tauri production build.
8. Confirm the packaged desktop app can reach the backend URL selected for production.
9. Verify `backend/runtime/llm_settings.json` is not committed or included in distributable source archives after a real key has been entered.
