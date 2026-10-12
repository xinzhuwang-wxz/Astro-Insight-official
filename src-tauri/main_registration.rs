use crate::commands::{
    backend_status,
    start_backend,
    stop_backend,
};

// Add these commands to tauri::Builder::invoke_handler.
//
// .invoke_handler(tauri::generate_handler![
//    backend_status,
//    start_backend,
//    stop_backend,
// ])