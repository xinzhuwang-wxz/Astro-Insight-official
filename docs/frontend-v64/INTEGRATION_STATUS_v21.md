# Astro Insight Integration v21

Implemented:
[x] Copilot runtime configuration separation
[x] LangGraph event -> UI label mapper

Important status:
- Existing CopilotKit layout remains preserved.
- Full protocol replacement is NOT claimed yet.
- Next step requires validating CopilotKit runtime version and connecting
  the actual chat component to Astro stream events.

Remaining:
- Replace placeholder public runtime configuration if required
- Connect AgentTimeline to chat state
- Tauri sidecar implementation