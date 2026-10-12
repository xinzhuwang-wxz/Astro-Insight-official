#[tauri::command]
pub fn backend_status() -> String {
    "unknown".to_string()
}

#[tauri::command]
pub fn start_backend() -> String {
    "backend start requested".to_string()
}

#[tauri::command]
pub fn stop_backend() -> String {
    "backend stop requested".to_string()
}