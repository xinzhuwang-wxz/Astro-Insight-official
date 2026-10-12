use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SerialPortInfo {
    pub port_name: String,
    pub port_type: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConnectionStatus {
    pub connected: bool,
    pub port: Option<String>,
    pub message: String,
    pub is_first_sender: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SerialMessage {
    pub timestamp: u64,
    pub data: String,
    pub message_type: MessageType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessageType {
    Data,
    Control,
    Error,
    Status,
}

// 串口通信相关常量
pub const HEADER: u8 = 255;
pub const FOOTER: u8 = 254;
pub const RETRANSMIT_REQUEST: u8 = 253;
pub const TRANSMIT_SUCCESS: u8 = 252;
pub const HI_BRO_PAYLOAD: &[u8] = b"HI,BRO";
pub const WOW_MAN_PAYLOAD: &[u8] = b"WOW,MAN";
pub const BAUD_RATE: u32 = 115200;

#[derive(Debug, thiserror::Error)]
pub enum SerialError {
    #[error("串口打开失败: {0}")]
    PortOpenError(String),
    #[error("串口通信错误: {0}")]
    CommunicationError(String),
    #[error("串口未连接")]
    NotConnected,
}
