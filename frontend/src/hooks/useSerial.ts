export const useSerial = () => {
  // 串口功能已移除；保留占位实现以避免历史引用报错
  return {
    ports: [],
    status: { connected: false, port: null, message: "串口功能已移除", is_first_sender: false },
    receivedMessages: [],
    sentMessages: [],
    loading: false,
    errors: [],
    notifications: [],
    listPorts: async () => [],
    refreshPorts: async () => [],
    connect: async () => ({ connected: false, port: null, message: "不可用", is_first_sender: false }),
    disconnect: async () => ({ connected: false, port: null, message: "不可用", is_first_sender: false }),
    sendData: async () => {},
    getStatus: async () => ({ connected: false, port: null, message: "不可用", is_first_sender: false }),
    autoDetectAndConnect: async () => ({ connected: false, port: null, message: "不可用", is_first_sender: false }),
    clearNotifications: () => {},
    clearErrors: () => {},
  } as const;
};
