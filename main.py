from time import perf_counter
import functools
from PySide6 import QtGui, QtCore, QtWidgets
import mainwindow
from datamediator import DataMediator

HOST = "192.168.4.141"
PORT = 65431


def main():
    app = QtWidgets.QApplication()
    data_source = DataMediator()
    window = mainwindow.MainWindow(data_source)
    window.resize(800, 600)
    window.show()
    app.exec()
    # client = socketclient.Client(HOST, PORT)\player.html
    # request = "cpu"
    # start_time = perf_counter()
    # current_time = perf_counter()
    # i = 0
    # while current_time - start_time < 10:
    #     value, req = client.get_value(request)
    #     print(f"{req}: {value}")
    #     i += 1
    #     current_time = perf_counter()
    # print(f"\n\n\nDid {i} loops")


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
