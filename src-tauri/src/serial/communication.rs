use crate::serial::types::*;
use crc::{Crc, CRC_16_MCRF4XX};
use serialport::{SerialPort, SerialPortType};
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::thread;
use tauri::{AppHandle, Emitter};

pub struct SerialCommunication {
    port: Option<Arc<Mutex<Box<dyn SerialPort>>>>,
    buffer: Arc<Mutex<VecDeque<u8>>>,
    connection_status: Arc<Mutex<ConnectionStatus>>,
    app_handle: AppHandle,
    crc: Crc<u16>,
    _listener_handle: Option<thread::JoinHandle<()>>,
    stop_signal: Arc<Mutex<bool>>,
}

impl SerialCommunication {
    pub fn new(app_handle: AppHandle) -> Self {
        Self {
            port: None,
            buffer: Arc::new(Mutex::new(VecDeque::new())),
            connection_status: Arc::new(Mutex::new(ConnectionStatus {
                connected: false,
                port: None,
                message: "未连接".to_string(),
                is_first_sender: false,
            })),
            app_handle,
            crc: Crc::<u16>::new(&CRC_16_MCRF4XX),
            _listener_handle: None,
            stop_signal: Arc::new(Mutex::new(false)),
        }
    }

    pub fn list_ports() -> Result<Vec<SerialPortInfo>, SerialError> {
        match serialport::available_ports() {
            Ok(ports) => {
                let port_info: Vec<SerialPortInfo> = ports
                    .iter()
                    .map(|port| SerialPortInfo {
                        port_name: port.port_name.clone(),
                        port_type: match &port.port_type {
                            SerialPortType::UsbPort(usb) => {
                                format!("USB (VID: {:04x}, PID: {:04x})", usb.vid, usb.pid)
                            }
                            SerialPortType::BluetoothPort => "Bluetooth".to_string(),
                            SerialPortType::PciPort => "PCI".to_string(),
                            SerialPortType::Unknown => "Unknown".to_string(),
                        },
                        description: port.port_name.clone(),
                    })
                    .collect();
                Ok(port_info)
            }
            Err(e) => Err(SerialError::PortOpenError(format!("获取串口列表失败: {}", e))),
        }
    }

    pub fn connect(&mut self, port_name: &str) -> Result<(), SerialError> {
        // 停止之前的监听线程
        self.stop_listener();

        match serialport::new(port_name, BAUD_RATE)
            .timeout(Duration::from_millis(100))
            .open()
        {
            Ok(port) => {
                self.port = Some(Arc::new(Mutex::new(port)));
                
                // 更新连接状态
                {
                    let mut status = self.connection_status.lock().unwrap();
                    status.connected = true;
                    status.port = Some(port_name.to_string());
                    status.message = format!("已连接到 {}", port_name);
                }

                // 启动监听线程
                self.start_listener();
                
                // 发送连接建立消息
                self.establish_connection();
                
                self.emit_status_update();
                Ok(())
            }
            Err(e) => {
                let error_msg = format!("连接串口 {} 失败: {}", port_name, e);
                {
                    let mut status = self.connection_status.lock().unwrap();
                    status.connected = false;
                    status.port = None;
                    status.message = error_msg.clone();
                }
                self.emit_status_update();
                Err(SerialError::PortOpenError(error_msg))
            }
        }
    }

    pub fn disconnect(&mut self) -> Result<(), SerialError> {
        self.stop_listener();
        self.port = None;
        
        {
            let mut status = self.connection_status.lock().unwrap();
            status.connected = false;
            status.port = None;
            status.message = "已断开连接".to_string();
            status.is_first_sender = false;
        }
        
        self.emit_status_update();
        Ok(())
    }

    pub fn send_data(&self, data: &str) -> Result<(), SerialError> {
        if let Some(port) = &self.port {
            let packet = self.pack_data(data.as_bytes());
            match port.lock() {
                Ok(mut port_guard) => {
                    port_guard.write_all(&packet)
                        .map_err(|e| SerialError::CommunicationError(e.to_string()))?;
                    port_guard.flush()
                        .map_err(|e| SerialError::CommunicationError(e.to_string()))?;
                    
                    // 发送数据事件
                    let message = SerialMessage {
                        timestamp: SystemTime::now()
                            .duration_since(UNIX_EPOCH)
                            .unwrap()
                            .as_millis() as u64,
                        data: data.to_string(),
                        message_type: MessageType::Data,
                    };
                    let _ = self.app_handle.emit("serial-data-sent", message);
                    
                    Ok(())
                }
                Err(_) => Err(SerialError::CommunicationError("无法获取串口锁".to_string())),
            }
        } else {
            Err(SerialError::NotConnected)
        }
    }

