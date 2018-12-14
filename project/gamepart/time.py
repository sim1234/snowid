import collections
import logging
import typing
import time

logger = logging.getLogger(__name__)


class FPSCounter:
    """FPS counter with throttling functionality"""

    def __init__(self, maxlen: int = 120):
        self.history: typing.Deque[float] = collections.deque(maxlen=maxlen)
        self.last_frame: float = time.perf_counter()

    def frame(self) -> float:
        new_frame = time.perf_counter()
        delta = new_frame - self.last_frame
        self.history.append(delta)
        self.last_frame = new_frame
        return (1.0 / delta) if delta else 0.0

    def get_fps(self) -> float:
        len_ = len(self.history)
        sum_ = sum(self.history)
        return (len_ / sum_) if sum_ else 0.0

    def target_fps(self, fps: float = 120, recent: int = None):
        if recent is None:
            recent = int(len(self.history) / 2 ** 0.5)
        history = list(self.history)[-recent:]
        len_ = len(history)
        sum_ = sum(history)
        sleep = int(min((len_ / fps) - sum_, 1 / fps) * 1000)
        if sleep > 0:
            start = time.perf_counter_ns()
            time.sleep(sleep / 1000)
            actual = (time.perf_counter_ns() - start) / 1_000_000
            fps = 1 / history[-1]
            logger.debug("FPS inhibition: %fms (%fms) FPS %f", sleep, fps, actual)

    def clear(self):
        while self.history:
            self.history.pop()
