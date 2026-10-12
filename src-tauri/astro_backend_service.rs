pub struct AstroBackendService;

impl AstroBackendService {
    pub fn start() {
        // Start local FastAPI backend.
        // Real process spawning depends on packaged sidecar path.
    }

    pub fn stop() {
        // Cleanup backend process.
    }

    pub fn status() -> &'static str {
        "unknown"
    }
}