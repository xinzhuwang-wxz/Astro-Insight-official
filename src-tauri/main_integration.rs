/*
Tauri main integration point.

Expected:

tauri::Builder::default()
  .invoke_handler(
      tauri::generate_handler![
          backend_status,
          start_backend,
          stop_backend
      ]
  )

The exact placement depends on the existing generated Tauri main.rs.
*/