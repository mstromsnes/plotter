import asyncio

import pandas as pd
from attrs import define, field
from sources import DataNotReadyException

from ..settings import get_settings
from .apiclient import AsyncAPIClient, Location, Variant


@define
class YrForecast:
    _client: AsyncAPIClient = AsyncAPIClient()
    _dataframe_mapping: dict[str, pd.DataFrame] = field(factory=dict)

    def get_locations(self) -> dict[str, Location]:
        settings = get_settings()
        locations: dict[str, dict[str, float]] = settings["yr"]["locations"]
        return {location: Location(**kwargs) for location, kwargs in locations.items()}

    def initial_load(self) -> None:
        locations = self.get_locations()

        async def get_forecast_for_location(location: Location):
            return await self._client.download_forecast_from_location(
                location, Variant.Compact
            )

        def load_forecast_into_dataframe(result: dict) -> pd.DataFrame:
            forecast = result["properties"]["timeseries"]
            frame = pd.DataFrame.from_records(forecast)
            observations_frame = pd.DataFrame.from_records(frame.data)
            instant_data = [
                item["details"] for item in observations_frame["instant"].to_numpy()
            ]
            instant_frame = pd.DataFrame.from_records(instant_data)
            frame["time"] = pd.to_datetime(frame["time"])
            return frame.join(instant_frame).drop("data", axis=1)

        async def collect_frame(location: Location, location_name: str):
            data = await get_forecast_for_location(location)
            frame = load_forecast_into_dataframe(data)
            self._dataframe_mapping[location_name] = frame

        async def create_dataframes():
            await asyncio.gather(
                *[
                    collect_frame(location, location_name)
                    for location_name, location in locations.items()
                ]
            )

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(create_dataframes())

    def data_for_location(self, location_name: str):
        try:
            return self._dataframe_mapping[location_name]
        except (AttributeError, KeyError):
            raise DataNotReadyException

    def update_data(self) -> None:
        pass
