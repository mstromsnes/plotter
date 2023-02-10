import socketclient
import numpy as np
from typing import Iterable
from datatypes import DataType, DataHandler, DataSet
from datetime import datetime
from enum import Enum, auto


def _changed_points_only(func):
    last_point: dict[DataType, DataStore.DataPoint] = {}

    def wrapper(self, datatype: DataType, datapoint: "DataStore.DataPoint"):
        nonlocal last_point
        if (
            last_point.get(datatype) is not None
            and last_point[datatype][1] != datapoint[1]
        ):
            func(self, datatype, last_point[datatype])
            func(self, datatype, datapoint)
        if last_point.get(datatype) is None:
            func(self, datatype, datapoint)
        last_point[datatype] = datapoint

    return wrapper


class DataStore:
    DataPoint = tuple[datetime, int | float]

    def __init__(self):
        time_array = np.zeros(1024, dtype=datetime)
        float_array = np.zeros(1024, dtype=float)
        int_array = np.zeros(1024, dtype=int)
        self._data: dict[DataType, tuple[np.ndarray, np.ndarray, int]] = {
            DataType.CPU_TEMP: (np.copy(time_array), np.copy(float_array), 0)
        }

    @_changed_points_only
    def append(self, data_type: DataType, data_point: DataPoint):
        time_array, data_array, cnt = self._data[data_type]
        while cnt + 1 >= data_array.size:
            self._resize_array(data_type)
            _, data_array, cnt = self._data[data_type]
        self._add_data_point(data_type, data_point)

    def extend(self, data_type: DataType, data_range: tuple[Iterable, Iterable]):
        time_array, data_array, cnt = self._data[data_type]
        new_time, new_data = data_range
        new_data_array = np.array(new_data)
        new_time_array = np.array(new_time)
        while new_data_array.size + cnt >= data_array.size:
            self._resize_array(data_type)
            _, data_array, cnt = self._data[data_type]
        self._add_data_range(data_type, (new_time_array, new_data_array))

    def overwrite_data(self, data_type, timestamp_array, data_array):
        self._data[data_type] = (timestamp_array, data_array, data_array.size)

    def _add_data_range(self, data_type: DataType, new_arrays: DataSet):
        time_array, data_array, cnt = self._data[data_type]
        new_time_array, new_data_array = new_arrays
        bool_array = np.ones(data_array.size, dtype=np.bool_)
        np.copyto(bool_array, np.zeros(cnt))
        np.copyto(time_array, new_time_array, where=bool_array)
        np.copyto(data_array, new_data_array, where=bool_array)
        cnt = cnt + new_data_array.size
        self._data[data_type] = (time_array, data_array, cnt)

    def _add_data_point(self, data_type: DataType, data_point: DataPoint):
        time_array, data_array, cnt = self._data[data_type]
        time, data = data_point
        time_array[cnt] = time
        data_array[cnt] = data
        cnt = cnt + 1
        self._data[data_type] = (time_array, data_array, cnt)

    def _resize_array(self, data_type: DataType):
        current_size = self._data[data_type][0].size
        new_size = 2 * current_size
        time_array, data_array, cnt = self._data[data_type]
        new_time_array = np.resize(time_array, new_size)
        new_data_array = np.resize(data_array, new_size)
        self._data[data_type] = (new_time_array, new_data_array, cnt)

    def get_data(self, data_type: DataType) -> DataSet:
        time, data, cnt = self._data[data_type]
        return time[:cnt], data[:cnt]


class DataSource(Enum):
    Socket = auto()
    Archive = auto()


class DataMediator:
    def __init__(self, source: DataSource):
        self.source = source
        self._socketclient = None
        self._datastore = DataStore()
        self._archive: dict[DataType, tuple[str, str]] = {}

    def connect(self, host, port):
        if self.source is DataSource.Socket:
            self._socketclient = socketclient.Client(host, port)

    def disconnect(self):
        self._socketclient = None

    def set_archive(self, data_type: DataType, timestamp_file, data_file):
        self._archive[data_type] = (timestamp_file, data_file)

    @property
    def client(self):
        return self._socketclient

    def get_data(self, data_type: DataType) -> DataSet:
        return self._datastore.get_data(data_type)

    def is_connected(self):
        return True if self._socketclient is not None else False

    def gather_data(self, request: DataType):
        match self.source:
            case DataSource.Socket:
                if self._socketclient is not None:
                    timestamp, value = self._socketclient.get_value(request.request())

                    self._datastore.append(
                        request, (timestamp, request.datatype(value))
                    )
            case DataSource.Archive:
                if self._archive.get(request) is not None:
                    time_file, data_file = self._archive[request]
                    time = np.load(time_file)
                    data = np.load(data_file)
                    self._datastore.overwrite_data(request, time, data)
