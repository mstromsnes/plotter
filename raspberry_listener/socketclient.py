import socket
from datetime import datetime


class Client:
    def __init__(self, host: str, port: int):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))

    def send_close(self):
        self._send_request("close")

    def _send_request(self, request: str):
        bytes_request = bytes(request + "\n", "utf-8")
        self.conn.sendall(bytes_request)

    def _handle_response(self) -> tuple[datetime, str]:
        resp = self.conn.recv(1024)
        resp_str = str(resp, "utf-8")
        return datetime.now(), resp_str.strip()

    def get_value(self, request: str) -> tuple[datetime, str]:
        self._send_request(request)
        return self._handle_response()

    def __del__(self):
        self.send_close()
        self.conn.shutdown(0)
        self.conn.close()
