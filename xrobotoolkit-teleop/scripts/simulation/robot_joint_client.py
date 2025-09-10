import zmq
import json
import numpy as np
import time

class ZMQClient:
    def __init__(self, server_addr="tcp://127.0.0.1:8989"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.LINGER, 0)  # 防止程序退出时阻塞
        self.socket.setsockopt(zmq.SNDHWM, 1)  # 设置高水位防止内存堆积
        self.server_addr = server_addr
        self.connect()
        
    def connect(self):
        """建立长连接"""
        print(f"Connecting to server at {self.server_addr}...")
        self.socket.connect(self.server_addr)
        
    def send_data(self, mode="restart", data=None):
        """
        发送数据到服务端
        :param mode: 操作模式
        :param data: numpy数组或可迭代数据，None则发送全零数组
        """
        if data is None:
            data = np.zeros(32)
        elif not isinstance(data, np.ndarray):
            data = np.array(data)
            
        message = {
            "mode": mode,
            "data": data.tolist()  # 转换为Python列表
        }
        
        try:
            self.socket.send_string(json.dumps(message))
            # print(f"Message sent (mode: {mode}, data shape: {data.shape})")
            return True
        except Exception as e:
            print(f"Send failed: {str(e)}")
            self.reconnect()  # 尝试重连
            return False
            
    def reconnect(self):
        """重新连接"""
        self.socket.close()
        self.socket = self.context.socket(zmq.PUSH)
        self.connect()
        
    def close(self):
        """关闭连接"""
        self.socket.close()
        self.context.term()
        print("Connection closed")
