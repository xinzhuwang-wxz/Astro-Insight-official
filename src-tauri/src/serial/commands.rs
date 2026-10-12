use crate::serial::{communication::SerialCommunication, types::*};
use std::sync::Mutex;
use tauri::{AppHandle, State, Emitter};

pub struct SerialState {
    pub comm: Mutex<Option<SerialCommunication>>,
}

#[tauri::command]
pub async fn list_serial_ports() -> Result<Vec<SerialPortInfo>, String> {
    SerialCommunication::list_ports().map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn connect_serial_port(
    port_name: String,
    state: State<'_, SerialState>,
    app_handle: AppHandle,
) -> Result<ConnectionStatus, String> {
    let mut comm_guard = state.comm.lock().unwrap();
    let mut comm = SerialCommunication::new(app_handle.clone());
    
    match comm.connect(&port_name) {
        Ok(_) => {
            let status = comm.get_status();
            *comm_guard = Some(comm);
            
            // 发送连接成功事件
            let _ = app_handle.emit("serial-connection-success", &status);
            Ok(status)
        }
        Err(e) => {
            let error_msg = e.to_string();
            // 发送连接失败事件
            let _ = app_handle.emit("serial-connection-error", &error_msg);
            Err(error_msg)
        }
    }
}

#[tauri::command]
pub async fn disconnect_serial_port(
    state: State<'_, SerialState>,
    app_handle: AppHandle,
) -> Result<ConnectionStatus, String> {
    let mut comm_guard = state.comm.lock().unwrap();
    
    if let Some(ref mut comm) = *comm_guard {
        match comm.disconnect() {
            Ok(_) => {
                let status = comm.get_status();
                *comm_guard = None;
                
                // 发送断开连接事件
                let _ = app_handle.emit("serial-disconnection", &status);
                Ok(status)
            }
            Err(e) => Err(e.to_string()),
        }
    } else {
        Err("没有活动的串口连接".to_string())
    }
}

#[tauri::command]
pub async fn get_serial_status(
    state: State<'_, SerialState>,
) -> Result<ConnectionStatus, String> {
    let comm_guard = state.comm.lock().unwrap();
    
    if let Some(ref comm) = *comm_guard {
        Ok(comm.get_status())
    } else {
        Ok(ConnectionStatus {
            connected: false,
            port: None,
            message: "未连接".to_string(),
            is_first_sender: false,
        })
    }
}

#[tauri::command]
pub async fn send_serial_data(
    data: String,
    state: State<'_, SerialState>,
) -> Result<(), String> {
    let comm_guard = state.comm.lock().unwrap();
    
    if let Some(ref comm) = *comm_guard {
        comm.send_data(&data).map_err(|e| e.to_string())
    } else {
        Err("串口未连接".to_string())
    }
}

#[tauri::command]
pub async fn auto_detect_and_connect(
    state: State<'_, SerialState>,
    app_handle: AppHandle,
) -> Result<ConnectionStatus, String> {
    let ports = SerialCommunication::list_ports().map_err(|e| e.to_string())?;
    
    if ports.is_empty() {
        let error_msg = "未找到可用的串口".to_string();
        let _ = app_handle.emit("serial-auto-detect-error", &error_msg);
        return Err(error_msg);
    }
    
    // 发送检测到的端口列表
    let _ = app_handle.emit("serial-ports-detected", &ports);
    
    // 尝试连接第一个可用串口
    let first_port = &ports[0];
    let _ = app_handle.emit("serial-auto-connect-attempt", &first_port.port_name);
    
    connect_serial_port(first_port.port_name.clone(), state, app_handle).await
}

#[tauri::command]
pub async fn refresh_serial_ports(
    app_handle: AppHandle,
) -> Result<Vec<SerialPortInfo>, String> {
    match SerialCommunication::list_ports() {
        Ok(ports) => {
            let _ = app_handle.emit("serial-ports-refreshed", &ports);
            Ok(ports)
        }
        Err(e) => {
            let error_msg = e.to_string();
            let _ = app_handle.emit("serial-refresh-error", &error_msg);
            Err(error_msg)
        }
    }
}
