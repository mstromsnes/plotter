import socket
from time import perf_counter
import functools

HOST = "192.168.4.141"
PORT = 65431


def main():
    connect_and_query()


def connect_and_query():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        request = "cpu"
        start_time = perf_counter()
        current_time = perf_counter()
        i = 0
        while current_time - start_time < 10:
            send_request(request, s)
            handle_response(request, s)
            i += 1
            current_time = perf_counter()
        print(f"\n\n\nDid {i} loops")
        send_close(s)


def send_close(conn: socket.socket):
    conn.sendall(bytes("close\n", "utf-8"))


def send_request(request: str, conn: socket.socket):
    bytes_request = bytes(request + "\n", "utf-8")
    conn.sendall(bytes_request)


def handle_response(request: str, s: socket.socket):
    resp = s.recv(1024)
    resp_str = str(resp, "utf-8")
    print(f"{request.strip()}: {resp_str.strip()}")


def timer(func):
    """timefunc's doc"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """time_wrapper's doc string"""
        start = perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = perf_counter() - start
        print(f"Function: {func.__name__}, Time: {time_elapsed}")
        return result

    return wrapper


if __name__ == "__main__":
    main()
