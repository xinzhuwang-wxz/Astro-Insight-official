# Tauri Backend Sidecar Plan

Desktop startup lifecycle:

1. Tauri application starts
2. Spawn FastAPI backend process
3. Wait for health endpoint
4. Start Next.js frontend window
5. Shutdown backend when app exits

Recommended production:
- Package Python backend with PyInstaller
- Use Tauri sidecar binaries
- Keep API endpoint local only