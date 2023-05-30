import pandas as pd
from datatypes import DataSet
from pandera.typing import DataFrame
import pandera as pa


from datatypes import SensorData
from fastapi import HTTPException
from datatypes import Sensor, SensorType
from remotereader import Format
from remotereader import (
    download_archive,
    ArchiveNotAvailableException,
)


class DataNotReadyException(Exception):
    ...


class DataMediator:
    def __init__(self):
        self._dataframe: DataFrame | None = self._load_dataframe()

    def _load_dataframe(
        self, timestamp: pd.Timestamp | None = None
    ) -> DataFrame | None:
        try:
            format = Format.Parquet if timestamp is None else Format.JSON
            dataframe = self._read_archive(timestamp, format)
        except (HTTPException, ArchiveNotAvailableException):
            dataframe = None
        return dataframe

    @property
    def dataframe(self):
        if self._dataframe is None:
            raise DataNotReadyException
        return self._dataframe

    def get_data(self, sensor: Sensor, sensor_type: SensorType) -> DataSet | None:
        if self._dataframe is None:
            return None
        self._dataframe = self._dataframe.sort_index()
        series: pd.Series = self._dataframe.loc[sensor_type.value, sensor.value][
            "reading"
        ]
        timearray = series.index.to_numpy()
        dataarray = series.to_numpy()
        return DataSet(timearray, dataarray)

    def merge_new_data_into_dataframe(self):
        if self._dataframe is None:
            self._dataframe = self._load_dataframe()
            return
        timestamp = self._dataframe.sort_index().index[-1][-1]
        new_df = self._load_dataframe(timestamp)
        self._dataframe = pd.concat((self._dataframe, new_df)).sort_index()

    @pa.check_types
    def _read_archive(
        self, timestamp: pd.Timestamp | None = None, format: Format = Format.Parquet
    ) -> DataFrame[SensorData]:
        """The data is stored in a pandas dataframe. Parquet is used to serialize the dataframe for initial transfer. Parquet is suitable for large dataframes, but the incremental updates are small.
        Parquet has too much overhead for small incremental updates. JSON serialization is used instead. Pandas allows several ways to serialize with json. Using orient=table lets us preserve the index correctly.
        """
        raw_archive = download_archive(timestamp, format)
        match format:
            case Format.Parquet:
                df = pd.read_parquet(raw_archive)
                df = SensorData.repair_dataframe(df).sort_index()
                return df
            case Format.JSON:
                return pd.read_json(raw_archive, orient="table").sort_index()
            case _:
                raise TypeError("Format not supported")
