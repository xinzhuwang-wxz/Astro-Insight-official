# v33 Core Integration

Changes:
- Moved runtime selection into a single frontend core boundary.
- Reviewed app layout entry.
- Preserved provider ordering while preparing runtime replacement.

Next actual core edits:
- Replace hardcoded Copilot runtime in the active provider.
- Wire chat UI submit handler to Astro stream.
- Implement Tauri Rust lifecycle.