    pub fn get_status(&self) -> ConnectionStatus {
        self.connection_status.lock().unwrap().clone()
    }

    fn pack_data(&self, payload: &[u8]) -> Vec<u8> {
        let crc = self.crc.checksum(payload);
        let crc_bytes = crc.to_be_bytes();
        
        let mut packet = Vec::new();
        packet.push(HEADER);
        packet.extend_from_slice(payload);
        packet.extend_from_slice(&crc_bytes);
        packet.push(FOOTER);
        packet
    }

    fn start_listener(&mut self) {
        if let Some(port) = &self.port {
            let port_clone = port.clone();
            let buffer_clone = self.buffer.clone();
            let status_clone = self.connection_status.clone();
            let app_handle_clone = self.app_handle.clone();
            let stop_signal_clone = self.stop_signal.clone();
            let crc_clone = self.crc.clone();

            // 重置停止信号
            *self.stop_signal.lock().unwrap() = false;

            let handle = thread::spawn(move || {
                Self::listener_thread(
                    port_clone,
                    buffer_clone,
                    status_clone,
                    app_handle_clone,
                    stop_signal_clone,
                    crc_clone,
                );
            });

            self._listener_handle = Some(handle);
        }
    }

    fn stop_listener(&mut self) {
        // 设置停止信号
        *self.stop_signal.lock().unwrap() = true;

        // 等待线程结束
        if let Some(handle) = self._listener_handle.take() {
            let _ = handle.join();
        }
    }

    fn listener_thread(
        port: Arc<Mutex<Box<dyn SerialPort>>>,
        buffer: Arc<Mutex<VecDeque<u8>>>,
        connection_status: Arc<Mutex<ConnectionStatus>>,
        app_handle: AppHandle,
        stop_signal: Arc<Mutex<bool>>,
        crc: Crc<u16>,
    ) {
        let mut read_buffer = [0u8; 1024];
        
        loop {
            // 检查停止信号
            if *stop_signal.lock().unwrap() {
                break;
            }

            if let Ok(mut port_guard) = port.try_lock() {
                if let Ok(bytes_read) = port_guard.read(&mut read_buffer) {
                    if bytes_read > 0 {
                        let mut buffer_guard = buffer.lock().unwrap();
                        for &byte in &read_buffer[..bytes_read] {
                            buffer_guard.push_back(byte);
                        }
                        drop(buffer_guard);
                        
                        // 处理完整数据包
                        Self::process_packets(&buffer, &connection_status, &app_handle, &crc, &port);
                    }
                }
            }
            
            thread::sleep(Duration::from_millis(5));
        }
    }

    fn process_packets(
        buffer: &Arc<Mutex<VecDeque<u8>>>,
        connection_status: &Arc<Mutex<ConnectionStatus>>,
        app_handle: &AppHandle,
        crc: &Crc<u16>,
        port: &Arc<Mutex<Box<dyn SerialPort>>>,
    ) {
        loop {
            let packet = {
                let mut buffer_guard = buffer.lock().unwrap();
                Self::extract_packet(&mut buffer_guard)
            };

            match packet {
                Some(packet_data) => {
                    if let Some((payload, crc_correct)) = Self::unpack_packet(&packet_data, crc) {
                        if crc_correct {
                            Self::handle_valid_packet(&payload, connection_status, app_handle, port, crc);
                        } else {
                            // CRC 错误，发送重传请求
                            Self::send_control_message(port, crc, &[RETRANSMIT_REQUEST]);
                            let _ = app_handle.emit("serial-error", "CRC校验失败，请求重传");
                        }
                    }
                }
                None => break,
            }
        }
    }

    fn extract_packet(buffer: &mut VecDeque<u8>) -> Option<Vec<u8>> {
        // 查找包头
        let start_pos = buffer.iter().position(|&x| x == HEADER)?;
        
        // 移除包头之前的数据
        for _ in 0..start_pos {
            buffer.pop_front();
        }
        
        // 查找包尾
        let remaining: Vec<u8> = buffer.iter().cloned().collect();
        let end_pos = remaining[1..].iter().position(|&x| x == FOOTER)?;
        
        // 提取完整数据包
        let packet_length = end_pos + 2;
        let mut packet = Vec::new();
        for _ in 0..packet_length {
            if let Some(byte) = buffer.pop_front() {
                packet.push(byte);
            }
        }
        
        Some(packet)
    }

