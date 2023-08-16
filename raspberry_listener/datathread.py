import weakref
from typing import Callable

import debugpy
from PySide6 import QtCore

LoadFn = Callable[[], None]


class DataThreadController(QtCore.QObject):
    finished = QtCore.Signal()
    init_load = QtCore.Signal()
    update_data = QtCore.Signal()

    def __init__(self, initial_load_fn: LoadFn, update_data_fn: LoadFn | None = None):
        super().__init__()
        self.workerThread = QtCore.QThread()
        self.finalizer = weakref.finalize(self, self.quit_thread)

        self.initial_load_fn = initial_load_fn
        self.update_data_fn = update_data_fn

        self.init_load_worker = self.Worker(self.initial_load_fn)
        self.init_load_worker.moveToThread(self.workerThread)
        self.init_load.connect(self.init_load_worker.run)
        self.init_load_worker.finished.connect(self.finished)

        if self.update_data_fn is not None:
            self.repeat_load_worker = self.Worker(self.update_data_fn)
            self.repeat_load_worker.moveToThread(self.workerThread)
            self.update_data.connect(self.repeat_load_worker.run)
            self.repeat_load_worker.finished.connect(self.finished)
        else:
            self.init_load_worker.finished.connect(self.quit_thread)

        self.workerThread.start()
        self.init_load.emit()

    def quit_thread(self):
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
