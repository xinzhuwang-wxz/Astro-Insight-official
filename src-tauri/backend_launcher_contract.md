# Backend launcher contract

Expected desktop flow:

1. Tauri starts
2. Spawn local FastAPI backend
3. Poll /health
4. Launch frontend window

Not implemented here:
- Rust process manager
- packaged backend binary
- release signing