use std::process::{Child, Command};

pub struct BackendProcess {
    child: Option<Child>,
}

impl BackendProcess {
    pub fn new() -> Self {
        Self { child: None }
    }

    pub fn start(&mut self) {
        // Production implementation should spawn packaged FastAPI sidecar.
    }

    pub fn stop(&mut self) {
        // Cleanup child process.
    }
}