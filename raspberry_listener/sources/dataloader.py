from typing import Protocol


class DataLoader(Protocol):
    """This is the underlying handler for a source of data. It controls data updates to a dataframe, and provides a getter for that dataframe for read-purposes"""

    def initial_load(self) -> None:
        ...

    def update_data(self) -> None:
        ...


class DataNotReadyException(Exception):
    ...
