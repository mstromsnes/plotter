import socketclient
import numpy as np
from enum import Enum, auto
from typing import Iterable


class DataType(Enum):
    CPU_TEMP = auto()


class DataStore:
    def __init__(self):
        self._data: dict[DataType, tuple[np.ndarray, int]] = {
            DataType.CPU_TEMP: (np.zeros(1024), 0)
        }

    def append(self, data_type: DataType, data_point: int | float):
        data_array, cnt = self._data[data_type]
        while cnt + 1 >= data_array.size:
            self._resize_array(data_type)
        self._add_data_point(data_type, data_point)

    def extend(self, data_type, data_range: Iterable):
        data_array, cnt = self._data[data_type]
        new_data_array = np.array(data_range)
        while new_data_array.size + cnt >= data_array.size:
            self._resize_array(data_type)
        self._add_data_range(data_type, new_data_array)

    def _add_data_range(self, data_type: DataType, new_data_array: np.ndarray):
        data_array, cnt = self._data[data_type]
        bool_array = np.ones(data_array.size, dtype=np.bool_)
        np.copyto(bool_array, np.zeros(cnt))
        np.copyto(data_array, new_data_array, where=bool_array)
        cnt = cnt + new_data_array.size
        self._data[data_type] = (data_array, cnt)

    def _add_data_point(self, data_type, data_point):
        array, cnt = self._data[data_type]
        array[cnt] = data_point
        cnt = cnt + 1
        self._data[data_type] = (array, cnt)

    def _resize_array(self, data_type: DataType):
        current_size = self._data[data_type][0].size
        new_size = 2 * current_size
        self._data[data_type][0].resize(new_size)

    def get_data(self, data_type) -> tuple[np.ndarray, int]:
        return self._data[data_type]


class DataMediator:
    def __init__(self):
        self._socketclient = None
        self._datastore = DataStore()

    def connect(self, host, port):
        self._socketclient = socketclient.Client(host, port)

    def disconnect(self):
        self._socketclient = None

    @property
    def client(self):
        return self._socketclient

    def get_data(self, data_type) -> tuple[np.ndarray, int]:
        return self._datastore.get_data(data_type)

    def is_connected(self):
        return True if self._socketclient is not None else False
