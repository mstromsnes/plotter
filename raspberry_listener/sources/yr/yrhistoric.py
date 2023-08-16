import asyncio
from datetime import datetime

import pandas as pd
from attrs import define, field
from sources import DataNotReadyException

from ..settings import get_settings
from .apiclient import AsyncAPIClient


@define
class YrHistoric:
    _dataframe_mapping: dict[str, pd.DataFrame] = field(factory=dict)
    _client = AsyncAPIClient()

    def get_station_id_mapping(self):
        settings = get_settings()
        station_id_mapping: dict[str, str] = settings["frost"]["stations"]
        return station_id_mapping

    def initial_load(self) -> None:
        station_id_mapping = self.get_station_id_mapping()

        async def get_data_from_station_id(station_id: str):
            response = (
                await self._client.download_historic_from_station_between_interval(
                    station_id,
                    datetime(2023, 1, 1),
                    datetime.now(),
                )
            )
            return response["data"]

        def create_frame(data: dict, location_name):
            full_frame = pd.DataFrame.from_records(data)
            full_frame = full_frame.explode("observations").reset_index(drop=True)
            observations_frame = pd.DataFrame.from_records(
                full_frame.observations.to_numpy()
            )
            full_frame = full_frame.join(observations_frame).drop(
                "observations", axis=1
            )
            full_frame["location"] = location_name
            return full_frame

        async def collect_frame(station_id: str, location_name: str):
            data = await get_data_from_station_id(station_id)

            self._dataframe_mapping[location_name] = create_frame(data, location_name)

        async def create_dataframes():
            await asyncio.gather(
                *[
                    collect_frame(station_id, location_name)
                    for location_name, station_id in station_id_mapping.items()
                ]
            )

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(create_dataframes())

    def data_for_location(self, location: str):
        try:
            return self._dataframe_mapping[location]
        except (AttributeError, KeyError):
            raise DataNotReadyException

    def update_data(self) -> None:
        pass