    fn unpack_packet(packet: &[u8], crc: &Crc<u16>) -> Option<(Vec<u8>, bool)> {
        if packet.len() < 5 || packet[0] != HEADER || packet[packet.len() - 1] != FOOTER {
            return None;
        }

        let payload_crc_segment = &packet[1..packet.len() - 1];
        if payload_crc_segment.len() < 2 {
            return None;
        }

        let received_crc_bytes = &payload_crc_segment[payload_crc_segment.len() - 2..];
        let potential_payload = &payload_crc_segment[..payload_crc_segment.len() - 2];

        if potential_payload.is_empty() {
            return None;
        }

        let received_crc = u16::from_be_bytes([received_crc_bytes[0], received_crc_bytes[1]]);
        let calculated_crc = crc.checksum(potential_payload);
        let crc_correct = received_crc == calculated_crc;

        Some((potential_payload.to_vec(), crc_correct))
    }

    fn handle_valid_packet(
        payload: &[u8],
        connection_status: &Arc<Mutex<ConnectionStatus>>,
        app_handle: &AppHandle,
        port: &Arc<Mutex<Box<dyn SerialPort>>>,
        crc: &Crc<u16>,
    ) {
        if payload == HI_BRO_PAYLOAD {
            // 收到连接请求，回复 WOW,MAN
            Self::send_control_message(port, crc, WOW_MAN_PAYLOAD);
            {
                let mut status = connection_status.lock().unwrap();
                status.is_first_sender = false;
                status.message = "连接已建立 (作为响应方)".to_string();
            }
            let _ = app_handle.emit("serial-status", connection_status.lock().unwrap().clone());
        } else if payload == WOW_MAN_PAYLOAD {
            // 收到连接响应
            {
                let mut status = connection_status.lock().unwrap();
                status.is_first_sender = true;
                status.message = "连接已建立 (作为发起方)".to_string();
            }
            let _ = app_handle.emit("serial-status", connection_status.lock().unwrap().clone());
        } else if payload == &[TRANSMIT_SUCCESS] {
            // 发送成功确认
            let _ = app_handle.emit("serial-ack", "传输成功");
        } else if payload == &[RETRANSMIT_REQUEST] {
            // 重传请求
            let _ = app_handle.emit("serial-nack", "收到重传请求");
        } else {
            // 普通数据
            Self::send_control_message(port, crc, &[TRANSMIT_SUCCESS]);
            let data_str = String::from_utf8_lossy(payload);
            
            let message = SerialMessage {
                timestamp: SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_millis() as u64,
                data: data_str.to_string(),
                message_type: MessageType::Data,
            };
            
            let _ = app_handle.emit("serial-data-received", message);
        }
    }

    fn send_control_message(
        port: &Arc<Mutex<Box<dyn SerialPort>>>,
        crc: &Crc<u16>,
        payload: &[u8],
    ) {
        let packet = Self::pack_data_static(payload, crc);
        if let Ok(mut port_guard) = port.lock() {
            let _ = port_guard.write_all(&packet);
            let _ = port_guard.flush();
        }
    }

    fn pack_data_static(payload: &[u8], crc: &Crc<u16>) -> Vec<u8> {
        let checksum = crc.checksum(payload);
        let crc_bytes = checksum.to_be_bytes();
        
        let mut packet = Vec::new();
        packet.push(HEADER);
        packet.extend_from_slice(payload);
        packet.extend_from_slice(&crc_bytes);
        packet.push(FOOTER);
        packet
    }

    fn establish_connection(&self) {
        if let Some(port) = &self.port {
            let packet = self.pack_data(HI_BRO_PAYLOAD);
            if let Ok(mut port_guard) = port.lock() {
                let _ = port_guard.write_all(&packet);
                let _ = port_guard.flush();
            }
        }
    }

    fn emit_status_update(&self) {
        let status = self.connection_status.lock().unwrap().clone();
        let _ = self.app_handle.emit("serial-status", status);
    }
}

impl Drop for SerialCommunication {
    fn drop(&mut self) {
        self.stop_listener();
    }
}
