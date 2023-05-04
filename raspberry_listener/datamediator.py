import numpy as np
import pandas as pd
from datatypes import DataType, DataHandler, DataSet
from remotereader import LogDownloader
from datetime import datetime


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
        self._data: dict[DataHandler, tuple[np.ndarray, np.ndarray, int]] = dict()
        for type in DataType.to_set():
            self._data[type] = (
                np.copy(time_array),
                np.zeros(1024, dtype=type.datatype()),
                0,
            )

    @_changed_points_only
    def append(self, data_type: DataHandler, data_point: DataPoint):
        time_array, data_array, cnt = self._data[data_type]
        while cnt + 1 >= data_array.size:
            self._resize_array(data_type)
            _, data_array, cnt = self._data[data_type]
        self._add_data_point(data_type, data_point)

    def extend(self, data_type: DataHandler, data_range: DataSet):
        time_array, data_array, cnt = self._data[data_type]
        new_time, new_data = data_range
        new_data_array = np.array(new_data)
        new_time_array = np.array(new_time)
        while new_data_array.size + cnt >= data_array.size:
            self._resize_array(data_type)
            _, data_array, cnt = self._data[data_type]
        self._add_data_range(data_type, (new_time_array, new_data_array))

    def overwrite_data(self, data_type, timestamp_array, data_array):
        timestamp_array, data_array = self._drop_nan(timestamp_array, data_array)
        self._data[data_type] = (timestamp_array, data_array, data_array.size)

    def _drop_nan(self, timestamp_array, data_array):
        finite_data = np.isfinite(data_array)
        timestamp_array = timestamp_array[finite_data]
        data_array = data_array[finite_data]
        return timestamp_array, data_array

    def _add_data_range(self, data_type: DataHandler, new_arrays: DataSet):
        time_array, data_array, cnt = self._data[data_type]
        new_time_array, new_data_array = new_arrays
        bool_array = np.ones(data_array.size, dtype=np.bool_)
        np.copyto(bool_array, np.zeros(cnt))
        np.copyto(time_array, new_time_array, where=bool_array)
        np.copyto(data_array, new_data_array, where=bool_array)
        cnt = cnt + new_data_array.size
        self._data[data_type] = (time_array, data_array, cnt)

    def _add_data_point(self, data_type: DataHandler, data_point: DataPoint):
        time_array, data_array, cnt = self._data[data_type]
        time, data = data_point
        time_array[cnt] = time
        data_array[cnt] = data
        cnt = cnt + 1
        self._data[data_type] = (time_array, data_array, cnt)

    def _resize_array(self, data_type: DataHandler):
        current_size = self._data[data_type][0].size
        new_size = 2 * current_size
        time_array, data_array, cnt = self._data[data_type]
        new_time_array = np.resize(time_array, new_size)
        new_data_array = np.resize(data_array, new_size)
        self._data[data_type] = (new_time_array, new_data_array, cnt)

    def get_data(self, data_type: DataHandler) -> DataSet:
        time, data, cnt = self._data[data_type]
        return DataSet(time[:cnt], data[:cnt])


class DataMediator:
    def __init__(self):
        self.archive = LogDownloader()
        self._datastore = DataStore()

    def get_data(self, data_type: DataHandler) -> DataSet:
        return self._datastore.get_data(data_type)

    def gather_data(self, request: DataHandler):
        dataset = self._read_parquet_latest_archive()
        unpacked_dataset = self._unpack_dataframe(dataset)
        for df_name in request.dataframe_names:
            self._datastore.overwrite_data(
                request, unpacked_dataset["index"], unpacked_dataset[df_name]
            )

    def _read_parquet_latest_archive(self):
        """Pandas and parquet are used to archive the data. Pandas serve as the interface to parquet, a binary file format supporting compression suitable for storage.
        Pandas dataframes are not suitable for storing live incoming data, as adding new data is cumbersome. The unpacked numpy arrays are much more suitable for this.
        """
        return pd.read_parquet(self.archive.get_latest_archive())

    @staticmethod
    def _unpack_dataframe(dataframe: pd.DataFrame):
        df_as_dict = {}
        df_as_dict["index"] = dataframe.index.to_numpy(dtype=np.datetime64)
        for datatype in DataType.to_set():
            for column in datatype.dataframe_names:
                if column in dataframe.columns:
                    dtype = datatype.datatype()
                    df_as_dict[column] = dataframe[column].to_numpy(dtype=dtype)

        return df_as_dict
