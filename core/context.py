import multiprocessing
from enum import IntEnum, auto

class SignalState(IntEnum):
    DEFAULT = auto()
    PAUSE = auto()
    QUIT = auto()
    RESTART = auto()
    OPEN_SETTINGS = auto()

class MainContext():
    def __init__(self):
        self.signal = multiprocessing.Value("i", SignalState.DEFAULT)
        self.signal_cond = multiprocessing.Condition()

    def do_when_signal(self, callback):
        with self.signal_cond:
            self.signal_cond.wait()
            callback(self)
                
    def watch_signal(self, callback):
        while True:
            with self.signal_cond:
                self.signal_cond.wait()
                if not callback(self):
                    break
