from PySide6 import QtCore
from datamediator import DataMediator
from mainwindow import MainWindow
from typing import Callable

import debugpy


class DataThread(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, data_source: DataMediator, window: MainWindow):
        super().__init__()
        self.threadpool = QtCore.QThreadPool()
        self.data_source = data_source
        self.window = window

    def gather_data(self):
        worker = self.Worker(self.data_source, lambda: self.finished.emit())
        self.threadpool.start(worker)

    class Worker(QtCore.QRunnable):
        def __init__(self, data_source: DataMediator, callback_fn: Callable):
            super().__init__()
            self.data_source = data_source
            self.callback_fn = callback_fn

        def run(self):
            # Call this before code running in the datathread when debugging.
            # debugpy.debug_this_thread()
            self.data_source.merge_new_data_into_dataframe()
            self.callback_fn()
