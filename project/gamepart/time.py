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
            logger.log(0, "FPS inhibition: %fms (%fms) FPS %f", sleep, actual, fps)

    def clear(self):
        self.last_frame = time.perf_counter()
        while self.history:
            self.history.pop()


class TimeFeeder:
    """Quantize passed time into time_step chunks"""

    def __init__(self, time_step: float = 1 / 2 ** 10, speed: float = 1.0):
        self.time_step = time_step
        self.speed = speed
        self.system_time = 0.0
        self.world_time = 0.0

    def tick(self, delta: float, max_iter: int = 0):
        self.system_time += delta * self.speed
        x = 0
        while self.world_time < self.system_time:
            self.world_time += self.time_step
            yield self.time_step
            x += 1
            if max_iter and x >= max_iter:
                logger.warning(
                    "World time is lagging by %d steps", self.lag // self.time_step
                )
                return

    def catch_up(self) -> float:
        return sum(self.tick(0))

    @property
    def lag(self):
        return self.system_time - self.world_time
