from datetime import datetime

import numpy as np
from scipy.ndimage.filters import median_filter
from sources.dataloader import DataLoader, DataNotReadyException

from .apiclient import download_historic_from_station_between_interval

INDRE_ARNA = "SN50830"


class YrHistoric(DataLoader):
    def initial_load(self) -> None:
        self.response = download_historic_from_station_between_interval(
            INDRE_ARNA, datetime(2023, 1, 1), datetime.now(), "P1D"
        )
        self.data = self.response["data"]
        length = len(self.data)
        self._time = np.zeros(length, dtype="datetime64[s]")
        self._temperature = np.zeros(length, dtype=np.float32)
        self._humidity = np.zeros(length, dtype=np.float32)
        for i, entry in enumerate(self.data):
            observerations = entry["observations"]
            for obs in observerations:
                match obs["elementId"]:
                    case "air_temperature":
                        self._temperature[i] = obs["value"]
                    case "relative_humidity":
                        self._humidity[i] = obs["value"]
            time = np.datetime64(entry["referenceTime"])
            self._time[i] = time
        self.filter_data()
        print("Data ready")

    @property
    def time(self):
        try:
            return self._time
        except AttributeError:
            raise DataNotReadyException

    @property
    def temperature(self):
        try:
            return self._temperature
        except AttributeError:
            raise DataNotReadyException

    @property
    def humidity(self):
        try:
            return self._humidity
        except AttributeError:
            raise DataNotReadyException

    def filter_data(self):
        self._humidity = median_filter(self.humidity, 5)
        self._temperature = median_filter(self.temperature, 5)

    def update_data(self) -> None:
        pass
