import zmq
import json
import numpy as np
import threading
import time
from typing import Dict, Any
import pathlib
import sys
HOME_PATH = str(pathlib.Path("../").parent.resolve())
sys.path.append(HOME_PATH)
from Mujoco_env.envs.h1_ik import make_sim_env

CONTROL_FREQ = 100  # 控制频率(Hz)
CONTROL_DT = 1.0 / CONTROL_FREQ  # 控制时间间隔(s)

class ZMQServer:
    def __init__(self, ip: str = "127.0.0.1", port: int = 8989):

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.ip = ip
        self.port = port
        self.running = False
        self.thread = None  # 用于存储监听线程
        self.start()
        self.joint_data=np.zeros(32)
        self.reset_flag=False
    def start(self) -> None:
        if self.running:
            print("Server is already running!")
            return

        addr = f"tcp://{self.ip}:{self.port}"
        print(f"Starting ZMQ server on {addr}")
        
        try:
            self.socket.bind(addr)
            self.socket.setsockopt(zmq.RCVHWM, 10)  # 设置接收高水位防止内存堆积
            self.running = True
            
            # 启动监听线程
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()
            
            print("Server started successfully.")
        except zmq.ZMQError as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    def _listen(self) -> None:

        while self.running:
            try:
                message = self.socket.recv_string()
                self._process_message(message)
            except zmq.ZMQError as e:
                if self.running:  # 如果是主动关闭导致的错误则忽略
                    print(f"ZMQ error: {str(e)}")
                break
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue

    def _process_message(self, message: str) -> None:
        try:
            data: Dict[str, Any] = json.loads(message)
            
            # 验证消息结构
            if not all(k in data for k in ["mode", "data"]):
                raise ValueError("Invalid message format: missing 'mode' or 'data'")
                
            # 转换为 numpy 数组
            np_data = np.array(data["data"], dtype=np.float32)
            np.set_printoptions(precision=4, suppress=True)
            
            # 根据模式处理
            if data["mode"] == "eval":
                self.reset_flag=False
                self.joint_data=np_data
                # print(f"[EVAL] Received data shape: {np_data.shape}")
            elif data["mode"] == "reset":
                self.reset_flag=True
                # print("Resetting environment...")
            else:
                print(f"Unknown mode: {data['mode']}")
                
        except json.JSONDecodeError:
            print("Error: Invalid JSON received")
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def stop(self) -> None:
        if not self.running:
            return
            
        print("Shutting down server...")
        self.running = False
        
        try:
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)  # 等待线程结束
        except Exception as e:
            print(f"Error stopping thread: {str(e)}")
        finally:
            self.socket.close()
            self.context.term()
            print("Server stopped.")

if __name__ == "__main__":
    server = ZMQServer()
    env = make_sim_env(freq=CONTROL_FREQ)
    try:
        while True:
            # print(server.joint_data)
            step_data=np.zeros(17)
            step_data[0:17]=server.joint_data[0:17].copy() #7+7+1
            # step_data[15]=0.0 #left hand
            # step_data[16]=0.0 #right hand
            env.step_all_simple(step_data)
            if(server.reset_flag):
                env.reset()

    except KeyboardInterrupt:
        print("\nUser interrupted.")
        exit(0)
    finally:
        server.stop()  # 确保服务器正确关闭