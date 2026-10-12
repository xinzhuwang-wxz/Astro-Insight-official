# Validation report

## Passed in the current environment

- Backend whole-tree syntax compilation: `python -m compileall -q backend`
- LLM API-format/unit contracts: OpenAI-compatible and Anthropic-native selection, auto inference, saved settings, invalid-format rejection
- Stream input contracts: native query, OpenAI-style messages, Anthropic text content blocks, nested Copilot-style input
- Stream route mock smoke test including SSE response and thread/session mapping
- LLM settings secret masking and blank-key preservation
- Frontend TypeScript full-tree syntax parse: `tsc --project tsconfig.json --noCheck --noEmit`
- Buffered SSE decoder split-chunk/CRLF behavior
- Canonical FastAPI no-key smoke: health/settings/protocol validation and invalid stream request handling
- Secret-pattern scan after removing the old local `.env`; no known bundled production-looking API key remains

Current focused pytest result: **12 passed**.

## API-format behavior now implemented

### OpenAI-compatible

Runtime: `langchain_openai.ChatOpenAI`

Expected base URL style: typically `https://.../v1`. The configured URL is preserved except for a trailing slash.

### Anthropic-native

Runtime: `langchain_anthropic.ChatAnthropic`

Expected base URL style: `https://api.anthropic.com` or the root of an Anthropic-compatible gateway. A terminal `/v1` or `/v1/messages` is normalized so the SDK does not double-append the Messages path.

### Auto

`provider=anthropic` or `provider=claude` selects Anthropic-native. Other providers default to OpenAI-compatible unless `api_format` is explicitly set.

## Not verified here

- A real OpenAI/Anthropic/provider request, because no production API key was supplied.
- `pnpm install` / `next build`, because this execution environment does not have the project dependencies installed and cannot fetch them from the network.
- `cargo check` / `tauri build`, because a Rust/Tauri toolchain is not available here.
- Provider-specific quirks of third-party gateways beyond the OpenAI-compatible / Anthropic-native contracts.

These should be the first production-machine checks after adding credentials and installing dependencies.
