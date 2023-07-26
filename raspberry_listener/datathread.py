from PySide6 import QtCore
from sources import DataLoader
from typing import Callable
import debugpy


class DataThreadController(QtCore.QObject):
    finished = QtCore.Signal()
    init_load = QtCore.Signal()
    update_data = QtCore.Signal()

    def __init__(self, data_source: DataLoader):
        super().__init__()
        self.workerThread = QtCore.QThread()
        self.data_source = data_source
        self._already_queued = False
        self.init_load_worker = self.Worker(self.data_source.initial_load)
        self.init_load_worker.moveToThread(self.workerThread)
        self.repeat_load_worker = self.Worker(self.data_source.update_data)
        self.repeat_load_worker.moveToThread(self.workerThread)
        self.workerThread.start()
        self.init_load.connect(self.init_load_worker.run)
        self.init_load_worker.finished.connect(self.finished)
        self.init_load.emit()
        self.update_data.connect(self.repeat_load_worker.run)
        self.repeat_load_worker.finished.connect(self.finished)

    def __del__(self):
        self.workerThread.quit()
        self.workerThread.wait()

    class Worker(QtCore.QObject):
        finished = QtCore.Signal()

        def __init__(self, data_source_callback: Callable):
            super().__init__()
            self.data_source_callback = data_source_callback

        @QtCore.Slot()
        def run(self):
            # Call this before code running in the datathread when debugging.
            if debugpy.is_client_connected():
                debugpy.debug_this_thread()
            self.data_source_callback()
            self.finished.emit()
