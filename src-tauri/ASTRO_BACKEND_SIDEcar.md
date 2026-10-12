Desktop startup plan:

Tauri
 |
 +-- start FastAPI sidecar
 |
 +-- wait for /health
 |
 +-- open Next.js UI

The backend remains local-only.