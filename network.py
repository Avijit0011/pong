import socket
import json
import threading
import time

DEFAULT_PORT = 5555

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def trigger_firewall_prompt():
    """
    Pre-binds a temporary socket on 0.0.0.0 so Windows OS triggers the
    'Windows Defender Firewall - Allow App Access' dialog on startup.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 0))
        s.listen(1)
        s.close()
    except Exception:
        pass

class NetworkServer:
    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None
        self.is_running = False
        self.is_connected = False
        self.latest_client_input = {"up": False, "down": False, "ready": False, "chat_msg": ""}
        self.incoming_chat_queue = []
        self.lock = threading.Lock()

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            self.server_socket.settimeout(1.0)
            self.is_running = True
            
            thread = threading.Thread(target=self._listen_loop, daemon=True)
            thread.start()
            return True, f"Server started on port {self.port}"
        except Exception as e:
            return False, f"Failed to start server: {e}"

    def _listen_loop(self):
        while self.is_running and not self.is_connected:
            try:
                client, addr = self.server_socket.accept()
                self.client_socket = client
                self.client_addr = addr
                self.is_connected = True
                self.client_socket.setblocking(False)
                
                recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                recv_thread.start()
                break
            except socket.timeout:
                continue
            except Exception:
                break

    def _recv_loop(self):
        buffer = ""
        while self.is_running and self.is_connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    self.is_connected = False
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            with self.lock:
                                self.latest_client_input["up"] = msg.get("up", False)
                                self.latest_client_input["down"] = msg.get("down", False)
                                self.latest_client_input["ready"] = msg.get("ready", False)
                                if msg.get("chat_msg"):
                                    self.incoming_chat_queue.append(msg["chat_msg"])
                        except json.JSONDecodeError:
                            pass
            except BlockingIOError:
                time.sleep(0.005)
            except Exception:
                self.is_connected = False
                break

    def broadcast_state(self, state_dict):
        if not self.is_connected or not self.client_socket:
            return False
        try:
            payload = (json.dumps(state_dict) + '\n').encode('utf-8')
            self.client_socket.sendall(payload)
            return True
        except Exception:
            self.is_connected = False
            return False

    def get_client_input(self):
        with self.lock:
            return dict(self.latest_client_input)

    def pop_incoming_chat(self):
        with self.lock:
            messages = list(self.incoming_chat_queue)
            self.incoming_chat_queue.clear()
            return messages

    def stop(self):
        self.is_running = False
        self.is_connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass


class NetworkClient:
    def __init__(self):
        self.socket = None
        self.is_connected = False
        self.latest_game_state = None
        self.incoming_chat_queue = []
        self.lock = threading.Lock()
        self.is_running = False

    def connect(self, host, port=DEFAULT_PORT):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3.0)
            self.socket.connect((host, port))
            self.socket.setblocking(False)
            self.is_connected = True
            self.is_running = True

            recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
            recv_thread.start()
            return True, f"Connected to {host}:{port}"
        except Exception as e:
            self.is_connected = False
            return False, f"Connection failed: {e}"

    def _recv_loop(self):
        buffer = ""
        while self.is_running and self.is_connected:
            try:
                data = self.socket.recv(8192)
                if not data:
                    self.is_connected = False
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            state = json.loads(line)
                            with self.lock:
                                self.latest_game_state = state
                                if "chat_broadcast" in state and state["chat_broadcast"]:
                                    self.incoming_chat_queue.extend(state["chat_broadcast"])
                        except json.JSONDecodeError:
                            pass
            except BlockingIOError:
                time.sleep(0.005)
            except Exception:
                self.is_connected = False
                break

    def send_input(self, input_dict):
        if not self.is_connected or not self.socket:
            return False
        try:
            payload = (json.dumps(input_dict) + '\n').encode('utf-8')
            self.socket.sendall(payload)
            return True
        except Exception:
            self.is_connected = False
            return False

    def get_game_state(self):
        with self.lock:
            return self.latest_game_state

    def pop_incoming_chat(self):
        with self.lock:
            messages = list(self.incoming_chat_queue)
            self.incoming_chat_queue.clear()
            return messages

    def disconnect(self):
        self.is_running = False
        self.is_connected = False
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
