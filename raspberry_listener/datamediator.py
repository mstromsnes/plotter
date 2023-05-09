import pandas as pd
from datatypes import DataSet
from pandera.typing import DataFrame
import pandera as pa

from datatypes import SensorData
from fastapi import HTTPException
from datatypes import Sensor, SensorType

from remotereader import get_latest_archive


class DataMediator:
    def __init__(self):
        self._dataframe: DataFrame[SensorData] = self._load_dataframe()

    @pa.check_types
    def _load_dataframe(self) -> DataFrame[SensorData]:
        try:
            dataframe = self._read_parquet_latest_archive()
        except HTTPException:
            dataframe = SensorData.example(size=0)
        return dataframe

    def get_data(self, sensor: Sensor, sensor_type: SensorType) -> DataSet:
        self._dataframe = self._dataframe.sort_index()
        series: pd.Series = self._dataframe.loc[sensor_type.value, sensor.value][
            "reading"
        ]
        timearray = series.index.to_numpy()
        dataarray = series.to_numpy()
        return DataSet(timearray, dataarray)

    def gather_data(self):
        self._dataframe = self._load_dataframe()

    @pa.check_types
    def _read_parquet_latest_archive(self) -> DataFrame[SensorData]:
        """Pandas and parquet are used to archive the data. Pandas serve as the interface to parquet, a binary file format supporting compression suitable for storage.
        Pandas dataframes are not suitable for storing live incoming data, as adding new data is cumbersome. The unpacked numpy arrays are much more suitable for this.
        """
        return pd.read_parquet(get_latest_archive())
