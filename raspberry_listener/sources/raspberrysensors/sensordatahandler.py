import datetime

import pandas as pd
import pandera as pa
from sources import (
    DataNotReadyException,
    FrameHandler,
)
from .datatypes import SensorData, SensorType, Sensor
from pandera.typing import DataFrame

from numpy import datetime64, floating
from numpy.typing import NDArray

from .remotereader import (
    ArchiveNotAvailableException,
    Format,
    HTTPException,
    download_archive,
)


class SensorDataFrameHandler(FrameHandler):
    def __init__(self):
        self._dataframe: DataFrame | None = None

    def get_data(
        self, keys: tuple[SensorType, Sensor]
    ) -> tuple[NDArray[datetime64], NDArray[floating]]:
        if self._dataframe is None:
            raise DataNotReadyException
        data = self._dataframe.loc[
            (*map(lambda enum: enum.value, keys), slice(None)), slice(None)
        ]
        time_data = data.index.get_level_values(2).to_numpy()
        temperature_data = data["reading"].to_numpy()
        return time_data, temperature_data

    def _load_dataframe(
        self, timestamp: pd.Timestamp | None = None
    ) -> DataFrame | None:
        def get_format(timestamp: pd.Timestamp | None) -> Format:
            if timestamp is None:
                return Format.Parquet
            timedelta = datetime.datetime.now() - timestamp
            if timedelta > pd.Timedelta(minutes=20):
                return Format.Parquet
            return Format.JSON

        try:
            format = get_format(timestamp)
            dataframe = self._read_archive(timestamp, format)
        except (HTTPException, ArchiveNotAvailableException):
            dataframe = None
        return dataframe

    @property
    def dataframe(self):
        if self._dataframe is None:
            raise DataNotReadyException
        return self._dataframe

    def initial_load(self):
        two_days_ago = pd.Timestamp(
            datetime.datetime.now() - datetime.timedelta(days=2)
        )
        self._dataframe = self._load_dataframe(two_days_ago)

    def update_data(self):
        if self._dataframe is None:
            self._dataframe = self._load_dataframe()
            return
        latest_available_timestamp = self._dataframe.sort_index().index[-1][-1]
        new_df = self._load_dataframe(latest_available_timestamp)
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
