from fabric import connection, transfer
import pathlib
import logging


class LogDownloader:
    def __init__(self):
        self.remote_dir = pathlib.Path("/home/.temp/")
        self.cpu = "cpu_temp.npy"
        self.time = "timestamp.npy"
        self.local_timestamp_file, self.local_cpu_file = self._download_archived_files()

    def _download_archived_files(self):
        with connection.Connection(
            "friendlynas", user="alaka", connect_kwargs={"password": "greendino"}
        ) as nas:
            t = transfer.Transfer(nas)
            cpu_file_result = t.get(self.remote_dir / self.cpu)
            datetime_file_result = t.get(self.remote_dir / self.time)
            result = datetime_file_result.local, cpu_file_result.local
            logging.info(f"Downloaded files to {result}")
            return result

    def get_latest_archive(self):
        return self._download_archived_files()
