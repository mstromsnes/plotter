from time import perf_counter
import functools
import socketclient

HOST = "192.168.4.141"
PORT = 65431


def main():
    client = socketclient.Client(HOST, PORT)
    request = "cpu"
    start_time = perf_counter()
    current_time = perf_counter()
    i = 0
    while current_time - start_time < 10:
        value, req = client.get_value(request)
        print(f"{req}: {value}")
        i += 1
        current_time = perf_counter()
    print(f"\n\n\nDid {i} loops")


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = perf_counter() - start
        print(f"Function: {func.__name__}, Time: {time_elapsed}")
        return result

    return wrapper


if __name__ == "__main__":
    main()
