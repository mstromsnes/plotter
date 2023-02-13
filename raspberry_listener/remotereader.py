from fabric import connection, transfer
import pathlib
import logging

DATASET_FILE = "raspberry_log.parquet"


class LogDownloader:
    def __init__(self):
        self.remote_dir = pathlib.Path("/home/.temp/")
        self.local_dataset_file = self._download_archived_file()

    def _download_archived_file(self) -> str:
        with connection.Connection(
            "friendlynas", user="alaka", connect_kwargs={"password": "greendino"}
        ) as nas:
            t = transfer.Transfer(nas)
            dataset_file_result = t.get(self.remote_dir / DATASET_FILE)
            result = dataset_file_result.local
            logging.info(f"Downloaded files to {result}")
            return result

    def get_latest_archive(self):
        return self._download_archived_file()
