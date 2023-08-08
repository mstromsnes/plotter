from collections import Counter, namedtuple
from datetime import datetime, timedelta
from pprint import pprint

import numpy as np
from sources.dataloader import DataLoader

from .apiclient import Location, Variant, download_location

ARNA = Location(60.42203, 5.46824, 60)
OSLO = Location(59.91273, 10.74609, 5)


class YrForecast(DataLoader):
    def initial_load(self) -> None:
        self.data = download_location(ARNA, Variant.Compact)
        self.timeseries = self.data["properties"]["timeseries"]
        now = np.datetime64(datetime.now() + timedelta(days=2))
        length = self.count_timestamps_until_provided(now, self.timeseries)
        self.time = np.zeros(length, dtype="datetime64[s]")
        self.temperature = np.zeros(length, dtype=np.float16)
        self.humidity = np.zeros(length, dtype=np.float16)
        for i, entry in enumerate(self.timeseries):
            if i > length - 1:
                break
            details = entry["data"]["instant"]["details"]

            time = np.datetime64(entry["time"])
            temp = details["air_temperature"]
            humidity = details["relative_humidity"]

            self.time[i] = time
            self.temperature[i] = temp
            self.humidity[i] = humidity

    def count_timestamps_until_provided(
        self, latest_timestamp: np.datetime64, timeseries
    ) -> int:
        """Counts how many entries in the timeseries provided are before the given timestamp. This lets us cut off our dataset before the data-frequency dips below 1/hour

        Args:
            latest_timestamp (np.datetime64): _description_
            timeseries (_type_): _description_

        Returns:
            int: count of timestamps
        """
        i = 0
        for entry in timeseries:
            if np.datetime64(entry["time"]) < latest_timestamp:
                i += 1
            else:
                break
        return i

    def update_data(self) -> None:
        pass
